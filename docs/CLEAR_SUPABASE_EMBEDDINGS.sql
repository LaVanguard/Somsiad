-- SQL to clear all embeddings from Supabase
-- Run this in Supabase SQL Editor

-- Delete all embeddings
DELETE FROM embeddings;

-- Verify deletion
SELECT COUNT(*) as remaining_embeddings FROM embeddings;

-- This should return 0
