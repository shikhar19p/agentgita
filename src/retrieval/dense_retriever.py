from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class DenseRetriever:
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.corpus_embeddings = None
        self.corpus = None
    
    def index_corpus(self, corpus: List[Dict[str, Any]]):
        self.corpus = corpus
        
        texts_to_embed = []
        for verse in corpus:
            text = self._create_searchable_text(verse)
            texts_to_embed.append(text)
        
        self.corpus_embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True)
    
    def _create_searchable_text(self, verse: Dict[str, Any]) -> str:
        parts = []
        
        parts.append(verse.get("translation_english", ""))
        
        themes = verse.get("themes", [])
        if themes:
            parts.append(" ".join(themes))
        
        keywords = verse.get("keywords", [])
        if keywords:
            parts.append(" ".join(keywords))
        
        if "interpretive_notes" in verse:
            notes = verse["interpretive_notes"]
            if "core_teaching" in notes:
                parts.append(notes["core_teaching"])
        
        return " ".join(parts)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if self.corpus_embeddings is None:
            raise ValueError("Corpus not indexed. Call index_corpus() first.")
        
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        similarities = cosine_similarity(query_embedding, self.corpus_embeddings)[0]
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            verse_id = self.corpus[idx]["id"]
            score = float(similarities[idx])
            results.append((verse_id, score))
        
        return results
