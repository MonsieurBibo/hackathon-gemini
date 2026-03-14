# GenealogyAI — Hackathon Gemini Paris 2026

Agent autonome de généalogie française : entre un nom d'ancêtre, remonte l'arbre génération par génération en naviguant seul les archives départementales, lisant les actes manuscrits avec Gemini Vision, et construisant une base de connaissance sémantique.

**Stack** : FastAPI · React/Vite · Gemini 2.5 Pro · gemini-embedding-2-preview · ChromaDB · Arkotheque HTTP API

---

## Lancer le projet

```bash
# Backend
cd backend && pip install -r requirements.txt
cp .env.example .env  # ajouter GEMINI_API_KEY
uvicorn main:app --reload

# Frontend
cd frontend && npm install
npm run dev
```

---

## Documentation

### Projet
| Fichier | Contenu |
|---------|---------|
| `docs/project/architecture.md` | Pipeline complet, stack, demo path, risques |
| `docs/project/competitive.md` | Analyse concurrentielle (généalogie + GS e-commerce) |
| `docs/project/models.md` | Modèles Gemini disponibles et recommandations |
| `docs/project/genealogy-apis.md` | Research sur les APIs généalogiques existantes (FamilySearch, Geneanet, BnF…) |

### Arkotheque (archives départementales françaises)
| Fichier | Contenu |
|---------|---------|
| `docs/arkotheque/overview.md` | Vue d'ensemble, 2 versions, tableau des depts testés |
| `docs/arkotheque/api-old.md` | Endpoints + format filtres version ancienne (majoritaire) |
| `docs/arkotheque/api-new.md` | Endpoints version nouvelle (Jura-style) |
| `docs/arkotheque/departments.md` | IDs précis par département (Cher, Ardennes, Indre, M&M, Jura) |

### Tâches de développement
| Fichier | Contenu |
|---------|---------|
| `docs/tasks/contracts.md` | Contrats de données : JSON, SSE events, endpoints REST |
| `docs/tasks/backend.md` | Tâches B0–B8 avec signatures de fonctions |
| `docs/tasks/frontend.md` | Tâches F0–F6 avec types TypeScript |
| `docs/tasks/roadmap.md` | Phases de développement + critères de done |

### Découvertes
| Fichier | Contenu |
|---------|---------|
| `DISCOVERIES.md` | Résumé des découvertes critiques (API, POC validé) |

---

## POC validé

Acte de naissance de **Prudence Aimée PINÇON**, 3 mars 1843, Neuilly-en-Sancerre (Cher).
Père extrait : Jean Pinçon (laboureur). Pipeline Arkotheque → Gemini OCR fonctionnel.
