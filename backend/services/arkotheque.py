"""
Client Arkotheque — version ancienne (routing.json présent).
Couvre : Cher (18), Ardennes (08), Indre (36), Meurthe-et-Moselle (54).

Ref tâche    : B1 (docs/tasks/backend.md)
Ref API      : docs/arkotheque/api-old.md
Ref IDs      : docs/arkotheque/departments.md
Ref contrats : docs/tasks/contracts.md

Points critiques (découvertes 2026-03-14) :
- La réponse search retourne {total, results[]} — pas {hits:{hits:[]}}
- aggregations est une LISTE, pas un dict
- Le total affiché est toujours faux (non-filtré) ; seuls results[] sont filtrés
- Filtre commune : clé = filtres[i].refUnique du moteur (pas le fieldName d'agg)
  - mode="input" + valeur plain (Cher 18)
  - mode="select" + valeur avec hash (Ardennes 08)
- contenuIds[0] obligatoire pour le Cher ; absent du moteur metadata pour autres depts
- idArkoFile se récupère via render-fiche → data-visionneuse JSON dans le HTML
- Filtrage année/type : côté client depuis intitule (ex: "3E 2346 1843 - 1852")
"""
from __future__ import annotations

import json
import re

import httpx


# ---------------------------------------------------------------------------
# Config par département
# ---------------------------------------------------------------------------
DEPT_CONFIG: dict[str, dict] = {
    "18": {
        "base_url": "https://www.archives18.fr",
        "moteur_id": 1,
        "moteur_ref": "arko_default_61011a8e5db65",
        "contenu_id": "2655739",
        "restitution_ref": "arko_default_61011eb03aad2",
        "filter_commune": "arko_default_61011b4c3eacb",
        "filter_commune_mode": "input",   # valeur plain, sans hash
    },
    "08": {
        "base_url": "https://archives.cd08.fr",
        "moteur_id": 6,
        "moteur_ref": "arko_default_6776ac3012e9d",
        "contenu_id": None,
        "restitution_ref": "arko_default_6776af9fd9f6f",
        "filter_commune": "arko_default_6776acf636161",      # filtres[i].refUnique → clé param
        "filter_commune_agg": "arko_default_67764c817422f",  # fieldName agg → chercher bucket
        "filter_commune_mode": "select",                     # valeur avec hash [[arko_fiche_xxx]]
        "filter_annee": "arko_default_6776acf64bf69",        # filtres[1].refUnique → clé param
        "filter_annee_agg": "arko_default_67764c880046a",    # fieldName agg → chercher bucket
    },
    "36": {
        "base_url": "https://www.archives36.fr",
        "moteur_id": 8,
        "moteur_ref": "arko_default_61a0ae5412613",
        "contenu_id": None,
        "restitution_ref": None,
        "filter_commune": None,
        "filter_commune_mode": None,
    },
    "54": {
        "base_url": "https://archivesenligne.meurthe-et-moselle.fr",
        "moteur_id": 1,
        "moteur_ref": "arko_default_62bc69358b041",
        "contenu_id": None,
        "restitution_ref": None,
        "filter_commune": None,
        "filter_commune_mode": None,
    },
}


def get_config(dept: str) -> dict:
    cfg = DEPT_CONFIG.get(dept)
    if not cfg:
        raise ValueError(f"Département {dept!r} non supporté")
    return cfg


# ---------------------------------------------------------------------------
# Détection de version
# ---------------------------------------------------------------------------
async def detect_version(base_url: str) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{base_url}/js/routing.json")
        return "old" if resp.status_code == 200 else "new"


# ---------------------------------------------------------------------------
# Helpers filtres (conservés pour mode select + découverte aggregations)
# ---------------------------------------------------------------------------
def _build_filter_params(
    moteur_ref: str,
    filters: list[tuple[str, str]],
    mode: str = "select",
) -> dict:
    """Construit les query params au format Arkotheque complet."""
    params: dict[str, str] = {
        f"{moteur_ref}--filtreGroupes[operator]": "AND",
        f"{moteur_ref}--filtreGroupes[mode]": "simple",
    }
    for i, (filter_ref, value) in enumerate(filters):
        prefix = f"{moteur_ref}--filtreGroupes[groupes][{i}][{filter_ref}]"
        params[f"{prefix}[q][0]"] = value
        params[f"{prefix}[op]"] = "AND"
        params[f"{prefix}[extras][mode]"] = mode
    return params


def _get_aggregations(data: dict) -> list[dict]:
    """Retourne aggregations comme liste (format réel de l'API)."""
    aggs = data.get("aggregations", [])
    if isinstance(aggs, dict):
        # Compatibilité avec les mocks de tests
        return [aggs]
    return aggs


def _find_bucket_value(aggregations: list[dict], field_ref: str, term: str) -> str | None:
    """Trouve la valeur exacte (avec hash) d'un terme dans les aggregations."""
    for agg in aggregations:
        sub = agg.get(field_ref, {})
        for key, val in sub.items():
            if isinstance(val, dict) and "buckets" in val:
                for bucket in val["buckets"]:
                    key_str: str = str(bucket.get("key", ""))
                    if term.lower() in key_str.lower():
                        return key_str
    return None


def _find_period_bucket(
    aggregations: list[dict], filter_ref: str, annee_debut: int, annee_fin: int
) -> str | None:
    """Trouve le bucket de période qui couvre l'intervalle cible."""
    best: str | None = None
    for agg in aggregations:
        sub = agg.get(filter_ref, {})
        for key, val in sub.items():
            if isinstance(val, dict) and "buckets" in val:
                for bucket in val["buckets"]:
                    key_str: str = str(bucket.get("key", ""))
                    part = key_str.split("[[")[0].strip()
                    if "-" in part:
                        try:
                            start, end = (int(x) for x in part.split("-"))
                            if start <= annee_fin and end >= annee_debut:
                                best = key_str
                        except ValueError:
                            continue
    return best


# ---------------------------------------------------------------------------
# Recherche principale
# ---------------------------------------------------------------------------
def _covers_year_range(intitule: str, annee_debut: int, annee_fin: int) -> bool:
    """Vérifie si un intitulé de registre couvre la période cible."""
    match = re.search(r"(\d{4})\s*[-–]\s*(\d{4})", intitule)
    if match:
        start, end = int(match.group(1)), int(match.group(2))
        return start <= annee_fin and end >= annee_debut
    match = re.search(r"(\d{4})", intitule)
    if match:
        year = int(match.group(1))
        return annee_debut <= year <= annee_fin
    return False


async def _fetch_id_arko_file(
    base_url: str, moteur_ref: str, fiche_ref: str, restitution_ref: str
) -> tuple[int | None, str | None]:
    """
    Appelle render-fiche et extrait idArkoFile + fieldRef depuis data-visionneuse.
    Retourne (None, None) si non trouvé.
    """
    url = (
        f"{base_url}/_recherche-api/render-fiche"
        f"/{moteur_ref}/{fiche_ref}/{restitution_ref}/detail/html"
    )
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return None, None
    m = re.search(r'data-visionneuse="([^"]+)"', resp.text)
    if not m:
        return None, None
    try:
        vis = json.loads(m.group(1).replace("&quot;", '"'))
        return vis.get("idArkoFile"), vis.get("refUniqueField")
    except (json.JSONDecodeError, AttributeError):
        return None, None


def _parse_hit(result: dict, id_arko_file: int | None, field_ref: str | None) -> dict:
    return {
        "fiche_id": result.get("id"),
        "titre": result.get("intitule", ""),
        "refUnique": result.get("refUnique", ""),
        "id_arko_file": id_arko_file,
        "field_ref": field_ref,
        "raw": result,
    }


async def search_acte(
    dept: str,
    commune: str,
    annee_debut: int,
    annee_fin: int,
) -> list[dict]:
    """
    Cherche les registres d'état civil couvrant une commune et une période.

    Retourne une liste de hits, chacun contenant :
      fiche_id, titre, refUnique, id_arko_file, field_ref, raw
    """
    cfg = get_config(dept)
    base_url = cfg["base_url"]
    moteur_id = cfg["moteur_id"]
    moteur_ref = cfg["moteur_ref"]

    params: dict[str, str] = {
        f"{moteur_ref}--filtreGroupes[operator]": "AND",
        f"{moteur_ref}--filtreGroupes[mode]": "simple",
    }
    if cfg.get("contenu_id"):
        params[f"{moteur_ref}--contenuIds[0]"] = cfg["contenu_id"]

    fc = cfg.get("filter_commune")
    mode = cfg.get("filter_commune_mode") or "input"
    commune_value = commune  # valeur par défaut (mode input)

    annee_value: str | None = None  # bucket année avec hash si dispo

    if fc and commune and mode == "select":
        # mode select : commune + éventuellement année nécessitent des hash
        # → premier appel sans filtres pour récupérer les aggregations
        agg_commune_key = cfg.get("filter_commune_agg") or fc
        agg_annee_key = cfg.get("filter_annee_agg")
        async with httpx.AsyncClient(timeout=15) as client:
            resp0 = await client.get(
                f"{base_url}/_recherche-api/search/{moteur_id}", params=params
            )
            resp0.raise_for_status()
            aggs0 = _get_aggregations(resp0.json())
        bucket = _find_bucket_value(aggs0, agg_commune_key, commune)
        if bucket:
            commune_value = bucket
        if agg_annee_key:
            annee_value = _find_period_bucket(aggs0, agg_annee_key, annee_debut, annee_fin)

    if fc and commune:
        params[f"{moteur_ref}--filtreGroupes[groupes][0][{fc}][q][0]"] = commune_value
        params[f"{moteur_ref}--filtreGroupes[groupes][0][{fc}][op]"] = "AND"
        params[f"{moteur_ref}--filtreGroupes[groupes][0][{fc}][extras][mode]"] = mode

    fa = cfg.get("filter_annee")
    if fa and annee_value:
        # filtre année côté serveur (select mode — valeur avec hash)
        idx = 1 if fc else 0
        params[f"{moteur_ref}--filtreGroupes[groupes][{idx}][{fa}][q][0]"] = annee_value
        params[f"{moteur_ref}--filtreGroupes[groupes][{idx}][{fa}][op]"] = "AND"
        params[f"{moteur_ref}--filtreGroupes[groupes][{idx}][{fa}][extras][mode]"] = "select"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{base_url}/_recherche-api/search/{moteur_id}", params=params
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results", [])

    # Filtrage local par année (si pas de filtre serveur, ou pour affiner)
    if not annee_value:
        results = [
            r for r in results
            if _covers_year_range(r.get("intitule", ""), annee_debut, annee_fin)
        ]
    matching = results

    if not matching:
        return []

    # Pour chaque registre : récupérer idArkoFile via render-fiche
    hits: list[dict] = []
    restitution_ref = cfg.get("restitution_ref")
    if restitution_ref:
        for r in matching:
            id_arko_file, field_ref = await _fetch_id_arko_file(
                base_url, moteur_ref, r["refUnique"], restitution_ref
            )
            hits.append(_parse_hit(r, id_arko_file, field_ref))
    else:
        hits = [_parse_hit(r, None, None) for r in matching]

    return hits


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def get_images_for_hit(base_url: str, hit: dict, max_pages: int = 400) -> list[str]:
    """
    Construit les URLs d'images pour un registre.

    max_pages est un plafond de sécurité. L'agent OCR s'arrête dès qu'il
    trouve l'acte ou lorsqu'une page retourne 404.
    """
    fiche_id = hit.get("fiche_id")
    id_arko_file = hit.get("id_arko_file")
    if not fiche_id or not id_arko_file:
        return []
    return [
        f"{base_url}/_recherche-images/show/{fiche_id}/image/{id_arko_file}/{i}"
        for i in range(max_pages)
    ]


async def get_image_bytes(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


# ---------------------------------------------------------------------------
# Fiche + visionneuse (endpoints secondaires conservés)
# ---------------------------------------------------------------------------
async def get_fiche(base_url: str, moteur_ref: str, fiche_ref: str, restitution_ref: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{base_url}/_recherche-api/render-fiche/{moteur_ref}/{fiche_ref}/{restitution_ref}/detail/html"
        )
        resp.raise_for_status()
        return {"html": resp.text}


async def get_visionneuse_infos(
    base_url: str, moteur_ref: str, fiche_ref: str, field_ref: str, id_arko_file: int
) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{base_url}/_recherche-api/visionneuse-infos/{moteur_ref}/{fiche_ref}/{field_ref}/image/{id_arko_file}"
        )
        resp.raise_for_status()
        return resp.json()
