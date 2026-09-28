import { CheckCircle, XCircle } from 'lucide-react'

function Tag({ label, value, color = 'var(--accent-blue)' }) {
  return (
    <div className="flex flex-col gap-0.5 p-3 rounded-lg" style={{ background: 'rgba(0,180,255,0.07)', border: '1px solid var(--border)' }}>
      <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</span>
      <span className="font-bold tracking-wide" style={{ color }}>{value}</span>
    </div>
  )
}

export default function JointSearchPanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}

  const interleaveType  = r.interleave_type ?? r.best_interleaver ?? '—'
  const fecType         = r.fec_type ?? r.best_fec ?? '—'
  const decodedBitCount = r.decoded_bit_count ?? (r.decoded_bits?.length ?? 0)
  const fecSuccess      = r.fec_success ?? false
  const conf            = result.confidence ?? 0

  return (
    <section className="space-y-4">
      <h2 className="text-xs font-bold tracking-widest px-1" style={{ color: 'var(--accent-amber)' }}>
        ▸ STAGE 4 · JOINT DE-INTERLEAVE + FEC SEARCH
      </h2>

      <div className="rounded-xl p-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
          <Tag label="Interleaver" value={interleaveType} color="var(--accent-amber)" />
          <Tag label="FEC Scheme" value={fecType} color="var(--accent-amber)" />
          <Tag label="Decoded Bits" value={decodedBitCount.toLocaleString()} color="var(--accent-green)" />
          <div className="flex flex-col gap-0.5 p-3 rounded-lg" style={{ background: 'rgba(0,180,255,0.07)', border: '1px solid var(--border)' }}>
            <span className="text-xs" style={{ color: 'var(--text-muted)' }}>FEC Status</span>
            <span className="font-bold flex items-center gap-1.5" style={{ color: fecSuccess ? 'var(--accent-green)' : 'var(--accent-red)' }}>
              {fecSuccess ? <CheckCircle size={14} /> : <XCircle size={14} />}
              {fecSuccess ? 'SUCCESS' : 'PARTIAL'}
            </span>
          </div>
        </div>

        {/* Confidence bar */}
        <div className="flex items-center gap-3">
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>CONFIDENCE</span>
          <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
            <div className="h-full rounded-full" style={{ width: `${conf * 100}%`, background: 'var(--accent-amber)' }} />
          </div>
          <span className="text-xs font-bold" style={{ color: 'var(--accent-amber)' }}>{(conf * 100).toFixed(1)}%</span>
        </div>

        {result.explanation && (
          <p className="text-xs leading-relaxed p-3 rounded-lg mt-4" style={{ background: 'rgba(255,255,255,0.03)', color: 'var(--text-muted)', borderLeft: '3px solid var(--accent-amber)' }}>
            {result.explanation}
          </p>
        )}
      </div>
    </section>
  )
}
