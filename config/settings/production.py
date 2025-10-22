"""
Production settings for Law_Advisor project.

Used for production deployment with security hardening and PostgreSQL.
"""

from .base import *

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allowed hosts - should be set via environment variable
# Example: ALLOWED_HOSTS="somsiad.railway.app,somsiad.com,www.somsiad.com"
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Database - Use DATABASE_URL environment variable (Railway/Heroku style)
# Fallback to Supabase PostgreSQL if DATABASE_URL not set
DATABASE_URL = config(
    'DATABASE_URL',
    default=f"postgresql://postgres:{config('SUPABASE_DB_PASSWORD', default='')}@{config('SUPABASE_DB_HOST', default='localhost')}:5432/postgres"
)

if dj_database_url:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Fallback if dj_database_url not installed
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': config('SUPABASE_DB_PASSWORD', default=''),
            'HOST': config('SUPABASE_DB_HOST', default='localhost'),
            'PORT': '5432',
        }
    }

# Security Settings
# https://docs.djangoproject.com/en/5.2/ref/settings/#security

# HTTPS/SSL
SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Railway/Heroku use proxy

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True  # Send session cookie only over HTTPS
CSRF_COOKIE_SECURE = True  # Send CSRF cookie only over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF cookie (for HTMX)
CSRF_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'knowledge': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'queries': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email Configuration (optional - for production error emails)
# Configure if you want Django to email admins about errors
ADMINS = [
    ('Admin', config('ADMIN_EMAIL', default='admin@example.com')),
]
SERVER_EMAIL = config('SERVER_EMAIL', default='noreply@somsiad.pl')

# Production email backend (configure if needed)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
