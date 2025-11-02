-- ============================================================
-- Somsiad - Complete Supabase Database Fix
-- Date: 2025-11-02
-- Purpose: Fix match_embeddings RPC function conflicts
-- ============================================================
--
-- ISSUE: Function overloading conflict + wrong table name
-- ERROR: "Could not choose the best candidate function..."
--        "column embeddings.content does not exist"
--
-- SOLUTION: Drop all versions, create ONE definitive function
--
-- INSTRUCTIONS:
-- 1. Open Supabase Dashboard → SQL Editor
-- 2. Copy this ENTIRE file
-- 3. Paste and Run (F5)
-- 4. Verify success messages
-- ============================================================

-- STEP 1: Drop ALL existing versions of match_embeddings
-- This removes function overloading ambiguity

DROP FUNCTION IF EXISTS match_embeddings(vector, int);
DROP FUNCTION IF EXISTS match_embeddings(vector, int, jsonb);
DROP FUNCTION IF EXISTS match_embeddings(vector(1536), int);
DROP FUNCTION IF EXISTS match_embeddings(vector(1536), int, jsonb);

-- Verify: Should show "DROP FUNCTION" messages


-- STEP 2: Create the definitive match_embeddings function
-- Uses correct table name: vector_embeddings (renamed in Sprint 7)
-- Returns uuid (not bigint) to match actual table schema

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

-- Verify: Should show "CREATE FUNCTION"


-- STEP 3: Verify function was created correctly

SELECT
  proname as function_name,
  pg_get_function_arguments(oid) as arguments
FROM pg_proc
WHERE proname = 'match_embeddings';

-- Expected output:
-- function_name      | arguments
-- -------------------+--------------------------------------
-- match_embeddings   | query_embedding vector, match_count integer


-- STEP 4: Test the function (optional)
-- Uncomment and replace with a real embedding vector to test

/*
SELECT
  id,
  LEFT(content, 50) as preview,
  similarity
FROM match_embeddings(
  '[0.1, 0.2, 0.3, ...]'::vector(1536),  -- Replace with real embedding
  5
);
*/


-- ============================================================
-- SUCCESS INDICATORS:
-- ✅ "DROP FUNCTION" messages (4x)
-- ✅ "CREATE FUNCTION" message
-- ✅ Verification query shows ONLY ONE function
-- ✅ No errors
-- ============================================================
--
-- NEXT STEPS:
-- 1. Test from Python: rag.search_similar_chunks("test", 5)
-- 2. Test from Frontend: Ask a question in chat
-- 3. Verify no errors in application
-- ============================================================
