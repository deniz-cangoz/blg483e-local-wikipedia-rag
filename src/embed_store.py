import json
from typing import List

import chromadb
import requests

from chunker import chunk_text
from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBED_MODEL,
    OLLAMA_HOST,
    RAW_DIR,
)


def embed_texts(texts: List[str]) -> List[List[float]]:
    embeddings: List[List[float]] = []
    for text in texts:
        response = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=120,
        )
        response.raise_for_status()
        embeddings.append(response.json()["embedding"])
    return embeddings


def get_collection(reset: bool = False):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_index(reset: bool = True) -> int:
    collection = get_collection(reset=reset)

    raw_files = sorted(RAW_DIR.glob("*.json"))
    if not raw_files:
        print(f"[WARN] No files in {RAW_DIR}. Run ingest.py first.")
        return 0

    total_chunks = 0
    for path in raw_files:
        record = json.loads(path.read_text(encoding="utf-8"))
        title = record["title"]
        entity_type = record["type"]
        url = record["url"]
        text = record["text"]

        chunks = chunk_text(text)
        if not chunks:
            continue

        print(f"[EMBED] {title} ({entity_type}): {len(chunks)} chunks")
        embeddings = embed_texts(chunks)

        ids = [f"{entity_type}_{path.stem}_{i}" for i in range(len(chunks))]
        metadatas = [
            {"title": title, "type": entity_type, "url": url, "chunk_index": i}
            for i in range(len(chunks))
        ]

        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        total_chunks += len(chunks)

    print(f"\n[DONE] Indexed {total_chunks} chunks across {len(raw_files)} entities.")
    return total_chunks


if __name__ == "__main__":
    build_index(reset=True)
