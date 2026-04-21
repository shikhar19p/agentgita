import re
from src.core.state import SystemState

ABSOLUTE_PHRASES = [
    "the only way", "must always", "never", "the correct interpretation",
    "the true meaning", "the single path", "the one answer",
]


class PluralityChecker:

    def check(self, state: SystemState) -> SystemState:
        state.add_trace("PLURALITY_CHECK", "Starting plurality enforcement")

        if not state.reasoning_graph:
            state.add_trace("PLURALITY_CHECK", "No reasoning to check")
            return state

        has_multiple = self._check_multiple_perspectives(state)
        if has_multiple:
            state.add_trace("PLURALITY_CHECK", "Multiple perspectives detected — ensuring balanced representation")
        else:
            state.add_trace("PLURALITY_CHECK", "Single unified perspective — no plurality concerns")

        if self._check_scope_diversity(state):
            state.add_trace("PLURALITY_CHECK", "Multiple interpretive scopes present — flagging for balanced treatment")

        # Strip absolute language from reasoning nodes
        violations = self._strip_absolute_language(state)
        if violations:
            state.add_trace("PLURALITY_CHECK", f"Softened {violations} absolute-language claim(s)")

        return state

    def _check_multiple_perspectives(self, state: SystemState) -> bool:
        return sum(
            1 for node in state.reasoning_graph
            if "Perspective A:" in node.claim or "Perspective B:" in node.claim
        ) >= 2

    def _check_scope_diversity(self, state: SystemState) -> bool:
        scopes = {
            rv.verse_data.get("interpretive_notes", {}).get("scope")
            for rv in state.retrieved_verses
        }
        scopes.discard(None)
        return len(scopes) >= 2

    def _strip_absolute_language(self, state: SystemState) -> int:
        """Replace absolute phrases with hedged alternatives. Returns count of edits."""
        replacements = {
            "the only way": "one possible way",
            "must always": "may",
            "never": "rarely",
            "the correct interpretation": "one interpretation",
            "the true meaning": "one understanding",
            "the single path": "one path",
            "the one answer": "one perspective",
        }
        count = 0
        for node in state.reasoning_graph:
            for phrase, replacement in replacements.items():
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                new_claim, n = pattern.subn(replacement, node.claim)
                if n:
                    node.claim = new_claim
                    count += n
        return count
