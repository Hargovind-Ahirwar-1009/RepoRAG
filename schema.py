from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any

@dataclass
class DocChunk:
    id: str
    repo: str
    path: str
    start_line: int
    end_line: int
    language: str
    kind: str  # "code" | "markdown" | "api"
    title: Optional[str] = None
    symbols: List[str] = field(default_factory=list)
    text: str = ""
    url: Optional[str] = None  
    commit: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for JSON/DB storage."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DocChunk":
        """Create DocChunk from a dictionary."""
        return DocChunk(**data)
