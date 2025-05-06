import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Use environment variable for SECRET_KEY in production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-#9^46q1m(@yts%4xkw&%uy&_$$t!drx$-ke^z_*ircyuhk1acs')

# SECURITY WARNING: don't run with debug turned on in production!
# Set DEBUG to False in production
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Add production domain names/IPs when DEBUG is False
if DEBUG:
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = ['eldawliya.com', 'www.eldawliya.com']  # Replace with your actual domains


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    # تطبيقات محلية
    'core.apps.CoreConfig',  # تطبيق أساسي للوظائف المشتركة
    'accounts',
    'meetings',
    'tasks',
    'Hr',
    'inventory',
    'administrator',
    'admin_permissions',  # تمت إضافة تطبيق صلاحيات الإدارة
    'Purchase_orders',
    'notifications',  # تطبيق التنبيهات
    'audit.apps.AuditConfig',  # تطبيق تسجيل وتدقيق الأحداث
    'employee_tasks',  # تطبيق مهام الموظفين
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
    'audit.middleware.AuditMiddleware',  # إضافة middleware لتسجيل الأحداث تلقائيًا
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
                'administrator.context_processors.user_permissions',
                'notifications.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'ElDawliya_sys.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# تكوين قاعدة البيانات مع آلية النسخ الاحتياطي
# استخدام مكتبة لاختبار الاتصال بقواعد البيانات
import sys
import django.db.utils

# قواعد بيانات النظام
DATABASES = {

    'default': {
        'ENGINE': 'mssql',
        'NAME': 'El_Dawliya_International',
        'HOST': 'DESKTOP-H361157',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'yes',
        },
    },
    # الإعدادات الأصلية - المحاولة الأولى
    'primary': {
        'ENGINE': 'mssql',
        'NAME': 'El_Dawliya_International',
        'HOST': 'DESKTOP-H361157',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'yes',
        },
    },
    
    # الإعدادات الجديدة - المحاولة الثانية
    'secondary': {
        'ENGINE': 'mssql',
        'NAME': 'ELDAWLIYA-Sys',
        'HOST': 'ELDAWLIYA-SYSTE',
        'PORT': '1433',
        'USER': 'admin',
        'PASSWORD': 'hgslduhgfwdv',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'yes',
        },
    },
    
    # SQLite للتطوير
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'El_Dawliya_International',
    },
}

# تنفيذ آلية النسخ الاحتياطي لقواعد البيانات
# نحاول الاتصال بقاعدة البيانات الأساسية أولاً، وإذا فشل، ننتقل إلى قاعدة البيانات الثانوية
try:
    # نحاول الاتصال بقاعدة البيانات الأساسية
    from django.db import connections
    connections['primary'].ensure_connection()
    # إذا نجح الاتصال، نستخدم الإعدادات الأساسية
    DATABASES['default'] = DATABASES['primary']
    print("تم الاتصال بنجاح بقاعدة البيانات الأساسية")
except (django.db.utils.OperationalError, Exception) as e:
    # إذا فشل الاتصال، نستخدم الإعدادات الثانوية
    DATABASES['default'] = DATABASES['secondary']
    print(f"فشل الاتصال بقاعدة البيانات الأساسية: {str(e)}")
    print("جاري استخدام قاعدة البيانات الثانوية")

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# إعدادات اللغة والتوقيت
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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Authentication
AUTH_USER_MODEL = 'accounts.Users_Login_New'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/home/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Media files (User-uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CSRF Settings
CSRF_FAILURE_VIEW = 'accounts.views.csrf_failure'
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Set to True for added security in production
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS


# # إعدادات Crispy Forms
# CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
# CRISPY_TEMPLATE_PACK = "bootstrap5"


# # إعدادات تسجيل الدخول
# LOGIN_REDIRECT_URL = 'dashboard'
# LOGIN_URL = 'login'
# LOGOUT_REDIRECT_URL = 'login'
# # إعدادات Django Bootstrap 5
# BOOTSTRAP5 = {
#     'javascript_urls': [
#         'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js',
#     ],
#     'css_url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css',
#     'javascript_in_head': True,
#     'include_jquery': True,
# }


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
