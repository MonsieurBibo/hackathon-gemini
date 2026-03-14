import { useState } from 'react'
import type { Individu, SearchFormData } from '@/types'
import { startSearch } from '@/api/client'

interface Props {
  individuList: Individu[]
  selectedId: string | null
  onSelect: (ind: Individu) => void
  onSearch: (sessionId: string) => void
  isRunning: boolean
}

const STATUS_LABEL: Record<Individu['statut'], string> = {
  complet: '● Complete',
  partiel: '◐ Partial',
  inconnu: '○ Searching',
}

const STATUS_CLASS: Record<Individu['statut'], string> = {
  complet: 'status-complete',
  partiel: 'status-partial',
  inconnu: 'status-unknown',
}

const FILL_CLASS: Record<Individu['statut'], string> = {
  complet: 'fill-complete',
  partiel: 'fill-partial',
  inconnu: 'fill-searching',
}

const FILL_WIDTH: Record<Individu['statut'], string> = {
  complet: '100%',
  partiel: '55%',
  inconnu: '20%',
}

export function SearchPanel({ individuList, selectedId, onSelect, onSearch, isRunning }: Props) {
  const [form, setForm] = useState<SearchFormData>({
    nom: '',
    prenom: '',
    commune: '',
    annee: new Date().getFullYear() - 180,
    generations: 2,
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (loading || isRunning) return
    setLoading(true)
    try {
      const id = await startSearch(form)
      onSearch(id)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel panel-left">
      <div className="panel-head">
        <span className="panel-head-title">Search</span>
      </div>

      <div className="panel-body">
        <div className="field">
          <label className="field-label">Family name</label>
          <input
            className="field-input"
            value={form.nom}
            onChange={e => setForm(f => ({ ...f, nom: e.target.value }))}
            placeholder="PINÇON"
          />
        </div>

        <div className="field">
          <label className="field-label">Given name</label>
          <input
            className="field-input"
            value={form.prenom}
            onChange={e => setForm(f => ({ ...f, prenom: e.target.value }))}
            placeholder="Prudence Aimée"
          />
        </div>

        <div className="field-row">
          <div className="field">
            <label className="field-label">Commune</label>
            <input
              className="field-input"
              value={form.commune}
              onChange={e => setForm(f => ({ ...f, commune: e.target.value }))}
              placeholder="Neuilly-en-Sancerre"
              style={{ fontSize: '10px' }}
            />
          </div>
          <div className="field">
            <label className="field-label">Year</label>
            <input
              className="field-input"
              type="number"
              value={form.annee}
              onChange={e => setForm(f => ({ ...f, annee: Number(e.target.value) }))}
            />
          </div>
        </div>

        <div className="field">
          <label className="field-label">Generations</label>
          <div className="gen-row">
            {([1, 2, 3] as const).map(g => (
              <button
                key={g}
                className={`gen-btn${form.generations === g ? ' active' : ''}`}
                onClick={() => setForm(f => ({ ...f, generations: g }))}
              >
                {['I', 'II', 'III'][g - 1]}
              </button>
            ))}
          </div>
        </div>

        <button
          className="submit-btn"
          onClick={handleSubmit}
          disabled={loading || isRunning || !form.nom || !form.prenom}
        >
          {loading ? 'Starting…' : isRunning ? 'Running…' : '→ Search'}
        </button>

        {individuList.length > 0 && (
          <>
            <div className="divider-row">
              <span className="divider-label">Found</span>
              <span className="divider-count">{individuList.length}</span>
            </div>

            {individuList.map(ind => (
              <div
                key={ind.id}
                className={`anc-card${selectedId === ind.id ? ' selected' : ''}`}
                onClick={() => onSelect(ind)}
              >
                <div className="anc-card-top">
                  <span className="anc-gen-tag">GEN-0{ind.generation}</span>
                  <span className={`anc-status-tag ${STATUS_CLASS[ind.statut]}`}>
                    {STATUS_LABEL[ind.statut]}
                  </span>
                </div>
                <div className="anc-name">{ind.prenom} {ind.nom}</div>
                <div className="anc-meta">
                  {ind.naissance.date_approx ? 'ca. ' : ''}
                  {ind.naissance.date?.slice(0, 4) ?? '?'}
                  {ind.naissance.commune ? ` · ${ind.naissance.commune}` : ''}
                </div>
                <div className="anc-bar">
                  <div
                    className={`anc-bar-fill ${FILL_CLASS[ind.statut]}`}
                    style={{ width: FILL_WIDTH[ind.statut] }}
                  />
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  )
}
