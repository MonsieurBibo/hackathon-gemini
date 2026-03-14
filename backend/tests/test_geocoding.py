import httpx
import respx
from services.geocoding import get_dept_from_commune, get_communes_limitrophes


@respx.mock
async def test_get_dept_from_commune_found():
    respx.get("https://geo.api.gouv.fr/communes").mock(
        return_value=httpx.Response(200, json=[
            {"nom": "Neuilly-en-Sancerre", "departement": {"code": "18", "nom": "Cher"}}
        ])
    )
    result = await get_dept_from_commune("Neuilly-en-Sancerre")
    assert result == "18"


@respx.mock
async def test_get_dept_from_commune_not_found():
    respx.get("https://geo.api.gouv.fr/communes").mock(
        return_value=httpx.Response(200, json=[])
    )
    result = await get_dept_from_commune("VilleInexistante")
    assert result is None


@respx.mock
async def test_get_communes_limitrophes():
    respx.get("https://geo.api.gouv.fr/communes/18160/communes-limitrophes").mock(
        return_value=httpx.Response(200, json=[
            {"nom": "Sancerre"},
            {"nom": "Verdigny"},
        ])
    )
    result = await get_communes_limitrophes("18160")
    assert "Sancerre" in result
    assert "Verdigny" in result
