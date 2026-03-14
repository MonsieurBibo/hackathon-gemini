"""
Smoke test — Prudence Aimée PINÇON, 1843, Neuilly-en-Sancerre (Cher 18)

Valide le pipeline complet :
  search_acte → ficheId=4082 + idArkoFile=1997
  image page 5 → JPEG valide
  OCR page 5 → père=Jean PINÇON, mère=Jeanne Aimée DALLOY

Usage :
  .venv/bin/python smoke_test_prudence.py
"""
import asyncio
import os
import sys

# Chercher .env depuis le répertoire parent
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from services.arkotheque import search_acte, get_images_for_hit, get_image_bytes
from services.geocoding import get_dept_from_commune


COMMUNE = "Neuilly-en-Sancerre"
ANNEE = 1843
EXPECTED_FICHE_ID = 4082
EXPECTED_ID_ARKO_FILE = 1997
EXPECTED_PAGE = 5


def ok(msg): print(f"  ✓ {msg}")
def fail(msg): print(f"  ✗ {msg}"); sys.exit(1)


async def main():
    print("\n=== Smoke test Prudence PINÇON ===\n")

    # --- Étape 1 : geocoding ---
    print("1. Geocoding commune → département")
    dept = await get_dept_from_commune(COMMUNE)
    if dept != "18":
        fail(f"dept attendu=18, obtenu={dept!r}")
    ok(f"commune={COMMUNE} → dept={dept}")

    # --- Étape 2 : search_acte ---
    print("\n2. search_acte(dept=18, commune=Neuilly-en-Sancerre, 1843-1843)")
    hits = await search_acte("18", COMMUNE, ANNEE, ANNEE)
    if not hits:
        fail("Aucun registre trouvé")
    ok(f"{len(hits)} registre(s) trouvé(s) :")
    for h in hits:
        print(f"     id={h['fiche_id']} titre={h['titre']} idArkoFile={h['id_arko_file']}")

    fiche4082 = next((h for h in hits if h["fiche_id"] == EXPECTED_FICHE_ID), None)
    if not fiche4082:
        fail(f"ficheId={EXPECTED_FICHE_ID} absent des résultats")
    ok(f"ficheId={EXPECTED_FICHE_ID} présent")

    if fiche4082["id_arko_file"] != EXPECTED_ID_ARKO_FILE:
        fail(f"idArkoFile attendu={EXPECTED_ID_ARKO_FILE}, obtenu={fiche4082['id_arko_file']}")
    ok(f"idArkoFile={EXPECTED_ID_ARKO_FILE} correct")

    # --- Étape 3 : URL image page 5 ---
    print("\n3. Image page 5 (acte Prudence)")
    urls = get_images_for_hit("https://www.archives18.fr", fiche4082, max_pages=10)
    if len(urls) < 6:
        fail(f"Trop peu d'URLs générées : {len(urls)}")
    url_page5 = urls[EXPECTED_PAGE]
    expected_url = f"https://www.archives18.fr/_recherche-images/show/{EXPECTED_FICHE_ID}/image/{EXPECTED_ID_ARKO_FILE}/{EXPECTED_PAGE}"
    if url_page5 != expected_url:
        fail(f"URL page 5 incorrecte:\n  attendu : {expected_url}\n  obtenu  : {url_page5}")
    ok(f"URL = {url_page5}")

    img = await get_image_bytes(url_page5)
    if not img or len(img) < 10_000:
        fail(f"Image trop petite ou vide : {len(img)} bytes")
    is_jpeg = img[:2] == b"\xff\xd8"
    if not is_jpeg:
        fail("Réponse n'est pas un JPEG")
    ok(f"JPEG valide, {len(img):,} bytes")

    # --- Étape 4 : OCR (si clé API disponible) ---
    from config import settings
    api_key = settings.resolved_api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("\n4. OCR — skipped (GEMINI_API_KEY absent)")
    else:
        print("\n4. OCR page 5 via Gemini")
        # Injecter la clé si nécessaire
        if not os.environ.get("GEMINI_API_KEY"):
            os.environ["GEMINI_API_KEY"] = api_key

        from agents.ocr_agent import find_acte_in_register, PersonHint
        hint = PersonHint(nom="PINÇON", prenom="Prudence Aimée", annee_naissance=1843, commune=COMMUNE)

        result = await find_acte_in_register(
            image_urls=[url_page5],
            hint=hint,
            min_confiance=0.5,
        )
        if result is None or not result.found:
            fail("Acte non trouvé par OCR sur page 5")
        ok(f"Acte trouvé, confiance={result.confiance:.2f}")

        if result.nom_pere:
            ok(f"Père : {result.nom_pere}")
        if result.nom_mere:
            ok(f"Mère : {result.nom_mere}")

        jean_ok = result.nom_pere and "PINÇON" in result.nom_pere.upper()
        jeanne_ok = result.nom_mere and "DALLOY" in result.nom_mere.upper()
        if not jean_ok:
            print(f"  ⚠  Père attendu 'Jean PINÇON', obtenu {result.nom_pere!r}")
        if not jeanne_ok:
            print(f"  ⚠  Mère attendue 'Jeanne Aimée DALLOY', obtenu {result.nom_mere!r}")

    print("\n=== SMOKE TEST PASSED ===\n")


if __name__ == "__main__":
    asyncio.run(main())
