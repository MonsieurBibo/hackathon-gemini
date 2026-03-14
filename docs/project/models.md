# Modèles Gemini — Mars 2026

---

## Modèles disponibles

| Rôle | Modèle | Prix input | Prix output | Points forts |
|------|--------|-----------|------------|--------------|
| OCR / Vision | `gemini-3.1-flash` | $0.15/M | $0.60/M | OCR manuscrits, faible coût volume (~4 000 pages/$1) |
| Raisonnement complexe | `gemini-3.1-pro` | $1.25/M | $5.00/M | Thinking L2, contexte 1M tokens, désambiguïsation noms |
| Routing / tâches simples | `gemini-3.1-flash-lite` | $0.05/M | $0.20/M | Latence <100ms |
| Embeddings | `gemini-embedding-2-preview` | $0.10/M | N/A | Multimodal (texte+image+vidéo+audio+PDF), top MTEB FR |
| Génération image | `imagen-4.0-ultra` | N/A | $0.03/image | UI/prototypage |

## Coût image

~258 tokens par image (constant quelle que soit la résolution, patch-based).

---

## Recommandations pour ce projet

| Tâche | Modèle |
|-------|--------|
| OCR actes manuscrits | `gemini-3.1-flash` |
| Désambiguïsation, raisonnement cross-sources | `gemini-3.1-pro` |
| Embeddings fiches + images actes | `gemini-embedding-2-preview` |
| Agent post-1900 (génération courrier) | `gemini-3.1-flash` |

**Fallback embeddings** : si `gemini-embedding-2-preview` instable (preview) → `gemini-embedding-001` (GA, texte seulement).
