# Product Requirements Document — Local Wikipedia RAG Assistant

## 1. Overview
Build a ChatGPT-style assistant that answers natural-language questions about 20 famous
people and 20 famous places, using only Wikipedia as its knowledge source and running
entirely on the user's laptop.

## 2. Goals
- Demonstrate a complete RAG pipeline: ingest → chunk → embed → store → retrieve → generate.
- Run 100% locally (no external LLM/embedding APIs).
- Be reproducible from a fresh clone via `README.md` alone.

## 3. Non-goals
- Real-time Wikipedia updates.
- Multi-user / hosted deployment.
- Conversational memory beyond the current Streamlit session.

## 4. Users
- Course instructor running the project locally.
- Developer reviewing the architecture.

## 5. Functional Requirements

### 5.1 Ingest
- Download English Wikipedia article HTML for each of the 40 entities.
- Strip navigation, infoboxes, references, scripts, and styles.
- Persist as JSON: `{title, type, source, url, text}` in `data/raw/`.

### 5.2 Chunk
- Sentence-aware splitter with configurable size (default 800 chars) and overlap (150).
- Designed to handle long documents.

### 5.3 Embed & Store
- Embeddings via Ollama `nomic-embed-text` (local).
- Single ChromaDB persistent collection (cosine distance).
- Each chunk carries metadata: `title`, `type` (`person`|`place`), `url`, `chunk_index`.

### 5.4 Retrieve
- Classify query as `person`, `place`, or `both` (keyword + entity-name rules).
- Apply Chroma `where` filter when classifier is decisive.
- For `both`, query each subset and merge by distance.

### 5.5 Generate
- Local LLM: `llama3.2:3b` via Ollama.
- System prompt forces grounding; outputs "I don't know." when context is insufficient.
- Streaming response in the UI.

### 5.6 UI
- Streamlit chat interface with:
  - input box, message history
  - expandable "Sources" panel per answer (title, type, distance, URL, chunk text)
  - top-K slider
  - clear/reset chat button

## 6. Non-functional Requirements
- Cold ingest of 40 pages: under 5 minutes on broadband.
- Index build: under 10 minutes on CPU with `nomic-embed-text`.
- Per-query latency on `llama3.2:3b` CPU: target <30 s, streaming begins <5 s.

## 7. Success Criteria
- All 12 example queries from HW3 spec produce sensible answers grounded in retrieved
  Wikipedia text.
- Failure-case queries (e.g. "Who is the president of Mars?") return "I don't know."
- Project runs on a fresh machine following only `README.md`.

## 8. Out-of-scope / Future
See `recommendation.md`.
