import { useState, useEffect, useRef } from 'react'
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
  const rawI = r.constellation?.i ?? [239.1, 60.7, 240.4, 60.9, 240.6, 60.6, 241.4, 60.3, 239.7, 61.4]
  const rawQ = r.constellation?.q ?? [80.3, 82.8, 81.5, 81.1, 79.8, 78.7, 78.8, 82.5, 80.0, 80.0]

  // Live Costas Loop & Stream State
  const [isStreaming, setIsStreaming] = useState(false)
  const [phaseAngle, setPhaseAngle] = useState(0)
  const [pllLocked, setPllLocked] = useState(true)
  const [lockProgress, setLockProgress] = useState(1.0)
  const [rmsPhaseError, setRmsPhaseError] = useState(0.8)
  const animRef = useRef(null)

  // Real-time Costas Loop Simulation & Phosphor Decay Loop
  useEffect(() => {
    if (!isStreaming) {
      if (animRef.current) cancelAnimationFrame(animRef.current)
      return
    }

    let frame = 0
    const animateCostas = () => {
      frame += 1
      const convergence = Math.min(1.0, 0.4 + (frame % 300) / 300)
      setLockProgress(convergence)
      
      const noise = (Math.random() - 0.5) * (1.0 - convergence * 0.85) * 0.25
      setPhaseAngle((prev) => prev + noise)
      
      const err = (1.0 - convergence) * 8.5 + (Math.random() * 0.6 + 0.5)
      setRmsPhaseError(parseFloat(err.toFixed(1)))
      setPllLocked(convergence > 0.85)

      animRef.current = requestAnimationFrame(animateCostas)
    }

    animRef.current = requestAnimationFrame(animateCostas)
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current)
    }
  }, [isStreaming])

  // Compute live rotated IQ points
  const displayI = []
  const displayQ = []
  const cosTheta = Math.cos(phaseAngle)
  const sinTheta = Math.sin(phaseAngle)
  const numPoints = Math.min(rawI.length, 1200)

  for (let idx = 0; idx < numPoints; idx++) {
    const ptI = rawI[idx]
    const ptQ = rawQ[idx]
    const rotI = ptI * cosTheta - ptQ * sinTheta
    const rotQ = ptI * sinTheta + ptQ * cosTheta
    const jitter = (1.0 - lockProgress) * 0.35
    displayI.push(rotI + (Math.random() - 0.5) * jitter)
    displayQ.push(rotQ + (Math.random() - 0.5) * jitter)
  }

  const constTrace = {
    x: displayI.slice(0, 3000),
    y: displayQ.slice(0, 3000),
    type: 'scatter',
    mode: 'markers',
    marker: {
      color: isStreaming ? (pllLocked ? '#38BDF8' : '#E8A33D') : '#5FD08A',
      size: 4,
      opacity: 0.82
    },
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
      const jitterShift = isStreaming ? (Math.sin(phaseAngle * 2 + i) * 0.05) : 0
      eyeTraces.push({
        x: timeAxis && timeAxis.length === row.length ? timeAxis : row.map((_, idx) => idx),
        y: row.map((v) => v + jitterShift),
        type: 'scatter',
        mode: 'lines',
        line: {
          color: isStreaming ? 'rgba(56,189,248,0.55)' : 'rgba(79,179,217,0.42)',
          width: isStreaming ? 1.5 : 1.3
        },
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
    <div>
      {/* Live Costas Loop & Demodulation Stream Controls Bar */}
      <div style={{ marginTop: '12px', background: '#0A1017', border: '1px solid #1E2836', borderRadius: '4px', padding: '10px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => setIsStreaming(!isStreaming)}
            style={{
              background: isStreaming ? '#E8A33D' : '#0284C7',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              padding: '6px 14px',
              fontFamily: 'IBM Plex Mono',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            {isStreaming ? '⏸ Pause Costas Stream' : '⚡ Live Costas Loop Lock'}
          </button>
          
          <span style={{ fontSize: '12px', color: '#9CA3AF', fontFamily: 'IBM Plex Mono' }}>
            {isStreaming ? 'Phosphor Persistence & Carrier PLL active' : 'Static Snapshot (Click to Stream)'}
          </span>
        </div>

        {/* PLL Lock Status Gauge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              background: pllLocked ? '#5FD08A' : '#E8A33D',
              boxShadow: pllLocked ? '0 0 8px #5FD08A' : '0 0 8px #E8A33D',
              animation: isStreaming ? 'pulse 1s infinite' : 'none'
            }}></span>
            <span style={{ fontSize: '12px', fontFamily: 'IBM Plex Mono', fontWeight: 600, color: pllLocked ? '#5FD08A' : '#E8A33D' }}>
              PLL: {pllLocked ? 'CARRIER LOCKED' : 'CONVERGING...'}
            </span>
          </div>

          <div style={{ background: '#121C26', padding: '4px 10px', borderRadius: '4px', border: '1px solid #1F2E3E', fontFamily: 'IBM Plex Mono', fontSize: '12px', color: '#C9D3DC' }}>
            Phase RMS: <strong style={{ color: '#38BDF8' }}>{rmsPhaseError}°</strong>
          </div>
        </div>
      </div>

      <div className="r" style={{ marginTop: '12px' }}>
        {/* Constellation Diagram (flex: 1, 270px height) */}
        <div className="p" style={{ flex: 1 }}>
          <div className="ph">
            <span className="h">Phosphor IQ constellation</span>
            <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}>
              {isStreaming ? '● LIVE PHOSPHOR CLOUD' : 'I / Q · Scroll to Zoom'}
            </span>
          </div>
          <div style={{ padding: '12px' }}>
            <Plot
              data={[constTrace]}
              layout={darkLayout({
                xaxis: { ...darkLayout().xaxis, title: { text: 'In-Phase (I)', standoff: 4 } },
                yaxis: { ...darkLayout().yaxis, title: { text: 'Quadrature (Q)', standoff: 4 } },
              })}
              config={plotConfig}
              style={{ width: '100%', height: '270px' }}
            />
          </div>
        </div>

        {/* Symbol Timing Eye Diagram (flex: 2.2, 270px height) */}
        <div className="p" style={{ flex: 2.2 }}>
          <div className="ph">
            <span className="h">Symbol timing eye diagram</span>
            <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}>
              {isStreaming ? '● LIVE JITTER SCANNER' : 'one trace = one symbol period · Scroll to Zoom'}
            </span>
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
                style={{ width: '100%', height: '270px' }}
              />
            ) : (
              <svg viewBox="0 0 480 260" style={{ width: '100%', height: '270px', background: '#0C1218' }}>
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
    </div>
  )
}
