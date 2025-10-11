# Sprint 2 Quick Start Guide

## 🚀 Get Your RAG System Running in 30 Minutes

This guide will get your RAG-powered legal advisor up and running quickly.

---

## Prerequisites

- ✅ Sprint 1 complete (authentication working)
- ✅ Python virtual environment active
- ✅ Django server can start

---

## Step 1: Get API Keys (15 min)

### A. OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up / Log in
3. Profile → "API keys" → "Create new secret key"
4. Copy key (starts with `sk-proj-...`)
5. Add $5-10 credit (Settings → Billing)

### B. Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up / Log in
3. "New Project":
   - Name: `Law_Advisor`
   - Password: (save it!)
   - Region: closest to you
   - Plan: Free
4. Wait ~2 minutes
5. **Database → Extensions** → Enable **pgvector**
6. **SQL Editor** → Run this:

```sql
-- Create embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx
ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create search function
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

7. **Settings → API** → Copy:
   - Project URL
   - anon public key

---

## Step 2: Configure .env (2 min)

Edit `.env` file in project root:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxx

# Environment
ENVIRONMENT=local
```

**Verify:**
```bash
python -c "from decouple import config; print('OpenAI:', 'OK' if config('OPENAI_API_KEY', default='') else 'MISSING'); print('Supabase:', 'OK' if config('SUPABASE_URL', default='') else 'MISSING')"
```

---

## Step 3: Prepare Sample Documents (5 min)

### Option A: Use Provided Samples (Quick)

1. Sample documents are in `sample_documents/` folder
2. Convert `.txt` to PDF:
   - **Online:** Use [txt2pdf.com](https://txt2pdf.com)
   - **Word:** Open .txt → Save As PDF
   - **LibreOffice:** Open .txt → Export as PDF

3. You should have 3 PDFs:
   - `budowa_przylegrod.pdf`
   - `drzewa_i_krzewy.pdf`
   - `przeglady_obowiazkowe.pdf`

### Option B: Use Real Documents (Better)

Find Polish legal documents (PDFs) about:
- Prawo budowlane
- Przepisy o ogrodach
- Obowiązki właścicieli domów

---

## Step 4: Upload & Process Documents (5 min)

### A. Start Server

```bash
venv\Scripts\python.exe manage.py runserver
```

### B. Upload via Admin

1. Go to: http://127.0.0.1:8000/admin/
2. Log in (superuser)
3. Go to: **Knowledge → Documents**
4. Click "Add Document"
5. Fill in:
   - **Title:** "Prawo budowlane - ogrodzenia"
   - **Category:** budowa
   - **File:** Upload PDF
6. Click "Save"
7. Repeat for all documents

### C. Process Documents

Open new terminal (keep server running):

```bash
venv\Scripts\python.exe manage.py process_documents --all
```

You should see:
```
Processing document: Prawo budowlane - ogrodzenia
Created 12 chunks from Prawo budowlane - ogrodzenia
Generated 12 embeddings
Stored 12 embeddings in Supabase
✅ Successfully processed Prawo budowlane - ogrodzenia

Processing complete: 3 succeeded, 0 failed out of 3 total
```

---

## Step 5: Test RAG System (3 min)

1. Go to: http://127.0.0.1:8000/
2. Log in
3. Ask a question:
   - "Jak wysoko mogę zbudować ogrodzenie od strony ulicy?"
   - "Czy mogę wyciąć drzewo bez pozwolenia?"
   - "Jakie przeglądy są obowiązkowe w domu?"

4. You should see:
   - ✅ AI-generated answer in Polish
   - 📚 Source documents with page numbers
   - ⏱️ Processing time

---

## Troubleshooting

### "RAG system not configured yet!"
- Check `.env` has all 3 keys
- Restart Django server after editing .env

### "No documents found for retrieval"
- Run: `python manage.py process_documents --all`
- Check admin: Documents should have `processed=True`

### "Supabase connection failed"
- Check Supabase project is not paused (supabase.com dashboard)
- Verify pgvector extension is enabled
- Check URL and key are correct

### "OpenAI API error"
- Check you added credit to OpenAI account
- Verify API key is valid (platform.openai.com)
- Check spending limits

### Documents not processing
- Check PDF is text-based (not scanned image)
- Try smaller PDF first (< 10 pages)
- Check logs: `venv\Scripts\python.exe manage.py process_documents --document-id 1`

---

## What's Working Now

✅ **RAG Pipeline:**
- PDF → Text extraction
- Text → Chunking
- Chunks → OpenAI embeddings
- Embeddings → Supabase storage
- Query → Vector search → GPT-4o-mini → Answer

✅ **Chat Interface:**
- Real AI responses
- Source attribution
- Processing time tracking
- Query history saved

✅ **Management:**
- Django admin for documents
- CLI command for processing
- Logging for debugging

---

## Next Steps

### Sprint 2 Remaining:
- [ ] Test with more documents
- [ ] Fine-tune chunk size/overlap
- [ ] Optimize retrieval (top-k)
- [ ] Add error recovery

### Sprint 3 Preview:
- Query history UI
- Conversation continuations
- Rating system
- User dashboard

---

## Cost Monitoring

### Check Usage:

**OpenAI:**
- Go to: platform.openai.com/usage
- Set spending limit: $10/month

**Supabase:**
- Go to: Settings → Usage
- Monitor: Database size, API calls

### Expected Costs (Dev):
- **Embeddings:** ~$0.10 for 1000 docs
- **Queries:** ~$0.02 per query
- **Total:** ~$2-5/month

---

## Need Help?

**Documentation:**
- `docs/API_KEYS_SETUP.md` - Detailed API setup
- `docs/SUPABASE_SETUP.md` - Full Supabase guide
- `docs/GIT_WORKFLOW.md` - Git safety rules

**Common Commands:**
```bash
# Process all documents
python manage.py process_documents --all

# Process single document
python manage.py process_documents --document-id 1

# Reprocess (delete old embeddings)
python manage.py process_documents --document-id 1 --reprocess

# Check Django
python manage.py check

# Run server
python manage.py runserver
```

---

**You're all set! 🎉**

Ask legal questions and watch RAG magic happen!

---

**Last Updated:** 11.10.2024
**Author:** Mike @LaVanguard
