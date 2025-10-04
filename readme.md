markdown# Law Advisor 🏠⚖️

AI-powered legal advisor dla właścicieli domów jednorodzinnych.

## 🎯 Problem
Właściciele domów nie wiedzą jakie przepisy ich dotyczą (budowa, ogród, przeglądy).

## 🛠️ Tech Stack
- Django 5.x + Django REST Framework
- LangChain + OpenAI (RAG)
- Supabase pgvector
- HTMX + Alpine.js + Tailwind

## 📊 Status
✅ Django setup + admin
⏸️ Auth (starting 05.10)
⏸️ RAG core (week 2)
⏸️ Query interface (week 3)

**Target:** 16.11.2025 - Certyfikat Przeprogramowani

## 🚀 Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
📁 Structure
Law_Advisor/
├── config/         # Django settings
├── accounts/       # Auth
├── knowledge/      # RAG + documents
├── queries/        # User queries
└── docs/           # Documentation
🎓 Context
Built for Przeprogramowani AI_devs certification (04.10 - 16.11.2025).
Author: Mike @LaVanguard