import React from 'react'

export default function FramesTable({ frames = [] }) {
  const hasRealFrames = frames && frames.length > 0
  const displayFrames = hasRealFrames ? frames : []

  return (
    <div className="sec">
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">F</span>
        <span className="ttl">Extracted frames & packet telemetry</span>
        <span className="sb">{displayFrames.length} synchronized</span>
        <span className="lt">
          <i style={{ background: displayFrames.length > 0 ? '#5FD08A' : '#64748B', boxShadow: displayFrames.length > 0 ? '0 0 7px #5FD08A' : 'none' }}></i>
          {displayFrames.length > 0 ? `${displayFrames.length} DETECTED` : '0 FRAMES'}
        </span>
      </div>

      <div className="p">
        {displayFrames.length === 0 ? (
          <div style={{ padding: '24px', textAlign: 'center', color: '#64748B', fontSize: '13px', fontFamily: 'IBM Plex Mono' }}>
            No synchronized packet frames detected. Raw demodulated bitstream preserved under Stage 03.
          </div>
        ) : (
          <>
            {/* Table Header */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '45px 95px 105px 130px 1.2fr 2fr',
                padding: '12px 16px',
                borderBottom: '1px solid #232C36'
              }}
              className="k"
            >
              <span>#</span>
              <span>Status</span>
              <span>Offset</span>
              <span>Sync Word</span>
              <span>Preamble / Header</span>
              <span>Decoded Payload (ASCII / Hex)</span>
            </div>

            {/* Table Rows */}
            {displayFrames.map((f, idx) => {
              const isVerified = f.support_status === 'VERIFIED'
              const payloadText = f.payload_ascii && f.payload_ascii.replace(/\./g, '').length > 0 ? f.payload_ascii : null
              return (
                <div
                  key={idx}
                  className="m"
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '45px 95px 105px 130px 1.2fr 2fr',
                    padding: '10px 16px',
                    fontSize: '12.5px',
                    borderTop: '1px solid #1E293B',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ color: '#64748B' }}>› {idx + 1}</span>
                  <span>
                    <span
                      style={{
                        background: isVerified ? 'rgba(95,208,138,0.12)' : 'rgba(232,163,61,0.12)',
                        color: isVerified ? '#5FD08A' : '#E8A33D',
                        border: `1px solid ${isVerified ? '#226B45' : 'rgba(232,163,61,0.4)'}`,
                        padding: '2px 6px',
                        borderRadius: '2px',
                        fontSize: '10px',
                        fontWeight: 600,
                      }}
                    >
                      {f.support_status || (isVerified ? 'VERIFIED' : 'CANDIDATE')}
                    </span>
                  </span>
                  <span style={{ color: '#38BDF8' }}>{f.offset} bits</span>
                  <span style={{ color: '#E2E8F0', fontWeight: 500 }}>{f.sync_word || 'None'}</span>
                  <span style={{ color: '#E8A33D', wordBreak: 'break-all', fontFamily: 'IBM Plex Mono' }}>{f.header_hex || '–'}</span>
                  <div style={{ wordBreak: 'break-all', fontFamily: 'IBM Plex Mono' }}>
                    {payloadText && (
                      <span style={{ color: '#5FD08A', fontWeight: 500, marginRight: '8px' }}>
                        "{payloadText}"
                      </span>
                    )}
                    <span style={{ color: payloadText ? '#64748B' : '#CBD5E1', fontSize: '11.5px' }}>
                      {f.payload_hex || '–'}
                    </span>
                  </div>
                </div>
              )
            })}
          </>
        )}
      </div>
    </div>
  )
}
