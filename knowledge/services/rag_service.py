"""
RAG Service for document retrieval and LLM generation.
Sprint 2 implementation.
"""
import time
from typing import List, Dict, Tuple
from django.conf import settings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangChainDocument
from supabase import create_client, Client


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Handles embeddings, vector search, and LLM generation.
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

        # Insert into Supabase
        response = self.supabase.table("embeddings").insert(records).execute()

        # Return IDs
        embedding_ids = [record["id"] for record in response.data]
        return embedding_ids

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
        # Build prompt with context
        context = "\n\n".join([
            f"[Fragment {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])

        prompt = f"""Jesteś Somsiad - pomocny doradca prawny dla właścicieli domów jednorodzinnych w Polsce.

Kontekst prawny:
{context}

Pytanie użytkownika:
{question}

Instrukcje:
- Odpowiedz na pytanie w oparciu o podany kontekst prawny
- Jeśli kontekst nie zawiera pełnej odpowiedzi, powiedz to wyraźnie
- Używaj prostego, przyjaznego języka (nie prawniczego żargonu)
- Dodaj odrobinę humoru jeśli to możliwe
- Jeśli to kwestia sąsiedzka, bądź dyplomatyczny
- Zawsze wspominaj o konsultacji z prawnikiem dla pewności

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
        # Build prompt with context
        context = "\n\n".join([
            f"[Fragment {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])

        prompt = f"""Jesteś Somsiad - pomocny doradca prawny dla właścicieli domów jednorodzinnych w Polsce.

Kontekst prawny:
{context}

Pytanie użytkownika:
{question}

Instrukcje:
- Odpowiedz na pytanie w oparciu o podany kontekst prawny
- Jeśli kontekst nie zawiera pełnej odpowiedzi, powiedz to wyraźnie
- Używaj prostego, przyjaznego języka (nie prawniczego żargonu)
- Dodaj odrobinę humoru jeśli to możliwe
- Jeśli to kwestia sąsiedzka, bądź dyplomatyczny
- Zawsze wspominaj o konsultacji z prawnikiem dla pewności

Odpowiedź:"""

        # Stream answer chunks
        for chunk in self.llm.stream(prompt):
            if hasattr(chunk, 'content'):
                yield chunk.content

    def process_query(
        self,
        question: str,
        top_k: int = 5
    ) -> Tuple[str, List[Dict], float]:
        """
        Full RAG pipeline: retrieve → generate answer.

        Args:
            question: User's question
            top_k: Number of context chunks to retrieve

        Returns:
            Tuple of (answer, sources, processing_time)
        """
        start_time = time.time()

        # 1. Search for relevant chunks
        search_results = self.search_similar_chunks(question, top_k=top_k)

        # 2. Extract context and sources
        context_chunks = [text for text, _, _ in search_results]
        sources = [
            {
                "text": text[:200] + "..." if len(text) > 200 else text,
                "metadata": metadata,
                "similarity": similarity
            }
            for text, metadata, similarity in search_results
        ]

        # 3. Generate answer
        answer = self.generate_answer(question, context_chunks)

        # 4. Calculate processing time
        processing_time = time.time() - start_time

        return answer, sources, processing_time
