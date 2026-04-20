from typing import List, Dict, Any, Tuple


def normalize_text(text: str) -> str:
    return text.lower().strip()


def calculate_relevance_score(query: str, verse: Dict[str, Any]) -> float:
    query_normalized = normalize_text(query)
    query_words = set(query_normalized.split())
    
    score = 0.0
    
    theme_weight = 3.0
    for theme in verse.get("themes", []):
        theme_normalized = normalize_text(theme)
        theme_words = set(theme_normalized.replace("_", " ").split())
        
        if theme_normalized in query_normalized:
            score += theme_weight * 2
        else:
            common_words = query_words.intersection(theme_words)
            score += len(common_words) * theme_weight
    
    keyword_weight = 2.0
    for keyword in verse.get("keywords", []):
        keyword_normalized = normalize_text(keyword)
        if keyword_normalized in query_normalized:
            score += keyword_weight * 2
        else:
            keyword_words = set(keyword_normalized.replace("-", " ").split())
            common_words = query_words.intersection(keyword_words)
            score += len(common_words) * keyword_weight
    
    translation_weight = 1.0
    translation_normalized = normalize_text(verse.get("translation_english", ""))
    translation_words = set(translation_normalized.split())
    common_words = query_words.intersection(translation_words)
    score += len(common_words) * translation_weight
    
    return score


def select_verse(query: str, corpus: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not corpus:
        raise ValueError("Corpus is empty")
    
    verse_scores = []
    for verse in corpus:
        score = calculate_relevance_score(query, verse)
        verse_scores.append((verse, score))
    
    verse_scores.sort(key=lambda x: x[1], reverse=True)
    
    best_verse, best_score = verse_scores[0]
    
    return best_verse
