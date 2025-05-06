import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-#9^46q1m(@yts%4xkw&%uy&_$$t!drx$-ke^z_*ircyuhk1acs')


DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

if DEBUG:
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = ['eldawliya.com', 'www.eldawliya.com']  # Replace with your actual domains


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
    # SQLite para desarrollo
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'El_Dawliya_International',
    },

    # SQL Server para producción (usando mssql-django)
    'mssql': {
        'ENGINE': 'mssql',
        'NAME': '',
        'HOST': 'DESKTOP-H361157',
        'PORT': '1433',
        'USER': '',
        'PASSWORD': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'yes',
        },
    },

    # SQL Server para producción
    'mssql_prod': {
        'ENGINE': 'mssql',
        'NAME': 'El_Dawliya_International',
        'HOST': 'DESKTOP-H361157',
        'PORT': '1433',
        # 'USER': 'admin',
        # 'PASSWORD': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'yes',
        },
    }
}


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


ANGUAGE_CODE = 'ar'

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


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

AUTH_USER_MODEL = 'accounts.Users_Login_New'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/home/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


CSRF_FAILURE_VIEW = 'accounts.views.csrf_failure'
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Set to True for added security in production
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
