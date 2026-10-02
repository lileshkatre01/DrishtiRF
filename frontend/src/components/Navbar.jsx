import { Radio, RefreshCw, Activity, Download, FileText, Printer } from 'lucide-react'
import { exportSigMF, getExportCsvUrl } from '../api/client'

const phaseLabel = {
  idle: { text: 'STANDBY', color: 'var(--text-muted)' },
  uploading: { text: 'INGESTING...', color: 'var(--accent-blue)' },
  processing: { text: 'ANALYSING...', color: 'var(--accent-amber)' },
  done: { text: 'COMPLETE', color: 'var(--accent-green)' },
  error: { text: 'FAULT', color: 'var(--accent-red)' },
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

  return (
    <header style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)' }}>
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">

        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg" style={{ background: 'rgba(0,255,136,0.1)', border: '1px solid rgba(0,255,136,0.3)' }}>
            <Radio size={20} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div>
            <div className="font-bold text-lg tracking-widest" style={{ color: 'var(--accent-green)', letterSpacing: '0.15em' }}>
              DRISHTI<span style={{ color: 'var(--accent-blue)' }}>RF</span>
            </div>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>SIGINT ANALYSIS PLATFORM · SIH 2026 PS-26147</div>
          </div>
        </div>

        {/* Status bar + Export actions */}
        <div className="flex items-center gap-4 flex-wrap">
          {capture && (
            <div className="hidden md:block text-xs" style={{ color: 'var(--text-muted)' }}>
              <span style={{ color: 'var(--text-primary)' }}>{capture.filename}</span>
              {capture.sample_rate && (
                <span className="ml-3">Fs: <span style={{ color: 'var(--accent-blue)' }}>{(capture.sample_rate / 1e6).toFixed(3)} MHz</span></span>
              )}
            </div>
          )}

          {/* System status */}
          <div className="flex items-center gap-2">
            <Activity size={14} style={{ color: status.color }} />
            <span className="text-xs font-bold tracking-widest" style={{ color: status.color }}>
              {status.text}
            </span>
          </div>

          {/* Export Buttons (when done) */}
          {phase === 'done' && job?.id && (
            <div className="flex items-center gap-2">
              <button
                onClick={handleDownloadSigMF}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-bold transition-all"
                style={{ background: 'rgba(0,255,136,0.1)', border: '1px solid rgba(0,255,136,0.4)', color: 'var(--accent-green)' }}
                title="Download SigMF metadata specification (.sigmf-meta)"
              >
                <Download size={12} />
                .SigMF
              </button>

              <a
                href={getExportCsvUrl(job.id)}
                download
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-bold transition-all"
                style={{ background: 'rgba(0,180,255,0.1)', border: '1px solid rgba(0,180,255,0.4)', color: 'var(--accent-blue)' }}
                title="Download extracted frame bitstreams as CSV"
              >
                <FileText size={12} />
                .CSV
              </a>

              <button
                onClick={handlePrintReport}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-bold transition-all"
                style={{ background: 'rgba(167,139,250,0.1)', border: '1px solid rgba(167,139,250,0.4)', color: '#a78bfa' }}
                title="Print or save PDF Analysis Report"
              >
                <Printer size={12} />
                PDF Report
              </button>
            </div>
          )}

          {/* Reset button */}
          {phase !== 'idle' && (
            <button
              onClick={onReset}
              className="flex items-center gap-2 px-3 py-1.5 rounded text-xs font-bold transition-all"
              style={{
                border: '1px solid var(--border)',
                color: 'var(--text-muted)',
                background: 'transparent',
              }}
              onMouseOver={e => e.currentTarget.style.color = 'var(--text-primary)'}
              onMouseOut={e => e.currentTarget.style.color = 'var(--text-muted)'}
            >
              <RefreshCw size={12} />
              NEW CAPTURE
            </button>
          )}
        </div>
      </div>
    </header>
  )
}

