import { useState, useCallback } from 'react'
import Navbar from './components/Navbar'
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
import { uploadSignalFile, createJob, getJobResults, getJobFrames, getCaptureSpectrum } from './api/client'

const STAGES = ['SPECTRAL', 'AMC', 'DEMOD', 'JOINT_SEARCH', 'CORRELATION', 'CONFIDENCE_EVALUATION']

export default function App() {
  const [phase, setPhase] = useState('idle')   // idle | uploading | processing | done | error
  const [capture, setCapture] = useState(null)
  const [job, setJob] = useState(null)
  const [results, setResults] = useState({})    // stage -> json_result
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
        }
      })
      setCapture(cap)
      setProgress(12)

      // 2. Fetch spectrum data for visualisation
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
      stageResults.forEach(r => { map[r.stage] = r })
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
  const displayProgress = phase === 'done' ? 100 : phase === 'processing' ? Math.max(20, Math.round((stageProgress / STAGES.length) * 80) + 15) : progress

  return (
    <div className="scanline min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      <Navbar capture={capture} job={job} phase={phase} onReset={reset} />

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">

        {/* Upload + Progress */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <UploadZone onFile={handleFile} disabled={phase === 'uploading' || phase === 'processing'} />
          <PipelineProgress
            phase={phase}
            progress={displayProgress}
            job={job}
            stages={STAGES}
            error={error}
          />
        </div>

        {/* Results Grid — only shown when data available */}
        {(spectrum || results.SPECTRAL) && (
          <SpectrumPanel spectrum={spectrum || results.SPECTRAL?.json_result} capture={capture} />
        )}

        {/* Stage 2 & Stage 3 Side-by-Side */}
        {(results.AMC || results.DEMOD) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            {results.AMC && (
              <AMCPanel result={results.AMC} />
            )}

            {results.DEMOD && results.AMC && (
              <DemodPanel result={results.DEMOD} modType={results.AMC?.json_result?.modulation} />
            )}
          </div>
        )}

        {results.DEMOD && (
          <EyeDiagramPanel result={results.DEMOD} />
        )}

        {results.JOINT_SEARCH && (
          <JointSearchPanel result={results.JOINT_SEARCH} />
        )}

        {results.CORRELATION && (
          <CorrelationPanel result={results.CORRELATION} />
        )}

        {results.CONFIDENCE_EVALUATION && (
          <ConfidencePanel result={results.CONFIDENCE_EVALUATION} />
        )}

        {frames.length > 0 && (
          <FramesTable frames={frames} />
        )}

      </main>
    </div>
  )
}
