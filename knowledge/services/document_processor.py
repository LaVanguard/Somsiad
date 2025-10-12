"""
Document processing service for PDF extraction and embedding generation.
Sprint 2 implementation.
"""
import logging
from typing import List, Dict
from PyPDF2 import PdfReader
from django.core.files.uploadedfile import UploadedFile
from knowledge.models import Document, Embedding
from knowledge.services.rag_service import RAGService
from knowledge.services.preprocessor import DocumentPreprocessor
from knowledge.services.semantic_chunker import SemanticChunker, LegalChunk
from knowledge.services.summarizer import DocumentSummarizer

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Handles PDF document processing:
    1. Extract text from PDF
    2. Preprocess and clean text
    3. Chunk text into smaller pieces
    4. Generate embeddings
    5. Store in Supabase + Django database
    """

    def __init__(
        self,
        enable_preprocessing: bool = True,
        use_semantic_chunking: bool = True,
        generate_summaries: bool = True
    ):
        self.rag_service = RAGService()
        self.preprocessor = DocumentPreprocessor()
        self.semantic_chunker = SemanticChunker()
        self.summarizer = DocumentSummarizer()
        self.enable_preprocessing = enable_preprocessing
        self.use_semantic_chunking = use_semantic_chunking
        self.generate_summaries = generate_summaries

    def extract_text_from_pdf(self, file_path: str) -> Dict[int, str]:
        """
        Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Dict mapping page number to text content
        """
        try:
            reader = PdfReader(file_path)
            pages = {}

            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    pages[page_num] = text.strip()

            logger.info(f"Extracted {len(pages)} pages from {file_path}")
            return pages

        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            raise

    def process_document(self, document: Document) -> bool:
        """
        Process a Document: extract, chunk, embed, and store.

        Args:
            document: Document model instance

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing document: {document.title} (ID: {document.id})")

            # 1. Extract text from PDF
            file_path = document.file.path
            pages = self.extract_text_from_pdf(file_path)

            if not pages:
                logger.warning(f"No text extracted from {document.title}")
                return False

            # 2. Combine all pages with page markers
            full_text = "\n\n".join([
                f"[Strona {page_num}]\n{text}"
                for page_num, text in pages.items()
            ])

            # 3. Preprocess text (clean administrative noise)
            if self.enable_preprocessing:
                logger.info(f"Preprocessing {document.title}...")
                preprocessed = self.preprocessor.preprocess(full_text)
                stats = self.preprocessor.get_stats(preprocessed['raw'], preprocessed['cleaned'])
                logger.info(
                    f"Preprocessing stats: {stats['chars_removed']} chars removed "
                    f"({stats['reduction_pct']}% reduction)"
                )
                full_text = preprocessed['cleaned']

            # 4. Generate document summary (if enabled)
            doc_summary = None
            if self.generate_summaries:
                logger.info(f"Generating document summary for {document.title}...")
                doc_summary = self.summarizer.generate_document_summary(
                    full_text,
                    document.title
                )
                logger.info(f"Summary generated: {len(doc_summary['summary'])} chars")

            # 5. Chunk text (semantic or fixed-size)
            base_metadata = {
                "document_id": document.id,
                "document_title": document.title,
                "category": document.category
            }

            if self.use_semantic_chunking:
                logger.info("Using semantic chunking (by articles)...")
                legal_chunks = self.semantic_chunker.chunk_document(full_text, base_metadata)
                logger.info(f"Created {len(legal_chunks)} semantic chunks")

                # Enrich metadata for each chunk
                enriched_chunks = []
                for chunk in legal_chunks:
                    enhanced_metadata = self.semantic_chunker.extract_metadata(chunk)
                    chunk.metadata.update(enhanced_metadata)
                    enriched_chunks.append(chunk)

                # Convert to format expected by RAG service
                texts = [chunk.content for chunk in enriched_chunks]
                chunk_metadata_list = [
                    {**base_metadata, **chunk.to_dict()}
                    for chunk in enriched_chunks
                ]
            else:
                # Fallback: Use original fixed-size chunking
                logger.info("Using fixed-size chunking...")
                langchain_chunks = self.rag_service.chunk_document(full_text, base_metadata)
                texts = [chunk.page_content for chunk in langchain_chunks]
                chunk_metadata_list = [
                    {**base_metadata, "chunk_index": i}
                    for i in range(len(texts))
                ]

            logger.info(f"Created {len(texts)} chunks from {document.title}")

            # 6. Add document summary as searchable chunk (if generated)
            if doc_summary:
                logger.info("Adding document summary as searchable chunk...")
                summary_chunk = self.summarizer.create_searchable_summary_chunk(
                    document.id,
                    document.title,
                    doc_summary
                )
                texts.insert(0, summary_chunk['content'])
                chunk_metadata_list.insert(0, summary_chunk['metadata'])
                logger.info("Document summary chunk added")

            # 7. Generate embeddings for all chunks (including summary)
            embeddings = self.rag_service.generate_embeddings(texts)
            logger.info(f"Generated {len(embeddings)} embeddings")

            # 8. Store in Supabase
            embedding_ids = self.rag_service.store_embeddings(
                embeddings,
                texts,
                chunk_metadata_list
            )
            logger.info(f"Stored {len(embedding_ids)} embeddings in Supabase")

            # 9. Store references in Django database
            for i, (text, emb_id, metadata) in enumerate(zip(texts, embedding_ids, chunk_metadata_list)):
                Embedding.objects.create(
                    document=document,
                    chunk_text=text[:5000],  # Truncate if needed
                    embedding_id=str(emb_id),
                    metadata=metadata
                )

            # 10. Mark document as processed
            document.processed = True
            document.save()

            # Log summary statistics
            logger.info(
                f"✅ Successfully processed {document.title}:\n"
                f"   - Chunks: {len(texts)}\n"
                f"   - Embeddings: {len(embeddings)}\n"
                f"   - Summary: {'Yes' if doc_summary else 'No'}\n"
                f"   - Semantic chunking: {'Yes' if self.use_semantic_chunking else 'No'}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to process {document.title}: {e}", exc_info=True)
            return False

    def _extract_page_range(self, text: str) -> str:
        """
        Extract page range from chunk text (if it contains page markers).

        Args:
            text: Chunk text with potential [Strona X] markers

        Returns:
            String like "1-3" or "5"
        """
        import re
        page_markers = re.findall(r'\[Strona (\d+)\]', text)

        if not page_markers:
            return "unknown"

        pages = sorted(set(int(p) for p in page_markers))

        if len(pages) == 1:
            return str(pages[0])
        else:
            return f"{pages[0]}-{pages[-1]}"

    def process_all_unprocessed(self) -> Dict[str, int]:
        """
        Process all unprocessed documents in the database.

        Returns:
            Dict with success/failure counts
        """
        unprocessed = Document.objects.filter(processed=False)
        total = unprocessed.count()

        if total == 0:
            logger.info("No unprocessed documents found")
            return {"total": 0, "success": 0, "failed": 0}

        logger.info(f"Found {total} unprocessed documents")

        success_count = 0
        failed_count = 0

        for document in unprocessed:
            try:
                if self.process_document(document):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Unexpected error processing {document.title}: {e}")
                failed_count += 1

        logger.info(
            f"Processing complete: {success_count} succeeded, "
            f"{failed_count} failed out of {total} total"
        )

        return {
            "total": total,
            "success": success_count,
            "failed": failed_count
        }

    def reprocess_document(self, document: Document) -> bool:
        """
        Reprocess a document (delete old embeddings and create new ones).

        Args:
            document: Document to reprocess

        Returns:
            True if successful
        """
        try:
            logger.info(f"Reprocessing document: {document.title}")

            # 1. Delete old embeddings from Django
            old_embeddings = document.embeddings.all()
            embedding_ids = [emb.embedding_id for emb in old_embeddings]
            old_embeddings.delete()

            # 2. Delete old embeddings from Supabase
            if embedding_ids:
                for emb_id in embedding_ids:
                    self.rag_service.supabase.table("embeddings").delete().eq("id", emb_id).execute()
                logger.info(f"Deleted {len(embedding_ids)} old embeddings")

            # 3. Mark as unprocessed and reprocess
            document.processed = False
            document.save()

            return self.process_document(document)

        except Exception as e:
            logger.error(f"Failed to reprocess {document.title}: {e}")
            return False
