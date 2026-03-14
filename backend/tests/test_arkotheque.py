import pytest
import httpx
import respx
from services.arkotheque import (
    _build_filter_params,
    _find_period_bucket,
    _find_bucket_value,
    _parse_hit,
    _covers_year_range,
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


def test_build_filter_params_mode_input():
    params = _build_filter_params("ref", [("fc", "Neuilly")], mode="input")
    assert params["ref--filtreGroupes[groupes][0][fc][extras][mode]"] == "input"


def test_build_filter_params_multiple():
    params = _build_filter_params("ref", [("f1", "v1"), ("f2", "v2")])
    assert "ref--filtreGroupes[groupes][0][f1][q][0]" in params
    assert "ref--filtreGroupes[groupes][1][f2][q][0]" in params


def test_build_filter_params_empty():
    params = _build_filter_params("ref", [])
    assert params["ref--filtreGroupes[operator]"] == "AND"
    assert len(params) == 2


# ---------------------------------------------------------------------------
# _covers_year_range
# ---------------------------------------------------------------------------

def test_covers_year_range_period():
    assert _covers_year_range("3E 2346 1843 - 1852", 1843, 1843) is True
    assert _covers_year_range("3E 2346 1843 - 1852", 1850, 1850) is True
    assert _covers_year_range("3E 2346 1843 - 1852", 1853, 1853) is False
    assert _covers_year_range("3E 2346 1843 - 1852", 1840, 1842) is False


def test_covers_year_range_overlap():
    assert _covers_year_range("3E 2474 1813 - 1852", 1843, 1843) is True


def test_covers_year_range_single_year():
    assert _covers_year_range("Classe 1890", 1890, 1890) is True
    assert _covers_year_range("Classe 1890", 1891, 1895) is False


def test_covers_year_range_no_year():
    assert _covers_year_range("Registre sans date", 1843, 1843) is False


# ---------------------------------------------------------------------------
# _find_period_bucket (format réel : aggregations = liste)
# ---------------------------------------------------------------------------

FAKE_AGGS_LIST = [
    {
        "filter_annee": {
            "filter_annee_terms": {
                "buckets": [
                    {"key": "1813-1822[[hash1]]"},
                    {"key": "1823-1832[[hash2]]"},
                    {"key": "1843-1852[[hash3]]"},
                ]
            }
        }
    }
]


def test_find_period_bucket_exact_match():
    result = _find_period_bucket(FAKE_AGGS_LIST, "filter_annee", 1843, 1843)
    assert result == "1843-1852[[hash3]]"


def test_find_period_bucket_overlap():
    result = _find_period_bucket(FAKE_AGGS_LIST, "filter_annee", 1820, 1825)
    assert result is not None


def test_find_period_bucket_no_match():
    result = _find_period_bucket(FAKE_AGGS_LIST, "filter_annee", 1900, 1910)
    assert result is None


def test_find_period_bucket_wrong_field():
    result = _find_period_bucket(FAKE_AGGS_LIST, "autre_filtre", 1843, 1843)
    assert result is None


# ---------------------------------------------------------------------------
# _find_bucket_value
# ---------------------------------------------------------------------------

FAKE_AGGS_COMMUNE = [
    {
        "arko_default_commune": {
            "arko_default_commune_terms": {
                "buckets": [
                    {"key": "Paris[[arko_fiche_aaa]]"},
                    {"key": "Neuilly-en-Sancerre[[arko_fiche_bbb]]"},
                ]
            }
        }
    }
]


def test_find_bucket_value_found():
    result = _find_bucket_value(FAKE_AGGS_COMMUNE, "arko_default_commune", "neuilly")
    assert result == "Neuilly-en-Sancerre[[arko_fiche_bbb]]"


def test_find_bucket_value_not_found():
    result = _find_bucket_value(FAKE_AGGS_COMMUNE, "arko_default_commune", "lyon")
    assert result is None


def test_find_bucket_value_wrong_field():
    result = _find_bucket_value(FAKE_AGGS_COMMUNE, "autre_champ", "Paris")
    assert result is None


# ---------------------------------------------------------------------------
# _parse_hit
# ---------------------------------------------------------------------------

def test_parse_hit_full():
    raw = {"id": 4082, "intitule": "3E 2346 1843 - 1852", "refUnique": "arko_fiche_abc"}
    hit = _parse_hit(raw, id_arko_file=1997, field_ref="arko_default_field")
    assert hit["fiche_id"] == 4082
    assert hit["titre"] == "3E 2346 1843 - 1852"
    assert hit["refUnique"] == "arko_fiche_abc"
    assert hit["id_arko_file"] == 1997
    assert hit["raw"] == raw


def test_parse_hit_no_image_info():
    raw = {"id": 99, "intitule": "test", "refUnique": "arko_fiche_x"}
    hit = _parse_hit(raw, None, None)
    assert hit["id_arko_file"] is None


# ---------------------------------------------------------------------------
# get_config
# ---------------------------------------------------------------------------

def test_get_config_known_dept():
    cfg = get_config("18")
    assert cfg["base_url"] == "https://www.archives18.fr"
    assert cfg["moteur_id"] == 1
    assert cfg["contenu_id"] == "2655739"
    assert cfg["restitution_ref"] == "arko_default_61011eb03aad2"


def test_get_config_unknown_dept():
    with pytest.raises(ValueError, match="non supporté"):
        get_config("99")


def test_all_depts_have_required_keys():
    required = ["base_url", "moteur_id", "moteur_ref", "contenu_id",
                "restitution_ref", "filter_commune", "filter_commune_mode"]
    for dept, cfg in DEPT_CONFIG.items():
        for key in required:
            assert key in cfg, f"dept {dept} missing {key}"


# ---------------------------------------------------------------------------
# detect_version
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
# get_image_bytes
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
# search_acte (HTTP mock — Cher dept 18, format réel)
# ---------------------------------------------------------------------------

RENDER_FICHE_HTML_VALID = (
    'data-visionneuse="'
    '{&quot;refUniqueFiche&quot;:&quot;arko_fiche_60febc1aa5228&quot;,'
    '&quot;refUniqueField&quot;:&quot;arko_default_field&quot;,'
    '&quot;idArkoFile&quot;:1997,'
    '&quot;mediaType&quot;:&quot;image&quot;}"'
)

FAKE_SEARCH_RESPONSE = {
    "total": 34,
    "results": [
        {
            "id": 4082,
            "intitule": "3E 2346 1843 - 1852",
            "refUnique": "arko_fiche_60febc1aa5228",
            "hasChildren": False,
        },
        {
            "id": 4084,
            "intitule": "3E 2474 1813 - 1852",
            "refUnique": "arko_fiche_other",
            "hasChildren": False,
        },
        {
            "id": 4076,
            "intitule": "3E 20914 1853 - 1862",  # hors période
            "refUnique": "arko_fiche_out",
            "hasChildren": False,
        },
    ],
    "aggregations": [],
}


@respx.mock
async def test_search_acte_cher_returns_matching():
    base = "https://www.archives18.fr"
    respx.get(f"{base}/_recherche-api/search/1").mock(
        return_value=httpx.Response(200, json=FAKE_SEARCH_RESPONSE)
    )
    respx.get(
        f"{base}/_recherche-api/render-fiche/arko_default_61011a8e5db65"
        "/arko_fiche_60febc1aa5228/arko_default_61011eb03aad2/detail/html"
    ).mock(return_value=httpx.Response(200, text=RENDER_FICHE_HTML_VALID))
    respx.get(
        f"{base}/_recherche-api/render-fiche/arko_default_61011a8e5db65"
        "/arko_fiche_other/arko_default_61011eb03aad2/detail/html"
    ).mock(return_value=httpx.Response(200, text=RENDER_FICHE_HTML_VALID))

    results = await search_acte("18", "Neuilly-en-Sancerre", 1843, 1843)

    assert len(results) == 2
    fiche_ids = [r["fiche_id"] for r in results]
    assert 4082 in fiche_ids
    assert 4084 in fiche_ids
    assert 4076 not in fiche_ids


@respx.mock
async def test_search_acte_no_results():
    base = "https://www.archives18.fr"
    respx.get(f"{base}/_recherche-api/search/1").mock(
        return_value=httpx.Response(200, json={"total": 0, "results": [], "aggregations": []})
    )
    results = await search_acte("18", "VilleInconnue", 1843, 1843)
    assert results == []
