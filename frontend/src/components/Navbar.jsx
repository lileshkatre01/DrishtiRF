import { Radio, RefreshCw, Activity } from 'lucide-react'

const phaseLabel = {
  idle: { text: 'STANDBY', color: 'var(--text-muted)' },
  uploading: { text: 'INGESTING...', color: 'var(--accent-blue)' },
  processing: { text: 'ANALYSING...', color: 'var(--accent-amber)' },
  done: { text: 'COMPLETE', color: 'var(--accent-green)' },
  error: { text: 'FAULT', color: 'var(--accent-red)' },
}

export default function Navbar({ capture, job, phase, onReset }) {
  const status = phaseLabel[phase] || phaseLabel.idle

  return (
    <header style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)' }}>
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">

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

        {/* Status bar */}
        <div className="flex items-center gap-6">
          {capture && (
            <div className="hidden md:block text-xs" style={{ color: 'var(--text-muted)' }}>
              <span style={{ color: 'var(--text-primary)' }}>{capture.filename}</span>
              {capture.sample_rate && (
                <span className="ml-3">Fs: <span style={{ color: 'var(--accent-blue)' }}>{(capture.sample_rate / 1e6).toFixed(3)} MHz</span></span>
              )}
              {capture.n_samples && (
                <span className="ml-3">N: <span style={{ color: 'var(--accent-blue)' }}>{capture.n_samples.toLocaleString()}</span></span>
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
