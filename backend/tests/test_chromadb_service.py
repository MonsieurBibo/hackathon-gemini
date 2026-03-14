"""
Tests ChromaDB service — B6

On mocke embed_text_and_image pour éviter les appels API.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from models.individu import Individu, Naissance, Acte


# Vecteur factice de dimension 3072 (dimension réelle de gemini-embedding-2-preview)
FAKE_EMBEDDING = [0.1] * 3072


@pytest.fixture(autouse=True)
def reset_collection():
    """Remet la collection à zéro avant et après chaque test."""
    from services.chromadb_service import reset_collection as do_reset
    do_reset()
    yield
    do_reset()


@pytest.fixture
def mock_embed():
    with patch(
        "services.chromadb_service.embed_text_and_image",
        new_callable=AsyncMock,
        return_value=FAKE_EMBEDDING,
    ) as m:
        yield m


# ---------------------------------------------------------------------------
# Tests store_individu
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_store_individu_retourne_id(mock_embed):
    from services.chromadb_service import store_individu, collection_count
    individu = Individu(nom="PINÇON", prenom="Jean", generation=1,
                        naissance=Naissance(commune="Neuilly-en-Sancerre", dept="18"))
    eid = await store_individu(individu)
    assert eid == str(individu.id)
    assert collection_count() == 1


@pytest.mark.asyncio
async def test_store_individu_upsert_pas_de_doublon(mock_embed):
    from services.chromadb_service import store_individu, collection_count
    individu = Individu(nom="DALLOY", prenom="Jeanne", generation=1,
                        naissance=Naissance(commune="Neuilly-en-Sancerre"))
    await store_individu(individu)
    await store_individu(individu)  # second store du même individu
    assert collection_count() == 1


@pytest.mark.asyncio
async def test_store_individu_avec_transcription(mock_embed):
    from services.chromadb_service import store_individu
    individu = Individu(
        nom="MARTIN", prenom="Pierre", generation=2,
        naissance=Naissance(commune="Bourges", dept="18"),
        actes=[Acte(type="naissance", transcription="L'an mil huit cent... Pierre Martin")],
    )
    eid = await store_individu(individu)
    assert eid == str(individu.id)
    # embed appelé avec un texte incluant la transcription
    call_text = mock_embed.call_args[0][0]
    assert "Martin" in call_text or "MARTIN" in call_text


# ---------------------------------------------------------------------------
# Tests search_similar
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_search_similar_collection_vide(mock_embed):
    from services.chromadb_service import search_similar
    results = await search_similar("laboureur Berry")
    assert results == []


@pytest.mark.asyncio
async def test_search_similar_retourne_resultats(mock_embed):
    from services.chromadb_service import store_individu, search_similar
    i1 = Individu(nom="PINÇON", prenom="Jean", generation=1,
                  naissance=Naissance(commune="Neuilly-en-Sancerre", dept="18"))
    i2 = Individu(nom="DALLOY", prenom="Jeanne", generation=1,
                  naissance=Naissance(commune="Neuilly-en-Sancerre", dept="18"))
    await store_individu(i1)
    await store_individu(i2)

    results = await search_similar("laboureur Berry", n_results=5)
    assert len(results) == 2
    assert "id" in results[0]
    assert "document" in results[0]
    assert "metadata" in results[0]
    assert "distance" in results[0]


@pytest.mark.asyncio
async def test_search_similar_respecte_n_results(mock_embed):
    from services.chromadb_service import store_individu, search_similar
    for i in range(5):
        ind = Individu(nom=f"NOM{i}", generation=i, naissance=Naissance(commune="Paris"))
        await store_individu(ind)

    results = await search_similar("laboureur", n_results=2)
    assert len(results) <= 2
