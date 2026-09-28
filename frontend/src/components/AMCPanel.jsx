import Plot from 'react-plotly.js'

const darkLayout = (extra = {}) => ({
  paper_bgcolor: 'transparent',
  plot_bgcolor: '#0d1422',
  font: { color: '#94a3b8', family: 'JetBrains Mono, monospace', size: 11 },
  margin: { l: 48, r: 16, t: 24, b: 40 },
  xaxis: { gridcolor: '#1e293b', zerolinecolor: '#334155', color: '#64748b' },
  yaxis: { gridcolor: '#1e293b', zerolinecolor: '#334155', color: '#64748b' },
  showlegend: false,
  ...extra,
})

const MOD_COLORS = {
  '2FSK': '#00b4ff', '4FSK': '#00ddff',
  BPSK: '#00ff88', QPSK: '#00ffcc',
  '8PSK': '#7cff88',
  '16QAM': '#ffb300', '64QAM': '#ff8c00',
  UNKNOWN: '#64748b',
}

const CONFIDENCE_BAR_COLOR = (c) => {
  if (c >= 0.85) return '#00ff88'
  if (c >= 0.65) return '#ffb300'
  return '#ff4444'
}

export default function AMCPanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}
  const mod = r.modulation ?? 'UNKNOWN'
  const conf = r.confidence ?? 0
  const symRate = r.symbol_rate_baud
  const snrConf = r.snr_confidence
  const confMap = r.confidence_map ?? {}

  // Confidence breakdown bar chart
  const confKeys = Object.keys(confMap)
  const confVals = Object.values(confMap)

  const barTrace = confKeys.length > 0 ? [{
    x: confKeys,
    y: confVals,
    type: 'bar',
    marker: { color: confVals.map(v => CONFIDENCE_BAR_COLOR(v)) },
    name: 'Confidence',
  }] : null

  return (
    <section className="space-y-4">
      <h2 className="text-xs font-bold tracking-widest px-1" style={{ color: 'var(--accent-blue)' }}>
        ▸ STAGE 2 · AUTOMATIC MODULATION CLASSIFICATION
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        {/* Verdict card */}
        <div className="rounded-xl p-6 flex flex-col gap-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
          <div className="text-xs font-bold tracking-widest" style={{ color: 'var(--text-muted)' }}>CLASSIFICATION VERDICT</div>

          <div className="flex items-end gap-4">
            <div>
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Modulation</div>
              <div className="text-4xl font-bold mt-1 tracking-wider" style={{ color: MOD_COLORS[mod] ?? 'var(--accent-green)' }}>
                {mod}
              </div>
            </div>
            <div className="pb-1">
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Confidence</div>
              <div className="text-2xl font-bold" style={{ color: CONFIDENCE_BAR_COLOR(conf) }}>
                {(conf * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Confidence bar */}
          <div className="h-2 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${conf * 100}%`, background: CONFIDENCE_BAR_COLOR(conf) }}
            />
          </div>

          {/* Params */}
          <div className="grid grid-cols-2 gap-3 mt-2">
            {symRate && (
              <div className="p-3 rounded-lg" style={{ background: 'rgba(0,180,255,0.07)', border: '1px solid var(--border)' }}>
                <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Symbol Rate</div>
                <div className="font-bold" style={{ color: 'var(--accent-blue)' }}>{(symRate / 1e3).toFixed(2)} kBaud</div>
              </div>
            )}
            {snrConf !== undefined && (
              <div className="p-3 rounded-lg" style={{ background: 'rgba(0,180,255,0.07)', border: '1px solid var(--border)' }}>
                <div className="text-xs" style={{ color: 'var(--text-muted)' }}>SNR Confidence</div>
                <div className="font-bold" style={{ color: 'var(--accent-blue)' }}>{(snrConf * 100).toFixed(1)}%</div>
              </div>
            )}
          </div>

          {/* Explanation */}
          {result.explanation && (
            <p className="text-xs leading-relaxed p-3 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)', color: 'var(--text-muted)', borderLeft: '3px solid var(--accent-blue)' }}>
              {result.explanation}
            </p>
          )}
        </div>

        {/* Confidence breakdown chart */}
        {barTrace && (
          <div className="rounded-xl p-5" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
            <div className="text-xs font-bold tracking-widest mb-3" style={{ color: 'var(--text-muted)' }}>MODULATION CONFIDENCE MAP</div>
            <Plot
              data={barTrace}
              layout={darkLayout({
                yaxis: { ...darkLayout().yaxis, range: [0, 1], title: { text: 'Confidence', standoff: 8 } },
              })}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '220px' }}
            />
          </div>
        )}
      </div>
    </section>
  )
}
