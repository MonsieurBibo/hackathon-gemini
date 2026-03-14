# DISCOVERIES

Ce fichier regroupe les découvertes clés du projet. Pour la documentation détaillée, voir `docs/`.

---

## Documents de référence

| Document | Contenu |
|----------|---------|
| `docs/arkotheque/overview.md` | Vue d'ensemble, 2 versions, tableau récapitulatif |
| `docs/arkotheque/api-old.md` | Endpoints + filtres version ancienne (majoritaire) |
| `docs/arkotheque/api-new.md` | Endpoints version nouvelle (Jura-style) |
| `docs/arkotheque/departments.md` | IDs par département testés (Cher, Ardennes, Indre, M&M, Jura) |
| `docs/project/architecture.md` | Pipeline, stack, demo path, risques, argumentaire |
| `docs/project/competitive.md` | Analyse concurrentielle (généalogie + GS e-commerce) |
| `docs/project/models.md` | Modèles Gemini et pricing |
| `docs/project/genealogy-apis.md` | Research APIs généalogiques (FamilySearch, Geneanet, BnF…) |
| `docs/tasks/contracts.md` | Contrats JSON, SSE events, endpoints REST |
| `docs/tasks/backend.md` | Tâches B0–B8 |
| `docs/tasks/frontend.md` | Tâches F0–F6 |
| `docs/tasks/roadmap.md` | Phases + critères de done |

---

## Découvertes critiques (résumé)

### Arkotheque — deux versions coexistent
- **Ancienne** (majoritaire) : `routing.json` présent, IDs `arko_default_XXX`, images via `/_recherche-images/show/`
- **Nouvelle** (Jura) : `routing.json` absent, formulaires UUID, images via `/images/{uuid}.jpg`
- Détection : `GET /js/routing.json` → 200 (ancienne) ou 404 (nouvelle)

### Format filtre — erreur initiale corrigée
Le format minimal documenté initialement **ne fonctionne pas**. Il faut absolument ajouter `[op]=AND` et `[extras][mode]=select` à chaque filtre. Voir `docs/arkotheque-api.md`.

### Moteurs "browse" — filtrage côté client
Sur Indre (recensement) et Meurthe-et-Moselle (matricules), les filtres ne réduisent pas le `total` serveur. Il faut paginer via `{moteurRef}--from=N` et filtrer localement.

### Accès images — 100% public, aucune auth
Confirmé sur 5 départements et 4 types d'actes. Aucun rate limiting détecté.

### Soldats indexés publics vs privés
- Cher (18) : **publics** → pipeline nominatif direct possible
- Meurthe-et-Moselle (54) : **privés** (login requis) → OCR page par page obligatoire

### Gemini Embedding 2 — modèle à utiliser
`gemini-embedding-2-preview` (lancé le 10 mars 2026) — multimodal, top MTEB FR.
Les anciens modèles (`gemini-embedding-exp-03-07`, `text-embedding-004`) sont dépréciés.

---

## B7 — Endpoints REST + SSE (implémenté)

**Choix : `asyncio.Queue` + `put_nowait` comme pont callback→SSE**

L'agent récursif utilise un callback synchrone `event_cb(SSEEvent) -> None` (choix initial fait pour la testabilité des agents). Pour brancher ça sur FastAPI SSE :
- `POST /search` crée une `asyncio.Queue`, injecte `queue.put_nowait` comme `event_cb`, lance `build_arbre()` via `asyncio.create_task()`.
- `GET /stream/{session_id}` consomme la queue dans un generator async → `StreamingResponse(media_type="text/event-stream")`.
- `GET /tree/{session_id}` retourne l'`Arbre` JSON stocké en mémoire (202 si encore en cours).

**Pourquoi pas un `asyncio.Queue` async dans l'agent ?** Le `put_nowait()` synchrone fonctionne car l'agent tourne dans le même event loop que FastAPI — pas besoin de `await queue.put()`. Ça préserve la signature synchrone du callback qui simplifie les tests unitaires.

**Sentinel double** : `build_arbre` émet `DoneEvent` (signal applicatif), puis le `finally` met `None` dans la queue (filet de sécurité si exception avant `DoneEvent`). Le generator SSE casse sur l'un ou l'autre en premier.

**Session store** : dict in-memory `_sessions`, suffisant pour le hackathon (pas de TTL, pas de persistence).

**Résultats** : 76 tests passent (8 nouveaux pour les endpoints).

---

## POC validé

**Acte de naissance — Prudence Aimée PINÇON, 3 mars 1843, Neuilly-en-Sancerre (Cher)**
- Archives18.fr, registre 3E 2346, ficheId=4082, idArkoFile=1997, position=5
- Père : Jean Pinçon (laboureur) | Mère : Jeanne Aimée Dalloy
- Image : `https://www.archives18.fr/_recherche-images/show/4082/image/1997/5`
