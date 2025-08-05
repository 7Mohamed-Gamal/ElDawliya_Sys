"""
إعدادات متقدمة لنظام الموارد البشرية الشامل
"""

import os
from .settings import *

# ===== إعدادات التخزين المؤقت المتقدم =====
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'hr_system',
        'TIMEOUT': 300,  # 5 دقائق افتراضي
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'hr_sessions',
        'TIMEOUT': 86400,  # 24 ساعة
    },
    'reports': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/3'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'hr_reports',
        'TIMEOUT': 3600,  # ساعة واحدة
    }
}

# استخدام Redis للجلسات
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400  # 24 ساعة

# ===== إعدادات Celery للمهام غير المتزامنة =====
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/4')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/5')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Riyadh'

# إعدادات المهام المجدولة
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# إعدادات المهام
CELERY_TASK_ROUTES = {
    'Hr.tasks.calculate_payroll': {'queue': 'payroll'},
    'Hr.tasks.generate_report': {'queue': 'reports'},
    'Hr.tasks.send_notification': {'queue': 'notifications'},
    'Hr.tasks.backup_data': {'queue': 'maintenance'},
}

# ===== إعدادات الملفات والوسائط =====
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# إعدادات رفع الملفات
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_PERMISSIONS = 0o644

# أنواع الملفات المسموحة
ALLOWED_FILE_TYPES = {
    'documents': ['.pdf', '.doc', '.docx', '.txt'],
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
    'spreadsheets': ['.xls', '.xlsx', '.csv'],
    'archives': ['.zip', '.rar', '.7z'],
}

# الحد الأقصى لحجم الملفات (بالبايت)
MAX_FILE_SIZES = {
    'documents': 5 * 1024 * 1024,  # 5 MB
    'images': 2 * 1024 * 1024,     # 2 MB
    'spreadsheets': 10 * 1024 * 1024,  # 10 MB
    'archives': 20 * 1024 * 1024,  # 20 MB
}

# ===== إعدادات الأمان المتقدمة =====
# تشفير البيانات الحساسة
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY', 'your-32-character-encryption-key-here')

# إعدادات كلمات المرور
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

# إعدادات الجلسات الآمنة
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# إعدادات HTTPS
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# ===== إعدادات التسجيل المتقدم =====
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
        'json': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'hr_system.log'),
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'hr_errors.log'),
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'Hr': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console', 'error_file'],
        'level': 'WARNING',
    },
}

# إنشاء مجلد السجلات إذا لم يكن موجوداً
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# ===== إعدادات REST Framework المتقدمة =====
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'api.authentication.APIKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
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
        'anon': '100/hour',
        'user': '1000/hour'
    },
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
}

# إعدادات JWT
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
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
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# ===== إعدادات الإشعارات =====
# إعدادات البريد الإلكتروني
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@eldawliya.com')

# إعدادات الإشعارات
NOTIFICATIONS_CONFIG = {
    'EMAIL_ENABLED': True,
    'SMS_ENABLED': False,  # يمكن تفعيلها لاحقاً
    'PUSH_ENABLED': True,
    'IN_APP_ENABLED': True,
    'BATCH_SIZE': 100,  # عدد الإشعارات في الدفعة الواحدة
    'RETRY_ATTEMPTS': 3,
    'RETRY_DELAY': 300,  # 5 دقائق
}

# ===== إعدادات التقارير =====
REPORTS_CONFIG = {
    'CACHE_TIMEOUT': 3600,  # ساعة واحدة
    'MAX_EXPORT_ROWS': 10000,
    'ALLOWED_FORMATS': ['pdf', 'excel', 'csv'],
    'TEMP_DIR': os.path.join(BASE_DIR, 'temp', 'reports'),
    'CLEANUP_AFTER_HOURS': 24,
}

# إنشاء مجلد التقارير المؤقت
os.makedirs(REPORTS_CONFIG['TEMP_DIR'], exist_ok=True)

# ===== إعدادات النسخ الاحتياطي =====
BACKUP_CONFIG = {
    'ENABLED': True,
    'SCHEDULE': '0 2 * * *',  # يومياً في الساعة 2 صباحاً
    'RETENTION_DAYS': 30,
    'BACKUP_DIR': os.path.join(BASE_DIR, 'backups'),
    'COMPRESS': True,
    'ENCRYPT': True,
    'INCLUDE_MEDIA': True,
}

# إنشاء مجلد النسخ الاحتياطي
os.makedirs(BACKUP_CONFIG['BACKUP_DIR'], exist_ok=True)

# ===== إعدادات الأداء =====
# إعدادات قاعدة البيانات للأداء
DATABASES['default']['OPTIONS'].update({
    'init_command': \"SET sql_mode='STRICT_TRANS_TABLES'\",
    'charset': 'utf8mb4',
    'use_unicode': True,
})

# إعدادات الاستعلامات
DATABASE_QUERY_TIMEOUT = 30  # ثانية
MAX_QUERY_RESULTS = 1000

# إعدادات التخزين المؤقت للاستعلامات
QUERY_CACHE_TIMEOUT = 300  # 5 دقائق

# ===== إعدادات المراقبة =====
MONITORING_CONFIG = {
    'ENABLED': True,
    'COLLECT_METRICS': True,
    'ALERT_THRESHOLDS': {
        'CPU_USAGE': 80,  # نسبة مئوية
        'MEMORY_USAGE': 85,  # نسبة مئوية
        'DISK_USAGE': 90,  # نسبة مئوية
        'RESPONSE_TIME': 2000,  # ميلي ثانية
    },
    'RETENTION_DAYS': 90,
}

# ===== إعدادات التكامل =====
INTEGRATION_CONFIG = {
    'ATTENDANCE_DEVICES': {
        'ENABLED': True,
        'SYNC_INTERVAL': 300,  # 5 دقائق
        'SUPPORTED_TYPES': ['zkteco', 'hikvision', 'dahua'],
    },
    'ACCOUNTING_SYSTEM': {
        'ENABLED': False,
        'API_ENDPOINT': '',
        'API_KEY': '',
    },
    'EXTERNAL_APIs': {
        'RATE_LIMIT': 1000,  # طلبات في الساعة
        'TIMEOUT': 30,  # ثانية
    }
}

# ===== إعدادات الذكاء الاصطناعي =====
AI_CONFIG = {
    'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY', ''),
    'ENABLED_FEATURES': [
        'document_analysis',
        'performance_insights',
        'predictive_analytics',
        'smart_notifications',
    ],
    'MAX_TOKENS': 1000,
    'TEMPERATURE': 0.7,
}

# ===== إعدادات التطوير =====
if DEBUG:
    # إضافة Django Debug Toolbar في بيئة التطوير
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    # إعدادات Debug Toolbar
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        'SHOW_COLLAPSED': True,
    }
    
    INTERNAL_IPS = ['127.0.0.1', '::1']

# ===== إعدادات الإنتاج =====
if not DEBUG:
    # إعدادات الأمان للإنتاج
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # ضغط الملفات الثابتة
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # إعدادات Sentry لمراقبة الأخطاء
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN', ''),
        integrations=[
            DjangoIntegration(auto_enabling=True),
            CeleryIntegration(monitor_beat_tasks=True),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment='production',
    )