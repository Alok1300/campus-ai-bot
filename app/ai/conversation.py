"""
conversation.py — In-memory conversation session store.
Keeps last N turns per session for context-aware AI responses.
"""
from typing import Dict, List, Any
from collections import deque
import time

MAX_TURNS = 10  # keep last 10 turns per session

class ConversationSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turns: deque = deque(maxlen=MAX_TURNS)
        self.last_activity = time.time()
        # Track last resolved entities for context follow-up
        self.last_source: str | None = None
        self.last_destination: str | None = None
        self.last_results: List[Any] = []
        self.current_location: str | None = None

    def add_turn(self, role: str, content: str):
        self.turns.append({"role": role, "content": content})
        self.last_activity = time.time()

    def get_history(self) -> List[Dict[str, str]]:
        return list(self.turns)

    def is_stale(self, max_age_seconds: int = 3600) -> bool:
        return (time.time() - self.last_activity) > max_age_seconds


class ConversationStore:
    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}

    def get_or_create(self, session_id: str) -> ConversationSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(session_id)
        return self._sessions[session_id]

    def cleanup_stale(self):
        """Remove sessions inactive for more than 1 hour."""
        stale = [sid for sid, s in self._sessions.items() if s.is_stale()]
        for sid in stale:
            del self._sessions[sid]


conversation_store = ConversationStore()
