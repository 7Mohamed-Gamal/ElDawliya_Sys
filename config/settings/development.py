"""
Development settings for ElDawliya System.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database for development
DATABASES['default'].update({
    'NAME': os.environ.get('DB_NAME', 'eldawliya_dev'),
})

# Static files for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache for development (use dummy cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Session settings for development
SESSION_COOKIE_SECURE = False

# Security settings for development
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar (if installed)
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
        INTERNAL_IPS = ['127.0.0.1', 'localhost']
    except ImportError:
        pass

# Logging for development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['core']['level'] = 'DEBUG'
LOGGING['loggers']['api']['level'] = 'DEBUG'

# Development-specific settings
DEVELOPMENT_MODE = True