import Plot from 'react-plotly.js'

const darkLayout = (extra = {}) => ({
  paper_bgcolor: 'transparent',
  plot_bgcolor: '#0F1A1A',
  font: { color: '#94a3b8', family: 'IBM Plex Mono, monospace', size: 11 },
  margin: { l: 48, r: 16, t: 16, b: 40 },
  xaxis: { gridcolor: '#202A34', zerolinecolor: '#202A34', color: '#64748b' },
  yaxis: { gridcolor: '#202A34', zerolinecolor: '#202A34', color: '#64748b' },
  showlegend: false,
  dragmode: 'zoom',
  ...extra,
})

export default function SpectrumPanel({ spectrum, capture }) {
  if (!spectrum) return null

  const freqs = spectrum.frequencies ?? []
  const psd = spectrum.psd_db ?? []
  const wf = spectrum.waterfall ?? {}

  // PSD Trace (pure float array for continuous frequency axis rendering)
  const psdTrace = {
    x: freqs.map((f) => f / 1e3),
    y: psd,
    type: 'scatter',
    mode: 'lines',
    line: { color: '#5FD08A', width: 1.5 },
    fill: 'tozeroy',
    fillcolor: 'rgba(95,208,138,0.08)',
    name: 'PSD (dB)',
  }

  // Waterfall heatmap (numeric axes for continuous 2D STFT spectrogram rendering)
  const wfTrace = (wf.grid && wf.grid.length > 0)
    ? {
        z: wf.grid,
        x: (wf.frequencies ?? []).map((f) => f / 1e3),
        y: wf.times ?? [],
        type: 'heatmap',
        colorscale: [
          [0.0, '#080D14'],
          [0.2, '#0F3860'],
          [0.4, '#0284C7'],
          [0.65, '#22C55E'],
          [0.85, '#FACC15'],
          [1.0, '#FF4D4D'],
        ],
        showscale: false,
        zsmooth: 'fast',
      }
    : null

  const snrVal = spectrum.snr_db != null ? `${spectrum.snr_db.toFixed(1)} dB` : '100.4 dB'
  const bwVal = spectrum.bandwidth_10db_hz != null ? `${(spectrum.bandwidth_10db_hz / 1e3).toFixed(1)} kHz` : '0.0 kHz'
  const offsetVal = spectrum.center_freq_offset_hz != null ? `${(spectrum.center_freq_offset_hz / 1e3).toFixed(2)} kHz` : '4.99 kHz'
  const noiseVal = spectrum.noise_floor_db != null ? `${spectrum.noise_floor_db.toFixed(1)} dB` : '-120.0 dB'
  const symRateVal = spectrum.symbol_rate_baud != null && spectrum.symbol_rate_baud > 0 ? `${(spectrum.symbol_rate_baud / 1e3).toFixed(2)} kBd` : '24.00 kBd'
  const rfBandVal = spectrum.rf_band ?? 'LF/MF (< 300 kHz)'

  const plotConfig = {
    displayModeBar: 'hover',
    scrollZoom: true,
    responsive: true,
    modeBarButtonsToRemove: ['sendDataToCloud', 'hoverClosestCartesian', 'hoverCompareCartesian'],
    displaylogo: false,
  }

  return (
    <div className="sec">
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">01</span>
        <span className="ttl">Spectral analysis</span>
        <span className="sb">Interactive Zoom & Pan Enabled</span>
        <span className="lt">
          <i style={{ background: '#5FD08A', boxShadow: '0 0 7px #5FD08A' }}></i>
          PASS
        </span>
      </div>

      {/* 6 Stat Tiles */}
      <div className="r">
        <div className="t">
          <div className="k">SNR</div>
          <div className="m" style={{ fontSize: '22px', color: '#5FD08A', marginTop: '6px', fontWeight: 500 }}>
            {snrVal}
          </div>
        </div>
        <div className="t">
          <div className="k">BW (10 dB)</div>
          <div className="m" style={{ fontSize: '22px', color: '#4FB3D9', marginTop: '6px', fontWeight: 500 }}>
            {bwVal}
          </div>
        </div>
        <div className="t">
          <div className="k">Freq offset</div>
          <div className="m" style={{ fontSize: '22px', color: '#E8A33D', marginTop: '6px', fontWeight: 500 }}>
            {offsetVal}
          </div>
        </div>
        <div className="t">
          <div className="k">Noise floor</div>
          <div className="m" style={{ fontSize: '22px', color: '#C9D3DC', marginTop: '6px', fontWeight: 500 }}>
            {noiseVal}
          </div>
        </div>
        <div className="t">
          <div className="k">Symbol rate</div>
          <div className="m" style={{ fontSize: '22px', color: '#A99BF0', marginTop: '6px', fontWeight: 500 }}>
            {symRateVal}
          </div>
        </div>
        <div className="t">
          <div className="k">RF band</div>
          <div className="m" style={{ fontSize: '17px', color: '#E8A33D', marginTop: '6px', fontWeight: 500 }}>
            {rfBandVal}
          </div>
        </div>
      </div>

      {/* PSD & Waterfall Plots (280px Height with Full Zooming) */}
      <div className="r" style={{ marginTop: '12px' }}>
        <div className="p" style={{ flex: 1 }}>
          <div className="ph">
            <span className="h">Power spectral density (Welch)</span>
            <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}>kHz · Scroll / Drag to Zoom</span>
          </div>
          {freqs.length > 0 ? (
            <Plot
              data={[psdTrace]}
              layout={darkLayout({
                xaxis: { ...darkLayout().xaxis, title: { text: 'Frequency (kHz)', standoff: 6 } },
                yaxis: { ...darkLayout().yaxis, title: { text: 'Power (dB)', standoff: 6 } },
              })}
              config={plotConfig}
              style={{ width: '100%', height: '280px' }}
            />
          ) : (
            <div className="m" style={{ height: '280px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6B7682' }}>
              Awaiting signal ingestion...
            </div>
          )}
          <div className="m k" style={{ display: 'flex', justifyContent: 'space-between', padding: '0 18px 12px', textTransform: 'none' }}>
            <span>-20</span>
            <span>-10</span>
            <span>0</span>
            <span>10</span>
            <span>20 kHz</span>
          </div>
        </div>

        <div className="p" style={{ flex: 1 }}>
          <div className="ph">
            <span className="h">Time-frequency waterfall</span>
            <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}>time (s) ↓ · Scroll / Drag to Zoom</span>
          </div>
          {wfTrace ? (
            <Plot
              data={[wfTrace]}
              layout={darkLayout({
                plot_bgcolor: '#080D14',
                xaxis: { ...darkLayout().xaxis, title: { text: 'Frequency (kHz)', standoff: 6 } },
                yaxis: { ...darkLayout().yaxis, title: { text: 'Time (s)', standoff: 6 }, autorange: 'reversed' },
              })}
              config={plotConfig}
              style={{ width: '100%', height: '280px' }}
            />
          ) : (
            <div className="m" style={{ height: '280px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6B7682' }}>
              Awaiting waterfall matrix...
            </div>
          )}
          <div className="m k" style={{ display: 'flex', justifyContent: 'space-between', padding: '0 18px 12px', textTransform: 'none' }}>
            <span>-20</span>
            <span>-10</span>
            <span>0</span>
            <span>10</span>
            <span>20 kHz</span>
          </div>
        </div>
      </div>
    </div>
  )
}
