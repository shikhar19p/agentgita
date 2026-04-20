import json
from pathlib import Path
from typing import List, Dict, Any


def load_corpus(corpus_path: str = None) -> List[Dict[str, Any]]:
    if corpus_path is None:
        corpus_path = Path(__file__).parent.parent / "data" / "corpus.json"
    else:
        corpus_path = Path(corpus_path)
    
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus file not found: {corpus_path}")
    
    with open(corpus_path, 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    if not isinstance(corpus, list):
        raise ValueError("Corpus must be a list of verse entries")
    
    for entry in corpus:
        required_fields = ["id", "chapter", "verses", "sloka_sanskrit_iast", 
                          "translation_english", "themes", "keywords"]
        for field in required_fields:
            if field not in entry:
                raise ValueError(f"Missing required field '{field}' in entry {entry.get('id', 'unknown')}")
    
    return corpus


def get_verse_by_id(corpus: List[Dict[str, Any]], verse_id: str) -> Dict[str, Any]:
    for verse in corpus:
        if verse["id"] == verse_id:
            return verse
    return None
