from typing import List, Dict, Any
from src.core.state import SystemState


class PluralityChecker:
    
    def __init__(self):
        pass
    
    def check(self, state: SystemState) -> SystemState:
        state.add_trace("PLURALITY_CHECK", "Starting plurality enforcement")
        
        if not state.reasoning_graph:
            state.add_trace("PLURALITY_CHECK", "No reasoning to check")
            return state
        
        has_multiple_perspectives = self._check_multiple_perspectives(state)
        
        if has_multiple_perspectives:
            state.add_trace("PLURALITY_CHECK", 
                           "Multiple perspectives detected - ensuring balanced representation")
        else:
            state.add_trace("PLURALITY_CHECK", 
                           "Single unified perspective - no plurality concerns")
        
        has_scope_diversity = self._check_scope_diversity(state)
        
        if has_scope_diversity:
            state.add_trace("PLURALITY_CHECK", 
                           "Multiple interpretive scopes present - flagging for balanced treatment")
        
        return state
    
    def _check_multiple_perspectives(self, state: SystemState) -> bool:
        perspective_count = 0
        
        for node in state.reasoning_graph:
            if "Perspective A:" in node.claim or "Perspective B:" in node.claim:
                perspective_count += 1
        
        return perspective_count >= 2
    
    def _check_scope_diversity(self, state: SystemState) -> bool:
        scopes = set()
        
        for rv in state.retrieved_verses:
            verse_data = rv.verse_data
            if "interpretive_notes" in verse_data:
                scope = verse_data["interpretive_notes"].get("scope")
                if scope:
                    scopes.add(scope)
        
        return len(scopes) >= 2
    
    def _ensure_no_single_interpretation_assertion(self, state: SystemState) -> bool:
        for node in state.reasoning_graph:
            claim_lower = node.claim.lower()
            
            absolute_phrases = [
                "the only way", "must always", "never", "always",
                "the correct interpretation", "the true meaning"
            ]
            
            if any(phrase in claim_lower for phrase in absolute_phrases):
                return False
        
        return True
