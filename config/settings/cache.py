"""
Cache Configuration for ElDawliya System
=======================================

Redis-based caching configuration with fallback to database caching
"""

import os
from django.core.cache import cache

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_URL = os.getenv('REDIS_URL', f'redis://{":" + REDIS_PASSWORD + "@" if REDIS_PASSWORD else ""}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}')

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SERIALIZER': 'django_redis.serializers.pickle.PickleSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'eldawliya',
        'VERSION': 1,
        'TIMEOUT': 300,  # 5 minutes default
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
            },
        },
        'KEY_PREFIX': 'eldawliya_session',
        'TIMEOUT': 3600,  # 1 hour for sessions
    },
    'queries': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 30,
            },
        },
        'KEY_PREFIX': 'eldawliya_query',
        'TIMEOUT': 1800,  # 30 minutes for queries
    },
    'dashboard': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'eldawliya_dash',
        'TIMEOUT': 300,  # 5 minutes for dashboard data
    }
}

# Fallback to database cache if Redis is not available
try:
    import redis
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()
except (ImportError, redis.ConnectionError, redis.TimeoutError):
    print("Redis not available, falling back to database cache")
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 10000,
                'CULL_FREQUENCY': 3,
            }
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'session_cache_table',
            'TIMEOUT': 3600,
        },
        'queries': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'query_cache_table',
            'TIMEOUT': 1800,
        },
        'dashboard': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'dashboard_cache_table',
            'TIMEOUT': 300,
        }
    }

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Cache Key Prefixes
CACHE_KEY_PREFIXES = {
    'employee': 'emp',
    'department': 'dept',
    'attendance': 'att',
    'payroll': 'pay',
    'inventory': 'inv',
    'product': 'prod',
    'supplier': 'supp',
    'invoice': 'inv',
    'meeting': 'meet',
    'task': 'task',
    'report': 'rpt',
    'dashboard': 'dash',
    'query': 'qry',
    'session': 'sess',
    'user': 'usr',
}

# Cache Timeout Settings
CACHE_TIMEOUTS = {
    'short': 300,       # 5 minutes
    'medium': 1800,     # 30 minutes
    'long': 3600,       # 1 hour
    'daily': 86400,     # 24 hours
    'weekly': 604800,   # 7 days
    'monthly': 2592000, # 30 days
}

# Query Cache Settings
QUERY_CACHE_TIMEOUT = 1800  # 30 minutes
SLOW_QUERY_THRESHOLD = 1.0  # 1 second
ENABLE_QUERY_CACHING = True
ENABLE_QUERY_MONITORING = True

# Dashboard Cache Settings
DASHBOARD_CACHE_TIMEOUT = 300  # 5 minutes
DASHBOARD_STATS_CACHE_KEY = 'dashboard_stats'

# Cache Invalidation Settings
AUTO_INVALIDATE_CACHE = True
CACHE_INVALIDATION_PATTERNS = {
    'employee': ['emp_*', 'dept_employees_*', 'dashboard_*'],
    'department': ['dept_*', 'employees_*', 'dashboard_*'],
    'attendance': ['att_*', 'emp_*_att_*', 'dashboard_*'],
    'inventory': ['inv_*', 'prod_*', 'dashboard_*'],
    'payroll': ['pay_*', 'emp_*_pay_*', 'dashboard_*'],
}

# Performance Monitoring
CACHE_PERFORMANCE_MONITORING = True
CACHE_STATS_RETENTION_DAYS = 30

# Template Fragment Caching
TEMPLATE_CACHE_TIMEOUT = 3600  # 1 hour
ENABLE_TEMPLATE_CACHING = True

# API Response Caching
API_CACHE_TIMEOUT = 600  # 10 minutes
ENABLE_API_CACHING = True
