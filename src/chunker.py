import re
from typing import List

from config import CHUNK_SIZE, CHUNK_OVERLAP


def split_into_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    sentences = split_into_sentences(text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for sentence in sentences:
        s_len = len(sentence)
        if current_len + s_len + 1 > chunk_size and current:
            chunks.append(" ".join(current))
            if overlap > 0:
                tail: List[str] = []
                tail_len = 0
                for s in reversed(current):
                    if tail_len + len(s) + 1 > overlap:
                        break
                    tail.insert(0, s)
                    tail_len += len(s) + 1
                current = tail[:]
                current_len = tail_len
            else:
                current = []
                current_len = 0

        current.append(sentence)
        current_len += s_len + 1

    if current:
        chunks.append(" ".join(current))

    return chunks
