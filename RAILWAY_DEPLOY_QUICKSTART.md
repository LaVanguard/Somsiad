# Railway Deployment - Quick Start Guide

**Time:** 15-20 minutes
**Cost:** Free tier (Railway 500h/month + Supabase free tier)

---

## 🚀 Step-by-Step Deployment

### 1. **Railway Setup (5 min)**

1. Go to https://railway.app/
2. Click "Login with GitHub"
3. Click "New Project" → "Deploy from GitHub repo"
4. Select repository: `Law_Advisor`
5. Select branch: `feature/sprint2-rag-core`
6. Wait for initial build (~2-3 min)

---

### 2. **Get Supabase Credentials (3 min)**

Go to https://supabase.com/dashboard → Your project:

**Database Connection (choose ONE):**

**Option A - DATABASE_URL (recommended):**
1. Settings → Database → Connection string
2. Click "URI" tab
3. **IMPORTANT:** Use "Connection pooler" mode (port 6543)
4. Copy the URL (looks like):
   ```
   postgresql://postgres.xxx:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual password

**Option B - Individual variables:**
1. Settings → Database
2. Copy:
   - Host: `db.xxx.supabase.co`
   - Password: (your database password)

**API Credentials:**
1. Settings → API
2. Copy:
   - Project URL → `https://xxx.supabase.co`
   - anon public key → `eyJhbGc...` (long string)

---

### 3. **Configure Railway Environment (5 min)**

Railway dashboard → Your service → "Variables" tab:

Click "New Variable" and add these **ONE BY ONE:**

```
ENVIRONMENT
production

SECRET_KEY
mkoceau*-=)10pu*l1r5@a%n!7xg4i28cv3#xq9gp4=!whbf#c

DEBUG
False

ALLOWED_HOSTS
your-app-name.up.railway.app

DATABASE_URL
postgresql://postgres.xxx:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

SUPABASE_URL
https://your-project.supabase.co

SUPABASE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

OPENAI_API_KEY
sk-proj-...
```

**IMPORTANT:**
- Replace `[YOUR-PASSWORD]` with actual Supabase password
- Replace `your-app-name.up.railway.app` with your actual Railway domain (check "Settings" tab)
- Replace `your-project.supabase.co` with your Supabase URL
- Replace `eyJhbGc...` with your Supabase anon key
- Replace `sk-proj-...` with your OpenAI API key

After adding all variables, Railway will auto-redeploy.

---

### 4. **Run Migrations (2 min)**

Railway dashboard → Service → Click "..." → "Console"

In the console, run:
```bash
python manage.py migrate
```

Expected output: `OK` for each migration

---

### 5. **Create Admin User (2 min)**

Still in Railway console:
```bash
python manage.py createsuperuser
```

Enter:
- Email: `admin@example.com` (or your email)
- Password: (create strong password - save it!)
- Password (again): (repeat)

**Save these credentials!** You'll need them to login.

---

### 6. **Collect Static Files (1 min)**

Railway console:
```bash
python manage.py collectstatic --noinput
```

Expected: `X static files copied to '/app/staticfiles'`

---

### 7. **Test Deployment (2 min)**

1. Go to Railway → "Settings" → Copy your domain
2. Visit `https://your-app.up.railway.app/`
3. Should redirect to `/accounts/login/`
4. Login with superuser credentials
5. ✅ Success! You should see chat interface

---

## 🧪 Security Verification

### Test 1: Signup Blocked ✅
Visit: `https://your-app.up.railway.app/accounts/signup/`
Expected: Red page "Public Signup Disabled" (403)

### Test 2: Rate Limiting ✅
1. Login to app
2. Ask 21 questions within 1 minute
3. Expected: 21st query shows "Rate limit exceeded"

### Test 3: Admin Panel ✅
Visit: `https://your-app.up.railway.app/admin/`
Expected: Django admin login (use superuser credentials)

---

## 🎯 Post-Deployment

### Create Additional Users (Admin Only)

1. Login to `/admin/` as superuser
2. Users → Add user
3. Enter email + password
4. Save
5. Send credentials to user securely

**Remember:** Users CANNOT self-register!

---

## 🚨 Troubleshooting

### "500 Internal Server Error"
**Fix:**
1. Railway → Deployments → View Logs
2. Look for error messages
3. Common issues:
   - Missing environment variable
   - Wrong DATABASE_URL format
   - Migrations not run

### "This site can't be reached"
**Fix:**
1. Check Railway deployment status
2. Wait 2-3 min for build to complete
3. Check logs for crash errors

### "Rate limit exceeded" immediately
**Fix:**
- Wait 1 minute
- Rate limits reset automatically

### Cannot login
**Fix:**
1. Verify superuser was created: `railway run python manage.py shell`
2. In shell: `from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.all())`
3. If no users: Create superuser again

---

## 📊 Monitoring

### Railway Dashboard
- Deployments → View logs (real-time)
- Metrics → CPU, Memory, Network

### Logs to Watch
```
INFO - GET /api/query/stream/ 200
WARNING - Rate limit exceeded for RAG query
ERROR - 500 Internal Server Error
```

---

## 💰 Cost Estimate

**Railway:**
- Free: 500 hours/month
- After: ~$5-10/month

**Supabase:**
- Free: 500MB database, 2GB transfer/month
- After: ~$25/month (Pro plan)

**OpenAI:**
- ~$0.002 per query
- ~$0.0001 per document (embeddings)
- Estimated: $5-20/month

**Total:** ~$10-30/month (after free tiers)

---

## ✅ Deployment Complete!

You now have:
- ✅ Secure production deployment (HTTPS, rate limiting)
- ✅ No public signup (admin-only user management)
- ✅ RAG system with OpenAI + Supabase
- ✅ Monitoring and logs

**Next:** Start using the app or check full docs in `docs/PRODUCTION_DEPLOY_CHECKLIST.md`

---

**Need help?** Check logs in Railway dashboard or contact support.
