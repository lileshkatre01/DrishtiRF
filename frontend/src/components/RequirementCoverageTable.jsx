export default function RequirementCoverageTable({ results, capture }) {
  const hasResults = Object.keys(results || {}).length > 0
  const spectral = results?.SPECTRAL?.json_result ?? {}
  const amc = results?.AMC?.json_result ?? {}
  const demod = results?.DEMOD?.json_result ?? {}
  const joint = results?.JOINT_SEARCH?.json_result ?? {}
  const corr = results?.CORRELATION?.json_result ?? {}

  const fsMHz = spectral.sample_rate || capture?.sample_rate ? ((spectral.sample_rate || capture.sample_rate) / 1e6).toFixed(3) : '—'
  const mod = amc.modulation ?? (hasResults ? 'UNKNOWN' : '—')
  const bitCount = demod.bit_count ? demod.bit_count.toLocaleString() : (hasResults ? '0' : '—')
  const interleaver = joint.best_interleaver ?? (hasResults ? 'None' : '—')
  const fec = hasResults
    ? ((joint.best_fec ? `${joint.best_fec} · ` : 'None · ') + (joint.syndrome_zero ? 'converged' : 'partial'))
    : '—'
  const syncFrames = hasResults
    ? `${corr.best_sync_word || 'None'} · ${corr.frame_count ?? (corr.frames ? corr.frames.length : 0)} frames`
    : '—'

  return (
    <div className="sec" style={{ marginTop: '16px' }}>
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">SPEC</span>
        <span className="ttl">Pipeline capability & recovery matrix</span>
        <span className="sb">6-stage autonomous demodulation engine · live run</span>
        <span className="lt">
          <i style={{ background: hasResults ? '#5FD08A' : '#7D8A99', boxShadow: hasResults ? '0 0 7px #5FD08A' : 'none' }}></i>
          {hasResults ? '6 / 6 MAPPED' : '0 / 6 STANDBY'}
        </span>
      </div>

      {/* Table Header */}
      <div
        className="k m"
        style={{
          display: 'grid',
          gridTemplateColumns: '60px 1.1fr 2.3fr 1.6fr',
          gap: '12px',
          padding: '10px 4px',
          alignItems: 'center',
          borderBottom: '1px solid #2A333D',
        }}
      >
        <span>SPEC</span>
        <span>Stage Objective</span>
        <span>Engine Scope</span>
        <span>Recovered (This Run)</span>
      </div>

      {/* Row 1: Parameter Extraction */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '60px 1.1fr 2.3fr 1.6fr',
          gap: '12px',
          padding: '10px 4px',
          alignItems: 'center',
          borderBottom: '1px solid #1F2832',
          fontSize: '14px',
        }}
      >
        <span className="m" style={{ color: '#E8A33D', fontWeight: 600 }}>i</span>
        <span style={{ fontWeight: 600 }}>Identify signal parameters</span>
        <span style={{ color: '#B4C0CB' }}>Sampling freq · modulation · FEC · interleaving (+ SNR, BW, offset, symbol rate)</span>
        <span className="m" style={{ fontSize: '13px', color: hasResults ? '#5FD08A' : '#7D8A99' }}>
          {hasResults ? `Fs ${fsMHz} MHz · ${mod} · ${joint.best_fec || 'None'} · ${interleaver.split(' ')[0]}` : '—'}
        </span>
      </div>

      {/* Row 2: Demodulation */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '60px 1.1fr 2.3fr 1.6fr',
          gap: '12px',
          padding: '10px 4px',
          alignItems: 'center',
          borderBottom: '1px solid #1F2832',
          fontSize: '14px',
        }}
      >
        <span className="m" style={{ color: '#E8A33D', fontWeight: 600 }}>ii</span>
        <span style={{ fontWeight: 600 }}>Demodulate signals</span>
        <span style={{ color: '#B4C0CB' }}>FSK · PSK · QAM</span>
        <span className="m" style={{ fontSize: '13px', color: hasResults ? '#5FD08A' : '#7D8A99' }}>
          {hasResults ? `${mod} → ${bitCount} bits` : '—'}
        </span>
      </div>

      {/* Row 3: De-interleaving */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '60px 1.1fr 2.3fr 1.6fr',
          gap: '12px',
          padding: '10px 4px',
          alignItems: 'center',
          borderBottom: '1px solid #1F2832',
          fontSize: '14px',
        }}
      >
        <span className="m" style={{ color: '#E8A33D', fontWeight: 600 }}>iii</span>
        <span style={{ fontWeight: 600 }}>De-interleaving</span>
        <span style={{ color: '#B4C0CB' }}>Block · Convolutional · Diagonal · Pseudo-random</span>
        <span className="m" style={{ fontSize: '13px', color: hasResults ? '#5FD08A' : '#7D8A99' }}>
          {hasResults ? interleaver : '—'}
        </span>
      </div>

      {/* Row 4: FEC decoding */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '60px 1.1fr 2.3fr 1.6fr',
          gap: '12px',
          padding: '10px 4px',
          alignItems: 'center',
          borderBottom: '1px solid #1F2832',
          fontSize: '14px',
        }}
      >
        <span className="m" style={{ color: '#E8A33D', fontWeight: 600 }}>iv</span>
        <span style={{ fontWeight: 600 }}>FEC decoding</span>
        <span style={{ color: '#B4C0CB' }}>Viterbi · Reed-Solomon · Concatenated · LDPC</span>
        <span className="m" style={{ fontSize: '13px', color: hasResults ? '#5FD08A' : '#7D8A99' }}>
          {hasResults ? fec : '—'}
        </span>
      </div>

      {/* Row 5: Bitstream correlation */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '60px 1.1fr 2.3fr 1.6fr',
          gap: '12px',
          padding: '10px 4px',
          alignItems: 'center',
          borderBottom: '1px solid #1F2832',
          fontSize: '14px',
        }}
      >
        <span className="m" style={{ color: '#E8A33D', fontWeight: 600 }}>v</span>
        <span style={{ fontWeight: 600 }}>Bit-stream correlation</span>
        <span style={{ color: '#B4C0CB' }}>Header and payload identification</span>
        <span className="m" style={{ fontSize: '13px', color: hasResults ? '#5FD08A' : '#7D8A99' }}>
          {hasResults ? syncFrames : '—'}
        </span>
      </div>

      {/* Row 6: GUI */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '60px 1.1fr 2.3fr 1.6fr',
          gap: '12px',
          padding: '10px 4px',
          alignItems: 'center',
          fontSize: '14px',
        }}
      >
        <span className="m" style={{ color: '#E8A33D', fontWeight: 600 }}>GUI</span>
        <span style={{ fontWeight: 600 }}>Feature visibility</span>
        <span style={{ color: '#B4C0CB' }}>Spectrum · waterfall · constellation · eye diagram</span>
        <span className="m" style={{ fontSize: '13px', color: hasResults ? '#5FD08A' : '#7D8A99' }}>
          {hasResults ? 'all rendered' : '—'}
        </span>
      </div>
    </div>
  )
}
