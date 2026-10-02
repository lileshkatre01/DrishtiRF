import Plot from 'react-plotly.js'

const darkLayout = (extra = {}) => ({
  paper_bgcolor: 'transparent',
  plot_bgcolor: '#0d1422',
  font: { color: '#94a3b8', family: 'JetBrains Mono, monospace', size: 11 },
  margin: { l: 48, r: 16, t: 24, b: 40 },
  xaxis: { gridcolor: '#1e293b', zerolinecolor: '#334155', color: '#64748b', title: { text: 'Sample Index (within symbol)', standoff: 8 } },
  yaxis: { gridcolor: '#1e293b', zerolinecolor: '#334155', color: '#64748b', title: { text: 'Amplitude', standoff: 8 } },
  showlegend: false,
  ...extra,
})

export default function EyeDiagramPanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}

  // Eye diagram is a 2D array: each row is one symbol period trace
  const eyeMatrix = r.eye_diagram ?? []

  if (!eyeMatrix || eyeMatrix.length === 0) return null

  // Build one Plotly trace per symbol period row (limit to 80 traces for performance)
  const maxTraces = Math.min(eyeMatrix.length, 80)
  const traces = []

  for (let i = 0; i < maxTraces; i++) {
    const row = eyeMatrix[i]
    if (!Array.isArray(row) || row.length === 0) continue
    traces.push({
      x: row.map((_, idx) => idx),
      y: row,
      type: 'scatter',
      mode: 'lines',
      line: { color: 'rgba(0,180,255,0.18)', width: 1 },
      hoverinfo: 'skip',
    })
  }

  if (traces.length === 0) return null

  return (
    <section className="space-y-4">
      <h2 className="text-xs font-bold tracking-widest px-1" style={{ color: '#a78bfa' }}>
        ▸ STAGE 3B · EYE DIAGRAM
      </h2>

      <div className="rounded-xl p-5" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
        <div className="text-xs font-bold tracking-widest mb-1" style={{ color: 'var(--text-muted)' }}>
          SYMBOL TIMING EYE DIAGRAM
        </div>
        <div className="text-xs mb-3" style={{ color: 'var(--text-muted)' }}>
          Each trace = one symbol period. Open eye = clean timing synchronization.
        </div>
        <Plot
          data={traces}
          layout={darkLayout()}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: '100%', height: '280px' }}
        />
      </div>
    </section>
  )
}
