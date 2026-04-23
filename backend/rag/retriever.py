"""
FAISS Retriever for SlayBot

Loads the persisted FAISS index and chunk metadata, then provides
semantic search with optional metadata filtering.
"""

import json
from pathlib import Path
from typing import Optional

import numpy as np


VECTORSTORE_DIR = Path(__file__).resolve().parent / "vectorstore"


class SlayRetriever:
    """
    FAISS-based semantic retriever for SlayBot.
    
    Uses sentence-transformers for query embedding and FAISS for
    cosine similarity search. Supports metadata filtering by
    objection_tags and emotional_tags.
    """

    def __init__(self):
        self._index = None
        self._metadata = None
        self._model = None
        self._loaded = False

    def _load(self):
        """Lazy-load the FAISS index, metadata, and embedding model."""
        if self._loaded:
            return

        import faiss
        from sentence_transformers import SentenceTransformer

        index_path = VECTORSTORE_DIR / "slay_health.index"
        metadata_path = VECTORSTORE_DIR / "chunks_metadata.json"

        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                "FAISS index not found. Run 'python rag/ingest.py' first."
            )

        # Load index
        self._index = faiss.read_index(str(index_path))

        # Load metadata
        with open(metadata_path, "r") as f:
            self._metadata = json.load(f)

        # Load embedding model (same as used during ingestion)
        self._model = SentenceTransformer("all-MiniLM-L6-v2")
        self._loaded = True

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        objection_filter: Optional[str] = None,
        emotion_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Retrieve the most relevant chunks for a query.

        Args:
            query: Search query string
            top_k: Number of results to return
            objection_filter: Optional objection tag to filter by
            emotion_filter: Optional emotion tag to filter by

        Returns:
            List of dicts with 'text', 'score', and 'metadata'
        """
        self._load()

        # Embed query
        query_vec = self._model.encode(
            [query], normalize_embeddings=True
        ).astype("float32")

        # Search with extra results for post-filtering
        search_k = min(top_k * 3, self._index.ntotal)
        scores, indices = self._index.search(query_vec, search_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            chunk = self._metadata[idx]
            meta = chunk.get("metadata", {})

            # Apply metadata filters
            if objection_filter:
                tags = meta.get("objection_tags", [])
                if objection_filter not in tags and tags:
                    continue

            if emotion_filter:
                tags = meta.get("emotional_tags", [])
                if emotion_filter not in tags and tags:
                    continue

            results.append(
                {
                    "text": chunk["text"],
                    "score": float(score),
                    "metadata": meta,
                }
            )

            if len(results) >= top_k:
                break

        # If filters were too restrictive, fall back to unfiltered
        if len(results) < 2 and (objection_filter or emotion_filter):
            return self.retrieve(query, top_k=top_k)

        return results

    def format_context(self, results: list[dict]) -> str:
        """Format retrieved results into a context string for the LLM."""
        if not results:
            return "No relevant context found."

        parts = []
        for i, r in enumerate(results, 1):
            source = r["metadata"].get("source_url", "unknown")
            page_type = r["metadata"].get("page_type", "unknown")
            parts.append(
                f"[Source {i} — {page_type}]\n{r['text']}"
            )

        return "\n\n---\n\n".join(parts)

    def get_sources(self, results: list[dict]) -> list[str]:
        """Extract unique source URLs from results."""
        sources = []
        seen = set()
        for r in results:
            url = r["metadata"].get("source_url", "")
            if url and url not in seen:
                sources.append(url)
                seen.add(url)
        return sources


# Module-level singleton for reuse across the application
retriever = SlayRetriever()
