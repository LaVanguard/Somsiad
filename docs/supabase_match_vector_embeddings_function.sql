-- SQL function for vector similarity search in Supabase (Sprint 7 update)
-- This function should be executed in Supabase SQL Editor
--
-- IMPORTANT: This is the updated version that uses vector_embeddings table
-- (The table was renamed from embeddings → vector_embeddings in Sprint 7)

-- Drop old function if exists
DROP FUNCTION IF EXISTS match_embeddings(vector, int);

-- Create the match_embeddings function for vector similarity search
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
