export interface Acte {
  type: 'naissance' | 'mariage' | 'deces' | 'matricule' | 'recensement'
  url_image: string
  transcription: string
  source: string
  fiche_id: number
  confiance: number
}

export interface Media {
  type: 'photo_tombe' | 'portrait' | 'medaille' | 'note'
  url: string | null
  contenu: string | null
  source: 'user' | 'wikimedia' | 'geneanet'
}

export interface Individu {
  id: string
  nom: string
  prenom: string
  sexe: 'M' | 'F' | null
  naissance: {
    date: string | null
    date_approx: boolean
    commune: string
    dept: string
  }
  deces: {
    date: string | null
    commune: string | null
    dept: string | null
  }
  pere_id: string | null
  mere_id: string | null
  generation: number
  actes: Acte[]
  media: Media[]
  embedding_id: string | null
  statut: 'complet' | 'partiel' | 'inconnu' | 'post_1900'
}

export interface Arbre {
  session_id: string
  root_id: string
  individus: Record<string, Individu>
  generation_max: number
  generation_courante: number
  statut: 'en_cours' | 'termine' | 'erreur'
}

export interface AgentState {
  agent_id: string
  individu_id: string
  individu_nom: string
  status: 'searching' | 'ocr' | 'extracting' | 'done' | 'error' | 'thinking'
  last_message: string
  tentative?: number
  progress?: number
}

export type SSEEvent =
  | { type: 'thinking'; agent_id: string; individu_id: string; message: string }
  | { type: 'step'; agent_id: string; individu_id: string; message: string }
  | { type: 'ocr_chunk'; agent_id: string; individu_id: string; chunk: string }
  | { type: 'individual'; individu: Individu }
  | { type: 'individual_update'; individu_id: string; patch: Partial<Individu> }
  | { type: 'fallback'; agent_id: string; individu_id: string; tentative: number; raison: string; action: string }
  | { type: 'question'; agent_id: string; individu_id: string; question: string; options: string[] }
  | { type: 'error'; agent_id: string; individu_id: string; message: string }
  | { type: 'done'; arbre: Arbre }

export interface SearchFormData {
  nom: string
  prenom: string
  commune: string
  annee: number
  generations: 1 | 2 | 3
}
