import Plot from 'react-plotly.js'

const darkLayout = (extra = {}) => ({
  paper_bgcolor: 'transparent',
  plot_bgcolor: '#0d1422',
  font: { color: '#94a3b8', family: 'JetBrains Mono, monospace', size: 11 },
  margin: { l: 54, r: 16, t: 28, b: 44 },
  xaxis: { gridcolor: '#1e293b', zerolinecolor: '#1e293b', color: '#64748b' },
  yaxis: { gridcolor: '#1e293b', zerolinecolor: '#1e293b', color: '#64748b' },
  showlegend: false,
  ...extra,
})

function Card({ title, children }) {
  return (
    <div className="rounded-xl p-5" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
      <h3 className="text-xs font-bold tracking-widest mb-4" style={{ color: 'var(--text-muted)' }}>{title}</h3>
      {children}
    </div>
  )
}

export default function SpectrumPanel({ spectrum, capture }) {
  if (!spectrum) return null

  const freqs = spectrum.frequencies ?? []
  const psd   = spectrum.psd_db ?? []
  const wf    = spectrum.waterfall ?? {}

  // PSD Trace
  const psdTrace = {
    x: freqs.map(f => (f / 1e3).toFixed(2)),
    y: psd,
    type: 'scatter',
    mode: 'lines',
    line: { color: '#00ff88', width: 1.5 },
    fill: 'tozeroy',
    fillcolor: 'rgba(0,255,136,0.07)',
    name: 'PSD (dB)',
  }

  // Waterfall heatmap
  const wfTrace = wf.grid ? {
    z: wf.grid,
    x: (wf.frequencies ?? []).map(f => (f / 1e3).toFixed(1)),
    y: wf.times ?? [],
    type: 'heatmap',
    colorscale: [
      [0, '#0a0e1a'], [0.2, '#00264d'], [0.5, '#00b4ff'],
      [0.8, '#00ff88'], [1, '#ffffff'],
    ],
    showscale: false,
    zsmooth: 'best',
  } : null

  // Stat cards
  const stats = [
    { label: 'SNR', value: spectrum.snr_db != null ? `${spectrum.snr_db.toFixed(1)} dB` : '—', color: 'var(--accent-green)' },
    { label: 'BW (10 dB)', value: spectrum.bandwidth_10db_hz != null ? `${(spectrum.bandwidth_10db_hz / 1e3).toFixed(1)} kHz` : '—', color: 'var(--accent-blue)' },
    { label: 'Freq Offset', value: spectrum.center_freq_offset_hz != null ? `${(spectrum.center_freq_offset_hz / 1e3).toFixed(2)} kHz` : '—', color: 'var(--accent-amber)' },
    { label: 'Noise Floor', value: spectrum.noise_floor_db != null ? `${spectrum.noise_floor_db.toFixed(1)} dB` : '—', color: 'var(--text-muted)' },
  ]

  return (
    <section className="space-y-4">
      <h2 className="text-xs font-bold tracking-widest px-1" style={{ color: 'var(--accent-green)' }}>
        ▸ STAGE 1 · SPECTRAL ANALYSIS
      </h2>

      {/* Stat row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {stats.map(s => (
          <div key={s.label} className="rounded-lg p-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{s.label}</div>
            <div className="text-xl font-bold mt-1" style={{ color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Plots */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {freqs.length > 0 && (
          <Card title="POWER SPECTRAL DENSITY (Welch)">
            <Plot
              data={[psdTrace]}
              layout={darkLayout({
                xaxis: { ...darkLayout().xaxis, title: { text: 'Frequency (kHz)', standoff: 8 } },
                yaxis: { ...darkLayout().yaxis, title: { text: 'Power (dB)', standoff: 8 } },
              })}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '240px' }}
            />
          </Card>
        )}

        {wfTrace && (
          <Card title="TIME-FREQUENCY WATERFALL">
            <Plot
              data={[wfTrace]}
              layout={darkLayout({
                xaxis: { ...darkLayout().xaxis, title: { text: 'Freq (kHz)', standoff: 8 } },
                yaxis: { ...darkLayout().yaxis, title: { text: 'Time (s)', standoff: 8 } },
              })}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '240px' }}
            />
          </Card>
        )}
      </div>
    </section>
  )
}
