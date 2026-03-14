from __future__ import annotations
from typing import Literal, Union
from uuid import UUID
from pydantic import BaseModel
from models.individu import Individu
from models.arbre import Arbre


class ThinkingEvent(BaseModel):
    event: Literal["thinking"] = "thinking"
    agent_id: UUID
    individu_id: UUID
    message: str


class StepEvent(BaseModel):
    event: Literal["step"] = "step"
    agent_id: UUID
    individu_id: UUID
    message: str


class OcrChunkEvent(BaseModel):
    event: Literal["ocr_chunk"] = "ocr_chunk"
    agent_id: UUID
    individu_id: UUID
    chunk: str


class IndividualEvent(BaseModel):
    event: Literal["individual"] = "individual"
    individu: Individu


class IndividualUpdateEvent(BaseModel):
    event: Literal["individual_update"] = "individual_update"
    individu_id: UUID
    patch: dict


class FallbackEvent(BaseModel):
    event: Literal["fallback"] = "fallback"
    agent_id: UUID
    individu_id: UUID
    tentative: int
    raison: str
    action: str


class QuestionEvent(BaseModel):
    event: Literal["question"] = "question"
    agent_id: UUID
    individu_id: UUID
    question: str
    options: list[str]


class ErrorEvent(BaseModel):
    event: Literal["error"] = "error"
    agent_id: UUID
    individu_id: UUID
    message: str


class DoneEvent(BaseModel):
    event: Literal["done"] = "done"
    arbre: Arbre


SSEEvent = Union[
    ThinkingEvent, StepEvent, OcrChunkEvent,
    IndividualEvent, IndividualUpdateEvent,
    FallbackEvent, QuestionEvent, ErrorEvent, DoneEvent,
]
