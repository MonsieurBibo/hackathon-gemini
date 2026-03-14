import { useState } from 'react'
import type { Individu, Acte, Media } from '@/types'

interface Props { individu: Individu; onClose: () => void }

type DocItem = { kind: 'acte'; data: Acte } | { kind: 'media'; data: Media }

export function DocumentsViewer({ individu, onClose }: Props) {
  const items: DocItem[] = [
    ...individu.actes.map(a => ({ kind: 'acte' as const, data: a })),
    ...individu.media.map(m => ({ kind: 'media' as const, data: m })),
  ]
  const [selectedIdx, setSelectedIdx] = useState(0)
  const selected = items[selectedIdx]

  const getUrl = (item: DocItem) => item.kind === 'acte' ? item.data.url_image : item.data.url
  const getLabel = (item: DocItem) => item.kind === 'acte' ? item.data.type : item.data.type
  const getMeta = (item: DocItem) => item.kind === 'acte' ? `${item.data.source} · ${Math.round(item.data.confiance * 100)}% conf.` : item.data.source

  return (
    <div className="docviewer">
      <div className="docviewer-head">
        <div className="docviewer-title">{individu.prenom} {individu.nom} — Documents ({items.length})</div>
        <button style={{ background: 'none', border: '2px solid var(--lime)', color: 'var(--lime)', fontFamily: "'Archivo Black', sans-serif", fontSize: '11px', padding: '4px 16px', cursor: 'pointer', letterSpacing: '0.1em' }} onClick={onClose}>CLOSE ✕</button>
      </div>
      <div className="docviewer-body">
        <div className="docviewer-list">
          {items.map((item, i) => (
            <div key={i} className={`docviewer-item${i === selectedIdx ? ' active' : ''}`} onClick={() => setSelectedIdx(i)}>
              <div className="docviewer-item-type">{getLabel(item)}</div>
              <div className="docviewer-item-meta">{getMeta(item)}</div>
            </div>
          ))}
        </div>
        <div className="docviewer-preview">
          {selected && getUrl(selected) ? (
            <img src={getUrl(selected)!} alt="Document" />
          ) : selected?.kind === 'acte' && selected.data.transcription ? (
            <div className="docviewer-transcription">{selected.data.transcription}</div>
          ) : (
            <div style={{ fontFamily: 'JetBrains Mono, monospace', color: 'var(--mid)', fontSize: '11px' }}>No preview available</div>
          )}
        </div>
      </div>
    </div>
  )
}
