"""
Tests unitaires — Agent OCR (B2)

On mocke get_image_bytes et ocr_image pour rester hors-réseau.
"""
import json
from unittest.mock import AsyncMock, patch

import pytest

from agents.ocr_agent import (
    OcrResult,
    PersonHint,
    _build_prompt,
    _parse_json_response,
    extract_from_image,
    find_acte_in_register,
)


# ---------------------------------------------------------------------------
# _build_prompt
# ---------------------------------------------------------------------------

def test_build_prompt_full():
    hint = PersonHint(nom="PINÇON", prenom="Prudence Aimée", annee_naissance=1843, commune="Neuilly-en-Sancerre")
    prompt = _build_prompt(hint)
    assert "PINÇON" in prompt
    assert "Prudence Aimée" in prompt
    assert "1843" in prompt
    assert "Neuilly-en-Sancerre" in prompt


def test_build_prompt_nom_only():
    hint = PersonHint(nom="DUPONT")
    prompt = _build_prompt(hint)
    assert "DUPONT" in prompt


def test_build_prompt_prenom_before_nom():
    hint = PersonHint(nom="DUPONT", prenom="Marie")
    prompt = _build_prompt(hint)
    idx_prenom = prompt.index("Marie")
    idx_nom = prompt.index("DUPONT")
    assert idx_prenom < idx_nom


# ---------------------------------------------------------------------------
# _parse_json_response
# ---------------------------------------------------------------------------

def test_parse_json_plain():
    raw = '{"found": false, "confiance": 0.0}'
    data = _parse_json_response(raw)
    assert data["found"] is False


def test_parse_json_markdown_block():
    raw = '```json\n{"found": true, "confiance": 0.9}\n```'
    data = _parse_json_response(raw)
    assert data["found"] is True
    assert data["confiance"] == 0.9


def test_parse_json_markdown_no_lang():
    raw = '```\n{"found": false, "confiance": 0.1}\n```'
    data = _parse_json_response(raw)
    assert data["found"] is False


def test_parse_json_invalid_raises():
    with pytest.raises((json.JSONDecodeError, ValueError)):
        _parse_json_response("ceci n'est pas du JSON")


# ---------------------------------------------------------------------------
# extract_from_image
# ---------------------------------------------------------------------------

FOUND_RESPONSE = json.dumps({
    "found": True,
    "confiance": 0.92,
    "transcription": "Le trois mars mil huit cent quarante trois...",
    "type_acte": "naissance",
    "date_acte": "1843-03-03",
    "nom_enfant": "PINÇON",
    "prenom_enfant": "Prudence Aimée",
    "sexe": "F",
    "commune_naissance": "Neuilly-en-Sancerre",
    "nom_pere": "PINÇON",
    "prenom_pere": "Jean",
    "commune_pere": "Neuilly-en-Sancerre",
    "nom_mere": "DALLOY",
    "prenom_mere": "Jeanne Aimée",
    "commune_mere": None,
})

NOT_FOUND_RESPONSE = json.dumps({"found": False, "confiance": 0.0})


@pytest.mark.asyncio
async def test_extract_from_image_found():
    hint = PersonHint(nom="PINÇON", prenom="Prudence Aimée", annee_naissance=1843)
    with patch("agents.ocr_agent.ocr_image", new=AsyncMock(return_value=FOUND_RESPONSE)):
        result = await extract_from_image(b"fake_bytes", hint, page_index=2)

    assert result.found is True
    assert result.confiance == 0.92
    assert result.page_index == 2
    assert result.nom_pere == "PINÇON"
    assert result.prenom_mere == "Jeanne Aimée"
    assert result.nom_mere == "DALLOY"
    assert result.sexe == "F"


@pytest.mark.asyncio
async def test_extract_from_image_not_found():
    hint = PersonHint(nom="PINÇON")
    with patch("agents.ocr_agent.ocr_image", new=AsyncMock(return_value=NOT_FOUND_RESPONSE)):
        result = await extract_from_image(b"fake_bytes", hint, page_index=0)

    assert result.found is False
    assert result.confiance == 0.0


@pytest.mark.asyncio
async def test_extract_from_image_invalid_json_returns_empty():
    hint = PersonHint(nom="PINÇON")
    with patch("agents.ocr_agent.ocr_image", new=AsyncMock(return_value="Désolé, je ne peux pas lire cette image.")):
        result = await extract_from_image(b"fake_bytes", hint)

    assert result.found is False
    assert result.confiance == 0.0


@pytest.mark.asyncio
async def test_extract_calls_stream_callback():
    chunks = []
    hint = PersonHint(nom="DUPONT")

    async def fake_ocr(image_bytes, prompt, stream_callback=None):
        if stream_callback:
            stream_callback("chunk1")
            stream_callback("chunk2")
        return NOT_FOUND_RESPONSE

    with patch("agents.ocr_agent.ocr_image", new=fake_ocr):
        await extract_from_image(b"fake", hint, stream_callback=chunks.append)

    assert chunks == ["chunk1", "chunk2"]


# ---------------------------------------------------------------------------
# find_acte_in_register
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_find_acte_stops_at_first_match():
    hint = PersonHint(nom="PINÇON")
    call_count = 0

    async def fake_get_image_bytes(url):
        nonlocal call_count
        call_count += 1
        return b"fake"

    # page 0 : not found, page 1 : found, page 2 : ne doit pas être appelée
    responses = [NOT_FOUND_RESPONSE, FOUND_RESPONSE, NOT_FOUND_RESPONSE]

    async def fake_ocr(image_bytes, prompt, stream_callback=None):
        return responses[call_count - 1]

    with patch("agents.ocr_agent.get_image_bytes", new=fake_get_image_bytes), \
         patch("agents.ocr_agent.ocr_image", new=fake_ocr):
        result = await find_acte_in_register(
            ["url0", "url1", "url2"], hint, min_confiance=0.7
        )

    assert result is not None
    assert result.found is True
    assert result.page_index == 1
    assert call_count == 2  # s'est arrêté après la page 1


@pytest.mark.asyncio
async def test_find_acte_returns_none_when_not_found():
    hint = PersonHint(nom="INCONNU")

    async def fake_get_image_bytes(url):
        return b"fake"

    with patch("agents.ocr_agent.get_image_bytes", new=fake_get_image_bytes), \
         patch("agents.ocr_agent.ocr_image", new=AsyncMock(return_value=NOT_FOUND_RESPONSE)):
        result = await find_acte_in_register(["url0", "url1"], hint)

    assert result is None


@pytest.mark.asyncio
async def test_find_acte_respects_min_confiance():
    """Un résultat found=True mais confiance trop basse doit être ignoré."""
    hint = PersonHint(nom="DUPONT")
    low_conf = json.dumps({"found": True, "confiance": 0.4})

    async def fake_get_image_bytes(url):
        return b"fake"

    with patch("agents.ocr_agent.get_image_bytes", new=fake_get_image_bytes), \
         patch("agents.ocr_agent.ocr_image", new=AsyncMock(return_value=low_conf)):
        result = await find_acte_in_register(["url0"], hint, min_confiance=0.7)

    assert result is None


@pytest.mark.asyncio
async def test_find_acte_empty_register():
    hint = PersonHint(nom="DUPONT")
    result = await find_acte_in_register([], hint)
    assert result is None
