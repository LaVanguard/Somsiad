import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from accounts.decorators import ajax_login_required

from .models import Conversation, Query

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@login_required
def create_conversation(request):
    """Create a new conversation for the user."""
    try:
        # Create conversation with placeholder title
        conversation = Conversation.objects.create(
            user=request.user, title="Nowa rozmowa"
        )

        return JsonResponse(
            {
                "success": True,
                "conversation_id": conversation.id,
                "title": conversation.title,
            }
        )
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
@ajax_login_required
def list_conversations(request):
    """List all conversations for the current user."""
    conversations = Conversation.objects.filter(user=request.user).prefetch_related(
        "queries"
    )

    # Group by date
    from datetime import datetime, timedelta

    from django.utils import timezone

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)

    grouped = {"today": [], "yesterday": [], "older": []}

    for conv in conversations:
        if conv.updated_at >= today_start:
            grouped["today"].append(conv)
        elif conv.updated_at >= yesterday_start:
            grouped["yesterday"].append(conv)
        else:
            grouped["older"].append(conv)

    html = render_to_string(
        "partials/conversations_list.html", {"grouped_conversations": grouped}
    )

    return HttpResponse(html)


@require_http_methods(["GET"])
@login_required
def load_conversation(request, conversation_id):
    """Load all messages from a specific conversation."""
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )

    queries = conversation.queries.all().order_by("created_at")

    html = render_to_string("partials/conversation_messages.html", {"queries": queries})

    return HttpResponse(html)


@require_http_methods(["DELETE"])
@login_required
def delete_conversation(request, conversation_id):
    """Delete a conversation and all its queries."""
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )

    conversation.delete()
    logger.info(f"Deleted conversation {conversation_id} for user {request.user.id}")

    # Return empty response - HTMX will remove the element
    return HttpResponse(status=200)
