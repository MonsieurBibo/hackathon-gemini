import { useState } from 'react'
import type { Individu, Arbre } from '@/types'
import { AdminRequest } from './AdminRequest'
import { DocumentsViewer } from './DocumentsViewer'

interface Props {
  individu: Individu
  arbre: Arbre | null
  onClose: () => void
  onNavigate: (ind: Individu) => void
}

export function IndividuCard({ individu, arbre, onClose, onNavigate }: Props) {
  const [lightboxUrl, setLightboxUrl] = useState<string | null>(null)
  const [showDocuments, setShowDocuments] = useState(false)

  const pere = individu.pere_id ? arbre?.individus[individu.pere_id] : null
  const mere = individu.mere_id ? arbre?.individus[individu.mere_id] : null

  const isPost1900 = individu.statut === 'post_1900' || (!!individu.naissance.date && parseInt(individu.naissance.date.slice(0, 4)) > 1900)

  const enfants = arbre ? Object.values(arbre.individus).filter(i => i.pere_id === individu.id || i.mere_id === individu.id) : []

  const formatDate = (d: string | null, approx: boolean) => {
    if (!d) return '?'
    const year = d.slice(0, 4)
    if (approx) return `ca. ${year}`
    // Format YYYY-MM-DD → DD Mon YYYY
    const [, m, day] = d.split('-')
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    return `${parseInt(day)} ${months[parseInt(m) - 1]} ${year}`
  }

  const hasDocuments = individu.actes.length > 0 || individu.media.length > 0

  if (showDocuments) {
    return <DocumentsViewer individu={individu} onClose={() => setShowDocuments(false)} />
  }

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer">
        <div className="drawer-head">
          <div>
            <div className="drawer-title">{individu.prenom}<br />{individu.nom}</div>
          </div>
          {hasDocuments && (
            <button
              style={{
                background: 'none',
                border: '2px solid var(--lime)',
                color: 'var(--lime)',
                fontFamily: "'Archivo Black', sans-serif",
                fontSize: '9px',
                padding: '4px 10px',
                cursor: 'pointer',
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
              }}
              onClick={() => setShowDocuments(true)}
            >
              VIEW ALL DOCS
            </button>
          )}
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>

        <div className="drawer-body">
          {/* Post-1900 admin request */}
          {isPost1900 && <AdminRequest individu={individu} />}

          {/* Identity */}
          <div className="drawer-section">
            <div className="drawer-section-label">Identity</div>
            <div className="drawer-field">
              <span className="drawer-field-key">Born</span>
              <span className="drawer-field-val">
                {formatDate(individu.naissance.date, individu.naissance.date_approx)}
                {individu.naissance.commune ? ` · ${individu.naissance.commune}` : ''}
              </span>
            </div>
            {individu.deces.date && (
              <div className="drawer-field">
                <span className="drawer-field-key">Died</span>
                <span className="drawer-field-val">
                  {individu.deces.date}
                  {individu.deces.commune ? ` · ${individu.deces.commune}` : ''}
                </span>
              </div>
            )}
            <div className="drawer-field">
              <span className="drawer-field-key">Generation</span>
              <span className="drawer-field-val">{individu.generation}</span>
            </div>
            <div className="drawer-field">
              <span className="drawer-field-key">Status</span>
              <span className="drawer-field-val" style={{
                color: individu.statut === 'complet' ? 'var(--complete)'
                  : individu.statut === 'partiel' ? 'var(--partial)'
                  : individu.statut === 'post_1900' ? '#2060c0'
                  : 'var(--mid)'
              }}>
                {individu.statut.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Parents */}
          {(pere || mere) && (
            <div className="drawer-section">
              <div className="drawer-section-label">Parents</div>
              {pere && (
                <div
                  className="drawer-field"
                  style={{ cursor: 'pointer' }}
                  onClick={() => onNavigate(pere)}
                >
                  <span className="drawer-field-key">Father</span>
                  <span className="drawer-field-val" style={{ textDecoration: 'underline', textDecorationStyle: 'dotted' }}>
                    {pere.prenom} {pere.nom}
                  </span>
                </div>
              )}
              {mere && (
                <div
                  className="drawer-field"
                  style={{ cursor: 'pointer' }}
                  onClick={() => onNavigate(mere)}
                >
                  <span className="drawer-field-key">Mother</span>
                  <span className="drawer-field-val" style={{ textDecoration: 'underline', textDecorationStyle: 'dotted' }}>
                    {mere.prenom} {mere.nom}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Children */}
          {enfants.length > 0 && (
            <div className="drawer-section">
              <div className="drawer-section-label">Children</div>
              {enfants.map(enfant => (
                <div key={enfant.id} className="drawer-field" style={{ cursor: 'pointer' }} onClick={() => onNavigate(enfant)}>
                  <span className="drawer-field-key">{enfant.sexe === 'M' ? 'Son' : enfant.sexe === 'F' ? 'Daughter' : 'Child'}</span>
                  <span className="drawer-field-val" style={{ textDecoration: 'underline', textDecorationStyle: 'dotted' }}>{enfant.prenom} {enfant.nom}</span>
                </div>
              ))}
            </div>
          )}

          {/* Actes */}
          {individu.actes.length > 0 && (
            <div className="drawer-section">
              <div className="drawer-section-label">Records ({individu.actes.length})</div>
              {individu.actes.map((acte, i) => (
                <div key={i} className="drawer-acte">
                  <div className="drawer-acte-head">
                    <span className="drawer-acte-type">{acte.type}</span>
                    <span className="drawer-acte-conf">{Math.round(acte.confiance * 100)}% conf.</span>
                    {acte.url_image && (
                      <button className="drawer-acte-view" onClick={() => setLightboxUrl(acte.url_image)}>VIEW DOC</button>
                    )}
                  </div>
                  {acte.transcription && (
                    <div className="drawer-acte-body">{acte.transcription}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {lightboxUrl && (
        <div className="lightbox" onClick={() => setLightboxUrl(null)}>
          <img src={lightboxUrl} alt="Archive document" onClick={e => e.stopPropagation()} />
          <button className="lightbox-close" onClick={() => setLightboxUrl(null)}>CLOSE ✕</button>
        </div>
      )}
    </>
  )
}
