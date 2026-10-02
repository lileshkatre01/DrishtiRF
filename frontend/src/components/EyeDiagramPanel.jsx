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

  // Handle both {time: [], traces: [[]]} and raw [[]]
  const eyeData = r.eye_diagram
  if (!eyeData) return null

  const timeAxis = Array.isArray(eyeData?.time) ? eyeData.time : null
  const traceList = Array.isArray(eyeData?.traces) ? eyeData.traces : (Array.isArray(eyeData) ? eyeData : [])

  if (traceList.length === 0) return null

  // Build Plotly traces per symbol period (limit to 60 traces for fast rendering)
  const maxTraces = Math.min(traceList.length, 60)
  const traces = []

  for (let i = 0; i < maxTraces; i++) {
    const row = traceList[i]
    if (!Array.isArray(row) || row.length === 0) continue
    traces.push({
      x: timeAxis && timeAxis.length === row.length ? timeAxis : row.map((_, idx) => idx),
      y: row,
      type: 'scatter',
      mode: 'lines',
      line: { color: 'rgba(0,180,255,0.22)', width: 1.2 },
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
