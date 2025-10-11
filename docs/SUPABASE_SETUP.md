# Supabase Setup Guide for RAG Vector Storage

## Overview
Somsiad uses Supabase with pgvector extension to store and search document embeddings for RAG (Retrieval-Augmented Generation).

---

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up / Log in
3. Click **"New Project"**
4. Fill in:
   - **Name:** Law_Advisor_RAG (or your choice)
   - **Database Password:** (save this securely!)
   - **Region:** Choose closest to you
   - **Plan:** Free tier is sufficient for development
5. Wait ~2 minutes for project to initialize

---

## 2. Enable pgvector Extension

1. In your Supabase project, go to **Database → Extensions** (left sidebar)
2. Search for **"vector"**
3. Enable **"pgvector"** extension
4. Confirm activation

---

## 3. Create Embeddings Table

Go to **SQL Editor** in Supabase and run this SQL:

```sql
-- Create embeddings table with pgvector support
CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI text-embedding-3-small is 1536 dimensions
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster vector similarity search
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx
ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for metadata filtering (optional but recommended)
CREATE INDEX IF NOT EXISTS embeddings_metadata_idx
ON embeddings
USING gin (metadata);
```

**Explanation:**
- `embedding VECTOR(1536)`: Stores 1536-dimensional OpenAI embeddings
- `ivfflat` index: Approximate nearest neighbor search (fast for large datasets)
- `vector_cosine_ops`: Cosine similarity (best for semantic search)

---

## 4. Create Vector Search Function

Run this SQL to create the `match_embeddings` function:

```sql
-- Function to search for similar embeddings using cosine similarity
CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        embeddings.id,
        embeddings.content,
        embeddings.metadata,
        1 - (embeddings.embedding <=> query_embedding) AS similarity
    FROM embeddings
    WHERE
        CASE
            WHEN filter = '{}'::jsonb THEN TRUE
            ELSE embeddings.metadata @> filter
        END
    ORDER BY embeddings.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

**Explanation:**
- `<=>` operator: Cosine distance (pgvector)
- `1 - distance`: Convert to similarity score (0-1 range)
- `@>` operator: JSONB contains (for metadata filtering)
- Returns top `match_count` most similar embeddings

---

## 5. Get API Credentials

1. In Supabase, go to **Settings → API**
2. Copy these values:

   - **Project URL:** `https://xxxxx.supabase.co`
   - **anon public key:** `eyJhbGc...` (starts with eyJ)

3. Add to your `.env` file:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...your-anon-key...
```

---

## 6. Test Connection

Create a test script `test_supabase.py`:

```python
from supabase import create_client
import os
from decouple import config

# Load credentials
SUPABASE_URL = config('SUPABASE_URL')
SUPABASE_KEY = config('SUPABASE_KEY')

# Create client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test: Insert a dummy embedding
test_data = {
    "content": "Test document chunk",
    "embedding": [0.1] * 1536,  # Dummy 1536-dim vector
    "metadata": {"test": True}
}

response = supabase.table("embeddings").insert(test_data).execute()
print("Insert success:", response.data)

# Test: Search
query_embedding = [0.1] * 1536
search_response = supabase.rpc(
    "match_embeddings",
    {"query_embedding": query_embedding, "match_count": 1}
).execute()
print("Search success:", search_response.data)

# Cleanup: Delete test record
supabase.table("embeddings").delete().eq("metadata->test", True).execute()
print("Test complete!")
```

Run:
```bash
python test_supabase.py
```

If you see "Insert success" and "Search success", you're ready! 🎉

---

## 7. Security Configuration (Production)

### Row Level Security (RLS)

Enable RLS on embeddings table:

```sql
-- Enable RLS
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;

-- Policy: Allow service role (backend) full access
CREATE POLICY "Service role has full access"
ON embeddings
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Policy: Anonymous users can only read
CREATE POLICY "Public read access"
ON embeddings
FOR SELECT
TO anon
USING (true);
```

### API Key Management

- **Development:** Use `anon` key (safe for public)
- **Production:** Use `service_role` key (keep secret!)
- Store in `.env`, never commit to git

---

## 8. Monitoring & Limits

### Free Tier Limits
- **Database:** 500 MB
- **File Storage:** 1 GB
- **Bandwidth:** 5 GB/month
- **API Requests:** Unlimited (with rate limits)

### Monitor Usage
1. Go to **Settings → Usage**
2. Track database size, bandwidth, API calls

### Estimate Storage
- 1536-dim vector = ~6 KB per embedding
- 1000 embeddings = ~6 MB
- 10,000 embeddings = ~60 MB
- **500 MB = ~83,000 embeddings** (plenty for MVP!)

---

## 9. Troubleshooting

### Error: "relation 'embeddings' does not exist"
- Run the CREATE TABLE SQL again
- Check you're in the correct project

### Error: "function match_embeddings does not exist"
- Run the CREATE FUNCTION SQL again
- Ensure pgvector is enabled

### Error: "permission denied for table embeddings"
- Check RLS policies
- Use correct API key (service_role for backend)

### Slow Searches
- Check index exists: `\d embeddings` in SQL editor
- Rebuild index if needed:
  ```sql
  REINDEX INDEX embeddings_embedding_idx;
  ```

---

## 10. Alternative: Local pgvector (Development)

If you want to test locally without Supabase:

### Install PostgreSQL + pgvector

**Windows:**
```bash
# Install PostgreSQL from postgresql.org
# Then install pgvector extension
# (Requires compilation - advanced)
```

**Mac:**
```bash
brew install postgresql@15
brew install pgvector
```

**Linux:**
```bash
sudo apt install postgresql postgresql-contrib
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Update settings.py

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'law_advisor',
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Recommendation:** Stick with Supabase for simplicity! 🚀

---

## Next Steps

After Supabase is set up:
1. ✅ Update `.env` with credentials
2. ✅ Test connection with test script
3. 📝 Process documents → generate embeddings
4. 🧪 Test RAG pipeline
5. 🔗 Connect to chat interface

---

**Last Updated:** 11.10.2024
**Author:** Mike @LaVanguard
