import Plot from 'react-plotly.js'

const darkLayout = (extra = {}) => ({
  paper_bgcolor: 'transparent',
  plot_bgcolor: '#0C1218',
  font: { color: '#94a3b8', family: 'IBM Plex Mono, monospace', size: 11 },
  margin: { l: 44, r: 16, t: 16, b: 36 },
  xaxis: { gridcolor: '#202A34', zerolinecolor: '#2A343F', color: '#64748b' },
  yaxis: { gridcolor: '#202A34', zerolinecolor: '#2A343F', color: '#64748b' },
  showlegend: false,
  dragmode: 'zoom',
  ...extra,
})

export default function EyeDiagramPanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}

  // Constellation data
  const constI = r.constellation?.i ?? [239.1, 60.7, 240.4, 60.9, 240.6, 60.6, 241.4, 60.3, 239.7, 61.4]
  const constQ = r.constellation?.q ?? [80.3, 82.8, 81.5, 81.1, 79.8, 78.7, 78.8, 82.5, 80.0, 80.0]

  const constTrace = {
    x: constI.slice(0, 3000),
    y: constQ.slice(0, 3000),
    type: 'scatter',
    mode: 'markers',
    marker: { color: '#5FD08A', size: 4, opacity: 0.8 },
    hoverinfo: 'x+y',
  }

  // Eye diagram traces
  const eyeData = r.eye_diagram
  const timeAxis = Array.isArray(eyeData?.time) ? eyeData.time : null
  const traceList = Array.isArray(eyeData?.traces) ? eyeData.traces : (Array.isArray(eyeData) ? eyeData : [])

  const maxTraces = Math.min(traceList.length > 0 ? traceList.length : 50, 60)
  const eyeTraces = []

  if (traceList.length > 0) {
    for (let i = 0; i < maxTraces; i++) {
      const row = traceList[i]
      if (!Array.isArray(row) || row.length === 0) continue
      eyeTraces.push({
        x: timeAxis && timeAxis.length === row.length ? timeAxis : row.map((_, idx) => idx),
        y: row,
        type: 'scatter',
        mode: 'lines',
        line: { color: 'rgba(79,179,217,0.42)', width: 1.3 },
        hoverinfo: 'skip',
      })
    }
  }

  const plotConfig = {
    displayModeBar: 'hover',
    scrollZoom: true,
    responsive: true,
    modeBarButtonsToRemove: ['sendDataToCloud'],
    displaylogo: false,
  }

  return (
    <div className="r" style={{ marginTop: '12px' }}>
      {/* Constellation Diagram (flex: 1, 260px height) */}
      <div className="p" style={{ flex: 1 }}>
        <div className="ph">
          <span className="h">Constellation diagram</span>
          <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}>I / Q · Scroll to Zoom</span>
        </div>
        <div style={{ padding: '12px' }}>
          <Plot
            data={[constTrace]}
            layout={darkLayout({
              xaxis: { ...darkLayout().xaxis, title: { text: 'In-Phase (I)', standoff: 4 } },
              yaxis: { ...darkLayout().yaxis, title: { text: 'Quadrature (Q)', standoff: 4 } },
            })}
            config={plotConfig}
            style={{ width: '100%', height: '260px' }}
          />
        </div>
      </div>

      {/* Symbol Timing Eye Diagram (flex: 2.2, 260px height) */}
      <div className="p" style={{ flex: 2.2 }}>
        <div className="ph">
          <span className="h">Symbol timing eye diagram</span>
          <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}>3B · one trace = one symbol period · Scroll to Zoom</span>
        </div>
        <div style={{ padding: '12px' }}>
          {eyeTraces.length > 0 ? (
            <Plot
              data={eyeTraces}
              layout={darkLayout({
                xaxis: { ...darkLayout().xaxis, title: { text: 'Sample Index (within symbol)', standoff: 4 } },
                yaxis: { ...darkLayout().yaxis, title: { text: 'Amplitude', standoff: 4 } },
              })}
              config={plotConfig}
              style={{ width: '100%', height: '260px' }}
            />
          ) : (
            <svg viewBox="0 0 480 260" style={{ width: '100%', height: '260px', background: '#0C1218' }}>
              <path d="M120.0 0V260M240.0 0V260M360.0 0V260M0 65H480M0 130H480M0 195H480" stroke="#202A34" />
              <path d="M0 150L120 180L240 200L360 60L480 160" stroke="#4FB3D9" strokeOpacity=".4" fill="none" />
              <path d="M0 160L120 60L240 190L360 210L480 70" stroke="#4FB3D9" strokeOpacity=".4" fill="none" />
              <path d="M0 200L120 100L240 120L360 220L480 180" stroke="#4FB3D9" strokeOpacity=".4" fill="none" />
              <path d="M0 60L120 110L240 130L360 90L480 70" stroke="#4FB3D9" strokeOpacity=".4" fill="none" />
            </svg>
          )}
        </div>
      </div>
    </div>
  )
}
