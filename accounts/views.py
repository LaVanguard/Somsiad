from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging

from knowledge.services.rag_service import RAGService
from queries.models import Query

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'home.html')


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
        'processing_time': processing_time
    }

    html = render_to_string('partials/message.html', context)
    return HttpResponse(html)


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