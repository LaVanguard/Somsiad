"""
Django management command to process documents for RAG.
Usage: python manage.py process_documents [--all] [--document-id ID] [--reprocess]
"""
from django.core.management.base import BaseCommand, CommandError
from knowledge.models import Document
from knowledge.services.document_processor import DocumentProcessor


class Command(BaseCommand):
    help = 'Process PDF documents for RAG embeddings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all unprocessed documents'
        )
        parser.add_argument(
            '--document-id',
            type=int,
            help='Process specific document by ID'
        )
        parser.add_argument(
            '--reprocess',
            action='store_true',
            help='Reprocess document (delete old embeddings)'
        )

    def handle(self, *args, **options):
        processor = DocumentProcessor()

        # Process all unprocessed documents
        if options['all']:
            self.stdout.write(self.style.WARNING('Processing all unprocessed documents...'))
            results = processor.process_all_unprocessed()

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Processing complete:\n"
                    f"  - Total: {results['total']}\n"
                    f"  - Success: {results['success']}\n"
                    f"  - Failed: {results['failed']}"
                )
            )
            return

        # Process specific document
        if options['document_id']:
            try:
                document = Document.objects.get(id=options['document_id'])
            except Document.DoesNotExist:
                raise CommandError(f"Document with ID {options['document_id']} not found")

            self.stdout.write(f"Processing document: {document.title}")

            if options['reprocess']:
                success = processor.reprocess_document(document)
            else:
                success = processor.process_document(document)

            if success:
                self.stdout.write(self.style.SUCCESS(f"✅ Successfully processed: {document.title}"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Failed to process: {document.title}"))
            return

        # No arguments provided
        raise CommandError(
            'Please specify --all or --document-id\n'
            'Examples:\n'
            '  python manage.py process_documents --all\n'
            '  python manage.py process_documents --document-id 1\n'
            '  python manage.py process_documents --document-id 1 --reprocess'
        )
