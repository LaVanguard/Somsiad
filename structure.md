# Project Structure

## 📁 Directory Tree
Law_Advisor/
├── config/              # Django settings
│   ├── settings.py      # Main config
│   ├── urls.py          # Root URLs
│   └── wsgi.py
├── accounts/            # User auth
├── knowledge/           # RAG + documents
├── queries/             # User queries
├── templates/           # HTML templates
├── static/              # CSS, JS
├── docs/                # Documentation
└── manage.py

## 🎯 Apps

**accounts:** User authentication  
**knowledge:** Document upload, RAG, embeddings  
**queries:** User questions, AI responses, history

## 🔄 Data Flow
User → Query Form (HTMX)
↓
Backend → RAGService
↓
Supabase → Retrieve chunks
↓
OpenAI → Generate answer
↓
Response + Citations → User

## 🗄️ Models

**User:** username, email, password  
**Document:** title, file, category, processed  
**Embedding:** document, chunk_text, embedding_id  
**Query:** user, question, answer, sources

## 🔧 Key Files

- `config/settings.py` - Django config
- `requirements.txt` - Dependencies
- `.env` - Environment variables
- `PROJECT_TEMPLATE.md` - Development roadmap

**Last Updated:** 2025-10-04