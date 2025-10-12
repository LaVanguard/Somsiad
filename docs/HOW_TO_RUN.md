# How to Run Somsiad - Quick Start Guide

**Get your advanced RAG system running in 15 minutes!**

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- [ ] Supabase account ([Sign up](https://supabase.com))
- [ ] ~$5 OpenAI credit (for testing)

---

## Step 1: Clone & Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/LaVanguard/Law_Advisor.git
cd Law_Advisor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure API Keys (3 minutes)

### A. Create `.env` file

```bash
# Copy example file
cp .env.example .env
```

### B. Add your API keys

Edit `.env` and add:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbG...your-supabase-anon-key

# Django
SECRET_KEY=your-django-secret-key
DEBUG=True
```

### C. Get Supabase credentials

1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Create new project (or use existing)
3. Go to Project Settings → API
4. Copy:
   - **URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`

---

## Step 3: Setup Supabase Database (5 minutes)

### A. Enable pgvector extension

In Supabase SQL Editor, run:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

### B. Create embeddings table

```sql
-- Create embeddings table
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    embedding VECTOR(1536),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for fast similarity search
CREATE INDEX ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### C. Create search function

```sql
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

---

## Step 4: Initialize Django (2 minutes)

```bash
# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
# Follow prompts to set username, email, password
```

---

## Step 5: Upload Documents (3 minutes)

### A. Start Django server

```bash
python manage.py runserver
```

### B. Create user account

1. Go to: http://127.0.0.1:8000/accounts/signup/
2. Sign up with your email
3. Login

### C. Upload a document (Two Options)

**Option 1: Via Web Interface (Recommended)**
1. Click hamburger menu (☰) in top left
2. Switch to "Dokumenty" tab
3. Fill in form:
   - **Tytuł:** `Warunki techniczne budynków 2022`
   - **Kategoria:** Choose `Budowa`
   - **File:** Upload PDF
4. Click "Dodaj PDF"
5. Click "Przetwórz" button when document appears

**Option 2: Via Admin Panel**
1. Go to: http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Navigate to: **Knowledge → Documents → Add Document**
4. Fill in form and save

---

## Step 6: Process Documents (5-10 minutes)

### Process uploaded documents

```bash
# Process all unprocessed documents
python manage.py process_documents --all
```

### Expected output:

```
Processing document: Warunki techniczne budynków 2022 (ID: 1)
Extracted 60 pages from document
Preprocessing Warunki techniczne budynków 2022...
Preprocessing stats: 2847 chars removed (5.2% reduction)
Generating document summary for Warunki techniczne budynków 2022...
Summary generated: 1340 chars
Using semantic chunking (by articles)...
Created 124 semantic chunks
Adding document summary as searchable chunk...
Generated 125 embeddings
Stored 125 embeddings in Supabase
✅ Successfully processed Warunki techniczne budynków 2022:
   - Chunks: 125
   - Embeddings: 125
   - Summary: Yes
   - Semantic chunking: Yes

Processing complete: 1 succeeded, 0 failed out of 1 total
```

---

## Step 7: Test the System! (2 minutes)

### A. Test RAG pipeline

```bash
# Run advanced RAG test
python test_advanced_rag.py
```

### B. Ask a question via chat

1. Go to: http://127.0.0.1:8000/
2. Login (or signup)
3. Type a question in the chat input
4. **Press Enter** to send (or Shift+Enter for new line)
5. Watch the **real-time streaming response** appear word-by-word!

**Example questions:**
- "Jak wysoko mogę zbudować ogrodzenie od strony ulicy?"
- "Czy mogę wyciąć drzewo bez pozwolenia?"
- "Jakie przeglądy są obowiązkowe w domu?"

### Expected result:

```
🟦 Your Question:
"Jak wysoko mogę zbudować ogrodzenie od strony ulicy?"

🤖 Somsiad (streaming word-by-word):
"Według przepisów technicznych, ogrodzenie od strony ulicy może mieć
maksymalną wysokość 2,2 metra. Przepisy te określone są w rozporządzeniu
w sprawie warunków technicznych..."

📄 Źródła:
- Art. 5 - Warunki techniczne (str. 12)
- Art. 12 - Ogrodzenia (str. 28)

⏱️ Czas odpowiedzi: 3.45s
```

### C. Test conversation features

1. **View conversation history:**
   - Click hamburger menu (☰)
   - Switch to "Rozmowy" tab
   - See your conversations grouped by date (Dzisiaj/Wczoraj/Starsze)

2. **Start new conversation:**
   - Click "Nowa rozmowa" button
   - Ask a different question
   - See it appear in the sidebar

3. **Load old conversation:**
   - Click on any previous conversation
   - See full message history load instantly

---

## Troubleshooting

### Issue: "No module named 'langchain'"

**Fix:**
```bash
pip install -r requirements.txt
```

### Issue: "OpenAI API key not found"

**Fix:**
Check `.env` file exists and contains:
```bash
OPENAI_API_KEY=sk-...
```

### Issue: "Supabase connection failed"

**Fix:**
1. Verify Supabase URL and key in `.env`
2. Check pgvector extension is enabled
3. Verify embeddings table exists

### Issue: "PDF processing fails"

**Fix:**
- Ensure PDF is text-based (not scanned image)
- Check file size < 50MB
- Try different PDF

### Issue: "Encoding errors (� characters)"

**Fix:**
Preprocessor should auto-fix. If not, the PDF may have:
- Non-standard encoding
- Scanned images (use OCR first)

---

## Project Structure Quick Reference

```
Law_Advisor/
├── legal_documents/raw/budowa/  ← Put your PDFs here
├── docs/                        ← Documentation
├── knowledge/services/          ← RAG system code
├── manage.py                    ← Django management
└── .env                         ← API keys (never commit!)
```

---

## Important Commands

### Development Server
```bash
python manage.py runserver
```

### Process Documents
```bash
# All unprocessed
python manage.py process_documents --all

# Specific document
python manage.py process_documents --document-id 1

# Reprocess (delete old embeddings)
python manage.py process_documents --document-id 1 --reprocess
```

### Django Admin
```bash
# Create superuser
python manage.py createsuperuser

# Access admin
http://127.0.0.1:8000/admin/
```

### Testing
```bash
# Test preprocessing
python test_preprocessing.py

# Test advanced RAG
python test_advanced_rag.py

# Django tests
pytest
```

---

## Next Steps

Now that it's running:

1. **Add more documents:**
   - Go to Django admin → Documents → Add
   - Process with `python manage.py process_documents --all`

2. **Test queries:**
   - Use the chat interface at http://127.0.0.1:8000/
   - Try different types of questions

3. **Check quality:**
   - Are answers accurate?
   - Are sources relevant?
   - Adjust retrieval parameters if needed

4. **Read advanced docs:**
   - See `docs/ADVANCED_RAG.md` for architecture details
   - See `docs/API_KEYS_SETUP.md` for more configuration options

---

## Cost Monitoring

**Track your usage:**
1. OpenAI Dashboard: https://platform.openai.com/usage
2. Supabase Dashboard: Check database size

**Typical costs (development):**
- Document processing: ~$0.01 per 50-page document
- Queries: ~$0.01 per query
- Monthly: ~$2-5 for testing

---

## Getting Help

**Documentation:**
- [ADVANCED_RAG.md](ADVANCED_RAG.md) - RAG system details
- [API_KEYS_SETUP.md](API_KEYS_SETUP.md) - Configuration guide
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Database setup

**Issues:**
- GitHub Issues: https://github.com/LaVanguard/Law_Advisor/issues

**Learning Resources:**
- LangChain Docs: https://python.langchain.com/docs/
- Supabase AI Docs: https://supabase.com/docs/guides/ai
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings

---

## Success Checklist

You're ready when:

- [ ] Django server runs without errors
- [ ] User account created and logged in
- [ ] At least one document uploaded
- [ ] Document processed successfully (125+ chunks created)
- [ ] Test script passes all checks
- [ ] Chat interface responds to queries with **streaming** (word-by-word)
- [ ] Sources show high similarity scores (>0.75)
- [ ] Answers are relevant and in Polish
- [ ] Conversations appear in sidebar grouped by date
- [ ] Enter key sends messages, Shift+Enter creates new line
- [ ] Document upload works from web interface

---

**Congratulations! You have a production-quality RAG system running!**

Now go ask Somsiad some legal questions and enjoy your advanced AI-powered legal advisor!

---

**Last Updated:** 2025-10-12
**Author:** Mike @LaVanguard
**Time to Complete:** ~15 minutes (plus document processing time)
