"""
إعدادات التطوير المحسنة لنظام الموارد البشرية
"""

from .settings import *
from .settings_advanced import *

# تفعيل وضع التطوير
DEBUG = True
DEVELOPMENT_MODE = True

# إضافة أدوات التطوير
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

# إعدادات Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'SHOW_COLLAPSED': True,
    'SHOW_TEMPLATE_CONTEXT': True,
    'ENABLE_STACKTRACES': True,
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

INTERNAL_IPS = [
    '127.0.0.1',
    '::1',
    'localhost',
    '192.168.1.48',
]

# إعدادات قاعدة البيانات للتطوير
DATABASES['default']['OPTIONS'].update({
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': True,
    'isolation_level': 'read committed',
})

# تفعيل تسجيل الاستعلامات في التطوير
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# إعدادات البريد الإلكتروني للتطوير
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# إعدادات Celery للتطوير
CELERY_TASK_ALWAYS_EAGER = False  # تشغيل المهام بشكل غير متزامن
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_WORKER_LOG_LEVEL = 'DEBUG'

# إعدادات التخزين المؤقت للتطوير
CACHES['default']['TIMEOUT'] = 60  # دقيقة واحدة فقط في التطوير

# إعدادات الملفات الثابتة للتطوير
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# إعدادات إضافية للتطوير
ALLOWED_HOSTS = ['*']  # السماح لجميع المضيفين في التطوير

# تعطيل بعض إعدادات الأمان في التطوير
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# إعدادات Django Extensions
SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000

# إعدادات إضافية للتطوير السريع
TEMPLATE_DEBUG = True
TEMPLATE_STRING_IF_INVALID = 'INVALID_VARIABLE'

# إعدادات اختبار الأداء
PERFORMANCE_TESTING = {
    'ENABLED': True,
    'LOG_SLOW_QUERIES': True,
    'SLOW_QUERY_THRESHOLD': 0.5,  # نصف ثانية
    'LOG_TEMPLATE_RENDERING': True,
    'SLOW_TEMPLATE_THRESHOLD': 0.1,  # عُشر ثانية
}

# إعدادات البيانات التجريبية
DEMO_DATA = {
    'ENABLED': True,
    'AUTO_CREATE': True,
    'EMPLOYEES_COUNT': 50,
    'DEPARTMENTS_COUNT': 10,
    'COMPANIES_COUNT': 3,
}

# إعدادات التطوير المتقدمة
DEVELOPMENT_SETTINGS = {
    'AUTO_RELOAD': True,
    'SHOW_ERRORS': True,
    'DETAILED_ERRORS': True,
    'PROFILING': True,
    'MEMORY_DEBUGGING': True,
    'SQL_DEBUGGING': True,
}

print("🚀 وضع التطوير مفعل - Development Mode Activated")
print(f"📊 Debug Toolbar: {'مفعل' if 'debug_toolbar' in INSTALLED_APPS else 'معطل'}")
print(f"🗄️ قاعدة البيانات: {DATABASES['default']['HOST']}")
print(f"📧 البريد الإلكتروني: {EMAIL_BACKEND}")
print(f"⚡ Celery Eager: {CELERY_TASK_ALWAYS_EAGER}")