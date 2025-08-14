import os, re, subprocess, hashlib
from pathlib import Path

SUPPORTED_CODE_EXTS = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".java": "java", ".cpp": "cpp", ".cc":"cpp", ".c": "c",
    ".go": "go", ".rb": "ruby", ".php": "php", ".rs": "rust",
    ".cs": "csharp", ".scala":"scala", ".kt":"kotlin",
}

MARKDOWN_EXTS = {".md", ".mdx"}

GITHUB_BLOB_FMT = "https://github.com/{owner}/{repo}/blob/{commit}/{path}#L{start}-L{end}"

def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def run(cmd, cwd=None) -> str:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=False)
    if p.returncode != 0:
        raise RuntimeError(p.stderr)
    return p.stdout

def guess_language(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext in SUPPORTED_CODE_EXTS:
        return SUPPORTED_CODE_EXTS[ext]
    if ext in MARKDOWN_EXTS:
        return "markdown"
    return "text"
