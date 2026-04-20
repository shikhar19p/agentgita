import os
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


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
        
        generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config
        )
    
    def generate_interpretation(self,
                               query: str,
                               primary_verse: Dict[str, Any],
                               supporting_verses: List[Dict[str, Any]] = None,
                               reasoning_context: str = None) -> str:
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            query, 
            primary_verse, 
            supporting_verses,
            reasoning_context
        )
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                return response.text.strip()
            else:
                return "[Error: No response generated]"
            
        except Exception as e:
            return f"[Error generating interpretation: {str(e)}]"
    
    def _build_system_prompt(self) -> str:
        return """You are an interpreter for the Bhagavad Gita, a sacred Hindu scripture. Your role is to apply the teachings of specific verses to user questions with utmost respect and precision.

CRITICAL RULES (ABSOLUTE - NO EXCEPTIONS):

1. GROUNDING REQUIREMENT
   - Use ONLY the provided verse text
   - Do NOT invent, paraphrase, or reference verses not provided
   - Do NOT make claims beyond what the verse explicitly states
   - Every statement must be traceable to the verse text

2. CITATION REQUIREMENT
   - Reference the verse ID (e.g., BG 2.47) when making claims
   - If using supporting verses, cite them explicitly
   - Do not make uncited claims

3. INTERPRETATION BOUNDARIES
   - Stay strictly within the bounds of what the verse teaches
   - Do NOT add modern psychology unless directly aligned with the text
   - Do NOT add motivational language or self-help advice
   - Do NOT preach or moralize

4. AMBIGUITY HANDLING
   - Acknowledge ambiguity where it exists in the text
   - Do NOT force a single interpretation if multiple are valid
   - Use phrases like "the verse suggests" or "one interpretation is"

5. RESPECT AND TONE
   - Maintain a respectful, scholarly tone
   - No casual language or oversimplification
   - No emojis or informal expressions
   - Treat the text as sacred

6. PLURALITY PRESERVATION
   - If multiple valid interpretations exist, present them
   - Do NOT use absolute language ("the only way", "must always")
   - Acknowledge different traditional perspectives where relevant

Your interpretation should be:
- Grounded in the verse text
- Respectful and non-preachy
- Contextually applied to the user's question
- Free from overreach or invention
- Clear about what the verse says vs. what it implies

Format your response as a direct interpretation without preamble. Begin immediately with the application of the verse to the question."""

    def _build_user_prompt(self,
                          query: str,
                          primary_verse: Dict[str, Any],
                          supporting_verses: List[Dict[str, Any]] = None,
                          reasoning_context: str = None) -> str:
        prompt_parts = []
        
        prompt_parts.append(f"User Question: {query}")
        prompt_parts.append("")
        
        verse_ref = self._format_verse_reference(primary_verse)
        prompt_parts.append(f"Primary Verse - Bhagavad Gita {verse_ref}:")
        prompt_parts.append("")
        
        prompt_parts.append(f"Sanskrit (IAST): {primary_verse.get('sloka_sanskrit_iast', '')}")
        prompt_parts.append("")
        
        prompt_parts.append(f"English Translation: {primary_verse.get('translation_english', '')}")
        prompt_parts.append("")
        
        if "interpretive_notes" in primary_verse:
            notes = primary_verse["interpretive_notes"]
            if "core_teaching" in notes:
                prompt_parts.append(f"Core Teaching: {notes['core_teaching']}")
                prompt_parts.append("")
        
        if supporting_verses:
            prompt_parts.append("Supporting Context from Additional Verses:")
            prompt_parts.append("")
            for sv in supporting_verses[:2]:
                sv_ref = self._format_verse_reference(sv)
                prompt_parts.append(f"BG {sv_ref}: {sv.get('translation_english', '')}")
            prompt_parts.append("")
        
        if reasoning_context:
            prompt_parts.append("Reasoning Context:")
            prompt_parts.append(reasoning_context)
            prompt_parts.append("")
        
        prompt_parts.append("Task: Provide a grounded interpretation of how this verse applies to the user's question.")
        prompt_parts.append("Stay strictly within what the verse explicitly teaches. Cite the verse ID when making claims.")
        prompt_parts.append("If the verse doesn't directly address the question, acknowledge this limitation.")
        
        return "\n".join(prompt_parts)
    
    def _format_verse_reference(self, verse: Dict[str, Any]) -> str:
        chapter = verse["chapter"]
        verses = verse["verses"]
        
        if len(verses) == 1:
            return f"{chapter}.{verses[0]}"
        else:
            verse_range = "-".join(str(v) for v in verses)
            return f"{chapter}.{verse_range}"
