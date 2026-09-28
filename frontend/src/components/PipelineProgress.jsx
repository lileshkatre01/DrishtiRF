import { CheckCircle, Circle, Loader, XCircle, AlertCircle } from 'lucide-react'

const STAGE_LABELS = {
  SPECTRAL: 'Spectral Analysis',
  AMC: 'Modulation Classification',
  DEMOD: 'Demodulation',
  JOINT_SEARCH: 'De-interleave + FEC',
  CORRELATION: 'Sync Correlation',
  CONFIDENCE_EVALUATION: 'Confidence Evaluation',
}

function StageRow({ name, jobStage, phase }) {
  const stages = Object.keys(STAGE_LABELS)
  const thisIdx = stages.indexOf(name)
  const activeIdx = stages.indexOf(jobStage)

  let icon, color
  if (phase === 'done') {
    icon = <CheckCircle size={14} />; color = 'var(--accent-green)'
  } else if (thisIdx < activeIdx) {
    icon = <CheckCircle size={14} />; color = 'var(--accent-green)'
  } else if (thisIdx === activeIdx) {
    icon = <Loader size={14} className="animate-spin" />; color = 'var(--accent-amber)'
  } else {
    icon = <Circle size={14} />; color = 'var(--text-muted)'
  }

  return (
    <div className="flex items-center gap-3 py-1.5">
      <span style={{ color }}>{icon}</span>
      <span className="text-xs tracking-wide" style={{ color: thisIdx <= activeIdx || phase === 'done' ? 'var(--text-primary)' : 'var(--text-muted)' }}>
        {STAGE_LABELS[name]}
      </span>
    </div>
  )
}

export default function PipelineProgress({ phase, progress, job, stages, error }) {
  return (
    <div className="rounded-xl p-6 flex flex-col gap-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>

      <div className="flex items-center justify-between">
        <span className="text-xs font-bold tracking-widest" style={{ color: 'var(--text-muted)' }}>PIPELINE STATUS</span>
        <span className="text-xs font-bold" style={{ color: 'var(--accent-green)' }}>
          {progress}%
        </span>
      </div>

      {/* Progress bar */}
      <div className="relative h-2 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
        {(phase === 'uploading' || phase === 'processing') && progress < 100 ? (
          <div
            className="progress-shimmer h-full rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        ) : (
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${progress}%`,
              background: phase === 'error' ? 'var(--accent-red)' : 'var(--accent-green)'
            }}
          />
        )}
      </div>

      {/* Stage list */}
      <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
        {stages.map(s => (
          <StageRow key={s} name={s} jobStage={job?.stage ?? ''} phase={phase} />
        ))}
      </div>

      {/* Error message */}
      {error && (
        <div className="flex items-start gap-2 mt-2 p-3 rounded-lg text-xs" style={{ background: 'rgba(255,68,68,0.1)', border: '1px solid rgba(255,68,68,0.3)', color: 'var(--accent-red)' }}>
          <AlertCircle size={14} className="shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {phase === 'idle' && (
        <p className="text-xs text-center" style={{ color: 'var(--text-muted)' }}>
          Upload a signal file to begin analysis
        </p>
      )}

      {phase === 'done' && (
        <div className="flex items-center gap-2 text-xs font-bold" style={{ color: 'var(--accent-green)' }}>
          <CheckCircle size={14} />
          Analysis complete — all stages passed
        </div>
      )}
    </div>
  )
}
