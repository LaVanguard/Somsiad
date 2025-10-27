"""
Hybrid Search Service combining BM25 keyword + Vector semantic search.
Sprint 8 - RAG 2.0 implementation.
"""
import logging
from typing import List, Dict, Tuple
from django.conf import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class HybridSearchService:
    """
    Hybrid search combining BM25 (keyword) and vector (semantic) search.

    Uses Reciprocal Rank Fusion (RRF) to combine results from both methods.
    """

    def __init__(self, bm25_service=None, rag_service=None):
        """
        Initialize HybridSearchService.

        Args:
            bm25_service: BM25Service instance (created if None)
            rag_service: RAGService instance (created if None)
        """
        # Import here to avoid circular imports
        from knowledge.services.bm25_service import BM25Service
        from knowledge.services.rag_service import RAGService

        self.bm25_service = bm25_service or BM25Service()
        self.rag_service = rag_service or RAGService()

        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # RRF constant (standard value from literature)
        self.k = 60

    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[Tuple[str, float]],
        vector_results: List[Tuple[str, Dict, float]]
    ) -> List[Tuple[str, float]]:
        """
        Combine BM25 and vector search results using Reciprocal Rank Fusion.

        RRF formula: score(chunk) = Σ (1 / (k + rank_i))
        where k=60 (constant), rank_i = position in result list i

        Args:
            bm25_results: List of (chunk_id, bm25_score)
            vector_results: List of (content, metadata, similarity_score)
                           where metadata contains 'id'

        Returns:
            List of (chunk_id, rrf_score) sorted by RRF score descending
        """
        rrf_scores = {}

        # Add BM25 rankings
        for rank, (chunk_id, bm25_score) in enumerate(bm25_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (self.k + rank + 1)

        # Add vector rankings
        for rank, (content, metadata, similarity) in enumerate(vector_results):
            # Extract chunk ID from metadata or use a hash of content
            chunk_id = metadata.get('id') if isinstance(metadata, dict) else None

            if chunk_id is None:
                # Fallback: fetch ID from database using content
                logger.warning(f"Chunk ID not in metadata for rank {rank}, fetching from DB...")
                try:
                    response = self.supabase.table("vector_embeddings") \
                        .select("id") \
                        .eq("content", content) \
                        .limit(1) \
                        .execute()

                    if response.data:
                        chunk_id = str(response.data[0]['id'])
                    else:
                        logger.error(f"Could not find chunk ID for content: {content[:50]}...")
                        continue

                except Exception as e:
                    logger.error(f"Error fetching chunk ID: {e}")
                    continue

            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (self.k + rank + 1)

        # Sort by RRF score (descending)
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        logger.info(f"RRF fusion: {len(bm25_results)} BM25 + {len(vector_results)} vector "
                   f"→ {len(sorted_results)} unique chunks")

        return sorted_results

    def _fetch_chunks_by_ids(self, chunk_ids: List[str]) -> List[Dict]:
        """
        Fetch full chunk data from Supabase by IDs.

        Args:
            chunk_ids: List of chunk IDs

        Returns:
            List of chunk dictionaries with content, metadata, id
        """
        if not chunk_ids:
            return []

        try:
            # Fetch chunks from Supabase
            response = self.supabase.table("vector_embeddings") \
                .select("id, content, metadata") \
                .in_("id", chunk_ids) \
                .execute()

            chunks = response.data

            # Create a mapping to preserve order
            chunk_map = {str(chunk['id']): chunk for chunk in chunks}

            # Return in the same order as chunk_ids
            ordered_chunks = [
                chunk_map[chunk_id]
                for chunk_id in chunk_ids
                if chunk_id in chunk_map
            ]

            return ordered_chunks

        except Exception as e:
            logger.error(f"Error fetching chunks by IDs: {e}")
            return []

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        use_query_rewriting: bool = False
    ) -> List[Dict]:
        """
        Perform hybrid search combining BM25 and vector search.

        Args:
            query: Search query
            top_k: Number of final results to return
            use_query_rewriting: Whether to use query rewriting (Sprint 8 Feature 2)

        Returns:
            List of chunk dictionaries with content, metadata, id, rrf_score
        """
        logger.info(f"Hybrid search: '{query}' (top_k={top_k})")

        # For now, ignore query_rewriting (will implement in Feature 2)
        if use_query_rewriting:
            logger.warning("Query rewriting not yet implemented. Using original query.")

        # Retrieve more results than needed for better fusion
        retrieve_k = max(top_k * 4, 20)

        # 1. BM25 keyword search
        logger.info(f"Running BM25 search (top_{retrieve_k})...")
        bm25_results = self.bm25_service.search(query, top_k=retrieve_k)

        # 2. Vector semantic search
        logger.info(f"Running vector search (top_{retrieve_k})...")
        vector_results = self.rag_service.search_similar_chunks(query, top_k=retrieve_k)

        # 3. Reciprocal Rank Fusion
        logger.info("Fusing results with RRF...")
        fused_results = self._reciprocal_rank_fusion(bm25_results, vector_results)

        # 4. Fetch top-k chunks
        top_chunk_ids = [chunk_id for chunk_id, score in fused_results[:top_k]]
        chunks = self._fetch_chunks_by_ids(top_chunk_ids)

        # 5. Add RRF scores to chunks
        rrf_score_map = dict(fused_results)
        for chunk in chunks:
            chunk['rrf_score'] = rrf_score_map.get(str(chunk['id']), 0.0)

        logger.info(f"Hybrid search complete: {len(chunks)} chunks returned")

        return chunks

    def multi_query_hybrid_search(
        self,
        queries: List[str],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Perform hybrid search with multiple query variations.

        Args:
            queries: List of query variations
            top_k: Number of final results to return

        Returns:
            List of chunk dictionaries with aggregated RRF scores
        """
        logger.info(f"Multi-query hybrid search: {len(queries)} queries (top_k={top_k})")

        all_rrf_scores = {}

        # Run hybrid search for each query variation
        for i, query in enumerate(queries):
            logger.info(f"Query {i+1}/{len(queries)}: '{query}'")

            # BM25 and vector search
            retrieve_k = max(top_k * 4, 20)
            bm25_results = self.bm25_service.search(query, top_k=retrieve_k)
            vector_results = self.rag_service.search_similar_chunks(query, top_k=retrieve_k)

            # RRF fusion for this query
            query_rrf_results = self._reciprocal_rank_fusion(bm25_results, vector_results)

            # Aggregate scores across queries
            for chunk_id, score in query_rrf_results:
                all_rrf_scores[chunk_id] = all_rrf_scores.get(chunk_id, 0) + score

        # Sort by aggregated RRF score
        sorted_results = sorted(all_rrf_scores.items(), key=lambda x: x[1], reverse=True)

        # Fetch top-k chunks
        top_chunk_ids = [chunk_id for chunk_id, score in sorted_results[:top_k]]
        chunks = self._fetch_chunks_by_ids(top_chunk_ids)

        # Add aggregated RRF scores
        for chunk in chunks:
            chunk['rrf_score'] = all_rrf_scores.get(str(chunk['id']), 0.0)

        logger.info(f"Multi-query hybrid search complete: {len(chunks)} chunks returned")

        return chunks
