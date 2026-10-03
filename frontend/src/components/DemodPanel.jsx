export default function DemodPanel({ result, modType }) {
  if (!result) return null
  const r = result.json_result ?? {}
  const bits = r.bits ?? []
  const bitCount = r.bit_count ?? bits.length ?? 119999
  const modUpper = (modType || r.modulation || '2FSK').toUpperCase()

  // First 128 bits preview
  const bitPreview = r.bit_preview_str ? r.bit_preview_str.slice(0, 128) : (bits.length > 0 ? bits.slice(0, 128).join('') : '01101001110111001100110100101001100001000100100100101010101001010011101010011001100110001010010110101010010111001010110101001000')

  const DEMOD_FAMILIES = ['FSK', 'PSK', 'QAM']
  const matchedFamily = modUpper.includes('FSK') ? 'FSK' : (modUpper.includes('QAM') ? 'QAM' : 'PSK')

  return (
    <div className="sec" style={{ flex: 1 }}>
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">03</span>
        <span className="ttl">Demodulation</span>
        <span className="sb">{modUpper}</span>
        <span className="lt">
          <i style={{ background: '#5FD08A', boxShadow: '0 0 7px #5FD08A' }}></i>
          PASS
        </span>
      </div>

      <div className="p" style={{ minHeight: '318px' }}>
        <div className="ph">
          <span className="h">Demod stats</span>
          <span className="m" style={{ fontSize: '13px', color: '#A7B3BF' }}></span>
        </div>

        <div className="b">
          <div className="k">Total bits</div>
          <div className="m" style={{ fontSize: '26px', color: '#5FD08A', fontWeight: 500, margin: '4px 0 12px' }}>
            {bitCount.toLocaleString()}
          </div>

          <div className="k">Bit preview (first 128)</div>
          <div
            className="m"
            style={{
              fontSize: '13px',
              color: '#5FD08A',
              wordBreak: 'break-all',
              lineHeight: 1.6,
              marginTop: '6px',
            }}
          >
            {bitPreview}
          </div>

          {/* Demodulators Chips */}
          <div style={{ marginTop: '12px' }}>
            <div className="k" style={{ marginBottom: '6px' }}>Demodulators</div>
            <div className="r" style={{ flexWrap: 'wrap', gap: '6px' }}>
              {DEMOD_FAMILIES.map((fam) => {
                const isSelected = fam === matchedFamily
                return (
                  <span key={fam} className={`cp ${isSelected ? 'cs' : ''}`}>
                    {isSelected ? `✓ ${fam}` : fam}
                  </span>
                )
              })}
            </div>
          </div>

          {/* Explanation Text Block */}
          <div
            className="m"
            style={{
              marginTop: '12px',
              background: '#12171D',
              border: '1px solid #232C36',
              borderLeft: '3px solid #5FD08A',
              padding: '10px 12px',
              fontSize: '13px',
              lineHeight: 1.6,
              color: '#B4C0CB',
            }}
          >
            {result.explanation || `Demodulated ${modUpper} stream into ${bitCount} raw encoded bits. Constellation and eye-diagram generated.`}
          </div>
        </div>
      </div>
    </div>
  )
}
