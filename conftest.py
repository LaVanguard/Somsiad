"""
Pytest configuration and fixtures for Sprint 4 testing.
Provides reusable test fixtures for all test modules.
"""

import pytest
from django.contrib.auth.models import User

from knowledge.models import Document, Embedding
from queries.models import Conversation, Query


@pytest.fixture
def mock_user(db):
    """Create a test user."""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def mock_document(db):
    """Create a test document."""
    return Document.objects.create(
        title="Test Legal Document", category="budowa", processed=False
    )


@pytest.fixture
def mock_processed_document(db, mock_document):
    """Create a processed test document with embeddings."""
    mock_document.processed = True
    mock_document.save()

    # Create sample embedding
    Embedding.objects.create(
        document=mock_document,
        chunk_text="Art. 1. Test article content",
        embedding_id="test-uuid-123",
        metadata={"article_number": "1", "is_document_summary": False},
    )

    return mock_document


@pytest.fixture
def mock_conversation(db, mock_user):
    """Create a test conversation."""
    return Conversation.objects.create(user=mock_user, title="Test Conversation")


@pytest.fixture
def mock_query(db, mock_user, mock_conversation):
    """Create a test query."""
    return Query.objects.create(
        user=mock_user,
        conversation=mock_conversation,
        question="Test legal question?",
        answer="Test answer",
        sources=[],
        processing_time=1.23,
        ttft=0.45,
    )


@pytest.fixture
def mock_openai_embedding(mocker):
    """Mock OpenAI embeddings API."""
    mock = mocker.patch("langchain_openai.OpenAIEmbeddings.embed_documents")
    mock.return_value = [[0.1] * 1536]  # 1536-dim vector
    return mock


@pytest.fixture
def mock_openai_query_embedding(mocker):
    """Mock OpenAI query embedding."""
    mock = mocker.patch("langchain_openai.OpenAIEmbeddings.embed_query")
    mock.return_value = [0.1] * 1536
    return mock


@pytest.fixture
def mock_openai_chat(mocker):
    """Mock OpenAI chat completion."""
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.content = "Test AI response"

    mock = mocker.patch("langchain_openai.ChatOpenAI.invoke")
    mock.return_value = mock_response
    return mock


@pytest.fixture
def mock_supabase_search(mocker):
    """Mock Supabase vector search."""
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": "test-uuid",
            "content": "Art. 1. Test content",
            "metadata": {"article_number": "1"},
            "similarity": 0.95,
        }
    ]

    mock = mocker.patch("supabase.client.Client.rpc")
    mock.return_value.execute.return_value = mock_response
    return mock


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests automatically."""
    pass
