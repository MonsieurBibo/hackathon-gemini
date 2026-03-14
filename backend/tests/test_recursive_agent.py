"""
Tests unitaires — Agent récursif (B4)

On mocke search_acte, get_images_for_hit, find_acte_in_register, get_dept_from_commune.
Pas d'appels réseau.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.ocr_agent import OcrResult, PersonHint
from agents.recursive_agent import (
    _make_individu_from_hint,
    _make_parent_hint,
    _update_individu_from_ocr,
    build_arbre,
)
from models.events import (
    DoneEvent,
    ErrorEvent,
    IndividualEvent,
    IndividualUpdateEvent,
    StepEvent,
    ThinkingEvent,
)
from models.individu import Individu, Naissance


# ---------------------------------------------------------------------------
# Helpers purs
# ---------------------------------------------------------------------------

def test_make_individu_from_hint_full():
    hint = PersonHint(nom="PINÇON", prenom="Prudence Aimée", annee_naissance=1843, commune="Neuilly-en-Sancerre")
    ind = _make_individu_from_hint(hint, generation=0)
    assert ind.nom == "PINÇON"
    assert ind.prenom == "Prudence Aimée"
    assert ind.naissance.commune == "Neuilly-en-Sancerre"
    assert ind.naissance.date == "1843"
    assert ind.naissance.date_approx is True
    assert ind.generation == 0
    assert ind.statut == "inconnu"


def test_make_individu_from_hint_no_annee():
    hint = PersonHint(nom="DUPONT")
    ind = _make_individu_from_hint(hint, generation=2)
    assert ind.naissance.date is None
    assert ind.generation == 2


def test_make_parent_hint_with_all_info():
    hint = _make_parent_hint("PINÇON", "Jean", "Neuilly-en-Sancerre", 1843)
    assert hint is not None
    assert hint.nom == "PINÇON"
    assert hint.prenom == "Jean"
    assert hint.annee_naissance == 1818  # 1843 - 25


def test_make_parent_hint_no_nom_returns_none():
    assert _make_parent_hint(None, "Jean", "Paris", 1843) is None
    assert _make_parent_hint("", "Jean", "Paris", 1843) is None


def test_make_parent_hint_no_annee():
    hint = _make_parent_hint("DUPONT", "Marie", None, None)
    assert hint.annee_naissance is None


def test_update_individu_from_ocr_full():
    individu = Individu(nom="PINCON", generation=0)
    result = OcrResult(
        found=True,
        confiance=0.92,
        nom_enfant="PINÇON",
        prenom_enfant="Prudence Aimée",
        sexe="F",
        commune_naissance="Neuilly-en-Sancerre",
        date_acte="1843-03-03",
        nom_pere="PINÇON",
        prenom_pere="Jean",
        nom_mere="DALLOY",
        prenom_mere="Jeanne Aimée",
        transcription="Le trois mars mil huit cent quarante trois...",
    )
    patch = _update_individu_from_ocr(individu, result, source="archives18.fr")

    assert individu.nom == "PINÇON"
    assert individu.prenom == "Prudence Aimée"
    assert individu.sexe == "F"
    assert individu.naissance.date == "1843-03-03"
    assert individu.naissance.date_approx is False
    assert individu.statut == "complet"
    assert len(individu.actes) == 1
    assert individu.actes[0].type == "naissance"
    assert "statut" in patch


def test_update_individu_does_not_overwrite_existing_prenom():
    individu = Individu(nom="PINÇON", prenom="Déjà connu")
    result = OcrResult(found=True, confiance=0.9, prenom_enfant="Autre")
    _update_individu_from_ocr(individu, result, source="test")
    assert individu.prenom == "Déjà connu"  # pas écrasé


def test_update_individu_low_confidence_gives_partiel():
    individu = Individu(nom="DUPONT")
    result = OcrResult(found=True, confiance=0.5)
    _update_individu_from_ocr(individu, result, source="test")
    assert individu.statut == "partiel"


# ---------------------------------------------------------------------------
# build_arbre — tests d'intégration avec mocks
# ---------------------------------------------------------------------------

PRUNED_OCR_RESULT = OcrResult(
    found=True,
    confiance=0.92,
    nom_enfant="PINÇON",
    prenom_enfant="Prudence Aimée",
    sexe="F",
    date_acte="1843-03-03",
    commune_naissance="Neuilly-en-Sancerre",
    nom_pere="PINÇON",
    prenom_pere="Jean",
    commune_pere="Neuilly-en-Sancerre",
    nom_mere="DALLOY",
    prenom_mere="Jeanne Aimée",
)

FAKE_HIT = {
    "fiche_id": "4082",
    "titre": "Naissances 1843-1852",
    "commune": "Neuilly-en-Sancerre",
    "raw": {"idArkoFile": 1997, "nbrPages": 10},
}


@pytest.mark.asyncio
async def test_build_arbre_root_only_no_dept():
    """Si le département est introuvable, l'arbre contient juste la racine avec statut partiel."""
    hint = PersonHint(nom="PINÇON", prenom="Prudence Aimée", annee_naissance=1843, commune="Inconnu-ville")
    events = []

    with patch("agents.recursive_agent.get_dept_from_commune", new=AsyncMock(return_value=None)):
        arbre = await build_arbre(hint, generation_max=2, event_cb=events.append)

    assert arbre.root_id is not None
    root = arbre.individus[str(arbre.root_id)]
    assert root.statut == "partiel"
    assert arbre.statut == "termine"

    event_types = [e.event for e in events]
    assert "individual" in event_types
    assert "error" in event_types
    assert "done" in event_types


@pytest.mark.asyncio
async def test_build_arbre_gen0_found_parents_not_recursed():
    """Génération max = 0 : on cherche l'acte de la racine mais on ne recurse pas."""
    hint = PersonHint(nom="PINÇON", prenom="Prudence Aimée", annee_naissance=1843, commune="Neuilly-en-Sancerre")
    events = []

    with patch("agents.recursive_agent.get_dept_from_commune", new=AsyncMock(return_value="18")), \
         patch("agents.recursive_agent.search_acte", new=AsyncMock(return_value=[FAKE_HIT])), \
         patch("agents.recursive_agent.get_images_for_hit", return_value=["url0", "url1"]), \
         patch("agents.recursive_agent.find_acte_in_register", new=AsyncMock(return_value=PRUNED_OCR_RESULT)):
        arbre = await build_arbre(hint, generation_max=0, event_cb=events.append)

    root = arbre.individus[str(arbre.root_id)]
    assert root.statut == "complet"
    # Pas de parents créés car generation_max=0
    assert root.pere_id is None
    assert root.mere_id is None
    assert len(arbre.individus) == 1


@pytest.mark.asyncio
async def test_build_arbre_gen1_creates_parents():
    """Génération max = 1 : parents créés mais pas leurs propres parents."""
    hint = PersonHint(nom="PINÇON", prenom="Prudence Aimée", annee_naissance=1843, commune="Neuilly-en-Sancerre")
    events = []

    # Parents aussi sans acte trouvé (dept inconnu)
    with patch("agents.recursive_agent.get_dept_from_commune", new=AsyncMock(side_effect=["18", None, None])), \
         patch("agents.recursive_agent.search_acte", new=AsyncMock(return_value=[FAKE_HIT])), \
         patch("agents.recursive_agent.get_images_for_hit", return_value=["url0"]), \
         patch("agents.recursive_agent.find_acte_in_register", new=AsyncMock(return_value=PRUNED_OCR_RESULT)):
        arbre = await build_arbre(hint, generation_max=1, event_cb=events.append)

    # Racine + père + mère = 3 individus
    assert len(arbre.individus) == 3

    root = arbre.individus[str(arbre.root_id)]
    assert root.pere_id is not None
    assert root.mere_id is not None

    pere = arbre.individus[str(root.pere_id)]
    assert pere.nom == "PINÇON"
    assert pere.prenom == "Jean"
    assert pere.generation == 1

    mere = arbre.individus[str(root.mere_id)]
    assert mere.nom == "DALLOY"
    assert mere.generation == 1


@pytest.mark.asyncio
async def test_build_arbre_emits_correct_event_sequence():
    """Vérifie la séquence d'événements SSE."""
    hint = PersonHint(nom="PINÇON", annee_naissance=1843, commune="Neuilly")
    events = []

    with patch("agents.recursive_agent.get_dept_from_commune", new=AsyncMock(return_value="18")), \
         patch("agents.recursive_agent.search_acte", new=AsyncMock(return_value=[FAKE_HIT])), \
         patch("agents.recursive_agent.get_images_for_hit", return_value=["url0"]), \
         patch("agents.recursive_agent.find_acte_in_register", new=AsyncMock(return_value=PRUNED_OCR_RESULT)):
        await build_arbre(hint, generation_max=0, event_cb=events.append)

    types = [e.event for e in events]
    # IndividualEvent en premier, DoneEvent en dernier
    assert types[0] == "individual"
    assert types[-1] == "done"
    assert "individual_update" in types
    assert "step" in types


@pytest.mark.asyncio
async def test_build_arbre_no_hits():
    """Aucun registre trouvé → statut partiel, pas de crash."""
    hint = PersonHint(nom="INCONNU", commune="Inconnue")
    events = []

    with patch("agents.recursive_agent.get_dept_from_commune", new=AsyncMock(return_value="18")), \
         patch("agents.recursive_agent.search_acte", new=AsyncMock(return_value=[])):
        arbre = await build_arbre(hint, generation_max=2, event_cb=events.append)

    root = arbre.individus[str(arbre.root_id)]
    assert root.statut == "partiel"
    error_events = [e for e in events if e.event == "error"]
    assert len(error_events) >= 1


@pytest.mark.asyncio
async def test_build_arbre_no_images_in_hit():
    """Registre sans métadonnées image → ignoré, statut partiel."""
    hint = PersonHint(nom="DUPONT", commune="Paris")
    events = []

    with patch("agents.recursive_agent.get_dept_from_commune", new=AsyncMock(return_value="18")), \
         patch("agents.recursive_agent.search_acte", new=AsyncMock(return_value=[FAKE_HIT])), \
         patch("agents.recursive_agent.get_images_for_hit", return_value=[]):
        arbre = await build_arbre(hint, generation_max=2, event_cb=events.append)

    root = arbre.individus[str(arbre.root_id)]
    assert root.statut == "partiel"


@pytest.mark.asyncio
async def test_build_arbre_ocr_not_found():
    """OCR parcourt toutes les pages sans trouver → statut partiel."""
    hint = PersonHint(nom="DUPONT", annee_naissance=1850, commune="Bourges")
    events = []

    with patch("agents.recursive_agent.get_dept_from_commune", new=AsyncMock(return_value="18")), \
         patch("agents.recursive_agent.search_acte", new=AsyncMock(return_value=[FAKE_HIT])), \
         patch("agents.recursive_agent.get_images_for_hit", return_value=["url0"]), \
         patch("agents.recursive_agent.find_acte_in_register", new=AsyncMock(return_value=None)):
        arbre = await build_arbre(hint, generation_max=2, event_cb=events.append)

    root = arbre.individus[str(arbre.root_id)]
    assert root.statut == "partiel"
    error_events = [e for e in events if e.event == "error"]
    assert any("introuvable" in e.message for e in error_events)


@pytest.mark.asyncio
async def test_build_arbre_returns_arbre_with_session_id():
    """L'Arbre a toujours un session_id et un root_id."""
    hint = PersonHint(nom="TEST")
    with patch("agents.recursive_agent.get_dept_from_commune", new=AsyncMock(return_value=None)):
        arbre = await build_arbre(hint)

    assert arbre.session_id is not None
    assert arbre.root_id is not None
