# Tâches Frontend

> Référence : contrats dans `contracts.md`

---

## F0 — Setup projet
**Dépendances** : aucune | **Bloque** : tout

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install
npm install d3 @types/d3 axios
```

Structure :
```
frontend/src/
  components/
    TreeView.tsx
    AgentsPanel.tsx
    IndividuCard.tsx
    Chatbox.tsx
    SearchForm.tsx
  hooks/
    useSSE.ts
    useArbre.ts
  types/
    index.ts
  api/
    client.ts
  App.tsx
```

`VITE_API_URL=http://localhost:8000`

---

## F1 — Types TypeScript
**Dépendances** : F0 | **Bloque** : F2, F3, F4, F5, F6

`src/types/index.ts` — miroir exact du contrat JSON :

```typescript
interface Individu {
  id: string
  nom: string
  prenom: string
  sexe: "M" | "F" | null
  naissance: { date: string | null; date_approx: boolean; commune: string; dept: string }
  deces: { date: string | null; commune: string | null; dept: string | null }
  pere_id: string | null
  mere_id: string | null
  generation: number
  actes: Acte[]
  media: Media[]
  embedding_id: string | null
  statut: "complet" | "partiel" | "inconnu"
}

interface Acte {
  type: "naissance" | "mariage" | "deces" | "matricule" | "recensement"
  url_image: string
  transcription: string
  source: string
  fiche_id: number
  confiance: number
}

interface Media {
  type: "photo_tombe" | "portrait" | "medaille" | "note"
  url: string | null
  contenu: string | null
  source: "user" | "wikimedia" | "geneanet"
}

interface Arbre {
  session_id: string
  root_id: string
  individus: Record<string, Individu>
  generation_max: number
  generation_courante: number
  statut: "en_cours" | "termine" | "erreur"
}

interface AgentState {
  agent_id: string
  individu_id: string
  individu_nom: string
  status: "searching" | "ocr" | "extracting" | "done" | "error"
  last_message: string
  tentative?: number
}

type SSEEvent =
  | { type: "thinking"; agent_id: string; individu_id: string; message: string }
  | { type: "step"; agent_id: string; individu_id: string; message: string }
  | { type: "ocr_chunk"; agent_id: string; individu_id: string; chunk: string }
  | { type: "individual"; individu: Individu }
  | { type: "individual_update"; individu_id: string; patch: Partial<Individu> }
  | { type: "fallback"; agent_id: string; individu_id: string; tentative: number; raison: string; action: string }
  | { type: "question"; agent_id: string; individu_id: string; question: string; options: string[] }
  | { type: "error"; agent_id: string; individu_id: string; message: string }
  | { type: "done"; arbre: Arbre }
```

---

## F2 — Hook SSE
**Dépendances** : F0, F1 | **Bloque** : F3, F4

```typescript
// src/hooks/useSSE.ts
function useSSE(sessionId: string | null): {
  arbre: Arbre | null
  agents: AgentState[]
  ocrStream: string
  question: SSEEvent & { type: "question" } | null
  isRunning: boolean
}
```

- `EventSource` sur `GET /stream/{session_id}`
- `individual` → merge dans `arbre.individus`
- `individual_update` → patch individu existant
- `ocr_chunk` → concat dans `ocrStream`
- `done` → `isRunning = false`

---

## F3 — Arbre D3
**Dépendances** : F0, F1, F2 | **Bloque** : rien

```typescript
// Props: arbre: Arbre | null, onNodeClick: (individu: Individu) => void
```

- Layout horizontal : racine à droite, ancêtres à gauche
- Nœud : prénom + nom + année naissance
- Couleurs : vert=complet, orange=partiel, gris=inconnu
- Animation fade+scale à chaque `event: individual`
- Clic → ouvre `IndividuCard`
- Pan/zoom avec `d3-zoom`

---

## F4 — Panneau Agents
**Dépendances** : F0, F1, F2 | **Bloque** : rien

```typescript
// Props: agents: AgentState[], ocrStream: string
```

- Carte par agent : nom individu + génération + last_message + barre progression
- Badge statut : `searching | ocr | extracting | done | error`
- Fallback en orange avec numéro de tentative
- Section tokens OCR en bas : monospace, auto-scroll

---

## F5 — Fiche Individu
**Dépendances** : F0, F1 | **Bloque** : rien

```typescript
// Props: individu: Individu | null, onClose: () => void
```

- Identité complète (nom, prénom, dates, lieux)
- Liens père / mère cliquables
- Liste actes : miniature + transcription expandable
- Galerie media (photo tombe, portrait, médaille)
- Section notes
- Upload image ou note → `POST /upload/{session_id}/{individu_id}`

---

## F6 — Formulaire + Chatbox
**Dépendances** : F0, F1 | **Bloque** : rien

```typescript
// SearchForm.tsx
// Champs : nom, prénom, commune, année, générations (1-3)
// Submit → POST /search → session_id → active le SSE

// Chatbox.tsx
// Props: question: QuestionEvent | null, sessionId: string
// - Si question active : affiche options + boutons choix
// - Sinon : input texte libre
// - Submit → POST /answer/{session_id}
// - Toggle show/hide
```
