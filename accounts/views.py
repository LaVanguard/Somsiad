# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging
import json
import time

from knowledge.services.rag_service import RAGService
from knowledge.models import Document
from queries.models import Query, Conversation
from .ratelimit_decorators import ratelimit_rag_query

logger = logging.getLogger(__name__)


@login_required
def home(request):
    """Home view with document data and conversations for sidebar."""
    # Get processed and unprocessed documents
    processed_docs = Document.objects.filter(processed=True).order_by('-uploaded_at')
    unprocessed_docs = Document.objects.filter(processed=False).order_by('-uploaded_at')

    # Get user conversations if authenticated
    conversations = []
    if request.user.is_authenticated:
        from datetime import timedelta
        from django.utils import timezone

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)

        user_conversations = Conversation.objects.filter(
            user=request.user
        ).prefetch_related('queries')

        grouped = {
            'today': [],
            'yesterday': [],
            'older': []
        }

        for conv in user_conversations:
            if conv.updated_at >= today_start:
                grouped['today'].append(conv)
            elif conv.updated_at >= yesterday_start:
                grouped['yesterday'].append(conv)
            else:
                grouped['older'].append(conv)

        conversations = grouped

    context = {
        'processed_documents': processed_docs,
        'unprocessed_documents': unprocessed_docs,
        'processed_count': processed_docs.count(),
        'unprocessed_count': unprocessed_docs.count(),
        'grouped_conversations': conversations,
    }

    return render(request, 'home.html', context)


@require_http_methods(["POST"])
@login_required
def query_api(request):
    """
    Chat API endpoint with RAG integration.
    Processes user questions and returns AI-generated legal advice.
    """
    question = request.POST.get('question', '').strip()
    image = request.FILES.get('image', None)
    action = request.POST.get('action', None)
    conversation_id = request.POST.get('conversation_id', None)

    # Get or create conversation
    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        except Conversation.DoesNotExist:
            pass

    # Create new conversation if none exists
    if not conversation:
        conversation = Conversation.objects.create(
            user=request.user,
            title=question[:50] + "..." if len(question) > 50 else question
        )

    # Validate question
    if not question:
        return HttpResponse(
            render_to_string('partials/message.html', {
                'question': '',
                'answer': '❌ Proszę zadać pytanie!',
                'error': True
            })
        )

    # Handle image upload (save for Query model)
    image_url = None
    saved_image = None
    if image:
        # Save image temporarily (will be saved to Query model)
        import base64
        image_data = base64.b64encode(image.read()).decode('utf-8')
        image_url = f"data:{image.content_type};base64,{image_data}"
        saved_image = image

    # Handle joke actions (mock responses - no RAG)
    if action in ['prokuratura', 'donos', 'straz']:
        answer = _get_joke_response(action, question)
        sources = []
        processing_time = 0.0

    # Regular question - use RAG
    else:
        # Check if API keys are configured
        if not settings.OPENAI_API_KEY or not settings.SUPABASE_URL:
            answer = (
                "⚠️ RAG system not configured yet!\n\n"
                "To use the AI legal advisor, you need to:\n"
                "1. Set up Supabase (see docs/SUPABASE_SETUP.md)\n"
                "2. Add OPENAI_API_KEY to .env\n"
                "3. Add SUPABASE_URL and SUPABASE_KEY to .env\n\n"
                "For now, here's a mock response: "
                "Analizuję Twoje pytanie o przepisy budowlane... 🤖"
            )
            sources = []
            processing_time = 0.0
        else:
            try:
                # Use RAG service
                rag = RAGService()
                answer, sources, processing_time = rag.process_query(question, top_k=5)
                logger.info(f"RAG query completed in {processing_time:.2f}s")

            except Exception as e:
                logger.error(f"RAG query failed: {e}", exc_info=True)
                answer = (
                    f"❌ Wystąpił błąd podczas przetwarzania pytania.\n\n"
                    f"Sprawdź:\n"
                    f"- Czy Supabase jest poprawnie skonfigurowany\n"
                    f"- Czy dokumenty zostały przetworzone (python manage.py process_documents --all)\n"
                    f"- Czy klucze API są prawidłowe\n\n"
                    f"Błąd techniczny: {str(e)}"
                )
                sources = []
                processing_time = 0.0

    # Save query to database
    try:
        Query.objects.create(
            user=request.user,
            conversation=conversation,
            question=question,
            image=saved_image,
            answer=answer,
            sources=sources,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Failed to save query: {e}")

    # Render response
    context = {
        'question': question,
        'image_url': image_url,
        'answer': answer,
        'sources': sources[:3] if sources else [],  # Show max 3 sources
        'processing_time': processing_time,
        'conversation_id': conversation.id
    }

    html = render_to_string('partials/message.html', context)
    return HttpResponse(html)


@require_http_methods(["POST"])
@login_required
@ratelimit_rag_query
def query_stream_api(request):
    """
    Streaming chat API endpoint with RAG integration.
    Returns Server-Sent Events (SSE) for real-time response streaming.
    """
    question = request.POST.get('question', '').strip()
    conversation_id = request.POST.get('conversation_id', None)

    # Get or create conversation
    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        except Conversation.DoesNotExist:
            pass

    if not conversation:
        conversation = Conversation.objects.create(
            user=request.user,
            title=question[:50] + "..." if len(question) > 50 else question
        )

    # Validate question
    if not question:
        def error_stream():
            yield f"data: {json.dumps({'error': 'Proszę zadać pytanie!'})}\n\n"
        return StreamingHttpResponse(error_stream(), content_type='text/event-stream')

    # Check API keys
    if not settings.OPENAI_API_KEY or not settings.SUPABASE_URL:
        def config_error_stream():
            yield f"data: {json.dumps({'error': 'RAG system not configured'})}\n\n"
        return StreamingHttpResponse(config_error_stream(), content_type='text/event-stream')

    def event_stream():
        """Generator for SSE streaming."""
        start_time = time.time()
        ttft = None  # Time To First Token (PRD NFR-1)
        first_token_sent = False
        full_answer = ""
        sources = []

        try:
            # Initialize RAG
            rag = RAGService()

            # Search for relevant chunks
            search_results = rag.search_similar_chunks(question, top_k=5)
            context_chunks = [text for text, _, _ in search_results]
            sources = [
                {
                    "text": text[:200] + "..." if len(text) > 200 else text,
                    "metadata": metadata,
                    "similarity": similarity
                }
                for text, metadata, similarity in search_results
            ]

            # Send conversation ID first
            yield f"data: {json.dumps({'conversation_id': conversation.id})}\n\n"

            # Stream answer chunks
            for chunk in rag.generate_answer_streaming(question, context_chunks):
                if chunk:
                    # Measure TTFT (Time To First Token) - PRD v2.1 NFR-1
                    if not first_token_sent:
                        ttft = time.time() - start_time
                        first_token_sent = True
                        logger.info(f"TTFT: {ttft:.3f}s (PRD target: <5s P95)")

                    full_answer += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # Calculate total processing time
            processing_time = time.time() - start_time

            # Save to database with performance metrics
            Query.objects.create(
                user=request.user,
                conversation=conversation,
                question=question,
                answer=full_answer,
                sources=sources,
                processing_time=processing_time,
                ttft=ttft  # Time To First Token (PRD v2.1 NFR-1)
            )

            # Generate conversation title if this is the first query
            if conversation.queries.count() == 1:  # Just created first query
                new_title = _generate_conversation_title(question, full_answer)
                conversation.title = new_title
                conversation.save()
                logger.info(f"Generated conversation title: {new_title}")

            # Log performance metrics
            if ttft:
                logger.info(f"Performance: TTFT={ttft:.3f}s, Total={processing_time:.3f}s")

            # Send completion event with sources and performance data
            yield f"data: {json.dumps({
                'done': True,
                'sources': sources[:3],
                'processing_time': processing_time,
                'ttft': ttft
            })}\n\n"

        except Exception as e:
            logger.error(f"Streaming RAG query failed: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def _generate_conversation_title(question: str, answer: str) -> str:
    """
    Generate a short conversation title from Q&A using OpenAI.

    Args:
        question: User's question
        answer: AI's answer

    Returns:
        Short title (max 50 chars)
    """
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.3
        )

        prompt = f"""Wygeneruj krótki tytuł (max 40 znaków) dla tej rozmowy w języku polskim.
Tytuł powinien być zwięzłym opisem tematu rozmowy.

Pytanie: {question[:200]}
Odpowiedź: {answer[:200]}

Zwróć TYLKO tytuł, bez cudzysłowów i dodatkowych znaków."""

        response = llm.invoke(prompt)
        title = response.content.strip()[:50]  # Limit to 50 chars

        return title if title else question[:50] + "..."

    except Exception as e:
        logger.error(f"Failed to generate title: {e}")
        # Fallback: use first 50 chars of question
        return question[:50] + ("..." if len(question) > 50 else "")


def _get_joke_response(action: str, question: str) -> str:
    """Generate joke responses for action buttons."""
    templates = {
        'prokuratura': (
            '⚖️ ZGŁOSZENIE DO PROKURATURY REJONOWEJ\n\n'
            'Szanowny Panie Prokuratorze,\n\n'
            'Niniejszym zgłaszam sprawę wymagającą interwencji prokuratury. '
            'Sprawa dotyczy: "{}"\n\n'
            'Z poważaniem,\n'
            'Zatroskany Obywatel\n\n'
            '(To jest żartobliwa odpowiedź 😄)'
        ),
        'donos': (
            '📧 ANONIMOWY DONOS DO URZĘDU GMINY\n\n'
            'Do Wójta Gminy,\n\n'
            'Uprzejmie informuję o nieprawidłowościach: "{}"\n\n'
            'Proszę o dyskretną interwencję.\n\n'
            'Pozdrawiam,\n'
            'Anonim z sąsiedztwa\n\n'
            '(To jest żartobliwa odpowiedź 😄)'
        ),
        'straz': (
            '🚨 ZGŁOSZENIE DO STRAŻY MIEJSKIEJ\n\n'
            'Witam,\n\n'
            'Proszę o pilną interwencję Straży Miejskiej w sprawie: "{}"\n\n'
            'Zgłoszenie dotyczy naruszenia porządku publicznego.\n\n'
            'Dziękuję,\n'
            'Zaniepokojony Mieszkaniec\n\n'
            '(To jest żartobliwa odpowiedź 😄)'
        )
    }
    return templates.get(action, '').format(question)