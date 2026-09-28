import { Signal } from 'lucide-react'

export default function CorrelationPanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}

  const syncFound    = r.sync_found ?? false
  const bestSync     = r.best_sync_word ?? '—'
  const frameCount   = r.frame_count ?? 0
  const bitInverted  = r.bit_inverted ?? false
  const entropy      = r.payload_entropy ?? null
  const conf         = result.confidence ?? 0
  const frames       = r.frames ?? []

  return (
    <section className="space-y-4">
      <h2 className="text-xs font-bold tracking-widest px-1" style={{ color: '#a78bfa' }}>
        ▸ STAGE 5 · BITSTREAM CORRELATION + FRAMING
      </h2>

      <div className="rounded-xl p-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">

          <div className="p-3 rounded-lg" style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid var(--border)' }}>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Sync Detected</div>
            <div className="font-bold mt-0.5 flex items-center gap-1.5" style={{ color: syncFound ? 'var(--accent-green)' : 'var(--accent-red)' }}>
              <Signal size={14} />
              {syncFound ? 'YES' : 'NO'}
            </div>
          </div>

          <div className="p-3 rounded-lg" style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid var(--border)' }}>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Sync Word</div>
            <div className="font-bold mt-0.5 tracking-wider text-sm" style={{ color: '#a78bfa' }}>{bestSync}</div>
          </div>

          <div className="p-3 rounded-lg" style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid var(--border)' }}>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Frames Found</div>
            <div className="text-2xl font-bold" style={{ color: 'var(--accent-blue)' }}>{frameCount}</div>
          </div>

          <div className="p-3 rounded-lg" style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid var(--border)' }}>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Bit Polarity</div>
            <div className="font-bold mt-0.5" style={{ color: bitInverted ? 'var(--accent-amber)' : 'var(--accent-green)' }}>
              {bitInverted ? 'INVERTED' : 'NORMAL'}
            </div>
          </div>
        </div>

        {entropy !== null && (
          <div className="flex items-center gap-3 mb-4">
            <span className="text-xs" style={{ color: 'var(--text-muted)' }}>PAYLOAD ENTROPY</span>
            <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
              <div className="h-full rounded-full" style={{ width: `${(entropy / 8) * 100}%`, background: '#a78bfa' }} />
            </div>
            <span className="text-xs font-bold" style={{ color: '#a78bfa' }}>{entropy.toFixed(2)} bits/byte</span>
          </div>
        )}

        <div className="flex items-center gap-3">
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>CONFIDENCE</span>
          <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
            <div className="h-full rounded-full" style={{ width: `${conf * 100}%`, background: '#a78bfa' }} />
          </div>
          <span className="text-xs font-bold" style={{ color: '#a78bfa' }}>{(conf * 100).toFixed(1)}%</span>
        </div>

        {result.explanation && (
          <p className="text-xs leading-relaxed p-3 rounded-lg mt-4" style={{ background: 'rgba(255,255,255,0.03)', color: 'var(--text-muted)', borderLeft: '3px solid #a78bfa' }}>
            {result.explanation}
          </p>
        )}
      </div>
    </section>
  )
}
