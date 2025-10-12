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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import home, query_api, query_stream_api
from knowledge.document_views import (
    upload_document,
    process_document,
    process_all_documents,
    reprocess_document,
    list_documents
)
from queries.views import (
    create_conversation,
    list_conversations,
    load_conversation,
    delete_conversation
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', home, name='home'),
    path('api/query/', query_api, name='query_api'),
    path('api/query/stream/', query_stream_api, name='query_stream_api'),

    # Document management endpoints
    path('api/documents/upload/', upload_document, name='upload_document'),
    path('api/documents/<int:document_id>/process/', process_document, name='process_document'),
    path('api/documents/<int:document_id>/reprocess/', reprocess_document, name='reprocess_document'),
    path('api/documents/process-all/', process_all_documents, name='process_all_documents'),
    path('api/documents/list/', list_documents, name='list_documents'),

    # Conversation endpoints
    path('api/conversations/create/', create_conversation, name='create_conversation'),
    path('api/conversations/list/', list_conversations, name='list_conversations'),
    path('api/conversations/<int:conversation_id>/', load_conversation, name='load_conversation'),
    path('api/conversations/<int:conversation_id>/delete/', delete_conversation, name='delete_conversation'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)