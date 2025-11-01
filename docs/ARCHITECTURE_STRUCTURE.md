# Somsiad - Architecture Structure (ASCII Diagram)

**Project:** Law_Advisor (Somsiad - AI Legal Advisor)
**Version:** 1.0
**Date:** 2025-10-31
**Sprint:** 8 (RAG 2.0 Optimization - 25% Complete)

---

## Overview

This document provides a comprehensive ASCII-based visualization of the Somsiad project architecture, showing the relationships between documentation, application components, services, and external dependencies.

---

```
SOMSIAD - AI LEGAL ADVISOR ARCHITECTURE
========================================

┌─────────────────────────────────────────────────────────────────────┐
│                         DOCS/ (Dokumentacja)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  PRD.md ──────────────────────┐                                     │
│  SPRINT_8_RAG_2.0_PLAN.md     │                                     │
│  SPRINT_1-7_SUMMARY.md        │                                     │
│  ADVANCED_RAG.md              ├─→ Definicje wymagań biznesowych     │
│  API_KEYS_SETUP.md            │                                     │
│  DEPLOYMENT.md                │                                     │
│  HOW_TO_RUN.md ───────────────┘                                     │
│                                                                       │
│  supabase_*.sql ──────────────→ Funkcje RPC dla pgvector           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Dokumentuje wymagania
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       WARSTWA APLIKACJI DJANGO                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  config/ ──────────────────────┐                                    │
│  ├─ settings.py                ├─→ Konfiguracja projektu           │
│  ├─ urls.py                    │   (env vars, DB, middleware)       │
│  └─ wsgi.py/asgi.py ───────────┘                                    │
│                                                                       │
│  accounts/ ────────────────────┐                                    │
│  ├─ models.py (User)           ├─→ Autentykacja użytkowników       │
│  ├─ views.py                   │   (django-allauth)                 │
│  └─ adapters.py ───────────────┘                                    │
│                                  │                                   │
│                                  │ FK: user_id                       │
│                                  ▼                                   │
│  queries/ ─────────────────────┐                                    │
│  ├─ models.py                  │                                    │
│  │   ├─ Conversation ──────────┼─→ Grupy rozmów użytkownika        │
│  │   ├─ Query ─────────────────┼─→ Historia Q&A + feedback         │
│  │   └─ SystemPrompt ──────────┼─→ Edytowalny prompt systemu       │
│  └─ views.py ──────────────────┘   (create, list, load, delete)    │
│           │                                                          │
│           │ Wywołuje RAG Service                                     │
│           ▼                                                          │
│  knowledge/ ───────────────────┐                                    │
│  ├─ models.py                  │                                    │
│  │   ├─ Document ──────────────┼─→ PDF dokumenty prawne            │
│  │   └─ Embedding ─────────────┼─→ Linki do Supabase pgvector      │
│  │                              │                                    │
│  ├─ services/ ─────────────────┤                                    │
│  │   │                          │                                    │
│  │   ├─ rag_service.py ────────┼─→ Główna logika RAG               │
│  │   │   ├─ process_query()    │   - Embeddings (OpenAI)           │
│  │   │   ├─ search_similar()   │   - LLM (GPT-4o-mini)             │
│  │   │   └─ generate_answer()  │   - Koordynacja pipeline          │
│  │   │          │               │                                    │
│  │   │          │               │                                    │
│  │   │   ┌──────┴─────────┐    │                                    │
│  │   │   │                 │    │                                    │
│  │   │   ▼                 ▼    │                                    │
│  │   ├─ hybrid_search_service.py─→ RAG 2.0 - Feature 1             │
│  │   │   ├─ hybrid_search()     │   - BM25 + Vector search          │
│  │   │   ├─ RRF fusion (k=60)   │   - Reciprocal Rank Fusion        │
│  │   │   └─ multi_query()       │                                    │
│  │   │          │                │                                    │
│  │   │          ├──────────────┐ │                                    │
│  │   │          │              │ │                                    │
│  │   │          ▼              ▼ │                                    │
│  │   ├─ bm25_service.py ───────┼─→ BM25 keyword search              │
│  │   │   ├─ build_index()      │   (rank-bm25 library)              │
│  │   │   ├─ search()           │   Index: media/bm25_index.pkl      │
│  │   │   └─ Polish tokenizer   │                                    │
│  │   │                          │                                    │
│  │   ├─ document_processor.py ─┼─→ Pipeline przetwarzania PDF       │
│  │   │   ├─ process_document() │   (wywołuje komponenty poniżej)    │
│  │   │   └─ rebuild BM25 index │                                    │
│  │   │          │               │                                    │
│  │   │          ├───────┬───────┼────────┐                          │
│  │   │          ▼       ▼       ▼        ▼                          │
│  │   ├─ preprocessor.py ────────┼─→ Czyszczenie tekstu (9% noise)   │
│  │   ├─ semantic_chunker.py ───┼─→ Chunking wg struktury prawnej   │
│  │   │                          │   (Art., §, Rozdział)              │
│  │   └─ summarizer.py ──────────┼─→ Hierarchiczne podsumowania      │
│  │                              │   (dokument, rozdział, chunk)      │
│  └─────────────────────────────┘                                    │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                    Komunikacja z zewnętrznymi serwisami
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  SUPABASE    │    │   OPENAI API     │    │  DJANGO DB       │
│  PostgreSQL  │    │                  │    │  (SQLite/Pg)     │
├──────────────┤    ├──────────────────┤    ├──────────────────┤
│              │    │                  │    │                  │
│ vector_      │    │ text-embedding-  │    │ User             │
│ embeddings   │    │ 3-small          │    │ Conversation     │
│   ├─ id      │◄───┤ $0.00002/1K      │    │ Query            │
│   ├─ content │    │                  │    │ Document         │
│   ├─ embedding    │ gpt-4o-mini      │    │ Embedding        │
│   └─ metadata│    │ $0.15/1M tokens  │    │ SystemPrompt     │
│              │    │                  │    │                  │
│ RPC:         │    │ Streaming SSE    │    │                  │
│ match_       │    │ supported        │    │                  │
│ embeddings() │    │                  │    │                  │
│              │    │                  │    │                  │
│ pgvector     │    │                  │    │                  │
│ extension    │    │                  │    │                  │
└──────────────┘    └──────────────────┘    └──────────────────┘
      │                    │                         │
      │                    │                         │
      └────────────────────┴─────────────────────────┘
                           │
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         WARSTWA FRONTEND                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  templates/ ───────────────────┐                                    │
│  ├─ base.html                  │                                    │
│  ├─ chat/                      ├─→ UI interfejsu czatu             │
│  │   ├─ chat.html              │   - HTMX (dynamiczne updaty)       │
│  │   └─ message_bubble.html    │   - Alpine.js (reaktywność)        │
│  ├─ accounts/                  │   - Tailwind CSS (styling)         │
│  │   ├─ login.html             │                                    │
│  │   └─ signup.html            │                                    │
│  └─ partials/                  │                                    │
│      ├─ conversations_list.html│                                    │
│      └─ conversation_messages  │                                    │
│                                 │                                    │
│  static/ ──────────────────────┤                                    │
│  ├─ css/                       │                                    │
│  │   └─ tailwind.min.css       │                                    │
│  ├─ js/                        │                                    │
│  │   ├─ htmx.min.js            │                                    │
│  │   └─ alpine.min.js          │                                    │
│  └─ Inter font ────────────────┘                                    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP/HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT (Production)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Railway/Render ───────────────┐                                    │
│  ├─ Gunicorn WSGI server       ├─→ Python 3.11                      │
│  ├─ Whitenoise (static files)  │   Django 5.2.7                     │
│  ├─ Environment variables      │   128 tests (59% coverage)         │
│  └─ Health checks              │                                    │
│                                 │                                    │
│  GitHub Actions (CI/CD) ───────┤                                    │
│  ├─ Lint + Security checks     │                                    │
│  ├─ Test automation (pytest)   │                                    │
│  └─ Auto-deploy on merge       │                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PRZEPŁYW DANYCH - RAG QUERY PIPELINE

```
Użytkownik → "Jak wysoko mogę zbudować płot?"
│
│ 1. HTTP POST /api/chat/
│
▼
queries/views.py
│
│ 2. Tworzy Query object (FK: User, Conversation)
│
▼
knowledge/services/rag_service.py :: process_query()
│
│ 3a. use_hybrid_search=True? (Sprint 8)
│     TAK → hybrid_search_service.py
│     │
│     ├─ 3b. BM25 keyword search ─→ bm25_service.py
│     │     └─ Tokenizacja PL → BM25Okapi → top-20 (chunk_id, score)
│     │
│     ├─ 3c. Vector semantic search ─→ OpenAI embeddings
│     │     └─ text-embedding-3-small → Supabase RPC match_embeddings
│     │         → top-20 (content, metadata, similarity)
│     │
│     └─ 3d. RRF Fusion (k=60) ─────→ Top-5 chunks (deduplikacja)
│
│ 4. Context chunks + Question → generate_answer()
│    │
│    └─ SystemPrompt (from DB) + Context + Question
│        → OpenAI GPT-4o-mini
│        → Streaming SSE lub complete response
│
▼
Query.answer (zapisz odpowiedź)
Query.sources (zapisz źródła)
Query.processing_time (timestamp)
│
│ 5. Render partials/message_bubble.html
│
▼
HTMX swap → Wyświetl w UI
```

---

## SPRINT 8 RAG 2.0 FEATURES (25% COMPLETE)

```
✅ Feature 1: Hybrid Search (BM25 + Vector + RRF)
   Files: bm25_service.py, hybrid_search_service.py
   Status: Zaimplementowane i przetestowane
   Impact: +17% retrieval accuracy (75% → 92% target)

⏳ Feature 2: Query Rewriting (Multi-Query RAG)
   Files: query_rewriter.py (planowane)
   Status: Nie rozpoczęte
   Impact: +10-15% recall improvement

⏳ Feature 3: Reranking (Cross-Encoder)
   Files: reranker_service.py (planowane)
   Status: Nie rozpoczęte
   Impact: +15% Precision@5 (70% → 85%)

⏳ Feature 4: Self-RAG (Relevance Check)
   Files: self_rag_service.py (planowane)
   Status: Nie rozpoczęte
   Impact: -70% hallucination rate (10% → 3%)
```

---

## ZALEŻNOŚCI KLUCZOWYCH KOMPONENTÓW

```
RAGService (knowledge/services/rag_service.py)
├── depends_on: OpenAI API (embeddings, LLM)
├── depends_on: Supabase (pgvector storage)
├── used_by: queries/views.py (chat endpoint)
└── used_by: knowledge/services/document_processor.py

HybridSearchService (Sprint 8)
├── depends_on: BM25Service
├── depends_on: RAGService (vector search)
├── depends_on: Supabase (chunk fetching)
└── used_by: RAGService.process_query()

BM25Service
├── depends_on: rank-bm25 library
├── depends_on: media/bm25_index.pkl (persisted index)
└── rebuilt_by: DocumentProcessor (on new docs)

DocumentProcessor
├── depends_on: Preprocessor (noise removal)
├── depends_on: SemanticChunker (legal structure parsing)
├── depends_on: Summarizer (hierarchical summaries)
├── depends_on: RAGService (embeddings + storage)
└── used_by: knowledge/document_views.py (upload endpoint)
```

---

## DATA MODELS RELATIONSHIPS

```
┌─────────────┐
│    User     │
│  (Django)   │
└──────┬──────┘
       │ 1:N
       ├────────────────────┐
       │                    │
       ▼                    ▼
┌──────────────┐    ┌──────────────┐
│ Conversation │    │   Document   │
│              │    │              │
└──────┬───────┘    └──────┬───────┘
       │ 1:N               │ 1:N
       │                   │
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│    Query     │    │  Embedding   │
│              │    │              │
│ - question   │    │ - chunk_text │
│ - answer     │    │ - embedding_id (Supabase)
│ - sources    │    │ - metadata   │
│ - rating     │    │              │
└──────────────┘    └──────────────┘
       │
       │ References
       ▼
┌──────────────┐
│ SystemPrompt │
│              │
│ - prompt_text│
│ - is_active  │
└──────────────┘
```

---

## METRYKI KLUCZOWE

### Performance
- **Query latency (P95):** Target <5s, Current ~3s
- **TTFT (Time To First Token):** Target <5s (SSE streaming)
- **BM25 index rebuild:** <5s (434 chunks)
- **Vector search:** ~100ms (Supabase pgvector)

### Jakość RAG
- **Retrieval accuracy:** Baseline 75% → Target 92% (Sprint 8)
- **Precision@5:** 70% → 85%
- **Hallucination rate:** 10% → 3%

### Coverage
- **128 unit/integration tests**
- **59% code coverage**
- **Playwright E2E infrastructure ready**

---

## TECH STACK SUMMARY

### Backend
- Django 5.2.7
- Python 3.11
- LangChain (RAG orchestration)
- OpenAI API (GPT-4o-mini, text-embedding-3-small)
- Supabase (PostgreSQL + pgvector)

### Frontend
- HTMX 1.9.10 (HTML-over-the-wire)
- Alpine.js 3.x (reactivity)
- Tailwind CSS (styling)

### Testing & CI/CD
- pytest + pytest-django (128 tests)
- Playwright (E2E)
- GitHub Actions (CI/CD)

### Deployment
- Gunicorn (WSGI server)
- Whitenoise (static files)
- Railway/Render (hosting)

---

## FILE STRUCTURE

```
Law_Advisor/
├── docs/                           # Dokumentacja (← START HERE)
│   ├── PRD.md                      # Product Requirements
│   ├── SPRINT_8_RAG_2.0_PLAN.md   # Sprint 8 implementation plan
│   ├── ARCHITECTURE_STRUCTURE.md  # This file
│   └── ...
│
├── config/                         # Django project settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                       # Authentication app
│   ├── models.py                   # User model (Django built-in)
│   ├── views.py                    # Login/signup/logout
│   └── adapters.py                 # Django-allauth config
│
├── queries/                        # Query & conversation app
│   ├── models.py                   # Conversation, Query, SystemPrompt
│   ├── views.py                    # Chat API endpoints
│   └── templates/
│       └── chat/
│
├── knowledge/                      # RAG knowledge base app
│   ├── models.py                   # Document, Embedding
│   ├── services/
│   │   ├── rag_service.py          # Main RAG orchestration
│   │   ├── hybrid_search_service.py # Sprint 8: Hybrid search
│   │   ├── bm25_service.py         # Sprint 8: BM25 keyword search
│   │   ├── document_processor.py   # PDF processing pipeline
│   │   ├── preprocessor.py         # Text cleaning
│   │   ├── semantic_chunker.py     # Legal structure chunking
│   │   └── summarizer.py           # Hierarchical summaries
│   └── templates/
│       └── documents/
│
├── templates/                      # Global templates
│   ├── base.html
│   └── partials/
│
├── static/                         # Static assets
│   ├── css/
│   ├── js/
│   └── fonts/
│
├── media/                          # User uploads
│   ├── documents/                  # PDF files
│   ├── query_images/               # User-uploaded images
│   └── bm25_index.pkl              # Sprint 8: BM25 index
│
├── tests/                          # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── manage.py                       # Django CLI
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Test configuration
└── .github/
    └── workflows/
        └── ci.yml                  # CI/CD pipeline
```

---

## DOCUMENT PROCESSING PIPELINE

```
PDF Upload (Admin)
│
│ 1. POST /knowledge/upload/
│
▼
knowledge/document_views.py
│
│ 2. Create Document record
│
▼
knowledge/services/document_processor.py :: process_document()
│
├─ 3a. Extract text from PDF (PyPDF2)
│
├─ 3b. preprocessor.py :: clean_text()
│      └─ Remove headers, footers, page numbers (9% noise reduction)
│
├─ 3c. semantic_chunker.py :: chunk_by_legal_structure()
│      └─ Split by: Rozdział, Art., §, ustęp
│      └─ Preserve legal hierarchy
│
├─ 3d. summarizer.py :: create_hierarchical_summaries()
│      └─ Document summary (całość)
│      └─ Chapter summaries (rozdziały)
│      └─ Chunk summaries (fragmenty)
│
├─ 3e. rag_service.py :: generate_embeddings()
│      └─ OpenAI text-embedding-3-small
│      └─ Batch processing (50 chunks/batch)
│
├─ 3f. rag_service.py :: store_embeddings()
│      └─ Supabase vector_embeddings table
│      └─ pgvector extension (cosine similarity)
│
└─ 3g. bm25_service.py :: rebuild_index()
       └─ Polish tokenizer
       └─ BM25Okapi algorithm
       └─ Save to media/bm25_index.pkl
│
▼
Document.processed = True
```

---

## SUMMARY

**Somsiad Architecture:**
1. **Documentation-driven** - `docs/` defines all requirements and plans
2. **Django-based** - 3 main apps: accounts, queries, knowledge
3. **RAG 2.0 Pipeline** - Hybrid search (BM25 + vector) with RRF fusion
4. **External APIs** - OpenAI (embeddings + LLM), Supabase (pgvector)
5. **Modern Frontend** - HTMX + Alpine.js + Tailwind CSS
6. **Production-ready** - CI/CD, testing (59% coverage), deployment infrastructure

**Current State:** Sprint 8 in progress (25% complete)
- ✅ Feature 1: Hybrid Search (BM25 + Vector + RRF)
- ⏳ Features 2-4: Query rewriting, reranking, self-RAG

**Next Steps:**
1. Complete Sprint 8 RAG 2.0 features
2. Deploy to production (Railway/Render)
3. Submit for 10xDevs certification (16.11.2024 deadline)

---

**Author:** Mike @LaVanguard
**Course:** Przeprogramowani 10xDevs
**Project:** Somsiad - AI Legal Advisor for Polish Homeowners
**Last Updated:** 2025-10-31
