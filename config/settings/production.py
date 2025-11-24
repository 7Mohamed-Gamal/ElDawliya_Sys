"""
Production settings for ElDawliya System.
"""

# TODO: Replace wildcard import
# from .base import specific_items

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database for production
DATABASES['default'].update({
    'NAME': os.environ.get('DB_NAME', 'eldawliya_prod'),
    'OPTIONS': {
        'driver': 'ODBC Driver 17 for SQL Server',
        'extra_params': 'TrustServerCertificate=yes;Encrypt=yes',
    },
})

# Static files for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Session settings for production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

# Logging for production
LOGGING['handlers']['file']['filename'] = '/var/log/eldawliya/django.log'
LOGGING['handlers']['file']['level'] = 'WARNING'

# Error reporting
ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@eldawliya.com')),
]

MANAGERS = ADMINS

# Email settings for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'server@eldawliya.com')

# Production-specific settings
PRODUCTION_MODE = True

# Sentry for error tracking (if configured)
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), sentry_logging],
        traces_sample_rate=0.1,
        send_default_pii=True
    )
