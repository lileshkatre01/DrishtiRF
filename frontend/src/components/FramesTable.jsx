import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'

function truncateHex(hex, maxLen = 32) {
  if (!hex) return '—'
  return hex.length > maxLen ? hex.slice(0, maxLen) + '…' : hex
}

export default function FramesTable({ frames }) {
  const [expanded, setExpanded] = useState(null)

  if (!frames || frames.length === 0) return null

  return (
    <section className="space-y-4">
      <h2 className="text-xs font-bold tracking-widest px-1" style={{ color: 'var(--accent-blue)' }}>
        ▸ EXTRACTED FRAMES · {frames.length} TOTAL
      </h2>

      <div className="rounded-xl overflow-hidden" style={{ border: '1px solid var(--border)' }}>
        {/* Header */}
        <div className="grid grid-cols-12 px-4 py-2 text-xs font-bold tracking-widest"
          style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
          <div className="col-span-1">#</div>
          <div className="col-span-2">OFFSET</div>
          <div className="col-span-3">SYNC WORD</div>
          <div className="col-span-3">HEADER</div>
          <div className="col-span-3">PAYLOAD PREVIEW</div>
        </div>

        {/* Rows */}
        <div className="divide-y" style={{ borderColor: 'var(--border)', background: 'var(--bg-card)' }}>
          {frames.map((frame, i) => (
            <div key={frame.id ?? i}>
              <div
                className="grid grid-cols-12 px-4 py-2.5 text-xs cursor-pointer transition-colors"
                style={{ color: 'var(--text-primary)' }}
                onMouseOver={e => e.currentTarget.style.background = 'rgba(0,180,255,0.04)'}
                onMouseOut={e => e.currentTarget.style.background = 'transparent'}
                onClick={() => setExpanded(expanded === i ? null : i)}
              >
                <div className="col-span-1 flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
                  {expanded === i ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                  {i + 1}
                </div>
                <div className="col-span-2 font-mono" style={{ color: 'var(--accent-blue)' }}>
                  {frame.offset}
                </div>
                <div className="col-span-3 font-bold tracking-wide" style={{ color: 'var(--accent-green)' }}>
                  {frame.sync_word ?? '—'}
                </div>
                <div className="col-span-3 font-mono text-xs" style={{ color: 'var(--accent-amber)' }}>
                  {truncateHex(frame.header_hex)}
                </div>
                <div className="col-span-3 font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
                  {truncateHex(frame.payload_hex)}
                </div>
              </div>

              {/* Expanded row */}
              {expanded === i && (
                <div className="px-5 py-4 text-xs space-y-2" style={{ background: 'rgba(0,0,0,0.3)', borderTop: '1px solid var(--border)' }}>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>HEADER HEX: </span>
                    <span className="font-mono break-all" style={{ color: 'var(--accent-amber)' }}>{frame.header_hex ?? '—'}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>PAYLOAD HEX: </span>
                    <span className="font-mono break-all" style={{ color: 'var(--text-primary)' }}>{frame.payload_hex ?? '—'}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
