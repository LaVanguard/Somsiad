"""
Document management views for HTMX sidebar operations.
Handles upload, processing, and status updates.
"""
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import logging

from knowledge.models import Document
from knowledge.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@login_required
def upload_document(request):
    """Upload a new document via HTMX."""
    title = request.POST.get('title', '').strip()
    category = request.POST.get('category', 'budowa')
    file = request.FILES.get('file')

    # Validation
    if not title:
        return HttpResponse(
            '<div class="text-red-400">❌ Podaj tytuł dokumentu</div>'
        )

    if not file:
        return HttpResponse(
            '<div class="text-red-400">❌ Wybierz plik PDF</div>'
        )

    if not file.name.endswith('.pdf'):
        return HttpResponse(
            '<div class="text-red-400">❌ Tylko pliki PDF są dozwolone</div>'
        )

    try:
        # Create document
        document = Document.objects.create(
            title=title,
            category=category,
            file=file,
            processed=False
        )

        logger.info(f"Document uploaded: {document.title} (ID: {document.id})")

        # Return success message
        return HttpResponse(
            f'''<div class="text-green-400">
                ✅ Dokument "{title}" został dodany!<br>
                <span class="text-xs">Kliknij "Przetwórz" aby go przetworzyć</span>
            </div>
            <script>
                // Refresh document lists after 2 seconds
                setTimeout(() => {{
                    htmx.ajax('GET', '/api/documents/list/?status=unprocessed', {{target: '#unprocessed-list'}});
                }}, 2000);
            </script>'''
        )

    except Exception as e:
        logger.error(f"Document upload failed: {e}", exc_info=True)
        return HttpResponse(
            f'<div class="text-red-400">❌ Błąd: {str(e)}</div>'
        )


@require_http_methods(["POST"])
@login_required
def process_document(request, document_id):
    """Process a single document (generate embeddings)."""
    document = get_object_or_404(Document, id=document_id)

    try:
        logger.info(f"Starting document processing: {document.title}")

        # Process document
        processor = DocumentProcessor()
        success = processor.process_document(document)

        if success:
            return HttpResponse(
                f'''<div class="text-green-400">
                    ✅ Dokument "{document.title}" przetworzony!<br>
                    <span class="text-xs">Utworzono {document.embeddings.count()} chunków</span>
                </div>
                <script>
                    // Refresh both lists
                    setTimeout(() => {{
                        htmx.ajax('GET', '/api/documents/list/?status=processed', {{target: '#processed-list'}});
                        htmx.ajax('GET', '/api/documents/list/?status=unprocessed', {{target: '#unprocessed-list'}});
                    }}, 2000);
                </script>'''
            )
        else:
            return HttpResponse(
                f'<div class="text-red-400">❌ Przetwarzanie {document.title} nie powiodło się</div>'
            )

    except Exception as e:
        logger.error(f"Document processing failed: {e}", exc_info=True)
        return HttpResponse(
            f'<div class="text-red-400">❌ Błąd: {str(e)}</div>'
        )


@require_http_methods(["POST"])
@login_required
def process_all_documents(request):
    """Process all unprocessed documents."""
    unprocessed = Document.objects.filter(processed=False)
    count = unprocessed.count()

    if count == 0:
        return HttpResponse(
            '<div class="text-yellow-400">⚠️ Brak dokumentów do przetworzenia</div>'
        )

    try:
        processor = DocumentProcessor()
        results = processor.process_all_unprocessed()

        return HttpResponse(
            f'''<div class="text-green-400">
                ✅ Przetworzono {results['success']}/{results['total']} dokumentów!<br>
                <span class="text-xs">Nieudane: {results['failed']}</span>
            </div>
            <script>
                // Refresh both lists
                setTimeout(() => {{
                    htmx.ajax('GET', '/api/documents/list/?status=processed', {{target: '#processed-list'}});
                    htmx.ajax('GET', '/api/documents/list/?status=unprocessed', {{target: '#unprocessed-list'}});
                }}, 3000);
            </script>'''
        )

    except Exception as e:
        logger.error(f"Batch processing failed: {e}", exc_info=True)
        return HttpResponse(
            f'<div class="text-red-400">❌ Błąd: {str(e)}</div>'
        )


@require_http_methods(["POST"])
@login_required
def reprocess_document(request, document_id):
    """Reprocess a document (delete old embeddings and create new)."""
    document = get_object_or_404(Document, id=document_id)

    try:
        processor = DocumentProcessor()
        success = processor.reprocess_document(document)

        if success:
            return HttpResponse(
                f'''<div class="text-green-400">
                    ✅ Dokument "{document.title}" przetworzony ponownie!
                </div>
                <script>
                    setTimeout(() => {{
                        htmx.ajax('GET', '/api/documents/list/?status=processed', {{target: '#processed-list'}});
                    }}, 2000);
                </script>'''
            )
        else:
            return HttpResponse(
                f'<div class="text-red-400">❌ Ponowne przetwarzanie nie powiodło się</div>'
            )

    except Exception as e:
        logger.error(f"Reprocessing failed: {e}", exc_info=True)
        return HttpResponse(
            f'<div class="text-red-400">❌ Błąd: {str(e)}</div>'
        )


@require_http_methods(["GET"])
@login_required
def list_documents(request):
    """List documents (processed or unprocessed) for HTMX refresh."""
    status = request.GET.get('status', 'processed')

    if status == 'processed':
        documents = Document.objects.filter(processed=True).order_by('-uploaded_at')
        template = 'partials/processed_documents.html'
    else:
        documents = Document.objects.filter(processed=False).order_by('-uploaded_at')
        template = 'partials/unprocessed_documents.html'

    html = render_to_string(template, {'documents': documents})
    return HttpResponse(html)
