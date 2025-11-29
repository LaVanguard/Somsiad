"""
Test script for Sprint 8 Hybrid Search functionality.
Run with: python test_hybrid_search.py
"""

import os
import sys

import django

# Fix encoding for Windows console
if sys.platform.startswith("win"):
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from knowledge.services.bm25_service import BM25Service
from knowledge.services.hybrid_search_service import HybridSearchService
from knowledge.services.rag_service import RAGService


def test_bm25_service():
    """Test BM25 keyword search."""
    print("\n" + "=" * 80)
    print("TEST 1: BM25 Keyword Search")
    print("=" * 80)

    bm25 = BM25Service()

    # Build index
    print("\n📊 Building BM25 index...")
    stats = bm25.build_index()
    print(f"✅ Index built: {stats}")

    # Save index
    print("\n💾 Saving BM25 index...")
    if bm25.save_index():
        print("✅ Index saved successfully")
    else:
        print("❌ Failed to save index")

    # Test search
    test_queries = [
        "Art. 5",
        "ogrodzenie",
        "maksymalna wysokość",
        "przeglądy techniczne",
    ]

    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = bm25.search(query, top_k=5)
        print(f"   Results: {len(results)} chunks")
        for i, (chunk_id, score) in enumerate(results[:3], 1):
            print(f"   {i}. Chunk {chunk_id[:8]}... (score: {score:.4f})")


def test_hybrid_search():
    """Test hybrid search (BM25 + vector)."""
    print("\n" + "=" * 80)
    print("TEST 2: Hybrid Search (BM25 + Vector + RRF)")
    print("=" * 80)

    hybrid = HybridSearchService()

    test_queries = [
        "Jak wysoko mogę zbudować ogrodzenie?",
        "Art. 5 wysokość płotu",
        "Jakie przeglądy są obowiązkowe?",
    ]

    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            results = hybrid.hybrid_search(query, top_k=5)
            print(f"   ✅ Results: {len(results)} chunks")
            for i, chunk in enumerate(results[:3], 1):
                chunk_id = str(chunk["id"])[:8]
                rrf_score = chunk.get("rrf_score", 0)
                content_preview = chunk["content"][:80].replace("\n", " ")
                print(f"   {i}. {chunk_id}... (RRF: {rrf_score:.4f})")
                print(f'      "{content_preview}..."')
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_rag_with_hybrid_search():
    """Test full RAG pipeline with hybrid search."""
    print("\n" + "=" * 80)
    print("TEST 3: RAG Pipeline with Hybrid Search")
    print("=" * 80)

    rag = RAGService()

    test_query = "Jakie są wymagania dotyczące wysokości ogrodzenia?"

    print(f"\n🔍 Query: '{test_query}'")
    print("\n📚 Testing with hybrid search (BM25 + vector)...")

    try:
        answer, sources, time_taken = rag.process_query(
            test_query, top_k=5, use_hybrid_search=True
        )

        print(f"✅ Answer generated in {time_taken:.2f}s")
        print(f"\n📝 Answer preview:")
        print(f"{answer[:300]}...")

        print(f"\n📚 Sources ({len(sources)}):")
        for i, source in enumerate(sources[:3], 1):
            rrf_score = source.get("rrf_score", 0)
            text_preview = source["text"][:80].replace("\n", " ")
            print(f"   {i}. RRF: {rrf_score:.4f}")
            print(f'      "{text_preview}..."')

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    # Compare with vector-only search
    print("\n📊 Testing with vector-only search (baseline)...")
    try:
        answer2, sources2, time_taken2 = rag.process_query(
            test_query, top_k=5, use_hybrid_search=False
        )

        print(f"✅ Answer generated in {time_taken2:.2f}s")
        print(f"\n📚 Sources ({len(sources2)}):")
        for i, source in enumerate(sources2[:3], 1):
            similarity = source.get("similarity", 0)
            text_preview = source["text"][:80].replace("\n", " ")
            print(f"   {i}. Similarity: {similarity:.4f}")
            print(f'      "{text_preview}..."')

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🚀 Sprint 8: Hybrid Search Testing")
    print("=" * 80)

    try:
        # Test 1: BM25 Service
        test_bm25_service()

        # Test 2: Hybrid Search Service
        test_hybrid_search()

        # Test 3: RAG with Hybrid Search
        test_rag_with_hybrid_search()

        print("\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
