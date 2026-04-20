from typing import List, Dict, Any
from src.core.state import SystemState, ReasoningNode


class DialecticalReasoner:
    
    def __init__(self):
        pass
    
    def reason(self, state: SystemState) -> SystemState:
        state.add_trace("DIALECTICAL_REASONING", "Starting dialectical reasoning")
        
        if not state.retrieved_verses:
            state.add_trace("DIALECTICAL_REASONING", "No verses to reason from")
            return state
        
        if state.contradictions:
            state.add_trace("DIALECTICAL_REASONING", 
                           f"Processing {len(state.contradictions)} contradictions")
            reasoning_nodes = self._construct_dialectical_reasoning(
                state.retrieved_verses, 
                state.contradictions,
                state.query
            )
        else:
            state.add_trace("DIALECTICAL_REASONING", "No contradictions - constructing unified reasoning")
            reasoning_nodes = self._construct_unified_reasoning(
                state.retrieved_verses,
                state.query
            )
        
        state.reasoning_graph.extend(reasoning_nodes)
        
        state.add_trace("DIALECTICAL_REASONING", 
                       f"Generated {len(reasoning_nodes)} reasoning nodes")
        
        return state
    
    def _construct_dialectical_reasoning(self, 
                                        retrieved_verses: List[Any],
                                        contradictions: List[Any],
                                        query: str) -> List[ReasoningNode]:
        nodes = []
        
        for contradiction in contradictions:
            involved_verses = [
                rv for rv in retrieved_verses 
                if rv.verse_id in contradiction.verse_ids
            ]
            
            if len(involved_verses) >= 2:
                perspective_a = self._extract_perspective(involved_verses[0])
                perspective_b = self._extract_perspective(involved_verses[1])
                
                node_a = ReasoningNode(
                    claim=f"Perspective A: {perspective_a}",
                    supporting_verses=[involved_verses[0].verse_id],
                    grounded=True,
                    confidence=0.8
                )
                nodes.append(node_a)
                
                node_b = ReasoningNode(
                    claim=f"Perspective B: {perspective_b}",
                    supporting_verses=[involved_verses[1].verse_id],
                    grounded=True,
                    confidence=0.8
                )
                nodes.append(node_b)
                
                synthesis = self._synthesize_perspectives(
                    perspective_a, 
                    perspective_b,
                    contradiction.description
                )
                
                synthesis_node = ReasoningNode(
                    claim=f"Synthesis: {synthesis}",
                    supporting_verses=[v.verse_id for v in involved_verses],
                    grounded=True,
                    confidence=0.7
                )
                nodes.append(synthesis_node)
        
        return nodes
    
    def _construct_unified_reasoning(self, 
                                    retrieved_verses: List[Any],
                                    query: str) -> List[ReasoningNode]:
        nodes = []
        
        if not retrieved_verses:
            return nodes
        
        primary_verse = retrieved_verses[0]
        primary_teaching = self._extract_core_teaching(primary_verse)
        
        primary_node = ReasoningNode(
            claim=f"Primary teaching: {primary_teaching}",
            supporting_verses=[primary_verse.verse_id],
            grounded=True,
            confidence=0.9
        )
        nodes.append(primary_node)
        
        if len(retrieved_verses) > 1:
            supporting_teachings = []
            supporting_verse_ids = []
            
            for rv in retrieved_verses[1:3]:
                teaching = self._extract_core_teaching(rv)
                supporting_teachings.append(teaching)
                supporting_verse_ids.append(rv.verse_id)
            
            if supporting_teachings:
                support_claim = f"Supporting context: {'; '.join(supporting_teachings)}"
                support_node = ReasoningNode(
                    claim=support_claim,
                    supporting_verses=supporting_verse_ids,
                    grounded=True,
                    confidence=0.75
                )
                nodes.append(support_node)
        
        return nodes
    
    def _extract_perspective(self, retrieved_verse: Any) -> str:
        verse_data = retrieved_verse.verse_data
        
        if "interpretive_notes" in verse_data:
            core_teaching = verse_data["interpretive_notes"].get("core_teaching", "")
            if core_teaching:
                return core_teaching
        
        translation = verse_data.get("translation_english", "")
        if len(translation) > 150:
            return translation[:150] + "..."
        return translation
    
    def _extract_core_teaching(self, retrieved_verse: Any) -> str:
        verse_data = retrieved_verse.verse_data
        
        if "interpretive_notes" in verse_data:
            core_teaching = verse_data["interpretive_notes"].get("core_teaching", "")
            if core_teaching:
                return core_teaching
        
        translation = verse_data.get("translation_english", "")
        if len(translation) > 100:
            return translation[:100] + "..."
        return translation
    
    def _synthesize_perspectives(self, 
                                 perspective_a: str, 
                                 perspective_b: str,
                                 tension_description: str) -> str:
        synthesis_templates = {
            "action": "Both perspectives address different aspects of action: one emphasizes engagement, the other emphasizes detachment. They are complementary rather than contradictory.",
            "devotion": "These verses present different paths (jnana and bhakti) which the Gita treats as complementary approaches to the same truth.",
            "duty": "The tension between duty and compassion is resolved through understanding one's svadharma in context.",
            "effort": "Divine will and self-effort are not opposed; effort is the means through which divine will manifests."
        }
        
        for key, template in synthesis_templates.items():
            if key in tension_description.lower():
                return template
        
        return "These perspectives represent different dimensions of the same teaching, to be understood contextually."
