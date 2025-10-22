"""
Django settings package.

Automatically loads the correct settings module based on DJANGO_SETTINGS_MODULE
environment variable or defaults to development settings.

Available settings modules:
- config.settings.development (default for local development)
- config.settings.production (for production deployment)
"""

import os

# Determine which settings to use
environment = os.environ.get('ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *
