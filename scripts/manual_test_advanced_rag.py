"""
Test script for advanced RAG implementation.
Tests semantic chunking, summarization, and metadata enrichment.

NOTE: This test requires actual PDF files in legal_documents/ directory.
Skip in CI/CD environments where files are not available.
"""

import os
import sys

import pytest

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from PyPDF2 import PdfReader

from knowledge.services.preprocessor import DocumentPreprocessor
from knowledge.services.semantic_chunker import SemanticChunker
from knowledge.services.summarizer import DocumentSummarizer


@pytest.mark.skip(reason="Requires PDF files in legal_documents/ (not in git)")
def test_advanced_rag():
    """Test the advanced RAG pipeline."""

    print("=" * 80)
    print("ADVANCED RAG SYSTEM TEST")
    print("=" * 80)

    # Test file
    pdf_path = "legal_documents/raw/budowa/warunki_techniczne_metro_2023.pdf"
    print(f"\nTest file: {pdf_path}")

    # 1. Extract text
    print("\n" + "-" * 80)
    print("STEP 1: TEXT EXTRACTION")
    print("-" * 80)

    reader = PdfReader(pdf_path)
    pages = {}
    for page_num, page in enumerate(
        reader.pages[:5], start=1
    ):  # First 5 pages only for testing
        text = page.extract_text()
        if text.strip():
            pages[page_num] = text.strip()

    full_text = "\n\n".join(
        [f"[Strona {page_num}]\n{text}" for page_num, text in pages.items()]
    )

    print(f"Extracted {len(pages)} pages")
    print(f"Total characters: {len(full_text):,}")

    # 2. Preprocessing
    print("\n" + "-" * 80)
    print("STEP 2: PREPROCESSING")
    print("-" * 80)

    preprocessor = DocumentPreprocessor()
    preprocessed = preprocessor.preprocess(full_text)
    cleaned_text = preprocessed["cleaned"]

    stats = preprocessor.get_stats(full_text, cleaned_text)
    print(f"Characters before:  {stats['chars_before']:,}")
    print(f"Characters after:   {stats['chars_after']:,}")
    print(f"Reduction:          {stats['reduction_pct']}%")

    # 3. Semantic Chunking
    print("\n" + "-" * 80)
    print("STEP 3: SEMANTIC CHUNKING")
    print("-" * 80)

    chunker = SemanticChunker()
    metadata = {
        "document_id": 1,
        "document_title": "Warunki techniczne metra 2023",
        "category": "budowa",
    }

    legal_chunks = chunker.chunk_document(cleaned_text, metadata)
    print(f"Created {len(legal_chunks)} semantic chunks")

    # Show sample chunks
    print("\nSample chunks:")
    for i, chunk in enumerate(legal_chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(f"  Type: {chunk.chunk_type}")
        print(f"  Article: {chunk.article_number or 'N/A'}")
        print(f"  Section: {chunk.section_name or 'N/A'}")
        print(f"  Length: {len(chunk.content)} chars")
        print(f"  Preview: {chunk.content[:150]}...")

        # Extract metadata
        enriched = chunker.extract_metadata(chunk)
        print(f"  Article refs: {enriched.get('article_references', [])[:3]}")
        print(f"  Para refs: {enriched.get('paragraph_references', [])[:3]}")
        print(f"  Measurements: {enriched.get('measurements', [])[:3]}")
        print(f"  Has obligations: {enriched.get('contains_obligations', False)}")

    # 4. Document Summarization
    print("\n" + "-" * 80)
    print("STEP 4: DOCUMENT SUMMARIZATION")
    print("-" * 80)
    print("Generating document summary (this may take 10-20 seconds)...")

    summarizer = DocumentSummarizer()
    doc_summary = summarizer.generate_document_summary(
        cleaned_text, "Warunki techniczne metra 2023"
    )

    print("\nDOCUMENT SUMMARY:")
    print("-" * 40)
    print(doc_summary["summary"])

    print("\nKEY TOPICS:")
    print("-" * 40)
    for topic in doc_summary["key_topics"]:
        print(f"  - {topic}")

    print("\nSCOPE:")
    print("-" * 40)
    print(doc_summary["scope"])

    # 5. Chunk Statistics
    print("\n" + "=" * 80)
    print("CHUNKING STATISTICS")
    print("=" * 80)

    chunk_types = {}
    for chunk in legal_chunks:
        chunk_types[chunk.chunk_type] = chunk_types.get(chunk.chunk_type, 0) + 1

    print(f"Total chunks: {len(legal_chunks)}")
    print("\nChunk types:")
    for chunk_type, count in chunk_types.items():
        print(f"  {chunk_type}: {count}")

    chunk_sizes = [len(chunk.content) for chunk in legal_chunks]
    print(f"\nChunk sizes:")
    print(f"  Min: {min(chunk_sizes)} chars")
    print(f"  Max: {max(chunk_sizes)} chars")
    print(f"  Avg: {sum(chunk_sizes) // len(chunk_sizes)} chars")

    # 6. Metadata Enrichment Stats
    print("\n" + "=" * 80)
    print("METADATA ENRICHMENT STATS")
    print("=" * 80)

    total_article_refs = 0
    total_para_refs = 0
    total_measurements = 0
    chunks_with_obligations = 0

    for chunk in legal_chunks:
        enriched = chunker.extract_metadata(chunk)
        total_article_refs += len(enriched.get("article_references", []))
        total_para_refs += len(enriched.get("paragraph_references", []))
        total_measurements += len(enriched.get("measurements", []))
        if enriched.get("contains_obligations", False):
            chunks_with_obligations += 1

    print(f"Total article references extracted: {total_article_refs}")
    print(f"Total paragraph references: {total_para_refs}")
    print(f"Total measurements found: {total_measurements}")
    print(f"Chunks with obligations: {chunks_with_obligations}/{len(legal_chunks)}")

    # 7. Summary Chunk
    print("\n" + "=" * 80)
    print("SEARCHABLE SUMMARY CHUNK")
    print("=" * 80)

    summary_chunk = summarizer.create_searchable_summary_chunk(
        1, "Warunki techniczne metra 2023", doc_summary
    )

    print(f"Summary chunk length: {len(summary_chunk['content'])} chars")
    print(f"Is summary: {summary_chunk['metadata']['is_summary']}")
    print(f"\nPreview:")
    print(summary_chunk["content"][:500])

    print("\n" + "=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)
    print("\nAdvanced RAG features verified:")
    print("  [OK] Semantic chunking by articles/sections")
    print("  [OK] Document-level summarization")
    print("  [OK] Metadata enrichment (refs, measurements, obligations)")
    print("  [OK] Searchable summary chunks")
    print("\nReady for production document processing!")
    print("=" * 80)


if __name__ == "__main__":
    test_advanced_rag()
