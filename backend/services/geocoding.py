"""
Geocoding INSEE — détection du département depuis le nom de commune.

API : https://geo.api.gouv.fr (gratuite, pas d'auth)
Utilisé par : B1 (search_acte), B5 (communes limitrophes pour fallback)
Ref tâche : B1 + B5 (docs/tasks/backend.md)
"""
import httpx

GEO_API = "https://geo.api.gouv.fr/communes"


async def get_dept_from_commune(commune: str) -> str | None:
    """Retourne le code département INSEE depuis le nom de commune."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            GEO_API,
            params={"nom": commune, "fields": "departement", "limit": 1},
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            return data[0].get("departement", {}).get("code")
    return None


async def get_communes_limitrophes(code_insee: str) -> list[str]:
    """Retourne les noms des communes limitrophes."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{GEO_API}/{code_insee}/communes-limitrophes")
        resp.raise_for_status()
        return [c["nom"] for c in resp.json()]
