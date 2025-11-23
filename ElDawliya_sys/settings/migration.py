"""
ElDawliya System - Migration Settings
====================================

Minimal settings for running migrations without external dependencies.
"""

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Create necessary directories
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# ================================================================
# SECURITY SETTINGS
# ================================================================

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-migration-key-only')
DEBUG = True
ALLOWED_HOSTS = ['*']

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
    # Minimal third-party apps for migrations
]

LOCAL_APPS = [
    # Core apps
    'core',
    'api',
    
    # Business apps
    'accounts',
    'hr',
    'meetings',
    'tasks',
    'inventory',
    'administrator',
    'Purchase_orders',
    'notifications',
    'audit',
    
    # HR modules
    'cars',
    'attendance',
    'org',
    'employees',
    'companies',
    'leaves',
    'evaluations',
    'payrolls',
    'banks',
    'insurance',
    'training',
    'loans',
    'disciplinary',
    'tickets',
    'workflow',
    'assets',
    'rbac',
    'reports',
    'syssettings',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ================================================================
# MIDDLEWARE CONFIGURATION
# ================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ================================================================
# URL CONFIGURATION
# ================================================================

ROOT_URLCONF = 'ElDawliya_sys.settings.migration_urls'

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
            ],
        },
    },
]

# ================================================================
# DATABASE CONFIGURATION
# ================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_migration.sqlite3',
    }
}

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

# ================================================================
# STATIC FILES CONFIGURATION
# ================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

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

# ================================================================
# LOGGING CONFIGURATION
# ================================================================

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
    },
}

# ================================================================
# CACHE CONFIGURATION
# ================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

print("🔧 Migration settings loaded")