import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
import sys
import django.db.utils
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Server configuration from environment variables
SERVER_IP = os.environ.get('SERVER_IP', '127.0.0.1')
SERVER_HOSTNAME = os.environ.get('SERVER_HOSTNAME', 'localhost')

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Generate a new secret key and store it in .env file
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY must be set in environment variables or .env file")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

# Allowed hosts - should be configured via environment variable
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Log configuration for debugging (only in development)
if DEBUG:
    print(f"DEBUG MODE: {DEBUG}")
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
    # Advanced Features
    'channels',
    'django_celery_beat',
    'django_celery_results',
    'django_extensions',
    'storages',
    'django_cleanup',
    # Core apps
    'hr.apps.HrConfig',  # Main HR system hub
    'core.apps.CoreConfig',
    'api.apps.ApiConfig',  # API application
    'accounts',
    'meetings',
    'tasks',
    # 'Hr',  # Removed - replaced with modular HR applications
    'inventory',
    'administrator',
    'Purchase_orders',
    'notifications',
    'audit.apps.AuditConfig',
    'employee_tasks',
    'cars',
    'attendance.apps.AttendanceConfig',  # New attendance management app
    'org.apps.OrgConfig',
    'employees.apps.EmployeesConfig',
    'companies.apps.CompaniesConfig',
    'leaves.apps.LeavesConfig',
    'evaluations.apps.EvaluationsConfig',
    'payrolls.apps.PayrollsConfig',
    'banks',
    'insurance.apps.InsuranceConfig',
    'training.apps.TrainingConfig',
    'disciplinary.apps.DisciplinaryConfig',
    'loans.apps.LoansConfig',
    'assets.apps.AssetsConfig',
    'tickets.apps.TicketsConfig',
    'workflow.apps.WorkflowConfig',
    'syssettings.apps.SyssettingsConfig',
    'reports.apps.ReportsConfig',  # Reports and analytics system
    'rbac.apps.RbacConfig',
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
        'HOST': '192.168.1.48',
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

FIELD_ENCRYPTION_KEY = os.getenv('FIELD_ENCRYPTION_KEY')

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

# Redis Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Caching Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Redis Cache (disabled for now)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': REDIS_URL,
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
#             'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
#         },
#         'KEY_PREFIX': 'hr_system',
#         'TIMEOUT': 300,  # 5 minutes default
#     }
# }

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Celery Beat Configuration
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Channels Configuration (WebSocket)
ASGI_APPLICATION = 'ElDawliya_sys.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# File Storage Configuration
if not DEBUG:
    # Production file storage (can be configured for AWS S3, etc.)
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# HR System Specific Settings
HR_SETTINGS = {
    'EMPLOYEE_NUMBER_PREFIX': 'EMP',
    'EMPLOYEE_NUMBER_LENGTH': 6,
    'DEFAULT_WORK_HOURS_PER_DAY': 8,
    'DEFAULT_WORK_DAYS_PER_WEEK': 5,
    'OVERTIME_THRESHOLD_MINUTES': 30,
    'LATE_THRESHOLD_MINUTES': 15,
    'DOCUMENT_EXPIRY_WARNING_DAYS': 30,
    'LEAVE_BALANCE_CALCULATION_METHOD': 'monthly',  # monthly, yearly
    'PAYROLL_CALCULATION_METHOD': 'monthly',
    'ATTENDANCE_SYNC_INTERVAL_MINUTES': 15,
}

# Notification Settings
NOTIFICATIONS_SETTINGS = {
    'EMAIL_NOTIFICATIONS': True,
    'SMS_NOTIFICATIONS': False,  # Can be enabled later
    'PUSH_NOTIFICATIONS': True,
    'DEFAULT_NOTIFICATION_METHODS': ['email', 'in_app'],
}

# Security Settings for HR System
HR_SECURITY_SETTINGS = {
    'REQUIRE_2FA_FOR_SENSITIVE_OPERATIONS': False,  # Can be enabled
    'LOG_ALL_HR_OPERATIONS': True,
    'ENCRYPT_SENSITIVE_FIELDS': True,
    'PASSWORD_RESET_TIMEOUT_DAYS': 1,
    'SESSION_TIMEOUT_MINUTES': 480,  # 8 hours
}

# Email Configuration (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@eldawliya.com')

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
        'hr_audit': {
            'format': '{asctime} - {name} - {levelname} - {message}',
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
        'hr_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'hr_system.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'hr_audit',
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
        'hr_system': {
            'handlers': ['hr_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
