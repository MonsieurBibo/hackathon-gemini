# Arkotheque — API version nouvelle (Jura-style)

> S'applique à : Jura (39), et quelques autres départements minoritaires.
> Détection : `GET /js/routing.json` → HTTP 404

---

## Endpoints

```bash
# Lister les formulaires de recherche disponibles
GET /page/acces-aux-documents-numerises  # → HTML avec formulaires

# Rechercher
GET /search/results
  ?formUuid={uuid}
  &0-controlledAccessGeographicName={commune}
  &2-controlledAccessSubject={MARIAGE|NAISSANCE|DECES|BAPTEME}
  &4-date_begin={annee}
  &4-date_end={annee}
  &sort=referencecode_asc
  &mode=list
# → HTML avec liens ARK : /ark:/36595/{arkName}/{mediaUuid}

# Métadonnées + liste des pages d'un registre
GET /visualizer/api?naan=36595&arkName={arkName}&uuid={mediaUuid}
# → JSON : data["media"][i]["location"]["original"] = URL image i

# Image directe
GET /images/{uuid}.jpg            # Original haute résolution
GET /images/{uuid}_thumbnail.jpg  # Miniature
```

---

## Paramètres de recherche

| Paramètre | Description |
|-----------|-------------|
| `0-controlledAccessGeographicName` | Commune |
| `1-controlledAccessPhysicalCharacteristic` | Type physique |
| `2-controlledAccessSubject` | Type d'acte (MARIAGE, NAISSANCE, DECES, BAPTEME…) |
| `4-date_begin` / `4-date_end` | Fourchette d'années |

---

## Exemple — Jura (archives39.fr)

### Formulaires disponibles
| Formulaire | UUID |
|-----------|------|
| Registres paroissiaux et état-civil | `1eb1f0a3-b7ba-4c8a-bdae-395b322800e4` |
| Dénombrements de population | `0400d188-e8a7-4e0e-931f-9023104d59a0` |
| Dispenses de mariage (1742-1791) | `dc9dfd64-14e6-4345-9c0a-9bba2e9f5e63` |
| Matricules militaires | `e9d5f8fe-3bed-4634-b4ed-be1c714f0c98` |

### Requête — Mariages à Dole, 1870-1900
```
GET https://archives39.fr/search/results
  ?formUuid=1eb1f0a3-b7ba-4c8a-bdae-395b322800e4
  &0-controlledAccessGeographicName=Dole%2C+commune
  &2-controlledAccessSubject=MARIAGE
  &4-date_begin=1870
  &4-date_end=1900
  &sort=referencecode_asc
  &mode=list
→ 31 registres
```

### Image validée — Mariage, Dole, 1870
- arkName : `st98bn3lxfrg` | mediaUuid : `9798831d-239f-444b-8ca6-f0cb9503b9ad`
- 49 pages, 4256×3040 px, 524 KB

```bash
# Métadonnées
https://archives39.fr/visualizer/api?naan=36595&arkName=st98bn3lxfrg&uuid=9798831d-239f-444b-8ca6-f0cb9503b9ad

# Image page 0
https://archives39.fr/images/9798831d-239f-444b-8ca6-f0cb9503b9ad.jpg
```
