"""
Agent OCR — B2

Lit les pages d'un registre Arkotheque et extrait les infos d'un acte de naissance
pour une personne donnée.

Pipeline :
  1. fetch image bytes (via arkotheque.get_image_bytes)
  2. appel Gemini Vision avec prompt structuré
  3. parse JSON → OcrResult
  4. find_acte_in_register itère les pages et s'arrête dès qu'on trouve l'acte

Pourquoi parse JSON manuel et non function-calling :
  - google-genai 1.x async ne supporte pas encore response_schema de façon stable
  - Gemini 2.5 Pro suit très bien les instructions JSON explicites
  - On garde le stream_callback pour le SSE frontend

Ref tâche : B2 (docs/tasks/backend.md)
"""
from __future__ import annotations

import json
import re
from typing import Callable, Literal

from pydantic import BaseModel

from services.arkotheque import get_image_bytes
from services.gemini import ocr_image


# ---------------------------------------------------------------------------
# Modèles de données
# ---------------------------------------------------------------------------

class PersonHint(BaseModel):
    """Infos connues sur la personne à chercher dans le registre."""
    nom: str
    prenom: str | None = None
    annee_naissance: int | None = None
    commune: str | None = None


class OcrResult(BaseModel):
    """Résultat de l'extraction OCR sur une page."""
    found: bool
    confiance: float                      # 0.0 – 1.0
    page_index: int | None = None

    # Acte
    transcription: str | None = None      # texte brut de l'acte
    type_acte: Literal["naissance", "mariage", "deces", "autre"] | None = None
    date_acte: str | None = None          # "1843-03-03" ou "1843" si partiel

    # Enfant
    nom_enfant: str | None = None
    prenom_enfant: str | None = None
    sexe: Literal["M", "F"] | None = None
    commune_naissance: str | None = None

    # Père
    nom_pere: str | None = None
    prenom_pere: str | None = None
    commune_pere: str | None = None

    # Mère
    nom_mere: str | None = None
    prenom_mere: str | None = None
    commune_mere: str | None = None


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_USER_PROMPT_TMPL = """\
Tu es un expert en paléographie française spécialisé dans les actes d'état civil
du XIXe siècle. Tu lis des manuscrits anciens en français.

Voici une page d'un registre d'état civil français (XIXe siècle).

Je cherche l'acte de naissance de : {hint_description}

Instructions :
1. Lis attentivement toute la page.
2. Si tu trouves l'acte de naissance correspondant, extrais les informations demandées.
3. Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ni après.
4. Si l'acte n'est pas sur cette page, retourne found=false.
5. Pour les noms, utilise la graphie exacte du document (majuscules comprises).

Format JSON attendu :
{{
  "found": true,
  "confiance": 0.0-1.0,
  "transcription": "texte brut de l'acte trouvé ou null",
  "type_acte": "naissance",
  "date_acte": "YYYY-MM-DD ou YYYY ou null",
  "nom_enfant": "NOM en majuscules ou null",
  "prenom_enfant": "Prénom ou null",
  "sexe": "M" ou "F" ou null,
  "commune_naissance": "commune ou null",
  "nom_pere": "NOM en majuscules ou null",
  "prenom_pere": "Prénom ou null",
  "commune_pere": "commune ou null",
  "nom_mere": "NOM en majuscules ou null",
  "prenom_mere": "Prénom ou null",
  "commune_mere": "commune ou null"
}}

Si l'acte n'est pas trouvé sur cette page :
{{
  "found": false,
  "confiance": 0.0
}}
"""


def _build_prompt(hint: PersonHint) -> str:
    parts = []
    if hint.prenom:
        parts.append(hint.prenom)
    parts.append(hint.nom)
    if hint.annee_naissance:
        parts.append(f"né(e) vers {hint.annee_naissance}")
    if hint.commune:
        parts.append(f"à {hint.commune}")
    return _USER_PROMPT_TMPL.format(hint_description=" ".join(parts))


# ---------------------------------------------------------------------------
# Extraction sur une seule image
# ---------------------------------------------------------------------------

def _parse_json_response(raw: str) -> dict:
    """Extrait le JSON depuis la réponse Gemini (qui peut contenir du markdown)."""
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", raw)
    if match:
        raw = match.group(1)
    return json.loads(raw.strip())


async def extract_from_image(
    image_bytes: bytes,
    hint: PersonHint,
    page_index: int = 0,
    stream_callback: Callable[[str], None] | None = None,
) -> OcrResult:
    """
    Envoie une image à Gemini et retourne un OcrResult structuré.
    stream_callback est appelé avec chaque chunk texte (pour SSE).
    """
    prompt = _build_prompt(hint)
    raw = await ocr_image(image_bytes, prompt, stream_callback=stream_callback)

    try:
        data = _parse_json_response(raw)
    except (json.JSONDecodeError, ValueError):
        # Si Gemini ne renvoie pas du JSON valide, on retourne un résultat vide
        return OcrResult(found=False, confiance=0.0, page_index=page_index)

    # Filtre les clés inconnues pour éviter les erreurs Pydantic
    known = {k: v for k, v in data.items() if k in OcrResult.model_fields}
    return OcrResult(page_index=page_index, **known)


# ---------------------------------------------------------------------------
# Parcours d'un registre page par page
# ---------------------------------------------------------------------------

async def find_acte_in_register(
    image_urls: list[str],
    hint: PersonHint,
    min_confiance: float = 0.7,
    stream_callback: Callable[[str], None] | None = None,
) -> OcrResult | None:
    """
    Parcourt les pages d'un registre dans l'ordre jusqu'à trouver l'acte.

    Retourne le premier OcrResult avec found=True et confiance >= min_confiance,
    ou None si aucune page ne correspond.

    Pourquoi parcours séquentiel et non parallèle :
    - Les pages sont ordonnées chronologiquement → on s'arrête tôt si l'acte est en début
    - Le parallèle coûterait inutilement N appels Gemini au lieu de K (K << N)
    """
    for i, url in enumerate(image_urls):
        img_bytes = await get_image_bytes(url)
        result = await extract_from_image(
            img_bytes,
            hint,
            page_index=i,
            stream_callback=stream_callback,
        )
        if result.found and result.confiance >= min_confiance:
            return result

    return None
