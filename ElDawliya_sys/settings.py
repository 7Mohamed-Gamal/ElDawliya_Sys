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
DEBUG = True

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
    'api.apps.ApiConfig',  # API application
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
    'attendance.apps.AttendanceConfig',  # New attendance management app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
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
                'ElDawliya_sys.context_processors.rtl_context_processor',
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
        'HOST': 'DESKTOP-H36115',
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
            'Trusted_Connection': 'yes',
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

# Text direction settings
TEXT_DIRECTION = 'rtl'  # Default text direction
CURRENT_LANGUAGE = 'ar'  # Default language
CURRENT_FONT = 'Cairo'  # Default font

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

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Database fallback mechanism
# Store original configurations
DEFAULT_DB_CONFIG = DATABASES['default'].copy()
PRIMARY_DB_CONFIG = DATABASES['primary'].copy()

# Make sure primary database uses the same configuration as default except for HOST
PRIMARY_DB_CONFIG['ENGINE'] = DEFAULT_DB_CONFIG['ENGINE']
PRIMARY_DB_CONFIG['NAME'] = DEFAULT_DB_CONFIG['NAME']
PRIMARY_DB_CONFIG['PORT'] = DEFAULT_DB_CONFIG['PORT']
PRIMARY_DB_CONFIG['USER'] = DEFAULT_DB_CONFIG['USER']
PRIMARY_DB_CONFIG['PASSWORD'] = DEFAULT_DB_CONFIG['PASSWORD']
PRIMARY_DB_CONFIG['OPTIONS'] = DEFAULT_DB_CONFIG['OPTIONS'].copy()
DATABASES['primary'] = PRIMARY_DB_CONFIG

# Define a simple function to check if a host is reachable
def is_host_reachable(host, port, timeout=1):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, int(port)))
        return True
    except Exception:
        return False

# Try to reach the default database host
default_host = DATABASES['default']['HOST']
default_port = DATABASES['default']['PORT']
primary_host = DATABASES['primary']['HOST']
primary_port = DATABASES['primary']['PORT']

try:
    # Check if default host is reachable
    if not is_host_reachable(default_host, default_port):
        print(f"WARNING: Default database host {default_host} is not reachable.")

        # Check if primary host is reachable before switching
        if is_host_reachable(primary_host, primary_port):
            print(f"Primary database host {primary_host} is reachable. Switching to primary database.")
            DATABASES['default'] = DATABASES['primary'].copy()
            ACTIVE_DB = 'primary'
        else:
            print(f"WARNING: Primary database host {primary_host} is also not reachable. Keeping default configuration.")
    else:
        print(f"Default database host {default_host} is reachable.")
except Exception as e:
    print(f"Error in database fallback mechanism: {e}")
    print("Continuing with original database configuration.")

# Force try primary if requested
if os.environ.get('FORCE_PRIMARY_DB', 'False') == 'True':
    print("NOTICE: Forced use of primary database by environment variable.")
    DATABASES['default'] = DATABASES['primary'].copy()
    ACTIVE_DB = 'primary'

# Load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.authentication.CombinedAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/min',
        'user': '60/min'
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT Configuration
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
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only allow all origins in debug mode

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'apikey',  # Custom header for API key
]

# Swagger/OpenAPI Configuration
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'ApiKey': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': True,
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

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'api.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'api': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
