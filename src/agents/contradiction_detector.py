from typing import List, Dict, Any
from src.core.state import SystemState, Contradiction


class ContradictionDetector:
    
    TENSION_INDICATORS = {
        "action_vs_renunciation": {
            "keywords": ["karma", "action", "sannyasa", "renunciation", "akarma"],
            "themes": ["action", "detachment", "non_doership"]
        },
        "devotion_vs_knowledge": {
            "keywords": ["bhakti", "jnana", "devotion", "knowledge"],
            "themes": ["devotion", "wisdom", "knowledge"]
        },
        "duty_vs_compassion": {
            "keywords": ["dharma", "duty", "ahimsa", "compassion"],
            "themes": ["duty", "compassion", "non_violence"]
        },
        "self_effort_vs_divine_will": {
            "keywords": ["daiva", "karma", "effort", "surrender"],
            "themes": ["action", "surrender", "responsibility"]
        }
    }
    
    def __init__(self):
        pass
    
    def detect(self, state: SystemState) -> SystemState:
        state.add_trace("CONTRADICTION_DETECTION", "Starting contradiction detection")
        
        if len(state.retrieved_verses) < 2:
            state.add_trace("CONTRADICTION_DETECTION", "Insufficient verses for contradiction detection")
            return state
        
        contradictions = self._detect_thematic_tensions(state.retrieved_verses)
        
        for contradiction in contradictions:
            state.contradictions.append(contradiction)
        
        state.add_trace("CONTRADICTION_DETECTION", 
                       f"Detected {len(contradictions)} potential contradictions/tensions")
        
        return state
    
    def _detect_thematic_tensions(self, retrieved_verses: List[Any]) -> List[Contradiction]:
        contradictions = []
        
        verse_groups = {}
        for tension_type, indicators in self.TENSION_INDICATORS.items():
            verse_groups[tension_type] = []
            
            for rv in retrieved_verses:
                verse_data = rv.verse_data
                
                keyword_match = any(
                    kw in verse_data.get("keywords", []) 
                    for kw in indicators["keywords"]
                )
                theme_match = any(
                    theme in verse_data.get("themes", []) 
                    for theme in indicators["themes"]
                )
                
                if keyword_match or theme_match:
                    verse_groups[tension_type].append(rv.verse_id)
        
        for tension_type, verse_ids in verse_groups.items():
            if len(verse_ids) >= 2:
                contradiction = Contradiction(
                    verse_ids=verse_ids,
                    description=f"Potential tension: {tension_type.replace('_', ' ')}",
                    severity="moderate"
                )
                contradictions.append(contradiction)
        
        scope_conflicts = self._detect_scope_conflicts(retrieved_verses)
        contradictions.extend(scope_conflicts)
        
        return contradictions
    
    def _detect_scope_conflicts(self, retrieved_verses: List[Any]) -> List[Contradiction]:
        conflicts = []
        
        scopes = {}
        for rv in retrieved_verses:
            verse_data = rv.verse_data
            if "interpretive_notes" in verse_data:
                scope = verse_data["interpretive_notes"].get("scope")
                if scope:
                    if scope not in scopes:
                        scopes[scope] = []
                    scopes[scope].append(rv.verse_id)
        
        if len(scopes) >= 3:
            all_verse_ids = []
            for verse_list in scopes.values():
                all_verse_ids.extend(verse_list)
            
            conflict = Contradiction(
                verse_ids=all_verse_ids,
                description="Multiple interpretive scopes detected (metaphysical, ethical, devotional, etc.)",
                severity="low"
            )
            conflicts.append(conflict)
        
        return conflicts
