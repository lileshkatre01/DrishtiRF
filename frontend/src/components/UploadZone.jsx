import { useRef, useState } from 'react'

export default function UploadZone({ onFile, disabled }) {
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    if (disabled) return
    const file = e.dataTransfer.files[0]
    if (file) onFile(file)
  }

  const handleChange = (e) => {
    const file = e.target.files[0]
    if (file) onFile(file)
  }

  return (
    <div className="p" style={{ flex: 1 }}>
      <input
        ref={inputRef}
        type="file"
        accept=".iq,.wav,.sigmf-meta,.sigmf,.bin,.dat"
        className="hidden"
        onChange={handleChange}
        disabled={disabled}
      />
      <div
        className="b"
        onClick={() => !disabled && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '12px',
          padding: '36px 16px 20px',
          border: `2px dashed ${dragOver ? '#E8A33D' : '#3A4652'}`,
          margin: '16px',
          borderRadius: '3px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          background: dragOver ? 'rgba(232,163,61,0.05)' : 'transparent',
          transition: 'all 0.15s ease',
        }}
      >
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#4FB3D9" strokeWidth="1.6">
          <path d="M12 16V4M7 9l5-5 5 5M4 16v4h16v-4" />
        </svg>

        <div style={{ fontWeight: 600, letterSpacing: '.1em', fontSize: '14.5px', color: '#fff' }}>
          DROP SIGNAL FILE
        </div>
        <div className="m k" style={{ textTransform: 'none', color: '#A7B3BF' }}>
          or click to browse
        </div>

        <div className="r" style={{ marginTop: '6px' }}>
          <span className="m" style={{ border: '1px solid #3A4652', padding: '4px 8px', fontSize: '13px', color: '#C9D3DC' }}>.IQ</span>
          <span className="m" style={{ border: '1px solid #3A4652', padding: '4px 8px', fontSize: '13px', color: '#C9D3DC' }}>.WAV</span>
          <span className="m" style={{ border: '1px solid #3A4652', padding: '4px 8px', fontSize: '13px', color: '#C9D3DC' }}>.SIGMF-META</span>
          <span className="m" style={{ border: '1px solid #3A4652', padding: '4px 8px', fontSize: '13px', color: '#C9D3DC' }}>.SIGMF</span>
        </div>

        <div className="m k" style={{ textTransform: 'none', marginTop: '10px', color: '#6B7682' }}>
          Raw IQ · WAV stereo · SigMF
        </div>
      </div>
    </div>
  )
}
