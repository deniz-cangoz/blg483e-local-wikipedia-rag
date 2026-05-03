# Recommendations for Production Deployment

The current system is optimized for a single-user, local laptop. To deploy it as a real
product, the following changes are recommended.

## 1. Model Serving
- Replace single-process Ollama with a hosted inference layer (vLLM, TGI, or managed
  Ollama on a GPU node). CPU `llama3.2:3b` latency (~10–30 s/answer) is unusable in
  production; a GPU drops this below 2 s.
- Run an LLM gateway (e.g. LiteLLM) so the model can be swapped without code changes.

## 2. Vector Store
- Chroma's persistent client is fine up to ~1M chunks but is single-node. For scale,
  migrate to a managed/clustered store: Qdrant, Weaviate, or pgvector on Postgres.
- Add periodic re-indexing jobs and versioned collections so embedding-model upgrades
  don't break the live index.

## 3. Ingestion Pipeline
- Move ingestion off the user's laptop into an Airflow / Prefect job that:
  - pulls Wikipedia changes incrementally via the MediaWiki API,
  - re-chunks only changed articles,
  - writes new embeddings in batches.
- Cache article HTML and ETags to avoid re-downloading unchanged pages.

## 4. Retrieval Quality
- Replace the keyword classifier with a small intent-classification model (DistilBERT
  fine-tune) — handles ambiguity better.
- Add a reranker (BGE-reranker / Cohere local) on top-20 candidates → final top-4.
- Hybrid retrieval: BM25 + dense embeddings, fused with RRF.

## 5. Observability
- Log every query with: classification decision, retrieved chunk IDs, distances,
  generation time, token counts.
- Track grounding metrics: % of answers that cite retrieved spans, % "I don't know"
  rate, user thumbs-up/down.

## 6. Safety & Quality
- Add a hallucination-detection pass: verify each factual claim in the answer is
  supported by at least one retrieved chunk (n-gram or NLI check).
- Rate-limit per user; add abuse filters on input.
- Cache answers (Redis, keyed by normalized query + index version) for popular queries.

## 7. UX
- Persistent chat history per user (Postgres).
- Citation links inline in the answer text rather than only in an expander.
- Streaming over WebSockets in a real frontend (Next.js) instead of Streamlit.

## 8. Security & Compliance
- Authenticate users; do not expose Ollama port directly.
- Audit Wikipedia content for license (CC BY-SA) attribution in the UI.
- TLS-terminate at a reverse proxy (Caddy / nginx).

## 9. Cost / Capacity
- Track $/query: dominant cost is GPU time. Right-size with autoscaling on request rate.
- Pre-compute and cache embeddings for the full Wikipedia subset; embedding is a
  one-time cost per index version.
