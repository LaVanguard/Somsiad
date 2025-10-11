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

### 🔜 Coming in Sprint 2 (11-17.10.2024)
- 🧠 RAG integration (LangChain + OpenAI)
- 📚 Knowledge base (PDF upload & embeddings)
- 🔍 Real legal advice (zamiast mocków)
- 💾 Supabase pgvector storage

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
- Supabase Postgres + pgvector (production - Sprint 2)

**Future integrations:**
- LangChain (RAG orchestration)
- OpenAI GPT-4o-mini (LLM)
- Supabase (vector storage)

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
├── knowledge/          # RAG + document storage (Sprint 2)
├── queries/            # User queries & history (Sprint 2)
├── config/             # Django settings
├── templates/          # HTML templates
│   ├── account/        # Login, signup, password reset
│   ├── partials/       # HTMX message components
│   ├── base.html       # Base template
│   └── home.html       # Main chat interface
├── static/             # Static files (CSS, JS, images)
│   └── images/         # Logo & assets
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
- ⏳ **Sprint 2** (11-17.10): Knowledge Base + RAG Core
- 📋 **Sprint 3** (18-24.10): Query Interface
- 📋 **Sprint 4** (25-31.10): History + Tests
- 📋 **Sprint 5** (1-7.11): CI/CD + Deploy
- 📋 **Sprint 6** (8-14.11): Polish + Docs

## 🎓 Learning Goals

- Master Django + HTMX stack
- Implement production RAG system
- Deploy full-stack AI app
- Build portfolio-worthy project

## 📝 Notes

- **Somsiad typo is intentional** - never change it! 😄
- Mock responses currently - real LLM in Sprint 2
- Action buttons are jokes but fully functional
- Ready for Supabase + OpenAI integration

## 🤝 Contributing

This is a learning project for Przeprogramowani 10xDevs certification. Feedback welcome!

## 📄 License

Educational project - built for learning purposes.

---

**Author:** Mike @LaVanguard
**Course:** Przeprogramowani 10xDevs (Oct-Nov 2024)
**Built with:** ❤️ and Claude Code
