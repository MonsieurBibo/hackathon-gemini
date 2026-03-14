# Arkotheque — API version ancienne

> S'applique à : Cher, Ardennes, Indre, Meurthe-et-Moselle, et la majorité des ~80 depts.
> Détection : `GET /js/routing.json` → HTTP 200

---

## Endpoints

```bash
# Détection de version
GET /js/routing.json

# Initialiser un moteur (→ id numérique + filtres + total)
GET /_recherche-api/moteur?refUnique={moteurWidgetRef}&{moteurWidgetRef}--contenuIds[0]={contenuId}

# Rechercher (avec ou sans filtres)
GET /_recherche-api/search/{id}?{moteur}--filtreGroupes[...]

# Rendu HTML d'une fiche (contient idArkoFile + data-visionneuse)
GET /_recherche-api/render-fiche/{moteurRef}/{ficheRef}/{restitRef}/detail/html

# Info visionneuse (liste toutes les pages d'un registre)
GET /_recherche-api/visionneuse-infos/{moteurRef}/{ficheRef}/{fieldRef}/image/{idArkoFile}

# Image d'une page (0-indexé)
GET /_recherche-images/show/{ficheId}/image/{idArkoFile}/{position}

# Crop IIIF haute résolution
GET /_recherche-images/show/{ficheId}/image/{idArkoFile}/{position}/{x,y,w,h}/{width,}/0/default.jpg

# Découvrir le format exact d'un filtre (→ redirection 302 avec URL complète)
GET /_recherche-api/rebond-detail/{moteurRef}/{fieldName}/{terme}

# Pagination
GET /_recherche-api/search/{id}?{moteurRef}--from=N
```

- 25 résultats par page (non configurable)
- Tri par défaut : commune alphabétique + année croissante

---

## Format des filtres (CRITIQUE)

### Format INCOMPLET — ne fonctionne PAS
```
?moteurRef--filtreGroupes[groupes][0][filterRef][q][0]=valeur
&moteurRef--filtreGroupes[mode]=simple
```

### Format COMPLET — obligatoire
```
?{moteur}--filtreGroupes[groupes][0][{filterRef}][q][0]={valeur}
&{moteur}--filtreGroupes[groupes][0][{filterRef}][op]=AND
&{moteur}--filtreGroupes[groupes][0][{filterRef}][extras][mode]=select
&{moteur}--filtreGroupes[operator]=AND
&{moteur}--filtreGroupes[mode]=simple
```

Les champs `[op]=AND` et `[extras][mode]=select` sont **obligatoires**.

### Plusieurs filtres combinés
```
?{moteur}--filtreGroupes[groupes][0][{filter1}][q][0]=valeur1
&{moteur}--filtreGroupes[groupes][0][{filter1}][op]=AND
&{moteur}--filtreGroupes[groupes][0][{filter1}][extras][mode]=select
&{moteur}--filtreGroupes[groupes][1][{filter2}][q][0]=valeur2
&{moteur}--filtreGroupes[groupes][1][{filter2}][op]=AND
&{moteur}--filtreGroupes[groupes][1][{filter2}][extras][mode]=select
&{moteur}--filtreGroupes[operator]=AND
&{moteur}--filtreGroupes[mode]=simple
```

### Format des valeurs
- **Filtre select** : valeur textuelle avec hash → `Charleville[[arko_fiche_676961e5ed375]]`
- **Filtre date ponctuelle** : `1843-01-01[[hash]]`
- **Filtre période** : `1813-1822[[hash]]`
- Les valeurs exactes viennent des `aggregations[*].{fieldName}_terms.buckets[*].key` dans la réponse search

### ⚠️ Moteurs "browse" vs "annotations"
Sur certains moteurs (browse/physique), les filtres **ne réduisent pas le `total`** côté serveur — filtrage géré en JavaScript côté client. Solution : paginer via `{moteur}--from=N` et filtrer localement.

---

## Format des images

| Aspect | Valeur |
|--------|--------|
| Format | JPEG |
| Résolution typique | 1300–4256 × 2000–3040 px |
| Taille typique | 400–525 KB par page |
| Authentification | **Aucune — accès public total** |
| Rate limiting | Non détecté |

---

## Algorithme de découverte automatique pour un nouveau département

```python
# 1. Détecter la version
resp = GET /js/routing.json
# → 200 = ancienne version, continuer ci-dessous

# 2. Trouver la page des registres (menu du site)
# Chercher : href="/archives-numerisees/..." ou "registres-paroissiaux"
# Extraire : data-moteur="arko_default_XXXX" data-contenu="NNNNNN"

# 3. Initialiser le moteur
GET /_recherche-api/moteur?refUnique={moteurWidgetRef}&{moteurWidgetRef}--contenuIds[0]={contenuId}
# → id (numérique), filtres[].refUnique, filtres[].properties[].fieldName

# 4. Scanner tous les moteurs disponibles (alternative)
for i in range(1, 30):
    GET /_recherche-api/search/{i}

# 5. Récupérer les valeurs de filtres disponibles
GET /_recherche-api/search/{id}  # sans filtre
# → aggregations[*].{fieldName}_terms.buckets[*].key

# 6. Construire la requête filtrée (format complet ci-dessus)
```
