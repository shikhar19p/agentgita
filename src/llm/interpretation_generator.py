from typing import Dict, Any, List
from src.core.state import SystemState
from src.llm.openai_client import OpenAIClient


class InterpretationGenerator:
    
    def __init__(self, openai_client: OpenAIClient):
        self.client = openai_client
    
    def generate(self, state: SystemState) -> SystemState:
        state.add_trace("INTERPRETATION_GENERATION", "Starting LLM-based interpretation")
        
        if not state.retrieved_verses:
            state.add_trace("INTERPRETATION_GENERATION", "No verses to interpret")
            return state
        
        primary_verse = state.retrieved_verses[0].verse_data
        
        supporting_verses = []
        if len(state.retrieved_verses) > 1:
            supporting_verses = [rv.verse_data for rv in state.retrieved_verses[1:3]]
        
        reasoning_context = self._extract_reasoning_context(state)
        
        interpretation = self.client.generate_interpretation(
            query=state.query,
            primary_verse=primary_verse,
            supporting_verses=supporting_verses,
            reasoning_context=reasoning_context
        )
        
        if interpretation.startswith("[Error"):
            state.add_trace("INTERPRETATION_GENERATION", f"LLM error: {interpretation}")
        else:
            state.add_trace("INTERPRETATION_GENERATION", 
                           f"Generated interpretation ({len(interpretation)} chars)")
            
            for node in state.reasoning_graph:
                if "Primary teaching:" in node.claim or "Interpretation" in node.claim:
                    node.claim = interpretation
                    break
            else:
                from src.core.state import ReasoningNode
                interpretation_node = ReasoningNode(
                    claim=interpretation,
                    supporting_verses=[state.retrieved_verses[0].verse_id],
                    grounded=True,
                    confidence=0.85
                )
                state.reasoning_graph.append(interpretation_node)
        
        return state
    
    def _extract_reasoning_context(self, state: SystemState) -> str:
        context_parts = []
        
        if state.contradictions:
            context_parts.append(f"Note: {len(state.contradictions)} thematic tensions detected:")
            for contradiction in state.contradictions[:2]:
                context_parts.append(f"- {contradiction.description}")
        
        if len(state.retrieved_verses) > 1:
            scopes = set()
            for rv in state.retrieved_verses[:3]:
                if "interpretive_notes" in rv.verse_data:
                    scope = rv.verse_data["interpretive_notes"].get("scope")
                    if scope:
                        scopes.add(scope)
            
            if len(scopes) > 1:
                context_parts.append(f"Multiple interpretive scopes present: {', '.join(scopes)}")
        
        return "\n".join(context_parts) if context_parts else None
