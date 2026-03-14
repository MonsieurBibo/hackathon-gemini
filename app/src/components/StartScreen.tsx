import { useState } from 'react'
import type { SearchFormData } from '@/types'
import { startSearch } from '@/api/client'

interface StartScreenProps {
  onSearch: (sessionId: string) => void
}

export function StartScreen({ onSearch }: StartScreenProps) {
  const [form, setForm] = useState<SearchFormData>({
    nom: '',
    prenom: '',
    commune: '',
    annee: 1843,
    generations: 2,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async () => {
    if (loading || !form.nom || !form.prenom) return
    setLoading(true)
    setError(null)
    try {
      const id = await startSearch(form)
      onSearch(id)
    } catch (e) {
      console.error(e)
      setError('Failed to start search. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="start-screen">
      <div className="start-box">
        <div className="start-title">GENEALOGY AI</div>
        <div className="start-subtitle">
          Navigate French archives autonomously. OCR handwritten acts. Build your tree.
        </div>

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
              placeholder="1843"
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
          disabled={loading || !form.nom || !form.prenom}
        >
          {loading ? 'Starting…' : '→ Start Search'}
        </button>

        {error && (
          <div className="start-error">{error}</div>
        )}
      </div>
    </div>
  )
}
