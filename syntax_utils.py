from dataclasses import dataclass
from typing import List, Dict, Optional
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
import os


STYLE_NAME = os.getenv("CODE_HIGHLIGHT_STYLE", "default")

def highlight_code(code: str, language: Optional[str] = None) -> str:
    try:
        lexer = get_lexer_by_name(language) if language else guess_lexer(code)
    except Exception:
        from pygments.lexers.special import TextLexer
        lexer = TextLexer()

    formatter = HtmlFormatter(
        style=STYLE_NAME,
        linenos="table",
        nowrap=False,
        full=False,
        cssclass="highlight"
    )
    highlighted = highlight(code, lexer, formatter)
    return f"<div class='code-block'><pre><code>{highlighted}</code></pre></div>"

def get_pygments_css() -> str:
    return HtmlFormatter(style=STYLE_NAME).get_style_defs('.highlight')

@dataclass
class DocChunk:
    id: str
    repo: str
    path: str
    start_line: int
    end_line: int
    language: str
    kind: str  # "code" | "markdown" | "api"
    title: Optional[str]
    symbols: List[str]
    text: str
    url: Optional[str]  # permalink to GitHub blob lines
    commit: Optional[str]
    meta: Dict

    def render_highlighted(self) -> str:
        """
        Returns HTML-highlighted version of the chunk's text
        based on the stored programming language.
        """
        return highlight_code(self.text, self.language)
