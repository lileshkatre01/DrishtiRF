import { useState, useCallback } from 'react'
import Navbar from './components/Navbar'
import SignalVerdictHUD from './components/SignalVerdictHUD'
import TargetBadgePanel from './components/TargetBadgePanel'
import UploadZone from './components/UploadZone'
import PipelineProgress from './components/PipelineProgress'
import SpectrumPanel from './components/SpectrumPanel'
import AMCPanel from './components/AMCPanel'
import DemodPanel from './components/DemodPanel'
import EyeDiagramPanel from './components/EyeDiagramPanel'
import JointSearchPanel from './components/JointSearchPanel'
import CorrelationPanel from './components/CorrelationPanel'
import ConfidencePanel from './components/ConfidencePanel'
import FramesTable from './components/FramesTable'
import RequirementCoverageTable from './components/RequirementCoverageTable'
import { uploadSignalFile, createJob, getJobResults, getJobFrames, getCaptureSpectrum } from './api/client'

const STAGES = ['SPECTRAL', 'AMC', 'DEMOD', 'JOINT_SEARCH', 'CORRELATION', 'CONFIDENCE_EVALUATION']

export default function App() {
  const [phase, setPhase] = useState('idle') // idle | uploading | processing | done | error
  const [capture, setCapture] = useState(null)
  const [job, setJob] = useState(null)
  const [results, setResults] = useState({}) // stage -> json_result
  const [frames, setFrames] = useState([])
  const [spectrum, setSpectrum] = useState(null)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)

  const handleFile = useCallback(async (file) => {
    setPhase('uploading')
    setError(null)
    setResults({})
    setFrames([])
    setSpectrum(null)
    setProgress(0)

    try {
      // 1. Upload
      const { data: cap } = await uploadSignalFile(file, {
        onProgress: (e) => {
          if (e.total) setProgress(Math.round((e.loaded / e.total) * 10))
        },
      })
      setCapture(cap)
      setProgress(12)

      // 2. Fetch spectrum data for visualisations
      try {
        const { data: spec } = await getCaptureSpectrum(cap.id)
        setSpectrum(spec)
      } catch (_) {}

      setProgress(18)
      setPhase('processing')

      // 3. Run analysis pipeline job (synchronous in current backend)
      const { data: jobData } = await createJob(cap.id)
      setJob(jobData)
      setProgress(95)

      // 4. Fetch stage results
      const { data: stageResults } = await getJobResults(jobData.id)
      const map = {}
      stageResults.forEach((r) => {
        map[r.stage] = r
      })
      setResults(map)

      // 5. Fetch frames
      const { data: framesData } = await getJobFrames(jobData.id)
      setFrames(framesData)

      setProgress(100)
      setPhase('done')
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Unknown error')
      setPhase('error')
    }
  }, [])

  const reset = () => {
    setPhase('idle')
    setCapture(null)
    setJob(null)
    setResults({})
    setFrames([])
    setSpectrum(null)
    setProgress(0)
    setError(null)
  }

  const stageProgress = STAGES.indexOf(job?.stage ?? '') + 1
  const displayProgress =
    phase === 'done'
      ? 100
      : phase === 'processing'
      ? Math.max(20, Math.round((stageProgress / STAGES.length) * 80) + 15)
      : progress

  return (
    <div style={{ minHeight: '100vh', background: '#D3D9E0', color: '#14181D' }}>
      {/* Top Header Navbar */}
      <Navbar capture={capture} job={job} phase={phase} onReset={reset} />

      {/* Main Container - Full Width Responsive Layout */}
      <main style={{ padding: '0 20px 40px', width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
        {/* Section 00A: Target Classification Badge (Aviation, Maritime, Drone, Satellite, Tactical RF) */}
        {(results.CORRELATION || results.AMC) && (
          <TargetBadgePanel
            correlationResult={results.CORRELATION}
            amcResult={results.AMC}
            spectralResult={results.SPECTRAL}
            capture={capture}
          />
        )}

        {/* Section 00B: Signal Verdict HUD */}
        <SignalVerdictHUD results={results} capture={capture} job={job} />


        {/* Upload Drop Zone & Pipeline Status Row */}
        <div className="r" style={{ marginTop: '16px' }}>
          <UploadZone onFile={handleFile} disabled={phase === 'uploading' || phase === 'processing'} />
          <PipelineProgress
            phase={phase}
            progress={displayProgress}
            job={job}
            stages={STAGES}
            error={error}
          />
        </div>

        {/* Section 01: Spectral Analysis */}
        <SpectrumPanel spectrum={spectrum || results.SPECTRAL?.json_result} capture={capture} />

        {/* Section 02 & Section 03: AMC + Demodulation */}
        <div className="r">
          <AMCPanel result={results.AMC} />
          <DemodPanel result={results.DEMOD} modType={results.AMC?.json_result?.modulation} />
        </div>

        {/* Section 03B: Constellation + Symbol Timing Eye Diagram */}
        <EyeDiagramPanel result={results.DEMOD} />

        {/* Section 04: Joint De-interleave + FEC Search */}
        <JointSearchPanel result={results.JOINT_SEARCH} />

        {/* Section 05: Bitstream Correlation + Framing */}
        <CorrelationPanel result={results.CORRELATION} />

        {/* Section 06: 3-Tier Confidence Evaluation */}
        <ConfidencePanel result={results.CONFIDENCE_EVALUATION} />

        {/* Section F: Extracted Frames Table */}
        <FramesTable frames={frames} />

        {/* Section NTRO: PS-26147 Requirement Coverage */}
        <RequirementCoverageTable results={results} capture={capture} />
      </main>
    </div>
  )
}
