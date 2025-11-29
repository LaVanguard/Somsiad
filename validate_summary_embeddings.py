"""
Validate hierarchical summary embeddings (PRD v2.1 FR-1.3)
Priority 2 Task - Summary Embedding Validation
"""

import os
import sys

import django

# Fix Windows encoding for Unicode symbols
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import logging

from knowledge.models import Document, Embedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_summary_embeddings():
    """
    Validate that all processed documents have hierarchical summary embeddings.
    PRD v2.1 FR-1.3 requires:
    - 3-part summaries (STRESZCZENIE, KLUCZOWE TEMATY, ZAKRES ZASTOSOWANIA)
    - Summaries embedded as searchable chunks
    """
    print("=" * 70)
    print("HIERARCHICAL SUMMARY EMBEDDING VALIDATION (PRD v2.1 FR-1.3)")
    print("=" * 70)
    print()

    # Get all processed documents
    processed_docs = Document.objects.filter(processed=True).order_by("id")
    total_docs = processed_docs.count()

    if total_docs == 0:
        print("⚠️  No processed documents found")
        print()
        return

    print(f"📊 Found {total_docs} processed documents")
    print()

    docs_with_summary = 0
    docs_without_summary = 0
    summary_details = []

    for doc in processed_docs:
        # Check if document has a summary chunk
        summary_chunks = Embedding.objects.filter(
            document=doc, metadata__is_document_summary=True
        )

        has_summary = summary_chunks.exists()
        summary_count = summary_chunks.count()

        if has_summary:
            docs_with_summary += 1

            # Get the summary chunk
            summary = summary_chunks.first()
            chunk_text = summary.chunk_text

            # Validate 3-part structure
            has_streszczenie = "STRESZCZENIE:" in chunk_text
            has_tematy = "KLUCZOWE TEMATY:" in chunk_text
            has_zakres = "ZAKRES ZASTOSOWANIA:" in chunk_text

            is_complete = has_streszczenie and has_tematy and has_zakres

            status = "✅ COMPLETE" if is_complete else "⚠️  PARTIAL"

            summary_details.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "has_summary": True,
                    "summary_count": summary_count,
                    "is_complete": is_complete,
                    "status": status,
                    "parts": {
                        "streszczenie": has_streszczenie,
                        "tematy": has_tematy,
                        "zakres": has_zakres,
                    },
                }
            )

            print(f"{status} - Doc {doc.id}: {doc.title[:50]}")
            if summary_count > 1:
                print(f"         ⚠️  Multiple summary chunks found: {summary_count}")
            if not is_complete:
                missing = []
                if not has_streszczenie:
                    missing.append("STRESZCZENIE")
                if not has_tematy:
                    missing.append("KLUCZOWE TEMATY")
                if not has_zakres:
                    missing.append("ZAKRES ZASTOSOWANIA")
                print(f"         Missing: {', '.join(missing)}")
        else:
            docs_without_summary += 1
            summary_details.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "has_summary": False,
                    "summary_count": 0,
                    "is_complete": False,
                    "status": "❌ NO SUMMARY",
                }
            )
            print(f"❌ NO SUMMARY - Doc {doc.id}: {doc.title[:50]}")

    print()
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print()
    print(f"Total Processed Documents: {total_docs}")
    print(
        f"Documents WITH Summary:    {docs_with_summary} ({docs_with_summary/total_docs*100:.1f}%)"
    )
    print(
        f"Documents WITHOUT Summary: {docs_without_summary} ({docs_without_summary/total_docs*100:.1f}%)"
    )
    print()

    # Check PRD compliance
    compliance_pct = (docs_with_summary / total_docs * 100) if total_docs > 0 else 0

    if compliance_pct == 100:
        print("✅ PRD v2.1 FR-1.3 COMPLIANCE: PASS (100% documents have summaries)")
    elif compliance_pct >= 90:
        print(
            f"⚠️  PRD v2.1 FR-1.3 COMPLIANCE: PARTIAL ({compliance_pct:.1f}% coverage)"
        )
    else:
        print(f"❌ PRD v2.1 FR-1.3 COMPLIANCE: FAIL ({compliance_pct:.1f}% coverage)")

    print()
    print("📋 Requirements (PRD v2.1 FR-1.3):")
    print("   - DocumentSummarizer generates 3-part summaries")
    print("   - Summaries include: STRESZCZENIE, KLUCZOWE TEMATY, ZAKRES ZASTOSOWANIA")
    print("   - Summaries are embedded as searchable chunks")
    print("   - Summary chunks have metadata flag: is_document_summary=True")
    print()

    # Show sample summary if available
    if summary_details and summary_details[0]["has_summary"]:
        print("=" * 70)
        print("SAMPLE SUMMARY CHUNK")
        print("=" * 70)
        sample_doc = processed_docs.first()
        sample_summary = Embedding.objects.filter(
            document=sample_doc, metadata__is_document_summary=True
        ).first()

        if sample_summary:
            print(f"\nDocument: {sample_doc.title}")
            print(f"Summary Length: {len(sample_summary.chunk_text)} chars")
            print(f"\nFirst 500 chars:")
            print("-" * 70)
            print(sample_summary.chunk_text[:500] + "...")
            print()

    return summary_details


if __name__ == "__main__":
    validate_summary_embeddings()
