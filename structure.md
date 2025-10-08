# Project Structure

## 📁 Directory Tree
```
Law_Advisor/
├── config/              # Django settings
│   ├── settings.py      # Main config (allauth, static files)
│   ├── urls.py          # Root URLs (admin, accounts, api)
│   └── wsgi.py
├── accounts/            # User authentication
│   ├── views.py         # home view + query_api endpoint
│   └── models.py        # Custom user (future)
├── knowledge/           # RAG + documents (Sprint 2)
│   └── services.py      # RAG service (future)
├── queries/             # User queries (Sprint 2)
│   └── models.py        # Query history
├── templates/           # HTML templates
│   ├── account/         # Django-allauth overrides
│   │   ├── login.html   # Custom login page (Somsiad branding)
│   │   └── password_reset.html
│   ├── partials/        # HTMX components
│   │   └── message.html # Chat message bubbles (user + AI)
│   ├── base.html        # Base template (HTMX, Alpine, Tailwind)
│   └── home.html        # Main chat interface
├── static/              # Static files
│   └── images/          # Logo & assets
│       └── logo.png     # Somsiad monkey logo
├── logo/                # Original logo files
│   └── Logo_Law_Advisor.png
├── .gitignore           # Git ignore rules
├── .env.example         # Environment variables template
├── manage.py
├── requirements.txt
└── README.md
```

## 🎯 Apps

**accounts:** User authentication (django-allauth)
- Login, signup, password reset
- Mock query API endpoint (will move to queries in Sprint 2)

**knowledge:** Document upload, RAG, embeddings (Sprint 2)
- PDF processing
- Vector embeddings (Supabase)
- RAG service (LangChain)

**queries:** User questions, AI responses, history (Sprint 2)
- Query model
- Response storage
- Citations

## 🔄 Data Flow (Current - Sprint 1)

```
User → Login (allauth) → Home page (chat UI)
↓
User types question + optional image
↓
HTMX POST → /api/query/
↓
accounts/views.py → query_api()
↓
Mock response generated
↓
templates/partials/message.html rendered
↓
HTMX swaps response into chat
```

## 🔄 Data Flow (Future - Sprint 2)

```
User → Query Form (HTMX)
↓
Backend → RAGService (knowledge/services.py)
↓
Supabase → Retrieve top-k chunks (pgvector)
↓
OpenAI → Generate answer with citations
↓
Response + Citations → User (HTMX partial)
```

## 🗄️ Models

**User:** Built-in Django auth (future: custom fields)
- email (login method)
- password

**Document:** (Sprint 2)
- title, file, category, processed
- Admin uploads PDFs

**Embedding:** (Sprint 2)
- document FK, chunk_text, embedding_id
- Supabase vector storage

**Query:** (Sprint 2)
- user FK, question, answer, sources
- Chat history

## 🔧 Key Files

### Configuration
- `config/settings.py` - Django config (apps, allauth, static files)
- `config/urls.py` - URL routing (admin, accounts, api)
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules

### Templates
- `templates/base.html` - Base with HTMX, Alpine.js, Tailwind
- `templates/home.html` - Chat interface (main page)
- `templates/account/login.html` - Custom login (Somsiad branding)
- `templates/partials/message.html` - Chat bubbles (user + AI + action buttons)

### Views
- `accounts/views.py` - Home view + mock query API

### Static
- `static/images/logo.png` - Somsiad logo

## 🎨 UI Components

### Chat Interface (home.html)
- **Top nav:** Hamburger menu | Somsiad logo | User avatar
- **Main area:** Welcome message → Chat messages
- **Bottom input:** Image upload button | Text input | Send button
- **Features:** HTMX real-time updates, Alpine.js reactivity

### Message Bubbles (partials/message.html)
- **User message:** Dark grey bubble (right), optional image
- **AI response:** Light grey bubble (left) with Somsiad logo
- **Action buttons:** 3 joke buttons below AI response
  - Zgłoś do Prokuratury
  - Wyślij anonimowy donos
  - Zadzwoń po Straż Miejską

## 📦 Dependencies (requirements.txt)

**Current (Sprint 1):**
- Django 5.2.7
- django-allauth 65.11.2
- djangorestframework 3.16.1
- pytest + pytest-django (testing)

**Future (Sprint 2):**
- langchain
- langchain-openai
- openai
- supabase

## 🚀 Sprint Progress

**Sprint 1 (DONE):**
- ✅ Django setup
- ✅ Auth (django-allauth)
- ✅ Chat UI (HTMX + Alpine + Tailwind)
- ✅ Image upload
- ✅ Mock API
- ✅ Joke action buttons

**Sprint 2 (Next):**
- 📋 Supabase setup
- 📋 RAG service (LangChain)
- 📋 PDF upload & processing
- 📋 Real LLM integration

---

**Last Updated:** 2024-10-08 (Sprint 1 Complete)
