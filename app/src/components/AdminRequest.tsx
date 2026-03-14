import { useState } from 'react'
import type { Individu } from '@/types'

interface Props { individu: Individu }

export function AdminRequest({ individu }: Props) {
  const [copied, setCopied] = useState(false)

  const formatDate = (d: string | null) => {
    if (!d) return 'date inconnue'
    const [y, m, day] = d.split('-')
    return `${day || '??'} ${['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'][parseInt(m||'1')-1]} ${y}`
  }

  const letter = `Madame, Monsieur,

Je me permets de vous contacter dans le cadre de recherches généalogiques.

Je souhaiterais obtenir une copie intégrale de l'acte de naissance de :

Nom : ${individu.nom} ${individu.prenom}
Date de naissance : ${formatDate(individu.naissance.date)}
Lieu de naissance : ${individu.naissance.commune || 'commune inconnue'} (${individu.naissance.dept || '??'})

Cette demande est effectuée à des fins de recherche généalogique personnelle,
conformément à l'article 7 de la loi n° 2008-696 du 15 juillet 2008.

Dans l'attente de votre réponse, je vous adresse mes sincères salutations.`

  const handleCopy = () => {
    navigator.clipboard.writeText(letter).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="drawer-section">
      <div className="admin-banner">RECORDS RESTRICTED — Born after 1900. Public access not available.</div>
      <div className="drawer-section-label">Contact</div>
      <div className="drawer-field">
        <span className="drawer-field-key">Mairie</span>
        <span className="drawer-field-val">{individu.naissance.commune || '—'}</span>
      </div>
      <div className="drawer-field">
        <span className="drawer-field-key">Dept</span>
        <span className="drawer-field-val">{individu.naissance.dept || '—'}</span>
      </div>
      <div className="drawer-field">
        <span className="drawer-field-key">Delay</span>
        <span className="drawer-field-val">2–8 weeks</span>
      </div>
      <div className="drawer-section-label" style={{ marginTop: '12px' }}>Draft Letter</div>
      <textarea className="admin-letter" rows={10} readOnly value={letter} />
      <div style={{ display: 'flex', marginTop: '8px' }}>
        <button className="admin-btn" onClick={handleCopy}>{copied ? 'COPIED ✓' : 'COPY LETTER'}</button>
        <button className="admin-btn admin-btn-outline" onClick={() => window.open('https://www.service-public.gouv.fr/particuliers/vosdroits/F1427', '_blank', 'noopener,noreferrer')}>OPEN MAIRIE.FR</button>
      </div>
    </div>
  )
}
