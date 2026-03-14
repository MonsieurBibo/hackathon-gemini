from __future__ import annotations
from typing import Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from models.individu import Individu


class Arbre(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    root_id: UUID | None = None
    individus: dict[str, Individu] = {}   # UUID str → Individu
    generation_max: int = 3
    generation_courante: int = 0
    statut: Literal["en_cours", "termine", "erreur"] = "en_cours"
