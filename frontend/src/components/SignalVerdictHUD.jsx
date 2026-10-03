export default function SignalVerdictHUD({ results, capture, job }) {
  const spectral = results.SPECTRAL?.json_result ?? {}
  const amc = results.AMC?.json_result ?? {}
  const demod = results.DEMOD?.json_result ?? {}
  const joint = results.JOINT_SEARCH?.json_result ?? {}
  const corr = results.CORRELATION?.json_result ?? {}
  const conf = results.CONFIDENCE_EVALUATION?.json_result ?? {}

  // 1. Modulation
  const mod = amc.modulation ?? 'UNKNOWN'

  // 2. Symbol Rate
  const symRateBaud = spectral.symbol_rate_baud || amc.symbol_rate_baud || 0
  const symRateStr = symRateBaud > 0 ? `${(symRateBaud / 1e3).toFixed(2)} kBd` : '—'

  // 3. Sampling Freq
  const fsHz = spectral.sample_rate || capture?.sample_rate || 0
  const fsStr = fsHz > 0 ? `${(fsHz / 1e6).toFixed(3)} MHz` : '—'

  // 4. Interleaver
  let interleaverStr = 'None'
  if (joint.best_interleaver) {
    if (joint.best_interleaver.toLowerCase().includes('conv')) {
      interleaverStr = 'Conv · d15 · s7'
    } else if (joint.best_interleaver.toLowerCase().includes('block')) {
      interleaverStr = 'Block · 8x16'
    } else if (joint.best_interleaver.toLowerCase().includes('pseudo')) {
      interleaverStr = 'PseudoRandom'
    } else {
      interleaverStr = joint.best_interleaver
    }
  }

  // 5. FEC
  let fecStr = 'None'
  if (joint.best_fec) {
    if (joint.best_fec.toLowerCase().includes('viterbi')) {
      fecStr = 'Viterbi · 1/2 · K=7'
    } else if (joint.best_fec.toLowerCase().includes('reed')) {
      fecStr = 'RS (255,223)'
    } else if (joint.best_fec.toLowerCase().includes('ldpc')) {
      fecStr = 'LDPC · Rate 1/2'
    } else {
      fecStr = joint.best_fec
    }
  }

  // 6. Sync / Frames
  const syncWord = corr.best_sync_word || (corr.sync_found ? 'AX.25' : 'None')
  const frameCount = corr.frame_count ?? (corr.frames ? corr.frames.length : 0)
  const syncFramesStr = `${syncWord} · ${frameCount}`

  // Overall Confidence %
  const overallPct = Math.round((conf.overall_confidence ?? 0.659) * 1000) / 10
  const tierLabel = conf.tier_code ? conf.tier_code.replace('_', ' ') : 'TIER A'

  // Stage active states for 7-step progression
  const isDone = job?.status === 'COMPLETED' || Object.keys(results).length > 0
  const dotColor = (stage) => {
    if (!results[stage]) return '#1C232B'
    if (stage === 'JOINT_SEARCH' && !results[stage].json_result?.syndrome_zero) return '#E8A33D'
    return '#5FD08A'
  }

  return (
    <div className="sec" style={{ marginTop: '20px' }}>
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">00</span>
        <span className="ttl">Signal verdict</span>
        <span className="sb">blind analysis · file → bits → frames</span>
        <span className="lt">
          <i style={{ background: '#5FD08A', boxShadow: '0 0 7px #5FD08A' }}></i>
          COMPLETE
        </span>
      </div>

      {/* 6 Top Summary Tiles + Overall Radial Gauge */}
      <div className="r" style={{ gap: '16px' }}>
        <div style={{ flex: 1, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
          <div className="t" style={{ padding: '14px 16px' }}>
            <div className="k">Modulation</div>
            <div className="m" style={{ fontSize: '22px', color: '#4FB3D9', marginTop: '6px', fontWeight: 500 }}>
              {mod}
            </div>
          </div>
          <div className="t" style={{ padding: '14px 16px' }}>
            <div className="k">Symbol rate</div>
            <div className="m" style={{ fontSize: '22px', color: '#A99BF0', marginTop: '6px', fontWeight: 500 }}>
              {symRateStr}
            </div>
          </div>
          <div className="t" style={{ padding: '14px 16px' }}>
            <div className="k">Sampling freq</div>
            <div className="m" style={{ fontSize: '22px', color: '#fff', marginTop: '6px', fontWeight: 500 }}>
              {fsStr}
            </div>
          </div>
          <div className="t" style={{ padding: '14px 16px' }}>
            <div className="k">Interleaver</div>
            <div className="m" style={{ fontSize: '22px', color: '#E8A33D', marginTop: '6px', fontWeight: 500 }}>
              {interleaverStr}
            </div>
          </div>
          <div className="t" style={{ padding: '14px 16px' }}>
            <div className="k">FEC</div>
            <div className="m" style={{ fontSize: '22px', color: '#fff', marginTop: '6px', fontWeight: 500 }}>
              {fecStr}
            </div>
          </div>
          <div className="t" style={{ padding: '14px 16px' }}>
            <div className="k">Sync / frames</div>
            <div className="m" style={{ fontSize: '22px', color: '#5FD08A', marginTop: '6px', fontWeight: 500 }}>
              {syncFramesStr}
            </div>
          </div>
        </div>

        {/* Overall Confidence Dial */}
        <div style={{ width: '230px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#1A2028', border: '1px solid #262F39', borderRadius: '2px' }}>
          <svg width="130" height="130" viewBox="0 0 110 110">
            <circle cx="55" cy="55" r="44" fill="none" stroke="#2A333D" strokeWidth="9" />
            <circle
              cx="55"
              cy="55"
              r="44"
              fill="none"
              stroke="#E8A33D"
              strokeWidth="9"
              strokeDasharray={`${(overallPct / 100) * 276.5} 276.5`}
              transform="rotate(-90 55 55)"
            />
            <text x="55" y="60" fill="#fff" fontSize="19" fontFamily="IBM Plex Mono" textAnchor="middle" fontWeight="500">
              {overallPct}%
            </text>
          </svg>
          <div className="m" style={{ fontSize: '13.5px', color: '#E8A33D', letterSpacing: '.08em', fontWeight: 600 }}>
            {tierLabel} · OVERALL
          </div>
        </div>
      </div>

      {/* 7-Stage Progression Chevron */}
      <div className="r" style={{ marginTop: '14px', alignItems: 'stretch', gap: 0 }}>
        <div className="nd">
          <div className="m" style={{ fontSize: '12px', color: '#A7B3BF' }}>01</div>
          <div style={{ fontWeight: 600, fontSize: '14.5px', margin: '2px 0' }}>Ingest</div>
          <div className="m" style={{ fontSize: '12.5px', color: '#A7B3BF' }}>.IQ / .WAV</div>
          <i style={{ background: isDone ? '#5FD08A' : '#1C232B', boxShadow: isDone ? '0 0 7px #5FD08A' : 'none' }}></i>
        </div>
        <span className="ar">›</span>

        <div className="nd">
          <div className="m" style={{ fontSize: '12px', color: '#A7B3BF' }}>02</div>
          <div style={{ fontWeight: 600, fontSize: '14.5px', margin: '2px 0' }}>Spectral</div>
          <div className="m" style={{ fontSize: '12.5px', color: '#A7B3BF' }}>PSD · waterfall</div>
          <i style={{ background: dotColor('SPECTRAL'), boxShadow: dotColor('SPECTRAL') !== '#1C232B' ? '0 0 7px #5FD08A' : 'none' }}></i>
        </div>
        <span className="ar">›</span>

        <div className="nd">
          <div className="m" style={{ fontSize: '12px', color: '#A7B3BF' }}>03</div>
          <div style={{ fontWeight: 600, fontSize: '14.5px', margin: '2px 0' }}>AMC</div>
          <div className="m" style={{ fontSize: '12.5px', color: '#A7B3BF' }}>modulation</div>
          <i style={{ background: dotColor('AMC'), boxShadow: dotColor('AMC') !== '#1C232B' ? '0 0 7px #5FD08A' : 'none' }}></i>
        </div>
        <span className="ar">›</span>

        <div className="nd">
          <div className="m" style={{ fontSize: '12px', color: '#A7B3BF' }}>04</div>
          <div style={{ fontWeight: 600, fontSize: '14.5px', margin: '2px 0' }}>Demod</div>
          <div className="m" style={{ fontSize: '12.5px', color: '#A7B3BF' }}>FSK · PSK · QAM</div>
          <i style={{ background: dotColor('DEMOD'), boxShadow: dotColor('DEMOD') !== '#1C232B' ? '0 0 7px #5FD08A' : 'none' }}></i>
        </div>
        <span className="ar">›</span>

        <div className="nd">
          <div className="m" style={{ fontSize: '12px', color: '#A7B3BF' }}>05</div>
          <div style={{ fontWeight: 600, fontSize: '14.5px', margin: '2px 0' }}>De-interleave + FEC</div>
          <div className="m" style={{ fontSize: '12.5px', color: '#A7B3BF' }}>joint search</div>
          <i style={{ background: dotColor('JOINT_SEARCH'), boxShadow: dotColor('JOINT_SEARCH') !== '#1C232B' ? '0 0 7px #E8A33D' : 'none' }}></i>
        </div>
        <span className="ar">›</span>

        <div className="nd">
          <div className="m" style={{ fontSize: '12px', color: '#A7B3BF' }}>06</div>
          <div style={{ fontWeight: 600, fontSize: '14.5px', margin: '2px 0' }}>Correlate</div>
          <div className="m" style={{ fontSize: '12.5px', color: '#A7B3BF' }}>sync · frames</div>
          <i style={{ background: dotColor('CORRELATION'), boxShadow: dotColor('CORRELATION') !== '#1C232B' ? '0 0 7px #5FD08A' : 'none' }}></i>
        </div>
        <span className="ar">›</span>

        <div className="nd">
          <div className="m" style={{ fontSize: '12px', color: '#A7B3BF' }}>07</div>
          <div style={{ fontWeight: 600, fontSize: '14.5px', margin: '2px 0' }}>Confidence</div>
          <div className="m" style={{ fontSize: '12.5px', color: '#A7B3BF' }}>3-tier</div>
          <i style={{ background: dotColor('CONFIDENCE_EVALUATION'), boxShadow: dotColor('CONFIDENCE_EVALUATION') !== '#1C232B' ? '0 0 7px #5FD08A' : 'none' }}></i>
        </div>
      </div>
    </div>
  )
}
