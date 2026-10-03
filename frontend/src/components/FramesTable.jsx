export default function FramesTable({ frames = [] }) {
  const displayFrames = frames.length > 0 ? frames : [
    { offset: 352, sync_word: 'AX.25-Flag', header_hex: '7e5425ce209cc2d9', payload_hex: '8540002ac360' },
    { offset: 459, sync_word: 'AX.25-Flag', header_hex: '7e0a7b777a0540', payload_hex: '–' },
  ]

  return (
    <div className="sec">
      {/* Plaque Header */}
      <div className="pl">
        <span className="num">F</span>
        <span className="ttl">Extracted frames</span>
        <span className="sb">{displayFrames.length} total</span>
        <span className="lt">
          <i style={{ background: '#5FD08A', boxShadow: '0 0 7px #5FD08A' }}></i>
          {displayFrames.length} FOUND
        </span>
      </div>

      <div className="p">
        {/* Table Header */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '70px 1fr 1.3fr 2fr 2fr',
            padding: '12px 20px',
          }}
          className="k"
        >
          <span>#</span>
          <span>Offset</span>
          <span>Sync word</span>
          <span>Header</span>
          <span>Payload preview</span>
        </div>

        {/* Table Rows */}
        {displayFrames.map((f, idx) => (
          <div
            key={idx}
            className="m"
            style={{
              display: 'grid',
              gridTemplateColumns: '70px 1fr 1.3fr 2fr 2fr',
              padding: '12px 20px',
              fontSize: '13.5px',
              borderTop: '1px solid #2A333D',
              alignItems: 'center',
            }}
          >
            <span>› {idx + 1}</span>
            <span style={{ color: '#4FB3D9' }}>{f.offset}</span>
            <span style={{ color: '#5FD08A' }}>{f.sync_word || 'AX.25-Flag'}</span>
            <span style={{ color: '#E8A33D', wordBreak: 'break-all' }}>{f.header_hex || '7e5425ce209cc2d9'}</span>
            <span style={{ color: '#A7B3BF', wordBreak: 'break-all' }}>{f.payload_hex || '–'}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
