import { useCallback, useState } from 'react'
import { Upload, FileAudio, AlertCircle } from 'lucide-react'

const ACCEPTED = ['.iq', '.wav', '.sigmf-meta', '.sigmf']

export default function UploadZone({ onFile, disabled }) {
  const [dragOver, setDragOver] = useState(false)
  const [fileError, setFileError] = useState(null)

  const validate = (file) => {
    const name = file.name.toLowerCase()
    const ok = ACCEPTED.some(ext => name.endsWith(ext))
    if (!ok) {
      setFileError(`Unsupported format. Accepted: ${ACCEPTED.join(', ')}`)
      return false
    }
    setFileError(null)
    return true
  }

  const handle = useCallback((file) => {
    if (!file || disabled) return
    if (validate(file)) onFile(file)
  }, [onFile, disabled])

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    handle(file)
  }

  const onChange = (e) => {
    const file = e.target.files[0]
    handle(file)
  }

  return (
    <div
      className={`relative rounded-xl p-8 flex flex-col items-center justify-center gap-4 transition-all cursor-pointer ${dragOver ? 'drop-zone-active' : ''}`}
      style={{
        border: `2px dashed ${dragOver ? 'var(--accent-green)' : 'var(--border)'}`,
        background: 'var(--bg-card)',
        minHeight: '220px',
        opacity: disabled ? 0.5 : 1,
        pointerEvents: disabled ? 'none' : 'auto',
      }}
      onDragOver={e => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={onDrop}
      onClick={() => document.getElementById('file-input').click()}
    >
      <input
        id="file-input"
        type="file"
        accept=".iq,.wav,.sigmf-meta,.sigmf"
        className="hidden"
        onChange={onChange}
      />

      <div className="p-4 rounded-full" style={{ background: 'rgba(0,180,255,0.1)', border: '1px solid rgba(0,180,255,0.3)' }}>
        <Upload size={28} style={{ color: 'var(--accent-blue)' }} />
      </div>

      <div className="text-center">
        <p className="font-bold tracking-wider" style={{ color: 'var(--text-primary)' }}>
          DROP SIGNAL FILE
        </p>
        <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
          or click to browse
        </p>
      </div>

      {/* Accepted formats */}
      <div className="flex flex-wrap justify-center gap-2 mt-1">
        {ACCEPTED.map(ext => (
          <span key={ext} className="px-2 py-0.5 rounded text-xs font-bold tracking-wider"
            style={{ background: 'rgba(0,180,255,0.08)', border: '1px solid rgba(0,180,255,0.2)', color: 'var(--accent-blue)' }}>
            <FileAudio size={10} className="inline mr-1" />
            {ext.toUpperCase()}
          </span>
        ))}
      </div>

      {fileError && (
        <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--accent-red)' }}>
          <AlertCircle size={14} />
          {fileError}
        </div>
      )}

      <p className="text-xs absolute bottom-3 right-4" style={{ color: 'var(--text-muted)' }}>
        Raw IQ · WAV Stereo · SigMF
      </p>
    </div>
  )
}
