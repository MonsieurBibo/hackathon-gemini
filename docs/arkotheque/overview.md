# Arkotheque — Vue d'ensemble

**Éditeur** : 1égal2 (Symfony + FOSJsRoutingBundle + React)
**Couverture** : ~80 départements français
**Testée sur** : Cher (18), Ardennes (08), Indre (36), Meurthe-et-Moselle (54), Jura (39)

---

## Deux versions coexistent

| | Version ancienne (majoritaire) | Version nouvelle (minoritaire) |
|--|-------------------------------|-------------------------------|
| **Détection** | `GET /js/routing.json` → 200 | `GET /js/routing.json` → 404 |
| **Moteurs** | IDs numériques (`search/1`) | UUIDs (`search/form/{uuid}`) |
| **Filtres** | `arko_default_XXXX` | Paramètres GET nommés |
| **Images** | `/_recherche-images/show/{ficheId}/image/{fileId}/{pos}` | `/images/{uuid}.jpg` |
| **Exemples** | Cher, Ardennes, Indre, M&M | Jura |
| **Doc** | `api-old.md` | `api-new.md` |

**Algorithme de détection** :
```python
resp = GET /js/routing.json
version = "old" if resp.status == 200 else "new"
```

---

## Ce qui est identique entre tous les départements (ancienne version)

- Routes dans `routing.json` (mêmes noms, même structure)
- Format URL image `/_recherche-images/show/{id}/image/{fileId}/{pos}`
- Format IIIF crop
- Endpoints `render-fiche`, `visionneuse-infos`, `rebond-detail`
- Structure JSON des réponses `search/{id}`
- **Accès images : 100% public, aucune auth, aucun rate limiting détecté**

## Ce qui diffère entre départements

- `arko_default_XXXX` : générés au déploiement, uniques par site
- IDs numériques des moteurs (engine 1, 3, 5… différents)
- Valeurs d'agrégation et leurs hashes `[[...]]`
- Types de moteurs disponibles (ex: soldats indexés publics ou privés)
- Format des dates (ponctuel vs période)

---

## Tableau récapitulatif des départements testés

| Département | URL | Version | État civil | Recensement | Matricules | Soldats indexés publics |
|------------|-----|---------|-----------|-------------|-----------|------------------------|
| Cher (18) | archives18.fr | Ancienne | Engine 1 | — | Engine 4 | **Oui** (Engine 5) |
| Ardennes (08) | archives.cd08.fr | Ancienne | Engine 6 | — | Engine 10 | Oui (Engine 7) |
| Indre (36) | archives36.fr | Ancienne | Engine 8 | Engine 5 | Engine 6 | Oui (Engine 9) |
| M-et-M (54) | archivesenligne.mm.fr | Ancienne | Engine 1 | Engine 4 | Engine 3 | **Non** (Engine 11 privé) |
| Jura (39) | archives39.fr | **Nouvelle** | UUID | UUID | UUID | N/A |

**Recommandation hackathon** : Cher (18) en priorité — soldats publics + POC déjà validé.
