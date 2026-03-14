"""
Client Arkotheque — version ancienne (routing.json présent).
Couvre : Cher (18), Ardennes (08), Indre (36), Meurthe-et-Moselle (54).
"""
from __future__ import annotations
import httpx

# ---------------------------------------------------------------------------
# Config par département : base_url + IDs moteur état civil
# ---------------------------------------------------------------------------
DEPT_CONFIG: dict[str, dict] = {
    "18": {
        "base_url": "https://www.archives18.fr",
        "moteur_id": 1,
        "moteur_ref": "arko_default_61011a8e5db65",
        "filter_commune": "arko_default_61011b4c3eacb",
        "filter_annee": "arko_default_61011b4c62fc5",
    },
    "08": {
        "base_url": "https://archives.cd08.fr",
        "moteur_id": 6,
        "moteur_ref": "arko_default_6776ac3012e9d",
        "filter_commune": "arko_default_6776acf636161",
        "filter_annee": "arko_default_6776acf64bf69",
    },
    "36": {
        "base_url": "https://www.archives36.fr",
        "moteur_id": 8,
        "moteur_ref": "arko_default_61a0ae5412613",
        "filter_commune": None,
        "filter_annee": None,
    },
    "54": {
        "base_url": "https://archivesenligne.meurthe-et-moselle.fr",
        "moteur_id": 1,
        "moteur_ref": "arko_default_62bc69358b041",
        "filter_commune": None,
        "filter_annee": None,
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
# Recherche des registres (moteur browse)
# ---------------------------------------------------------------------------
def _build_filter_params(
    moteur_ref: str,
    filters: list[tuple[str, str]],  # [(filter_ref, value), ...]
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
        params[f"{prefix}[extras][mode]"] = "select"
    return params


async def _get_aggregations(base_url: str, moteur_id: int) -> dict:
    """Récupère les valeurs de filtres disponibles via les aggregations."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{base_url}/_recherche-api/search/{moteur_id}")
        resp.raise_for_status()
        return resp.json().get("aggregations", {})


def _find_bucket_value(aggregations: dict, field_ref: str, term: str) -> str | None:
    """Trouve la valeur exacte (avec hash) d'un terme dans les aggregations."""
    bucket_key = f"{field_ref}_terms"
    for agg in aggregations.values():
        if bucket_key in agg:
            for bucket in agg[bucket_key].get("buckets", []):
                key: str = bucket.get("key", "")
                if term.lower() in key.lower():
                    return key
    return None


async def search_acte(
    dept: str,
    commune: str,
    annee_debut: int,
    annee_fin: int,
) -> list[dict]:
    """
    Cherche les registres d'état civil pour une commune et une période.
    Retourne une liste de fiches (registres).
    """
    cfg = get_config(dept)
    base_url = cfg["base_url"]
    moteur_id = cfg["moteur_id"]
    moteur_ref = cfg["moteur_ref"]

    filters: list[tuple[str, str]] = []

    # Commune
    if cfg["filter_commune"]:
        aggs = await _get_aggregations(base_url, moteur_id)
        commune_value = _find_bucket_value(aggs, cfg["filter_commune"], commune)
        if commune_value:
            filters.append((cfg["filter_commune"], commune_value))

        # Période : cherche le bucket qui contient l'année cible
        if cfg["filter_annee"]:
            period_value = _find_period_bucket(aggs, cfg["filter_annee"], annee_debut, annee_fin)
            if period_value:
                filters.append((cfg["filter_annee"], period_value))

    params = _build_filter_params(moteur_ref, filters)

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{base_url}/_recherche-api/search/{moteur_id}",
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    hits = data.get("hits", {}).get("hits", [])
    return [_parse_hit(h) for h in hits]


def _find_period_bucket(
    aggregations: dict, filter_ref: str, annee_debut: int, annee_fin: int
) -> str | None:
    """Trouve le bucket de période qui couvre l'intervalle cible."""
    bucket_key = f"{filter_ref}_terms"
    best: str | None = None
    for agg in aggregations.values():
        if bucket_key in agg:
            for bucket in agg[bucket_key].get("buckets", []):
                key: str = bucket.get("key", "")
                # Format : "1813-1822[[hash]]"
                part = key.split("[[")[0]
                if "-" in part:
                    try:
                        start, end = (int(x) for x in part.split("-"))
                        if start <= annee_fin and end >= annee_debut:
                            best = key
                    except ValueError:
                        continue
    return best


def _parse_hit(hit: dict) -> dict:
    src = hit.get("_source", {})
    return {
        "fiche_id": hit.get("_id"),
        "titre": src.get("titre") or src.get("label") or "",
        "commune": src.get("commune") or "",
        "annee_debut": src.get("anneeDebut") or src.get("date_debut"),
        "annee_fin": src.get("anneeFin") or src.get("date_fin"),
        "cote": src.get("cote") or "",
        "raw": src,
    }


# ---------------------------------------------------------------------------
# Fiche + images
# ---------------------------------------------------------------------------
async def get_fiche(base_url: str, moteur_ref: str, fiche_ref: str, restitution_ref: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{base_url}/_recherche-api/render-fiche/{moteur_ref}/{fiche_ref}/{restitution_ref}/detail/html"
        )
        resp.raise_for_status()
        return resp.json()


async def get_image_urls(
    base_url: str,
    moteur_ref: str,
    fiche_ref: str,
    field_ref: str,
    id_arko_file: int,
    nb_pages: int,
) -> list[str]:
    """Construit les URLs d'images pour toutes les pages d'un registre."""
    return [
        f"{base_url}/_recherche-images/show/{fiche_ref}/image/{id_arko_file}/{i}"
        for i in range(nb_pages)
    ]


async def get_visionneuse_infos(
    base_url: str, moteur_ref: str, fiche_ref: str, field_ref: str, id_arko_file: int
) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{base_url}/_recherche-api/visionneuse-infos/{moteur_ref}/{fiche_ref}/{field_ref}/image/{id_arko_file}"
        )
        resp.raise_for_status()
        return resp.json()


async def get_image_bytes(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content
