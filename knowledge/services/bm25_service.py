"""
BM25 Service for keyword search in RAG system.
Sprint 8 - RAG 2.0 implementation.
"""

import logging
import pickle
import re
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from django.conf import settings
from rank_bm25 import BM25Okapi
from supabase import Client, create_client

logger = logging.getLogger(__name__)


class BM25Service:
    """
    BM25 keyword search service for hybrid retrieval.

    Provides traditional keyword-based search to complement vector semantic search.
    Uses BM25Okapi algorithm (Best Match 25 with Okapi BM25 weighting).
    """

    # Polish stopwords for better keyword matching
    POLISH_STOPWORDS = {
        "i",
        "w",
        "z",
        "na",
        "do",
        "o",
        "a",
        "po",
        "to",
        "od",
        "za",
        "dla",
        "przez",
        "pod",
        "przy",
        "co",
        "oraz",
        "jako",
        "jak",
        "je",
        "lub",
        "jest",
        "są",
        "były",
        "była",
        "był",
        "być",
        "te",
        "ta",
        "ten",
        "tym",
        "czy",
        "nie",
        "się",
        "tylko",
        "może",
        "można",
        "także",
        "również",
    }

    def __init__(self, index_path: str = None):
        """
        Initialize BM25Service.

        Args:
            index_path: Path to serialized BM25 index file.
                       Defaults to media/bm25_index.pkl
        """
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Set default index path
        if index_path is None:
            media_dir = Path(settings.MEDIA_ROOT)
            media_dir.mkdir(exist_ok=True)
            index_path = str(media_dir / "bm25_index.pkl")

        self.index_path = index_path
        self.index: Optional[BM25Okapi] = None
        self.chunk_ids: List[str] = []
        self.corpus_tokenized: List[List[str]] = []

        # Try to load existing index
        self._load_index()

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize Polish text for BM25 indexing.

        Args:
            text: Input text

        Returns:
            List of tokens (lowercase, no stopwords)
        """
        # Lowercase
        text = text.lower()

        # Split on whitespace and punctuation (keep alphanumeric + Polish chars)
        tokens = re.findall(r"[a-ząćęłńóśźż0-9]+", text)

        # Remove stopwords and very short tokens
        tokens = [
            token
            for token in tokens
            if token not in self.POLISH_STOPWORDS and len(token) > 2
        ]

        return tokens

    def build_index(self) -> dict:
        """
        Build BM25 index from all document chunks in Supabase.

        Returns:
            Statistics about the built index
        """
        logger.info("Building BM25 index from Supabase...")

        # Fetch all chunks from Supabase
        response = (
            self.supabase.table("vector_embeddings").select("id, content").execute()
        )
        chunks = response.data

        if not chunks:
            logger.warning("No chunks found in Supabase. BM25 index not built.")
            return {"total_chunks": 0, "avg_tokens_per_chunk": 0}

        logger.info(f"Fetched {len(chunks)} chunks from Supabase")

        # Tokenize all chunks
        self.chunk_ids = []
        self.corpus_tokenized = []

        for chunk in chunks:
            chunk_id = str(chunk["id"])
            content = chunk["content"]

            tokens = self._tokenize(content)

            self.chunk_ids.append(chunk_id)
            self.corpus_tokenized.append(tokens)

        # Build BM25 index
        self.index = BM25Okapi(self.corpus_tokenized)

        # Calculate statistics
        total_tokens = sum(len(tokens) for tokens in self.corpus_tokenized)
        avg_tokens = (
            total_tokens / len(self.corpus_tokenized) if self.corpus_tokenized else 0
        )

        stats = {
            "total_chunks": len(self.chunk_ids),
            "avg_tokens_per_chunk": round(avg_tokens, 2),
            "total_tokens": total_tokens,
        }

        logger.info(f"BM25 index built: {stats}")

        return stats

    def save_index(self) -> bool:
        """
        Serialize and save BM25 index to disk.

        Returns:
            True if successful, False otherwise
        """
        if self.index is None:
            logger.error("No index to save. Build index first.")
            return False

        try:
            index_data = {
                "index": self.index,
                "chunk_ids": self.chunk_ids,
                "corpus_tokenized": self.corpus_tokenized,
            }

            with open(self.index_path, "wb") as f:
                pickle.dump(index_data, f)

            logger.info(f"BM25 index saved to {self.index_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save BM25 index: {e}")
            return False

    def _load_index(self) -> bool:
        """
        Load BM25 index from disk.

        Returns:
            True if successful, False otherwise
        """
        try:
            if not Path(self.index_path).exists():
                logger.info("No existing BM25 index found. Will build on first search.")
                return False

            with open(self.index_path, "rb") as f:
                index_data = pickle.load(f)

            self.index = index_data["index"]
            self.chunk_ids = index_data["chunk_ids"]
            self.corpus_tokenized = index_data["corpus_tokenized"]

            logger.info(
                f"BM25 index loaded from {self.index_path} ({len(self.chunk_ids)} chunks)"
            )
            return True

        except Exception as e:
            logger.warning(f"Failed to load BM25 index: {e}")
            return False

    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """
        Search for relevant chunks using BM25 keyword matching.

        Args:
            query: Search query
            top_k: Number of top results to return

        Returns:
            List of (chunk_id, bm25_score) tuples, sorted by score descending
        """
        # Build index if not already built
        if self.index is None:
            logger.info("BM25 index not found. Building index...")
            self.build_index()
            self.save_index()

        # Tokenize query
        query_tokens = self._tokenize(query)

        if not query_tokens:
            logger.warning(f"Query tokenized to empty list: '{query}'")
            return []

        # Get BM25 scores for all documents
        scores = self.index.get_scores(query_tokens)

        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        # Build results with chunk IDs and scores
        results = [
            (self.chunk_ids[idx], float(scores[idx]))
            for idx in top_indices
            if scores[idx] > 0  # Only include non-zero scores
        ]

        logger.info(f"BM25 search: '{query}' -> {len(results)} results (top_k={top_k})")

        return results

    def rebuild_index(self) -> dict:
        """
        Rebuild and save BM25 index from scratch.

        Returns:
            Statistics about the rebuilt index
        """
        logger.info("Rebuilding BM25 index...")
        stats = self.build_index()
        self.save_index()
        logger.info("BM25 index rebuilt successfully")
        return stats
