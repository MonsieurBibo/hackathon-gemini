import type { Individu, Arbre } from '@/types'

interface Props {
  individu: Individu
  arbre: Arbre | null
  onClose: () => void
  onNavigate: (ind: Individu) => void
}

export function IndividuCard({ individu, arbre, onClose, onNavigate }: Props) {
  const pere = individu.pere_id ? arbre?.individus[individu.pere_id] : null
  const mere = individu.mere_id ? arbre?.individus[individu.mere_id] : null

  const formatDate = (d: string | null, approx: boolean) => {
    if (!d) return '?'
    return `${approx ? 'ca. ' : ''}${d}`
  }

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer">
        <div className="drawer-head">
          <div>
            <div className="drawer-title">{individu.prenom}<br />{individu.nom}</div>
          </div>
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>

        <div className="drawer-body">
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

          {/* Actes */}
          {individu.actes.length > 0 && (
            <div className="drawer-section">
              <div className="drawer-section-label">Records ({individu.actes.length})</div>
              {individu.actes.map((acte, i) => (
                <div key={i} className="drawer-acte">
                  <div className="drawer-acte-head">
                    <span className="drawer-acte-type">{acte.type}</span>
                    <span className="drawer-acte-conf">{Math.round(acte.confiance * 100)}% conf.</span>
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
    </>
  )
}
