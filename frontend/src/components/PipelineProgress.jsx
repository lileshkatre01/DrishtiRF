export default function PipelineProgress({ phase, progress, job, stages, error }) {
  const isDone = phase === 'done'
  const isError = phase === 'error'
  const pct = isDone ? 100 : Math.round(progress || 0)

  // Number of active green segments (out of 30)
  const activeSegments = Math.round((pct / 100) * 30)

  const STAGE_NAMES = [
    { key: 'SPECTRAL', name: 'Spectral Analysis' },
    { key: 'AMC', name: 'Modulation Classification' },
    { key: 'DEMOD', name: 'Demodulation' },
    { key: 'JOINT_SEARCH', name: 'De-interleave + FEC' },
    { key: 'CORRELATION', name: 'Sync Correlation' },
    { key: 'CONFIDENCE_EVALUATION', name: 'Confidence Evaluation' },
  ]

  return (
    <div className="p" style={{ flex: 1 }}>
      <div className="ph">
        <span className="h">Pipeline status</span>
        <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}>
          {pct}%
        </span>
      </div>

      <div className="b">
        {/* 30-Segmented Progress Bar */}
        <div style={{ display: 'flex', gap: '2px' }}>
          {Array.from({ length: 30 }).map((_, i) => (
            <i
              key={i}
              style={{
                flex: 1,
                height: '14px',
                background: i < activeSegments ? (isError ? '#F0605D' : '#5FD08A') : '#1C232B',
                borderRadius: '1px',
                transition: 'background 0.2s ease',
              }}
            />
          ))}
        </div>

        {/* Stage Checklist */}
        <div style={{ marginTop: '8px' }}>
          {STAGE_NAMES.map((s, idx) => {
            const isPassed = isDone || (job?.progress && job.progress >= (idx + 1) * 16)
            return (
              <div
                key={s.key}
                style={{
                  display: 'flex',
                  gap: '10px',
                  alignItems: 'center',
                  padding: '7px 0',
                  borderBottom: idx < STAGE_NAMES.length - 1 ? '1px solid #1F2832' : 'none',
                  fontSize: '14px',
                }}
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke={isPassed ? '#5FD08A' : '#4A5560'} strokeWidth="1.8">
                  <circle cx="7" cy="7" r="6" />
                  {isPassed && <path d="M4 7l2 2 4-4" />}
                </svg>
                <span style={{ color: isPassed ? '#E4EAF0' : '#A7B3BF' }}>{s.name}</span>
                <span className="m" style={{ marginLeft: 'auto', fontSize: '13px', color: isPassed ? '#5FD08A' : '#4A5560' }}>
                  {isPassed ? 'PASS' : 'WAIT'}
                </span>
              </div>
            )
          })}
        </div>

        {/* Footer Status Message */}
        <div className="m" style={{ fontSize: '13px', color: isError ? '#F0605D' : isDone ? '#5FD08A' : '#E8A33D', marginTop: '10px' }}>
          {isError ? `Error: ${error}` : isDone ? 'Analysis complete — all stages passed' : 'Processing pipeline stages...'}
        </div>
      </div>
    </div>
  )
}
