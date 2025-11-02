# Supabase RPC Function Fix Plan

**Date:** 2025-11-02
**Issue:** Function overloading conflict with `match_embeddings`
**Error Message:**
```
PGRST203: Could not choose the best candidate function between:
- public.match_embeddings(query_embedding => public.vector, match_count => integer)
- public.match_embeddings(query_embedding => public.vector, match_count => integer, filter => jsonb)
```

---

## 🔍 Root Cause Analysis

### Problem
There are **TWO versions** of `match_embeddings` function in Supabase:

1. **Version 1** (2 parameters - old):
   ```sql
   match_embeddings(query_embedding vector(1536), match_count int)
   ```

2. **Version 2** (3 parameters - with filter):
   ```sql
   match_embeddings(query_embedding vector(1536), match_count int, filter jsonb)
   ```

When Python code calls:
```python
supabase.rpc("match_embeddings", {
    "query_embedding": embedding,
    "match_count": 5
})
```

PostgreSQL **cannot decide** which function to use because both match the signature (the 3-parameter version has a default for `filter`).

### Additional Issue
Both functions reference **wrong table name**:
- Functions use: `embeddings` (old name)
- Actual table: `vector_embeddings` (renamed in Sprint 7)

---

## ✅ Proposed Solution

### Step 1: Drop ALL existing `match_embeddings` functions

This clears all versions to avoid conflicts:

```sql
-- Drop all versions of match_embeddings
DROP FUNCTION IF EXISTS match_embeddings(vector, int);
DROP FUNCTION IF EXISTS match_embeddings(vector, int, jsonb);
```

### Step 2: Create ONE definitive function

Create a single, properly-named function that:
- Uses correct table name: `vector_embeddings`
- Has clear return type with UUID (not bigint)
- Uses only 2 required parameters (no filter for now)

```sql
-- Create the definitive match_embeddings function
CREATE OR REPLACE FUNCTION match_embeddings(
  query_embedding vector(1536),
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    vector_embeddings.id,
    vector_embeddings.content,
    vector_embeddings.metadata,
    1 - (vector_embeddings.embedding <=> query_embedding) as similarity
  FROM vector_embeddings
  ORDER BY vector_embeddings.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

---

## 📋 Implementation Steps

### A. In Supabase Dashboard

1. Open **Supabase Dashboard** → https://supabase.com/dashboard
2. Navigate to your project
3. Go to **SQL Editor** (left sidebar)
4. Copy and paste the **complete SQL** (see below)
5. Click **Run** (or press F5)
6. Verify success message

### B. Complete SQL Script to Run

```sql
-- ============================================================
-- Somsiad - Fix match_embeddings RPC Function
-- Date: 2025-11-02
-- Purpose: Remove function overloading conflict + fix table name
-- ============================================================

-- Step 1: Drop ALL existing versions of match_embeddings
DROP FUNCTION IF EXISTS match_embeddings(vector, int);
DROP FUNCTION IF EXISTS match_embeddings(vector, int, jsonb);
DROP FUNCTION IF EXISTS match_embeddings(vector(1536), int);
DROP FUNCTION IF EXISTS match_embeddings(vector(1536), int, jsonb);

-- Step 2: Create the definitive function (uses vector_embeddings table)
CREATE OR REPLACE FUNCTION match_embeddings(
  query_embedding vector(1536),
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    vector_embeddings.id,
    vector_embeddings.content,
    vector_embeddings.metadata,
    1 - (vector_embeddings.embedding <=> query_embedding) as similarity
  FROM vector_embeddings
  ORDER BY vector_embeddings.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Step 3: Verify function was created
SELECT
  proname as function_name,
  pg_get_function_arguments(oid) as arguments,
  pg_get_functiondef(oid) as definition
FROM pg_proc
WHERE proname = 'match_embeddings';
```

### C. Test the Function

After running the SQL, test it:

```sql
-- Test query (replace with real embedding vector)
SELECT * FROM match_embeddings(
  '[0.1, 0.2, 0.3, ...]'::vector(1536),
  5
);
```

Expected result: 5 rows with columns `id`, `content`, `metadata`, `similarity`

---

## 🔧 Why This Solution Works

### 1. **Removes Ambiguity**
- Drops ALL versions → no overloading conflict
- Creates ONE canonical function

### 2. **Correct Table Name**
- Uses `vector_embeddings` (current name since Sprint 7)
- Not `embeddings` (old name)

### 3. **Correct Return Type**
- Returns `uuid` for `id` (matches Supabase table schema)
- Not `bigint` (was wrong in old docs)

### 4. **Simple API**
- Only 2 parameters (embedding, count)
- No complex filtering (can add later if needed)

---

## 🚨 Before You Run This

### Pre-flight Checklist

- [ ] You have access to Supabase Dashboard
- [ ] You're logged into the correct project
- [ ] `vector_embeddings` table exists (check in Table Editor)
- [ ] You have at least 1 embedding in the table
- [ ] You have SQL Editor permissions

### Verify Table Exists

```sql
-- Check if vector_embeddings table exists
SELECT table_name
FROM information_schema.tables
WHERE table_name = 'vector_embeddings';

-- Check row count
SELECT COUNT(*) FROM vector_embeddings;

-- Check table structure
\d vector_embeddings
```

Expected:
- Table exists ✅
- Count > 0 (should be 434+ from Sprint 7)
- Columns: `id (uuid)`, `content (text)`, `embedding (vector(1536))`, `metadata (jsonb)`, `created_at`

---

## 🧪 Post-Fix Verification

### 1. Check Function Exists

```sql
-- List all match_embeddings functions
\df match_embeddings

-- Expected: Only ONE function with signature:
-- match_embeddings(vector(1536), integer)
```

### 2. Test from Python

```python
# In Django shell or Python script
from knowledge.services.rag_service import RAGService

rag = RAGService()

# Test search
results = rag.search_similar_chunks("ogrodzenie", top_k=3)

print(f"Found {len(results)} results")
for text, metadata, score in results:
    print(f"- Score: {score:.3f} | {text[:50]}...")
```

Expected: No errors, returns 3 results

### 3. Test from Frontend

1. Open application: http://127.0.0.1:8000
2. Log in
3. Ask a question: "Jak wysoka może być działka graniczna?"
4. Wait for response

Expected:
- ✅ No error "column embeddings.content does not exist"
- ✅ AI responds with answer
- ✅ Sources shown below answer

---

## 📊 Impact Assessment

### What This Fixes

| Issue | Before | After |
|-------|--------|-------|
| Function overloading | ❌ Error PGRST203 | ✅ Clear function signature |
| Table name | ❌ Uses `embeddings` | ✅ Uses `vector_embeddings` |
| Return type | ❌ bigint (wrong) | ✅ uuid (correct) |
| Vector search | ❌ Fails | ✅ Works |
| Hybrid search (Sprint 8) | ❌ Fails | ✅ Works |
| RAG queries | ❌ Fails | ✅ Works |

### What This Doesn't Break

- ✅ Django ORM tables unchanged
- ✅ Existing data preserved (434+ embeddings)
- ✅ Application code unchanged (Python already uses correct API)
- ✅ No migrations needed

---

## 🔄 Rollback Plan (If Needed)

If something goes wrong, you can restore the old function:

```sql
-- Rollback: Restore old function (uses embeddings table)
DROP FUNCTION IF EXISTS match_embeddings(vector(1536), int);

CREATE OR REPLACE FUNCTION match_embeddings(
  query_embedding vector(1536),
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    embeddings.id,
    embeddings.content,
    embeddings.metadata,
    1 - (embeddings.embedding <=> query_embedding) as similarity
  FROM embeddings
  ORDER BY embeddings.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

**⚠️ WARNING:** This rollback uses the OLD table name `embeddings`, which doesn't exist! Only use this if you need to debug.

---

## 📝 After Completing This Fix

1. ✅ Update `docs/supabase_match_vector_embeddings_function.sql` with new SQL
2. ✅ Mark `SPRINT_8_PROGRESS.md` issue as resolved
3. ✅ Test full RAG pipeline
4. ✅ Test hybrid search (BM25 + vector)
5. ✅ Commit fix to git

---

## 🎯 Success Criteria

Fix is complete when:

- [ ] SQL runs without errors in Supabase
- [ ] Only ONE `match_embeddings` function exists
- [ ] Function uses `vector_embeddings` table
- [ ] Python `rag.search_similar_chunks()` works
- [ ] Frontend queries return AI responses
- [ ] No error "column embeddings.content does not exist"

---

**Author:** Mike @LaVanguard
**Sprint:** 8 - RAG 2.0 Query Optimization
**Priority:** 🔴 CRITICAL (blocks all RAG functionality)
