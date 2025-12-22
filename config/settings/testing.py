"""
Testing settings for ElDawliya System.
"""

# TODO: Replace wildcard import
# from .base import specific_items

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Database for testing (use SQLite for faster tests)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Password hashers for testing (faster)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Static files for testing
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Session settings for testing
SESSION_COOKIE_SECURE = False

# Security settings for testing
SECURE_SSL_REDIRECT = False

# Logging for testing (minimal)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Testing-specific settings
TESTING_MODE = True

# Disable migrations for faster tests
class DisableMigrations:
    """DisableMigrations class"""
    def __contains__(self, item):
        """__contains__ function"""
        return True

    def __getitem__(self, item):
        """__getitem__ function"""
        return None

MIGRATION_MODULES = DisableMigrations()
