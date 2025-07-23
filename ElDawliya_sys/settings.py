import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
import sys
import django.db.utils

# Add FIELD_ENCRYPTION_KEY setting at the top with other key configurations
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY', 'Qk1vQ2JwQ2d2b1JwQ2JwQ2d2b1JwQ2JwQ2d2b1JwQ2I=')

SERVER_IP = '192.168.1.48'
SERVER_HOSTNAME = 'ELDAWLIYA-SYSTE'

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECERT_KEY', 'django-insecure-#9^46q1m(@yts%4xkw&%uy&_$$t!drx$-ke^z_*ircyuhk1acs')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = ['127.0.0.1', '127.0.0.1:8080', 'localhost', '192.168.1.48', '197.44.104.245']

print(f"DEBUG: {DEBUG}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    # REST Framework and API
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    # Core apps
    'core.apps.CoreConfig',
    'api.apps.ApiConfig',
    'accounts',
    'meetings',
    'tasks',
    'Hr',
    'inventory',
    'administrator',
    'Purchase_orders',
    'notifications',
    'audit.apps.AuditConfig',
    'employee_tasks',
    'cars',
    'attendance.apps.AttendanceConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit.middleware.AuditMiddleware',
    'inventory.middleware.FilterScriptMiddleware',
    'administrator.middleware.DatabaseConnectionMiddleware',
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
                'ElDawliya_sys.context_processors.rtl_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'ElDawliya_sys.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'ElDawliya_Sys',
        'HOST': 'ELDAWLIYA-SYSTE',
        'PORT': '1433',
        'USER': 'admin',
        'PASSWORD': 'hgslduhgfwdv',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
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
        },
    }
}

DEFAULT_DB = DATABASES['default'].copy()
PRIMARY_DB = DATABASES['primary'].copy()
ACTIVE_DB = os.environ.get('DJANGO_ACTIVE_DB', 'default')
DATABASE_ROUTERS = ['ElDawliya_sys.db_router.DatabaseRouter']

# Database fallback check
def is_host_reachable(host, port, timeout=1):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, int(port)))
        return True
    except Exception:
        return False
    
try:
    if not is_host_reachable(DATABASES['default']['HOST'], DATABASES['default']['PORT']):
        print(f"WARNING: Default database host {DATABASES['default']['HOST']} is not reachable.")
        if is_host_reachable(DATABASES['primary']['HOST'], DATABASES['primary']['PORT']):
            DATABASES['default'] = DATABASES['primary'].copy()
            ACTIVE_DB = 'primary'
except Exception as e:
    print(f"Error checking database: {e}")
