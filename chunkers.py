import re
from typing import List, Tuple
from pathlib import Path
from schema import DocChunk
from utils import sha1



def split_python(src: str) -> List[Tuple[int,int]]:
    lines = src.splitlines()
    idxs = [i for i,l in enumerate(lines) if re.match(r"^(def |class )", l)] or [0]
    idxs = sorted(set([0] + idxs + [len(lines)]))
    return [(idxs[i], idxs[i+1]) for i in range(len(idxs)-1)]

JS_FUNC_RE = re.compile(r"^(export\s+)?(async\s+)?(function|class)\s+|^const\s+\w+\s*=\s*(\(.+\)\s*=>|function)")

def split_js(src: str) -> List[Tuple[int,int]]:
    lines = src.splitlines()
    idxs = [i for i,l in enumerate(lines) if JS_FUNC_RE.search(l)] or [0]
    idxs = sorted(set([0] + idxs + [len(lines)]))
    return [(idxs[i], idxs[i+1]) for i in range(len(idxs)-1)]

JAVA_RE = re.compile(r"^(public|protected|private)?\s*(class|interface|enum)\s+|^\s*(public|private|protected|static|final).*\(.*\)\s*\{")

def split_java(src: str) -> List[Tuple[int,int]]:
    lines = src.splitlines()
    idxs = [i for i,l in enumerate(lines) if JAVA_RE.search(l)] or [0]
    idxs = sorted(set([0] + idxs + [len(lines)]))
    return [(idxs[i], idxs[i+1]) for i in range(len(idxs)-1)]

CPP_RE = re.compile(r"^\s*(class|struct)\s+|^[\w:<>~\*\&\s]+\(.*\)\s*\{")

def split_cpp(src: str) -> List[Tuple[int,int]]:
    lines = src.splitlines()
    idxs = [i for i,l in enumerate(lines) if CPP_RE.search(l)] or [0]
    idxs = sorted(set([0] + idxs + [len(lines)]))
    return [(idxs[i], idxs[i+1]) for i in range(len(idxs)-1)]

def split_markdown(src: str) -> List[Tuple[int,int]]:
    lines = src.splitlines()
    idxs = [i for i,l in enumerate(lines) if l.strip().startswith("#")] or [0]
    idxs = sorted(set([0] + idxs + [len(lines)]))
    return [(idxs[i], idxs[i+1]) for i in range(len(idxs)-1)]

LANG_SPLITTERS = {
    "python": split_python,
    "javascript": split_js,
    "typescript": split_js,
    "java": split_java,
    "cpp": split_cpp,
    "c": split_cpp,
    "markdown": split_markdown,
}

def make_chunks(repo: str, path: str, text: str, language: str, commit: str):
    splitter = LANG_SPLITTERS.get(language)
    chunks = []
    if not splitter:
        lines = text.splitlines()
        size = 80
        spans = [(i, min(i+size, len(lines))) for i in range(0, len(lines), size)]
    else:
        spans = splitter(text)

    title = Path(path).name
    for start, end in spans:
        seg = "\n".join(text.splitlines()[start:end])
        if len(seg.strip()) < 10:
            continue
        chunk_id = sha1(f"{repo}:{path}:{start}:{end}:{commit}")
        chunks.append(DocChunk(
            id=chunk_id, repo=repo, path=path,
            start_line=start+1, end_line=end,
            language=language,
            kind="markdown" if language=="markdown" else "code",
            title=title, symbols=[], text=seg,
            url=None, commit=commit, meta={}
        ))
    return chunks
