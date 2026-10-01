import Plot from 'react-plotly.js'

const darkLayout = (extra = {}) => ({
  paper_bgcolor: 'transparent',
  plot_bgcolor: '#0d1422',
  font: { color: '#94a3b8', family: 'JetBrains Mono, monospace', size: 11 },
  margin: { l: 40, r: 16, t: 24, b: 40 },
  xaxis: { gridcolor: '#1e293b', zerolinecolor: '#334155', color: '#64748b' },
  yaxis: { gridcolor: '#1e293b', zerolinecolor: '#334155', color: '#64748b' },
  showlegend: false,
  ...extra,
})

export default function DemodPanel({ result, modType }) {
  if (!result) return null
  const r = result.json_result ?? {}

  const bits         = r.bits ?? []
  const bitCount     = r.bit_count ?? bits.length
  const constI       = r.constellation_i ?? []
  const constQ       = r.constellation_q ?? []
  const eyeI         = r.eye_diagram_i ?? []
  const eyeTime      = r.eye_diagram_time ?? []

  // Constellation scatter
  const constTrace = constI.length > 0 ? [{
    x: constI.slice(0, 2000),
    y: constQ.slice(0, 2000),
    type: 'scatter',
    mode: 'markers',
    marker: { color: '#00ff88', size: 2, opacity: 0.5 },
  }] : null

  // Eye diagram
  const eyeTrace = eyeI.length > 0 ? [{
    x: eyeTime,
    y: eyeI.slice(0, 2000),
    type: 'scatter',
    mode: 'lines',
    line: { color: '#00b4ff', width: 0.5 },
    opacity: 0.5,
  }] : null

  // Bit histogram (first 256 bits preview)
  const preview = bits.slice(0, 128)

  return (
    <section className="space-y-4">
      <h2 className="text-xs font-bold tracking-widest px-1" style={{ color: 'var(--accent-green)' }}>
        ▸ STAGE 3 · DEMODULATION · {modType ?? ''}
      </h2>

      <div className="flex flex-col gap-4">

        {/* Stats */}
        <div className="rounded-xl p-5 flex flex-col gap-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
          <div className="text-xs font-bold tracking-widest" style={{ color: 'var(--text-muted)' }}>DEMOD STATS</div>
          <div>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Total Bits</div>
            <div className="text-3xl font-bold" style={{ color: 'var(--accent-green)' }}>{bitCount.toLocaleString()}</div>
          </div>
          {r.ber !== undefined && (
            <div>
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>BER Estimate</div>
              <div className="text-xl font-bold" style={{ color: 'var(--accent-amber)' }}>{r.ber?.toExponential(2)}</div>
            </div>
          )}
          {/* Raw bits preview */}
          {preview.length > 0 && (
            <div>
              <div className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>BIT PREVIEW (first 128)</div>
              <div className="text-xs leading-5 break-all font-mono" style={{ color: 'var(--accent-green)', opacity: 0.8 }}>
                {preview.join('')}
              </div>
            </div>
          )}
          {result.explanation && (
            <p className="text-xs leading-relaxed p-3 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)', color: 'var(--text-muted)', borderLeft: '3px solid var(--accent-green)' }}>
              {result.explanation}
            </p>
          )}
        </div>

        {/* Constellation */}
        {constTrace && (
          <div className="rounded-xl p-5" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
            <div className="text-xs font-bold tracking-widest mb-3" style={{ color: 'var(--text-muted)' }}>CONSTELLATION DIAGRAM</div>
            <Plot
              data={constTrace}
              layout={darkLayout({
                xaxis: { ...darkLayout().xaxis, title: { text: 'I', standoff: 6 } },
                yaxis: { ...darkLayout().yaxis, title: { text: 'Q', standoff: 6 } },
              })}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '220px' }}
            />
          </div>
        )}

        {/* Eye diagram */}
        {eyeTrace && (
          <div className="rounded-xl p-5" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
            <div className="text-xs font-bold tracking-widest mb-3" style={{ color: 'var(--text-muted)' }}>EYE DIAGRAM</div>
            <Plot
              data={eyeTrace}
              layout={darkLayout({
                xaxis: { ...darkLayout().xaxis, title: { text: 'Time', standoff: 6 } },
                yaxis: { ...darkLayout().yaxis, title: { text: 'Amplitude', standoff: 6 } },
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
