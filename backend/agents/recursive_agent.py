"""
Agent récursif généalogique — B4 (CORE)

Orchestre la boucle complète :
  PersonHint → search_acte → OCR pages → extract parents → recurse

Émission d'événements SSE via un callback synchrone `event_cb(SSEEvent)`.
Ce choix (callback vs async generator) facilite les tests unitaires et
l'intégration avec FastAPI SSE (les events sont mis dans une Queue).

Critère de done : remonte 2 générations depuis Prudence PINÇON (POC Cher)
sans intervention manuelle.

Ref tâche : B4 (docs/tasks/backend.md)
"""
from __future__ import annotations

import uuid
from typing import Callable
from uuid import UUID, uuid4

from agents.ocr_agent import OcrResult, PersonHint, find_acte_in_register
from models.arbre import Arbre
from models.events import (
    DoneEvent,
    ErrorEvent,
    IndividualEvent,
    IndividualUpdateEvent,
    OcrChunkEvent,
    SSEEvent,
    StepEvent,
    ThinkingEvent,
)
from models.individu import Acte, Individu, Naissance
from services.arkotheque import DEPT_CONFIG, get_config, get_images_for_hit, search_acte
from services.geocoding import get_dept_from_commune


# ---------------------------------------------------------------------------
# Conversion OcrResult → Individu
# ---------------------------------------------------------------------------

def _make_individu_from_hint(hint: PersonHint, generation: int) -> Individu:
    return Individu(
        nom=hint.nom,
        prenom=hint.prenom,
        naissance=Naissance(
            commune=hint.commune,
            date=str(hint.annee_naissance) if hint.annee_naissance else None,
            date_approx=True,
        ),
        generation=generation,
        statut="inconnu",
    )


def _update_individu_from_ocr(individu: Individu, result: OcrResult, source: str) -> dict:
    """
    Met à jour un Individu avec les données OCR et retourne le patch (pour SSE).
    Mutation en place — l'Individu est déjà dans l'Arbre.
    """
    patch: dict = {}

    if result.nom_enfant and result.nom_enfant != individu.nom:
        individu.nom = result.nom_enfant
        patch["nom"] = individu.nom

    if result.prenom_enfant and not individu.prenom:
        individu.prenom = result.prenom_enfant
        patch["prenom"] = individu.prenom

    if result.sexe and not individu.sexe:
        individu.sexe = result.sexe
        patch["sexe"] = individu.sexe

    if result.commune_naissance:
        individu.naissance.commune = result.commune_naissance
        patch["naissance.commune"] = result.commune_naissance

    if result.date_acte:
        individu.naissance.date = result.date_acte
        individu.naissance.date_approx = False
        patch["naissance.date"] = result.date_acte

    acte = Acte(
        type="naissance",
        transcription=result.transcription,
        source=source,
        confiance=result.confiance,
    )
    individu.actes.append(acte)
    individu.statut = "complet" if result.confiance >= 0.8 else "partiel"
    patch["statut"] = individu.statut

    return patch


def _make_parent_hint(
    nom: str | None,
    prenom: str | None,
    commune: str | None,
    annee_ref: int | None,
) -> PersonHint | None:
    """
    Crée un PersonHint pour un parent.
    Un parent est né ~25 ans avant l'enfant (approximation).
    Retourne None si le nom est inconnu.
    """
    if not nom:
        return None
    annee_parent = (annee_ref - 25) if annee_ref else None
    return PersonHint(
        nom=nom,
        prenom=prenom,
        commune=commune,
        annee_naissance=annee_parent,
    )


# ---------------------------------------------------------------------------
# Résolution du département
# ---------------------------------------------------------------------------

async def _resolve_dept(commune: str | None, dept_hint: str | None) -> str | None:
    """
    Résout le code département depuis la commune ou un hint existant.
    Retourne None si impossible à résoudre.
    N'essaie la géocodification que si le résultat serait un département
    supporté par Arkotheque (DEPT_CONFIG).
    """
    if dept_hint and dept_hint in DEPT_CONFIG:
        return dept_hint
    if not commune:
        return None
    dept = await get_dept_from_commune(commune)
    if dept and dept in DEPT_CONFIG:
        return dept
    return None


# ---------------------------------------------------------------------------
# Cœur de la récursion
# ---------------------------------------------------------------------------

async def _process_individu(
    individu: Individu,
    arbre: Arbre,
    agent_id: UUID,
    generation: int,
    generation_max: int,
    event_cb: Callable[[SSEEvent], None],
) -> None:
    """
    Cherche l'acte de naissance de l'individu, enrichit l'Arbre, recurse.
    """
    nom_complet = f"{individu.prenom or ''} {individu.nom}".strip()

    # --- Étape 1 : résoudre le département ---
    event_cb(ThinkingEvent(
        event="thinking",
        agent_id=agent_id,
        individu_id=individu.id,
        message=f"Résolution département pour {nom_complet} ({individu.naissance.commune})",
    ))

    dept = await _resolve_dept(individu.naissance.commune, individu.naissance.dept)
    if not dept:
        event_cb(ErrorEvent(
            event="error",
            agent_id=agent_id,
            individu_id=individu.id,
            message=f"Département introuvable pour {nom_complet} — commune : {individu.naissance.commune!r}",
        ))
        individu.statut = "partiel"
        return

    individu.naissance.dept = dept
    cfg = get_config(dept)

    # --- Étape 2 : chercher les registres ---
    annee = None
    if individu.naissance.date:
        try:
            annee = int(individu.naissance.date[:4])
        except ValueError:
            pass

    event_cb(StepEvent(
        event="step",
        agent_id=agent_id,
        individu_id=individu.id,
        message=f"Recherche registres pour {nom_complet} — dept {dept}, {individu.naissance.commune}, ~{annee}",
    ))

    try:
        hits = await search_acte(
            dept=dept,
            commune=individu.naissance.commune or "",
            annee_debut=(annee - 2) if annee else 1800,
            annee_fin=(annee + 2) if annee else 1900,
        )
    except Exception as exc:
        event_cb(ErrorEvent(
            event="error",
            agent_id=agent_id,
            individu_id=individu.id,
            message=f"Erreur Arkotheque pour {nom_complet} : {exc}",
        ))
        individu.statut = "partiel"
        return

    if not hits:
        event_cb(ErrorEvent(
            event="error",
            agent_id=agent_id,
            individu_id=individu.id,
            message=f"Aucun registre trouvé pour {nom_complet} — dept {dept}",
        ))
        individu.statut = "partiel"
        return

    # --- Étape 3 : OCR des registres ---
    hint = PersonHint(
        nom=individu.nom,
        prenom=individu.prenom,
        annee_naissance=annee,
        commune=individu.naissance.commune,
    )

    ocr_result: OcrResult | None = None
    for hit in hits:
        image_urls = get_images_for_hit(cfg["base_url"], hit)
        if not image_urls:
            event_cb(StepEvent(
                event="step",
                agent_id=agent_id,
                individu_id=individu.id,
                message=f"Registre {hit.get('titre', hit.get('fiche_id'))} — métadonnées images absentes, ignoré",
            ))
            continue

        event_cb(StepEvent(
            event="step",
            agent_id=agent_id,
            individu_id=individu.id,
            message=f"OCR registre {hit.get('titre', hit.get('fiche_id'))} ({len(image_urls)} pages)",
        ))

        def _ocr_chunk_cb(chunk: str, _id=individu.id) -> None:
            event_cb(OcrChunkEvent(
                event="ocr_chunk",
                agent_id=agent_id,
                individu_id=_id,
                chunk=chunk,
            ))

        try:
            ocr_result = await find_acte_in_register(
                image_urls=image_urls,
                hint=hint,
                stream_callback=_ocr_chunk_cb,
            )
        except Exception as exc:
            event_cb(ErrorEvent(
                event="error",
                agent_id=agent_id,
                individu_id=individu.id,
                message=f"Erreur OCR pour {nom_complet} : {exc}",
            ))
            continue

        if ocr_result:
            break  # acte trouvé dans ce registre

    if not ocr_result:
        event_cb(ErrorEvent(
            event="error",
            agent_id=agent_id,
            individu_id=individu.id,
            message=f"Acte de naissance introuvable pour {nom_complet}",
        ))
        individu.statut = "partiel"
        return

    # --- Étape 4 : enrichir l'Individu ---
    patch = _update_individu_from_ocr(individu, ocr_result, source=cfg["base_url"])
    event_cb(IndividualUpdateEvent(
        event="individual_update",
        individu_id=individu.id,
        patch=patch,
    ))

    # --- Étape 5 : récursion sur les parents ---
    if generation >= generation_max:
        return

    # Année de naissance de l'enfant pour estimer celle des parents
    annee_enfant = annee
    if ocr_result.date_acte:
        try:
            annee_enfant = int(ocr_result.date_acte[:4])
        except ValueError:
            pass

    for role, nom_p, prenom_p, commune_p in [
        ("père", ocr_result.nom_pere, ocr_result.prenom_pere, ocr_result.commune_pere),
        ("mère", ocr_result.nom_mere, ocr_result.prenom_mere, ocr_result.commune_mere),
    ]:
        parent_hint = _make_parent_hint(nom_p, prenom_p, commune_p or individu.naissance.commune, annee_enfant)
        if not parent_hint:
            continue

        parent = _make_individu_from_hint(parent_hint, generation=generation + 1)
        arbre.individus[str(parent.id)] = parent

        if role == "père":
            individu.pere_id = parent.id
        else:
            individu.mere_id = parent.id

        event_cb(IndividualEvent(event="individual", individu=parent))

        await _process_individu(
            individu=parent,
            arbre=arbre,
            agent_id=agent_id,
            generation=generation + 1,
            generation_max=generation_max,
            event_cb=event_cb,
        )


# ---------------------------------------------------------------------------
# Point d'entrée public
# ---------------------------------------------------------------------------

async def build_arbre(
    hint: PersonHint,
    generation_max: int = 3,
    event_cb: Callable[[SSEEvent], None] | None = None,
) -> Arbre:
    """
    Construit un arbre généalogique récursif depuis une PersonHint racine.

    event_cb est appelé de façon synchrone pour chaque événement SSE.
    Si None, les événements sont ignorés (utile pour les tests).

    Retourne l'Arbre construit (avec les Individus enrichis).
    """
    if event_cb is None:
        event_cb = lambda _: None  # noqa: E731

    agent_id = uuid4()
    arbre = Arbre(generation_max=generation_max)

    root = _make_individu_from_hint(hint, generation=0)
    arbre.root_id = root.id
    arbre.individus[str(root.id)] = root

    event_cb(IndividualEvent(event="individual", individu=root))

    await _process_individu(
        individu=root,
        arbre=arbre,
        agent_id=agent_id,
        generation=0,
        generation_max=generation_max,
        event_cb=event_cb,
    )

    arbre.statut = "termine"
    event_cb(DoneEvent(event="done", arbre=arbre))

    return arbre
