# API Keys Setup Guide

## Required API Keys for RAG System

Somsiad needs 2 API services to function:

1. **OpenAI** - For embeddings and LLM (GPT-4o-mini)
2. **Supabase** - For vector storage (PostgreSQL + pgvector)

---

## 1. OpenAI API Key

### Step-by-Step

1. **Go to OpenAI Platform**
   - Visit: [platform.openai.com](https://platform.openai.com)
   - Sign up or log in

2. **Create API Key**
   - Click your profile icon (top-right)
   - Select "API keys"
   - Click "Create new secret key"
   - Name it: `Law_Advisor` (optional)
   - Copy the key immediately (you won't see it again!)
   - Format: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

3. **Add Credit (if needed)**
   - Go to "Settings" → "Billing"
   - Add $5-10 for testing (more than enough!)
   - OpenAI requires payment method for API access

4. **Add to .env**
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

### Cost Breakdown

| Service | Model | Cost | Usage Estimate |
|---------|-------|------|----------------|
| Embeddings | text-embedding-3-small | $0.02 / 1M tokens | ~$0.10 for 1000 documents |
| LLM | GPT-4o-mini | $0.15 / 1M input tokens | ~$0.50 for 100 queries |
| LLM | GPT-4o-mini | $0.60 / 1M output tokens | ~$1.00 for 100 queries |

**Total for testing:** $5-10/month (very affordable!)

### Usage Monitoring

- Go to "Usage" in OpenAI dashboard
- Set spending limits to avoid surprises
- Recommended limit: $10/month for development

---

## 2. Supabase Keys

### Step-by-Step

1. **Create Supabase Account**
   - Visit: [supabase.com](https://supabase.com)
   - Sign up (GitHub auth works well)

2. **Create New Project**
   - Click "New Project"
   - Fill in:
     - **Name:** `Law_Advisor_RAG` (or your choice)
     - **Database Password:** Use strong password (SAVE THIS!)
     - **Region:** Choose closest to you
     - **Plan:** Free (plenty for development)
   - Click "Create new project"
   - Wait ~2 minutes for provisioning

3. **Enable pgvector Extension**
   - Go to **Database → Extensions** (left sidebar)
   - Search for "vector"
   - Enable **pgvector** extension
   - Confirm

4. **Create Embeddings Table**
   - Go to **SQL Editor** (left sidebar)
   - Copy SQL from `docs/SUPABASE_SETUP.md` section 3
   - Click "Run" (bottom-right)
   - You should see "Success. No rows returned"

5. **Create Search Function**
   - Still in SQL Editor
   - Copy SQL from `docs/SUPABASE_SETUP.md` section 4
   - Click "Run"
   - Should see success message

6. **Get API Keys**
   - Go to **Settings → API** (left sidebar)
   - Copy these values:
     - **Project URL:** `https://xxxxx.supabase.co`
     - **anon public key:** Long string starting with `eyJ...`
   - **DO NOT use service_role key** (it's too powerful for .env)

7. **Add to .env**
   ```env
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-key-here
   ```

### Free Tier Limits

- **Database:** 500 MB (enough for ~83,000 embeddings!)
- **Bandwidth:** 5 GB/month
- **API Requests:** Unlimited (with rate limits)
- **Perfect for development!**

---

## 3. Update Your .env File

Open `.env` in project root (create from `.env.example` if needed):

```env
# Django Configuration
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI API
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Supabase (for pgvector embeddings)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxx

# Environment
ENVIRONMENT=local
```

**IMPORTANT:** Never commit `.env` to git! (It's in `.gitignore`)

---

## 4. Verify Setup

Run this Python script to test connections:

```bash
python -c "
from decouple import config
print('✅ OpenAI Key:', 'Set' if config('OPENAI_API_KEY', default='') else '❌ Missing')
print('✅ Supabase URL:', 'Set' if config('SUPABASE_URL', default='') else '❌ Missing')
print('✅ Supabase Key:', 'Set' if config('SUPABASE_KEY', default='') else '❌ Missing')
"
```

Should see:
```
✅ OpenAI Key: Set
✅ Supabase URL: Set
✅ Supabase Key: Set
```

---

## 5. Test RAG System

Once keys are configured:

### A. Process Sample Documents

```bash
# Upload a PDF via Django admin
python manage.py runserver
# Go to: http://127.0.0.1:8000/admin/knowledge/document/
# Add a legal document PDF

# Process it
python manage.py process_documents --all
```

### B. Test Query

```bash
# Start server
python manage.py runserver

# Go to: http://127.0.0.1:8000/
# Login
# Ask a legal question
# Should see RAG-powered response with sources!
```

---

## Troubleshooting

### Error: "OpenAI API key not found"
- Check `.env` file has `OPENAI_API_KEY=sk-proj-...`
- Restart Django server after editing .env
- Verify key is valid at platform.openai.com

### Error: "Supabase connection failed"
- Check `SUPABASE_URL` is correct (no trailing slash)
- Check `SUPABASE_KEY` is the **anon** key (not service_role)
- Verify pgvector extension is enabled
- Check project is not paused (free tier auto-pauses after inactivity)

### Error: "match_embeddings function does not exist"
- Run the SQL from `docs/SUPABASE_SETUP.md` section 4
- Check you're using the correct Supabase project

### Error: "No documents found for retrieval"
- Upload documents via Django admin first
- Run `python manage.py process_documents --all`
- Check documents are marked as `processed=True` in admin

---

## Security Best Practices

### Development
- ✅ Use `.env` for secrets
- ✅ Never commit `.env` to git
- ✅ Use Supabase anon key (not service_role)
- ✅ Set OpenAI spending limits

### Production (later)
- Use environment variables (not .env file)
- Rotate keys regularly
- Enable Supabase RLS (Row Level Security)
- Use separate keys for prod/dev
- Monitor usage and set alerts

---

## Cost Summary

### Monthly Estimates (Development)

| Service | Free Tier | Paid Usage | Est. Cost |
|---------|-----------|------------|-----------|
| Supabase | 500 MB DB, 5 GB bandwidth | N/A | $0 |
| OpenAI Embeddings | N/A | 1000 docs × 500 tokens | $0.10 |
| OpenAI GPT-4o-mini | N/A | 100 queries | $1.50 |
| **Total** | | | **~$2-5/month** |

**Very affordable for a production RAG system!** 🎉

---

## Next Steps

After setting up API keys:

1. ✅ Verify keys with test script
2. 📄 Upload sample legal documents (PDF)
3. ⚙️ Process documents: `python manage.py process_documents --all`
4. 💬 Test chat interface
5. 🎯 Review responses and tune system

---

**Last Updated:** 11.10.2024
**Author:** Mike @LaVanguard
