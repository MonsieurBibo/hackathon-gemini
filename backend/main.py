"""
GenealogyAI — FastAPI entrypoint

Endpoints :
  GET  /health                   → liveness probe
  POST /search                   → démarre l'agent récursif, retourne session_id
  GET  /stream/{session_id}      → SSE stream des événements de l'agent
  GET  /tree/{session_id}        → snapshot JSON de l'arbre (disponible après "done")
  GET  /similar                  → recherche sémantique dans les ancêtres indexés (ChromaDB)
  POST /admin                    → acte post-1900 : administration + courrier pré-rempli
"""
import asyncio
from typing import AsyncGenerator, Union
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agents.admin_agent import AdminResult, LienFamille, TypeActe, handle_post_1900
from agents.ocr_agent import PersonHint
from agents.recursive_agent import build_arbre
from services.chromadb_service import search_similar, store_individu
from config import settings
from models.arbre import Arbre
from models.events import SSEEvent

app = FastAPI(title="GenealogyAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Session store (in-memory, suffisant pour le hackathon)
# ---------------------------------------------------------------------------

_sessions: dict[str, dict] = {}
# Structure : session_id → {"queue": asyncio.Queue, "arbre": Arbre | None, "task": asyncio.Task}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    nom: str
    prenom: str
    commune: str
    annee: int = Field(ge=1600, le=1900)
    generations: int = Field(default=3, ge=1, le=3)


class SearchResponse(BaseModel):
    session_id: UUID


class AnswerRequest(BaseModel):
    agent_id: UUID
    individu_id: UUID
    choix: Union[int, str]           # 0 | 1 | "texte libre"


class AnswerResponse(BaseModel):
    ok: bool


class AdminRequest(BaseModel):
    type_acte: TypeActe
    nom: str
    prenom: str | None = None
    commune: str | None = None
    annee: int = Field(ge=1901, le=2026)
    lien: LienFamille
    pays_naissance: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    """
    Démarre l'agent récursif en tâche background.
    Retourne immédiatement un session_id pour suivre l'avancement via /stream.
    """
    session_id = uuid4()
    queue: asyncio.Queue[SSEEvent | None] = asyncio.Queue()

    def event_cb(evt: SSEEvent) -> None:
        # Appelé de façon synchrone depuis l'agent (dans le même event loop).
        queue.put_nowait(evt)

    async def _run() -> None:
        try:
            arbre = await build_arbre(
                hint=PersonHint(
                    nom=req.nom,
                    prenom=req.prenom,
                    commune=req.commune,
                    annee_naissance=req.annee,
                ),
                generation_max=req.generations,
                event_cb=event_cb,
            )
            _sessions[str(session_id)]["arbre"] = arbre
        except Exception:
            # build_arbre émet DoneEvent avant de retourner normalement ;
            # en cas d'exception inattendue on envoie un sentinel pour débloquer le stream.
            queue.put_nowait(None)
        finally:
            # Sentinel de sécurité : débloque le stream si DoneEvent n'a pas été émis.
            queue.put_nowait(None)

    task = asyncio.create_task(_run())
    _sessions[str(session_id)] = {"queue": queue, "arbre": None, "task": task}

    return SearchResponse(session_id=session_id)


@app.get("/stream/{session_id}")
async def stream_events(session_id: UUID):
    """
    SSE stream des événements de l'agent.

    Format SSE : chaque message est `event: <type>\\ndata: <json>\\n\\n`.
    Le stream se termine sur l'événement "done" (ou un sentinel interne).
    """
    key = str(session_id)
    if key not in _sessions:
        raise HTTPException(status_code=404, detail="Session inconnue")

    queue: asyncio.Queue = _sessions[key]["queue"]

    async def _generate() -> AsyncGenerator[str, None]:
        while True:
            evt = await queue.get()
            if evt is None:
                # Sentinel interne (erreur inattendue sans DoneEvent)
                yield "event: done\ndata: {}\n\n"
                break
            data = evt.model_dump_json()
            event_name = evt.event
            yield f"event: {event_name}\ndata: {data}\n\n"
            if event_name == "done":
                break

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # désactive le buffering nginx
        },
    )


@app.get("/tree/{session_id}")
async def get_tree(session_id: UUID):
    """
    Retourne l'arbre complet en JSON une fois l'agent terminé.
    Retourne 202 si la construction est encore en cours.
    """
    key = str(session_id)
    if key not in _sessions:
        raise HTTPException(status_code=404, detail="Session inconnue")

    arbre: Arbre | None = _sessions[key]["arbre"]
    if arbre is None:
        raise HTTPException(status_code=202, detail="Arbre en cours de construction")

    return arbre.model_dump()


@app.get("/similar")
async def similar(q: str = Query(..., min_length=2), n: int = Query(default=5, ge=1, le=20)):
    """
    Recherche sémantique dans les ancêtres indexés via ChromaDB.
    Exemple : /similar?q=laboureur+Berry
    Retourne les n individus les plus proches sémantiquement.
    """
    results = await search_similar(q, n_results=n)
    return {"query": q, "results": results}


@app.post("/admin", response_model=AdminResult)
async def admin_post_1900(req: AdminRequest):
    """
    Pour un ancêtre dont l'acte est postérieur à 1900 (non disponible sur Arkotheque) :
    détermine l'administration compétente et génère un courrier de demande pré-rempli.
    """
    return await handle_post_1900(
        type_acte=req.type_acte,
        nom=req.nom,
        prenom=req.prenom,
        commune=req.commune,
        annee=req.annee,
        lien=req.lien,
        pays_naissance=req.pays_naissance,
    )
