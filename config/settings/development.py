"""
Development settings for Law_Advisor project.

Used for local development with DEBUG enabled and SQLite database.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CSRF Configuration (for HTMX and AJAX requests)
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF cookie
CSRF_COOKIE_SAMESITE = 'Lax'  # Reasonable protection while allowing functionality
CSRF_USE_SESSIONS = False  # Use cookie-based CSRF token (default)
CSRF_COOKIE_SECURE = False  # HTTP is fine for local development

# Development-specific settings
# Email backend for console output (not actually sending emails)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# More verbose error pages in development
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}
