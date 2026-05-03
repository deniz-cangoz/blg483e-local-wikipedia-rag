import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from generator import generate_stream
from retriever import classify_query, retrieve_smart


st.set_page_config(page_title="Local Wikipedia RAG", page_icon=":books:", layout="wide")
st.title("Local Wikipedia RAG Assistant")
st.caption("Runs entirely on localhost using Ollama + Chroma.")

with st.sidebar:
    st.header("Settings")
    show_context = st.checkbox("Show retrieved context", value=True)
    top_k = st.slider("Top-K chunks", min_value=2, max_value=10, value=4)
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources") and show_context:
            with st.expander("Sources"):
                for i, src in enumerate(msg["sources"], 1):
                    st.markdown(f"**{i}. {src['title']} ({src['type']})** - distance={src['distance']:.4f}")
                    st.markdown(f"[{src['url']}]({src['url']})")
                    st.write(src["text"])

query = st.chat_input("Ask about a famous person or place...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        decision = classify_query(query)
        st.caption(f"Query classified as: **{decision}**")

        with st.spinner("Retrieving context..."):
            hits = retrieve_smart(query, top_k=top_k)

        placeholder = st.empty()
        full_response = ""
        for token in generate_stream(query, hits):
            full_response += token
            placeholder.markdown(full_response + "_")
        placeholder.markdown(full_response)

        if show_context:
            with st.expander("Sources"):
                for i, src in enumerate(hits, 1):
                    st.markdown(f"**{i}. {src['title']} ({src['type']})** - distance={src['distance']:.4f}")
                    st.markdown(f"[{src['url']}]({src['url']})")
                    st.write(src["text"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "sources": hits,
        })
