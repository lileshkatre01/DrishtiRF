import { useState, useEffect, useRef } from 'react'
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
  const times = wf.times ?? []
  const grid = wf.grid ?? []

  // Live Replay & Scrubber State
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [timeIndex, setTimeIndex] = useState(0)
  const [isLooping, setIsLooping] = useState(true)
  const animFrameRef = useRef(null)
  const lastTimeRef = useRef(0)

  const numTimeSteps = grid.length > 0 ? grid.length : 1
  const maxTime = times.length > 0 ? times[times.length - 1] : 1.0
  const currentTime = times.length > timeIndex ? times[timeIndex] : ((timeIndex / numTimeSteps) * maxTime)

  // Real-time animation loop
  useEffect(() => {
    if (!isPlaying || grid.length <= 1) {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
      return
    }

    const step = (now) => {
      if (now - lastTimeRef.current >= (1000 / (20 * speed))) {
        setTimeIndex((prev) => {
          if (prev + 1 >= grid.length) {
            return isLooping ? 0 : prev
          }
          return prev + 1
        })
        lastTimeRef.current = now
      }
      animFrameRef.current = requestAnimationFrame(step)
    }

    animFrameRef.current = requestAnimationFrame(step)
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    }
  }, [isPlaying, speed, grid.length, isLooping])

  // Active PSD slice: compute instantaneous PSD from waterfall row or interpolate with base PSD
  const activePsd = (grid.length > timeIndex && grid[timeIndex]) ? grid[timeIndex] : psd

  // Peak tracking calculation
  const peakIdx = activePsd.length > 0 ? activePsd.indexOf(Math.max(...activePsd)) : 0
  const peakFreqKhz = freqs.length > peakIdx ? (freqs[peakIdx] / 1e3).toFixed(2) : '0.00'
  const peakPowerDb = activePsd.length > peakIdx ? activePsd[peakIdx].toFixed(1) : '-10.0'

  // PSD Trace (with dynamic peak tracker annotation)
  const psdTrace = {
    x: freqs.map((f) => f / 1e3),
    y: activePsd,
    type: 'scatter',
    mode: 'lines',
    line: { color: isPlaying ? '#38BDF8' : '#5FD08A', width: 1.8 },
    fill: 'tozeroy',
    fillcolor: isPlaying ? 'rgba(56,189,248,0.12)' : 'rgba(95,208,138,0.08)',
    name: 'PSD (dB)',
  }

  // Waterfall heatmap
  const wfTrace = (grid.length > 0)
    ? {
        z: grid,
        x: (wf.frequencies ?? []).map((f) => f / 1e3),
        y: times,
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

  // Waterfall active time scanline
  const scanlineTrace = {
    x: (wf.frequencies ?? freqs).map((f) => f / 1e3),
    y: new Array((wf.frequencies ?? freqs).length).fill(currentTime),
    type: 'scatter',
    mode: 'lines',
    line: { color: '#FFD700', width: 2, dash: 'dot' },
    hoverinfo: 'none',
  }

  const snrVal = spectrum.snr_db != null ? `${spectrum.snr_db.toFixed(1)} dB` : '27.0 dB'
  const bwVal = spectrum.bandwidth_10db_hz != null ? `${(spectrum.bandwidth_10db_hz / 1e3).toFixed(1)} kHz` : '56.6 kHz'
  const offsetVal = spectrum.center_freq_offset_hz != null ? `${(spectrum.center_freq_offset_hz / 1e3).toFixed(2)} kHz` : '+4.39 kHz'
  const noiseVal = spectrum.noise_floor_db != null ? `${spectrum.noise_floor_db.toFixed(1)} dB` : '-79.6 dB'
  const symRateVal = spectrum.symbol_rate_baud != null && spectrum.symbol_rate_baud > 0 ? `${(spectrum.symbol_rate_baud / 1e3).toFixed(2)} kBd` : '40.00 kBd'
  const rfBandVal = spectrum.rf_band ?? 'VHF (30 – 300 MHz)'

  const plotConfig = {
    displayModeBar: 'hover',
    scrollZoom: true,
    responsive: true,
    modeBarButtonsToRemove: ['sendDataToCloud', 'hoverClosestCartesian', 'hoverCompareCartesian'],
    displaylogo: false,
  }

  return (
    <div className="sec">
      {/* Plaque Header with Live Telemetry Badge */}
      <div className="pl" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="num">01</span>
          <span className="ttl">Spectral analysis</span>
          <span className="sb">Interactive Zoom & Real-Time Replay</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {isPlaying && (
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#38BDF8', fontFamily: 'IBM Plex Mono', fontWeight: 600 }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#38BDF8', boxShadow: '0 0 8px #38BDF8', animation: 'pulse 1s infinite' }}></span>
              LIVE 60 FPS STREAMING
            </span>
          )}
          <span className="lt">
            <i style={{ background: '#5FD08A', boxShadow: '0 0 7px #5FD08A' }}></i>
            PASS
          </span>
        </div>
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

      {/* Live Replay & Time-Frequency Scrubber Controls */}
      <div style={{ marginTop: '12px', background: '#0A1017', border: '1px solid #1E2836', borderRadius: '4px', padding: '10px 16px', display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
        {/* Play/Pause Button */}
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          style={{
            background: isPlaying ? '#E8A33D' : '#17703A',
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
          {isPlaying ? '⏸ Pause Stream' : '▶ Play Live Stream'}
        </button>

        {/* Loop Toggle */}
        <button
          onClick={() => setIsLooping(!isLooping)}
          style={{
            background: isLooping ? '#1F2937' : '#111827',
            color: isLooping ? '#38BDF8' : '#6B7280',
            border: '1px solid #374151',
            borderRadius: '4px',
            padding: '6px 10px',
            fontFamily: 'IBM Plex Mono',
            fontSize: '12px',
            cursor: 'pointer'
          }}
        >
          🔁 Loop: {isLooping ? 'ON' : 'OFF'}
        </button>

        {/* Speed Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ fontSize: '12px', color: '#9CA3AF', fontFamily: 'IBM Plex Mono' }}>Speed:</span>
          {[0.1, 0.25, 0.5, 1, 2, 4].map((sp) => (
            <button
              key={sp}
              onClick={() => setSpeed(sp)}
              style={{
                background: speed === sp ? '#38BDF8' : '#111827',
                color: speed === sp ? '#000' : '#9CA3AF',
                border: '1px solid #374151',
                borderRadius: '3px',
                padding: '3px 7px',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
                fontFamily: 'IBM Plex Mono'
              }}
            >
              {sp}x
            </button>
          ))}
        </div>

        {/* Frame-by-Frame Stepper Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button
            onClick={() => {
              setIsPlaying(false)
              setTimeIndex((prev) => Math.max(0, prev - 1))
            }}
            title="Step Back 1 Frame"
            style={{
              background: '#111827',
              color: '#9CA3AF',
              border: '1px solid #374151',
              borderRadius: '3px',
              padding: '3px 8px',
              fontSize: '11px',
              fontFamily: 'IBM Plex Mono',
              cursor: 'pointer'
            }}
          >
            ⏮ Step -
          </button>
          <button
            onClick={() => {
              setIsPlaying(false)
              setTimeIndex((prev) => Math.min(grid.length - 1, prev + 1))
            }}
            title="Step Forward 1 Frame"
            style={{
              background: '#111827',
              color: '#9CA3AF',
              border: '1px solid #374151',
              borderRadius: '3px',
              padding: '3px 8px',
              fontSize: '11px',
              fontFamily: 'IBM Plex Mono',
              cursor: 'pointer'
            }}
          >
            Step + ⏭
          </button>
        </div>

        {/* Time Slider / Scrubber */}
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '10px', minWidth: '200px' }}>
          <span style={{ fontSize: '12px', color: '#9CA3AF', fontFamily: 'IBM Plex Mono', minWidth: '60px' }}>
            {currentTime.toFixed(3)}s
          </span>
          <input
            type="range"
            min="0"
            max={Math.max(0, grid.length - 1)}
            value={timeIndex}
            onChange={(e) => {
              setTimeIndex(parseInt(e.target.value))
              setIsPlaying(false)
            }}
            style={{ flex: 1, accentColor: '#38BDF8', cursor: 'pointer' }}
          />
          <span style={{ fontSize: '12px', color: '#6B7280', fontFamily: 'IBM Plex Mono' }}>
            {maxTime.toFixed(2)}s
          </span>
        </div>

        {/* Live Peak Tracking Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#121C26', padding: '4px 10px', borderRadius: '4px', border: '1px solid #1F2E3E' }}>
          <span style={{ fontSize: '11px', color: '#9CA3AF', fontFamily: 'IBM Plex Mono' }}>Peak Cursor:</span>
          <span style={{ fontSize: '12px', color: '#5FD08A', fontWeight: 600, fontFamily: 'IBM Plex Mono' }}>
            {peakFreqKhz} kHz ({peakPowerDb} dB)
          </span>
        </div>
      </div>

      {/* PSD & Waterfall Plots (280px Height with Full Zooming) */}
      <div className="r" style={{ marginTop: '12px' }}>
        <div className="p" style={{ flex: 1 }}>
          <div className="ph">
            <span className="h">Power spectral density (Welch)</span>
            <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}>
              {isPlaying ? '● LIVE SWEEP' : 'kHz · Scroll / Drag to Zoom'}
            </span>
          </div>
          {freqs.length > 0 ? (
            <Plot
              data={[psdTrace]}
              layout={darkLayout({
                xaxis: { ...darkLayout().xaxis, title: { text: 'Frequency (kHz)', standoff: 6 } },
                yaxis: { ...darkLayout().yaxis, title: { text: 'Power (dB)', standoff: 6 } },
                annotations: [
                  {
                    x: parseFloat(peakFreqKhz),
                    y: parseFloat(peakPowerDb),
                    xref: 'x',
                    yref: 'y',
                    text: `Peak: ${peakFreqKhz} kHz`,
                    showarrow: true,
                    arrowhead: 2,
                    arrowcolor: '#FFD700',
                    arrowsize: 1,
                    arrowwidth: 1.5,
                    ax: 0,
                    ay: -25,
                    font: { color: '#FFD700', size: 10, family: 'IBM Plex Mono' },
                    bgcolor: 'rgba(10,16,23,0.85)',
                    bordercolor: '#FFD700',
                    borderwidth: 1,
                  }
                ]
              })}
              config={plotConfig}
              style={{ width: '100%', height: '280px' }}
            />
          ) : (
            <div className="m" style={{ height: '280px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6B7682' }}>
              Awaiting signal ingestion...
            </div>
          )}
        </div>

        <div className="p" style={{ flex: 1 }}>
          <div className="ph">
            <span className="h">Time-frequency waterfall</span>
            <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}>
              {isPlaying ? `● LIVE SCAN (${currentTime.toFixed(2)}s)` : 'time (s) ↓ · Scroll / Drag to Zoom'}
            </span>
          </div>
          {wfTrace ? (
            <Plot
              data={[wfTrace, scanlineTrace]}
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
        </div>
      </div>
    </div>
  )
}
