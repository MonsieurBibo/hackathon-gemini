import pytest
import httpx
import respx
from services.arkotheque import (
    _build_filter_params,
    _find_period_bucket,
    _find_bucket_value,
    _parse_hit,
    detect_version,
    search_acte,
    get_image_bytes,
    DEPT_CONFIG,
    get_config,
)

# ---------------------------------------------------------------------------
# _build_filter_params
# ---------------------------------------------------------------------------

def test_build_filter_params_single():
    params = _build_filter_params("moteur_ref", [("filter_commune", "Paris[[hash]]")])
    assert params["moteur_ref--filtreGroupes[operator]"] == "AND"
    assert params["moteur_ref--filtreGroupes[mode]"] == "simple"
    assert params["moteur_ref--filtreGroupes[groupes][0][filter_commune][q][0]"] == "Paris[[hash]]"
    assert params["moteur_ref--filtreGroupes[groupes][0][filter_commune][op]"] == "AND"
    assert params["moteur_ref--filtreGroupes[groupes][0][filter_commune][extras][mode]"] == "select"


def test_build_filter_params_multiple():
    params = _build_filter_params("ref", [("f1", "v1"), ("f2", "v2")])
    assert "ref--filtreGroupes[groupes][0][f1][q][0]" in params
    assert "ref--filtreGroupes[groupes][1][f2][q][0]" in params


def test_build_filter_params_empty():
    params = _build_filter_params("ref", [])
    assert params["ref--filtreGroupes[operator]"] == "AND"
    assert len(params) == 2  # seulement operator + mode


# ---------------------------------------------------------------------------
# _find_period_bucket
# ---------------------------------------------------------------------------

FAKE_AGGS = {
    "agg1": {
        "filter_annee_terms": {
            "buckets": [
                {"key": "1813-1822[[hash1]]"},
                {"key": "1823-1832[[hash2]]"},
                {"key": "1843-1852[[hash3]]"},
            ]
        }
    }
}


def test_find_period_bucket_exact_match():
    result = _find_period_bucket(FAKE_AGGS, "filter_annee", 1843, 1843)
    assert result == "1843-1852[[hash3]]"


def test_find_period_bucket_overlap():
    result = _find_period_bucket(FAKE_AGGS, "filter_annee", 1820, 1825)
    # 1813-1822 et 1823-1832 couvrent tous les deux → retourne le dernier trouvé
    assert result is not None


def test_find_period_bucket_no_match():
    result = _find_period_bucket(FAKE_AGGS, "filter_annee", 1900, 1910)
    assert result is None


def test_find_period_bucket_wrong_field():
    result = _find_period_bucket(FAKE_AGGS, "autre_filtre", 1843, 1843)
    assert result is None


# ---------------------------------------------------------------------------
# _find_bucket_value
# ---------------------------------------------------------------------------

FAKE_AGGS_COMMUNE = {
    "agg_commune": {
        "filter_commune_terms": {
            "buckets": [
                {"key": "Neuilly-en-Sancerre[[arko_fiche_abc]]"},
                {"key": "Bourges[[arko_fiche_def]]"},
            ]
        }
    }
}


def test_find_bucket_value_found():
    result = _find_bucket_value(FAKE_AGGS_COMMUNE, "filter_commune", "Neuilly")
    assert result == "Neuilly-en-Sancerre[[arko_fiche_abc]]"


def test_find_bucket_value_case_insensitive():
    result = _find_bucket_value(FAKE_AGGS_COMMUNE, "filter_commune", "neuilly")
    assert result == "Neuilly-en-Sancerre[[arko_fiche_abc]]"


def test_find_bucket_value_not_found():
    result = _find_bucket_value(FAKE_AGGS_COMMUNE, "filter_commune", "Lyon")
    assert result is None


# ---------------------------------------------------------------------------
# _parse_hit
# ---------------------------------------------------------------------------

def test_parse_hit_full():
    hit = {
        "_id": "4082",
        "_source": {
            "titre": "Naissances 1843-1852",
            "commune": "Neuilly-en-Sancerre",
            "anneeDebut": 1843,
            "anneeFin": 1852,
            "cote": "3E 2346",
        },
    }
    parsed = _parse_hit(hit)
    assert parsed["fiche_id"] == "4082"
    assert parsed["commune"] == "Neuilly-en-Sancerre"
    assert parsed["annee_debut"] == 1843
    assert parsed["cote"] == "3E 2346"


def test_parse_hit_minimal():
    parsed = _parse_hit({"_id": "1", "_source": {}})
    assert parsed["fiche_id"] == "1"
    assert parsed["titre"] == ""
    assert parsed["commune"] == ""


# ---------------------------------------------------------------------------
# get_config
# ---------------------------------------------------------------------------

def test_get_config_known_dept():
    cfg = get_config("18")
    assert cfg["base_url"] == "https://www.archives18.fr"
    assert cfg["moteur_id"] == 1


def test_get_config_unknown_dept():
    with pytest.raises(ValueError, match="non supporté"):
        get_config("99")


def test_all_depts_have_required_keys():
    for dept, cfg in DEPT_CONFIG.items():
        assert "base_url" in cfg, f"dept {dept} missing base_url"
        assert "moteur_id" in cfg, f"dept {dept} missing moteur_id"
        assert "moteur_ref" in cfg, f"dept {dept} missing moteur_ref"


# ---------------------------------------------------------------------------
# detect_version (HTTP mock)
# ---------------------------------------------------------------------------

@respx.mock
async def test_detect_version_old():
    respx.get("https://www.archives18.fr/js/routing.json").mock(
        return_value=httpx.Response(200, json={})
    )
    result = await detect_version("https://www.archives18.fr")
    assert result == "old"


@respx.mock
async def test_detect_version_new():
    respx.get("https://archives39.fr/js/routing.json").mock(
        return_value=httpx.Response(404)
    )
    result = await detect_version("https://archives39.fr")
    assert result == "new"


# ---------------------------------------------------------------------------
# get_image_bytes (HTTP mock)
# ---------------------------------------------------------------------------

@respx.mock
async def test_get_image_bytes_ok():
    url = "https://www.archives18.fr/_recherche-images/show/4082/image/1997/5"
    respx.get(url).mock(return_value=httpx.Response(200, content=b"JPEG_BYTES"))
    data = await get_image_bytes(url)
    assert data == b"JPEG_BYTES"


@respx.mock
async def test_get_image_bytes_error():
    url = "https://www.archives18.fr/_recherche-images/show/9999/image/0/0"
    respx.get(url).mock(return_value=httpx.Response(404))
    with pytest.raises(httpx.HTTPStatusError):
        await get_image_bytes(url)


# ---------------------------------------------------------------------------
# search_acte (HTTP mock — Cher dept 18)
# ---------------------------------------------------------------------------

FAKE_SEARCH_RESPONSE = {
    "aggregations": {
        "agg_commune": {
            "arko_default_61011b4c3eacb_terms": {
                "buckets": [{"key": "Neuilly-en-Sancerre[[arko_fiche_xyz]]"}]
            }
        },
        "agg_annee": {
            "arko_default_61011b4c62fc5_terms": {
                "buckets": [{"key": "1843-1852[[hash_abc]]"}]
            }
        },
    },
    "hits": {
        "hits": [
            {
                "_id": "4082",
                "_source": {
                    "titre": "Naissances 1843-1852",
                    "commune": "Neuilly-en-Sancerre",
                    "anneeDebut": 1843,
                    "anneeFin": 1852,
                    "cote": "3E 2346",
                },
            }
        ]
    },
}


@respx.mock
async def test_search_acte_cher():
    base = "https://www.archives18.fr"
    # Premier appel (aggregations sans filtre) + deuxième appel (avec filtres)
    respx.get(f"{base}/_recherche-api/search/1").mock(
        return_value=httpx.Response(200, json=FAKE_SEARCH_RESPONSE)
    )
    results = await search_acte("18", "Neuilly-en-Sancerre", 1843, 1843)
    assert len(results) == 1
    assert results[0]["fiche_id"] == "4082"
    assert results[0]["commune"] == "Neuilly-en-Sancerre"


@respx.mock
async def test_search_acte_commune_not_in_aggs():
    base = "https://www.archives18.fr"
    # Aggregations vides → pas de filtre commune, recherche quand même
    respx.get(f"{base}/_recherche-api/search/1").mock(
        return_value=httpx.Response(200, json={"aggregations": {}, "hits": {"hits": []}})
    )
    results = await search_acte("18", "InconnuVille", 1800, 1810)
    assert results == []
