import os
import time
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_MAX_RETRIES = 3
_BACKOFF_BASE = 2.0   # seconds


class GeminiClient:

    def __init__(self,
                 model: str = "gemini-1.5-pro",
                 temperature: float = 0.3,
                 max_tokens: int = 1500):
        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment. "
                "Please set it in .env file or environment variables."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            },
        )

    def generate_interpretation(self,
                                query: str,
                                primary_verse: Dict[str, Any],
                                supporting_verses: Optional[List[Dict[str, Any]]] = None,
                                reasoning_context: Optional[str] = None) -> str:
        prompt = self._build_system_prompt() + "\n\n" + self._build_user_prompt(
            query, primary_verse, supporting_verses or [], reasoning_context
        )

        last_error = ""
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self.model.generate_content(prompt)
                if response.text:
                    return response.text.strip()
                return "[Error: No response generated]"
            except Exception as e:
                last_error = str(e)
                if attempt < _MAX_RETRIES:
                    wait = _BACKOFF_BASE ** attempt
                    time.sleep(wait)

        return f"[Error generating interpretation after {_MAX_RETRIES} attempts: {last_error}]"

    # ------------------------------------------------------------------

    @staticmethod
    def _build_system_prompt() -> str:
        return """You are an interpreter for the Bhagavad Gita, a sacred Hindu scripture. Your role is to apply the teachings of specific verses to user questions with utmost respect and precision.

CRITICAL RULES (ABSOLUTE — NO EXCEPTIONS):

1. GROUNDING REQUIREMENT
   - Use ONLY the provided verse text.
   - Do NOT invent, paraphrase, or reference verses not provided.
   - Every statement must be traceable to the verse text.

2. CITATION REQUIREMENT
   - Reference the verse ID (e.g., BG 2.47) when making claims.
   - Do not make uncited claims.

3. INTERPRETATION BOUNDARIES
   - Stay strictly within the bounds of what the verse teaches.
   - Do NOT add modern psychology unless directly aligned with the text.
   - Do NOT add motivational language or self-help advice.

4. AMBIGUITY HANDLING
   - Acknowledge ambiguity where it exists.
   - Do NOT force a single interpretation if multiple are valid.
   - Use phrases like "the verse suggests" or "one interpretation is".

5. RESPECT AND TONE
   - Maintain a respectful, scholarly tone.
   - No casual language, emojis, or oversimplification.

6. PLURALITY PRESERVATION
   - If multiple valid interpretations exist, present them.
   - Avoid absolute language ("the only way", "must always").

Format: direct interpretation without preamble. Begin immediately with the application of the verse to the question."""

    @staticmethod
    def _build_user_prompt(query: str,
                           primary_verse: Dict[str, Any],
                           supporting_verses: List[Dict[str, Any]],
                           reasoning_context: Optional[str]) -> str:
        verse_ref = _format_verse_ref(primary_verse)
        parts = [
            f"User Question: {query}",
            "",
            f"Primary Verse — Bhagavad Gita {verse_ref}:",
            "",
            f"Sanskrit (IAST): {primary_verse.get('sloka_sanskrit_iast', '')}",
            "",
            f"English Translation: {primary_verse.get('translation_english', '')}",
            "",
        ]

        teaching = primary_verse.get("interpretive_notes", {}).get("core_teaching", "")
        if teaching:
            parts += [f"Core Teaching: {teaching}", ""]

        if supporting_verses:
            parts.append("Supporting Context from Additional Verses:")
            parts.append("")
            for sv in supporting_verses[:2]:
                parts.append(f"BG {_format_verse_ref(sv)}: {sv.get('translation_english', '')}")
            parts.append("")

        if reasoning_context:
            parts += ["Reasoning Context:", reasoning_context, ""]

        parts += [
            "Task: Provide a grounded interpretation of how this verse applies to the user's question.",
            "Stay strictly within what the verse explicitly teaches. Cite the verse ID when making claims.",
            "If the verse doesn't directly address the question, acknowledge this limitation.",
        ]
        return "\n".join(parts)


def _format_verse_ref(verse: Dict[str, Any]) -> str:
    chapter = verse.get("chapter", "?")
    verses = verse.get("verses", [])
    if not verses:
        return str(chapter)
    if len(verses) == 1:
        return f"{chapter}.{verses[0]}"
    return f"{chapter}.{verses[0]}-{verses[-1]}"
