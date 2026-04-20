from typing import Dict, Any
from src.core.state import SystemState


class ResponseRenderer:

    def render(self, state: SystemState) -> SystemState:
        state.add_trace("RESPONSE_RENDERING", "Starting response rendering")

        if state.should_refuse() or not state.retrieved_verses:
            state.add_trace("RESPONSE_RENDERING", "Skipping — refusal or no verses")
            return state

        primary_verse = state.retrieved_verses[0]
        parts = []

        parts += ["User Query:", state.query, ""]

        verse_ref = self._format_verse_reference(primary_verse.verse_data)
        parts += [f"Bhagavad Gita {verse_ref} (English Translation)", ""]

        parts += [
            "Sanskrit (Transliteration):",
            primary_verse.verse_data.get("sloka_sanskrit_iast", ""),
            "",
        ]

        parts += [
            "English Translation:",
            primary_verse.verse_data.get("translation_english", ""),
            "",
        ]

        parts += ["Meaning of the Śloka:", self._extract_meaning(primary_verse.verse_data), ""]

        parts += [
            "Interpretation (Applied to the User's Question):",
            self._construct_interpretation(state),
            "",
        ]

        guidance = self._extract_supportive_guidance(primary_verse.verse_data)
        if guidance:
            parts += ["(Optional) Supportive Guidance:", guidance, ""]

        visual = self._extract_visual_context(primary_verse.verse_data)
        if visual:
            parts += ["(Optional) Visual Context:", visual, ""]

        state.final_response = "\n".join(parts)
        state.add_trace("RESPONSE_RENDERING", "Response rendered successfully")
        return state

    # ------------------------------------------------------------------

    @staticmethod
    def _format_verse_reference(verse_data: Dict[str, Any]) -> str:
        chapter = verse_data.get("chapter", "?")
        verses = verse_data.get("verses", [])
        if not verses:
            return str(chapter)
        if len(verses) == 1:
            return f"{chapter}.{verses[0]}"
        return f"{chapter}.{verses[0]}-{verses[-1]}"

    @staticmethod
    def _extract_meaning(verse_data: Dict[str, Any]) -> str:
        teaching = verse_data.get("interpretive_notes", {}).get("core_teaching", "")
        return teaching or verse_data.get("translation_english", "")

    @staticmethod
    def _construct_interpretation(state: SystemState) -> str:
        if not state.reasoning_graph:
            return "[Interpretation requires LLM integration]"

        # Prefer an LLM-generated node that doesn't carry a structural prefix
        _structural = ("Perspective A:", "Perspective B:", "Synthesis:", "Primary teaching:", "Supporting context:")
        for node in state.reasoning_graph:
            if node.grounded and node.claim and not any(node.claim.startswith(p) for p in _structural):
                return node.claim

        # Fall back: build from structural nodes
        parts = []
        for node in state.reasoning_graph:
            if not node.grounded:
                continue
            claim = node.claim
            for prefix in _structural:
                if claim.startswith(prefix):
                    stripped = claim[len(prefix):].strip()
                    parts.append(stripped if prefix == "Synthesis:" else claim)
                    break
            else:
                parts.append(claim)

        return "\n\n".join(parts) if parts else "[Interpretation requires LLM integration]"

    @staticmethod
    def _extract_supportive_guidance(verse_data: Dict[str, Any]) -> str:
        practices = verse_data.get("supportive_practices", [])
        return ", ".join(practices[:3]) if practices else ""

    @staticmethod
    def _extract_visual_context(verse_data: Dict[str, Any]) -> str:
        tags = verse_data.get("image_tags", [])
        if not tags:
            return ""
        if len(tags) == 1:
            return f"Image prompt: {tags[0]}"
        prompts = [f"{i+1}. {tag}" for i, tag in enumerate(tags[:2])]
        return "Image prompts:\n" + "\n".join(prompts)
