# Sprint 8: RAG 2.0 Query Optimization - Implementation Plan

**Data:** 27 października 2025
**Branch:** `feature/sprint8-rag2-optimization`
**Status:** 📋 Planning Phase
**Estimated Duration:** 6-8 hours development + 2 hours testing

---

## 🎯 Sprint Objective

Transform Somsiad's RAG system from **Advanced RAG 1.5** to **Production-Grade RAG 2.0** by implementing industry-standard 2025 optimization techniques that dramatically improve retrieval accuracy, precision, and answer quality.

**Goal:** Achieve 90%+ retrieval accuracy and eliminate hallucinations through hybrid search, query rewriting, reranking, and self-reflection.

---

## 📊 Current State Analysis

### What We Have (RAG 1.5)
✅ Semantic chunking (legal structure-aware)
✅ Document summarization (hierarchical)
✅ Metadata enrichment (article refs, measurements)
✅ Vector search (Supabase pgvector, cosine similarity)
✅ Preprocessing (9% noise reduction)
✅ Streaming responses (SSE)
✅ Batch processing (no timeouts)

### What We're Missing (RAG 2.0)
❌ **Hybrid Search** - Only vector search, no keyword matching
❌ **Query Rewriting** - Single query, no variations for better recall
❌ **Reranking** - No cross-encoder refinement of results
❌ **Self-Reflection** - No relevance validation before answering
❌ **Query Classification** - All queries treated the same
❌ **Corrective Feedback** - No fallback for low-quality retrieval

### Performance Baseline
- Retrieval Accuracy: ~75%
- Precision@5: ~70%
- Answer Quality: Good
- Hallucination Rate: ~10%

### Target Metrics (After RAG 2.0)
- Retrieval Accuracy: **92%** (+17%)
- Precision@5: **85%** (+15%)
- Answer Quality: **Excellent** (+20%)
- Hallucination Rate: **3%** (-70%)

---

## 🏗️ Phase 1 Architecture

### High-Level Flow

```
User Query
    ↓
1. QUERY REWRITING (Multi-Query RAG)
    ↓ (generates 3 variations)
    ├─ Query 1: Original
    ├─ Query 2: Rewritten (formal)
    └─ Query 3: Rewritten (expanded)
    ↓
2. HYBRID SEARCH (Parallel)
    ├─ BM25 Keyword Search (top-20)
    ├─ Vector Semantic Search (top-20)
    └─ Reciprocal Rank Fusion (RRF)
    ↓ (40-60 chunks retrieved)
    ↓
3. DEDUPLICATION & MERGING
    ↓ (top-20 unique chunks)
    ↓
4. RERANKING (Cross-Encoder)
    ↓ (top-5 refined)
    ↓
5. SELF-RAG (Relevance Check)
    ↓ (validates chunks are relevant)
    ├─ Relevant → Generate Answer
    └─ Not Relevant → Return "Insufficient Info"
    ↓
6. ANSWER GENERATION (GPT-4o-mini)
    ↓
7. STREAMING RESPONSE
```

---

## 📦 Feature 1: Hybrid Search (BM25 + Vector)

### Problem Statement
**Current:** Vector search alone misses exact keyword matches (e.g., "Art. 5", "§ 12", specific legal terms).
**Impact:** ~15% of queries fail because vector embeddings don't capture exact lexical matches.

### Solution: Hybrid Search
Combine **BM25 (keyword)** + **Vector (semantic)** search, then fuse results using **Reciprocal Rank Fusion (RRF)**.

---

### Step-by-Step Implementation

#### Step 1.1: Install BM25 Library
**File:** `requirements.txt`
```txt
rank-bm25==0.2.2
```

**Commands:**
```bash
pip install rank-bm25==0.2.2
```

---

#### Step 1.2: Create BM25 Index Builder
**File:** `knowledge/services/bm25_service.py` (NEW)

**Purpose:** Build and persist BM25 index for keyword search.

**Key Components:**
1. **BM25Index class**
   - Load all document chunks from Supabase
   - Tokenize Polish text (split on whitespace + remove stopwords)
   - Build BM25 index using `rank_bm25.BM25Okapi`
   - Serialize index to disk (pickle) for fast loading

2. **Methods:**
   - `build_index()` - Build from Supabase chunks
   - `save_index(path)` - Persist to disk
   - `load_index(path)` - Load from disk
   - `search(query, top_k)` - Search and return chunk IDs + scores

**Pseudocode:**
```python
class BM25Service:
    def __init__(self):
        self.supabase = create_client(...)
        self.index = None
        self.chunk_ids = []
        self.tokenizer = self._create_tokenizer()

    def _create_tokenizer(self):
        # Polish-aware tokenizer
        # Remove stopwords: "i", "w", "z", "na", "do", etc.
        pass

    def build_index(self):
        # 1. Fetch all chunks from Supabase vector_embeddings
        chunks = self.supabase.table("vector_embeddings").select("id, content").execute()

        # 2. Tokenize each chunk
        tokenized_corpus = [self.tokenizer(chunk['content']) for chunk in chunks]

        # 3. Build BM25 index
        self.index = BM25Okapi(tokenized_corpus)
        self.chunk_ids = [chunk['id'] for chunk in chunks]

    def search(self, query: str, top_k: int = 20):
        # 1. Tokenize query
        tokenized_query = self.tokenizer(query)

        # 2. Get BM25 scores
        scores = self.index.get_scores(tokenized_query)

        # 3. Get top-k chunk IDs + scores
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = [(self.chunk_ids[i], scores[i]) for i in top_indices]

        return results
```

**Data Storage:**
- BM25 index: `media/bm25_index.pkl` (pickle file)
- Rebuild index when new documents are processed

---

#### Step 1.3: Implement Reciprocal Rank Fusion (RRF)
**File:** `knowledge/services/hybrid_search_service.py` (NEW)

**Purpose:** Combine BM25 and vector search results.

**RRF Formula:**
```
RRF_score(chunk) = Σ (1 / (k + rank_i))
where k = 60 (constant), rank_i = position in result list i
```

**Key Components:**
1. **HybridSearchService class**
   - Combines BM25Service + RAGService (vector search)
   - Implements RRF fusion
   - Deduplicates results

2. **Methods:**
   - `hybrid_search(query, top_k)` - Main entry point
   - `_reciprocal_rank_fusion(bm25_results, vector_results)` - Fuse scores
   - `_fetch_chunks_by_ids(chunk_ids)` - Get full chunks from Supabase

**Pseudocode:**
```python
class HybridSearchService:
    def __init__(self):
        self.bm25_service = BM25Service()
        self.rag_service = RAGService()
        self.k = 60  # RRF constant

    def hybrid_search(self, query: str, top_k: int = 20):
        # 1. BM25 search (top-20)
        bm25_results = self.bm25_service.search(query, top_k=20)
        # [(chunk_id, bm25_score), ...]

        # 2. Vector search (top-20)
        vector_results = self.rag_service.search_similar_chunks(query, top_k=20)
        # [(chunk_id, content, metadata, similarity), ...]

        # 3. RRF fusion
        fused_results = self._reciprocal_rank_fusion(bm25_results, vector_results)

        # 4. Fetch full chunks for top-k
        top_chunk_ids = [chunk_id for chunk_id, score in fused_results[:top_k]]
        chunks = self._fetch_chunks_by_ids(top_chunk_ids)

        return chunks

    def _reciprocal_rank_fusion(self, bm25_results, vector_results):
        # Map chunk_id → RRF score
        rrf_scores = {}

        # Add BM25 rankings
        for rank, (chunk_id, score) in enumerate(bm25_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (self.k + rank + 1)

        # Add vector rankings
        for rank, (chunk_id, content, metadata, similarity) in enumerate(vector_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (self.k + rank + 1)

        # Sort by RRF score (descending)
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_results
```

**Notes:**
- BM25 and vector search run in parallel (use `concurrent.futures` if needed)
- RRF is more robust than weighted averaging
- k=60 is standard in literature (tested in MS MARCO)

---

#### Step 1.4: Integrate Hybrid Search into RAG Pipeline
**File:** `knowledge/services/rag_service.py`

**Changes:**
1. Add `use_hybrid_search` parameter to `process_query()`
2. Replace `search_similar_chunks()` with `HybridSearchService.hybrid_search()` when enabled
3. Keep fallback to pure vector search for backward compatibility

**Pseudocode:**
```python
class RAGService:
    def __init__(self):
        # ... existing code ...
        self.hybrid_search_service = HybridSearchService()

    def process_query(self, question: str, top_k: int = 5, use_hybrid_search: bool = True):
        start_time = time.time()

        # 1. Search for relevant chunks
        if use_hybrid_search:
            search_results = self.hybrid_search_service.hybrid_search(question, top_k=top_k)
        else:
            search_results = self.search_similar_chunks(question, top_k=top_k)

        # ... rest of pipeline unchanged ...
```

---

#### Step 1.5: Update BM25 Index on Document Processing
**File:** `knowledge/services/document_processor.py`

**Changes:**
1. After storing embeddings, trigger BM25 index rebuild
2. Add flag to skip rebuild during batch processing (rebuild once at end)

**Pseudocode:**
```python
class DocumentProcessor:
    def process_document(self, document):
        # ... existing code ...

        # After storing embeddings
        embedding_ids = self.rag_service.store_embeddings(...)

        # Rebuild BM25 index
        bm25_service = BM25Service()
        bm25_service.build_index()
        bm25_service.save_index('media/bm25_index.pkl')

        # ... rest of code ...
```

---

### Testing Plan (Feature 1)

**Test Cases:**
1. **Exact Match Test**
   - Query: "Art. 5"
   - Expected: BM25 should rank exact match #1

2. **Semantic Test**
   - Query: "Jak wysoko mogę zbudować płot?"
   - Expected: Vector search should find relevant chunks

3. **Hybrid Test**
   - Query: "Maksymalna wysokość ogrodzenia Art. 5"
   - Expected: RRF should combine both BM25 (Art. 5) + vector (wysokość ogrodzenia)

**Performance Benchmark:**
- Build index time: < 5 seconds (434 chunks)
- Search time: < 100ms (hybrid search)
- Memory usage: < 50MB (BM25 index)

---

## 📦 Feature 2: Query Rewriting (Multi-Query RAG)

### Problem Statement
**Current:** Single query may be poorly phrased, missing keywords, or too vague.
**Impact:** ~10-15% of queries have low recall due to phrasing issues.

### Solution: Multi-Query RAG
Generate 2-3 query variations using GPT-4o-mini, search with all variations, deduplicate and merge results.

---

### Step-by-Step Implementation

#### Step 2.1: Create Query Rewriter Service
**File:** `knowledge/services/query_rewriter.py` (NEW)

**Purpose:** Generate query variations using LLM.

**Key Components:**
1. **QueryRewriter class**
   - Uses GPT-4o-mini to generate variations
   - Returns 2-3 rewritten queries
   - Caches rewrites to reduce API calls

2. **Methods:**
   - `rewrite_query(query, num_variations=2)` - Generate variations
   - `_create_rewrite_prompt(query)` - LLM prompt for rewriting

**Pseudocode:**
```python
class QueryRewriter:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def rewrite_query(self, query: str, num_variations: int = 2):
        prompt = self._create_rewrite_prompt(query, num_variations)
        response = self.llm.invoke(prompt)

        # Parse LLM response (expects numbered list)
        variations = self._parse_variations(response.content)

        return [query] + variations  # Include original + rewrites

    def _create_rewrite_prompt(self, query: str, num_variations: int):
        return f"""Jesteś ekspertem od wyszukiwania dokumentów prawnych.

Użytkownik zadał pytanie: "{query}"

Wygeneruj {num_variations} alternatywne wersje tego pytania, które:
1. Używają formalnego języka prawnego
2. Zawierają synonimy i powiązane terminy
3. Są bardziej szczegółowe lub bardziej ogólne

Format odpowiedzi (tylko lista, bez dodatkowych komentarzy):
1. [pierwsza wersja]
2. [druga wersja]
"""

    def _parse_variations(self, response: str):
        # Extract numbered list
        lines = response.strip().split('\n')
        variations = []

        for line in lines:
            # Match "1. ...", "2. ...", etc.
            match = re.match(r'^\d+\.\s*(.+)$', line.strip())
            if match:
                variations.append(match.group(1))

        return variations
```

**Example Output:**
```
Original: "Jak wysoko ogrodzenie?"

Variations:
1. "Maksymalna wysokość ogrodzenia zgodnie z przepisami budowlanymi"
2. "Jakie są wymagania prawne dotyczące wysokości płotu od strony ulicy?"
```

---

#### Step 2.2: Integrate Multi-Query Search
**File:** `knowledge/services/hybrid_search_service.py`

**Changes:**
1. Add `use_query_rewriting` parameter to `hybrid_search()`
2. If enabled, rewrite query before searching
3. Search with all variations in parallel
4. Deduplicate and merge results with RRF

**Pseudocode:**
```python
class HybridSearchService:
    def __init__(self):
        # ... existing code ...
        self.query_rewriter = QueryRewriter()

    def hybrid_search(self, query: str, top_k: int = 20, use_query_rewriting: bool = True):
        # 1. Generate query variations
        if use_query_rewriting:
            queries = self.query_rewriter.rewrite_query(query, num_variations=2)
        else:
            queries = [query]

        # 2. Search with all variations (parallel)
        all_results = []
        for q in queries:
            bm25_results = self.bm25_service.search(q, top_k=20)
            vector_results = self.rag_service.search_similar_chunks(q, top_k=20)
            all_results.append((bm25_results, vector_results))

        # 3. Multi-query RRF fusion
        fused_results = self._multi_query_rrf_fusion(all_results)

        # 4. Fetch top-k chunks
        top_chunk_ids = [chunk_id for chunk_id, score in fused_results[:top_k]]
        chunks = self._fetch_chunks_by_ids(top_chunk_ids)

        return chunks

    def _multi_query_rrf_fusion(self, all_results):
        # Fuse results from multiple queries
        rrf_scores = {}

        for bm25_results, vector_results in all_results:
            # Standard RRF for each query
            query_scores = self._reciprocal_rank_fusion(bm25_results, vector_results)

            # Aggregate scores across queries
            for chunk_id, score in query_scores:
                rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + score

        # Sort by aggregated RRF score
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_results
```

**Notes:**
- Query rewriting adds ~300ms latency (LLM call)
- Cache rewrites by query hash to reduce API costs
- Can run searches in parallel using `ThreadPoolExecutor`

---

### Testing Plan (Feature 2)

**Test Cases:**
1. **Vague Query Test**
   - Original: "ogrodzenie"
   - Expected: Rewrites should add context ("wysokość", "przepisy", "budowa")

2. **Poorly Phrased Test**
   - Original: "Jak wysoko mogę?"
   - Expected: Rewrites should complete the question

3. **Recall Test**
   - Query: "płot" (fence)
   - Expected: Rewrites should include "ogrodzenie" (synonym)

**Performance Benchmark:**
- Rewrite time: < 500ms (GPT-4o-mini)
- Recall improvement: +10-15%

---

## 📦 Feature 3: Reranking (Cross-Encoder)

### Problem Statement
**Current:** Hybrid search retrieves top-20 chunks, but ranking may not be optimal.
**Impact:** Relevant chunks may be ranked #15-20, missing the top-5 context window.

### Solution: Cross-Encoder Reranking
Use a cross-encoder model to re-score top-20 chunks and refine to top-5.

---

### Step-by-Step Implementation

#### Step 3.1: Install Sentence Transformers
**File:** `requirements.txt`
```txt
sentence-transformers==2.7.0
```

**Commands:**
```bash
pip install sentence-transformers==2.7.0
```

---

#### Step 3.2: Create Reranker Service
**File:** `knowledge/services/reranker_service.py` (NEW)

**Purpose:** Rerank search results using cross-encoder.

**Key Components:**
1. **RerankerService class**
   - Loads cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
   - Scores query-chunk pairs
   - Returns top-k reranked results

2. **Methods:**
   - `rerank(query, chunks, top_k)` - Rerank and return top-k
   - `_score_pairs(query, chunks)` - Cross-encoder scoring

**Pseudocode:**
```python
from sentence_transformers import CrossEncoder

class RerankerService:
    def __init__(self):
        # Load cross-encoder model (multilingual, works for Polish)
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def rerank(self, query: str, chunks: List[Dict], top_k: int = 5):
        # 1. Create query-chunk pairs
        pairs = [(query, chunk['content']) for chunk in chunks]

        # 2. Score all pairs with cross-encoder
        scores = self.model.predict(pairs)

        # 3. Sort chunks by cross-encoder score
        scored_chunks = [
            {**chunk, 'rerank_score': score}
            for chunk, score in zip(chunks, scores)
        ]
        sorted_chunks = sorted(scored_chunks, key=lambda x: x['rerank_score'], reverse=True)

        # 4. Return top-k
        return sorted_chunks[:top_k]
```

**Model Details:**
- **Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Size:** ~90MB
- **Languages:** Multilingual (includes Polish)
- **Speed:** ~50ms for 20 pairs (CPU), ~10ms (GPU)

**Alternative Models (if needed):**
- `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (better multilingual)
- `cross-encoder/ms-marco-MiniLM-L-12-v2` (higher quality, slower)

---

#### Step 3.3: Integrate Reranking into Hybrid Search
**File:** `knowledge/services/hybrid_search_service.py`

**Changes:**
1. Add `use_reranking` parameter to `hybrid_search()`
2. Retrieve top-20 with hybrid search
3. Rerank to top-5 with cross-encoder

**Pseudocode:**
```python
class HybridSearchService:
    def __init__(self):
        # ... existing code ...
        self.reranker = RerankerService()

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        use_query_rewriting: bool = True,
        use_reranking: bool = True
    ):
        # 1-2. Query rewriting + hybrid search (retrieve top-20)
        retrieve_k = 20 if use_reranking else top_k

        # ... existing hybrid search code ...
        chunks = self._fetch_chunks_by_ids(top_chunk_ids[:retrieve_k])

        # 3. Rerank to top-k
        if use_reranking:
            chunks = self.reranker.rerank(query, chunks, top_k=top_k)

        return chunks[:top_k]
```

---

### Testing Plan (Feature 3)

**Test Cases:**
1. **Ranking Quality Test**
   - Query: "Maksymalna wysokość ogrodzenia"
   - Expected: Most relevant chunk ranked #1 after reranking

2. **Precision Test**
   - Measure Precision@5 before and after reranking
   - Expected: +10-15% improvement

**Performance Benchmark:**
- Rerank time: < 100ms (20 chunks, CPU)
- Model load time: < 2 seconds (first request)
- Memory usage: ~200MB (model in RAM)

---

## 📦 Feature 4: Self-RAG (Relevance Check)

### Problem Statement
**Current:** RAG always generates an answer, even with irrelevant chunks.
**Impact:** ~10% of answers are hallucinations due to forced generation from poor context.

### Solution: Self-RAG Reflection
Before generation, LLM evaluates if retrieved chunks are relevant to the question. If not, return "I don't have enough information."

---

### Step-by-Step Implementation

#### Step 4.1: Create Self-RAG Service
**File:** `knowledge/services/self_rag_service.py` (NEW)

**Purpose:** Validate retrieval quality before generation.

**Key Components:**
1. **SelfRAGService class**
   - Uses GPT-4o-mini to judge relevance
   - Returns binary decision (relevant/not relevant)
   - Provides confidence score

2. **Methods:**
   - `check_relevance(query, chunks)` - Main entry point
   - `_create_relevance_prompt(query, chunks)` - LLM prompt

**Pseudocode:**
```python
class SelfRAGService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        self.relevance_threshold = 0.7  # Confidence threshold

    def check_relevance(self, query: str, chunks: List[str]) -> Dict:
        prompt = self._create_relevance_prompt(query, chunks)
        response = self.llm.invoke(prompt)

        # Parse response (expects: RELEVANT or NOT_RELEVANT + reasoning)
        result = self._parse_relevance_response(response.content)

        return {
            'is_relevant': result['decision'] == 'RELEVANT',
            'confidence': result['confidence'],
            'reasoning': result['reasoning']
        }

    def _create_relevance_prompt(self, query: str, chunks: List[str]):
        chunks_text = '\n\n'.join([f"[Chunk {i+1}]\n{chunk}" for i, chunk in enumerate(chunks)])

        return f"""Jesteś ekspertem oceniającym jakość wyników wyszukiwania.

PYTANIE UŻYTKOWNIKA:
{query}

ZNALEZIONE FRAGMENTY DOKUMENTÓW:
{chunks_text}

ZADANIE:
Oceń czy znalezione fragmenty zawierają wystarczające informacje do udzielenia odpowiedzi na pytanie użytkownika.

ODPOWIEDŹ (dokładnie w tym formacie):
DECYZJA: [RELEVANT lub NOT_RELEVANT]
PEWNOŚĆ: [0.0-1.0]
UZASADNIENIE: [krótkie wyjaśnienie]
"""

    def _parse_relevance_response(self, response: str):
        # Extract decision, confidence, reasoning
        lines = response.strip().split('\n')

        decision = 'NOT_RELEVANT'
        confidence = 0.0
        reasoning = ''

        for line in lines:
            if line.startswith('DECYZJA:'):
                decision = 'RELEVANT' if 'RELEVANT' in line else 'NOT_RELEVANT'
            elif line.startswith('PEWNOŚĆ:'):
                confidence = float(re.search(r'[\d.]+', line).group())
            elif line.startswith('UZASADNIENIE:'):
                reasoning = line.replace('UZASADNIENIE:', '').strip()

        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning
        }
```

**Example Output:**
```
Query: "Jak wysoko mogę zbudować płot?"
Chunks: [chunk about fence height regulations]

Response:
DECYZJA: RELEVANT
PEWNOŚĆ: 0.95
UZASADNIENIE: Fragmenty zawierają konkretne przepisy dotyczące maksymalnej wysokości ogrodzenia.
```

---

#### Step 4.2: Integrate Self-RAG into RAG Pipeline
**File:** `knowledge/services/rag_service.py`

**Changes:**
1. Add `use_self_rag` parameter to `process_query()`
2. Check relevance before generation
3. Return fallback message if not relevant

**Pseudocode:**
```python
class RAGService:
    def __init__(self):
        # ... existing code ...
        self.self_rag = SelfRAGService()

    def process_query(
        self,
        question: str,
        top_k: int = 5,
        use_hybrid_search: bool = True,
        use_self_rag: bool = True
    ):
        start_time = time.time()

        # 1. Search for relevant chunks (hybrid search)
        search_results = self.hybrid_search_service.hybrid_search(question, top_k=top_k)
        context_chunks = [result['content'] for result in search_results]

        # 2. Self-RAG relevance check
        if use_self_rag:
            relevance = self.self_rag.check_relevance(question, context_chunks)

            if not relevance['is_relevant']:
                # Return fallback message
                answer = """Przepraszam, ale nie znalazłem wystarczających informacji w dostępnych dokumentach prawnych, aby odpowiedzieć na Twoje pytanie.

Możliwe przyczyny:
- Pytanie dotyczy obszaru, którego nie obejmują dostępne przepisy
- Potrzebujesz bardziej szczegółowej interpretacji prawnej

Sugestia: Rozważ konsultację z prawnikiem lub doprecyzuj pytanie."""

                sources = []  # No sources if not relevant
                processing_time = time.time() - start_time

                return answer, sources, processing_time

        # 3. Generate answer (normal flow)
        answer = self.generate_answer(question, context_chunks)

        # ... rest of code ...
```

---

### Testing Plan (Feature 4)

**Test Cases:**
1. **Relevant Chunks Test**
   - Query: "Maksymalna wysokość ogrodzenia"
   - Chunks: [fence regulations]
   - Expected: RELEVANT, confidence > 0.8

2. **Irrelevant Chunks Test**
   - Query: "How to build a rocket?"
   - Chunks: [Polish fence regulations]
   - Expected: NOT_RELEVANT, confidence > 0.8

3. **Edge Case Test**
   - Query: "Przepisy dotyczące kotłów"
   - Chunks: [unrelated building regulations]
   - Expected: NOT_RELEVANT or low confidence

**Performance Benchmark:**
- Relevance check time: < 500ms (GPT-4o-mini)
- False positive rate: < 5%
- False negative rate: < 3%

---

## 🔧 Implementation Order

### Day 1 (3-4 hours)
1. ✅ Create planning document (this file)
2. 🔨 Implement Feature 1: Hybrid Search
   - Step 1.1: Install BM25 library
   - Step 1.2: Create BM25Service
   - Step 1.3: Create HybridSearchService (RRF)
   - Step 1.4: Integrate into RAGService
   - Step 1.5: Update DocumentProcessor (index rebuild)
   - Testing: Basic hybrid search tests

### Day 2 (2-3 hours)
3. 🔨 Implement Feature 2: Query Rewriting
   - Step 2.1: Create QueryRewriter
   - Step 2.2: Integrate multi-query search
   - Testing: Query variation tests

4. 🔨 Implement Feature 3: Reranking
   - Step 3.1: Install sentence-transformers
   - Step 3.2: Create RerankerService
   - Step 3.3: Integrate into HybridSearchService
   - Testing: Reranking quality tests

### Day 3 (1-2 hours)
5. 🔨 Implement Feature 4: Self-RAG
   - Step 4.1: Create SelfRAGService
   - Step 4.2: Integrate into RAGService
   - Testing: Relevance check tests

### Day 4 (2 hours)
6. 🧪 Integration Testing
   - End-to-end pipeline test
   - Performance benchmarking
   - Edge case testing

7. 📊 Performance Evaluation
   - Compare metrics (before/after)
   - Document improvements
   - Update README

---

## 📁 New Files Created

```
knowledge/services/
├── bm25_service.py           (NEW) - BM25 keyword search
├── query_rewriter.py         (NEW) - Multi-query generation
├── reranker_service.py       (NEW) - Cross-encoder reranking
├── self_rag_service.py       (NEW) - Relevance validation
└── hybrid_search_service.py  (NEW) - Main orchestrator (RRF fusion)

media/
└── bm25_index.pkl            (NEW) - Serialized BM25 index

docs/
└── SPRINT_8_RAG_2.0_PLAN.md  (THIS FILE)
```

---

## 📁 Modified Files

```
knowledge/services/
└── rag_service.py            (MODIFIED) - Add hybrid search + self-RAG flags

knowledge/services/
└── document_processor.py     (MODIFIED) - Rebuild BM25 index after processing

requirements.txt              (MODIFIED) - Add rank-bm25, sentence-transformers

queries/
└── views.py                  (MODIFIED) - Update query endpoint to use new pipeline
```

---

## 🧪 Testing Strategy

### Unit Tests
- Test each service independently
- Mock external dependencies (LLM, Supabase)
- Focus on edge cases

### Integration Tests
- Test full RAG 2.0 pipeline
- Use real documents and queries
- Measure end-to-end latency

### Performance Tests
- Benchmark each component
- Memory profiling (especially BM25 index, cross-encoder)
- Concurrent request testing

### Quality Tests
- Retrieval accuracy (manual evaluation on 20 test queries)
- Precision@5, Recall@20
- Hallucination rate (manual evaluation)

---

## 📊 Success Metrics

### Performance Targets
| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Retrieval Accuracy | 75% | 92% | Manual eval (20 queries) |
| Precision@5 | 70% | 85% | Automated |
| Recall@20 | 60% | 80% | Automated |
| Hallucination Rate | 10% | 3% | Manual eval |
| Query Latency (p95) | 3s | 4s | Automated |
| Memory Usage | 100MB | 400MB | Automated |

### Quality Gates
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ Retrieval accuracy ≥ 90%
- ✅ Precision@5 ≥ 80%
- ✅ Query latency p95 ≤ 5s
- ✅ No regressions in existing features

---

## 🚨 Risk Mitigation

### Risk 1: Increased Latency
- **Risk:** Query rewriting + reranking add ~800ms latency
- **Mitigation:**
  - Cache query rewrites by hash
  - Use ThreadPoolExecutor for parallel searches
  - Load cross-encoder model on startup (not per-request)

### Risk 2: Memory Usage
- **Risk:** BM25 index + cross-encoder model = ~300MB RAM
- **Mitigation:**
  - Lazy load models (only when needed)
  - Use model quantization if needed
  - Monitor memory usage in production

### Risk 3: BM25 Index Staleness
- **Risk:** Index not updated when new documents added
- **Mitigation:**
  - Rebuild index after each document processing
  - Add background task to rebuild index nightly (if batch uploads)

### Risk 4: Polish Language Support
- **Risk:** Cross-encoder may not work well for Polish
- **Mitigation:**
  - Test with Polish queries first
  - Use multilingual models (`mmarco` variants)
  - Fallback to pure hybrid search if reranking degrades quality

---

## 🔄 Rollback Plan

If RAG 2.0 causes issues in production:

1. **Feature Flags:** All features are opt-in via parameters
   ```python
   rag_service.process_query(
       question,
       use_hybrid_search=False,  # Disable hybrid search
       use_self_rag=False        # Disable self-RAG
   )
   ```

2. **Backward Compatibility:** Old vector-only search still available

3. **Database:** No schema changes, fully backward compatible

4. **Deployment:** Deploy with feature flags OFF, enable gradually

---

## 📈 Expected Impact

### User Experience
- **Faster accurate answers** - Better retrieval = better context
- **Fewer hallucinations** - Self-RAG prevents bad answers
- **Exact match support** - BM25 finds "Art. 5" instantly
- **Synonym handling** - Query rewriting finds related terms

### System Performance
- **Latency:** +800ms (acceptable for quality gain)
- **Memory:** +300MB (manageable)
- **API costs:** +$0.001 per query (query rewriting)

### Development Benefits
- **State-of-the-art RAG** - Matches 2025 industry standards
- **Modular architecture** - Each feature can be toggled independently
- **Testable** - Clear interfaces, easy to unit test
- **Scalable** - BM25 index can handle 10K+ documents

---

## 🎓 Learning Outcomes

By implementing RAG 2.0, we master:
1. **Hybrid Search** - BM25 + vector fusion (industry standard)
2. **Query Optimization** - Multi-query RAG, rewriting techniques
3. **Reranking** - Cross-encoder usage, re-scoring strategies
4. **Self-Reflection** - LLM self-evaluation, confidence scoring
5. **Production RAG** - Real-world best practices, not toy demos

---

## 📚 References

### Papers & Articles
- **Hybrid Search:** "Reciprocal Rank Fusion" (Cormack et al., 2009)
- **Multi-Query RAG:** "Query Rewriting for Retrieval-Augmented Generation" (2024)
- **Self-RAG:** "Self-RAG: Learning to Retrieve, Generate, and Critique" (Asai et al., 2023)
- **Corrective RAG:** "Corrective Retrieval Augmented Generation" (Yan et al., 2024)

### Libraries & Models
- **rank-bm25:** https://github.com/dorianbrown/rank_bm25
- **sentence-transformers:** https://www.sbert.net/
- **Cross-Encoder Models:** https://huggingface.co/cross-encoder

### Industry Best Practices
- **Weaviate RAG Guide:** https://weaviate.io/blog/advanced-rag
- **LangChain Multi-Query:** https://python.langchain.com/docs/use_cases/query_analysis
- **Superlinked Hybrid Search:** https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking

---

## ✅ Sprint Success Criteria

This sprint is complete when:
- ✅ All 4 features implemented and tested
- ✅ Retrieval accuracy ≥ 90% (measured on test set)
- ✅ Query latency p95 ≤ 5s
- ✅ Self-RAG prevents hallucinations (< 5% false positives)
- ✅ BM25 index auto-rebuilds on document processing
- ✅ Documentation updated (ADVANCED_RAG.md)
- ✅ Sprint summary document created (SPRINT_8_COMPLETE.md)

---

**Ready to implement!** 🚀

**Next Step:** Create feature branch and start with Feature 1 (Hybrid Search).

---

**Author:** Mike @LaVanguard
**Sprint:** 8 - RAG 2.0 Query Optimization
**Date:** 27.10.2025
**Status:** Planning Complete ✅
