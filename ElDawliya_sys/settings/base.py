"""
ElDawliya System - Base Settings
===============================

Common settings for all environments.
Environment-specific settings should be in separate files.

This file contains all the base configuration that is shared across
development, testing, and production environments.
"""

import os
import sys
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Create necessary directories
(BASE_DIR / 'logs').mkdir(exist_ok=True)
(BASE_DIR / 'media').mkdir(exist_ok=True)
(BASE_DIR / 'staticfiles').mkdir(exist_ok=True)

# ================================================================
# SECURITY SETTINGS
# ================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "DJANGO_SECRET_KEY must be set in environment variables or .env file. "
        "Generate one using: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

# Allowed hosts - should be configured via environment variable
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ================================================================
# APPLICATION DEFINITION
# ================================================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'channels',
    'django_celery_beat',
    'django_celery_results',
    'django_extensions',
    'storages',
    'django_cleanup',
]

LOCAL_APPS = [
    # Core apps
    'api.apps.ApiConfig',
    'accounts',
    'administrator',
    'notifications',
    'core.apps.CoreConfig',
    'audit.apps.AuditConfig',
    'companies.apps.CompaniesConfig',
    'org.apps.OrgConfig',
    'frontend',  # Enable frontend app
    
    # HR System
    'apps.hr.apps.HrConfig',
    'apps.hr.attendance.apps.AttendanceConfig',
    'apps.hr.employees.apps.EmployeesConfig',
    'apps.hr.leaves.apps.LeavesConfig',
    'apps.hr.evaluations.apps.EvaluationsConfig',
    'apps.hr.payroll.apps.PayrollsConfig',
    'apps.hr.training.apps.TrainingConfig',
    
    # Inventory & Procurement
    'apps.inventory.apps.InventoryConfig',
    'apps.procurement.purchase_orders.apps.PurchaseOrdersConfig',
    
    # Projects and Finance
    'apps.projects.tasks.apps.TasksConfig',
    'apps.projects.meetings.apps.MeetingsConfig',
    'apps.finance.banks.apps.BanksConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ================================================================
# MIDDLEWARE CONFIGURATION
# ================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit.middleware.AuditMiddleware',  # Re-enabled for testing
]

# ================================================================
# URL CONFIGURATION
# ================================================================

ROOT_URLCONF = 'ElDawliya_sys.urls'

# ================================================================
# TEMPLATE CONFIGURATION
# ================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'ElDawliya_sys.context_processors.system_info',
            ],
        },
    },
]

# ================================================================
# WSGI/ASGI CONFIGURATION
# ================================================================

WSGI_APPLICATION = 'ElDawliya_sys.wsgi.application'
ASGI_APPLICATION = 'ElDawliya_sys.asgi.application'

# ================================================================
# DATABASE CONFIGURATION
# ================================================================

from .config import config_manager

# Get database configuration from config manager
DATABASES = {
    'default': config_manager.get_database_config()
}

# Active database setting for router
ACTIVE_DB = 'default'

# Database router for multi-database support
DATABASE_ROUTERS = ['ElDawliya_sys.db_router.DatabaseRouter']

# ================================================================
# INTERNATIONALIZATION
# ================================================================

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ================================================================
# STATIC FILES CONFIGURATION
# ================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ================================================================
# MEDIA FILES CONFIGURATION
# ================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================================================
# AUTHENTICATION CONFIGURATION
# ================================================================

AUTH_USER_MODEL = 'accounts.Users_Login_New'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ================================================================
# SESSION CONFIGURATION
# ================================================================

SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ================================================================
# CRISPY FORMS CONFIGURATION
# ================================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ================================================================
# REST FRAMEWORK CONFIGURATION
# ================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'api.authentication.EnhancedAPIKeyAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.environ.get('API_THROTTLE_ANON', '10/min'),
        'user': os.environ.get('API_THROTTLE_USER', '60/min')
    }
}

# ================================================================
# JWT CONFIGURATION
# ================================================================

try:
    from datetime import timedelta

    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
        'ROTATE_REFRESH_TOKENS': True,
        'BLACKLIST_AFTER_ROTATION': True,
        'UPDATE_LAST_LOGIN': True,
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': SECRET_KEY,
        'VERIFYING_KEY': None,
        'AUDIENCE': None,
        'ISSUER': None,
        'JWK_URL': None,
        'LEEWAY': 0,
        'AUTH_HEADER_TYPES': ('Bearer',),
        'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
        'USER_ID_FIELD': 'id',
        'USER_ID_CLAIM': 'user_id',
        'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
        'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
        'TOKEN_TYPE_CLAIM': 'token_type',
        'JTI_CLAIM': 'jti',
        'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
        'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
        'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
    }
except ImportError:
    # Fallback JWT configuration without timedelta
    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': 3600,  # 60 minutes in seconds
        'REFRESH_TOKEN_LIFETIME': 604800,  # 7 days in seconds
        'ROTATE_REFRESH_TOKENS': True,
        'BLACKLIST_AFTER_ROTATION': True,
        'UPDATE_LAST_LOGIN': True,
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': SECRET_KEY,
    }

# ================================================================
# SECURITY CONFIGURATION
# ================================================================

# Get security configuration from config manager
security_config = config_manager.get_security_config()
FIELD_ENCRYPTION_KEY = security_config['FIELD_ENCRYPTION_KEY']

# ================================================================
# CORS CONFIGURATION
# ================================================================

CORS_ALLOWED_ORIGINS = security_config['CORS_ALLOWED_ORIGINS']
CORS_ALLOW_CREDENTIALS = security_config['CORS_ALLOW_CREDENTIALS']

# ================================================================
# CSRF CONFIGURATION
# ================================================================

CSRF_TRUSTED_ORIGINS = security_config['CSRF_TRUSTED_ORIGINS']

# ================================================================
# LOGGING CONFIGURATION
# ================================================================

# Get logging configuration from config manager
LOGGING = config_manager.get_logging_config()

# ================================================================
# EMAIL CONFIGURATION
# ================================================================

# Get email configuration from config manager
email_config = config_manager.get_email_config()
EMAIL_BACKEND = email_config['EMAIL_BACKEND']
EMAIL_HOST = email_config['EMAIL_HOST']
EMAIL_PORT = email_config['EMAIL_PORT']
EMAIL_USE_TLS = email_config['EMAIL_USE_TLS']
EMAIL_HOST_USER = email_config['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = email_config['EMAIL_HOST_PASSWORD']
DEFAULT_FROM_EMAIL = email_config['DEFAULT_FROM_EMAIL']

# ================================================================
# CACHE CONFIGURATION
# ================================================================

# Get cache configuration from config manager
CACHES = config_manager.get_cache_config()

# ================================================================
# CELERY CONFIGURATION
# ================================================================

# Get Celery configuration from config manager
celery_config = config_manager.get_celery_config()
CELERY_BROKER_URL = celery_config['CELERY_BROKER_URL']
CELERY_RESULT_BACKEND = celery_config['CELERY_RESULT_BACKEND']
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ================================================================
# CHANNELS CONFIGURATION
# ================================================================

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/6')],
        },
    },
}

# ================================================================
# API CONFIGURATION
# ================================================================

# Get API configuration from config manager
api_config = config_manager.get_api_config()
GEMINI_API_KEY = api_config['GEMINI_API_KEY']
GEMINI_MODEL = api_config['GEMINI_MODEL']
API_RATE_LIMIT = api_config['API_RATE_LIMIT']

# Update REST Framework throttle rates from config
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': api_config['API_THROTTLE_ANON'],
    'user': api_config['API_THROTTLE_USER']
}

# ================================================================
# HR SYSTEM SPECIFIC SETTINGS
# ================================================================

# Get HR-specific settings from config manager
HR_SETTINGS = config_manager.get_hr_settings()

# ================================================================
# SWAGGER/OPENAPI CONFIGURATION
# ================================================================

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'example'
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
}
