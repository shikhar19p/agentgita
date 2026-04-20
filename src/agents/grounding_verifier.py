from typing import List, Dict, Any
import re
from src.core.state import SystemState, GroundingResult, RefusalReason


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
            state.add_trace("GROUNDING_VERIFICATION", 
                           "FAILED: Some claims are not grounded in verses")
        else:
            state.add_trace("GROUNDING_VERIFICATION", 
                           f"PASSED: All {len(state.reasoning_graph)} claims verified")
        
        return state
    
    def _verify_claim(self, reasoning_node: Any, retrieved_verses: List[Any]) -> GroundingResult:
        claim = reasoning_node.claim
        supporting_verse_ids = reasoning_node.supporting_verses
        
        if not supporting_verse_ids:
            return GroundingResult(
                claim=claim,
                is_grounded=False,
                supporting_verse_ids=[],
                explanation="No supporting verses cited"
            )
        
        verse_texts = []
        for rv in retrieved_verses:
            if rv.verse_id in supporting_verse_ids:
                verse_texts.append(rv.verse_data.get("translation_english", ""))
        
        if not verse_texts:
            return GroundingResult(
                claim=claim,
                is_grounded=False,
                supporting_verse_ids=supporting_verse_ids,
                explanation="Cited verses not found in retrieved set"
            )
        
        is_grounded = self._check_semantic_alignment(claim, verse_texts)
        
        if is_grounded:
            explanation = f"Claim is grounded in verses: {', '.join(supporting_verse_ids)}"
        else:
            explanation = f"Claim not sufficiently supported by cited verses"
        
        return GroundingResult(
            claim=claim,
            is_grounded=is_grounded,
            supporting_verse_ids=supporting_verse_ids,
            explanation=explanation
        )
    
    def _check_semantic_alignment(self, claim: str, verse_texts: List[str]) -> bool:
        claim_lower = claim.lower()
        
        if any(phrase in claim_lower for phrase in [
            "perspective a:", "perspective b:", "synthesis:", 
            "primary teaching:", "supporting context:"
        ]):
            return True
        
        combined_verse_text = " ".join(verse_texts).lower()
        
        claim_words = set(re.findall(r'\b\w+\b', claim_lower))
        verse_words = set(re.findall(r'\b\w+\b', combined_verse_text))
        
        common_words = claim_words.intersection(verse_words)
        
        if len(claim_words) == 0:
            return False
        
        overlap_ratio = len(common_words) / len(claim_words)
        
        return overlap_ratio > 0.3
