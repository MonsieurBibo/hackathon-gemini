# Tâches Backend

> Référence : contrats dans `contracts.md`, API Arkotheque dans `../arkotheque-api.md`

---

## B0 — Setup projet
**Dépendances** : aucune | **Bloque** : tout

Structure :
```
backend/
  main.py
  agents/
    recursive_agent.py
    ocr_agent.py
    admin_agent.py
  services/
    arkotheque.py
    gemini.py
    chromadb.py
    geocoding.py
  models/
    individu.py
    arbre.py
    events.py
  utils/
    fuzzy.py
    fallback.py
```

- `requirements.txt` : `fastapi`, `uvicorn`, `google-genai`, `chromadb`, `httpx`, `python-multipart`, `python-Levenshtein`
- `.env.example` : `GEMINI_API_KEY=`
- CORS pour `http://localhost:5173`
- `GET /health` → `{ "status": "ok" }`

---

## B1 — Client Arkotheque
**Dépendances** : B0 | **Bloque** : B2, B4

```python
async def detect_version(base_url: str) -> str:
    # GET /js/routing.json → 200 = "old", 404 = "new"

async def get_moteurs(base_url: str) -> dict:
    # GET /_recherche-api/moteur/init/{id}

async def search_acte(
    base_url: str, moteur_ref: str,
    nom: str, prenom: str, commune: str,
    annee_debut: int, annee_fin: int
) -> list[dict]:
    # Format filtre obligatoire : [op]=AND + [extras][mode]=select

async def get_fiche(base_url: str, fiche_id: int) -> dict:
    # GET /_recherche-api/render-fiche/{id}

async def get_image_urls(base_url: str, fiche_id: int) -> list[str]:
    # GET /_recherche-api/visionneuse-infos/{fiche_id}

async def get_image_bytes(url: str) -> bytes:
    # Pas d'auth requise
```

Départements préconfigurés : Cher `www.archives18.fr`, Ardennes `archives.cd08.fr`, Indre `www.archives36.fr`

Détection dept depuis commune : `https://geo.api.gouv.fr/communes?nom={commune}&fields=departement`

---

## B2 — Agent OCR (F3)
**Dépendances** : B0, B1, B3 | **Bloque** : B4

```python
def select_pages(
    image_urls: list[str],
    type_registre: str,  # "table_decennale" | "registre" | "alphabetique"
    nom: str, annee_cible: int,
    annee_debut_registre: int, annee_fin_registre: int
) -> list[int]:
    # table_decennale : position proportionnelle de l'année → max 3 pages
    # alphabetique : estime position selon première lettre du nom
    # registre : offset = annee_cible - annee_debut

async def ocr_pages(
    image_urls: list[str], page_indices: list[int],
    context: str, stream_callback: callable
) -> dict | None:
    # Envoie pages à Gemini 2.5 Pro Vision
    # None si individu pas trouvé → déclenche page suivante
```

Prompt OCR :
```
Tu es un expert en paléographie française des XVIIIe-XIXe siècles.
Extrais en JSON : type_acte, individu {nom, prenom, date, commune},
pere {nom, prenom, profession}, mere {nom, prenom, profession}, temoins, notes.
Si illisible → null. Ne devine pas.
```

---

## B3 — Service Gemini
**Dépendances** : B0 | **Bloque** : B2, B4, B8

```python
async def ocr_image(image_bytes: bytes, prompt: str, stream_callback=None) -> str:
    # gemini-2.5-pro, streaming si callback fourni

async def embed_text_and_image(text: str, image_bytes: bytes = None) -> list[float]:
    # gemini-embedding-2-preview → vecteur float[3072]

async def answer_admin_question(context: str, question: str) -> str:
    # gemini-2.5-pro, pour B8
```

---

## B4 — Agent récursif (CORE)
**Dépendances** : B0, B1, B2, B3 | **Bloque** : B5, B6, B7

```python
async def run_recursive_search(
    nom: str, prenom: str, commune: str, annee: int,
    generations_max: int, session_id: str, event_queue: asyncio.Queue
) -> Arbre:
    # 1. Dept depuis commune (INSEE)
    # 2. base_url Arkotheque pour ce dept
    # 3. Cherche acte de naissance (B1)
    # 4. OCR avec sélection de pages (B2)
    # 5. Extrait père + mère
    # 6. Émet event: individual
    # 7. Récursion séquentielle (père d'abord, puis mère)
    # 8. Émet event: done à generation_max

async def enrich_individu(individu: Individu, event_queue: asyncio.Queue) -> Individu:
    # Cherche mariage, décès
    # Si homme 1850-1920 : cherche matricule
    # Si dispo : cherche recensement
    # Émet event: individual_update par acte trouvé
```

---

## B5 — Cascade fallback
**Dépendances** : B4 | **Bloque** : rien

```python
async def search_with_fallback(...) -> dict | None:
    # T1 : commune exacte + année exacte
    # T2 : fuzzy nom (Levenshtein ≤2) + ±5 ans
    # T3 : communes limitrophes (INSEE)
    # T4 : source alternative (mariage si naissance introuvable)
    # T5 : event: question → attend 30s
    # T6 : nœud "inconnu"
    # Émet event: fallback à chaque tentative

def get_communes_limitrophes(commune: str, dept: str) -> list[str]:
    # https://geo.api.gouv.fr/communes/{code}/communes-limitrophes

def fuzzy_nom_variants(nom: str) -> list[str]:
    # "Pinçon" → ["Pincon", "Pinsson", "Pinson", ...]
```

---

## B6 — ChromaDB + Embeddings
**Dépendances** : B0, B3 | **Bloque** : rien

```python
def init_collection() -> chromadb.Collection:
    # "ancetres", in-memory

async def store_individu(individu: Individu, image_bytes: bytes = None):
    # embed texte fiche + image acte → ChromaDB

async def search_similar(query: str, n_results: int = 5) -> list[Individu]:
    # ex: "tous les laboureurs du Berry"
```

---

## B7 — Endpoints REST + SSE
**Dépendances** : B0, B4 | **Bloque** : frontend

- `POST /search` : crée session + lance `run_recursive_search` en background task
- `GET /stream/{session_id}` : consomme `event_queue` en SSE
- Sessions in-memory : `dict[session_id → {queue, arbre, agents}]`
- Timeout session : 30 min

---

## B8 — Agent post-1900 (F1)
**Dépendances** : B0, B3 | **Bloque** : rien

```python
async def handle_post_1900(
    nom: str, prenom: str, commune: str, annee: int,
    lien_famille: str  # "moi-même" | "parent" | "grand-parent" | "autre"
) -> dict:
    # Détermine administration : mairie, CNAFF, Ministère des Armées
    # Génère courrier pré-rempli
    # Retourne : { "administration": {...}, "courrier": str, "delai": str }
```
