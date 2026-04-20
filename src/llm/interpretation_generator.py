from typing import Any, List
from src.core.state import SystemState, ReasoningNode


class InterpretationGenerator:
    """Wraps any LLM client that implements generate_interpretation()."""

    def __init__(self, llm_client: Any):
        self.client = llm_client

    def generate(self, state: SystemState) -> SystemState:
        state.add_trace("INTERPRETATION_GENERATION", "Starting LLM-based interpretation")

        if not state.retrieved_verses:
            state.add_trace("INTERPRETATION_GENERATION", "No verses to interpret")
            return state

        primary_verse = state.retrieved_verses[0].verse_data
        supporting_verses = [rv.verse_data for rv in state.retrieved_verses[1:3]]
        reasoning_context = self._extract_reasoning_context(state)

        interpretation = self.client.generate_interpretation(
            query=state.query,
            primary_verse=primary_verse,
            supporting_verses=supporting_verses,
            reasoning_context=reasoning_context,
        )

        if interpretation.startswith("[Error"):
            state.add_trace("INTERPRETATION_GENERATION", f"LLM error: {interpretation}")
            return state

        state.add_trace(
            "INTERPRETATION_GENERATION",
            f"Generated interpretation ({len(interpretation)} chars)"
        )

        # Replace the primary-teaching node if present; otherwise append a new node
        for node in state.reasoning_graph:
            if "Primary teaching:" in node.claim or node.claim.startswith("Interpretation"):
                node.claim = interpretation
                break
        else:
            state.reasoning_graph.append(ReasoningNode(
                claim=interpretation,
                supporting_verses=[state.retrieved_verses[0].verse_id],
                grounded=True,
                confidence=0.85,
            ))

        return state

    def _extract_reasoning_context(self, state: SystemState) -> str:
        parts = []

        if state.contradictions:
            parts.append(f"Note: {len(state.contradictions)} thematic tensions detected:")
            for c in state.contradictions[:2]:
                parts.append(f"- {c.description}")

        scopes = set()
        for rv in state.retrieved_verses[:3]:
            scope = rv.verse_data.get("interpretive_notes", {}).get("scope")
            if scope:
                scopes.add(scope)
        if len(scopes) > 1:
            parts.append(f"Multiple interpretive scopes present: {', '.join(scopes)}")

        return "\n".join(parts) if parts else None
