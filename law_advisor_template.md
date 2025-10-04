# Law Advisor MVP - Project Template

**Target:** Certyfikat Przeprogramowani (16.11.2025)  
**Stack:** Django + HTMX + Alpine.js + LangChain + Supabase  
**Goal:** Learning Django + RAG, portfolio piece, wyróżnienie

---

## 🎯 MVP Scope (42 dni do 16.11.2025)

### Must-Have Features
- [x] User auth (register, login, logout)
- [x] RAG query interface (user asks → AI answers with citations)
- [x] Knowledge base (admin uploads PDFs → embeddings)
- [x] Query history (user sees past questions)
- [x] 1 E2E test (Playwright: user query flow)
- [x] CI/CD (GitHub Actions: tests + deploy)

### Nice-to-Have (jeśli czas po 10.11)
- [ ] Public deployment (Railway + domain)
- [ ] Response caching (same question → cached answer)
- [ ] Better UI polish (Tailwind components)

---

## 📅 Timeline (42 dni = 6 sprintów po 7 dni)

### Sprint 1 (4-10.10): Setup + Auth
**Goal:** Django project działa, auth ready  
**Deliverable:** User może się zarejestrować i zalogować

- [ ] Day 1-2: Django setup + Docker + Postgres local
- [ ] Day 3-4: Auth (django-allauth) + templates base
- [ ] Day 5-6: HTMX setup + first interactive component
- [ ] Day 7: Sprint review + deploy preview test

### Sprint 2 (11-17.10): Knowledge Base + RAG Core
**Goal:** Admin może uploadować PDFy, embeddingi w Supabase  
**Deliverable:** RAG pipeline działa (bez frontendu jeszcze)

- [ ] Day 8-9: Supabase setup + pgvector + Document model
- [ ] Day 10-11: PDF upload + parsing (PyPDF2)
- [ ] Day 12-13: LangChain + OpenAI embeddings
- [ ] Day 14: Test RAG w Django shell

### Sprint 3 (18-24.10): Query Interface
**Goal:** User może zadać pytanie i dostać odpowiedź  
**Deliverable:** Working query flow end-to-end

- [ ] Day 15-16: Query model + HTMX form
- [ ] Day 17-18: RAG service integration (LangChain)
- [ ] Day 19-20: Response display + citations formatting
- [ ] Day 21: Polish UX (loading states, errors)

### Sprint 4 (25-31.10): History + Tests
**Goal:** User widzi historię, testy działają  
**Deliverable:** Core features complete + tested

- [ ] Day 22-23: Query history view (HTMX pagination)
- [ ] Day 24-25: Pytest setup + unit tests
- [ ] Day 26-27: Playwright E2E test (full flow)
- [ ] Day 28: Fix bugs from testing

### Sprint 5 (1-7.11): CI/CD + Deploy
**Goal:** Auto-deploy działa, app live  
**Deliverable:** Public URL + green CI

- [ ] Day 29-30: GitHub Actions (tests)
- [ ] Day 31-32: Railway/Render setup + env vars
- [ ] Day 33-34: Deploy pipeline + smoke tests
- [ ] Day 35: Domain + SSL (jeśli public)

### Sprint 6 (8-14.11): Polish + Docs
**Goal:** PRD/specs complete, app polished  
**Deliverable:** Ready to submit

- [ ] Day 36-37: PRD.md + TECH_SPEC.md
- [ ] Day 38-39: UI polish + accessibility
- [ ] Day 40-41: Video demo + README
- [ ] Day 42: Submit (16.11 23:59)

---

## 🔧 Tech Setup Checklist

### Local Environment
```bash
# Prerequisites
python --version  # 3.11+
node --version    # 18+ (for Tailwind CLI)
docker --version  # 24+
git --version

# Create project
mkdir law-advisor && cd law-advisor
git init
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Django setup
pip install django djangorestframework python-decouple
django-admin startproject config .
python manage.py startapp accounts
python manage.py startapp knowledge
python manage.py startapp queries

# Docker Postgres
# Create docker-compose.yml (see below)
docker-compose up -d
```

### Key Files Setup

**docker-compose.yml**
```yaml
version: '3.9'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: law_advisor
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**requirements/base.txt**
```
Django>=5.0
djangorestframework>=3.14
django-allauth>=0.57
python-decouple>=3.8
psycopg2-binary>=2.9
langchain>=0.1
langchain-openai>=0.0.5
supabase>=2.0
pypdf2>=3.0
openai>=1.0
python-dotenv>=1.0
```

**requirements/local.txt**
```
-r base.txt
pytest>=7.4
pytest-django>=4.5
playwright>=1.40
ipython>=8.17
django-debug-toolbar>=4.2
```

**.env.example**
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/law_advisor

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-key-here

# OpenAI
OPENAI_API_KEY=sk-xxx

# Optional
ENVIRONMENT=local
```

---

## 📊 Data Models

### accounts/models.py
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user - extend later if needed"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
```

### knowledge/models.py
```python
from django.db import models
from django.contrib.postgres.fields import ArrayField

class Document(models.Model):
    """Legal document (PDF) uploaded by admin"""
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    category = models.CharField(max_length=100)  # e.g. "garden", "electrical"
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'documents'
        ordering = ['-uploaded_at']

class Embedding(models.Model):
    """Vector embedding for RAG retrieval"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    chunk_text = models.TextField()  # Original text chunk
    embedding_id = models.CharField(max_length=100)  # Supabase vector ID
    metadata = models.JSONField(default=dict)  # Page number, section, etc.
    
    class Meta:
        db_table = 'embeddings'
```

### queries/models.py
```python
from django.db import models
from apps.accounts.models import User

class Query(models.Model):
    """User query with RAG response"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True)
    sources = models.JSONField(default=list)  # Citations from RAG
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(null=True)  # seconds
    
    class Meta:
        db_table = 'queries'
        ordering = ['-created_at']
```

---

## 🧠 RAG Architecture

### knowledge/services.py (core RAG logic)
```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from supabase import create_client
import os

class RAGService:
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.vectorstore = SupabaseVectorStore(
            client=self.supabase,
            embedding=self.embeddings,
            table_name='embeddings',
            query_name='match_embeddings'
        )
    
    def query(self, question: str, top_k: int = 5):
        """Query RAG system with citations"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": top_k}),
            return_source_documents=True
        )
        
        result = qa_chain({"query": question})
        
        return {
            'answer': result['result'],
            'sources': [
                {
                    'text': doc.page_content,
                    'metadata': doc.metadata
                }
                for doc in result['source_documents']
            ]
        }
    
    def add_document(self, document_id: int, chunks: list[dict]):
        """Add document chunks to vector store"""
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        self.vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas
        )
```

### knowledge/admin.py (PDF upload + processing)
```python
from django.contrib import admin
from .models import Document
from .services import RAGService
import PyPDF2

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'uploaded_at', 'processed']
    actions = ['process_documents']
    
    def process_documents(self, request, queryset):
        """Process PDFs and create embeddings"""
        rag = RAGService()
        
        for doc in queryset.filter(processed=False):
            # Extract text from PDF
            pdf = PyPDF2.PdfReader(doc.file.path)
            chunks = []
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                # Simple chunking (improve with LangChain splitters)
                chunk_size = 1000
                for i in range(0, len(text), chunk_size):
                    chunks.append({
                        'text': text[i:i+chunk_size],
                        'metadata': {
                            'document_id': doc.id,
                            'page': page_num + 1,
                            'title': doc.title
                        }
                    })
            
            # Add to vector store
            rag.add_document(doc.id, chunks)
            doc.processed = True
            doc.save()
        
        self.message_user(request, f"Processed {queryset.count()} documents")
```

---

## 🎨 Frontend (HTMX + Alpine)

### templates/base.html
```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Law Advisor{% endblock %}</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    
    <!-- Alpine.js -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex">
                    <a href="/" class="flex items-center">
                        <span class="text-xl font-bold">Law Advisor</span>
                    </a>
                </div>
                <div class="flex items-center">
                    {% if user.is_authenticated %}
                        <a href="{% url 'queries:history' %}" class="px-3 py-2">Historia</a>
                        <a href="{% url 'account_logout' %}" class="px-3 py-2">Wyloguj</a>
                    {% else %}
                        <a href="{% url 'account_login' %}" class="px-3 py-2">Zaloguj</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>
    
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### templates/queries/query_form.html
```html
{% extends 'base.html' %}

{% block content %}
<div class="max-w-3xl mx-auto" x-data="{ loading: false }">
    <h1 class="text-3xl font-bold mb-6">Zadaj pytanie o przepisy</h1>
    
    <form 
        hx-post="{% url 'queries:ask' %}" 
        hx-target="#response"
        hx-indicator="#spinner"
        @htmx:before-request="loading = true"
        @htmx:after-request="loading = false"
        class="mb-8"
    >
        {% csrf_token %}
        <textarea 
            name="question" 
            rows="4" 
            class="w-full border rounded-lg p-3"
            placeholder="Np. Czy mogę postawić szopę 3m od granicy działki?"
            required
        ></textarea>
        <button 
            type="submit" 
            class="mt-3 bg-blue-600 text-white px-6 py-2 rounded-lg"
            :disabled="loading"
        >
            <span x-show="!loading">Zapytaj AI</span>
            <span x-show="loading" id="spinner">Szukam odpowiedzi...</span>
        </button>
    </form>
    
    <div id="response" class="bg-white rounded-lg shadow p-6">
        <!-- HTMX will replace this -->
    </div>
</div>
{% endblock %}
```

### templates/queries/response_partial.html (HTMX partial)
```html
<div class="space-y-4">
    <h2 class="text-xl font-semibold">Odpowiedź:</h2>
    <div class="prose max-w-none">
        {{ answer|linebreaks }}
    </div>
    
    {% if sources %}
    <div class="mt-6 border-t pt-4">
        <h3 class="font-semibold mb-2">Źródła:</h3>
        <ul class="space-y-2">
            {% for source in sources %}
            <li class="text-sm bg-gray-50 p-3 rounded">
                <p class="text-gray-700">{{ source.text|truncatewords:50 }}</p>
                <p class="text-xs text-gray-500 mt-1">
                    Źródło: {{ source.metadata.title }} (str. {{ source.metadata.page }})
                </p>
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
</div>
```

### queries/views.py
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Query
from apps.knowledge.services import RAGService
import time

@login_required
def query_form(request):
    return render(request, 'queries/query_form.html')

@login_required
@require_http_methods(["POST"])
def ask_question(request):
    question = request.POST.get('question')
    
    # Track processing time
    start = time.time()
    
    # Query RAG
    rag = RAGService()
    result = rag.query(question)
    
    processing_time = time.time() - start
    
    # Save to DB
    query = Query.objects.create(
        user=request.user,
        question=question,
        answer=result['answer'],
        sources=result['sources'],
        processing_time=processing_time
    )
    
    # Return HTMX partial
    return render(request, 'queries/response_partial.html', {
        'answer': result['answer'],
        'sources': result['sources']
    })

@login_required
def query_history(request):
    queries = Query.objects.filter(user=request.user)[:20]
    return render(request, 'queries/history.html', {'queries': queries})
```

---

## 🧪 Testing Strategy

### tests/test_rag.py (Pytest)
```python
import pytest
from apps.knowledge.services import RAGService

@pytest.mark.django_db
def test_rag_query():
    rag = RAGService()
    result = rag.query("Jakie są wymagania dla ogrodzenia?")
    
    assert 'answer' in result
    assert 'sources' in result
    assert len(result['sources']) > 0
```

### tests/test_e2e.py (Playwright)
```python
from playwright.sync_api import Page, expect

def test_user_query_flow(page: Page):
    # Login
    page.goto("http://localhost:8000/accounts/login/")
    page.fill('input[name="username"]', 'testuser')
    page.fill('input[name="password"]', 'testpass123')
    page.click('button[type="submit"]')
    
    # Ask question
    page.goto("http://localhost:8000/")
    page.fill('textarea[name="question"]', 'Czy mogę postawić szopę 3m od granicy?')
    page.click('button[type="submit"]')
    
    # Wait for response
    page.wait_for_selector('#response', state='visible', timeout=10000)
    
    # Verify answer appeared
    expect(page.locator('#response')).to_contain_text('Odpowiedź')
```

---

## 🚀 Deployment

### .github/workflows/ci.yml
```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements/local.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
          SECRET_KEY: test-secret-key
        run: |
          pytest
      
      - name: Run E2E tests
        run: |
          python manage.py runserver &
          playwright install
          pytest tests/test_e2e.py

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy to Railway
        # Railway CLI deployment
        run: echo "Deploy step here"
```

### Railway deployment
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

---

## 📋 Daily Workflow (jak pracować z tym templatem)

### Morning (9:00, 5 min)
1. Otwórz ten template
2. Znajdź dzisiejszy sprint + day
3. Check co do zrobienia (3-4 taski max)
4. Plan: kiedy focus block? (np. 10:00-12:00)

### Coding (focus block)
1. Cursor AI: otwórz codebase
2. Claude Code: dla większych tasków
3. **Output-first**: zrób → test → commit → note (max 10 linijek)
4. Stuck >30 min? → ping Focus Coach

### Evening (22:00, 10 min)
1. Update checklist (✅ done tasks)
2. Commit + push
3. Note: co zrobiłeś (output, nie input)
4. Plan jutro: next 3 taski

### Weekend Review (sobota, 20 min)
1. Sprint recap: co done, co blocked
2. Update timeline jeśli opóźnienia
3. Adjust scope jeśli trzeba (lepiej mniejszy MVP działający niż wielki stuck)

---

## ⚠️ Red Flags & Pivots

**Jeśli którykolwiek sprint przekracza 7 dni:**
→ CUT SCOPE. Lepiej mniejszy MVP na czas niż ambitny spóźniony.

**Jeśli stuck >2 dni na tym samym:**
→ PIVOT lub ASK. Discord przeprogramowani / Focus Coach / Claude.

**Jeśli <3h coding dziennie przez 3 dni:**
→ RESET. Deep dive session: co blokuje?

**Jeśli 01.11 a backend nie działa:**
→ EMERGENCY. Skip polish, focus tylko core (auth + RAG + 1 test).

---

## 📚 Docs Required (moduł 2-3)

### PRD.md (Product Requirements Doc)
```markdown
# Law Advisor - Product Requirements

## Problem
Właściciele domów nie wiedzą jakie przepisy ich dotyczą (ogród, budowa, ubezpieczenia).

## Solution
AI advisor z RAG → user pyta, AI odpowiada z cytatami z przepisów.

## Target Users
- Właściciele domów jednorodzinnych
- Zarządcy nieruchomości
- Osoby planujące budowę/remont

## MVP Features
[List from above]

## Success Metrics
- User może zadać pytanie i dostać answer <10s
- Citations accuracy >80%
- User retention: 3+ queries per user
```

### TECH_SPEC.md
```markdown
# Technical Specification

## Architecture
Django + HTMX + LangChain + Supabase pgvector

## Data Flow
1. User submits question (HTMX POST)
2. Backend queries RAG (LangChain)
3. RAG retrieves top-k chunks (Supabase)
4. LLM generates answer (OpenAI)
5. HTMX updates UI with response + citations

## Models
[See Data Models section above]

## API Endpoints
- POST /queries/ask/ → Submit question
- GET /queries/history/ → View past queries

## External Services
- OpenAI API (embeddings + chat)
- Supabase (vector storage + Postgres)
```

---

## 🎯 Success Criteria (16.11 submission)

**Must have to pass:**
- ✅ Auth works (login/register)
- ✅ User can ask question → get AI answer
- ✅ Admin can upload PDFs → embeddings created
- ✅ User sees query history
- ✅ 1 E2E test passes
- ✅ CI runs on push
- ✅ PRD + TECH_SPEC complete

**Nice to have for wyróżnienie:**
- ⭐ Public URL live
- ⭐ Clean UI (Tailwind polished)
- ⭐ Fast responses (<5s)
- ⭐ Good documentation (README with demo)

---

## 💡 Pro Tips

1. **Start with Django admin** - najszybszy sposób na upload PDFów (no custom UI needed v1)
2. **Use gpt-4o-mini** - 10x cheaper niż gpt-4, wystarczająco dobry dla RAG
3. **Simple chunking first** - 1000 chars per chunk, improve later
4. **HTMX over React** - 0 build step, instant feedback, prosty debug
5. **PostgreSQL local** - same DB dev/prod, łatwiejszy debug
6. **Railway free tier** - $5 credit, wystarczy na MVP
7. **Playwright for E2E** - jeden test wystarczy, full user flow

---

## 🔗 Resources

**Django:**
- https://docs.djangoproject.com/en/5.0/
- https://django-allauth.readthedocs.io/

**HTMX:**
- https://htmx.org/docs/
- https://htmx.org/examples/

**LangChain:**
- https://python.langchain.com/docs/get_started/introduction
- https://python.langchain.com/docs/use_cases/question_answering/

**Supabase:**
- https://supabase.com/docs/guides/ai/quickstarts/generate-text-embeddings
- https://supabase.com/docs/guides/database/extensions/pgvector

**Playwright:**
- https://playwright.dev/python/docs/intro

---

## ✅ Next Steps

1. **Copy this template** to your repo: `docs/PROJECT_TEMPLATE.md`
2. **Setup project** (Sprint 1 Day 1-2)
3. **Daily check-ins** with Focus Coach (morning + evening)
4. **Weekly reviews** (each Saturday)
5. **Ship on 16.11** 🚀

**Let's build this. Output > input. Done > perfect.**
