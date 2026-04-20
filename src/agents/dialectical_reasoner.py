from typing import List, Any
from src.core.state import SystemState, ReasoningNode


_SYNTHESIS_MAP = {
    "action": "Both perspectives address different aspects of action: one emphasizes engagement, the other emphasizes detachment. They are complementary rather than contradictory.",
    "devotion": "These verses present different paths (jnana and bhakti) which the Gita treats as complementary approaches to the same truth.",
    "duty": "The tension between duty and compassion is resolved through understanding one's svadharma in context.",
    "effort": "Divine will and self-effort are not opposed; effort is the means through which divine will manifests.",
    "renunciation": "Renunciation of fruits, not of action, is the Gita's resolution — inner detachment while remaining outwardly engaged.",
    "knowledge": "Knowledge and devotion are presented as two wings of the same bird; neither excludes the other.",
}


class DialecticalReasoner:

    def reason(self, state: SystemState) -> SystemState:
        state.add_trace("DIALECTICAL_REASONING", "Starting dialectical reasoning")

        if not state.retrieved_verses:
            state.add_trace("DIALECTICAL_REASONING", "No verses to reason from")
            return state

        if state.contradictions:
            state.add_trace("DIALECTICAL_REASONING", f"Processing {len(state.contradictions)} contradictions")
            nodes = self._construct_dialectical_reasoning(state.retrieved_verses, state.contradictions)
        else:
            state.add_trace("DIALECTICAL_REASONING", "No contradictions — constructing unified reasoning")
            nodes = self._construct_unified_reasoning(state.retrieved_verses)

        state.reasoning_graph.extend(nodes)
        state.add_trace("DIALECTICAL_REASONING", f"Generated {len(nodes)} reasoning nodes")
        state.mark_step("dialectical_reasoning")
        return state

    # ------------------------------------------------------------------

    def _construct_dialectical_reasoning(self, retrieved_verses: List[Any], contradictions: List[Any]) -> List[ReasoningNode]:
        nodes = []
        for contradiction in contradictions:
            involved = [rv for rv in retrieved_verses if rv.verse_id in contradiction.verse_ids]
            if len(involved) < 2:
                continue

            nodes.append(ReasoningNode(
                claim=f"Perspective A: {self._extract_perspective(involved[0])}",
                supporting_verses=[involved[0].verse_id],
                grounded=True,
                confidence=0.8,
            ))
            nodes.append(ReasoningNode(
                claim=f"Perspective B: {self._extract_perspective(involved[1])}",
                supporting_verses=[involved[1].verse_id],
                grounded=True,
                confidence=0.8,
            ))
            nodes.append(ReasoningNode(
                claim=f"Synthesis: {self._synthesize(contradiction.description)}",
                supporting_verses=[v.verse_id for v in involved],
                grounded=True,
                confidence=0.7,
            ))
        return nodes

    def _construct_unified_reasoning(self, retrieved_verses: List[Any]) -> List[ReasoningNode]:
        nodes = []
        if not retrieved_verses:
            return nodes

        primary = retrieved_verses[0]
        nodes.append(ReasoningNode(
            claim=f"Primary teaching: {self._extract_core_teaching(primary)}",
            supporting_verses=[primary.verse_id],
            grounded=True,
            confidence=0.9,
        ))

        # Use ALL remaining retrieved verses as supporting context (not just [1:3])
        support_verses = retrieved_verses[1:]
        if support_verses:
            teachings = [self._extract_core_teaching(rv) for rv in support_verses]
            nodes.append(ReasoningNode(
                claim=f"Supporting context: {'; '.join(teachings)}",
                supporting_verses=[rv.verse_id for rv in support_verses],
                grounded=True,
                confidence=0.75,
            ))

        return nodes

    # ------------------------------------------------------------------

    def _extract_perspective(self, rv: Any) -> str:
        teaching = rv.verse_data.get("interpretive_notes", {}).get("core_teaching", "")
        if teaching:
            return teaching
        translation = rv.verse_data.get("translation_english", "")
        return translation[:150] + "..." if len(translation) > 150 else translation

    def _extract_core_teaching(self, rv: Any) -> str:
        teaching = rv.verse_data.get("interpretive_notes", {}).get("core_teaching", "")
        if teaching:
            return teaching
        translation = rv.verse_data.get("translation_english", "")
        return translation[:100] + "..." if len(translation) > 100 else translation

    def _synthesize(self, tension_description: str) -> str:
        desc_lower = tension_description.lower()
        for key, template in _SYNTHESIS_MAP.items():
            if key in desc_lower:
                return template
        return "These perspectives represent different dimensions of the same teaching, to be understood contextually."
