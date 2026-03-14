from __future__ import annotations
from typing import Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Naissance(BaseModel):
    date: str | None = None          # ISO 8601 ou None si inconnu
    date_approx: bool = False
    commune: str | None = None
    dept: str | None = None          # code INSEE (ex: "18")


class Deces(BaseModel):
    date: str | None = None
    commune: str | None = None
    dept: str | None = None


class Acte(BaseModel):
    type: Literal["naissance", "mariage", "deces", "matricule", "recensement"]
    url_image: str | None = None
    transcription: str | None = None
    source: str | None = None        # ex: "archives18.fr"
    fiche_id: int | None = None
    confiance: float | None = Field(default=None, ge=0.0, le=1.0)


class Media(BaseModel):
    type: Literal["photo_tombe", "portrait", "medaille", "note"]
    url: str | None = None
    contenu: str | None = None       # texte si type=note
    source: Literal["user", "wikimedia", "geneanet"]


class Individu(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    nom: str
    prenom: str | None = None
    sexe: Literal["M", "F"] | None = None
    naissance: Naissance = Field(default_factory=Naissance)
    deces: Deces = Field(default_factory=Deces)
    pere_id: UUID | None = None
    mere_id: UUID | None = None
    generation: int = 0
    actes: list[Acte] = []
    media: list[Media] = []
    embedding_id: str | None = None
    statut: Literal["complet", "partiel", "inconnu"] = "inconnu"
