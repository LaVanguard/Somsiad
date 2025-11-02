# Database Structure Documentation - Somsiad (Law Advisor)

**Last Updated:** 2025-11-02
**Current Sprint:** Sprint 8 - RAG 2.0 Query Optimization
**Database:** Supabase PostgreSQL (Cloud)

---

## 📊 Database Architecture Overview

Somsiad uses a **hybrid database architecture**:

1. **Supabase PostgreSQL** (Cloud) - Primary database for all data
2. **Local Filesystem** - Media files storage (PDFs, images)

```
┌─────────────────────────────────────────────────────────────┐
│                  SUPABASE POSTGRESQL (CLOUD)                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Django Tables (ORM-managed)                                 │
│  ├── auth_user                  (Django default)            │
│  ├── documents                  (Document metadata)          │
│  ├── embeddings                 (Embedding tracking)         │
│  ├── queries                    (User queries & answers)     │
│  ├── conversations              (Chat sessions)              │
│  └── system_prompts             (RAG prompts)               │
│                                                               │
│  Supabase pgvector Table (Direct SQL)                       │
│  └── vector_embeddings          (Vector embeddings + RAG)   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Table Schemas

### 1. **`documents`** (Django ORM)

**Purpose:** Stores metadata about uploaded PDF documents
**Created:** Sprint 2
**Table Name:** `documents`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO | Document ID |
| `title` | VARCHAR(255) | NOT NULL | Document title (auto-generated from filename) |
| `file` | VARCHAR(100) | NOT NULL | Path to PDF file in media/documents/ |
| `category` | VARCHAR(100) | NOT NULL | Document category (default: 'document') |
| `uploaded_at` | TIMESTAMP | NOT NULL, DEFAULT NOW | Upload timestamp |
| `processed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Has document been processed for embeddings? |

**Indexes:**
- PRIMARY KEY on `id`
- Ordered by `-uploaded_at` (newest first)

**Related Django Model:** `knowledge.models.Document`

---

### 2. **`embeddings`** (Django ORM)

**Purpose:** Tracks which embeddings belong to which documents (metadata only)
**Created:** Sprint 2
**Table Name:** `embeddings`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO | Embedding tracking ID |
| `document_id` | INTEGER | FOREIGN KEY → documents.id, CASCADE | Parent document |
| `chunk_text` | TEXT | NOT NULL | Original text chunk from document |
| `embedding_id` | VARCHAR(100) | NOT NULL | UUID of vector in `vector_embeddings` table |
| `metadata` | JSONB | DEFAULT {} | Page number, section, etc. |
| `created_at` | TIMESTAMP | DEFAULT NOW | Creation timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `document_id`
- Ordered by `document`, `id`

**Related Django Model:** `knowledge.models.Embedding`

**⚠️ IMPORTANT:** This table does **NOT** store actual vector embeddings. It only stores metadata and references to `vector_embeddings` table.

---

### 3. **`vector_embeddings`** (Supabase pgvector)

**Purpose:** Stores actual vector embeddings for RAG semantic search
**Created:** Sprint 2
**Table Name:** `vector_embeddings` (renamed from `embeddings` in Sprint 7)
**Access Method:** Direct Supabase API (not Django ORM)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Vector embedding ID |
| `content` | TEXT | NOT NULL | Document chunk text |
| `embedding` | VECTOR(1536) | NOT NULL | OpenAI embedding (text-embedding-3-small) |
| `metadata` | JSONB | DEFAULT {} | Document metadata (title, page, article, etc.) |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW | Creation timestamp |

**Indexes:**
```sql
-- Vector similarity search (pgvector ivfflat)
CREATE INDEX vector_embeddings_embedding_idx
ON vector_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Metadata filtering (optional)
CREATE INDEX vector_embeddings_metadata_idx
ON vector_embeddings
USING gin (metadata);
```

**RPC Functions:**
```sql
-- Vector similarity search function
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
```

**⚠️ CRITICAL NOTES:**
1. This table is **NOT** managed by Django ORM
2. Access via `supabase.table("vector_embeddings")`
3. Sprint 7 renamed from `embeddings` → `vector_embeddings` to avoid conflict
4. Contains 434+ embeddings (as of Sprint 7)

---

### 4. **`queries`** (Django ORM)

**Purpose:** Stores user questions and AI-generated answers
**Created:** Sprint 2, Extended in Sprint 3 (conversations)
**Table Name:** `queries`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO | Query ID |
| `user_id` | INTEGER | FOREIGN KEY → auth_user.id, CASCADE | Query author |
| `conversation_id` | INTEGER | FOREIGN KEY → conversations.id, CASCADE, NULL | Parent conversation |
| `question` | TEXT | NOT NULL | User's legal question |
| `image` | VARCHAR(100) | NULL | Optional image path (media/query_images/) |
| `answer` | TEXT | DEFAULT '' | AI-generated answer |
| `sources` | JSONB | DEFAULT [] | Citations and source documents |
| `rating` | INTEGER | NULL, CHOICES (1, 5) | User feedback (thumbs up/down) |
| `processing_time` | FLOAT | NULL | Total time from query to completion (seconds) |
| `ttft` | FLOAT | NULL | Time To First Token (PRD v2.1 NFR-1, target: <5s P95) |
| `created_at` | TIMESTAMP | DEFAULT NOW | Query timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `user_id`
- FOREIGN KEY on `conversation_id`
- Ordered by `-created_at` (newest first)

**Related Django Model:** `queries.models.Query`

**Sources JSONB Structure:**
```json
[
  {
    "text": "Fragment tekstu...",
    "metadata": {
      "document_title": "Prawo budowlane",
      "article_number": "Art. 29",
      "section_name": "Rozdział 4"
    },
    "similarity": 0.87  // or "rrf_score" in Sprint 8
  }
]
```

---

### 5. **`conversations`** (Django ORM)

**Purpose:** Groups related queries into chat sessions
**Created:** Sprint 3
**Table Name:** `conversations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO | Conversation ID |
| `user_id` | INTEGER | FOREIGN KEY → auth_user.id, CASCADE | Conversation owner |
| `title` | VARCHAR(255) | NOT NULL | Conversation title (auto-generated from first query) |
| `created_at` | TIMESTAMP | DEFAULT NOW | Creation timestamp |
| `updated_at` | TIMESTAMP | AUTO UPDATE | Last message timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `user_id`
- Ordered by `-updated_at` (most recent first)

**Related Django Model:** `queries.models.Conversation`

---

### 6. **`system_prompts`** (Django ORM)

**Purpose:** Stores editable system prompts for RAG responses
**Created:** Sprint 6
**Table Name:** `system_prompts`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO | Prompt ID |
| `prompt_text` | TEXT | NOT NULL | System prompt for RAG responses |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Is this the active prompt? |
| `created_at` | TIMESTAMP | DEFAULT NOW | Creation timestamp |
| `updated_at` | TIMESTAMP | AUTO UPDATE | Last edit timestamp |
| `updated_by_id` | INTEGER | FOREIGN KEY → auth_user.id, SET NULL | Admin who last edited |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `updated_by_id`
- Ordered by `-updated_at`

**Constraints:**
- Only **one** prompt can have `is_active=True` at a time (enforced in Django model)

**Related Django Model:** `queries.models.SystemPrompt`

---

## 🔧 Database Connection Details

### Environment Variables (.env)

```bash
# Supabase PostgreSQL (Cloud Database)
DATABASE_URL=postgresql://postgres.xxx:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# Supabase API (for vector_embeddings table)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...  # service_role key

# OpenAI (for embeddings + LLM)
OPENAI_API_KEY=sk-proj-...
```

### Django Settings

```python
# config/settings/development.py
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Fallback to SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### Supabase Client (Python)

```python
from supabase import create_client, Client

supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)

# Access vector embeddings (NOT Django ORM)
response = supabase.table("vector_embeddings").select("*").execute()
```

---

## 🚨 Common Issues & Known Conflicts

### 1. **Table Naming Conflict (Sprint 7)**

**Problem:**
- Old documentation refers to `embeddings` table
- Sprint 7 renamed it to `vector_embeddings`
- Django ORM has separate `embeddings` table for metadata

**Resolution:**
```python
# ✅ CORRECT (after Sprint 7)
supabase.table("vector_embeddings").insert(records).execute()

# ❌ WRONG (old code)
supabase.table("embeddings").insert(records).execute()
```

### 2. **RPC Function Overloading (Sprint 8 Issue)**

**Problem:**
```
Could not choose the best candidate function between:
- match_embeddings(query_embedding => vector, match_count => integer)
- match_embeddings(query_embedding => vector, match_count => integer, filter => jsonb)
```

**Cause:** Multiple `match_embeddings` functions exist with different signatures

**Resolution:** (See fix section below)

---

## 📋 Migration History

### Sprint 2 (Initial Setup)
- Created `documents`, `embeddings`, `queries` tables
- Created `embeddings` table in Supabase (later renamed)
- Set up Django ORM + Supabase pgvector hybrid

### Sprint 3 (Conversations)
- Added `conversations` table
- Added `conversation_id` to `queries` table

### Sprint 6 (Editable Prompts)
- Added `system_prompts` table

### Sprint 7 (Database Migration)
- **Migrated from SQLite to Supabase PostgreSQL**
- **Renamed `embeddings` → `vector_embeddings`** in Supabase
- Fixed batch insert (50 embeddings per batch to avoid timeout)
- Migrated 434 existing embeddings

### Sprint 8 (RAG 2.0)
- Added BM25 index (local pickle file, not in database)
- Updated `match_embeddings` RPC function (**needs fix**)

---

## 🗂️ Data Flow Diagram

```
┌──────────────┐
│  User Query  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ 1. Create Query in Django                             │
│    queries.models.Query.objects.create(...)           │
│    → Stores in `queries` table                        │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ 2. Generate Embedding (OpenAI API)                    │
│    RAGService.embeddings.embed_query(question)        │
│    → Returns vector(1536)                             │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ 3. Search Vector DB (Supabase RPC)                    │
│    supabase.rpc("match_embeddings", {...})            │
│    → Searches `vector_embeddings` table               │
│    → Returns top-k similar chunks                     │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ 4. Generate Answer (OpenAI GPT-4o-mini)               │
│    RAGService.llm.invoke(prompt + context)            │
│    → Uses retrieved chunks as context                 │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ 5. Update Query with Answer                           │
│    query.answer = answer                              │
│    query.sources = sources                            │
│    query.save()                                       │
│    → Updates `queries` table                          │
└──────────────────────────────────────────────────────┘
```

---

## 🔍 How to Inspect Database

### Via Django Shell

```bash
venv/Scripts/python.exe manage.py shell
```

```python
# Check Django tables
from knowledge.models import Document, Embedding
from queries.models import Query, Conversation, SystemPrompt

# Count documents
Document.objects.count()

# Check queries
Query.objects.filter(user__email="test@example.com")

# Check active system prompt
SystemPrompt.objects.filter(is_active=True).first()
```

### Via Supabase SQL Editor

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Go to **SQL Editor**
3. Run queries:

```sql
-- Check vector embeddings count
SELECT COUNT(*) FROM vector_embeddings;

-- Check recent embeddings
SELECT id, LEFT(content, 50) as preview, metadata->>'document_title' as doc
FROM vector_embeddings
ORDER BY created_at DESC
LIMIT 10;

-- Check indexes
\d vector_embeddings

-- List all RPC functions
\df match_embeddings
```

---

## 📁 Related Files

| File | Purpose |
|------|---------|
| `knowledge/models.py` | Django models: Document, Embedding |
| `queries/models.py` | Django models: Query, Conversation, SystemPrompt |
| `knowledge/services/rag_service.py` | Vector embeddings CRUD |
| `knowledge/services/document_processor.py` | Document processing pipeline |
| `docs/SUPABASE_SETUP.md` | Supabase setup guide |
| `docs/SPRINT_7_DATABASE_UI_IMPROVEMENTS.md` | Migration history |
| `docs/supabase_match_vector_embeddings_function.sql` | RPC function SQL |

---

## ✅ Database Health Checklist

Before running the application, verify:

- [ ] `DATABASE_URL` is set in `.env` (Supabase connection string)
- [ ] `SUPABASE_URL` and `SUPABASE_KEY` are set in `.env`
- [ ] Django migrations applied: `python manage.py migrate`
- [ ] `vector_embeddings` table exists in Supabase
- [ ] `match_embeddings` RPC function exists and works
- [ ] pgvector extension enabled in Supabase
- [ ] At least one active `SystemPrompt` exists

---

**Author:** Mike @LaVanguard
**Documentation Version:** 1.0
**Sprint:** 8 - RAG 2.0 Query Optimization
