# Document Processing Pipeline - Complete Audit & Workflow

**Date:** 2025-10-21
**Purpose:** Audit document upload and processing flow to identify issues

---

## 📋 Expected Workflow (Step-by-Step)

### **Phase 1: Document Upload**

**User Action:** Upload PDF via sidebar
**Location:** `templates/home.html` → Sidebar → Documents Tab → Upload Form

**Backend Flow:**
1. **Request:** `POST /api/documents/upload/`
2. **Handler:** `knowledge/document_views.py:upload_document()` (line 21)
3. **Steps:**
   - Validate title exists
   - Validate file is PDF
   - Create `Document` object in Django DB with `processed=False`
   - Save PDF to `media/documents/`
4. **Response:** Success message + HTMX refresh of unprocessed list
5. **Database State:**
   - `documents` table: New row with `processed=False`
   - `embeddings` table: No changes yet

**Expected Outcome:** ✅ Document appears in "Nieprzetworzone" (Unprocessed) section

---

### **Phase 2: Document Processing**

**User Action:** Click "Przetwórz" button on document
**Location:** Sidebar → Unprocessed Documents → Process Button

**Backend Flow:**
1. **Request:** `POST /api/documents/{id}/process/`
2. **Handler:** `knowledge/document_views.py:process_document()` (line 77)
3. **Creates:** `DocumentProcessor` instance (line 89)
4. **Calls:** `processor.process_document(document)`

---

### **Phase 3: Document Processing Pipeline**

**Location:** `knowledge/services/document_processor.py:process_document()` (line 68)

#### **Step 1: PDF Text Extraction**
- **Method:** `extract_text_from_pdf(file_path)` (line 42)
- **Library:** PyPDF2
- **Output:** `Dict[int, str]` (page_number → text)
- **Potential Issues:**
  - File path not found
  - Corrupted PDF
  - Scanned PDF (no extractable text)

#### **Step 2: Text Preprocessing** (Optional, enabled by default)
- **Service:** `DocumentPreprocessor` (line 98)
- **File:** `knowledge/services/preprocessor.py`
- **Purpose:** Remove administrative noise, headers, footers
- **Output:** Cleaned text
- **Potential Issues:**
  - Over-aggressive cleaning
  - Regex errors

#### **Step 3: Document Summarization** (Optional, enabled by default)
- **Service:** `DocumentSummarizer` (line 110)
- **File:** `knowledge/services/summarizer.py`
- **Purpose:** Generate document-level summary using OpenAI
- **Requires:** `OPENAI_API_KEY` in environment
- **Potential Issues:**
  - ❌ **Missing API key**
  - ❌ **Network timeout**
  - ❌ **OpenAI rate limits**
  - ❌ **Invalid API key**

#### **Step 4: Semantic Chunking** (Enabled by default)
- **Service:** `SemanticChunker` (line 125)
- **File:** `knowledge/services/semantic_chunker.py`
- **Purpose:** Split document by legal structure (Art., §, Rozdział)
- **Output:** List of `LegalChunk` objects
- **Potential Issues:**
  - Document doesn't match legal patterns
  - Very large chunks

#### **Step 5: Generate Embeddings**
- **Service:** `RAGService.generate_embeddings()` (line 167)
- **File:** `knowledge/services/rag_service.py:85`
- **Uses:** OpenAI `text-embedding-3-small` model
- **Input:** List of text chunks
- **Output:** List of 1536-dimensional vectors
- **Requires:** `OPENAI_API_KEY`
- **Potential Issues:**
  - ❌ **Missing API key**
  - ❌ **Network errors (getaddrinfo failed)**
  - ❌ **Rate limiting**
  - ❌ **Text too long (>8191 tokens)**

#### **Step 6: Store in Supabase**
- **Service:** `RAGService.store_embeddings()` (line 171)
- **File:** `knowledge/services/rag_service.py:98`
- **Method:** Insert into `embeddings` table
- **Requires:**
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - Table `embeddings` must exist
- **Potential Issues:**
  - ❌ **Supabase connection failed**
  - ❌ **Table doesn't exist**
  - ❌ **Wrong vector dimension**
  - ❌ **Network timeout**

#### **Step 7: Store References in Django**
- **Location:** `document_processor.py:179`
- **Action:** Create `Embedding` objects in Django DB
- **Links:** Supabase embedding ID → Django Document
- **Potential Issues:**
  - Database transaction errors
  - Embedding ID mismatch

#### **Step 8: Mark as Processed**
- **Location:** `document_processor.py:188`
- **Action:** Set `document.processed = True`
- **Result:** Document moves from "Nieprzetworzone" to "Przetworzone"

---

## 🔍 Common Issues & Debugging

### **Issue 1: getaddrinfo failed**
**Error:** `[Errno 11001] getaddrinfo failed`

**Root Cause:** Network DNS resolution failure when trying to connect to:
- `api.openai.com` (for embeddings/summaries)
- `<project>.supabase.co` (for vector storage)

**Possible Reasons:**
1. No internet connection
2. Firewall blocking requests
3. Invalid API endpoint URL
4. DNS server issues

**Debug Steps:**
```python
# Test OpenAI connection
from openai import OpenAI
client = OpenAI(api_key="your-key")
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="test"
)
print(response)

# Test Supabase connection
from supabase import create_client
supabase = create_client("your-url", "your-key")
response = supabase.table("embeddings").select("count").execute()
print(response)
```

---

### **Issue 2: match_embeddings function not found**
**Error:** `PGRST202 - Could not find function match_embeddings`

**Root Cause:** PostgreSQL function not created in Supabase

**Solution:** Run SQL from `docs/SUPABASE_SETUP.md` (lines 69-100)

---

### **Issue 3: Function overloading conflict**
**Error:** `PGRST203 - Could not choose best candidate function`

**Root Cause:** Multiple versions of `match_embeddings` exist

**Solution:** Drop all versions and recreate (see fix above)

---

### **Issue 4: Document processing hangs**
**Symptom:** Processing never completes, no error shown

**Possible Causes:**
1. Very large PDF (>100 pages)
2. OpenAI timeout waiting for embeddings
3. Summarization taking too long

**Debug:**
- Check Django logs: `tail -f logs/django.log`
- Add logging to DocumentProcessor
- Disable summarization temporarily:
  ```python
  processor = DocumentProcessor(generate_summaries=False)
  ```

---

### **Issue 5: Empty chunks / No text extracted**
**Symptom:** "No text extracted" warning

**Causes:**
1. Scanned PDF (images, not text)
2. Encrypted/password-protected PDF
3. Non-standard PDF format

**Solution:**
- Use OCR tool (Tesseract) for scanned PDFs
- Check PDF can be opened normally

---

## 🧪 Testing Checklist

### **1. Environment Variables**
```bash
# Check all required vars are set
python manage.py shell
>>> from django.conf import settings
>>> print(settings.OPENAI_API_KEY[:10] + "...")  # Should show key
>>> print(settings.SUPABASE_URL)  # Should show URL
>>> print(settings.SUPABASE_KEY[:10] + "...")  # Should show key
```

### **2. Supabase Connection**
```bash
# Run connection test
python venv/Scripts/python.exe test_supabase_connection.py
```

### **3. Upload Test**
1. Go to sidebar → Documents tab
2. Upload small test PDF
3. Check appears in "Nieprzetworzone"
4. Check `media/documents/` has the file

### **4. Processing Test**
1. Click "Przetwórz" on uploaded document
2. Watch for success message: "[OK] Dokument ... przetworzony!"
3. Check document moves to "Przetworzone"
4. Check embeddings count is shown

### **5. Query Test**
1. Type question in chat
2. Should get AI response (not error)
3. Check sources are shown at bottom

---

## 🛠️ Quick Fixes

### **Disable Expensive Features for Testing**
Edit `knowledge/document_views.py:89`:
```python
# Disable summaries and preprocessing for faster testing
processor = DocumentProcessor(
    enable_preprocessing=False,
    use_semantic_chunking=True,  # Keep this, it's fast
    generate_summaries=False      # Disable OpenAI calls
)
```

### **Check Logs in Real-Time**
```bash
# In one terminal
python manage.py runserver

# In another terminal
tail -f logs/django.log  # If logging to file
# Or check console output
```

---

## 📊 Expected Performance

| Step | Time (Small PDF) | Time (Large PDF) |
|------|------------------|------------------|
| Upload | <1s | <2s |
| Text Extraction | <1s | 2-5s |
| Preprocessing | <0.5s | 1-2s |
| Summarization | 2-5s | 5-10s |
| Semantic Chunking | <1s | 1-3s |
| Embeddings | 2-10s | 10-30s |
| Supabase Storage | 1-3s | 3-10s |
| **Total** | **5-20s** | **20-60s** |

---

## 🔧 Next Steps

1. **Identify the specific error** you're seeing
2. **Check server logs** for stack trace
3. **Test each component** individually (OpenAI, Supabase, PDF extraction)
4. **Report back** with error message

---

**Status:** ⏳ Waiting for specific error details to debug further
