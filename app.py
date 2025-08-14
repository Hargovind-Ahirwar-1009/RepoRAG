import streamlit as st
from ingest import build_index
from retriever import HybridRetriever
from llm import generate_answer

st.set_page_config(page_title="CodeDocs RAG", page_icon="📚", layout="wide")
st.title("📚 Code Documentation RAG (GitHub + Multi‑Language)")

with st.sidebar:
    st.header("Index a Repository")
    src = st.text_input("GitHub URL or local path", placeholder="https://github.com/owner/repo or ./local/path")
    name = st.text_input("Collection name", value="default")
    backend = st.selectbox("Embedding backend", ["local", "openai"], index=0)
    
   
    openai_api_key = ""
    if backend == "openai":
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            type="password", 
            placeholder="sk-...",
            help="Get your API key from https://platform.openai.com/keys"
        )

    if st.button("Build / Update Index", type="primary"):
       
        with st.status("Indexing…", expanded=True) as status:
            info = build_index(src, name, backend, api_key=openai_api_key)
            st.write(info)
            status.update(label="Index ready", state="complete")
   

st.divider()

col1, col2 = st.columns([2,1])
with col1:
    question = st.text_area("Ask about the codebase or API…", height=140,
                            placeholder="e.g., How does the client authenticate? Show a minimal example in Python and JS.")
    topk = st.slider("Top-K context", 2, 10, 5)
    go = st.button("Search & Answer", type="primary")

with col2:
    coll = st.text_input("Use collection", value="default")

if go and question.strip():
    retr = HybridRetriever(collection_name=coll)
    hits = retr.query(question, k=topk)

    with st.expander("🔎 Top retrievals (debug)", expanded=False):
        for i,h in enumerate(hits,1):
            st.markdown(f"**{i}. {h.get('path','?')}** · Lines {h.get('start_line','?')}-{h.get('end_line','?')}  · Lang `{h.get('language','?')}`")
            st.code(h.get("doc",""), language=h.get("language","text"))

    answer = generate_answer(question, hits)
    st.markdown("### 🧠 Answer")
    st.write(answer)
