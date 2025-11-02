"""
Memetic Actions Views
API endpoints for fake legal actions (Prosecutor, Donos, Municipal Guard).
Sprint 9 - Entertainment feature.
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from knowledge.services.memetic_actions_service import MemeticActionsService
from .ratelimit_decorators import ratelimit

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@login_required
@ratelimit(key='user', rate='10/h', method='POST', block=True)
def generate_prosecutor_letter(request):
    """
    Generate fake prosecutor letter using GPT-5 mini.

    POST /api/actions/prosecutor/generate/
    Body: {"question": "...", "ai_answer": "..."}

    Returns: {"letter": "...", "timestamp": "..."}
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        ai_answer = data.get('ai_answer', '')

        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)

        # Generate letter
        service = MemeticActionsService()
        result = service.generate_prosecutor_letter(question, ai_answer)

        logger.info(f"User {request.user.id} generated prosecutor letter")

        return JsonResponse({
            'letter': result['letter'],
            'generated_by': result['generated_by'],
            'timestamp': timezone.now().isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Failed to generate prosecutor letter: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
@ratelimit(key='user', rate='10/h', method='POST', block=True)
def generate_donos_email(request):
    """
    Generate fake anonymous complaint email using GPT-5 mini.

    POST /api/actions/donos/generate/
    Body: {"question": "...", "ai_answer": "..."}

    Returns: {"subject": "...", "body": "...", "timestamp": "..."}
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        ai_answer = data.get('ai_answer', '')

        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)

        # Generate email
        service = MemeticActionsService()
        result = service.generate_donos_email(question, ai_answer)

        logger.info(f"User {request.user.id} generated donos email")

        return JsonResponse({
            'subject': result['subject'],
            'body': result['body'],
            'generated_by': result['generated_by'],
            'timestamp': timezone.now().isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Failed to generate donos email: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
@ratelimit(key='user', rate='10/h', method='POST', block=True)
def generate_straz_call_script(request):
    """
    Generate fake Municipal Guard call script using GPT-5 mini.

    POST /api/actions/straz/call/
    Body: {"question": "...", "ai_answer": "..."}

    Returns: {"messages": [...], "patrol_time": "...", "timestamp": "..."}
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        ai_answer = data.get('ai_answer', '')

        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)

        # Generate call script
        service = MemeticActionsService()
        result = service.generate_straz_call_script(question, ai_answer)

        logger.info(f"User {request.user.id} generated Straż call script")

        return JsonResponse({
            'messages': result['messages'],
            'patrol_time': result['patrol_time'],
            'generated_by': result['generated_by'],
            'timestamp': timezone.now().isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Failed to generate Straż call script: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
