# Arkotheque — IDs par département testés

Dernière mise à jour : 2026-03-14

---

## Cher — archives18.fr (ancienne version)

**URL** : `https://www.archives18.fr`

### Moteurs
| Engine | Collection | Total |
|--------|-----------|-------|
| 1 | Registres paroissiaux et état civil (browse) | ~8 000 |
| 4 | Registres matricules militaires (browse) | 514 |
| 5 | Soldats indexés — **PUBLICS** | 133 879 |
| 9 | Annotations registres paroissiaux | (crowdsourcé) |

### Moteur 1 — État civil
- Widget refUnique : `arko_default_61011a8e5db65`
- Filtre commune : `arko_default_61011b4c3eacb`
- Filtre type d'acte : `arko_default_61011b4c4f010`
- Filtre année : `arko_default_61011b4c62fc5`

### Acte POC validé — Prudence Aimée PINÇON
- Registre : 3E 2346 (Naissances 1843-1852)
- ficheId : 4082 | idArkoFile : 1997 | 259 images
- Acte N°13, image position 5
- Née le 3 mars 1843, Neuilly-en-Sancerre
- Père : Jean Pinçon (laboureur) | Mère : Jeanne Aimée Dalloy

```
https://www.archives18.fr/_recherche-images/show/4082/image/1997/5
```

---

## Ardennes — archives.cd08.fr (ancienne version)

**URL** : `https://archives.cd08.fr`

### Moteurs
| Engine | Collection | Total |
|--------|-----------|-------|
| 6 | Registres paroissiaux et état civil (browse) | 15 029 |
| 7 | Annotations registres paroissiaux | 279 121 |
| 10 | Registres matricules militaires | 1 856 |
| 12 | Annotations matricules | 145 315 |

### Moteur 6 — État civil
- Widget refUnique : `arko_default_6776ac3012e9d`
- Filtre commune : `arko_default_6776acf636161` (fieldName : `arko_default_67764c817422f`)
- Filtre date : `arko_default_6776acf64bf69` (fieldName : `arko_default_67764c880046a`)

#### Top communes
- Charleville : `Charleville[[arko_fiche_676961e5ed375]]`
- Sedan : `Sedan[[arko_fiche_676961ec377d3]]`
- Mézières : `Mézières[[arko_fiche_676961ea6d393]]`

#### Top périodes
- 1813-1822 : `1813-1822[[1d68fb89ac08a6453df7a36db2ba286673156f9c]]`
- 1823-1832 : `1823-1832[[312ac0a581f1672a5ba5612024228238d94dab26]]`

### Image validée — Naissance, Adon, 1813-1822
- ficheId : 22752 | idArkoFile : 20004 | 35 pages | 2800×1954 px

```bash
https://archives.cd08.fr/_recherche-images/show/22752/image/20004/0
# Crop IIIF moitié supérieure, 700px :
https://archives.cd08.fr/_recherche-images/show/22752/image/20004/0/0,0,2800,977/700,/0/default.jpg
```

---

## Indre — archives36.fr (ancienne version)

**URL** : `https://www.archives36.fr`

### Moteurs
| Engine | Collection | Total |
|--------|-----------|-------|
| 3 | Cadastre | 4 430 |
| **5** | **Recensement** | **4 679** |
| 6 | Matricules militaires (browse) | 549 |
| 7 | Notaires | 30 185 |
| 8 | État civil | 8 028 |
| 9 | Annotations matricules | 183 829 |

### Moteur 5 — Recensement
- refUnique : `arko_default_61a0ae5412613`
- Années dispo : 1836, 1841, 1846, 1851, 1856, 1861, 1866, 1872, 1876, 1881, 1886, 1891, 1896, 1901, 1906, 1911, 1921, 1926, 1931, 1936
- ⚠️ Filtres côté client — paginer via `?arko_default_61a0ae5412613--from=N`

### Images validées — Recensement 1901
```bash
# Châteauroux — ficheId=16701, idArkoFile=16510, 380 pages
https://www.archives36.fr/_recherche-images/show/16701/image/16510/0
# Aigurande — ficheId=16648, idArkoFile=16457, 43 pages
https://www.archives36.fr/_recherche-images/show/16648/image/16457/0
```

---

## Meurthe-et-Moselle — archivesenligne.meurthe-et-moselle.fr (ancienne version)

**URL** : `https://archivesenligne.meurthe-et-moselle.fr`

### Moteurs
| Engine | Collection | Total |
|--------|-----------|-------|
| 1 | État civil | 7 237 |
| **3** | **Matricules militaires (browse)** | **314** |
| 4 | Recensements | 6 775 |
| 5 | Tables de successions | 5 952 |
| 7 | Cadastre napoléonien | 1 680 |
| **11** | **Soldats indexés — PRIVÉS (login requis)** | 43 174 |

### Moteur 3 — Matricules militaires
- refUnique : `arko_default_62bc69358b041`
- Filtres : Bureau recrutement → Nancy (143), Toul (150) | Classe → format `1890-01-01[[hash]]`
- ⚠️ Filtres côté client — paginer les 314 résultats

### Image validée — Classe 1890, Bureau Nancy
- Cote : 1 R 1229 | ficheId : 7433 | idArkoFile : 7809 | 713 pages

```bash
https://archivesenligne.meurthe-et-moselle.fr/_recherche-images/show/7433/image/7809/0
```

---

## Jura — archives39.fr (NOUVELLE version)

**URL** : `https://archives39.fr` (sans www)

⚠️ API complètement différente — voir `api-new.md`

Formulaires UUID dans `api-new.md`.
