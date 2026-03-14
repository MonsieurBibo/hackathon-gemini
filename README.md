# Lignée — Hackathon Gemini Paris 2026

**Autonomous genealogy agent for French archives.** Enter an ancestor's name → the agent navigates departmental archives (Arkotheque), reads handwritten 19th-century records with Gemini 2.5 Pro, extracts parents, and climbs the family tree generation by generation.

No tool does this today: navigate → OCR raw scans → extract → recurse.

---

## Requirements

- Python 3.11+, `uv`
- Node 18+
- `GEMINI_API_KEY` in `backend/.env`

---

## Run

```bash
# Backend
cd backend
uv sync
cp .env.example .env   # add GEMINI_API_KEY
uv run uvicorn main:app --reload

# Frontend
cd app
npm install
npm run dev            # → http://localhost:5173
```

---

## Demo

1. Enter **Prudence Aimée Pinçon · Neuilly-en-Sancerre · 1843 · 2 generations**
2. Watch agents navigate archives and OCR manuscripts live
3. The family tree builds in real time — click any node to see the original document
4. If an ancestor was born after 1900 (restricted records), the app generates the mairie request letter automatically

**POC validated:** birth record of Prudence Aimée Pinçon found at archives18.fr, father Jean Pinçon extracted, recursive agent tested on 2 generations.

---

## Stack

| Layer | Tech |
|-------|------|
| Agent / OCR | Gemini 2.5 Pro (1M token context) |
| Embeddings | gemini-embedding-2-preview (multimodal) |
| Archives | Arkotheque HTTP API (~80 French departments) |
| Backend | FastAPI + SSE |
| Frontend | React + Vite + react-d3-tree |
| Vector DB | ChromaDB in-memory |
