export default function AMCPanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}
  const mod = r.modulation ?? 'UNKNOWN'
  const conf = r.confidence ?? 0.584
  const symRate = r.symbol_rate_baud ?? 24000
  const isLowConf = conf < 0.65

  const ALL_CLASSES = ['BPSK', 'QPSK', '8PSK', '2FSK', '4FSK', '16QAM', '64QAM']
  const activeSegments = Math.round(conf * 30)

  return (
    <div className="sec" style={{ flex: 1 }}>
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">02</span>
        <span className="ttl">Automatic modulation classification</span>
        <span className="sb"></span>
        <span className="lt">
          <i style={{ background: isLowConf ? '#E8A33D' : '#5FD08A', boxShadow: `0 0 7px ${isLowConf ? '#E8A33D' : '#5FD08A'}` }}></i>
          {isLowConf ? 'LOW CONF' : 'PASS'}
        </span>
      </div>

      <div className="p" style={{ minHeight: '318px' }}>
        <div className="ph">
          <span className="h">Classification verdict</span>
          <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}></span>
        </div>

        <div className="b">
          <div className="r" style={{ alignItems: 'flex-end', gap: '20px' }}>
            <div>
              <div className="k">Modulation</div>
              <div className="m" style={{ fontSize: '34px', color: '#4FB3D9', fontWeight: 500 }}>
                {mod}
              </div>
            </div>
            <div>
              <div className="k">Confidence</div>
              <div className="m" style={{ fontSize: '22px', color: isLowConf ? '#F0605D' : '#5FD08A', fontWeight: 500, marginBottom: '3px' }}>
                {(conf * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* 30-Segmented Confidence Bar */}
          <div style={{ display: 'flex', gap: '2px', margin: '12px 0' }}>
            {Array.from({ length: 30 }).map((_, i) => (
              <i
                key={i}
                style={{
                  flex: 1,
                  height: '14px',
                  background: i < activeSegments ? (isLowConf ? '#F0605D' : '#5FD08A') : '#1C232B',
                  borderRadius: '1px',
                }}
              />
            ))}
          </div>

          <div className="t" style={{ flex: 'none', width: '200px' }}>
            <div className="k">Symbol rate</div>
            <div className="m" style={{ color: '#4FB3D9', marginTop: '4px' }}>
              {(symRate / 1e3).toFixed(2)} kBaud
            </div>
          </div>

          {/* Classes Evaluated Chips */}
          <div style={{ marginTop: '12px' }}>
            <div className="k" style={{ marginBottom: '6px' }}>Classes evaluated</div>
            <div className="r" style={{ flexWrap: 'wrap', gap: '6px' }}>
              {ALL_CLASSES.map((c) => {
                const isSelected = c.toUpperCase() === mod.toUpperCase()
                return (
                  <span key={c} className={`cp ${isSelected ? 'cs' : ''}`}>
                    {isSelected ? `✓ ${c}` : c}
                  </span>
                )
              })}
            </div>
          </div>

          {/* Decision Rationale Text Block */}
          <div
            className="m"
            style={{
              marginTop: '12px',
              background: '#12171D',
              border: '1px solid #232C36',
              borderLeft: '3px solid #4FB3D9',
              padding: '10px 12px',
              fontSize: '13px',
              lineHeight: 1.6,
              color: '#B4C0CB',
            }}
          >
            {result.explanation || r.reason || `Modulation classified as ${mod} with ${(conf * 100).toFixed(1)}% confidence.`}
          </div>
        </div>
      </div>
    </div>
  )
}
