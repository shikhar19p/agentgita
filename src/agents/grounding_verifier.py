import re
from typing import List, Any
from src.core.state import SystemState, GroundingResult, RefusalReason

# Prefixes injected by DialecticalReasoner that are always considered grounded
_STRUCTURAL_PREFIXES = (
    "Perspective A:", "Perspective B:", "Synthesis:",
    "Primary teaching:", "Supporting context:",
)

# Threshold: fraction of claim words that must appear in verse text
_WORD_OVERLAP_THRESHOLD = 0.30

_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "of", "in", "on", "at", "to", "for", "with",
    "by", "from", "and", "or", "but", "not", "this", "that", "it", "its",
    "i", "my", "me", "we", "our", "you", "he", "she", "they", "their",
}


class GroundingVerifier:

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode

    def verify(self, state: SystemState) -> SystemState:
        state.add_trace("GROUNDING_VERIFICATION", "Starting grounding verification")

        if not state.reasoning_graph:
            state.add_trace("GROUNDING_VERIFICATION", "No reasoning nodes to verify")
            return state

        all_grounded = True
        for node in state.reasoning_graph:
            result = self._verify_claim(node, state.retrieved_verses)
            state.grounding_results.append(result)
            if not result.is_grounded:
                all_grounded = False
                node.grounded = False

        if not all_grounded and self.strict_mode:
            state.refusal_reason = RefusalReason.INSUFFICIENT_GROUNDING
            state.add_trace("GROUNDING_VERIFICATION", "FAILED: Some claims are not grounded in verses")
        else:
            state.add_trace(
                "GROUNDING_VERIFICATION",
                f"PASSED: {len(state.reasoning_graph)} claims verified"
            )

        state.mark_step("grounding_verification")
        return state

    def _verify_claim(self, node: Any, retrieved_verses: List[Any]) -> GroundingResult:
        claim = node.claim

        # Structural prefixes produced by the reasoning agents are always grounded
        if any(claim.startswith(p) for p in _STRUCTURAL_PREFIXES):
            return GroundingResult(
                claim=claim,
                is_grounded=True,
                supporting_verse_ids=node.supporting_verses,
                explanation="Structural reasoning node — grounded by construction",
            )

        if not node.supporting_verses:
            return GroundingResult(
                claim=claim,
                is_grounded=False,
                supporting_verse_ids=[],
                explanation="No supporting verses cited",
            )

        verse_texts = [
            rv.verse_data.get("translation_english", "") + " "
            + " ".join(rv.verse_data.get("interpretive_notes", {}).get("core_teaching", "").split())
            for rv in retrieved_verses
            if rv.verse_id in node.supporting_verses
        ]

        if not verse_texts:
            return GroundingResult(
                claim=claim,
                is_grounded=False,
                supporting_verse_ids=node.supporting_verses,
                explanation="Cited verses not found in retrieved set",
            )

        is_grounded = self._check_alignment(claim, verse_texts)
        return GroundingResult(
            claim=claim,
            is_grounded=is_grounded,
            supporting_verse_ids=node.supporting_verses,
            explanation=(
                f"Grounded in: {', '.join(node.supporting_verses)}"
                if is_grounded
                else "Insufficient word overlap with cited verses"
            ),
        )

    @staticmethod
    def _check_alignment(claim: str, verse_texts: List[str]) -> bool:
        combined = " ".join(verse_texts).lower()

        claim_words = {
            w for w in re.findall(r'\b\w+\b', claim.lower())
            if w not in _STOP_WORDS and len(w) > 2
        }
        verse_words = set(re.findall(r'\b\w+\b', combined))

        if not claim_words:
            return False

        overlap = len(claim_words & verse_words) / len(claim_words)
        return overlap >= _WORD_OVERLAP_THRESHOLD
