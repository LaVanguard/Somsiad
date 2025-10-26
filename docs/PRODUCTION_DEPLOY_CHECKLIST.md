# Production Deployment Checklist - Somsiad (Secured)

**Date:** 2025-10-26
**Security Level:** HIGH (Private app, no public signup)
**Platform:** Railway

---

## ✅ Security Measures Implemented

### 1. **Public Signup DISABLED**
- ✅ Custom `NoSignupAccountAdapter` blocks all signups
- ✅ `/accounts/signup/` returns 403 Forbidden
- ✅ Users can ONLY be created via Django admin by superuser
- ✅ Prevents: bot registrations, spam accounts, unauthorized access

### 2. **Rate Limiting Implemented**
- ✅ **RAG API:** 20 queries/minute per user or IP (protects OpenAI costs)
- ✅ **Document Upload:** 5 uploads/10 minutes per user
- ✅ **Document Processing:** 10 processes/10 minutes per user
- ✅ All rate limits logged to `logs/django.log`

### 3. **Production Security Headers**
- ✅ HTTPS redirect (SECURE_SSL_REDIRECT=True)
- ✅ HSTS enabled (1 year, includeSubDomains, preload)
- ✅ Secure cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- ✅ Content security (X-Frame-Options: DENY, nosniff)

---

## 🔑 Environment Variables for Railway

Copy these to Railway dashboard → Variables:

```bash
# Environment
ENVIRONMENT=production

# Django Security
SECRET_KEY=mkoceau*-=)10pu*l1r5@a%n!7xg4i28cv3#xq9gp4=!whbf#c
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app

# OpenAI (REQUIRED)
OPENAI_API_KEY=sk-your-key-here

# Supabase Vector DB (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Railway PostgreSQL (auto-provided, verify it exists)
# DATABASE_URL=postgresql://... (Railway adds this automatically)

# Email (OPTIONAL)
ADMIN_EMAIL=your-email@example.com
SERVER_EMAIL=noreply@somsiad.pl
```

---

## 📋 Deployment Steps (Railway)

### Step 1: Push code to GitHub

```bash
git add .
git commit -m "Production deployment: security hardening + signup disabled"
git push origin feature/sprint2-rag-core
```

### Step 2: Connect Railway to GitHub

1. Go to [Railway.app](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `Law_Advisor` repository
4. Select branch: `feature/sprint2-rag-core` (or `main` after merge)

### Step 3: Add PostgreSQL Database

1. In Railway project → Click "+ New" → "Database" → "PostgreSQL"
2. Railway auto-generates `DATABASE_URL` environment variable
3. Verify it appears in "Variables" tab

### Step 4: Configure Environment Variables

1. Click on your Django service → "Variables" tab
2. Add ALL variables from section above (🔑)
3. **CRITICAL:** Replace placeholders:
   - `OPENAI_API_KEY` → your actual OpenAI key
   - `SUPABASE_URL` → your Supabase project URL
   - `SUPABASE_KEY` → your Supabase anon key
   - `ALLOWED_HOSTS` → your Railway domain (e.g., `somsiad.up.railway.app`)

### Step 5: Deploy

1. Railway auto-deploys on code push
2. Monitor logs: Click "Deployments" → View logs
3. Wait for: "Starting gunicorn..." (successful deploy)

### Step 6: Run Migrations

In Railway dashboard → Service → "Settings" → "Deploy" section:

Click "Console" or run via Railway CLI:
```bash
railway run python manage.py migrate
```

### Step 7: Create Superuser (Admin Account)

**Via Railway Console:**
```bash
railway run python manage.py createsuperuser
```

**Follow prompts:**
- Email: your-admin@example.com
- Password: (strong password, save it!)
- Password confirmation: (repeat)

### Step 8: Collect Static Files

```bash
railway run python manage.py collectstatic --noinput
```

### Step 9: Verify Deployment

1. Visit your Railway URL: `https://your-app.railway.app/`
2. Should redirect to `/accounts/login/`
3. Login with superuser credentials
4. Test RAG query: Ask a question
5. Test document upload (if you have test PDFs)

---

## 🧪 Security Testing Checklist

### Test 1: Signup Blocked
```bash
# Should return 403 Forbidden
curl -X GET https://your-app.railway.app/accounts/signup/
```
✅ Expected: "Public Signup Disabled" page (403)

### Test 2: Rate Limiting (Manual)
1. Login to app
2. Submit 21 RAG queries within 1 minute
3. ✅ Expected: 21st query returns "Rate limit exceeded" (429)

### Test 3: Login Works
1. Visit `/accounts/login/`
2. Login with superuser credentials
3. ✅ Expected: Redirect to home (chat interface)

### Test 4: Admin Panel Access
1. Visit `/admin/`
2. Login with superuser credentials
3. ✅ Expected: Django admin panel loads

### Test 5: HTTPS Redirect
```bash
# Should redirect to HTTPS
curl -I http://your-app.railway.app/
```
✅ Expected: 301 Redirect → https://...

---

## 👤 User Management (Admin Only)

### How to Create New Users (Production)

**ONLY via Django Admin:**

1. Login to `/admin/` as superuser
2. Navigate to "Users" → "Add user"
3. Enter:
   - Email: user@example.com
   - Password: (generate strong password)
4. Click "Save"
5. Send credentials to user via secure channel (NOT email)

**IMPORTANT:**
- Users CANNOT self-register
- Users CANNOT reset passwords (no email configured)
- Admins must manage ALL user accounts

---

## 🔍 Monitoring & Logs

### Railway Logs
1. Railway dashboard → Service → "Deployments"
2. Click on deployment → "View Logs"
3. Monitor for:
   - Rate limit warnings
   - Failed login attempts
   - 500 errors

### Log Files (on server)
- Location: `/app/logs/django.log`
- Access via Railway CLI: `railway run cat logs/django.log`

---

## 🚨 Security Alerts to Monitor

Watch for these in logs:

```
WARNING - Rate limit exceeded for RAG query. User: X, IP: Y
WARNING - Rate limit exceeded for login from IP: X
WARNING - Rate limit exceeded for document upload. User: X
```

### If you see suspicious activity:
1. Check IP address in logs
2. Ban IP via Django admin (future: install `django-defender`)
3. Review user activity in `/admin/`

---

## 🔐 Security Best Practices

### DO:
✅ Use strong SECRET_KEY (already generated)
✅ Keep DEBUG=False in production
✅ Limit ALLOWED_HOSTS to your domain only
✅ Monitor logs regularly
✅ Update dependencies monthly (`pip list --outdated`)
✅ Create users ONLY via admin

### DON'T:
❌ Share production credentials
❌ Commit .env to git
❌ Enable DEBUG=True in production
❌ Allow public signup
❌ Use weak passwords for superuser

---

## 📊 Cost Estimation (Railway)

**Free Tier:**
- ✅ 500 hours/month execution time (enough for 1 service)
- ✅ PostgreSQL included (5GB storage)
- ❌ After 500 hours: ~$5-10/month

**OpenAI API Costs:**
- Embeddings: ~$0.0001 per 1000 tokens (~$0.01/document)
- GPT-4o-mini: ~$0.002 per query
- **Estimated:** $5-20/month (depends on usage)

**Total:** ~$10-30/month

---

## 🎯 Post-Deployment Tasks

1. ✅ **Create superuser** (Step 7)
2. ✅ **Test login flow**
3. ✅ **Test RAG query** (verify OpenAI API works)
4. ✅ **Upload 1 test document** (verify Supabase works)
5. ✅ **Process document** (verify full pipeline)
6. ✅ **Test rate limiting** (21 queries in 1 min)
7. ✅ **Verify signup is blocked** (403 on /accounts/signup/)

---

## 📞 Support & Documentation

- **Deployment Guide:** `docs/DEPLOYMENT.md`
- **PRD v2.1:** `docs/NEW PRD.md`
- **Railway Docs:** https://docs.railway.app/
- **Django Security:** https://docs.djangoproject.com/en/5.2/topics/security/

---

**Deployment Status:** ⏳ Ready to deploy
**Security Level:** 🔒 HIGH (Private app)
**Next Step:** Push to GitHub → Deploy on Railway
