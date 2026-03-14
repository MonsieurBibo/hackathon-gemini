"""
Service Gemini — wrapper autour de google-genai 1.x.

Modèles utilisés :
- OCR / vision      : gemini-3-flash-preview
- Raisonnement      : gemini-3.1-pro-preview (désambiguïsation, contexte 1M)
- Embeddings        : gemini-embedding-2-preview (multimodal texte+image, 3072 dims)

Ref tâche : B3 (docs/tasks/backend.md)
Ref modèles : docs/project/models.md
"""
from google import genai
from google.genai import types
from config import settings

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.resolved_api_key)
    return _client


async def ocr_image(
    image_bytes: bytes,
    prompt: str,
    stream_callback: callable = None,
) -> str:
    client = get_client()
    contents = [
        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        prompt,
    ]
    if stream_callback:
        full = []
        stream = await client.aio.models.generate_content_stream(
            model="gemini-3-flash-preview", contents=contents
        )
        async for chunk in stream:
            if chunk.text:
                stream_callback(chunk.text)
                full.append(chunk.text)
        return "".join(full)
    else:
        response = await client.aio.models.generate_content(
            model="gemini-3-flash-preview", contents=contents
        )
        return response.text


async def embed_text_and_image(
    text: str, image_bytes: bytes = None
) -> list[float]:
    client = get_client()
    if image_bytes:
        contents = types.Content(parts=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=text),
        ])
    else:
        contents = text
    response = await client.aio.models.embed_content(
        model="gemini-embedding-2-preview",
        contents=contents,
    )
    return response.embeddings[0].values


async def answer_admin_question(context: str, question: str) -> str:
    client = get_client()
    prompt = f"Contexte :\n{context}\n\nQuestion : {question}"
    response = await client.aio.models.generate_content(
        model="gemini-3.1-pro-preview", contents=prompt
    )
    return response.text
