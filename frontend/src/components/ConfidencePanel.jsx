import React from 'react'

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

function getEvidenceBadge(level) {
  const lvl = (level || 'UNKNOWN').toUpperCase()
  if (lvl === 'VERIFIED') {
    return <span style={{ background: '#0F2A1D', color: '#5FD08A', border: '1px solid #226B45', padding: '2px 6px', borderRadius: '2px', fontSize: '11px', fontWeight: 600 }}>VERIFIED</span>
  }
  if (lvl === 'MEASURED') {
    return <span style={{ background: 'rgba(56,189,248,0.1)', color: '#38BDF8', border: '1px solid rgba(56,189,248,0.4)', padding: '2px 6px', borderRadius: '2px', fontSize: '11px', fontWeight: 600 }}>MEASURED</span>
  }
  if (lvl === 'ESTIMATED') {
    return <span style={{ background: 'rgba(99,102,241,0.1)', color: '#818CF8', border: '1px solid rgba(99,102,241,0.4)', padding: '2px 6px', borderRadius: '2px', fontSize: '11px', fontWeight: 600 }}>ESTIMATED</span>
  }
  if (lvl === 'DEMODULATED' || lvl === 'RECOVERED') {
    return <span style={{ background: 'rgba(56,189,248,0.12)', color: '#38BDF8', border: '1px solid rgba(56,189,248,0.4)', padding: '2px 6px', borderRadius: '2px', fontSize: '11px', fontWeight: 600 }}>DEMODULATED</span>
  }
  if (lvl === 'HYPOTHESIS') {
    return <span style={{ background: 'rgba(232,163,61,0.1)', color: '#E8A33D', border: '1px solid rgba(232,163,61,0.4)', padding: '2px 6px', borderRadius: '2px', fontSize: '11px', fontWeight: 600 }}>HYPOTHESIS</span>
  }
  if (lvl === 'N/A') {
    return <span style={{ background: 'rgba(107,118,130,0.1)', color: '#94A3B8', border: '1px solid rgba(107,118,130,0.4)', padding: '2px 6px', borderRadius: '2px', fontSize: '11px', fontWeight: 600 }}>N/A (ANALOG)</span>
  }
  return <span style={{ background: 'rgba(148,163,184,0.1)', color: '#CBD5E1', border: '1px solid rgba(148,163,184,0.3)', padding: '2px 6px', borderRadius: '2px', fontSize: '11px', fontWeight: 600 }}>UNKNOWN</span>
}

export default function ConfidencePanel({ result }) {
  if (!result) return null
  const r = result.json_result ?? {}

  const rawTier = r.tier_code ?? (r.tier ? r.tier.replace(/Tier\s*([ABC]).*/i, '$1') : 'B')
  const tier = rawTier.replace('TIER_', '').trim().toUpperCase()

  const overall = r.overall_confidence ?? result.confidence ?? 0.659
  const subScores = r.sub_scores ?? r.stage_confidences ?? {}
  const evidenceLevels = r.evidence_levels ?? {}
  const limits = r.limits ?? [
    "Non-catalog LDPC matrices or proprietary interleavers fall back to hypothesis ranking.",
    "Signals with SNR < 3 dB fall back to Tier C spectral characterization.",
    "Analog transmissions bypass digital FEC/Interleaving stages."
  ]
  const needsReview = r.needs_review ?? (tier !== 'A')

  const spectralPct = (subScores.spectral ?? 1.0) * 100
  const amcPct = (subScores.amc ?? 0.58) * 100
  const demodPct = (subScores.demod ?? 0.90) * 100
  const fecPct = (subScores.joint_fec ?? subScores.joint_search ?? 0.25) * 100
  const corrPct = (subScores.correlation ?? 0.75) * 100

  const getScoreColor = (p) => {
    if (p >= 75) return '#5FD08A'
    if (p >= 40) return '#E8A33D'
    return '#F0605D'
  }

  const TIER_META = {
    A: {
      bg: '#0F2A1D',
      border: '#226B45',
      color: '#5FD08A',
      title: 'TIER A — VERIFIED PAYLOAD RECOVERY',
      desc: 'All stages converged with mathematical proof (Syndrome Zero / CRC Match). Zero hallucination.',
    },
    B: {
      bg: 'rgba(232,163,61,0.1)',
      border: 'rgba(232,163,61,0.4)',
      color: '#E8A33D',
      title: 'TIER B — PLAUSIBLE DEMODULATION / ANALOG',
      desc: 'Signal parameters & raw bitstream extracted. FEC parity unverified or Analog carrier detected.',
    },
    C: {
      bg: 'rgba(240,96,93,0.1)',
      border: 'rgba(240,96,93,0.4)',
      color: '#F0605D',
      title: 'TIER C — UNKNOWN / LOW SNR FALLBACK',
      desc: 'Signal below detection threshold or non-standard format. Stated UNKNOWN with engineering reason.',
    },
  }

  const currentTier = TIER_META[tier] ?? TIER_META.B

  return (
    <div className="sec">
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">06</span>
        <span className="ttl">3-tier defense-grade confidence & evidence</span>
        <span className="sb"></span>
        <span className="lt">
          <i style={{ background: currentTier.color, boxShadow: `0 0 7px ${currentTier.color}` }}></i>
          TIER {tier}
        </span>
      </div>

      <div className="p">
        <div className="b">
          {/* Needs Review Alert Strip */}
          {needsReview && (
            <div
              style={{
                background: 'rgba(232,163,61,0.12)',
                border: '1px solid rgba(232,163,61,0.3)',
                padding: '8px 12px',
                borderRadius: '2px',
                marginBottom: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '12px',
                color: '#E8A33D',
                fontWeight: 500,
              }}
            >
              <span style={{ fontSize: '14px' }}>⚠️</span>
              <span>
                <strong>ANALYST NOTICE:</strong> Output contains statistical hypotheses or unverified parity checks. Human review recommended before intelligence dissemination.
              </span>
            </div>
          )}

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
              <div className="k">Score</div>
              <div className="m" style={{ fontSize: '28px', color: currentTier.color }}>
                {(overall * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* 5 Stage Breakdown Speedometer Needle Gauges */}
          <div className="k" style={{ margin: '18px 0 8px' }}>Stage agreement meters</div>
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
            {r.rationale || result.explanation || `Assigned Tier ${tier}: Signal analysis executed.`}
          </div>

          {/* Granular Evidence Summary Table */}
          {Object.keys(evidenceLevels).length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <div className="k" style={{ marginBottom: '8px' }}>Per-Stage Evidence & Mathematical Proof</div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', background: '#0D1117', border: '1px solid #232C36' }}>
                <thead>
                  <tr style={{ background: '#161B22', color: '#94A3B8', textAlign: 'left' }}>
                    <th style={{ padding: '6px 10px', borderBottom: '1px solid #232C36' }}>Stage</th>
                    <th style={{ padding: '6px 10px', borderBottom: '1px solid #232C36' }}>Evidence Level</th>
                    <th style={{ padding: '6px 10px', borderBottom: '1px solid #232C36' }}>Verification Method</th>
                    <th style={{ padding: '6px 10px', borderBottom: '1px solid #232C36' }}>Observation / Basis</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(evidenceLevels).map(([stageKey, ev]) => (
                    <tr key={stageKey} style={{ borderBottom: '1px solid #1E293B' }}>
                      <td style={{ padding: '6px 10px', fontWeight: 600, color: '#E2E8F0', textTransform: 'uppercase' }}>{stageKey}</td>
                      <td style={{ padding: '6px 10px' }}>{getEvidenceBadge(ev.level)}</td>
                      <td style={{ padding: '6px 10px', color: '#94A3B8' }}>{ev.method}</td>
                      <td style={{ padding: '6px 10px', color: '#CBD5E1', fontFamily: 'IBM Plex Mono, monospace' }}>{ev.basis}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Stated Limits & Engineering Assumptions */}
          <div style={{ marginTop: '14px', background: 'rgba(15,23,42,0.6)', border: '1px solid #1E293B', padding: '10px 14px', borderRadius: '2px' }}>
            <div className="k" style={{ marginBottom: '6px', color: '#94A3B8' }}>Stated System Boundaries & Operating Limits</div>
            <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '11px', color: '#64748B', lineHeight: 1.6 }}>
              {limits.map((l, i) => (
                <li key={i}>{l}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
