# Architecture du projet

**Hackathon** : Paris, mars 2026 | Critères : Live Demo 45%, Créativité 35%, Impact 20%

---

## Proposition de valeur

> Tu entres le nom d'un ancêtre. L'agent navigue seul les archives départementales françaises, lit des actes manuscrits de 200 ans, extrait père et mère, remonte la génération suivante — et construit une base de connaissance consultable sémantiquement.

---

## Pipeline

```
[Input] Nom + commune + année approximative
          ↓
[1] Découverte Arkotheque
    GET /_recherche-api/moteur → engine id + filter refs
          ↓
[2] Recherche du registre
    GET /_recherche-api/search/{id}?[filtres] → fiche(s)
    GET /_recherche-api/render-fiche/... → idArkoFile
          ↓
[3] Récupération image
    GET /_recherche-images/show/{ficheId}/image/{idArkoFile}/{pos}
    → JPEG 1300–4256px, public, sans auth
          ↓
[4] OCR + Extraction (Gemini 2.5 Pro Vision)
    → JSON : nom, prénom, date, lieu, père, mère, témoins
          ↓
[5] Embedding + stockage
    gemini-embedding-2-preview → embed fiche JSON + image acte
    → ChromaDB in-memory
          ↓
[6] Boucle récursive
    père.nom + père.commune + (année - estimation)
    → retour à [1] pour la génération précédente
          ↓
[7] UI
    Arbre D3 animé + panneau agents + chatbox
```

---

## Stack technique

| Composant | Outil |
|-----------|-------|
| Archives | Arkotheque ancienne version (4 depts validés) |
| OCR | Gemini 2.5 Pro Vision |
| Embeddings | `gemini-embedding-2-preview` (multimodal, lancé 10 mars 2026) |
| Vector DB | ChromaDB in-memory |
| Backend | FastAPI + Python + httpx |
| Frontend | React + Vite + D3 |
| Déploiement | Cloud Run (back) + Vercel (front) |

---

## Scope hackathon

### MVP obligatoire
1. Input : nom + commune + année
2. Navigation Arkotheque Cher (archives18.fr) — déjà testé
3. OCR live avec Gemini 2.5 Pro
4. Boucle sur 2-3 générations
5. UI : arbre D3 animé + panneau agents

### Bonus si le temps le permet
- Recherche sémantique sur l'arbre ("tous les laboureurs", "même village")
- Support multi-département (Ardennes en fallback)
- Export GEDCOM

### Hors scope
- Records pré-1750 (latin, script différent)
- Nouvelle version Arkotheque (Jura)
- Export PDF

---

## Demo path (happy path pour les juges)

**Génération 1** — validé manuellement
- Prudence Aimée PINÇON, Neuilly-en-Sancerre, 1843
- ficheId=4082, position=5 → Père : Jean Pinçon, laboureur

**Génération 2** — à valider avant le hackathon
- Jean PINÇON, Neuilly-en-Sancerre, ~1810-1820

**Génération 3** — bonus
- Parents de Jean PINÇON, ~1785-1795

---

## Risques et mitigations

| Risque | Probabilité | Mitigation |
|--------|-------------|------------|
| Navigation Arkotheque cassée | Faible | HTTP direct, déjà testé sur 5 depts |
| OCR image dégradée | Moyenne | Pré-sélectionner les folios pour la demo |
| Disambiguation homonymes | Moyenne | Filtrer par commune + fourchette d'années |
| `gemini-embedding-2-preview` instable | Faible | Fallback sur `gemini-embedding-001` (GA) |
| Boucle infinie | Faible | Limiter à 3 générations, timeout par requête |

---

## Argumentaire concours

**Live Demo (45%)** : Un nom → navigation visible → image 1843 → transcription live → parents apparaissent → génération suivante. 5 min de storytelling cinématographique.

**Créativité (35%)** : Aucun concurrent ne ferme cette boucle. Gemini Embedding 2 sorti 4 jours avant. MyHeritage vient de valider le problème via leur propre hackathon.

**Impact (20%)** : ~10M généalogistes français. Arkotheque = millions d'actes non indexés. 2-6h par génération → quelques secondes.
