"""
User profile and system prompt management views.
"""
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import logging

from .models import SystemPrompt

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@login_required
def get_profile_sidebar(request):
    """Load user profile sidebar with system prompt editor (admin only)."""
    user = request.user

    # Get or create active system prompt
    system_prompt = SystemPrompt.objects.filter(is_active=True).first()
    if not system_prompt:
        system_prompt = SystemPrompt.objects.create(is_active=True)

    html = render_to_string('partials/profile_sidebar.html', {
        'user': user,
        'system_prompt': system_prompt,
        'is_admin': user.is_staff or user.is_superuser,
    })

    return HttpResponse(html)


@require_http_methods(["POST"])
@staff_member_required
def update_system_prompt(request):
    """Update the system prompt (admin only)."""
    prompt_text = request.POST.get('prompt_text', '').strip()

    if not prompt_text:
        return HttpResponse(
            '<div class="text-red-400 text-sm">❌ Prompt nie może być pusty</div>'
        )

    try:
        # Get or create active prompt
        system_prompt = SystemPrompt.objects.filter(is_active=True).first()
        if not system_prompt:
            system_prompt = SystemPrompt.objects.create(
                prompt_text=prompt_text,
                is_active=True,
                updated_by=request.user
            )
        else:
            system_prompt.prompt_text = prompt_text
            system_prompt.updated_by = request.user
            system_prompt.save()

        logger.info(f"System prompt updated by {request.user.email}")

        return HttpResponse(
            '<div class="text-green-400 text-sm">✅ Prompt zaktualizowany pomyślnie!</div>'
        )

    except Exception as e:
        logger.error(f"Failed to update system prompt: {e}")
        return HttpResponse(
            f'<div class="text-red-400 text-sm">❌ Błąd: {str(e)}</div>'
        )
