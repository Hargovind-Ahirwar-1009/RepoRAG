import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

SYS_PROMPT = (
    "You are CodeDocs-RAG, an expert technical writer and software engineer. "
    "Write concise, accurate explanations, preserve syntax, show minimal working code examples, and cite file paths + line ranges when possible. "
    "If a direct answer is unsafe or unknown, say so and provide best-effort guidance from retrieved context only."
)

def format_context(ctx: List[Dict]) -> str:
    blocks = []
    for c in ctx:
        title = c.get("title", "?")
        path = c.get("path", "?")
        lang = c.get("language", "text")
        start, end = c.get("start_line", 1), c.get("end_line", 1)
        code = c.get("doc", "")
        blocks.append(f"<doc title='{title}' path='{path}' lang='{lang}' lines='{start}-{end}'>\n{code}\n</doc>")
    return "\n\n".join(blocks)

def answer_with_openai(q: str, ctx: List[Dict]) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    content = [
        {"role": "system", "content": SYS_PROMPT},
        {"role": "user", "content": f"Question:\n{q}\n\nContext:\n{format_context(ctx)}"}
    ]
    r = client.chat.completions.create(model="gpt-4o-mini", messages=content, temperature=0.2)
    return r.choices[0].message.content

def answer_with_ollama(q: str, ctx: List[Dict]) -> str:
    import requests
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    payload = {
        "model": "llama3.1",
        "prompt": SYS_PROMPT + "\n\n" + f"Q: {q}\nCTX:\n{format_context(ctx)}"
    }
    r = requests.post(f"{host}/api/generate", json=payload, timeout=120)
    return r.text

def answer_with_groq(q: str, ctx: List[Dict]) -> str:
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in environment")
    client = Groq(api_key=api_key)
    content = [
        {"role": "system", "content": SYS_PROMPT},
        {"role": "user", "content": f"Question:\n{q}\n\nContext:\n{format_context(ctx)}"}
    ]
    r = client.chat.completions.create(model=model, messages=content, temperature=0.2)
    return r.choices[0].message.content

def generate_answer(q: str, ctx: List[Dict]) -> str:
    if os.getenv("OPENAI_API_KEY"):
        try:
            return answer_with_openai(q, ctx)
        except Exception as e:
            return f"(OpenAI LLM error: {e})\n\nTop context:\n" + "\n\n".join(c.get("doc", "")[:4000] for c in ctx)
    elif os.getenv("GROQ_API_KEY"):
        try:
            return answer_with_groq(q, ctx)
        except Exception as e:
            return f"(Groq LLM error: {e})\n\nTop context:\n" + "\n\n".join(c.get("doc", "")[:4000] for c in ctx)
    elif os.getenv("OLLAMA_HOST"):
        try:
            return answer_with_ollama(q, ctx)
        except Exception as e:
            return f"(Ollama LLM error: {e})\n\nTop context:\n" + "\n\n".join(c.get("doc", "")[:4000] for c in ctx)
    else:
        parts = []
        for i, c in enumerate(ctx, 1):
            path = c.get("path", "")
            lines = f"{c.get('start_line', 1)}-{c.get('end_line', 1)}"
            parts.append(f"[{i}] {path}:{lines}\n\n" + c.get("doc", ""))
        return "No LLM key configured. Showing top relevant snippets.\n\n" + "\n\n".join(parts)
