"""
Service ChromaDB — B6

Stocke les individus comme vecteurs pour permettre une recherche sémantique.
Collection in-memory (suffisant pour le hackathon — pas de persistence).

Modèle d'embedding : gemini-embedding-2-preview (3072 dims, multimodal).

Pourquoi chromadb in-memory et pas une BDD externe ?
→ Zéro infra, portable, suffisant pour ~1000 individus en démo.

Ref tâche : B6 (docs/tasks/backend.md)
"""
from __future__ import annotations

import chromadb

from models.individu import Individu
from services.gemini import embed_text_and_image

_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None

COLLECTION_NAME = "ancetres"


def _get_collection() -> chromadb.Collection:
    global _client, _collection
    if _collection is None:
        # EphemeralClient crée un client vraiment isolé (pas de singleton global).
        # Nécessaire pour que les tests puissent resetter l'état entre eux.
        _client = chromadb.EphemeralClient()
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def _individu_to_text(individu: Individu) -> str:
    """
    Sérialise un Individu en texte pour l'embedding.
    On inclut le nom, la commune, l'année, la génération, et les transcriptions.
    """
    parts = [
        f"{individu.prenom or ''} {individu.nom}".strip(),
        f"génération {individu.generation}",
    ]
    if individu.naissance.commune:
        parts.append(f"né(e) à {individu.naissance.commune}")
    if individu.naissance.date:
        parts.append(f"le {individu.naissance.date}")
    if individu.naissance.dept:
        parts.append(f"département {individu.naissance.dept}")
    for acte in individu.actes:
        if acte.transcription:
            parts.append(acte.transcription[:500])  # tronquer pour éviter token overflow

    return " — ".join(parts)


async def store_individu(individu: Individu, image_bytes: bytes | None = None) -> str:
    """
    Embed l'individu et le stocke dans ChromaDB.
    Retourne l'embedding_id (= str(individu.id)).
    Si l'individu est déjà présent (même id), le remplace.
    """
    collection = _get_collection()
    text = _individu_to_text(individu)
    embedding = await embed_text_and_image(text, image_bytes)

    embedding_id = str(individu.id)
    metadata = {
        "nom": individu.nom,
        "prenom": individu.prenom or "",
        "generation": individu.generation,
        "commune": individu.naissance.commune or "",
        "dept": individu.naissance.dept or "",
        "statut": individu.statut,
    }

    # upsert manuel : delete si présent puis add — chromadb EphemeralClient v1.5
    # ne garantit pas la déduplication via upsert dans tous les cas.
    existing = collection.get(ids=[embedding_id])
    if existing["ids"]:
        collection.delete(ids=[embedding_id])
    collection.add(
        ids=[embedding_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata],
    )
    return embedding_id


async def search_similar(query: str, n_results: int = 5) -> list[dict]:
    """
    Recherche sémantique texte libre.
    Retourne une liste de dicts avec les métadonnées + distance cosine.

    Exemple : "laboureur Berry" → ancêtres paysans du Cher/Indre.
    """
    collection = _get_collection()
    if collection.count() == 0:
        return []

    query_embedding = await embed_text_and_image(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for i, doc in enumerate(results["documents"][0]):
        output.append({
            "id": results["ids"][0][i],
            "document": doc,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return output


def collection_count() -> int:
    """Retourne le nombre d'individus indexés."""
    return _get_collection().count()


def reset_collection() -> None:
    """
    Vide la collection (utile pour les tests).
    EphemeralClient étant un singleton en chromadb v1.5, on ne peut pas détruire
    le client — on supprime tous les documents existants à la place.
    """
    global _collection
    if _collection is not None:
        ids = _collection.get()["ids"]
        if ids:
            _collection.delete(ids=ids)
    # Ne pas mettre _collection à None : on réutilise la même instance vide.
