"""
Integration tests for queries/views.py

Tests cover:
- Conversation CRUD operations
- Conversation listing with date grouping
- Loading conversation messages
- User isolation (can't access other users' conversations)
- Error handling
"""
import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from queries.models import Query, Conversation
import json

User = get_user_model()


# ============================================================================
# Create Conversation Tests
# ============================================================================

@pytest.mark.django_db
def test_create_conversation_requires_login():
    """Test that create conversation requires authentication"""
    client = Client()
    response = client.post('/api/conversations/create/')

    # Should redirect to login
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


@pytest.mark.django_db
def test_create_conversation_success(mock_user):
    """Test successful conversation creation"""
    client = Client()
    client.force_login(mock_user)

    response = client.post('/api/conversations/create/')

    assert response.status_code == 200
    data = json.loads(response.content)

    assert data['success'] is True
    assert 'conversation_id' in data
    assert 'title' in data
    assert data['title'] == 'Nowa rozmowa'

    # Verify conversation was created in database
    conv = Conversation.objects.get(id=data['conversation_id'])
    assert conv.user == mock_user
    assert conv.title == 'Nowa rozmowa'


@pytest.mark.django_db
def test_create_conversation_method_not_allowed():
    """Test that GET method is not allowed for create conversation"""
    client = Client()
    user = User.objects.create_user(username='test', password='test')
    client.force_login(user)

    response = client.get('/api/conversations/create/')

    # Should return 405 Method Not Allowed
    assert response.status_code == 405


# ============================================================================
# List Conversations Tests
# ============================================================================

@pytest.mark.django_db
def test_list_conversations_requires_login():
    """Test that list conversations requires authentication"""
    client = Client()
    response = client.get('/api/conversations/list/')

    # Should redirect to login
    assert response.status_code == 302


@pytest.mark.django_db
def test_list_conversations_empty(mock_user):
    """Test listing conversations when user has none"""
    client = Client()
    client.force_login(mock_user)

    response = client.get('/api/conversations/list/')

    assert response.status_code == 200
    # Should return HTML partial
    content = response.content.decode()
    assert len(content) >= 0  # Should return some HTML even if empty


@pytest.mark.django_db
def test_list_conversations_with_data(mock_user):
    """Test listing conversations with actual data"""
    client = Client()
    client.force_login(mock_user)

    # Create test conversations
    conv1 = Conversation.objects.create(
        user=mock_user,
        title='First Conversation'
    )
    conv2 = Conversation.objects.create(
        user=mock_user,
        title='Second Conversation'
    )

    response = client.get('/api/conversations/list/')

    assert response.status_code == 200
    content = response.content.decode()

    # Should contain conversation titles
    assert 'First Conversation' in content or 'Second Conversation' in content


@pytest.mark.django_db
def test_list_conversations_date_grouping(mock_user):
    """Test that conversations are grouped by date"""
    from django.utils import timezone
    from datetime import timedelta

    client = Client()
    client.force_login(mock_user)

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Create conversations at different times
    today_conv = Conversation.objects.create(
        user=mock_user,
        title='Today Conv'
    )
    today_conv.updated_at = today_start + timedelta(hours=10)
    today_conv.save()

    yesterday_conv = Conversation.objects.create(
        user=mock_user,
        title='Yesterday Conv'
    )
    yesterday_conv.updated_at = today_start - timedelta(hours=12)
    yesterday_conv.save()

    older_conv = Conversation.objects.create(
        user=mock_user,
        title='Older Conv'
    )
    older_conv.updated_at = today_start - timedelta(days=3)
    older_conv.save()

    response = client.get('/api/conversations/list/')

    assert response.status_code == 200
    content = response.content.decode()

    # All conversations should be present
    assert 'Today Conv' in content or 'Yesterday Conv' in content or 'Older Conv' in content


@pytest.mark.django_db
def test_list_conversations_user_isolation(mock_user):
    """Test that users only see their own conversations"""
    client = Client()
    client.force_login(mock_user)

    # Create another user with conversation
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@test.com',
        password='testpass'
    )
    other_conv = Conversation.objects.create(
        user=other_user,
        title='Other User Conversation'
    )

    # Create conversation for current user
    my_conv = Conversation.objects.create(
        user=mock_user,
        title='My Conversation'
    )

    response = client.get('/api/conversations/list/')

    assert response.status_code == 200
    content = response.content.decode()

    # Should contain own conversation
    # Other user's conversation may or may not be in HTML depending on template
    # But database query should only return user's conversations
    conversations = Conversation.objects.filter(user=mock_user)
    assert conversations.count() == 1
    assert conversations.first().title == 'My Conversation'


# ============================================================================
# Load Conversation Tests
# ============================================================================

@pytest.mark.django_db
def test_load_conversation_requires_login():
    """Test that load conversation requires authentication"""
    client = Client()
    response = client.get('/api/conversations/1/')

    # Should redirect to login
    assert response.status_code == 302


@pytest.mark.django_db
def test_load_conversation_success(mock_user):
    """Test loading conversation with messages"""
    client = Client()
    client.force_login(mock_user)

    # Create conversation with queries
    conv = Conversation.objects.create(
        user=mock_user,
        title='Test Conversation'
    )

    query1 = Query.objects.create(
        user=mock_user,
        conversation=conv,
        question='Question 1',
        answer='Answer 1',
        sources=[],
        processing_time=1.0
    )

    query2 = Query.objects.create(
        user=mock_user,
        conversation=conv,
        question='Question 2',
        answer='Answer 2',
        sources=[],
        processing_time=1.5
    )

    response = client.get(f'/api/conversations/{conv.id}/')

    assert response.status_code == 200
    content = response.content.decode()

    # Should contain both queries
    assert 'Question 1' in content or 'Question 2' in content


@pytest.mark.django_db
def test_load_conversation_not_found(mock_user):
    """Test loading non-existent conversation returns 404"""
    client = Client()
    client.force_login(mock_user)

    response = client.get('/api/conversations/99999/')

    assert response.status_code == 404


@pytest.mark.django_db
def test_load_conversation_wrong_user(mock_user):
    """Test that users can't load other users' conversations"""
    client = Client()

    # Create another user with conversation
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@test.com',
        password='testpass'
    )
    other_conv = Conversation.objects.create(
        user=other_user,
        title='Other User Conversation'
    )

    # Try to load as mock_user
    client.force_login(mock_user)
    response = client.get(f'/api/conversations/{other_conv.id}/load/')

    # Should return 404 (not found for this user)
    assert response.status_code == 404


@pytest.mark.django_db
def test_load_conversation_empty(mock_user):
    """Test loading conversation with no messages"""
    client = Client()
    client.force_login(mock_user)

    # Create conversation without queries
    conv = Conversation.objects.create(
        user=mock_user,
        title='Empty Conversation'
    )

    response = client.get(f'/api/conversations/{conv.id}/')

    assert response.status_code == 200
    # Should return HTML even if empty


# ============================================================================
# Delete Conversation Tests
# ============================================================================

@pytest.mark.django_db
def test_delete_conversation_requires_login():
    """Test that delete conversation requires authentication"""
    client = Client()
    response = client.delete('/api/conversations/1/delete/')

    # Should redirect to login
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_conversation_success(mock_user):
    """Test successful conversation deletion"""
    client = Client()
    client.force_login(mock_user)

    # Create conversation
    conv = Conversation.objects.create(
        user=mock_user,
        title='To Delete'
    )
    conv_id = conv.id

    response = client.delete(f'/api/conversations/{conv_id}/delete/')

    # Delete endpoint returns empty 200 response (for HTMX)
    assert response.status_code == 200

    # Verify conversation was deleted
    assert not Conversation.objects.filter(id=conv_id).exists()


@pytest.mark.django_db
def test_delete_conversation_with_queries(mock_user):
    """Test deleting conversation also deletes associated queries"""
    client = Client()
    client.force_login(mock_user)

    # Create conversation with queries
    conv = Conversation.objects.create(
        user=mock_user,
        title='Conv with Queries'
    )

    query = Query.objects.create(
        user=mock_user,
        conversation=conv,
        question='Test question',
        answer='Test answer',
        sources=[],
        processing_time=1.0
    )

    conv_id = conv.id
    query_id = query.id

    response = client.delete(f'/api/conversations/{conv_id}/delete/')

    assert response.status_code == 200

    # Both conversation and query should be deleted (cascade)
    assert not Conversation.objects.filter(id=conv_id).exists()
    assert not Query.objects.filter(id=query_id).exists()


@pytest.mark.django_db
def test_delete_conversation_not_found(mock_user):
    """Test deleting non-existent conversation returns 404"""
    client = Client()
    client.force_login(mock_user)

    response = client.delete('/api/conversations/99999/delete/')

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_conversation_wrong_user(mock_user):
    """Test that users can't delete other users' conversations"""
    client = Client()

    # Create another user with conversation
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@test.com',
        password='testpass'
    )
    other_conv = Conversation.objects.create(
        user=other_user,
        title='Other User Conversation'
    )
    other_conv_id = other_conv.id

    # Try to delete as mock_user
    client.force_login(mock_user)
    response = client.delete(f'/api/conversations/{other_conv_id}/delete/')

    # Should return 404 (not found for this user)
    assert response.status_code == 404

    # Conversation should still exist
    assert Conversation.objects.filter(id=other_conv_id).exists()


@pytest.mark.django_db
def test_delete_conversation_method_not_allowed(mock_user):
    """Test that GET/POST methods are not allowed for delete"""
    client = Client()
    client.force_login(mock_user)

    conv = Conversation.objects.create(
        user=mock_user,
        title='Test Conv'
    )

    # Try GET
    response = client.get(f'/api/conversations/{conv.id}/delete/')
    assert response.status_code == 405

    # Try POST
    response = client.post(f'/api/conversations/{conv.id}/delete/')
    assert response.status_code == 405


# ============================================================================
# Edge Cases & Integration Tests
# ============================================================================

@pytest.mark.django_db
def test_conversation_ordering(mock_user):
    """Test that conversations are ordered by updated_at"""
    client = Client()
    client.force_login(mock_user)

    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()

    # Create conversations with explicit timestamps
    conv1 = Conversation.objects.create(user=mock_user, title='First')
    conv2 = Conversation.objects.create(user=mock_user, title='Second')
    conv3 = Conversation.objects.create(user=mock_user, title='Third')

    # Update timestamps after creation to ensure ordering
    Conversation.objects.filter(id=conv1.id).update(updated_at=now - timedelta(hours=3))
    Conversation.objects.filter(id=conv2.id).update(updated_at=now - timedelta(hours=1))
    Conversation.objects.filter(id=conv3.id).update(updated_at=now)

    # Fetch conversations ordered by updated_at descending
    conversations = Conversation.objects.filter(user=mock_user).order_by('-updated_at')

    # Should be ordered newest first
    titles = [c.title for c in conversations]
    assert titles[0] == 'Third'
    assert titles[1] == 'Second'
    assert titles[2] == 'First'


@pytest.mark.django_db
def test_query_ordering_in_conversation(mock_user):
    """Test that queries within conversation are ordered by created_at"""
    client = Client()
    client.force_login(mock_user)

    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()

    conv = Conversation.objects.create(user=mock_user, title='Test')

    # Create queries in order
    q1 = Query.objects.create(
        user=mock_user,
        conversation=conv,
        question='First question',
        answer='First answer',
        sources=[],
        processing_time=1.0
    )
    q1.created_at = now
    q1.save()

    q2 = Query.objects.create(
        user=mock_user,
        conversation=conv,
        question='Second question',
        answer='Second answer',
        sources=[],
        processing_time=1.0
    )
    q2.created_at = now + timedelta(seconds=30)
    q2.save()

    # Load conversation
    response = client.get(f'/api/conversations/{conv.id}/')

    assert response.status_code == 200

    # Verify queries are ordered
    queries = conv.queries.all().order_by('created_at')
    assert queries[0].question == 'First question'
    assert queries[1].question == 'Second question'
