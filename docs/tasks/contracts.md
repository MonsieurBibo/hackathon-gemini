# Contrats de données — GenealogyAI

> À lire en premier. Référence partagée entre backend et frontend.

---

## Individu

```json
{
  "id": "uuid-v4",
  "nom": "Pinçon",
  "prenom": "Jean",
  "sexe": "M",
  "naissance": {
    "date": "1810-03-03",
    "date_approx": true,
    "commune": "Neuilly-en-Sancerre",
    "dept": "18"
  },
  "deces": {
    "date": null,
    "commune": null,
    "dept": null
  },
  "pere_id": "uuid | null",
  "mere_id": "uuid | null",
  "generation": 1,
  "actes": [
    {
      "type": "naissance | mariage | deces | matricule | recensement",
      "url_image": "https://...",
      "transcription": "texte brut extrait par Gemini",
      "source": "archives18.fr",
      "fiche_id": 4082,
      "confiance": 0.92
    }
  ],
  "media": [
    {
      "type": "photo_tombe | portrait | medaille | note",
      "url": "https://... | null",
      "contenu": "texte si type=note | null",
      "source": "user | wikimedia | geneanet"
    }
  ],
  "embedding_id": "uuid chromadb | null",
  "statut": "complet | partiel | inconnu"
}
```

---

## Arbre

```json
{
  "session_id": "uuid-v4",
  "root_id": "uuid",
  "individus": {
    "uuid": { "...individu..." }
  },
  "generation_max": 3,
  "generation_courante": 1,
  "statut": "en_cours | termine | erreur"
}
```

---

## Events SSE

```
event: thinking
data: { "agent_id": "uuid", "individu_id": "uuid", "message": "Recherche table décennale..." }

event: step
data: { "agent_id": "uuid", "individu_id": "uuid", "message": "Registre trouvé : Cher, p.3" }

event: ocr_chunk
data: { "agent_id": "uuid", "individu_id": "uuid", "chunk": "...tokens Gemini en streaming..." }

event: individual
data: { "individu": { ...individu complet... } }

event: individual_update
data: { "individu_id": "uuid", "patch": { "actes": [...] } }

event: fallback
data: { "agent_id": "uuid", "individu_id": "uuid", "tentative": 2, "raison": "acte introuvable", "action": "élargissement ±5 ans" }

event: question
data: { "agent_id": "uuid", "individu_id": "uuid", "question": "2 records trouvés, lequel ?", "options": ["...", "..."] }

event: error
data: { "agent_id": "uuid", "individu_id": "uuid", "message": "Aucun acte trouvé après 4 tentatives" }

event: done
data: { "arbre": { ...arbre complet... } }
```

---

## Endpoints REST

```
POST /search
  Body: { "nom": str, "prenom": str, "commune": str, "annee": int, "generations": int (1-3) }
  Response: { "session_id": "uuid" }

GET /stream/{session_id}
  Response: text/event-stream (SSE)

GET /tree/{session_id}
  Response: { arbre complet }

POST /answer/{session_id}
  Body: { "agent_id": "uuid", "individu_id": "uuid", "choix": 0 | 1 | "texte libre" }
  Response: { "ok": true }

POST /upload/{session_id}/{individu_id}
  Body: multipart/form-data (image ou note)
  Response: { "media": { ...media ajouté... } }

GET /health
  Response: { "status": "ok" }
```
