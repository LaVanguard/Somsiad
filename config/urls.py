"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.memetic_views import (
    generate_donos_email,
    generate_prosecutor_letter,
    generate_straz_call_script,
)
from accounts.signup_blocked_view import signup_blocked
from accounts.views import home, query_api, query_stream_api
from knowledge.document_views import (
    delete_document,
    list_documents,
    process_all_documents,
    process_document,
    reprocess_document,
    upload_document,
)
from queries.profile_views import get_profile_sidebar, update_system_prompt
from queries.views import (
    create_conversation,
    delete_conversation,
    list_conversations,
    load_conversation,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # BLOCK SIGNUP - Override allauth signup URLs
    path("accounts/signup/", signup_blocked, name="account_signup"),
    # Allow login and other auth endpoints
    path("accounts/", include("allauth.urls")),
    path("", home, name="home"),
    path("api/query/", query_api, name="query_api"),
    path("api/query/stream/", query_stream_api, name="query_stream_api"),
    # Document management endpoints
    path("api/documents/upload/", upload_document, name="upload_document"),
    path(
        "api/documents/<int:document_id>/process/",
        process_document,
        name="process_document",
    ),
    path(
        "api/documents/<int:document_id>/reprocess/",
        reprocess_document,
        name="reprocess_document",
    ),
    path(
        "api/documents/<int:document_id>/delete/",
        delete_document,
        name="delete_document",
    ),
    path(
        "api/documents/process-all/",
        process_all_documents,
        name="process_all_documents",
    ),
    path("api/documents/list/", list_documents, name="list_documents"),
    # Conversation endpoints
    path("api/conversations/create/", create_conversation, name="create_conversation"),
    path("api/conversations/list/", list_conversations, name="list_conversations"),
    path(
        "api/conversations/<int:conversation_id>/",
        load_conversation,
        name="load_conversation",
    ),
    path(
        "api/conversations/<int:conversation_id>/delete/",
        delete_conversation,
        name="delete_conversation",
    ),
    # Profile endpoints
    path("api/profile/", get_profile_sidebar, name="get_profile"),
    path(
        "api/profile/update-prompt/", update_system_prompt, name="update_system_prompt"
    ),
    # Memetic Actions (Sprint 9)
    path(
        "api/actions/prosecutor/generate/",
        generate_prosecutor_letter,
        name="generate_prosecutor_letter",
    ),
    path(
        "api/actions/donos/generate/", generate_donos_email, name="generate_donos_email"
    ),
    path(
        "api/actions/straz/call/",
        generate_straz_call_script,
        name="generate_straz_call",
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
