"""
Test script to verify RAG configuration is PRD-compliant.
Run: python test_rag_config.py
"""
import os
import sys
import django

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from knowledge.services.document_processor import DocumentProcessor
from knowledge.services.rag_service import RAGService
from django.conf import settings

def test_rag_config():
    """Verify all RAG configurations match PRD v2.1 Section 2.2"""

    print("=" * 60)
    print("RAG Configuration Validation (PRD v2.1)")
    print("=" * 60)

    # Test RAGService configuration
    print("\n1. RAGService Configuration:")
    rag = RAGService()
    chunk_size = rag.text_splitter._chunk_size
    chunk_overlap = rag.text_splitter._chunk_overlap

    print(f"   ✓ chunk_size: {chunk_size} (expected: 1500)")
    print(f"   ✓ chunk_overlap: {chunk_overlap} (expected: 200)")

    assert chunk_size == 1500, f"❌ chunk_size should be 1500, got {chunk_size}"
    assert chunk_overlap == 200, f"❌ chunk_overlap should be 200, got {chunk_overlap}"

    # Test DocumentProcessor configuration
    print("\n2. DocumentProcessor Configuration:")
    processor = DocumentProcessor()

    print(f"   ✓ SemanticChunker max_chunk_size: {processor.semantic_chunker.max_chunk_size}")
    print(f"   ✓ Preprocessing enabled: {processor.enable_preprocessing}")
    print(f"   ✓ Semantic chunking enabled: {processor.use_semantic_chunking}")
    print(f"   ✓ Summaries enabled: {processor.generate_summaries}")

    assert processor.semantic_chunker.max_chunk_size == 1500
    assert processor.use_semantic_chunking == True
    assert processor.generate_summaries == True

    # Test settings.py RAG_CONFIG
    print("\n3. settings.RAG_CONFIG:")
    if hasattr(settings, 'RAG_CONFIG'):
        rag_config = settings.RAG_CONFIG
        print(f"   ✓ EMBEDDING_MODEL: {rag_config['EMBEDDING_MODEL']}")
        print(f"   ✓ EMBEDDING_DIMENSION: {rag_config['EMBEDDING_DIMENSION']}")
        print(f"   ✓ GENERATION_MODEL: {rag_config['GENERATION_MODEL']}")
        print(f"   ✓ TEMPERATURE: {rag_config['TEMPERATURE']}")
        print(f"   ✓ TOP_K: {rag_config['TOP_K']}")
        print(f"   ✓ MAX_CHUNK_SIZE: {rag_config['MAX_CHUNK_SIZE']}")
        print(f"   ✓ CHUNK_OVERLAP: {rag_config['CHUNK_OVERLAP']}")

        assert rag_config['EMBEDDING_MODEL'] == 'text-embedding-3-small'
        assert rag_config['EMBEDDING_DIMENSION'] == 1536
        assert rag_config['GENERATION_MODEL'] == 'gpt-5-mini'
        assert rag_config['TEMPERATURE'] == 0.3
        assert rag_config['TOP_K'] == 5
        assert rag_config['MAX_CHUNK_SIZE'] == 1500
        assert rag_config['CHUNK_OVERLAP'] == 200
    else:
        print("   ⚠️ RAG_CONFIG not found in settings")

    # Summary
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - PRD v2.1 COMPLIANT")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Process a sample document to verify semantic chunking")
    print("  2. Check Supabase schema for pgvector table")
    print("  3. Test query endpoint with streaming")

if __name__ == '__main__':
    try:
        test_rag_config()
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
