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

  const fsMHz = capture?.sample_rate ? (capture.sample_rate / 1e6).toFixed(3) : '0.048'

  return (
    <header style={{ height: '60px', display: 'flex', alignItems: 'center', gap: '16px', padding: '0 24px', background: '#fff', borderBottom: '1px solid #D3D9E0' }}>
      {/* Brand Icon */}
      <svg width="30" height="30" viewBox="0 0 22 22" fill="none" stroke="#B86E00" strokeWidth="1.8">
        <path d="M1 11h4l2-7 4 14 3-10 2 3h5" />
      </svg>

      {/* Brand Titles */}
      <div>
        <div style={{ fontFamily: "'Barlow Condensed', sans-serif", fontWeight: 700, fontSize: '28px', letterSpacing: '.16em', lineHeight: 1 }}>
          DRISHTIRF
        </div>
        <div className="m" style={{ fontSize: '12.5px', color: '#4A5560', letterSpacing: '.06em' }}>
          SIGINT ANALYSIS PLATFORM · SIH 2026 PS-26147
        </div>
      </div>

      {/* Actions & Status on Right */}
      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '18px' }}>
        {capture?.filename && (
          <span className="m" style={{ fontSize: '13.5px', fontWeight: 500 }}>
            {capture.filename}
          </span>
        )}

        <span className="m" style={{ fontSize: '13.5px', color: '#4A5560' }}>
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
