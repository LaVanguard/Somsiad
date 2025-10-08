"""
RAG Service for Somsiad - Legal Knowledge Retrieval
Sprint 2 implementation
"""

# TODO: Implement in Sprint 2
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import SupabaseVectorStore
# from supabase import create_client
# import os


class RAGService:
    """
    Service for Retrieval-Augmented Generation (RAG) queries.

    This service will:
    1. Accept user questions about legal matters
    2. Retrieve relevant document chunks from Supabase pgvector
    3. Generate AI responses using OpenAI GPT-4o-mini
    4. Return answers with citations

    Implementation: Sprint 2 (11-17 October)
    """

    def __init__(self):
        """
        Initialize RAG service with Supabase and OpenAI clients.

        TODO Sprint 2:
        - Initialize Supabase client
        - Setup OpenAI embeddings
        - Configure vector store
        - Setup LLM (GPT-4o-mini)
        """
        pass

    def query(self, question: str, top_k: int = 5) -> dict:
        """
        Query the RAG system with a legal question.

        Args:
            question (str): User's legal question
            top_k (int): Number of relevant chunks to retrieve

        Returns:
            dict: {
                'answer': str,  # AI-generated response
                'sources': list[dict]  # Source citations
            }

        TODO Sprint 2:
        - Embed user question
        - Retrieve top-k chunks from Supabase
        - Generate answer with LLM
        - Format response with citations
        """
        raise NotImplementedError("RAG service will be implemented in Sprint 2")

    def add_document(self, document_id: int, chunks: list[dict]) -> None:
        """
        Add document chunks to vector store.

        Args:
            document_id (int): ID of the document
            chunks (list[dict]): List of text chunks with metadata
                [{
                    'text': str,
                    'metadata': {
                        'document_id': int,
                        'page': int,
                        'title': str
                    }
                }]

        TODO Sprint 2:
        - Embed text chunks
        - Store in Supabase pgvector
        - Link to Document model
        """
        raise NotImplementedError("Document processing will be implemented in Sprint 2")


# Example usage (Sprint 2):
"""
# Initialize service
rag = RAGService()

# Query
result = rag.query("Czy mogę postawić szopę 3m od granicy?")
print(result['answer'])
print(result['sources'])

# Add document
chunks = [
    {
        'text': 'Według ustawy o planowaniu...',
        'metadata': {'document_id': 1, 'page': 5, 'title': 'Prawo budowlane'}
    }
]
rag.add_document(document_id=1, chunks=chunks)
"""
