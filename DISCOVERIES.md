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
| `docs/frontend/TREE_LIBRARY_COMPARISON.md` | **NOUVEAU** — Comparaison D3.js, React Flow, vis-network, @visx, react-d3-tree + recommandation |
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

### Format filtre — deux modes distincts (découverte 2026-03-14)

Le code initial utilisait `extras[mode]=select` partout et les `fieldName` d'aggregation comme clés de filtre. **Faux sur les deux points.**

**Ce qui marche vraiment (validé sur Cher dept 18) :**

1. **Clé de filtre** = `filtres[i].refUnique` depuis l'endpoint `/_recherche-api/moteur` (ex: `arko_default_61011b4c3eacb`), PAS le `fieldName` des properties (ex: `arko_default_615ac9ea049ef`).

2. **Mode** = `input` pour le filtre commune (valeur plain sans hash). Le mode `select` (avec hash `Nom[[arko_fiche_xxx]]`) n'est pas le bon pour le filtre commune de Cher.

3. **`contenuIds[0]`** = obligatoire dans les params (valeur = data-contenu de la page HTML). Cher browse : `"2655739"`.

4. La clé correcte se découvre via `rebond-detail` :
   ```
   GET /_recherche-api/rebond-detail/{moteurRef}/{filtreRef}/{terme}
   → 302 Location : URL complète avec format exact des params
   ```

5. Le **total** dans la réponse reste toujours à la valeur non-filtrée (bug API). Seuls les **résultats** (`results[]`) sont filtrés. Filtrer année localement depuis `intitule`.

6. Filtres année/type d'acte : `rebond-detail` retourne 500 → filtrer **localement** depuis `intitule` (ex: "3E 2346 1843 - 1852").

**Résultats validés avec bon format (Cher, filtre commune Neuilly-en-Sancerre) :**
- `total` affiché : 11254 (faux) — `results` retournés : 34 (correct)
- `id=4082, intitule="3E 2346 1843 - 1852"` bien présent → ficheId confirmé

### Pipeline render-fiche → idArkoFile (découverte 2026-03-14)

Pour obtenir `idArkoFile` d'un registre :
```
GET /_recherche-api/render-fiche/{moteurRef}/{refUnique}/{restitutionRef}/detail/html
→ HTML contenant data-visionneuse='{"idArkoFile": 1997, "refUniqueField": "...", ...}'
```
- `restitutionRef` = `restits[0].refUnique` depuis l'endpoint `moteur`. Cher : `arko_default_61011eb03aad2`.
- L'`id` numérique du résultat search = le `ficheId` dans l'URL image.
- nb_pages : pas dans la réponse → sonder `show/{ficheId}/image/{idArkoFile}/{n}` jusqu'à 404.

### Moteurs "browse" — filtrage côté client
Sur Indre (recensement) et Meurthe-et-Moselle (matricules), les filtres ne réduisent pas le `total` serveur. Il faut paginer via `{moteurRef}--from=N` et filtrer localement.

Pour les moteurs **état civil browse** (Cher moteur 1, Ardennes moteur 6) : le filtre commune marche pour les résultats mais le total reste faux. Le filtre année ne marche pas → filtrage local depuis `intitule`.

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
