# Local Wikipedia RAG Assistant (BLG483E - HW3)

A fully-local Retrieval-Augmented Generation (RAG) assistant that answers questions about
20 famous people and 20 famous places using Wikipedia data. Runs entirely on localhost — no
external LLM API.

**Stack:** Python · Ollama (`llama3.2:3b` + `nomic-embed-text`) · ChromaDB · Streamlit

## Demo Video

[Watch the 5-minute demo on Google Drive](https://drive.google.com/file/d/1QWClECMJNjs4J3TJ2qRAEFp5tRHcZpJc/view?usp=sharing)

## 1. Prerequisites

- Python 3.11+ (`py --version`)
- [Ollama](https://ollama.com/) installed and running
- Pull the local models:

```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Verify Ollama is up: `ollama list` should show both models.

## 2. Install Dependencies

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

## 3. Run the Local Model

Ollama runs automatically as a service on Windows. To check:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

## 4. Ingest Wikipedia Data

Downloads each of the 40 Wikipedia pages and stores cleaned JSON under `data/raw/`.

```powershell
py src\ingest.py
```

## 5. Build the Vector Index

Chunks each document, generates embeddings via Ollama, and writes to a persistent
ChromaDB collection at `chroma_db/`.

```powershell
py src\embed_store.py
```

## 6. Start the Chat UI

```powershell
py -m streamlit run src\app.py
```

Browser will open at `http://localhost:8501`.

## Example Queries

- Who was Albert Einstein and what is he known for?
- What did Marie Curie discover?
- Where is the Eiffel Tower located?
- Compare Albert Einstein and Nikola Tesla
- Which famous place is located in Turkey?
- Who is the president of Mars?  *(should answer "I don't know")*

## Project Layout

```
src/
  config.py       # entity lists, paths, model names, chunk sizes
  ingest.py       # download + clean Wikipedia HTML
  chunker.py      # sentence-aware chunking with overlap
  embed_store.py  # Ollama embeddings + Chroma persistent store
  retriever.py    # query classification (person/place/both) + filtered retrieval
  generator.py    # prompt construction + Ollama generate (streaming)
  app.py          # Streamlit chat UI
data/raw/         # ingested Wikipedia JSON files
chroma_db/        # persistent vector store
```

## Design Choices (Brief)

- **Single Chroma collection with `type` metadata** (Option B). Simpler than two stores;
  the `where={"type": ...}` filter handles routing while still allowing mixed queries.
- **Sentence-aware chunking** (~800 chars, 150 overlap). Sentence boundaries preserve
  semantic units; overlap keeps facts that span a boundary retrievable.
- **Rule-based query classifier**: keyword + entity-name match. Fast, predictable, no
  extra LLM call.
- **`temperature=0.2`** + strict system prompt → grounded answers, "I don't know" fallback.

See `Product_prd.md` for the full spec and `recommendation.md` for production notes.
