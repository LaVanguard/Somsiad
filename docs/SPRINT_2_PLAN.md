# Sprint 2 Plan - Knowledge Base + RAG Core

**Sprint Duration:** 11-17 October 2024 (7 days)
**Status:** 📋 **PLANNED**

---

## 🎯 Goal
Admin może uploadować PDFy, embeddingi w Supabase → RAG pipeline działa

## 🚀 Deliverables

### 1. Supabase Setup (Day 8-9)
- [ ] Create Supabase project
- [ ] Enable pgvector extension
- [ ] Create embeddings table with vector column
- [ ] Configure authentication & API keys
- [ ] Test connection from Django

### 2. Document Upload & Processing (Day 10-11)
- [ ] Register Document & Embedding models in admin
- [ ] Implement PDF upload via Django admin
- [ ] Extract text from PDFs (PyPDF2)
- [ ] Chunk text into manageable pieces
- [ ] Store chunks in Django database

### 3. LangChain + OpenAI Integration (Day 12-13)
- [ ] Setup OpenAI API key
- [ ] Implement RAGService.add_document()
  - Generate embeddings (OpenAI)
  - Store in Supabase pgvector
  - Link to Document model
- [ ] Implement RAGService.query()
  - Embed user question
  - Retrieve top-k chunks
  - Generate answer with GPT-4o-mini
  - Return with citations

### 4. Testing (Day 14)
- [ ] Test PDF upload flow
- [ ] Test RAG query in Django shell
- [ ] Verify embeddings in Supabase
- [ ] Test citation accuracy
- [ ] Manual testing with real legal questions

---

## 📦 Dependencies (Already Added)

```
langchain==0.3.7
langchain-openai==0.2.9
langchain-community==0.3.7
openai==1.54.4
supabase==2.10.0
pypdf2==3.0.1
python-dotenv==1.0.1
tiktoken==0.8.0
```

---

## 🗄️ Database Models (Already Created)

### Document
- title: CharField
- file: FileField (PDF)
- category: CharField
- uploaded_at: DateTimeField
- processed: BooleanField

### Embedding
- document: ForeignKey(Document)
- chunk_text: TextField
- embedding_id: CharField (Supabase vector ID)
- metadata: JSONField (page, section, etc.)
- created_at: DateTimeField

### Query
- user: ForeignKey(User)
- question: TextField
- answer: TextField
- sources: JSONField (citations)
- created_at: DateTimeField
- processing_time: FloatField

---

## 🔧 Implementation Checklist

### Environment Setup
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create .env file from .env.example
- [ ] Add OPENAI_API_KEY
- [ ] Add SUPABASE_URL
- [ ] Add SUPABASE_KEY

### Supabase Configuration
```sql
-- Enable pgvector extension
create extension if not exists vector;

-- Create embeddings table
create table embeddings (
  id bigserial primary key,
  document_id integer not null,
  chunk_text text not null,
  embedding vector(1536),  -- OpenAI ada-002 dimension
  metadata jsonb,
  created_at timestamptz default now()
);

-- Create index for fast vector search
create index on embeddings using ivfflat (embedding vector_cosine_ops);
```

### Django Admin
```python
# knowledge/admin.py
from django.contrib import admin
from .models import Document, Embedding

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'uploaded_at', 'processed']
    list_filter = ['category', 'processed']
    actions = ['process_documents']

    def process_documents(self, request, queryset):
        # Process PDFs and create embeddings
        pass
```

### RAG Service Implementation
```python
# knowledge/services.py
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client
import os

class RAGService:
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = SupabaseVectorStore(
            client=self.supabase,
            embedding=self.embeddings,
            table_name='embeddings'
        )
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def query(self, question: str, top_k: int = 5):
        # Retrieve relevant chunks
        docs = self.vectorstore.similarity_search(question, k=top_k)

        # Generate answer with LLM
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = f"Odpowiedz na pytanie bazując na kontekście:\n\n{context}\n\nPytanie: {question}"

        answer = self.llm.predict(prompt)

        return {
            'answer': answer,
            'sources': [{'text': doc.page_content, 'metadata': doc.metadata} for doc in docs]
        }
```

---

## 🧪 Testing Strategy

### Manual Tests
1. **PDF Upload:**
   - Upload sample legal PDF in admin
   - Verify file saved
   - Check Document created

2. **Processing:**
   - Run "Process Documents" action
   - Check embeddings created
   - Verify in Supabase dashboard

3. **Query:**
   - Run in Django shell:
   ```python
   from knowledge.services import RAGService
   rag = RAGService()
   result = rag.query("Czy mogę postawić szopę 3m od granicy?")
   print(result)
   ```

4. **Integration:**
   - Replace mock in accounts/views.py with RAGService
   - Test from web UI

---

## 📊 Success Metrics

- [ ] Admin can upload PDF → processed successfully
- [ ] At least 5 test documents in knowledge base
- [ ] RAG query returns answer in <10 seconds
- [ ] Citations link back to correct document pages
- [ ] Answer accuracy > 80% (manual review)

---

## ⚠️ Risks & Mitigations

**Risk:** OpenAI API costs too high
**Mitigation:** Use gpt-4o-mini (cheapest), limit chunk size, cache responses

**Risk:** Supabase free tier limits
**Mitigation:** Monitor usage, upgrade if needed ($25/month)

**Risk:** PDF parsing errors
**Mitigation:** Start with simple text PDFs, add OCR later if needed

**Risk:** Slow vector search
**Mitigation:** Use pgvector indexes, limit top-k to 5

---

## 🔜 Sprint 3 Preview

**Goal:** Connect RAG to chat UI

- Replace mock responses with RAGService
- Move query endpoint to queries app
- Add loading states for long responses
- Display citations nicely
- Save queries to database

---

**Status:** Ready to start Sprint 2!
**Prepared:** 08 October 2024
