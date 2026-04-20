from typing import List, Dict, Any, Tuple
from collections import defaultdict
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.sparse_retriever import SparseRetriever
from src.core.state import SystemState, RetrievedVerse


class HybridRetriever:
    
    def __init__(self, 
                 dense_weight: float = 0.6,
                 sparse_weight: float = 0.4,
                 top_k: int = 5,
                 context_expansion: bool = True,
                 neighbor_verses: int = 2):
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.top_k = top_k
        self.context_expansion = context_expansion
        self.neighbor_verses = neighbor_verses
        
        self.dense_retriever = DenseRetriever()
        self.sparse_retriever = SparseRetriever()
        self.corpus = None
        self.corpus_index = {}
    
    def index_corpus(self, corpus: List[Dict[str, Any]]):
        self.corpus = corpus
        
        for verse in corpus:
            self.corpus_index[verse["id"]] = verse
        
        self.dense_retriever.index_corpus(corpus)
        self.sparse_retriever.index_corpus(corpus)
    
    def retrieve(self, state: SystemState) -> SystemState:
        state.add_trace("HYBRID_RETRIEVAL", "Starting hybrid retrieval")
        
        query = state.query
        
        dense_results = self.dense_retriever.retrieve(query, top_k=self.top_k * 2)
        state.add_trace("HYBRID_RETRIEVAL", f"Dense retrieval: {len(dense_results)} results")
        
        sparse_results = self.sparse_retriever.retrieve(query, top_k=self.top_k * 2)
        state.add_trace("HYBRID_RETRIEVAL", f"Sparse retrieval: {len(sparse_results)} results")
        
        fused_results = self._reciprocal_rank_fusion(dense_results, sparse_results)
        state.add_trace("HYBRID_RETRIEVAL", f"Fused results: {len(fused_results)} verses")
        
        top_results = fused_results[:self.top_k]
        
        if self.context_expansion:
            expanded_results = self._expand_context(top_results)
            state.add_trace("HYBRID_RETRIEVAL", f"Context expansion: {len(expanded_results)} verses")
        else:
            expanded_results = top_results
        
        for verse_id, score in expanded_results:
            verse_data = self.corpus_index[verse_id]
            retrieved_verse = RetrievedVerse(
                verse_id=verse_id,
                verse_data=verse_data,
                relevance_score=score,
                retrieval_method="hybrid"
            )
            state.retrieved_verses.append(retrieved_verse)
        
        state.add_trace("HYBRID_RETRIEVAL", f"Final retrieved: {len(state.retrieved_verses)} verses")
        
        return state
    
    def _reciprocal_rank_fusion(self, 
                                dense_results: List[Tuple[str, float]], 
                                sparse_results: List[Tuple[str, float]],
                                k: int = 60) -> List[Tuple[str, float]]:
        scores = defaultdict(float)
        
        for rank, (verse_id, _) in enumerate(dense_results, start=1):
            scores[verse_id] += self.dense_weight * (1.0 / (k + rank))
        
        for rank, (verse_id, _) in enumerate(sparse_results, start=1):
            scores[verse_id] += self.sparse_weight * (1.0 / (k + rank))
        
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_results
    
    def _expand_context(self, results: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        expanded = {}
        
        for verse_id, score in results:
            expanded[verse_id] = score
        
        for verse_id, score in results:
            verse = self.corpus_index[verse_id]
            chapter = verse["chapter"]
            verses = verse["verses"]
            
            for v_num in verses:
                for offset in range(-self.neighbor_verses, self.neighbor_verses + 1):
                    if offset == 0:
                        continue
                    
                    neighbor_num = v_num + offset
                    neighbor_id = f"BG_{chapter}_{neighbor_num}"
                    
                    if neighbor_id in self.corpus_index and neighbor_id not in expanded:
                        expanded[neighbor_id] = score * 0.5
        
        sorted_expanded = sorted(expanded.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_expanded
