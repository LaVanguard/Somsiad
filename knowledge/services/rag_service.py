"""
RAG Service for document retrieval and LLM generation.
Sprint 2 implementation.
Sprint 8: Added RAG 2.0 hybrid search support.
"""
import time
import logging
from typing import List, Dict, Tuple, Optional
from django.conf import settings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangChainDocument
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Handles embeddings, vector search, and LLM generation.

    Sprint 8: Now supports hybrid search (BM25 + vector) for better retrieval.
    """

    def __init__(self):
        """Initialize RAG components."""
        self.openai_api_key = settings.OPENAI_API_KEY
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY

        # Initialize clients
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key,
            model="text-embedding-3-small"
        )
        self.llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model="gpt-4o-mini",
            temperature=0.3
        )
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Text splitter for chunking documents
        # Note: PRD specifies 1500 char max chunk size (Section 2.2)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            length_function=len,
        )

        # Sprint 8: Hybrid search service (lazy loaded)
        self._hybrid_search_service: Optional['HybridSearchService'] = None

    def chunk_document(self, text: str, metadata: Dict = None) -> List[LangChainDocument]:
        """
        Split document into chunks for embedding.

        **DEPRECATED**: This method uses naive fixed-size chunking.
        For production, use DocumentProcessor with SemanticChunker instead.
        This is kept only for backward compatibility and testing.

        The production pipeline (DocumentProcessor) implements:
        - Semantic chunking by legal structure (Art., §, Rozdział)
        - Hierarchical document summaries
        - Metadata enrichment with legal references
        - Preprocessing to remove administrative noise

        Args:
            text: Document text
            metadata: Optional metadata (page numbers, etc.)

        Returns:
            List of LangChain Document objects
        """
        import warnings
        warnings.warn(
            "RAGService.chunk_document() uses naive chunking. "
            "Use DocumentProcessor with SemanticChunker for production.",
            DeprecationWarning,
            stacklevel=2
        )

        chunks = self.text_splitter.split_text(text)
        documents = [
            LangChainDocument(
                page_content=chunk,
                metadata=metadata or {}
            )
            for chunk in chunks
        ]
        return documents

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        embeddings = self.embeddings.embed_documents(texts)
        return embeddings

    def store_embeddings(
        self,
        embeddings: List[List[float]],
        texts: List[str],
        metadata: List[Dict]
    ) -> List[str]:
        """
        Store embeddings in Supabase pgvector.
        Inserts in batches to avoid timeout errors.

        Args:
            embeddings: List of embedding vectors
            texts: Corresponding text chunks
            metadata: Metadata for each chunk

        Returns:
            List of embedding IDs
        """
        # Prepare data for Supabase
        records = [
            {
                "embedding": emb,
                "content": text,
                "metadata": meta
            }
            for emb, text, meta in zip(embeddings, texts, metadata)
        ]

        # Insert in batches of 50 to avoid timeout
        batch_size = 50
        all_embedding_ids = []

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            response = self.supabase.table("vector_embeddings").insert(batch).execute()
            batch_ids = [record["id"] for record in response.data]
            all_embedding_ids.extend(batch_ids)
            logger.info(f"Inserted batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1} ({len(batch)} embeddings)")

        return all_embedding_ids

    def search_similar_chunks(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[str, Dict, float]]:
        """
        Search for similar document chunks using vector similarity.

        Args:
            query: User's question
            top_k: Number of results to return

        Returns:
            List of (text, metadata, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Search Supabase with RPC function (pgvector similarity)
        response = self.supabase.rpc(
            "match_embeddings",
            {
                "query_embedding": query_embedding,
                "match_count": top_k
            }
        ).execute()

        # Parse results
        results = [
            (
                record["content"],
                record["metadata"],
                record["similarity"]
            )
            for record in response.data
        ]

        return results

    def _get_system_prompt(self) -> str:
        """Get active system prompt from database or return default."""
        try:
            from queries.models import SystemPrompt
            system_prompt = SystemPrompt.objects.filter(is_active=True).first()
            if system_prompt:
                return system_prompt.prompt_text
        except Exception:
            pass

        # Fallback to default if database not available
        return """Jesteś Somsiad - pomocnym asystentem prawnym dla polskich właścicieli domów jednorodzinnych.

Twoim zadaniem jest udzielanie jasnych, rzeczowych odpowiedzi na pytania prawne dotyczące:
- Budownictwa i remontów
- Ogrodów i działek
- Przeglądów technicznych
- Sporów sąsiedzkich

Zasady odpowiedzi:
1. Odpowiadaj TYLKO na podstawie dostarczonych źródeł prawnych
2. Cytuj konkretne artykuły i przepisy
3. Używaj prostego języka, unikaj zbędnego żargonu prawnego
4. Jeśli nie masz pewności lub źródła nie zawierają odpowiedzi, powiedz to wprost
5. W razie potrzeby zasugeruj konsultację z prawnikiem

Format odpowiedzi:
- Krótkie podsumowanie (1-2 zdania)
- Szczegółowa odpowiedź z odniesieniami do przepisów
- Praktyczne wskazówki (jeśli masz pewność)"""

    def generate_answer(
        self,
        question: str,
        context_chunks: List[str]
    ) -> str:
        """
        Generate answer using LLM with retrieved context.

        Args:
            question: User's question
            context_chunks: Retrieved relevant document chunks

        Returns:
            Generated answer
        """
        # Get system prompt from database
        system_prompt = self._get_system_prompt()

        # Build prompt with context
        context = "\n\n".join([
            f"[Fragment {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])

        prompt = f"""{system_prompt}

Kontekst prawny:
{context}

Pytanie użytkownika:
{question}

Odpowiedź:"""

        # Generate answer
        response = self.llm.invoke(prompt)
        answer = response.content

        return answer

    def generate_answer_streaming(
        self,
        question: str,
        context_chunks: List[str]
    ):
        """
        Generate answer using LLM with retrieved context (streaming).

        Args:
            question: User's question
            context_chunks: Retrieved relevant document chunks

        Yields:
            Answer chunks as they are generated
        """
        # Get system prompt from database
        system_prompt = self._get_system_prompt()

        # Build prompt with context
        context = "\n\n".join([
            f"[Fragment {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])

        prompt = f"""{system_prompt}

Kontekst prawny:
{context}

Pytanie użytkownika:
{question}

Odpowiedź:"""

        # Stream answer chunks
        for chunk in self.llm.stream(prompt):
            if hasattr(chunk, 'content'):
                yield chunk.content

    @property
    def hybrid_search_service(self):
        """Lazy load HybridSearchService to avoid circular imports."""
        if self._hybrid_search_service is None:
            from knowledge.services.hybrid_search_service import HybridSearchService
            self._hybrid_search_service = HybridSearchService(rag_service=self)
        return self._hybrid_search_service

    def process_query(
        self,
        question: str,
        top_k: int = 5,
        use_hybrid_search: bool = True
    ) -> Tuple[str, List[Dict], float]:
        """
        Full RAG pipeline: retrieve → generate answer.

        Args:
            question: User's question
            top_k: Number of context chunks to retrieve
            use_hybrid_search: Whether to use hybrid search (BM25 + vector) [Sprint 8]

        Returns:
            Tuple of (answer, sources, processing_time)
        """
        start_time = time.time()

        # 1. Search for relevant chunks
        if use_hybrid_search:
            # Sprint 8: Hybrid search (BM25 + vector with RRF fusion)
            logger.info(f"Using hybrid search for query: '{question[:50]}...'")
            hybrid_results = self.hybrid_search_service.hybrid_search(question, top_k=top_k)

            # Extract context and sources from hybrid results
            context_chunks = [chunk['content'] for chunk in hybrid_results]
            sources = [
                {
                    "text": chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                    "metadata": chunk.get('metadata', {}),
                    "rrf_score": chunk.get('rrf_score', 0.0)
                }
                for chunk in hybrid_results
            ]
        else:
            # Original vector-only search
            logger.info(f"Using vector search for query: '{question[:50]}...'")
            search_results = self.search_similar_chunks(question, top_k=top_k)

            # Extract context and sources
            context_chunks = [text for text, _, _ in search_results]
            sources = [
                {
                    "text": text[:200] + "..." if len(text) > 200 else text,
                    "metadata": metadata,
                    "similarity": similarity
                }
                for text, metadata, similarity in search_results
            ]

        # 2. Generate answer
        answer = self.generate_answer(question, context_chunks)

        # 3. Calculate processing time
        processing_time = time.time() - start_time

        return answer, sources, processing_time
