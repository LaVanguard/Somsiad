# Deployment Guide - Somsiad (Law_Advisor)

Complete guide for deploying Somsiad to production on Railway.app (recommended) or other platforms.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Railway Deployment (Recommended)](#railway-deployment-recommended)
4. [Alternative Platforms](#alternative-platforms)
5. [Post-Deployment Steps](#post-deployment-steps)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ GitHub repository with your code
- ✅ OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- ✅ Supabase account with:
  - Project created
  - `pgvector` extension enabled
  - `match_embeddings` function created (see [SUPABASE_SETUP.md](./SUPABASE_SETUP.md))
- ✅ All tests passing locally (`pytest`)

---

## Environment Variables

Set these environment variables in your deployment platform:

### Required Variables

```bash
# Django Configuration
SECRET_KEY=<generate-with-command-below>
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app,yourdomain.com
ENVIRONMENT=production

# OpenAI API (for RAG)
OPENAI_API_KEY=sk-your-actual-openai-key

# Supabase (for vector storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### Optional Variables

```bash
# Database (Railway provides DATABASE_URL automatically)
DATABASE_URL=postgresql://user:password@host:5432/database

# Email notifications (optional)
ADMIN_EMAIL=admin@example.com
SERVER_EMAIL=noreply@somsiad.pl
```

### Generate SECRET_KEY

Run this command locally:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Railway Deployment (Recommended)

Railway is the easiest platform for Django deployment with automatic PostgreSQL provisioning.

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Authorize Railway to access your repository

### Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `Law_Advisor` repository
4. Railway will detect Django and start building

### Step 3: Add PostgreSQL Database

1. In your project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will provision a database and set `DATABASE_URL` automatically

### Step 4: Set Environment Variables

In Railway dashboard, go to your app → Variables:

```bash
SECRET_KEY=<your-generated-secret-key>
DEBUG=False
ALLOWED_HOSTS=<your-app>.railway.app
ENVIRONMENT=production
OPENAI_API_KEY=sk-your-openai-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

**Note:** Railway automatically sets `DATABASE_URL` for PostgreSQL - you don't need to set it manually.

### Step 5: Deploy

1. Railway will automatically deploy on every push to `main` branch
2. First deployment may take 2-3 minutes
3. Check deployment logs for any errors

### Step 6: Run Migrations

Railway runs migrations automatically via `Procfile`:

```
release: python manage.py migrate --noinput
```

If you need to run manually:

```bash
railway run python manage.py migrate
```

### Step 7: Create Superuser

Connect to Railway shell:

```bash
railway run python manage.py createsuperuser
```

Follow prompts to create admin account.

### Step 8: Upload Documents

1. Log in to admin panel: `https://your-app.railway.app/admin`
2. Go to "Documents" → "Add Document"
3. Upload your legal PDFs
4. Documents will be automatically processed and embedded

---

## Alternative Platforms

### Heroku

Similar to Railway, Heroku supports automatic deploys from GitHub.

**Setup:**

1. Create Heroku account
2. Install Heroku CLI
3. Create new app:
   ```bash
   heroku create somsiad-app
   heroku addons:create heroku-postgresql:mini
   ```
4. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ENVIRONMENT=production
   # ... other variables
   ```
5. Deploy:
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### Render

Render offers free tier with automatic deploys.

**Setup:**

1. Create account at [render.com](https://render.com)
2. New Web Service → Connect GitHub repo
3. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. Start Command: `gunicorn config.wsgi:application`
5. Add PostgreSQL database (free tier available)
6. Set environment variables in dashboard

### DigitalOcean App Platform

More control, good for scaling.

**Setup:**

1. Create DigitalOcean account
2. App Platform → Create App → GitHub
3. Choose `Law_Advisor` repo
4. DigitalOcean auto-detects Django
5. Add managed PostgreSQL database
6. Configure environment variables
7. Deploy

---

## Post-Deployment Steps

### 1. Verify Deployment

```bash
curl https://your-app.railway.app/accounts/login/
```

Should return 200 OK.

### 2. Check Static Files

Visit: `https://your-app.railway.app/static/style.css`

Should load CSS file.

### 3. Test Authentication

1. Go to signup page
2. Create test account
3. Verify login works

### 4. Test RAG System

1. Upload a test document via admin
2. Wait for processing (check logs)
3. Ask a question in chat interface
4. Verify AI response with sources

### 5. Monitor Logs

**Railway:**

```bash
railway logs
```

**Heroku:**

```bash
heroku logs --tail
```

### 6. Set Up Custom Domain (Optional)

**Railway:**

1. Settings → Domains
2. Add custom domain
3. Update DNS records
4. Update `ALLOWED_HOSTS`

---

## Troubleshooting

### Issue: 500 Internal Server Error

**Cause:** Usually misconfigured environment variables

**Solution:**

1. Check Railway logs: `railway logs`
2. Verify all required env vars are set
3. Check `SECRET_KEY` is set
4. Ensure `ALLOWED_HOSTS` includes your domain

### Issue: Static Files Not Loading

**Cause:** `collectstatic` not run or Whitenoise misconfigured

**Solution:**

```bash
railway run python manage.py collectstatic --noinput
```

Verify `STATIC_ROOT` and `STATICFILES_STORAGE` in settings.

### Issue: Database Connection Error

**Cause:** `DATABASE_URL` not set or incorrect

**Solution:**

1. Verify Railway PostgreSQL is attached
2. Check `DATABASE_URL` is automatically set
3. Try manual connection test:
   ```bash
   railway run python manage.py dbshell
   ```

### Issue: RAG Queries Failing

**Cause:** OpenAI API key invalid or Supabase not configured

**Solution:**

1. Verify `OPENAI_API_KEY` is valid
2. Check Supabase `match_embeddings` function exists:
   ```sql
   SELECT * FROM match_embeddings('[0.1, 0.2, ...]'::vector, 1);
   ```
3. Re-process documents if embeddings missing

### Issue: Gunicorn Workers Crashing

**Cause:** Insufficient memory or timeout

**Solution:**

Adjust `Procfile`:

```
web: gunicorn config.wsgi:application --workers 2 --threads 4 --timeout 120 --max-requests 1000 --max-requests-jitter 100
```

### Issue: CSRF Verification Failed

**Cause:** `ALLOWED_HOSTS` or `CSRF_TRUSTED_ORIGINS` incorrect

**Solution:**

Update production settings:

```python
CSRF_TRUSTED_ORIGINS = [
    'https://your-app.railway.app',
    'https://yourdomain.com',
]
```

---

## Security Checklist

Before going live:

- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` (50+ characters)
- [ ] `ALLOWED_HOSTS` restricted to your domains
- [ ] SSL/HTTPS enabled
- [ ] Database backups enabled
- [ ] Environment variables secured
- [ ] Admin panel protected (strong password)
- [ ] Error monitoring configured (Sentry recommended)
- [ ] Rate limiting enabled (optional)

---

## Monitoring & Maintenance

### Check Application Health

```bash
# Railway
railway logs --filter "ERROR"

# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://your-app.railway.app/
```

### Database Backups

Railway automatically backs up PostgreSQL daily. For manual backup:

```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

### Update Dependencies

Regularly update dependencies for security patches:

```bash
pip list --outdated
pip install -U <package-name>
```

Update `requirements.txt` and redeploy.

---

## Performance Optimization

### Enable Caching (Optional)

Add Redis for session/cache storage:

```bash
# Railway
railway add redis
```

Update settings:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
    }
}
```

### CDN for Static Files (Optional)

For high traffic, use Cloudflare or AWS CloudFront:

1. Configure CDN to cache `/static/*` and `/media/*`
2. Update `STATIC_URL` in settings

---

## Support

For deployment issues:

- **Railway Docs:** https://docs.railway.app/
- **Django Deployment:** https://docs.djangoproject.com/en/5.2/howto/deployment/
- **GitHub Issues:** https://github.com/LaVanguard/Law_Advisor/issues

---

**Happy Deploying! 🚀**

*Last Updated: 2025-10-22*
