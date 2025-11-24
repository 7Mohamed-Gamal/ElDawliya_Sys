"""
ElDawliya System - Development Settings
======================================

Settings for development environment.
"""

# TODO: Replace wildcard import
# from .base import specific_items

# ================================================================
# DEBUG CONFIGURATION
# ================================================================

DEBUG = True
DEVELOPMENT_MODE = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# ================================================================
# DEVELOPMENT APPS
# ================================================================

INSTALLED_APPS += [
    'debug_toolbar',
]

# ================================================================
# DEVELOPMENT MIDDLEWARE
# ================================================================

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

# ================================================================
# DEBUG TOOLBAR CONFIGURATION
# ================================================================

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'SHOW_COLLAPSED': True,
    'SHOW_TEMPLATE_CONTEXT': True,
    'ENABLE_STACKTRACES': True,
}

INTERNAL_IPS = [
    '127.0.0.1',
    '::1',
    'localhost',
]

# ================================================================
# DATABASE CONFIGURATION FOR DEVELOPMENT
# ================================================================

# Enable SQL logging in development
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# ================================================================
# CACHE CONFIGURATION FOR DEVELOPMENT
# ================================================================

# Use local memory cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 60,  # 1 minute for development
    }
}

# ================================================================
# EMAIL CONFIGURATION FOR DEVELOPMENT
# ================================================================

# Use console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ================================================================
# SECURITY SETTINGS FOR DEVELOPMENT
# ================================================================

# Disable security features for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# ================================================================
# CELERY CONFIGURATION FOR DEVELOPMENT
# ================================================================

# Run tasks synchronously in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ================================================================
# DEVELOPMENT UTILITIES
# ================================================================

# Django Extensions settings
SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000

# Template debugging
TEMPLATES[0]['OPTIONS']['debug'] = True

# ================================================================
# DEVELOPMENT LOGGING
# ================================================================

# More verbose logging in development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['hr_system']['level'] = 'DEBUG'

print("🚀 Development mode activated")
print(f"📊 Debug Toolbar: {'Enabled' if 'debug_toolbar' in INSTALLED_APPS else 'Disabled'}")
print(f"🗄️ Database: {DATABASES['default']['HOST']}")
print(f"📧 Email Backend: {EMAIL_BACKEND}")