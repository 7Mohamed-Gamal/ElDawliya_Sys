"""
ElDawliya System - Testing Settings
==================================

Settings for testing environment.
"""

from .base import *

# ================================================================
# TESTING CONFIGURATION
# ================================================================

DEBUG = False
TESTING = True

# ================================================================
# DATABASE CONFIGURATION FOR TESTING
# ================================================================

# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        },
        'TEST': {
            'NAME': ':memory:',
        }
    }
}

# ================================================================
# CACHE CONFIGURATION FOR TESTING
# ================================================================

# Use dummy cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# ================================================================
# EMAIL CONFIGURATION FOR TESTING
# ================================================================

# Use locmem backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ================================================================
# CELERY CONFIGURATION FOR TESTING
# ================================================================

# Run tasks synchronously in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ================================================================
# SECURITY SETTINGS FOR TESTING
# ================================================================

# Disable security features for testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ================================================================
# PASSWORD VALIDATION FOR TESTING
# ================================================================

# Disable password validation for testing
AUTH_PASSWORD_VALIDATORS = []

# ================================================================
# LOGGING CONFIGURATION FOR TESTING
# ================================================================

# Minimal logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}

# ================================================================
# TESTING UTILITIES
# ================================================================

# Speed up tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for testing
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# ================================================================
# TEST SPECIFIC SETTINGS
# ================================================================

# Test media root
MEDIA_ROOT = BASE_DIR / 'test_media'

# Test static root
STATIC_ROOT = BASE_DIR / 'test_staticfiles'

print("🧪 Testing mode activated")
print("🗄️ Using in-memory SQLite database")
print("📧 Using locmem email backend")
print("⚡ Celery tasks running synchronously")