import { exportSigMF, getExportCsvUrl } from '../api/client'

const phaseLabel = {
  idle: { text: 'STANDBY', color: '#A7B3BF' },
  uploading: { text: '● INGESTING...', color: '#4FB3D9' },
  processing: { text: '● ANALYSING...', color: '#E8A33D' },
  done: { text: '● COMPLETE', color: '#17703A' },
  error: { text: '● FAULT', color: '#F0605D' },
}

export default function Navbar({ capture, job, phase, onReset }) {
  const status = phaseLabel[phase] || phaseLabel.idle

  const handleDownloadSigMF = async () => {
    if (!job?.id) return
    try {
      const res = await exportSigMF(job.id)
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `drishtirf_analysis_${(capture?.filename || 'capture').replace(/\.[^/.]+$/, '')}.sigmf-meta`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e) {
      alert('Failed to export SigMF: ' + e.message)
    }
  }

  const handlePrintReport = () => {
    window.print()
  }

  const fsMHz = capture?.sample_rate ? (capture.sample_rate / 1e6).toFixed(3) : '—'

  return (
    <header style={{ height: '68px', display: 'flex', alignItems: 'center', gap: '16px', padding: '0 24px', background: '#0C121A', borderBottom: '1px solid #1E2836', color: '#fff' }}>
      {/* Brand Icon (Eye Logo from Image 2) */}
      <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#0A1017', border: '1px solid #223145', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 12px rgba(0,0,0,0.5)', shrink: 0 }}>
        <svg width="34" height="26" viewBox="0 0 34 26" fill="none">
          {/* Outer Golden/Orange Eye Outline */}
          <path d="M2 13C7 5.5 17 5.5 32 13C25 20.5 15 20.5 2 13Z" stroke="#E8A33D" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
          {/* Inner Iris Circle (Cyan) */}
          <circle cx="17" cy="13" r="6" stroke="#38BDF8" strokeWidth="2.2" fill="#0A1017" />
          {/* Pupil Signal Waveform (White) */}
          <path d="M13.2 13h1.6l1.2-3.2 1.6 6.4 1.2-3.2h1.6" stroke="#FFFFFF" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>

      {/* Brand Titles (DRISHTI in White + RF in Golden/Orange) */}
      <div>
        <div style={{ fontFamily: "'Barlow Condensed', sans-serif", fontWeight: 800, fontSize: '32px', letterSpacing: '.14em', lineHeight: 1 }}>
          <span style={{ color: '#FFFFFF' }}>DRISHTI</span>
          <span style={{ color: '#E8A33D' }}>RF</span>
        </div>
        <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', color: '#7D8A99', letterSpacing: '.38em', marginTop: '3px', fontWeight: 500, textTransform: 'uppercase' }}>
          SIGINT ANALYSIS PLATFORM
        </div>
      </div>

      {/* Actions & Status on Right */}
      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '18px' }}>
        {capture?.filename && (
          <span className="m" style={{ fontSize: '13.5px', fontWeight: 500 }}>
            {capture.filename}
          </span>
        )}

        <span className="m" style={{ fontSize: '13.5px', color: '#94A3B8' }}>
          Fs: {fsMHz} MHz
        </span>

        <span className="m" style={{ fontSize: '13.5px', fontWeight: 600, color: status.color }}>
          {status.text}
        </span>

        {job?.id && (
          <>
            <button onClick={handleDownloadSigMF} title="Export .sigmf-meta metadata">
              .SigMF
            </button>
            <a href={getExportCsvUrl(job.id)} download style={{ textDecoration: 'none' }}>
              <button title="Export frames .csv">
                .CSV
              </button>
            </a>
            <button className="pri" onClick={handlePrintReport} title="Generate and Print PDF Report">
              PDF Report
            </button>
          </>
        )}

        <button onClick={onReset}>
          New capture
        </button>
      </div>
    </header>
  )
}
