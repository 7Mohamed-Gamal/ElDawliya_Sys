from .settings import *

# Minimal middleware to avoid pulling in project-specific middleware (e.g., audit)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Restrict installed apps to those needed by Hr API and models only
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
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'accounts',
    'django_filters',
    'Hr',
]

# Use a minimal URLConf for tests to avoid loading project-level urls that import other apps
# Note: Module is under ElDawliya_sys (lowercase 'sys') directory
ROOT_URLCONF = 'ElDawliya_sys.urls_test'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Use SQLite for tests to avoid external DB dependencies
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Disable custom database router during tests
DATABASE_ROUTERS = []

# Skip migrations for the Hr app to avoid vendor-specific SQL in tests; use syncdb from models
MIGRATION_MODULES = {
    'Hr': None,
}

# Override DRF settings to avoid importing custom 'api' app classes
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Speed up hashing in tests (optional)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Reduce logging noise in tests
LOGGING['handlers']['console']['level'] = 'WARNING'
for logger_name in ['api', 'django']:
    if logger_name in LOGGING['loggers']:
        LOGGING['loggers'][logger_name]['level'] = 'WARNING'

# Use Django's default CSRF failure view
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

