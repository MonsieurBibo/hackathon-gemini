# Roadmap & Critères de done

---

## Ordre de développement

```
Phase 1 — Fondations (tout en parallèle)
  B0  Setup backend
  F0  Setup frontend
  F1  Types TypeScript

Phase 2 — Services (en parallèle)
  B1  Client Arkotheque     (dépend B0)
  B3  Service Gemini        (dépend B0)
  F2  Hook SSE              (dépend F0, F1)

Phase 3 — Core agent
  B2  Agent OCR             (dépend B1, B3)
  B4  Agent récursif        (dépend B1, B2, B3)
  B7  Endpoints REST + SSE  (dépend B4)

Phase 4 — UI (en parallèle, dès que B7 répond)
  F3  Arbre D3              (dépend F2)
  F4  Panneau agents        (dépend F2)
  F5  Fiche individu        (dépend F1)
  F6  Formulaire + Chatbox  (dépend F1)

Phase 5 — Bonus (si le temps le permet)
  B5  Cascade fallback      (améliore B4)
  B6  ChromaDB embeddings   (dépend B3)
  B8  Agent post-1900       (indépendant)
```

---

## Critères de done

| Tâche | Critère |
|-------|---------|
| B0 | `GET /health` répond 200 |
| B1 | Retrouve la fiche Prudence PINÇON (ficheId=4082, archives18.fr) |
| B2 | OCR correct sur l'acte de naissance de Prudence PINÇON |
| B3 | Embedding généré sans erreur, longueur 3072 |
| B4 | Remonte 2 générations depuis Prudence PINÇON sans intervention manuelle |
| B5 | Trouve un individu en élargissant la fenêtre ±5 ans |
| B6 | Recherche "laboureur Berry" retourne des résultats pertinents |
| B7 | Stream SSE reçu côté frontend avec tous les event types |
| B8 | Génère un courrier de demande pour un acte post-1900 |
| F0 | `npm run dev` tourne sans erreur |
| F1 | Tous les types compilent sans erreur TypeScript |
| F2 | Hook reçoit events SSE mockés et met à jour l'état correctement |
| F3 | Arbre avec 5 nœuds mockés, animation présente, clic fonctionnel |
| F4 | Panneau affiche 2 agents avec statuts différents |
| F5 | Fiche s'ouvre avec toutes les sections visibles |
| F6 | Formulaire soumet et démarre le stream SSE réel |

---

## Données de test de référence

**Individu de départ** : Prudence Aimée PINÇON, Neuilly-en-Sancerre (18), 3 mars 1843
- ficheId=4082, idArkoFile=1997, position=5
- Image : `https://www.archives18.fr/_recherche-images/show/4082/image/1997/5`
- Père extrait : Jean Pinçon — Mère : Jeanne Aimée Dalloy
