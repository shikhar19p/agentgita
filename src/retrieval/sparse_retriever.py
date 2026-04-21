from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
import re


class SparseRetriever:
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.bm25 = None
        self.corpus = None
        self.tokenized_corpus = []
    
    def index_corpus(self, corpus: List[Dict[str, Any]]):
        self.corpus = corpus
        self.tokenized_corpus = []
        
        for verse in corpus:
            text = self._create_searchable_text(verse)
            tokens = self._tokenize(text)
            self.tokenized_corpus.append(tokens)
        
        self.bm25 = BM25Okapi(self.tokenized_corpus, k1=self.k1, b=self.b)
    
    def _create_searchable_text(self, verse: Dict[str, Any]) -> str:
        parts = []
        parts.append(verse.get("translation_english", ""))
        themes = verse.get("themes", [])
        if themes:
            parts.append(" ".join(themes))
        keywords = verse.get("keywords", [])
        if keywords:
            parts.append(" ".join(keywords))
        core_teaching = verse.get("interpretive_notes", {}).get("core_teaching", "")
        if core_teaching:
            parts.append(core_teaching)
        return " ".join(parts)
    
    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return tokens
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if self.bm25 is None:
            raise ValueError("Corpus not indexed. Call index_corpus() first.")
        
        query_tokens = self._tokenize(query)
        
        scores = self.bm25.get_scores(query_tokens)
        
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            verse_id = self.corpus[idx]["id"]
            score = float(scores[idx])
            results.append((verse_id, score))
        
        return results
