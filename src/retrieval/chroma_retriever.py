import os
from typing import List, Dict, Any, Tuple

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from sentence_transformers import SentenceTransformer


class ChromaRetriever:
    """Persistent dense retriever backed by ChromaDB. Falls back to in-memory if ChromaDB unavailable."""

    COLLECTION_NAME = "gita_verses"
    PERSIST_DIR = ".chroma_db"

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.corpus: List[Dict[str, Any]] = []
        self._fallback_embeddings = None

        if CHROMA_AVAILABLE:
            self._client = chromadb.PersistentClient(
                path=self.PERSIST_DIR,
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        else:
            self._client = None
            self._collection = None

    def index_corpus(self, corpus: List[Dict[str, Any]]):
        self.corpus = corpus

        if not CHROMA_AVAILABLE:
            self._index_fallback(corpus)
            return

        existing_ids = set(self._collection.get(include=[])["ids"])
        corpus_ids = {v["id"] for v in corpus}

        if existing_ids == corpus_ids:
            return

        if existing_ids:
            self._client.delete_collection(self.COLLECTION_NAME)
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

        texts, ids, metadatas = [], [], []
        for verse in corpus:
            texts.append(self._searchable_text(verse))
            ids.append(verse["id"])
            metadatas.append({
                "chapter": verse["chapter"],
                "themes": ",".join(verse.get("themes", [])),
            })

        embeddings = self.model.encode(texts, convert_to_numpy=True).tolist()
        self._collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if not CHROMA_AVAILABLE:
            return self._retrieve_fallback(query, top_k)

        query_embedding = self.model.encode([query], convert_to_numpy=True).tolist()
        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self._collection.count()),
            include=["distances"],
        )
        ids = results["ids"][0]
        # ChromaDB cosine distance: 0=identical, 2=opposite → convert to similarity
        similarities = [1.0 - d for d in results["distances"][0]]
        return list(zip(ids, similarities))

    # ------------------------------------------------------------------
    # fallback (in-memory numpy) — used when chromadb is not installed
    # ------------------------------------------------------------------

    def _index_fallback(self, corpus: List[Dict[str, Any]]):
        import numpy as np
        texts = [self._searchable_text(v) for v in corpus]
        self._fallback_embeddings = self.model.encode(texts, convert_to_numpy=True)

    def _retrieve_fallback(self, query: str, top_k: int) -> List[Tuple[str, float]]:
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        q_emb = self.model.encode([query], convert_to_numpy=True)
        sims = cosine_similarity(q_emb, self._fallback_embeddings)[0]
        top_idx = np.argsort(sims)[::-1][:top_k]
        return [(self.corpus[i]["id"], float(sims[i])) for i in top_idx]

    @staticmethod
    def _searchable_text(verse: Dict[str, Any]) -> str:
        parts = [verse.get("translation_english", "")]
        parts += verse.get("themes", [])
        parts += verse.get("keywords", [])
        notes = verse.get("interpretive_notes", {})
        if "core_teaching" in notes:
            parts.append(notes["core_teaching"])
        return " ".join(parts)
