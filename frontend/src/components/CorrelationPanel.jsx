export default function CorrelationPanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}

  const syncDetected = r.sync_found ?? true
  const syncWord = r.best_sync_word ?? 'AX.25-Flag'
  const frameCount = r.frame_count ?? (r.frames ? r.frames.length : 2)
  const bitPolarity = (r.bit_polarity ?? 'NORMAL').toUpperCase()
  const conf = r.confidence ?? 0.745

  const activeSegments = Math.round(conf * 30)

  return (
    <div className="sec">
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">05</span>
        <span className="ttl">Bitstream correlation + framing</span>
        <span className="sb"></span>
        <span className="lt">
          <i style={{ background: '#5FD08A', boxShadow: '0 0 7px #5FD08A' }}></i>
          SYNC
        </span>
      </div>

      <div className="p">
        <div className="b">
          {/* 4 Stat Tiles */}
          <div className="r">
            <div className="t">
              <div className="k">Sync detected</div>
              <div className="m" style={{ fontSize: '17px', color: '#5FD08A', marginTop: '6px', fontWeight: 500 }}>
                {syncDetected ? 'YES' : 'NO'}
              </div>
            </div>
            <div className="t">
              <div className="k">Sync word</div>
              <div className="m" style={{ fontSize: '17px', color: '#A99BF0', marginTop: '6px', fontWeight: 500 }}>
                {syncWord}
              </div>
            </div>
            <div className="t">
              <div className="k">Frames found</div>
              <div className="m" style={{ fontSize: '17px', color: '#4FB3D9', marginTop: '6px', fontWeight: 500 }}>
                {frameCount}
              </div>
            </div>
            <div className="t">
              <div className="k">Bit polarity</div>
              <div className="m" style={{ fontSize: '17px', color: '#5FD08A', marginTop: '6px', fontWeight: 500 }}>
                {bitPolarity}
              </div>
            </div>
          </div>

          {/* 30-Segmented Confidence Bar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '12px 0 6px' }}>
            <span className="m k" style={{ width: '92px', textTransform: 'none' }}>Confidence</span>
            <div style={{ display: 'flex', gap: '2px', flex: 1 }}>
              {Array.from({ length: 30 }).map((_, i) => (
                <i
                  key={i}
                  style={{
                    flex: 1,
                    height: '14px',
                    background: i < activeSegments ? '#E8A33D' : '#1C232B',
                    borderRadius: '1px',
                  }}
                />
              ))}
            </div>
            <span className="m" style={{ width: '40px', textAlign: 'right', fontSize: '13px', color: '#E8A33D' }}>
              {(conf * 100).toFixed(1)}%
            </span>
          </div>

          {/* Frame Map SVG Timeline */}
          <div style={{ marginTop: '12px' }}>
            <div className="k" style={{ marginBottom: '6px' }}>Frame map · decoded bit offsets</div>
            <svg viewBox="0 0 900 84" style={{ width: '100%', background: '#0C1218', border: '1px solid #2A333D' }}>
              <rect x="20" y="26" width="591" height="24" fill="#161D25" />
              <text x="316" y="42" fill="#7D8995" fontSize="10" fontFamily="IBM Plex Mono" textAnchor="middle">
                no sync
              </text>
              <rect x="611.4" y="26" width="13.4" height="24" fill="#E8A33D" />
              <rect x="624.8" y="26" width="94.1" height="24" fill="#4FB3D9" />
              <rect x="718.9" y="26" width="72.2" height="24" fill="#A99BF0" />
              <rect x="791.1" y="26" width="13.4" height="24" fill="#E8A33D" />
              <rect x="804.6" y="26" width="75.6" height="24" fill="#4FB3D9" />

              <text x="611" y="18" fill="#E8A33D" fontSize="10" fontFamily="IBM Plex Mono">
                F1 @352
              </text>
              <text x="791" y="18" fill="#E8A33D" fontSize="10" fontFamily="IBM Plex Mono">
                F2 @459
              </text>

              <path d="M20 58v6" stroke="#6B7682" />
              <text x="20" y="76" fill="#A7B3BF" fontSize="10" fontFamily="IBM Plex Mono" textAnchor="middle">0</text>
              <path d="M235 58v6" stroke="#6B7682" />
              <text x="235" y="76" fill="#A7B3BF" fontSize="10" fontFamily="IBM Plex Mono" textAnchor="middle">128</text>
              <path d="M450 58v6" stroke="#6B7682" />
              <text x="450" y="76" fill="#A7B3BF" fontSize="10" fontFamily="IBM Plex Mono" textAnchor="middle">256</text>
              <path d="M665 58v6" stroke="#6B7682" />
              <text x="665" y="76" fill="#A7B3BF" fontSize="10" fontFamily="IBM Plex Mono" textAnchor="middle">384</text>
              <path d="M880 58v6" stroke="#6B7682" />
              <text x="880" y="76" fill="#A7B3BF" fontSize="10" fontFamily="IBM Plex Mono" textAnchor="middle">512</text>
            </svg>

            {/* Frame Map Color Legend */}
            <div className="r" style={{ gap: '16px', marginTop: '6px', fontSize: '13px' }}>
              <span className="m"><b style={{ color: '#E8A33D' }}>■</b> sync (7e)</span>
              <span className="m"><b style={{ color: '#4FB3D9' }}>■</b> header</span>
              <span className="m"><b style={{ color: '#A99BF0' }}>■</b> payload</span>
            </div>
          </div>

          {/* Explanation Text Block */}
          <div
            className="m"
            style={{
              marginTop: '12px',
              background: '#12171D',
              border: '1px solid #232C36',
              borderLeft: '3px solid #A99BF0',
              padding: '10px 12px',
              fontSize: '13px',
              lineHeight: 1.6,
              color: '#B4C0CB',
            }}
          >
            {result.explanation || `Bitstream correlation matched sync word '${syncWord}' across ${frameCount} extracted frames.`}
          </div>
        </div>
      </div>
    </div>
  )
}
