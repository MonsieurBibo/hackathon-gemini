"""
Tests agent post-1900 — B8

Le routing déterministe est testé sans mock.
La génération du courrier (Gemini) est mockée.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from agents.admin_agent import (
    _est_acces_libre,
    _est_ayant_droit,
    _choisir_administration,
    handle_post_1900,
)


# ---------------------------------------------------------------------------
# Tests _est_acces_libre
# ---------------------------------------------------------------------------

def test_naissance_avant_75_ans_pas_libre():
    assert _est_acces_libre("naissance", 1960) is False  # 2026 - 1960 = 66 ans

def test_naissance_apres_75_ans_libre():
    assert _est_acces_libre("naissance", 1940) is True   # 2026 - 1940 = 86 ans

def test_mariage_limite_exacte():
    assert _est_acces_libre("mariage", 1951) is False    # 75 ans = non libre
    assert _est_acces_libre("mariage", 1950) is True     # 76 ans = libre

def test_deces_apres_25_ans_libre():
    assert _est_acces_libre("deces", 2000) is True       # 26 ans

def test_deces_avant_25_ans_pas_libre():
    assert _est_acces_libre("deces", 2005) is False      # 21 ans

def test_matricule_classe_1921_libre():
    assert _est_acces_libre("matricule", 1921) is True

def test_matricule_classe_1922_pas_libre():
    assert _est_acces_libre("matricule", 1922) is False


# ---------------------------------------------------------------------------
# Tests _est_ayant_droit
# ---------------------------------------------------------------------------

def test_moi_meme_est_ayant_droit():
    assert _est_ayant_droit("moi-même") is True

def test_parent_est_ayant_droit():
    assert _est_ayant_droit("parent") is True

def test_autre_pas_ayant_droit():
    assert _est_ayant_droit("autre") is False


# ---------------------------------------------------------------------------
# Tests _choisir_administration
# ---------------------------------------------------------------------------

def test_administration_naissance_libre():
    admin, justifs, delai = _choisir_administration("naissance", 1930, "Bourges")
    assert "Mairie de Bourges" in admin.nom
    assert len(justifs) == 1  # juste identité facultative
    assert "semaine" in delai

def test_administration_naissance_non_libre():
    admin, justifs, delai = _choisir_administration("naissance", 1970, "Bourges")
    assert "Mairie de Bourges" in admin.nom
    assert any("parenté" in j.lower() for j in justifs)

def test_administration_matricule_ligne():
    admin, justifs, delai = _choisir_administration("matricule", 1910, "Cher")
    assert "Mémoire" in admin.notes or "archives" in admin.nom.lower()
    assert "Immédiat" in delai

def test_administration_matricule_shd():
    admin, justifs, delai = _choisir_administration("matricule", 1935, None)
    assert "SHD" in admin.nom or "Défense" in admin.nom

def test_administration_ne_a_etranger():
    admin, justifs, delai = _choisir_administration("naissance", 1930, None, pays_naissance="Maroc")
    assert "SCEC" in admin.nom or "Nantes" in admin.nom
    assert admin.email is not None

def test_administration_deces_libre():
    admin, justifs, delai = _choisir_administration("deces", 1990, "Lyon")
    assert "Mairie de Lyon" in admin.nom


# ---------------------------------------------------------------------------
# Tests handle_post_1900 (intégration avec Gemini mocké)
# ---------------------------------------------------------------------------

FAKE_COURRIER = "[PRÉNOM NOM]\n[ADRESSE]\n\nObjet : demande d'acte\n\nMadame, Monsieur..."


@pytest.fixture
def mock_gemini():
    with patch(
        "agents.admin_agent.answer_admin_question",
        new_callable=AsyncMock,
        return_value=FAKE_COURRIER,
    ) as m:
        yield m


@pytest.mark.asyncio
async def test_handle_post_1900_acte_libre(mock_gemini):
    result = await handle_post_1900(
        type_acte="naissance",
        nom="MARTIN",
        prenom="Pierre",
        commune="Bourges",
        annee=1930,
        lien="grand-parent",
    )
    assert result.acces_libre is True
    assert result.accessible is True
    assert result.courrier == FAKE_COURRIER
    assert "Mairie" in result.administration.nom


@pytest.mark.asyncio
async def test_handle_post_1900_acte_non_libre_ayant_droit(mock_gemini):
    result = await handle_post_1900(
        type_acte="naissance",
        nom="DUPONT",
        prenom="Marie",
        commune="Paris",
        annee=1970,
        lien="parent",
    )
    assert result.acces_libre is False
    assert result.accessible is True   # ayant droit → accès quand même
    assert any("parenté" in j.lower() for j in result.justificatifs)


@pytest.mark.asyncio
async def test_handle_post_1900_acte_non_libre_non_ayant_droit(mock_gemini):
    result = await handle_post_1900(
        type_acte="naissance",
        nom="DURAND",
        prenom="Louis",
        commune="Lyon",
        annee=1990,
        lien="autre",
    )
    assert result.acces_libre is False
    assert result.accessible is False  # pas ayant droit → pas accessible


@pytest.mark.asyncio
async def test_handle_post_1900_matricule_en_ligne(mock_gemini):
    result = await handle_post_1900(
        type_acte="matricule",
        nom="BERNARD",
        prenom="Henri",
        commune="Cher",
        annee=1910,
        lien="arriere-grand-parent",
    )
    assert result.acces_libre is True
    assert "Immédiat" in result.delai_reponse


@pytest.mark.asyncio
async def test_handle_post_1900_ne_etranger(mock_gemini):
    result = await handle_post_1900(
        type_acte="naissance",
        nom="BENALI",
        prenom="Ahmed",
        commune=None,
        annee=1950,
        lien="parent",
        pays_naissance="Algérie",
    )
    assert "SCEC" in result.administration.nom or "Nantes" in result.administration.nom


@pytest.mark.asyncio
async def test_handle_post_1900_courrier_appelle_gemini(mock_gemini):
    await handle_post_1900(
        type_acte="deces",
        nom="PETIT",
        prenom="Suzanne",
        commune="Bordeaux",
        annee=1998,
        lien="moi-même",
    )
    mock_gemini.assert_called_once()
