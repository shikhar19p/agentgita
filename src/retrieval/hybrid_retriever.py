from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from src.retrieval.chroma_retriever import ChromaRetriever
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

        self.dense_retriever = ChromaRetriever()
        self.sparse_retriever = SparseRetriever()
        self.corpus: Optional[List[Dict[str, Any]]] = None
        self.corpus_index: Dict[str, Dict[str, Any]] = {}

    def index_corpus(self, corpus: List[Dict[str, Any]]):
        self.corpus = corpus
        for verse in corpus:
            self.corpus_index[verse["id"]] = verse
        self.dense_retriever.index_corpus(corpus)
        self.sparse_retriever.index_corpus(corpus)

    def retrieve(self, state: SystemState, query_override: Optional[str] = None) -> SystemState:
        state.add_trace("HYBRID_RETRIEVAL", "Starting hybrid retrieval")

        query = query_override or state.active_query

        dense_results = self.dense_retriever.retrieve(query, top_k=self.top_k * 2)
        state.add_trace("HYBRID_RETRIEVAL", f"Dense retrieval: {len(dense_results)} results")

        sparse_results = self.sparse_retriever.retrieve(query, top_k=self.top_k * 2)
        state.add_trace("HYBRID_RETRIEVAL", f"Sparse retrieval: {len(sparse_results)} results")

        fused_results = self._reciprocal_rank_fusion(dense_results, sparse_results)
        top_results = fused_results[:self.top_k]

        if self.context_expansion:
            expanded_results = self._expand_context(top_results)
            state.add_trace("HYBRID_RETRIEVAL", f"Context expansion: {len(expanded_results)} verses")
        else:
            expanded_results = top_results

        # Clear prior results on retry so we don't accumulate duplicates
        state.retrieved_verses.clear()

        seen_ids = set()
        for verse_id, score in expanded_results:
            if verse_id in seen_ids:
                continue
            seen_ids.add(verse_id)
            verse_data = self.corpus_index[verse_id]
            state.retrieved_verses.append(RetrievedVerse(
                verse_id=verse_id,
                verse_data=verse_data,
                relevance_score=score,
                retrieval_method="hybrid",
            ))

        # Track retrieval confidence as avg score of top-k (before expansion)
        if top_results:
            state.retrieval_confidence = sum(s for _, s in top_results) / len(top_results)
        else:
            state.retrieval_confidence = 0.0

        state.add_trace(
            "HYBRID_RETRIEVAL",
            f"Final: {len(state.retrieved_verses)} verses | confidence={state.retrieval_confidence:.3f}"
        )
        state.mark_step("retrieval")
        return state

    def _reciprocal_rank_fusion(self,
                                dense_results: List[Tuple[str, float]],
                                sparse_results: List[Tuple[str, float]],
                                k: int = 60) -> List[Tuple[str, float]]:
        scores: Dict[str, float] = defaultdict(float)
        for rank, (verse_id, _) in enumerate(dense_results, start=1):
            scores[verse_id] += self.dense_weight * (1.0 / (k + rank))
        for rank, (verse_id, _) in enumerate(sparse_results, start=1):
            scores[verse_id] += self.sparse_weight * (1.0 / (k + rank))
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def _expand_context(self, results: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        expanded: Dict[str, float] = {}
        for verse_id, score in results:
            expanded[verse_id] = score

        for verse_id, score in results:
            verse = self.corpus_index[verse_id]
            chapter = verse["chapter"]
            for v_num in verse["verses"]:
                for offset in range(-self.neighbor_verses, self.neighbor_verses + 1):
                    if offset == 0:
                        continue
                    neighbor_id = f"BG_{chapter}_{v_num + offset}"
                    if neighbor_id in self.corpus_index and neighbor_id not in expanded:
                        expanded[neighbor_id] = score * 0.5

        return sorted(expanded.items(), key=lambda x: x[1], reverse=True)
