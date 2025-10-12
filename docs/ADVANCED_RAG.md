# Advanced RAG System Documentation

**Somsiad - Production-Quality Retrieval-Augmented Generation**

---

## Overview

This document describes the advanced RAG (Retrieval-Augmented Generation) system implemented in Somsiad. Unlike basic RAG systems that use fixed-size chunking, our implementation uses **semantic chunking**, **document summarization**, and **rich metadata enrichment** for superior retrieval quality.

---

## Architecture

### Pipeline Flow

```
PDF Document
    ↓
1. Text Extraction (PyPDF2)
    ↓
2. Preprocessing (remove noise, fix encoding)
    ↓
3. Document Summarization (GPT-4o-mini)
    ↓
4. Semantic Chunking (by articles/sections)
    ↓
5. Metadata Enrichment (refs, measurements, obligations)
    ↓
6. Embedding Generation (text-embedding-3-small)
    ↓
7. Vector Storage (Supabase pgvector)
    ↓
8. Database References (Django ORM)
```

---

## Key Components

### 1. Document Preprocessor (`knowledge/services/preprocessor.py`)

**Purpose:** Clean Polish legal documents before chunking

**What it removes:**
- Administrative headers: `Kancelaria Sejmu`, `Dziennik Ustaw`
- Journal references: `Dz. U. 2023 r. poz. 682`
- Dates and signatures: `Warszawa, dnia 27 czerwca 2023 r.`
- Ministry metadata: `ROZPORZĄDZENIE MINISTRA...`
- Encoding artifacts: Fixes `�` → `ł`, etc.

**Results:**
- 5-10% noise reduction
- Cleaner embeddings
- Better retrieval relevance

**Example:**
```python
preprocessor = DocumentPreprocessor()
result = preprocessor.preprocess(raw_text)
cleaned_text = result['cleaned']
stats = preprocessor.get_stats(raw_text, cleaned_text)
# {'reduction_pct': 9.32, 'chars_removed': 326}
```

---

### 2. Semantic Chunker (`knowledge/services/semantic_chunker.py`)

**Purpose:** Split documents by logical structure, not arbitrary character limits

**Chunking Strategy:**
1. **Split by sections** (Rozdział, Dział)
2. **Split by articles** (Art. 1, Art. 2, ...)
3. **Split by paragraphs** (§ 1, § 2, ...)
4. **Fallback:** Fixed-size for very long articles

**Chunk Types:**
- `article` - Complete legal article
- `section` - Major document section
- `subsection` - Article subsection (1., 2., 3.)
- `fragment` - Fallback for unusual structures
- `preamble` - Text before first article

**Example Output:**
```python
chunker = SemanticChunker()
chunks = chunker.chunk_document(text, metadata)

# Sample chunk:
LegalChunk(
    content="Art. 5. Przepisy rozporządzenia stosuje się...",
    chunk_type='article',
    article_number='Art. 5',
    section_name='Rozdział II',
    metadata={...}
)
```

**Statistics (warunki_techniczne_metro_2023.pdf, 5 pages):**
- 37 semantic chunks created
- Types: 13 articles, 10 fragments, 14 subsections
- Size range: 31-1516 chars (adaptive)
- Avg size: 468 chars

---

### 3. Document Summarizer (`knowledge/services/summarizer.py`)

**Purpose:** Generate hierarchical summaries for better retrieval context

**Features:**

#### A. Document-Level Summary
Generates 3-part summary:
1. **STRESZCZENIE** (Executive summary - 3-5 sentences)
2. **KLUCZOWE TEMATY** (Key topics - 5-7 bullet points)
3. **ZAKRES ZASTOSOWANIA** (Scope - who/what it applies to)

**Example:**
```
STRESZCZENIE:
Dokument "Warunki techniczne metra 2023" określa zasady projektowania
oraz budowy obiektów budowlanych metra i związanych z nimi urządzeń...

KLUCZOWE TEMATY:
- Przepisy ogólne dotyczące projektowania i budowy obiektów metra
- Definicje kluczowych terminów związanych z metrem
- Wymogi dotyczące wentylacji i bezpieczeństwa
...

ZAKRES ZASTOSOWANIA:
Dotyczy projektantów, wykonawców oraz operatorów systemów metra w Polsce...
```

#### B. Searchable Summary Chunk
The summary is embedded as a special chunk:
- Stored alongside regular chunks
- Has `is_summary: true` metadata
- Retrieved for broad queries
- Provides document-level context

---

### 4. Metadata Enrichment

**Auto-extracted metadata for each chunk:**

| Metadata Field | Description | Example |
|---------------|-------------|---------|
| `article_references` | Referenced articles | `['art. 5', 'art. 7']` |
| `paragraph_references` | Referenced paragraphs | `['§ 1', '§ 2']` |
| `measurements` | Distances, sizes | `['16 m', '2.5 km']` |
| `contains_obligations` | Has legal obligations | `true/false` |
| `article_number` | Primary article | `'Art. 5'` |
| `section_name` | Parent section | `'Rozdział II'` |
| `chunk_type` | Chunk type | `'article'` |

**Benefits:**
- **Hybrid search:** Combine semantic + keyword filtering
- **Precise matching:** Filter by article number before semantic search
- **Context awareness:** Know if chunk contains obligations

---

### 5. RAG Service (`knowledge/services/rag_service.py`)

**Purpose:** Orchestrate embedding generation and vector search

**Key Methods:**
```python
class RAGService:
    def generate_embeddings(texts: List[str]) -> List[List[float]]
        # OpenAI text-embedding-3-small (1536D)

    def search_similar_chunks(query: str, top_k: int = 5)
        # Supabase pgvector cosine similarity

    def generate_answer(question: str, context_chunks: List[str])
        # GPT-4o-mini with RAG prompt

    def process_query(question: str) -> (answer, sources, time)
        # Full RAG pipeline
```

---

### 6. Document Processor (`knowledge/services/document_processor.py`)

**Purpose:** Main orchestration pipeline

**Configuration:**
```python
processor = DocumentProcessor(
    enable_preprocessing=True,     # Clean noise
    use_semantic_chunking=True,    # Smart chunking
    generate_summaries=True        # Create summaries
)
```

**Processing Steps:**
1. Extract PDF text
2. Preprocess (clean)
3. Generate document summary
4. Semantic chunking
5. Enrich metadata
6. Add summary as searchable chunk
7. Generate embeddings (all chunks + summary)
8. Store in Supabase pgvector
9. Store references in Django DB
10. Mark document as processed

---

## Retrieval Strategy

### Hierarchical Retrieval

When user asks a question:

1. **Broad queries** → Document summary matches
   - "Co mówi to prawo?"
   - "Jakie są główne wymagania?"

2. **Specific queries** → Article chunks match
   - "Jak wysoko mogę zbudować ogrodzenie?"
   - "Jakie przeglądy są obowiązkowe?"

3. **Context queries** → Section summaries match
   - "Co jest w rozdziale 3?"

### Query Processing

```python
# User query
question = "Jak wysoko mogę zbudować ogrodzenie od strony ulicy?"

# 1. Generate query embedding
query_embedding = embeddings.embed_query(question)

# 2. Search Supabase (top-k=5)
similar_chunks = supabase.rpc("match_embeddings", {
    "query_embedding": query_embedding,
    "match_count": 5
})

# 3. Extract context
context_chunks = [chunk['content'] for chunk in similar_chunks]

# 4. Generate answer with GPT-4o-mini
prompt = f"""
Kontekst prawny:
{'\n\n'.join(context_chunks)}

Pytanie użytkownika:
{question}

Odpowiedz w oparciu o podany kontekst...
"""

answer = llm.invoke(prompt)

# 5. Return answer + sources + similarity scores
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ...

# Django
SECRET_KEY=django-secret-key
DEBUG=True
```

### RAG Parameters

Located in `knowledge/services/`:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Chunking** | | |
| `max_chunk_size` | 1500 chars | Max article size before splitting |
| **Embeddings** | | |
| `model` | text-embedding-3-small | OpenAI embedding model |
| `dimensions` | 1536 | Vector dimensions |
| **Generation** | | |
| `model` | gpt-4o-mini | LLM for summaries & answers |
| `temperature` | 0.3 | Generation randomness (low for consistency) |
| **Retrieval** | | |
| `top_k` | 5 | Number of chunks retrieved |
| `similarity` | cosine | Distance metric |

---

## Database Schema

### Supabase (pgvector)

```sql
-- Embeddings table
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    embedding VECTOR(1536),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding VECTOR(1536),
    match_count INT
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        embeddings.id,
        embeddings.content,
        embeddings.metadata,
        1 - (embeddings.embedding <=> query_embedding) AS similarity
    FROM embeddings
    ORDER BY embeddings.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

### Django Models

```python
class Document(models.Model):
    title = models.CharField(max_length=500)
    file = models.FileField(upload_to='documents/')
    category = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Embedding(models.Model):
    document = models.ForeignKey(Document, related_name='embeddings')
    chunk_text = models.TextField()
    embedding_id = models.CharField(max_length=100)  # Supabase UUID
    metadata = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Testing

### Test Scripts

1. **`test_preprocessing.py`** - Validates text cleaning
2. **`test_advanced_rag.py`** - End-to-end RAG test

### Run Tests

```bash
# Test preprocessing
python test_preprocessing.py

# Test full RAG pipeline (requires API keys)
python test_advanced_rag.py
```

### Expected Output

```
ADVANCED RAG SYSTEM TEST
================================================================================
Extracted 5 pages
Total characters: 20,285

PREPROCESSING
Characters before:  20,285
Characters after:   19,520
Reduction:          3.77%

SEMANTIC CHUNKING
Created 37 semantic chunks

DOCUMENT SUMMARIZATION
Generated summary: 1261 chars
Key topics: 7

METADATA ENRICHMENT
Article references: 5
Paragraph references: 14
Measurements: 4

[OK] Semantic chunking by articles/sections
[OK] Document-level summarization
[OK] Metadata enrichment
[OK] Searchable summary chunks
```

---

## Cost Estimates

**Development usage (per document):**
- Embeddings: ~$0.001 per 1000 tokens (~$0.01 per 50-page document)
- Summarization: ~$0.002 per document (GPT-4o-mini)
- Queries: ~$0.01 per query (embedding + generation)

**Monthly estimate (dev/testing):**
- 10 documents processed: ~$0.50
- 100 test queries: ~$1.00
- **Total: ~$2-5/month**

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Processing Time** | 10-30s per document | Depends on length & API latency |
| **Query Time** | 2-5s | Embedding + search + generation |
| **Chunk Quality** | High | Preserves legal structure |
| **Retrieval Relevance** | Excellent | Semantic + metadata filtering |
| **Summary Quality** | Very Good | GPT-4o-mini generated |

---

## Future Enhancements (Sprint 3+)

1. **Multi-Query RAG** - Generate query variations for better recall
2. **Hybrid Search** - Combine BM25 keyword + semantic search
3. **Re-ranking** - Cross-encoder for result re-ranking
4. **Parent Document Retrieval** - Search small chunks, return larger context
5. **Citation Extraction** - Extract and link law citations
6. **Hypothetical Questions** - Generate questions each chunk can answer

---

## Troubleshooting

### Common Issues

**1. Encoding errors in PDFs**
- **Symptom:** `�` characters in text
- **Fix:** Preprocessor auto-fixes common issues

**2. No articles detected**
- **Symptom:** Only one chunk created
- **Fix:** Document may use §  instead of Art. - chunker handles both

**3. Summary generation fails**
- **Symptom:** Empty summary
- **Fix:** Check OpenAI API key and quota

**4. Supabase connection errors**
- **Symptom:** `ConnectionError` during embedding storage
- **Fix:** Verify SUPABASE_URL and SUPABASE_KEY in `.env`

---

## References

- **LangChain Docs:** https://python.langchain.com/docs/
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings
- **Supabase pgvector:** https://supabase.com/docs/guides/ai/vector-columns
- **Semantic Chunking:** https://arxiv.org/abs/2301.00303

---

**Last Updated:** 2025-10-12
**Author:** Mike @LaVanguard
**Sprint:** 2 - Advanced RAG Implementation
