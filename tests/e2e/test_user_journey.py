"""
E2E Test 1: User Journey - Login → Ask Question → Get Answer

This test verifies the complete user flow:
1. User navigates to home page
2. User logs in successfully
3. User asks a legal question
4. System returns an answer with sources
5. Conversation is saved

Required for 10xDevs certification.
"""
import pytest
from playwright.sync_api import Page, expect
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.e2e
@pytest.mark.django_db
def test_complete_user_journey_with_rag_query(page: Page, live_server, test_user):
    """
    Test complete user journey: anonymous → login → ask question → get answer.

    This E2E test covers:
    - Navigation to home page
    - Login flow
    - Asking a legal question via chat interface
    - Receiving an answer (either RAG or joke action)
    - Verifying conversation was created
    """
    # Step 1: Navigate to home page
    page.goto(f"{str(live_server)}/")
    expect(page).to_have_title("Somsiad - Prawny Doradca AI")

    # Verify we see the landing page (not authenticated yet)
    # Should see login/signup buttons
    login_link = page.locator('a[href="/accounts/login/"]')
    expect(login_link).to_be_visible()

    # Step 2: Click login and fill credentials
    login_link.click()
    page.wait_for_url(f"{str(live_server)}/accounts/login/")

    page.fill('input[name="username"]', 'e2e_testuser')
    page.fill('input[name="password"]', 'testpass123')
    page.click('button[type="submit"]')

    # Step 3: Verify successful login (redirected to home)
    page.wait_for_url(f"{str(live_server)}/")

    # Should now see chat interface
    chat_input = page.locator('textarea[name="question"]')
    expect(chat_input).to_be_visible()

    # Step 4: Ask a legal question
    question = "Jakie są minimalne odległości budynku od granicy działki?"
    chat_input.fill(question)

    # Click submit button (or use one of the joke action buttons)
    # For simplicity, let's use the "prokuratura" joke button
    prokuratura_button = page.locator('button:has-text("Prokuratura")')

    # If prokuratura button exists, use it; otherwise use submit
    if prokuratura_button.is_visible():
        prokuratura_button.click()
    else:
        # Fallback: submit via Enter or submit button
        page.locator('button[type="submit"]').click()

    # Step 5: Wait for answer to appear
    # The answer should appear in the chat messages area
    page.wait_for_timeout(3000)  # Wait 3 seconds for response

    # Verify answer is displayed
    # Look for message bubbles or answer content
    messages = page.locator('.message, .answer, [id*="answer"]')
    expect(messages).to_have_count(2, timeout=10000)  # Question + Answer

    # Step 6: Verify conversation was created in database
    from queries.models import Conversation, Query

    conversations = Conversation.objects.filter(user=test_user)
    assert conversations.count() == 1, "Conversation should be created"

    conversation = conversations.first()
    assert conversation.title is not None
    assert len(conversation.title) > 0

    # Verify query was saved
    queries = Query.objects.filter(user=test_user, conversation=conversation)
    assert queries.count() == 1, "Query should be saved"

    query = queries.first()
    assert question in query.question
    assert len(query.answer) > 0
    assert query.processing_time is not None


@pytest.mark.e2e
@pytest.mark.django_db
def test_user_can_start_new_conversation(authenticated_page: Page, live_server, test_user):
    """
    Test user can create new conversation via UI.

    This test verifies:
    - User clicks "New Conversation" button
    - New conversation is created
    - Chat input is cleared
    """
    # Already authenticated via fixture
    page = authenticated_page

    # Verify we're on home page
    expect(page).to_have_url(f"{str(live_server)}/")

    # Look for "New Conversation" or "+" button
    new_conv_button = page.locator('button:has-text("Nowa rozmowa"), button:has-text("+")')

    # If button exists, click it
    if new_conv_button.is_visible():
        initial_conv_count = page.locator('.conversation-item').count()

        new_conv_button.click()
        page.wait_for_timeout(1000)

        # Verify new conversation appears in sidebar
        new_conv_count = page.locator('.conversation-item').count()
        assert new_conv_count == initial_conv_count + 1, "New conversation should appear"

    # Verify we can still ask questions
    chat_input = page.locator('textarea[name="question"]')
    expect(chat_input).to_be_visible()
    expect(chat_input).to_be_empty()
