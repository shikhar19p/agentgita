from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Turn:
    query: str
    response: str
    retrieved_verse_ids: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)


class ConversationMemory:
    """Episodic per-session memory — tracks prior turns to enable follow-up queries."""

    def __init__(self, max_turns: int = 10):
        self._turns: List[Turn] = []
        self.max_turns = max_turns

    def add_turn(self, query: str, response: str, verse_ids: List[str] = None, themes: List[str] = None):
        turn = Turn(
            query=query,
            response=response,
            retrieved_verse_ids=verse_ids or [],
            themes=themes or [],
        )
        self._turns.append(turn)
        if len(self._turns) > self.max_turns:
            self._turns.pop(0)

    def enrich_query(self, query: str) -> str:
        """Prepend recent context so follow-up queries like 'what about anger?' resolve correctly."""
        if not self._turns:
            return query

        recent = self._turns[-1]
        # Only enrich if query looks like a follow-up (short + no domain keywords)
        if len(query.split()) <= 6 and recent.themes:
            context_hint = f"[Prior context: {recent.query} — themes: {', '.join(recent.themes[:3])}] {query}"
            return context_hint
        return query

    def recent_verse_ids(self, n: int = 3) -> List[str]:
        """Return verse IDs retrieved in the last n turns — useful for seeding retrieval."""
        ids = []
        for turn in self._turns[-n:]:
            ids.extend(turn.retrieved_verse_ids)
        return list(dict.fromkeys(ids))  # deduplicated, order preserved

    def summary(self) -> str:
        if not self._turns:
            return "No prior conversation."
        lines = [f"Turn {i+1}: {t.query}" for i, t in enumerate(self._turns[-3:])]
        return "\n".join(lines)

    def clear(self):
        self._turns.clear()
