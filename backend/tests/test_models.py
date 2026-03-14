import pytest
from uuid import UUID
from pydantic import ValidationError
from models.individu import Individu, Acte, Naissance, Media
from models.arbre import Arbre



# ---------------------------------------------------------------------------
# Individu
# ---------------------------------------------------------------------------

def test_individu_minimal():
    ind = Individu(nom="Pinçon")
    assert isinstance(ind.id, UUID)
    assert ind.statut == "inconnu"
    assert ind.generation == 0
    assert ind.actes == []


def test_individu_full():
    ind = Individu(
        nom="Pinçon",
        prenom="Prudence Aimée",
        sexe="F",
        naissance=Naissance(date="1843-03-03", commune="Neuilly-en-Sancerre", dept="18"),
        generation=0,
        statut="complet",
    )
    assert ind.naissance.dept == "18"
    assert ind.sexe == "F"


def test_individu_invalid_sexe():
    with pytest.raises(ValidationError):
        Individu(nom="Test", sexe="X")


def test_individu_invalid_statut():
    with pytest.raises(ValidationError):
        Individu(nom="Test", statut="inconnu_statut")


# ---------------------------------------------------------------------------
# Acte
# ---------------------------------------------------------------------------

def test_acte_confiance_bounds():
    a = Acte(type="naissance", confiance=0.92)
    assert a.confiance == 0.92


def test_acte_confiance_out_of_bounds():
    with pytest.raises(ValidationError):
        Acte(type="naissance", confiance=1.5)


def test_acte_invalid_type():
    with pytest.raises(ValidationError):
        Acte(type="bapteme")


# ---------------------------------------------------------------------------
# Arbre
# ---------------------------------------------------------------------------

def test_arbre_defaults():
    arbre = Arbre()
    assert arbre.statut == "en_cours"
    assert arbre.generation_max == 3
    assert arbre.individus == {}


def test_arbre_add_individu():
    ind = Individu(nom="Pinçon", prenom="Jean")
    arbre = Arbre(root_id=ind.id)
    arbre.individus[str(ind.id)] = ind
    assert str(ind.id) in arbre.individus


def test_arbre_invalid_statut():
    with pytest.raises(ValidationError):
        Arbre(statut="pause")


# ---------------------------------------------------------------------------
# SearchRequest (depuis main.py)
# ---------------------------------------------------------------------------

def test_search_request_valid():
    from main import SearchRequest
    req = SearchRequest(nom="Pinçon", prenom="Prudence", commune="Neuilly-en-Sancerre", annee=1843)
    assert req.generations == 3  # défaut


def test_search_request_annee_too_recent():
    from main import SearchRequest
    with pytest.raises(ValidationError):
        SearchRequest(nom="Test", prenom="Test", commune="Paris", annee=1950)


def test_search_request_generations_max():
    from main import SearchRequest
    with pytest.raises(ValidationError):
        SearchRequest(nom="Test", prenom="Test", commune="Paris", annee=1800, generations=5)
