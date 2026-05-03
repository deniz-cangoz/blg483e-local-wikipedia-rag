import json as _json
from typing import Dict, Iterator, List

import requests

from config import LLM_MODEL, OLLAMA_HOST


SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions ONLY using the provided context "
    "from Wikipedia. Follow these rules strictly:\n"
    "1. Base your answer only on the CONTEXT below.\n"
    "2. If the context does not contain the answer, reply exactly: \"I don't know.\"\n"
    "3. Do not invent facts or add details that are not in the context.\n"
    "4. For \"who is X\" or \"what is X\" questions, give a substantive overview: "
    "what they are most famous for, key dates, main contributions or features. "
    "Prefer information from the lead/intro paragraphs of the context over trivia.\n"
    "5. For comparison questions, structure the answer with both subjects.\n"
    "6. Be clear and well-organized; avoid one-line trivia answers."
)


def build_prompt(query: str, hits: List[Dict]) -> str:
    if not hits:
        context_block = "(no context retrieved)"
    else:
        parts = []
        for i, h in enumerate(hits, 1):
            parts.append(f"[Source {i} - {h['title']} ({h['type']})]\n{h['text']}")
        context_block = "\n\n".join(parts)

    return (
        f"CONTEXT:\n{context_block}\n\n"
        f"QUESTION: {query}\n\n"
        "ANSWER:"
    )


def generate(query: str, hits: List[Dict]) -> str:
    prompt = build_prompt(query, hits)
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {"temperature": 0.2},
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()


def generate_stream(query: str, hits: List[Dict]) -> Iterator[str]:
    prompt = build_prompt(query, hits)
    with requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "stream": True,
            "options": {"temperature": 0.2},
        },
        stream=True,
        timeout=300,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            data = _json.loads(line.decode("utf-8"))
            chunk = data.get("response", "")
            if chunk:
                yield chunk
            if data.get("done"):
                break
