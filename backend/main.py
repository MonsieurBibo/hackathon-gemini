from typing import Union
from uuid import UUID
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, conint
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

app = FastAPI(title="GenealogyAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request / Response models ---

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


# --- Endpoints ---

@app.get("/health")
async def health():
    return {"status": "ok"}
