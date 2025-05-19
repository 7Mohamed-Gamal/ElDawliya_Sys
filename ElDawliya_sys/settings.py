import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
import sys
import django.db.utils

SERVER_IP = '192.168.1.48'
SERVER_HOSTNAME = 'ELDAWLIYA-SYSTE'

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-#9^46q1m(@yts%4xkw&%uy&_$$t!drx$-ke^z_*ircyuhk1acs')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'False'

# Allowed hosts
if DEBUG:
    ALLOWED_HOSTS = [SERVER_IP, '127.0.0.1', 'localhost']
else:
    ALLOWED_HOSTS = [SERVER_IP, '127.0.0.1', 'localhost']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'core.apps.CoreConfig',
    'accounts',
    'meetings',
    'tasks',
    'Hr',
    'inventory',
    'administrator',
    'admin_permissions',
    'Purchase_orders',
    'notifications',
    'audit.apps.AuditConfig',
    'employee_tasks',
    'cars',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit.middleware.AuditMiddleware',
    'inventory.middleware.FilterScriptMiddleware',  # Middleware for enhanced filtering in inventory
    'administrator.middleware.DatabaseConnectionMiddleware',  # Middleware to handle database connection errors
]

ROOT_URLCONF = 'ElDawliya_sys.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'inventory.context_processors.inventory_stats',
                'administrator.context_processors.system_settings',
                'notifications.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'ElDawliya_sys.wsgi.application'

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'ElDawliya_Sys',
        'HOST': 'localhost',
        'PORT': '1433',
        'USER': 'admin',
        'PASSWORD': 'hgslduhgfwdv',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'no',
        },
    },
    'primary': {
        'ENGINE': 'mssql',
        'NAME': 'ElDawliya_Sys',
        'HOST': 'ELDAWLIYA-SYSTE',
        'PORT': '1433',
        'USER': 'admin',
        'PASSWORD': 'hgslduhgfwdv',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'no',
        },
    }
}

# Save original settings
DEFAULT_DB = DATABASES['default'].copy()
PRIMARY_DB = DATABASES['primary'].copy()

# Active database setting
ACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', 'default')

# Database router
DATABASE_ROUTERS = ['ElDawliya_sys.db_router.DatabaseRouter']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ar'

LANGUAGES = [
    ('ar', _('العربية')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
    BASE_DIR / 'inventory/locale',
]

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Authentication
AUTH_USER_MODEL = 'accounts.Users_Login_New'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/home/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CSRF Settings
CSRF_FAILURE_VIEW = 'accounts.views.csrf_failure'
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Default Auto Field
# This is required for Django models
