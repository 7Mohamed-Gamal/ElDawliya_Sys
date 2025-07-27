"""
إعدادات التخزين المؤقت المتقدمة
"""

import os
from django.conf import settings

# إعدادات Redis
REDIS_CONFIG = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'IGNORE_EXCEPTIONS': True,
        },
        'TIMEOUT': 300,  # 5 دقائق افتراضي
        'VERSION': 1,
        'KEY_PREFIX': 'hr_cache',
    },
    
    # تخزين مؤقت للجلسات
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.pickle.PickleSerializer',
        },
        'TIMEOUT': 86400,  # 24 ساعة
        'KEY_PREFIX': 'hr_session',
    },
    
    # تخزين مؤقت للتقارير الثقيلة
    'reports': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/3'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'TIMEOUT': 3600,  # ساعة واحدة
        'KEY_PREFIX': 'hr_reports',
    },
    
    # تخزين مؤقت للبيانات المؤقتة
    'temporary': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/4'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300,  # 5 دقائق
        'KEY_PREFIX': 'hr_temp',
    }
}

# إعدادات التخزين المؤقت الهرمي
CACHE_HIERARCHY = {
    'L1': {
        'backend': 'locmem',
        'max_entries': 1000,
        'cull_frequency': 3,
        'timeout': 300,
    },
    'L2': {
        'backend': 'redis',
        'timeout': 1800,
    },
    'L3': {
        'backend': 'database',
        'timeout': 3600,
    }
}

# استراتيجيات الإبطال
CACHE_INVALIDATION_STRATEGIES = {
    'employee': {
        'on_create': ['employee:all', 'department:*', 'reports:employee_*'],
        'on_update': ['employee:{id}', 'employee:all', 'reports:employee_*'],
        'on_delete': ['employee:{id}', 'employee:all', 'department:*', 'reports:*'],
    },
    'department': {
        'on_create': ['department:all', 'employee:*', 'reports:department_*'],
        'on_update': ['department:{id}', 'department:all', 'employee:*'],
        'on_delete': ['department:{id}', 'department:all', 'employee:*', 'reports:*'],
    },
    'attendance': {
        'on_create': ['attendance:today', 'attendance:employee_{employee_id}', 'reports:attendance_*'],
        'on_update': ['attendance:{id}', 'attendance:today', 'reports:attendance_*'],
        'on_delete': ['attendance:{id}', 'attendance:today', 'reports:*'],
    },
    'payroll': {
        'on_create': ['payroll:period_{period_id}', 'reports:payroll_*'],
        'on_update': ['payroll:{id}', 'payroll:period_{period_id}', 'reports:payroll_*'],
        'on_delete': ['payroll:{id}', 'payroll:period_{period_id}', 'reports:*'],
    }
}

# قوالب المفاتيح
CACHE_KEY_TEMPLATES = {
    'employee_list': 'employee:list:{filters_hash}',
    'employee_detail': 'employee:detail:{employee_id}',
    'employee_count': 'employee:count:{filters_hash}',
    'department_list': 'department:list:{filters_hash}',
    'department_employees': 'department:employees:{department_id}',
    'attendance_summary': 'attendance:summary:{date}:{employee_id}',
    'payroll_calculation': 'payroll:calc:{employee_id}:{period_id}',
    'report_data': 'report:{report_type}:{params_hash}',
    'search_results': 'search:{query_hash}:{filters_hash}',
    'api_response': 'api:{endpoint}:{params_hash}',
}

# إعدادات الضغط
CACHE_COMPRESSION = {
    'enabled': True,
    'min_size': 1024,  # ضغط الكائنات أكبر من 1KB
    'algorithm': 'zlib',  # zlib, gzip, lz4
    'level': 6,  # مستوى الضغط (1-9)
}

# إعدادات التشفير
CACHE_ENCRYPTION = {
    'enabled': True,
    'key': os.getenv('CACHE_ENCRYPTION_KEY', 'default-cache-key-change-in-production'),
    'algorithm': 'AES',
    'sensitive_patterns': [
        'employee:salary_*',
        'employee:personal_*',
        'payroll:*',
        'api:auth_*',
    ]
}

# إعدادات المراقبة
CACHE_MONITORING = {
    'enabled': True,
    'metrics_retention_hours': 24,
    'alert_thresholds': {
        'hit_rate_warning': 70,  # تنبيه إذا انخفض معدل الإصابة عن 70%
        'hit_rate_critical': 50,  # تنبيه حرج إذا انخفض عن 50%
        'response_time_warning': 100,  # تنبيه إذا زاد وقت الاستجابة عن 100ms
        'response_time_critical': 500,  # تنبيه حرج إذا زاد عن 500ms
        'memory_usage_warning': 80,  # تنبيه إذا زاد استخدام الذاكرة عن 80%
        'memory_usage_critical': 95,  # تنبيه حرج إذا زاد عن 95%
    },
    'notification_channels': {
        'email': True,
        'slack': False,
        'webhook': False,
    }
}

# إعدادات التسخين
CACHE_WARMUP = {
    'enabled': True,
    'on_startup': True,
    'scheduled_times': ['06:00', '12:00', '18:00'],  # أوقات التسخين المجدولة
    'functions': [
        'Hr.services.cache_service.warm_up_hr_cache',
    ]
}

# إعدادات الأداء
CACHE_PERFORMANCE = {
    'connection_pool_size': 20,
    'connection_timeout': 5,
    'socket_timeout': 5,
    'retry_on_timeout': True,
    'health_check_interval': 30,
    'max_connections_per_pool': 50,
}

# قواعد TTL التلقائية
CACHE_TTL_RULES = {
    'employee:*': 3600,      # ساعة واحدة
    'department:*': 7200,    # ساعتان
    'attendance:daily:*': 86400,  # يوم واحد
    'attendance:monthly:*': 604800,  # أسبوع واحد
    'reports:*': 1800,       # 30 دقيقة
    'search:*': 900,         # 15 دقيقة
    'api:*': 300,            # 5 دقائق
    'temp:*': 60,            # دقيقة واحدة
}

# إعدادات التنظيف التلقائي
CACHE_CLEANUP = {
    'enabled': True,
    'interval_minutes': 30,
    'max_memory_usage': 85,  # نسبة مئوية
    'cleanup_strategies': [
        'lru',  # الأقل استخداماً حديثاً
        'expired',  # المنتهية الصلاحية
        'large_objects',  # الكائنات الكبيرة
    ]
}

# إعدادات النسخ الاحتياطي
CACHE_BACKUP = {
    'enabled': False,  # معطل افتراضياً
    'interval_hours': 6,
    'retention_days': 7,
    'backup_path': '/var/backups/hr_cache/',
    'compress': True,
}


def get_cache_config():
    """الحصول على إعدادات التخزين المؤقت المدمجة"""
    
    config = {
        'CACHES': REDIS_CONFIG,
        'CACHE_MIDDLEWARE_ALIAS': 'default',
        'CACHE_MIDDLEWARE_SECONDS': 300,
        'CACHE_MIDDLEWARE_KEY_PREFIX': 'hr_middleware',
        
        # إعدادات الجلسات
        'SESSION_ENGINE': 'django.contrib.sessions.backends.cache',
        'SESSION_CACHE_ALIAS': 'sessions',
        'SESSION_COOKIE_AGE': 86400,  # 24 ساعة
        
        # إعدادات القوالب
        'TEMPLATE_CACHE_TIMEOUT': 3600,
        
        # إعدادات مخصصة
        'HR_CACHE_HIERARCHY': CACHE_HIERARCHY,
        'HR_CACHE_INVALIDATION': CACHE_INVALIDATION_STRATEGIES,
        'HR_CACHE_KEY_TEMPLATES': CACHE_KEY_TEMPLATES,
        'HR_CACHE_COMPRESSION': CACHE_COMPRESSION,
        'HR_CACHE_ENCRYPTION': CACHE_ENCRYPTION,
        'HR_CACHE_MONITORING': CACHE_MONITORING,
        'HR_CACHE_WARMUP': CACHE_WARMUP,
        'HR_CACHE_PERFORMANCE': CACHE_PERFORMANCE,
        'HR_CACHE_TTL_RULES': CACHE_TTL_RULES,
        'HR_CACHE_CLEANUP': CACHE_CLEANUP,
        'HR_CACHE_BACKUP': CACHE_BACKUP,
    }
    
    return config


def apply_cache_settings():
    """تطبيق إعدادات التخزين المؤقت على Django"""
    
    cache_config = get_cache_config()
    
    # تحديث إعدادات Django
    for key, value in cache_config.items():
        setattr(settings, key, value)
    
    # إعداد السجلات
    if not hasattr(settings, 'LOGGING'):
        settings.LOGGING = {}
    
    if 'loggers' not in settings.LOGGING:
        settings.LOGGING['loggers'] = {}
    
    settings.LOGGING['loggers']['hr_cache'] = {
        'handlers': ['console', 'file'] if hasattr(settings, 'LOGGING') else ['console'],
        'level': 'INFO',
        'propagate': False,
    }
    
    settings.LOGGING['loggers']['hr_cache_monitor'] = {
        'handlers': ['console', 'file'] if hasattr(settings, 'LOGGING') else ['console'],
        'level': 'INFO',
        'propagate': False,
    }


# تطبيق الإعدادات تلقائياً عند الاستيراد
if hasattr(settings, 'DATABASES'):  # التأكد من أن Django مهيأ
    apply_cache_settings()