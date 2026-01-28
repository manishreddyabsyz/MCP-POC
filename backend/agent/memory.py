from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SessionState:
    session_id: str
    case_data: Optional[Dict[str, Any]] = None  # Structured case data for ChatGPT
    level2_qa: List[Dict[str, str]] = field(default_factory=list)  # {"q": "...", "a": "..."}
    pending_knowledge_article: Optional[Dict[str, Any]] = None


class MemoryStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, SessionState] = {}

    def get(self, session_id: str) -> SessionState:
        if not session_id:
            session_id = "default"
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id=session_id)
        return self._sessions[session_id]

    def reset(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]

