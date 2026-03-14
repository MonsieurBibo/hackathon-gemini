"""
Tests des endpoints REST + SSE — B7

On mocke build_arbre pour éviter les appels réseau.
"""
from __future__ import annotations

import asyncio
import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from models.arbre import Arbre
from models.events import DoneEvent, IndividualEvent, StepEvent
from models.individu import Individu


# ---------------------------------------------------------------------------
# Fixture : client FastAPI avec build_arbre mocké
# ---------------------------------------------------------------------------

@pytest.fixture
def client(monkeypatch):
    """
    Client HTTP synchrone (TestClient) avec build_arbre patché.
    build_arbre émet quelques événements fictifs puis retourne un Arbre vide.
    """
    from agents.ocr_agent import PersonHint
    from models.individu import Naissance

    async def _fake_build_arbre(
        hint: PersonHint,
        generation_max: int = 3,
        event_cb=None,
    ) -> Arbre:
        arbre = Arbre(generation_max=generation_max)
        individu = Individu(
            nom=hint.nom,
            prenom=hint.prenom or "",
            naissance=Naissance(commune=hint.commune),
            generation=0,
        )
        arbre.root_id = individu.id
        arbre.individus[str(individu.id)] = individu
        arbre.statut = "termine"

        if event_cb:
            event_cb(StepEvent(
                agent_id=uuid4(),
                individu_id=individu.id,
                message="recherche en cours",
            ))
            event_cb(IndividualEvent(individu=individu))
            event_cb(DoneEvent(arbre=arbre))

        return arbre

    monkeypatch.setattr("main.build_arbre", _fake_build_arbre)

    import main
    # Réinitialise le store entre les tests
    main._sessions.clear()

    from fastapi.testclient import TestClient
    with TestClient(main.app) as c:
        yield c


# ---------------------------------------------------------------------------
# Tests /health
# ---------------------------------------------------------------------------

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Tests POST /search
# ---------------------------------------------------------------------------

def test_search_returns_session_id(client):
    resp = client.post("/search", json={
        "nom": "PINÇON",
        "prenom": "Prudence",
        "commune": "Neuilly-en-Sancerre",
        "annee": 1843,
        "generations": 2,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "session_id" in body


def test_search_invalid_annee(client):
    resp = client.post("/search", json={
        "nom": "X", "prenom": "Y", "commune": "Z",
        "annee": 2000,  # > 1900
    })
    assert resp.status_code == 422


def test_search_invalid_generations(client):
    resp = client.post("/search", json={
        "nom": "X", "prenom": "Y", "commune": "Z",
        "annee": 1850,
        "generations": 5,  # > 3
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Tests GET /stream/{session_id}
# ---------------------------------------------------------------------------

def test_stream_unknown_session(client):
    resp = client.get(f"/stream/{uuid4()}")
    assert resp.status_code == 404


def test_stream_receives_events_and_done(client):
    # Démarrer une session
    r = client.post("/search", json={
        "nom": "PINÇON", "prenom": "Prudence",
        "commune": "Neuilly-en-Sancerre", "annee": 1843,
    })
    session_id = r.json()["session_id"]

    # Consommer le stream
    with client.stream("GET", f"/stream/{session_id}") as resp:
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

        events = []
        for line in resp.iter_lines():
            if line.startswith("event:"):
                events.append(line.split(":", 1)[1].strip())

    assert "step" in events
    assert "individual" in events
    assert "done" in events


# ---------------------------------------------------------------------------
# Tests GET /tree/{session_id}
# ---------------------------------------------------------------------------

def test_tree_unknown_session(client):
    resp = client.get(f"/tree/{uuid4()}")
    assert resp.status_code == 404


def test_tree_available_after_stream(client):
    # Lancer et consommer entièrement le stream pour s'assurer que l'arbre est prêt
    r = client.post("/search", json={
        "nom": "PINÇON", "prenom": "Prudence",
        "commune": "Neuilly-en-Sancerre", "annee": 1843,
    })
    session_id = r.json()["session_id"]

    # Vider le stream
    with client.stream("GET", f"/stream/{session_id}") as resp:
        for _ in resp.iter_lines():
            pass

    # L'arbre devrait maintenant être disponible
    resp = client.get(f"/tree/{session_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["statut"] == "termine"
    assert len(body["individus"]) >= 1
