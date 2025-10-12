# Somsiad 🐵⚖️

**AI-powered legal advisor dla właścicieli domów jednorodzinnych.**
*Working meme app - bo każdy zasługuje na doradcę prawnego z poczuciem humoru!*

## 🎯 Problem
Właściciele domów nie wiedzą jakie przepisy ich dotyczą (budowa, ogród, przeglądy). Somsiad pomaga odpowiedzieć na pytania prawne... i zgłosić sąsiada do prokuratury (dla żartów oczywiście 😄).

## ✨ Features

### ✅ Sprint 1 Complete (4-10.10.2024)
- 🔐 **Authentykacja** - Django-allauth (email-based login)
- 💬 **Chat Interface** - Minimalistyczny UI w stylu Claude/Gemini
- 🖼️ **Image Upload** - Dodaj zdjęcia do pytań
- ⚡ **HTMX-powered** - Real-time messaging bez przeładowania strony
- 😂 **Joke Action Buttons**:
  - Zgłoś do Prokuratury
  - Wyślij anonimowy donos do gminy
  - Zadzwoń po Straż Miejską

### ✅ Sprint 2 Complete (11-17.10.2024) - ADVANCED RAG
- 🧠 **Production RAG System** - LangChain + OpenAI GPT-4o-mini
- 📚 **Smart Document Processing**:
  - Semantic chunking by legal structure (articles, sections)
  - Document summarization (executive summaries + key topics)
  - Metadata enrichment (article refs, measurements, obligations)
- 🔍 **Intelligent Preprocessing** - Removes administrative noise (9% reduction)
- 💾 **Vector Storage** - Supabase pgvector with hierarchical retrieval
- 📊 **Rich Metadata** - Auto-extracts legal references and context

### ✅ Sprint 3 In Progress (18-24.10.2024) - CONVERSATIONS & STREAMING
- 💬 **Conversation Management**:
  - User-specific conversation tracking
  - Conversation history with timestamps
  - Auto-titled conversations from first question
  - Sidebar with conversation grouping (Today/Yesterday/Older)
- 🌊 **Real-time Streaming Responses**:
  - Server-Sent Events (SSE) for live AI responses
  - Word-by-word streaming like ChatGPT
  - Typing indicator during generation
  - Real-time source citation display
- ⌨️ **Enhanced UX**:
  - Enter to send, Shift+Enter for new line
  - Cleaner interface (removed stale hints)
  - Responsive message bubbles
- 📂 **Document Management UI**:
  - HTMX-powered document upload
  - Real-time processing status
  - Global document visibility (shared across users)

## 🛠️ Tech Stack

**Backend:**
- Django 5.2.7
- Django-allauth 65.11.2
- Django REST Framework 3.16.1
- Python 3.11+

**Frontend:**
- HTMX 1.9.10 (interactive components)
- Alpine.js 3.x (reactive UI)
- Tailwind CSS (styling)
- Inter font (typography)

**Database:**
- SQLite (development)
- Supabase Postgres + pgvector (production)

**AI/RAG Stack (Sprint 2):**
- LangChain 0.3.7 (RAG orchestration)
- OpenAI GPT-4o-mini (LLM generation)
- text-embedding-3-small (embeddings - 1536D)
- Supabase pgvector (vector storage)
- PyPDF2 3.0.1 (PDF processing)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git

### Installation

```bash
# Clone repo
git clone https://github.com/LaVanguard/Law_Advisor.git
cd Law_Advisor

# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (for admin panel)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Access the app
- **Home (Chat):** http://127.0.0.1:8000/
- **Login:** http://127.0.0.1:8000/accounts/login/
- **Admin:** http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
Law_Advisor/
├── accounts/           # User authentication
├── knowledge/          # RAG + document storage
│   ├── models.py       # Document, Embedding models
│   ├── admin.py        # Django admin interfaces
│   └── services/       # Advanced RAG services
│       ├── preprocessor.py         # Text cleaning
│       ├── semantic_chunker.py     # Smart chunking
│       ├── summarizer.py           # Document summaries
│       ├── rag_service.py          # RAG orchestration
│       └── document_processor.py   # Main pipeline
├── queries/            # User queries & conversation history
│   ├── models.py       # Query, Conversation models
│   ├── views.py        # Conversation management endpoints
│   └── migrations/     # Database migrations
├── config/             # Django settings
├── legal_documents/    # Source PDFs (gitignored)
│   ├── raw/            # Original PDFs by category
│   │   ├── budowa/     # Construction law
│   │   ├── ochrona_przyrody/  # Nature protection
│   │   └── przeglady/  # Inspections
│   └── README.md       # Document catalog
├── templates/          # HTML templates
│   ├── account/        # Login, signup, password reset
│   ├── partials/       # HTMX components
│   │   ├── message.html             # Chat message bubble
│   │   ├── conversations_list.html  # Conversation sidebar
│   │   ├── conversation_messages.html  # Message history
│   │   ├── processed_documents.html    # Document list
│   │   └── unprocessed_documents.html  # Pending documents
│   ├── base.html       # Base template
│   └── home.html       # Main chat interface with streaming
├── static/             # Static files (CSS, JS, images)
├── docs/               # Project documentation
│   ├── ADVANCED_RAG.md        # RAG system guide
│   ├── API_KEYS_SETUP.md      # API keys configuration
│   ├── SUPABASE_SETUP.md      # Database setup
│   └── SPRINT2_QUICKSTART.md  # Quick start guide
├── manage.py
├── requirements.txt
└── README.md
```

## 🎨 UI Design

**Brand:** Somsiad (intentional typo - "Sąsiad" = neighbor)
**Style:** Professional grey minimalism (Claude/Gemini inspired)
**Font:** Inter (modern, clean)
**Colors:**
- Background: `#F8F9FA`
- Cards: `#FFFFFF`
- Text: `#1F2937`
- Accent: `#6B7280`

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.
```

## 📅 Development Timeline

**Project duration:** 42 days (04.10.2024 - 16.11.2025)
**Certification goal:** Przeprogramowani 10xDevs

### Sprint Progress
- ✅ **Sprint 1** (4-10.10): Setup + Auth + UI
- ✅ **Sprint 2** (11-17.10): Advanced RAG System (semantic chunking, summaries, preprocessing)
- ⏳ **Sprint 3** (18-24.10): Conversations + Streaming + Document Management
- 📋 **Sprint 4** (25-31.10): Multi-Query RAG + Hybrid Search
- 📋 **Sprint 5** (1-7.11): CI/CD + Deploy
- 📋 **Sprint 6** (8-14.11): Polish + Docs

## 🎓 Learning Goals

- Master Django + HTMX stack
- Implement production RAG system
- Deploy full-stack AI app
- Build portfolio-worthy project

## 📝 Notes

- **Somsiad typo is intentional** - never change it! 😄
- **Advanced RAG system** - Production-quality semantic chunking & summarization
- Action buttons are jokes but fully functional
- See `docs/ADVANCED_RAG.md` for detailed RAG documentation
- See `docs/SPRINT2_QUICKSTART.md` for setup & testing guide

## 📚 Documentation

- **[ADVANCED_RAG.md](docs/ADVANCED_RAG.md)** - Complete RAG system architecture
- **[API_KEYS_SETUP.md](docs/API_KEYS_SETUP.md)** - OpenAI & Supabase configuration
- **[SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md)** - Vector database setup
- **[SPRINT2_QUICKSTART.md](docs/SPRINT2_QUICKSTART.md)** - Quick start guide

## 🤝 Contributing

This is a learning project for Przeprogramowani 10xDevs certification. Feedback welcome!

## 📄 License

Educational project - built for learning purposes.

---

**Author:** Mike @LaVanguard
**Course:** Przeprogramowani 10xDevs (Oct-Nov 2024)
**Built with:** ❤️ and Claude Code
