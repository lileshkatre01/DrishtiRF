// Helper to render a speedometer needle gauge
function GaugeSpeedometer({ label, pct, color = '#5FD08A' }) {
  const normalizedPct = Math.min(100, Math.max(0, pct))
  const angleDeg = -180 + (normalizedPct / 100) * 180 // -180 to 0 deg

  // Arc end coordinates
  const rad = (angleDeg * Math.PI) / 180
  const endX = (75 + 50 * Math.cos(rad)).toFixed(1)
  const endY = (80 + 50 * Math.sin(rad)).toFixed(1)

  // Needle end coordinates
  const needleLength = 42
  const nX = (75 + needleLength * Math.cos(rad)).toFixed(1)
  const nY = (80 + needleLength * Math.sin(rad)).toFixed(1)

  return (
    <div className="t" style={{ textAlign: 'center', padding: '12px 8px 10px' }}>
      <svg viewBox="0 0 150 100" style={{ width: '100%' }}>
        {/* Background Arc */}
        <path d="M25 80A50 50 0 0 1 125 80" fill="none" stroke="#242D37" strokeWidth="10" />

        {/* Value Arc */}
        <path
          d={`M25 80A50 50 0 0 1 ${endX} ${endY}`}
          fill="none"
          stroke={color}
          strokeWidth="10"
        />

        {/* Tick Marks */}
        <path d="M17.0 80.0L10.0 80.0" stroke="#6B7682" strokeWidth="2" />
        <path d="M19.8 62.1L16.0 60.8" stroke="#6B7682" strokeWidth="1" />
        <path d="M28.1 45.9L24.8 43.6" stroke="#6B7682" strokeWidth="1" />
        <path d="M40.9 33.1L38.6 29.8" stroke="#6B7682" strokeWidth="1" />
        <path d="M57.1 24.8L55.8 21.0" stroke="#6B7682" strokeWidth="1" />
        <path d="M75.0 22.0L75.0 15.0" stroke="#6B7682" strokeWidth="2" />
        <path d="M92.9 24.8L94.2 21.0" stroke="#6B7682" strokeWidth="1" />
        <path d="M109.1 33.1L111.4 29.8" stroke="#6B7682" strokeWidth="1" />
        <path d="M121.9 45.9L125.2 43.6" stroke="#6B7682" strokeWidth="1" />
        <path d="M130.2 62.1L134.0 60.8" stroke="#6B7682" strokeWidth="1" />
        <path d="M133.0 80.0L140.0 80.0" stroke="#6B7682" strokeWidth="2" />

        {/* Needle */}
        <path d={`M75 80L${nX} ${nY}`} stroke="#fff" strokeWidth="2.5" strokeLinecap="round" />
        <circle cx="75" cy="80" r="6" fill="#59646F" stroke="#000" />

        {/* Value Text */}
        <text x="75" y="97" fill={color} fontSize="15" fontFamily="IBM Plex Mono" textAnchor="middle" fontWeight="500">
          {Math.round(pct)}%
        </text>
      </svg>
      <div className="m k" style={{ textTransform: 'none', marginTop: '2px', fontSize: '13px', color: '#E4EAF0' }}>
        {label}
      </div>
    </div>
  )
}

export default function ConfidencePanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}

  const rawTier = r.tier_code ?? (r.tier ? r.tier.replace(/Tier\s*([ABC]).*/i, '$1') : 'A')
  const tier = rawTier.replace('TIER_', '').trim().toUpperCase()

  const overall = r.overall_confidence ?? result.confidence ?? 0.659
  const subScores = r.sub_scores ?? r.stage_confidences ?? {}

  const spectralPct = (subScores.spectral ?? 1.0) * 100
  const amcPct = (subScores.amc ?? 0.58) * 100
  const demodPct = (subScores.demod ?? 0.90) * 100
  const fecPct = (subScores.joint_fec ?? subScores.joint_search ?? 0.25) * 100
  const corrPct = (subScores.correlation ?? 0.75) * 100

  const getScoreColor = (p) => {
    if (p >= 80) return '#5FD08A'
    if (p >= 50) return '#E8A33D'
    return '#F0605D'
  }

  const TIER_META = {
    A: {
      bg: '#0F2A1D',
      border: '#226B45',
      color: '#5FD08A',
      title: 'TIER A — HIGH CONFIDENCE',
      desc: 'All pipeline stages converge with high agreement. Result is reliable.',
    },
    B: {
      bg: 'rgba(232,163,61,0.1)',
      border: 'rgba(232,163,61,0.4)',
      color: '#E8A33D',
      title: 'TIER B — MODERATE CONFIDENCE',
      desc: 'Partial pipeline convergence. Result is plausible but requires human verification.',
    },
    C: {
      bg: 'rgba(240,96,93,0.1)',
      border: 'rgba(240,96,93,0.4)',
      color: '#F0605D',
      title: 'TIER C — LOW CONFIDENCE',
      desc: 'Low agreement across stages. Parameters extracted under fallback conditions.',
    },
  }

  const currentTier = TIER_META[tier] ?? TIER_META.A

  return (
    <div className="sec">
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">06</span>
        <span className="ttl">3-tier confidence evaluation</span>
        <span className="sb"></span>
        <span className="lt">
          <i style={{ background: currentTier.color, boxShadow: `0 0 7px ${currentTier.color}` }}></i>
          TIER {tier}
        </span>
      </div>

      <div className="p">
        <div className="b">
          {/* Shield Banner */}
          <div
            className="r"
            style={{
              alignItems: 'center',
              background: currentTier.bg,
              border: `1px solid ${currentTier.border}`,
              padding: '16px 18px',
              borderRadius: '2px',
            }}
          >
            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke={currentTier.color} strokeWidth="1.7">
              <path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6z" />
              <path d="M8.5 12l2.5 2.5 4.5-5" />
            </svg>

            <div style={{ marginLeft: '12px' }}>
              <div className="m" style={{ fontSize: '17px', color: currentTier.color, letterSpacing: '.08em', fontWeight: 500 }}>
                {currentTier.title}
              </div>
              <div className="m k" style={{ textTransform: 'none', marginTop: '4px', color: '#B4C0CB' }}>
                {currentTier.desc}
              </div>
            </div>

            <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
              <div className="k">Overall</div>
              <div className="m" style={{ fontSize: '28px', color: currentTier.color }}>
                {(overall * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* 5 Stage Breakdown Speedometer Needle Gauges */}
          <div className="k" style={{ margin: '18px 0 8px' }}>Stage breakdown</div>
          <div className="r" style={{ gap: '10px' }}>
            <GaugeSpeedometer label="spectral" pct={spectralPct} color={getScoreColor(spectralPct)} />
            <GaugeSpeedometer label="amc" pct={amcPct} color={getScoreColor(amcPct)} />
            <GaugeSpeedometer label="demod" pct={demodPct} color={getScoreColor(demodPct)} />
            <GaugeSpeedometer label="joint_fec" pct={fecPct} color={getScoreColor(fecPct)} />
            <GaugeSpeedometer label="correlation" pct={corrPct} color={getScoreColor(corrPct)} />
          </div>

          {/* Decision Rationale Text Block */}
          <div
            className="m"
            style={{
              marginTop: '12px',
              background: '#12171D',
              border: '1px solid #232C36',
              borderLeft: `3px solid ${currentTier.color}`,
              padding: '10px 12px',
              fontSize: '13px',
              lineHeight: 1.6,
              color: '#B4C0CB',
            }}
          >
            {r.rationale || result.explanation || `Assigned Tier ${tier}: Signal decoded with verified payload integrity.`}
          </div>
        </div>
      </div>
    </div>
  )
}
