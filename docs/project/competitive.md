# Paysage concurrentiel — Mars 2026

---

## Généalogie autonome — gap confirmé

Aucun outil ne réalise la boucle complète :
> Navigation autonome → OCR images brutes non indexées → Extraction structurée → Récursivité

| Outil | Ce qu'il fait | Ce qu'il NE fait PAS |
|-------|--------------|----------------------|
| **MyHeritage Scribe AI** (lancé 4 mars 2026) | OCR + extraction sur document uploadé manuellement | Navigation autonome, Arkotheque, boucle récursive |
| **TreePilot** (mars 2026) | Agent multi-sources (Wikipedia, Wikidata) | Anglais seulement, zéro OCR images brutes |
| **FamilySearch AI** | OCR + full-text search dans leur base indexée | Archives externes, récursivité, records non indexés |
| **Ancestry AI** (janv. 2026) | Chat sur leur base de 20Md de records | Silo propriétaire, pas d'Arkotheque |
| **Geneanet** | Recherche dans 40M actes indexés par bénévoles | Pas d'OCR live, pas de navigation autonome |
| **Filae** | 250M actes 19e indexés | Pas d'API publique, pré-1800 faible |

**Pourquoi Gemini 2.5 Pro** : meilleur modèle sur manuscrits historiques (tests communauté généalogique mars 2026), quasi sans erreur sur actes de 1791.

---

## Gaussian Splat e-commerce — gap confirmé

Aucun produit commercial ne fait : `URL produit → image seule → 3DGS → placement dans la pièce` sans vidéo physique.

| Outil | Limitation critique |
|-------|---------------------|
| **Voxelo** | Vidéo physique obligatoire (2-3 min de filmage) |
| **Graswald** ($3.3M levés) | Vidéo physique obligatoire |
| **Reflct** | Viewer seulement, pas de génération |
| **DecorViz AI** | 2D seulement |
| **IKEA Place / Wayfair AR** | Catalogue propriétaire uniquement |

Stack open source disponible : Apple SHARP (image→GS en <1s), DiffSplat (ICLR 2025), InstantMesh.

---

## Gemini Embedding 2 — état mars 2026

| Modèle | Statut | Modalités |
|--------|--------|-----------|
| `gemini-embedding-2-preview` | Preview (lancé **10 mars 2026**) | Texte + Image + Vidéo + Audio + PDF |
| `gemini-embedding-001` | GA | Texte seulement |
| `gemini-embedding-exp-03-07` | **DÉPRÉCIÉ** jan. 2026 | — |
| `text-embedding-004` | **DÉPRÉCIÉ** août 2025 | — |

Premier modèle multimodal Google. Top MTEB multilingue. $0.20/million tokens texte.

---

## Autres idées hackathon (classées)

| Idée | Score |
|------|-------|
| **EchoTrace** — cold case multi-modal, Gemini Embedding 2 | 8.5/10 |
| **MotionRx** — vidéo sport → biomécanique → risque blessure | 8/10 |
| **SoundBriefing** — interprétation live + détection dérive sémantique | 7.5/10 |
| **PlanScanner** — permis de construire : plan + code → rapport violations | 7/10 |
| **JudgeRoom** — déposition live → contradictions avec dossier 1M tokens | 7/10 |
