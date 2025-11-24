"""
Advanced Logging Configuration for ElDawliya System
==================================================

Comprehensive logging setup with multiple handlers, formatters, and log levels
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / 'logs'

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    # Formatters
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'security': {
            'format': 'SECURITY {asctime} {levelname} {module} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'performance': {
            'format': 'PERF {asctime} {levelname} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    
    # Filters
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'skip_static_requests': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: not record.getMessage().startswith('/static/'),
        },
    },
    
    # Handlers
    'handlers': {
        # Console handler for development
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        
        # Main application log file
        'file_app': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'application.log',
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        
        # Error log file
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        
        # Security log file
        'file_security': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 10,
            'formatter': 'security',
            'encoding': 'utf-8',
        },
        
        # Performance log file
        'file_performance': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'performance.log',
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 10,
            'formatter': 'performance',
            'encoding': 'utf-8',
        },
        
        # Database queries log
        'file_db': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'database.log',
            'maxBytes': 100 * 1024 * 1024,  # 100MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        
        # Cache operations log
        'file_cache': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'cache.log',
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        
        # API requests log
        'file_api': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'api.log',
            'maxBytes': 100 * 1024 * 1024,  # 100MB
            'backupCount': 10,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        
        # User activity log
        'file_user_activity': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'user_activity.log',
            'maxBytes': 100 * 1024 * 1024,  # 100MB
            'backupCount': 20,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        
        # System monitoring log
        'file_monitoring': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'monitoring.log',
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 10,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        
        # Email handler for critical errors
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
            'include_html': True,
        },
        
        # Syslog handler for production
        'syslog': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
            'address': '/dev/log',  # Unix socket
        },
    },
    
    # Root logger
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file_app'],
    },
    
    # Loggers
    'loggers': {
        # Django framework loggers
        'django': {
            'handlers': ['console', 'file_app'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'django.request': {
            'handlers': ['file_error', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        
        'django.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'django.db.backends': {
            'handlers': ['file_db'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        # Application loggers
        'core': {
            'handlers': ['console', 'file_app'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'core.services.cache_service': {
            'handlers': ['file_cache'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        'core.services.query_optimizer': {
            'handlers': ['file_performance'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'core.services.monitoring_service': {
            'handlers': ['file_monitoring'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # HR module loggers
        'Hr': {
            'handlers': ['console', 'file_app'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'employees': {
            'handlers': ['file_app', 'file_user_activity'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'attendance': {
            'handlers': ['file_app'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'payrolls': {
            'handlers': ['file_app', 'file_security'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Inventory module loggers
        'inventory': {
            'handlers': ['file_app'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # API loggers
        'api': {
            'handlers': ['file_api'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'api.authentication': {
            'handlers': ['file_security'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Security loggers
        'security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        
        'audit': {
            'handlers': ['file_security', 'file_user_activity'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Performance loggers
        'performance': {
            'handlers': ['file_performance'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Third-party loggers
        'celery': {
            'handlers': ['file_app'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'redis': {
            'handlers': ['file_cache'],
            'level': 'WARNING',
            'propagate': False,
        },
        
        # Suppress noisy loggers
        'django.utils.autoreload': {
            'level': 'WARNING',
            'propagate': False,
        },
        
        'django.template': {
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Additional logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
ENABLE_SQL_LOGGING = os.getenv('ENABLE_SQL_LOGGING', 'False').lower() == 'true'
ENABLE_PERFORMANCE_LOGGING = os.getenv('ENABLE_PERFORMANCE_LOGGING', 'True').lower() == 'true'

# Adjust logging levels based on environment
if os.getenv('DJANGO_ENV') == 'production':
    # Production logging adjustments
    LOGGING['handlers']['console']['level'] = 'WARNING'
    LOGGING['loggers']['django.db.backends']['level'] = 'WARNING'
    
    # Add syslog handler in production
    LOGGING['handlers']['syslog']['level'] = 'INFO'
    LOGGING['root']['handlers'].append('syslog')

elif os.getenv('DJANGO_ENV') == 'development':
    # Development logging adjustments
    LOGGING['handlers']['console']['level'] = 'DEBUG'
    LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG' if ENABLE_SQL_LOGGING else 'WARNING'

# Performance logging configuration
if ENABLE_PERFORMANCE_LOGGING:
    LOGGING['loggers']['performance']['level'] = 'DEBUG'
    LOGGING['loggers']['core.services.query_optimizer']['level'] = 'DEBUG'

# Custom log formatters for different environments
if os.getenv('LOG_FORMAT') == 'json':
    # Use JSON formatting for all handlers
    for handler_name, handler_config in LOGGING['handlers'].items():
        if 'formatter' in handler_config and handler_config['formatter'] != 'json':
            handler_config['formatter'] = 'json'