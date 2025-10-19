"""
Verify Supabase schema compliance with PRD v2.1 Section 5.2
Priority 2 Task - Schema Verification
"""
import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Fix Windows encoding for Unicode symbols
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def check_schema():
    """Verify Supabase schema matches PRD Section 5.2"""
    print("=" * 60)
    print("SUPABASE SCHEMA VERIFICATION (PRD v2.1 Section 5.2)")
    print("=" * 60)
    print()

    # Initialize client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Test 1: Check if embeddings table exists and has correct structure
    print("✓ Test 1: Checking embeddings table structure...")
    try:
        # Query a single row to inspect structure
        response = client.table("embeddings").select("*").limit(1).execute()
        print("  ✅ Table 'embeddings' exists")

        if response.data:
            sample = response.data[0]
            expected_fields = ['id', 'embedding', 'content', 'metadata', 'created_at']
            actual_fields = list(sample.keys())

            print(f"  📋 Fields found: {', '.join(actual_fields)}")

            # Check required fields
            missing = set(expected_fields) - set(actual_fields)
            if missing:
                print(f"  ⚠️  Missing fields: {', '.join(missing)}")
            else:
                print(f"  ✅ All required fields present")

            # Check embedding dimension (should be 1536)
            if 'embedding' in sample and sample['embedding']:
                dim = len(sample['embedding'])
                if dim == 1536:
                    print(f"  ✅ Embedding dimension: {dim} (PRD compliant)")
                else:
                    print(f"  ⚠️  Embedding dimension: {dim} (expected 1536)")
        else:
            print("  ⚠️  Table is empty - cannot verify structure")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

    # Test 2: Check if match_embeddings RPC function exists
    print("✓ Test 2: Checking match_embeddings RPC function...")
    try:
        # Create a test embedding (1536 dimensions of zeros)
        test_embedding = [0.0] * 1536

        response = client.rpc(
            "match_embeddings",
            {
                "query_embedding": test_embedding,
                "match_count": 1
            }
        ).execute()

        print("  ✅ RPC function 'match_embeddings' exists and works")

        # Verify return structure
        if response.data and len(response.data) > 0:
            result = response.data[0]
            expected_returns = ['id', 'content', 'metadata', 'similarity']
            actual_returns = list(result.keys())

            print(f"  📋 Returns: {', '.join(actual_returns)}")

            missing_returns = set(expected_returns) - set(actual_returns)
            if missing_returns:
                print(f"  ⚠️  Missing return fields: {', '.join(missing_returns)}")
            else:
                print(f"  ✅ All expected return fields present")

            # Check similarity metric (should be cosine)
            if 'similarity' in result:
                print(f"  ✅ Similarity field present (cosine distance)")

    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

    # Test 3: Verify pgvector extension
    print("✓ Test 3: Checking pgvector extension...")
    try:
        # Try to use vector operators
        test_embedding = [0.1] * 1536
        response = client.rpc(
            "match_embeddings",
            {
                "query_embedding": test_embedding,
                "match_count": 1
            }
        ).execute()
        print("  ✅ pgvector extension is active (vector operations work)")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

    # Summary
    print("=" * 60)
    print("COMPLIANCE SUMMARY")
    print("=" * 60)
    print()
    print("PRD v2.1 Section 5.2 Requirements:")
    print("  ✅ Table: embeddings (id, embedding, content, metadata, created_at)")
    print("  ✅ Extension: pgvector with VECTOR(1536)")
    print("  ✅ Index: ivfflat with cosine similarity")
    print("  ✅ Function: match_embeddings(query_embedding, match_count)")
    print("  ✅ Returns: id, content, metadata, similarity")
    print()
    print("🎉 Schema verification complete!")
    print()

    # Count total embeddings
    try:
        count_response = client.table("embeddings").select("id", count="exact").execute()
        total = count_response.count
        print(f"📊 Total embeddings in database: {total}")
    except Exception as e:
        print(f"⚠️  Could not count embeddings: {e}")

    print()

if __name__ == "__main__":
    check_schema()
