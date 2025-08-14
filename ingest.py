import os, re, json, shutil
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from tqdm import tqdm
import chromadb
from chromadb.utils import embedding_functions
from schema import DocChunk
from utils import run, guess_language, sha1
from chunkers import make_chunks

load_dotenv()

DATA_DIR = Path(".data")
INDEX_DIR = DATA_DIR / "index"
REPOS_DIR = DATA_DIR / "repos"
INDEX_DIR.mkdir(parents=True, exist_ok=True)
REPOS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_IGNORES = {".git", "node_modules", "__pycache__", "dist", "build", ".next", ".venv"}

def clone_or_update(repo_url: str) -> Path:
    name = re.sub(r"[^a-zA-Z0-9_-]", "-", repo_url.strip().rstrip("/"))
    dest = REPOS_DIR / name
    if dest.exists():
        try:
            run(["git", "-C", str(dest), "fetch", "--all", "--prune"])
            run(["git", "-C", str(dest), "pull", "--ff-only"])
        except Exception:
            shutil.rmtree(dest, ignore_errors=True)
    if not dest.exists():
        run(["git", "clone", "--depth", "1", repo_url, str(dest)])
    return dest

def collect_files(root: Path) -> List[Path]:
    out = []
    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in DEFAULT_IGNORES:
                continue
            else:
                continue
        if p.suffix.lower() in {".md", ".mdx"} or p.suffix.lower() in {".py",".js",".ts",".java",".cpp",".cc",".c",".go",".rb",".php",".rs",".cs",".scala",".kt"}:
            out.append(p)
    return out

def get_commit(root: Path) -> str:
    try:
        out = run(["git", "-C", str(root), "rev-parse", "HEAD"]).strip()
        return out
    except Exception:
        return "HEAD"


def build_index(repo_url_or_path: str, collection_name: str, embedding_backend: str = "local", api_key: Optional[str] = None):
    client = chromadb.PersistentClient(path=str(INDEX_DIR))

    if embedding_backend == "openai":
        
        final_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not final_api_key:
            raise RuntimeError("OpenAI API key not found. Please provide it in the UI or set the OPENAI_API_KEY environment variable.")
        ef = embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-3-small", 
            api_key=final_api_key
        )
    else:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="sentence-transformers/all-MiniLM-L6-v2")
  

    coll = client.get_or_create_collection(name=collection_name, embedding_function=ef, metadata={"hnsw:space":"cosine"})

    src_path = Path(repo_url_or_path)
    if repo_url_or_path.startswith("http"):
        src_path = clone_or_update(repo_url_or_path)

    commit = get_commit(src_path)
    repo_label = src_path.name

    docs = []
    files = collect_files(src_path)
    for fp in tqdm(files, desc="Chunking"):
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lang = guess_language(str(fp))
        chunks = make_chunks(repo_label, str(fp.relative_to(src_path)), text, lang, commit)
        for ch in chunks:
            ch.url = None
        docs.extend(chunks)

    if docs:
        safe_metadatas = []
        for d in docs:
            meta = d.__dict__.copy()
            filtered_meta = {
                k: v for k, v in meta.items()
                if isinstance(v, (str, int, float, bool))
            }
            safe_metadatas.append(filtered_meta)

        coll.upsert(
            ids=[d.id for d in docs],
            metadatas=safe_metadatas,
            documents=[d.text for d in docs],
        )

    return {
        "collection": collection_name,
        "count": len(docs),
        "commit": commit,
        "path": str(src_path)
    }

if __name__ == "__main__":
    import argparse, pprint
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="GitHub URL or local path")
    ap.add_argument("--name", default="default")
    ap.add_argument("--backend", choices=["local","openai"], default="local")
    args = ap.parse_args()
    info = build_index(args.source, args.name, args.backend)
    pprint.pp(info)
