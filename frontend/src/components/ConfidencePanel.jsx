import { ShieldCheck, ShieldAlert, ShieldOff } from 'lucide-react'

const TIER_CONFIG = {
  A: { icon: ShieldCheck, color: 'var(--accent-green)', bg: 'rgba(0,255,136,0.1)', border: 'rgba(0,255,136,0.3)', label: 'TIER A — HIGH CONFIDENCE', desc: 'All pipeline stages converge with high agreement. Result is reliable.' },
  B: { icon: ShieldAlert, color: 'var(--accent-amber)', bg: 'rgba(255,179,0,0.1)', border: 'rgba(255,179,0,0.3)', label: 'TIER B — MODERATE CONFIDENCE', desc: 'Partial pipeline convergence. Result is plausible but requires human review.' },
  C: { icon: ShieldOff, color: 'var(--accent-red)', bg: 'rgba(255,68,68,0.1)', border: 'rgba(255,68,68,0.3)', label: 'TIER C — LOW CONFIDENCE', desc: 'Low agreement across pipeline stages. Signal parameters uncertain.' },
}

export default function ConfidencePanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}

  // Extract 'A', 'B', or 'C' from 'TIER_A' or 'A'
  const rawTier = r.tier_code ?? (r.tier ? r.tier.replace(/Tier\s*([ABC]).*/i, '$1') : 'C')
  const tier = rawTier.replace('TIER_', '').trim()
  const overall = r.overall_confidence ?? result.confidence ?? 0
  const stageConf = r.stage_confidences ?? r.sub_scores ?? {}
  const cfg = TIER_CONFIG[tier] ?? TIER_CONFIG.C
  const TierIcon = cfg.icon


  return (
    <section className="space-y-4">
      <h2 className="text-xs font-bold tracking-widest px-1" style={{ color: cfg.color }}>
        ▸ STAGE 6 · 3-TIER CONFIDENCE EVALUATION
      </h2>

      <div className="rounded-xl p-6" style={{ background: 'var(--bg-card)', border: `1px solid ${cfg.border}` }}>

        {/* Tier badge */}
        <div className="flex items-center gap-4 mb-6 p-4 rounded-xl" style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}>
          <TierIcon size={36} style={{ color: cfg.color }} />
          <div>
            <div className="font-bold text-lg tracking-wider" style={{ color: cfg.color }}>{cfg.label}</div>
            <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{cfg.desc}</div>
          </div>
          <div className="ml-auto text-right">
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Overall</div>
            <div className="text-3xl font-bold" style={{ color: cfg.color }}>{(overall * 100).toFixed(1)}%</div>
          </div>
        </div>

        {/* Stage confidence breakdown */}
        {Object.keys(stageConf).length > 0 && (
          <div className="space-y-2">
            <div className="text-xs font-bold tracking-widest mb-3" style={{ color: 'var(--text-muted)' }}>STAGE BREAKDOWN</div>
            {Object.entries(stageConf).map(([stage, conf]) => {
              const pct = typeof conf === 'number' ? conf : 0
              const barColor = pct >= 0.85 ? 'var(--accent-green)' : pct >= 0.65 ? 'var(--accent-amber)' : 'var(--accent-red)'
              return (
                <div key={stage} className="flex items-center gap-3">
                  <span className="text-xs w-40 shrink-0" style={{ color: 'var(--text-muted)' }}>{stage}</span>
                  <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
                    <div className="h-full rounded-full transition-all duration-700"
                      style={{ width: `${pct * 100}%`, background: barColor }} />
                  </div>
                  <span className="text-xs font-bold w-12 text-right" style={{ color: barColor }}>
                    {(pct * 100).toFixed(0)}%
                  </span>
                </div>
              )
            })}
          </div>
        )}

        {/* Rationale */}
        {(r.rationale || result.explanation) && (
          <p className="text-xs leading-relaxed p-3 rounded-lg mt-4" style={{ background: 'rgba(255,255,255,0.03)', color: 'var(--text-muted)', borderLeft: `3px solid ${cfg.color}` }}>
            {r.rationale || result.explanation}
          </p>
        )}
      </div>
    </section>
  )
}
