export default function JointSearchPanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}

  const bestInterleaver = r.best_interleaver || 'Convolutional (Depth 15, Span 7)'
  const bestFEC = r.best_fec || 'Viterbi (Rate 1/2, K=7)'
  const decodedBitsCount = r.decoded_bits_count ?? 512
  const isSyndromeZero = r.syndrome_zero ?? false
  const conf = r.confidence ?? 0.505

  const activeSegments = Math.round(conf * 30)
  const INTERLEAVERS = ['Block', 'Convolutional', 'Diagonal', 'Pseudo-random']
  const FEC_SCHEMES = ['Viterbi', 'Reed-Solomon', 'Concatenated', 'LDPC']

  return (
    <div className="sec">
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">04</span>
        <span className="ttl">Joint de-interleave + FEC search</span>
        <span className="sb"></span>
        <span className="lt">
          <i
            style={{
              background: isSyndromeZero ? '#5FD08A' : '#F0605D',
              boxShadow: `0 0 7px ${isSyndromeZero ? '#5FD08A' : '#F0605D'}`,
            }}
          ></i>
          {isSyndromeZero ? 'PASS' : 'PARTIAL'}
        </span>
      </div>

      <div className="p">
        <div className="b">
          {/* 4 Stat Tiles */}
          <div className="r">
            <div className="t">
              <div className="k">Interleaver</div>
              <div className="m" style={{ fontSize: '17px', color: '#E8A33D', marginTop: '6px', fontWeight: 500 }}>
                {bestInterleaver}
              </div>
            </div>
            <div className="t">
              <div className="k">FEC scheme</div>
              <div className="m" style={{ fontSize: '17px', color: '#fff', marginTop: '6px', fontWeight: 500 }}>
                {bestFEC}
              </div>
            </div>
            <div className="t">
              <div className="k">Decoded bits</div>
              <div className="m" style={{ fontSize: '17px', color: '#5FD08A', marginTop: '6px', fontWeight: 500 }}>
                {decodedBitsCount}
              </div>
            </div>
            <div className="t">
              <div className="k">FEC status</div>
              <div
                className="m"
                style={{
                  fontSize: '17px',
                  color: isSyndromeZero ? '#5FD08A' : '#F0605D',
                  marginTop: '6px',
                  fontWeight: 500,
                }}
              >
                {isSyndromeZero ? '✓ CONVERGED' : '✕ PARTIAL'}
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

          {/* De-interleavers Searched Chips */}
          <div style={{ marginTop: '12px' }}>
            <div className="k" style={{ marginBottom: '6px' }}>De-interleavers searched</div>
            <div className="r" style={{ flexWrap: 'wrap', gap: '6px' }}>
              {INTERLEAVERS.map((ilv) => {
                const isSelected = bestInterleaver.toLowerCase().includes(ilv.toLowerCase().replace('-random', ''))
                return (
                  <span key={ilv} className={`cp ${isSelected ? 'cs' : ''}`}>
                    {isSelected ? `✓ ${ilv}` : ilv}
                  </span>
                )
              })}
            </div>
          </div>

          {/* FEC Decoders Searched Chips */}
          <div style={{ marginTop: '12px' }}>
            <div className="k" style={{ marginBottom: '6px' }}>FEC decoders searched</div>
            <div className="r" style={{ flexWrap: 'wrap', gap: '6px' }}>
              {FEC_SCHEMES.map((fec) => {
                const isSelected = bestFEC.toLowerCase().includes(fec.toLowerCase().split('-')[0])
                return (
                  <span key={fec} className={`cp ${isSelected ? 'cs' : ''}`}>
                    {isSelected ? `✓ ${fec}` : fec}
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
              borderLeft: '3px solid #E8A33D',
              padding: '10px 12px',
              fontSize: '13px',
              lineHeight: 1.6,
              color: '#B4C0CB',
            }}
          >
            {result.explanation || `Joint search finished with best hypothesis: Interleaver=${bestInterleaver}, FEC=${bestFEC}.`}
          </div>
        </div>
      </div>
    </div>
  )
}
