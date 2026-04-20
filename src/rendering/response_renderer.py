from typing import List, Dict, Any
from src.core.state import SystemState


class ResponseRenderer:
    
    def __init__(self):
        pass
    
    def render(self, state: SystemState) -> SystemState:
        state.add_trace("RESPONSE_RENDERING", "Starting response rendering")
        
        if state.should_refuse():
            state.add_trace("RESPONSE_RENDERING", "Skipping - refusal required")
            return state
        
        if not state.retrieved_verses:
            state.add_trace("RESPONSE_RENDERING", "No verses to render")
            return state
        
        primary_verse = state.retrieved_verses[0]
        
        response_parts = []
        
        response_parts.append("User Query:")
        response_parts.append(state.query)
        response_parts.append("")
        
        verse_ref = self._format_verse_reference(primary_verse.verse_data)
        response_parts.append(f"Bhagavad Gita {verse_ref} (English Translation)")
        response_parts.append("")
        
        response_parts.append("Sanskrit (Transliteration):")
        response_parts.append(primary_verse.verse_data.get("sloka_sanskrit_iast", ""))
        response_parts.append("")
        
        response_parts.append("English Translation:")
        response_parts.append(primary_verse.verse_data.get("translation_english", ""))
        response_parts.append("")
        
        meaning = self._extract_meaning(primary_verse.verse_data)
        response_parts.append("Meaning of the Śloka:")
        response_parts.append(meaning)
        response_parts.append("")
        
        interpretation = self._construct_interpretation(state)
        response_parts.append("Interpretation (Applied to the User's Question):")
        response_parts.append(interpretation)
        response_parts.append("")
        
        supportive_guidance = self._extract_supportive_guidance(primary_verse.verse_data)
        if supportive_guidance:
            response_parts.append("(Optional) Supportive Guidance:")
            response_parts.append(supportive_guidance)
            response_parts.append("")
        
        visual_context = self._extract_visual_context(primary_verse.verse_data)
        if visual_context:
            response_parts.append("(Optional) Visual Context:")
            response_parts.append(visual_context)
            response_parts.append("")
        
        state.final_response = "\n".join(response_parts)
        state.add_trace("RESPONSE_RENDERING", "Response rendered successfully")
        
        return state
    
    def _format_verse_reference(self, verse_data: Dict[str, Any]) -> str:
        chapter = verse_data["chapter"]
        verses = verse_data["verses"]
        
        if len(verses) == 1:
            return f"{chapter}.{verses[0]}"
        else:
            verse_range = "-".join(str(v) for v in verses)
            return f"{chapter}.{verse_range}"
    
    def _extract_meaning(self, verse_data: Dict[str, Any]) -> str:
        if "interpretive_notes" in verse_data:
            core_teaching = verse_data["interpretive_notes"].get("core_teaching", "")
            if core_teaching:
                return core_teaching
        
        return verse_data.get("translation_english", "")
    
    def _construct_interpretation(self, state: SystemState) -> str:
        if not state.reasoning_graph:
            return "[Interpretation requires LLM integration - placeholder]"
        
        for node in state.reasoning_graph:
            if node.grounded and node.claim:
                if not any(prefix in node.claim for prefix in [
                    "Perspective A:", "Perspective B:", "Synthesis:", 
                    "Primary teaching:", "Supporting context:"
                ]):
                    return node.claim
        
        interpretation_parts = []
        
        for node in state.reasoning_graph:
            if node.grounded:
                claim = node.claim
                
                if "Primary teaching:" in claim:
                    claim = claim.replace("Primary teaching:", "").strip()
                    interpretation_parts.append(claim)
                elif "Perspective A:" in claim or "Perspective B:" in claim:
                    interpretation_parts.append(claim)
                elif "Synthesis:" in claim:
                    claim = claim.replace("Synthesis:", "").strip()
                    interpretation_parts.append(claim)
        
        if interpretation_parts:
            return "\n\n".join(interpretation_parts)
        else:
            return "[Interpretation requires LLM integration - placeholder]"
    
    def _extract_supportive_guidance(self, verse_data: Dict[str, Any]) -> str:
        practices = verse_data.get("supportive_practices", [])
        
        if practices:
            if len(practices) <= 3:
                return ", ".join(practices)
            else:
                return ", ".join(practices[:3])
        
        return ""
    
    def _extract_visual_context(self, verse_data: Dict[str, Any]) -> str:
        image_tags = verse_data.get("image_tags", [])
        
        if image_tags:
            if len(image_tags) == 1:
                return f"Image prompt: {image_tags[0]}"
            else:
                prompts = [f"{i+1}. {tag}" for i, tag in enumerate(image_tags[:2])]
                return "Image prompts:\n" + "\n".join(prompts)
        
        return ""
