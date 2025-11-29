"""Test Supabase connection and setup."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from supabase import create_client

print(f"Supabase URL: {settings.SUPABASE_URL}")
print(f"Key length: {len(settings.SUPABASE_KEY)} chars")

try:
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    print("[OK] Supabase client created")

    # Check embeddings table
    result = client.table("embeddings").select("id").limit(1).execute()
    print(f"[OK] Embeddings table exists (records: {len(result.data)})")

    # Check match_embeddings function
    test_emb = [0.1] * 1536
    search = client.rpc(
        "match_embeddings", {"query_embedding": test_emb, "match_count": 1}
    ).execute()
    print(f"[OK] match_embeddings function works (results: {len(search.data)})")

    print("\n[SUCCESS] Supabase is fully configured and ready!")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback

    traceback.print_exc()
