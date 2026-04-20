from typing import Dict, Any


def format_verse_reference(verse: Dict[str, Any]) -> str:
    chapter = verse["chapter"]
    verses = verse["verses"]
    
    if len(verses) == 1:
        return f"{chapter}.{verses[0]}"
    else:
        verse_range = "-".join(str(v) for v in verses)
        return f"{chapter}.{verse_range}"


def build_response(query: str, verse: Dict[str, Any]) -> str:
    verse_ref = format_verse_reference(verse)
    
    response_parts = []
    
    response_parts.append(f"User Query:")
    response_parts.append(query)
    response_parts.append("")
    
    response_parts.append(f"Bhagavad Gita {verse_ref} (English Translation)")
    response_parts.append("")
    
    response_parts.append("Sanskrit (Transliteration):")
    response_parts.append(verse["sloka_sanskrit_iast"])
    response_parts.append("")
    
    response_parts.append("Meaning (from the verse):")
    response_parts.append(verse["translation_english"])
    response_parts.append("")
    
    response_parts.append("Interpretation (applied to the user's question):")
    response_parts.append("[To be implemented with LLM integration]")
    response_parts.append("")
    
    return "\n".join(response_parts)
