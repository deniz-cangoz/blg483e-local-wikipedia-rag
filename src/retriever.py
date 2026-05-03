from typing import Dict, List, Optional

from config import PEOPLE, PLACES, TOP_K
from embed_store import embed_texts, get_collection


PERSON_KEYWORDS = {"who", "person", "scientist", "artist", "player", "musician", "writer", "born", "biography"}
PLACE_KEYWORDS = {"where", "located", "city", "country", "monument", "building", "mountain", "tower", "wall"}

ALL_ENTITIES = [(p, "person") for p in PEOPLE] + [(p, "place") for p in PLACES]


def detect_entities(query: str) -> List[Dict[str, str]]:
    q = query.lower()
    found: List[Dict[str, str]] = []
    for name, etype in ALL_ENTITIES:
        if name.lower() in q:
            found.append({"title": name, "type": etype})
    return found


def classify_query(query: str) -> str:
    q = query.lower()
    tokens = set(q.split())

    has_person = any(p.lower() in q for p in PEOPLE) or bool(tokens & PERSON_KEYWORDS)
    has_place = any(p.lower() in q for p in PLACES) or bool(tokens & PLACE_KEYWORDS)

    if has_person and has_place:
        return "both"
    if has_person:
        return "person"
    if has_place:
        return "place"
    return "both"


def _query_collection(query_embedding, top_k: int, where: Optional[dict]) -> List[Dict]:
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
    )
    hits: List[Dict] = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists):
        hits.append({
            "text": doc,
            "title": meta.get("title"),
            "type": meta.get("type"),
            "url": meta.get("url"),
            "chunk_index": meta.get("chunk_index"),
            "distance": dist,
        })
    return hits


def get_lead_chunks(entities: List[Dict[str, str]], n_lead: int = 2) -> List[Dict]:
    collection = get_collection()
    lead_hits: List[Dict] = []
    for ent in entities:
        res = collection.get(
            where={
                "$and": [
                    {"title": ent["title"]},
                    {"chunk_index": {"$lt": n_lead}},
                ]
            },
        )
        docs = res.get("documents", [])
        metas = res.get("metadatas", [])
        for doc, meta in zip(docs, metas):
            lead_hits.append({
                "text": doc,
                "title": meta.get("title"),
                "type": meta.get("type"),
                "url": meta.get("url"),
                "chunk_index": meta.get("chunk_index"),
                "distance": 0.0,
            })
    lead_hits.sort(key=lambda h: (h["title"], h.get("chunk_index") or 0))
    return lead_hits


def retrieve(query: str, top_k: int = TOP_K, type_filter: Optional[str] = None) -> List[Dict]:
    query_embedding = embed_texts([query])[0]
    where = {"type": type_filter} if type_filter in ("person", "place") else None
    return _query_collection(query_embedding, top_k, where)


def retrieve_smart(query: str, top_k: int = TOP_K) -> List[Dict]:
    decision = classify_query(query)
    entities = detect_entities(query)

    lead_hits = get_lead_chunks(entities, n_lead=2) if entities else []

    semantic_k = top_k if entities else top_k * 2

    if decision == "both":
        people_hits = retrieve(query, top_k=semantic_k, type_filter="person")
        place_hits = retrieve(query, top_k=semantic_k, type_filter="place")
        semantic = sorted(people_hits + place_hits, key=lambda h: h["distance"])[:semantic_k]
    else:
        semantic = retrieve(query, top_k=semantic_k, type_filter=decision)

    seen = set()
    merged: List[Dict] = []
    for h in lead_hits + semantic:
        key = (h["title"], h.get("chunk_index"))
        if key in seen:
            continue
        seen.add(key)
        merged.append(h)

    return merged
