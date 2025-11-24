"""
ElDawliya System - Configuration Management
==========================================

Centralized configuration management for the ElDawliya system.
This module provides utilities for managing environment-specific settings.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# Handle missing dependencies gracefully
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass


class ConfigManager:
    """
    Configuration manager for ElDawliya system.
    Provides centralized access to configuration values with validation.
    """

    def __init__(self):
        """__init__ function"""
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self._config_cache = {}

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration with validation."""
        db_engine = self.get_optional('DB_ENGINE', 'django.db.backends.sqlite3')
        
        if db_engine == 'django.db.backends.sqlite3':
            # SQLite configuration for development
            config = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': self.base_dir / self.get_optional('DB_NAME', 'db.sqlite3'),
            }
        else:
            # SQL Server configuration for production
            config = {
                'ENGINE': 'mssql',
                'NAME': self.get_required('DB_NAME'),
                'HOST': self.get_required('DB_HOST'),
                'PORT': self.get_optional('DB_PORT', '1433'),
                'USER': self.get_required('DB_USER'),
                'PASSWORD': self.get_required('DB_PASSWORD'),
                'OPTIONS': {
                    'driver': self.get_optional('DB_DRIVER', 'ODBC Driver 17 for SQL Server'),
                    'Trusted_Connection': self.get_optional('DB_TRUSTED', 'no'),
                    'MARS_Connection': 'yes',
                    'charset': 'utf8',
                    'collation': 'Arabic_CI_AS',
                    'autocommit': True,
                    'isolation_level': 'read committed',
                    'timeout': 30,
                    'query_timeout': 60,
                    'connection_timeout': 30,
                    'command_timeout': 60,
                },
                'TEST': {
                    'NAME': f"test_{self.get_required('DB_NAME')}",
                    'CHARSET': 'utf8',
                    'COLLATION': 'Arabic_CI_AS',
                }
            }

        return config

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration with fallback to database cache."""
        # Try Redis first if available
        try:
            import redis
            import django_redis
            redis_url = self.get_optional('REDIS_URL', 'redis://127.0.0.1:6379/1')
            
            # Test Redis connection
            redis_client = redis.from_url(redis_url)
            redis_client.ping()
            
            return {
                'default': {
                    'BACKEND': 'django_redis.cache.RedisCache',
                    'LOCATION': redis_url,
                    'OPTIONS': {
                        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                        'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
                        'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                    },
                    'KEY_PREFIX': 'hr_system',
                    'TIMEOUT': int(self.get_optional('CACHE_TIMEOUT_MEDIUM', '1800')),
                }
            }
        except (ImportError, Exception):
            # Fall back to database cache
            return {
                'default': {
                    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
                    'LOCATION': 'cache_table',
                    'TIMEOUT': int(self.get_optional('CACHE_TIMEOUT_MEDIUM', '1800')),
                    'OPTIONS': {
                        'MAX_ENTRIES': 10000,
                        'CULL_FREQUENCY': 3,
                    }
                }
            }

    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration."""
        return {
            'EMAIL_BACKEND': self.get_optional(
                'EMAIL_BACKEND',
                'django.core.mail.backends.smtp.EmailBackend'
            ),
            'EMAIL_HOST': self.get_optional('EMAIL_HOST', 'smtp.gmail.com'),
            'EMAIL_PORT': int(self.get_optional('EMAIL_PORT', '587')),
            'EMAIL_USE_TLS': self.get_bool('EMAIL_USE_TLS', True),
            'EMAIL_HOST_USER': self.get_optional('EMAIL_HOST_USER'),
            'EMAIL_HOST_PASSWORD': self.get_optional('EMAIL_HOST_PASSWORD'),
            'DEFAULT_FROM_EMAIL': self.get_optional(
                'DEFAULT_FROM_EMAIL',
                self.get_optional('EMAIL_HOST_USER', 'noreply@eldawliya.com')
            ),
        }

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            'FIELD_ENCRYPTION_KEY': self.get_optional('FIELD_ENCRYPTION_KEY'),
            'CORS_ALLOWED_ORIGINS': self.get_list('CORS_ALLOWED_ORIGINS'),
            'CORS_ALLOW_CREDENTIALS': self.get_bool('CORS_ALLOW_CREDENTIALS', True),
            'CSRF_TRUSTED_ORIGINS': self.get_list('CSRF_TRUSTED_ORIGINS'),
        }

    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return {
            'API_RATE_LIMIT': int(self.get_optional('API_RATE_LIMIT', '100')),
            'API_THROTTLE_ANON': self.get_optional('API_THROTTLE_ANON', '10/min'),
            'API_THROTTLE_USER': self.get_optional('API_THROTTLE_USER', '60/min'),
            'GEMINI_API_KEY': self.get_optional('GEMINI_API_KEY'),
            'GEMINI_MODEL': self.get_optional('GEMINI_MODEL', 'gemini-1.5-flash'),
        }

    def get_celery_config(self) -> Dict[str, Any]:
        """Get Celery configuration."""
        return {
            'CELERY_BROKER_URL': self.get_optional(
                'CELERY_BROKER_URL',
                'redis://127.0.0.1:6379/4'
            ),
            'CELERY_RESULT_BACKEND': self.get_optional(
                'CELERY_RESULT_BACKEND',
                'redis://127.0.0.1:6379/5'
            ),
        }

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        log_dir = self.base_dir / self.get_optional('LOG_DIR', 'logs')
        log_dir.mkdir(exist_ok=True)

        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                    'style': '{',
                },
                'simple': {
                    'format': '{levelname} {asctime} {message}',
                    'style': '{',
                },
            },
            'handlers': {
                'console': {
                    'level': self.get_optional('LOG_LEVEL', 'INFO'),
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                },
                'file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': log_dir / 'django.log',
                    'maxBytes': 1024*1024*10,  # 10 MB
                    'backupCount': 5,
                    'formatter': 'verbose',
                },
            },
            'root': {
                'handlers': ['console', 'file'],
                'level': self.get_optional('LOG_LEVEL', 'INFO'),
            },
            'loggers': {
                'django': {
                    'handlers': ['console', 'file'],
                    'level': 'INFO',
                    'propagate': False,
                },
                'hr_system': {
                    'handlers': ['console', 'file'],
                    'level': 'INFO',
                    'propagate': False,
                },
            },
        }

    def get_hr_settings(self) -> Dict[str, Any]:
        """Get HR system specific settings."""
        return {
            'EMPLOYEE_NUMBER_PREFIX': self.get_optional('EMPLOYEE_NUMBER_PREFIX', 'EMP'),
            'EMPLOYEE_NUMBER_LENGTH': int(self.get_optional('EMPLOYEE_NUMBER_LENGTH', '6')),
            'DEFAULT_WORK_HOURS_PER_DAY': int(self.get_optional('DEFAULT_WORK_HOURS_PER_DAY', '8')),
            'DEFAULT_WORK_DAYS_PER_WEEK': int(self.get_optional('DEFAULT_WORK_DAYS_PER_WEEK', '5')),
            'OVERTIME_THRESHOLD_MINUTES': int(self.get_optional('OVERTIME_THRESHOLD_MINUTES', '30')),
            'LATE_THRESHOLD_MINUTES': int(self.get_optional('LATE_THRESHOLD_MINUTES', '15')),
            'DOCUMENT_EXPIRY_WARNING_DAYS': int(self.get_optional('DOCUMENT_EXPIRY_WARNING_DAYS', '30')),
            'LEAVE_BALANCE_CALCULATION_METHOD': self.get_optional('LEAVE_BALANCE_CALCULATION_METHOD', 'monthly'),
            'PAYROLL_CALCULATION_METHOD': self.get_optional('PAYROLL_CALCULATION_METHOD', 'monthly'),
            'ATTENDANCE_SYNC_ENABLED': self.get_bool('ATTENDANCE_SYNC_ENABLED', True),
            'ATTENDANCE_SYNC_INTERVAL': int(self.get_optional('ATTENDANCE_SYNC_INTERVAL', '300')),
        }

    def get_required(self, key: str) -> str:
        """Get required environment variable."""
        value = os.environ.get(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

    def get_optional(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get optional environment variable."""
        return os.environ.get(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.environ.get(key, str(default)).lower()
        return value in ('true', '1', 't', 'yes', 'on')

    def get_list(self, key: str, default: Optional[str] = None) -> list:
        """Get list from comma-separated environment variable."""
        value = os.environ.get(key, default or '')
        return [item.strip() for item in value.split(',') if item.strip()]

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate all configuration and return validation results."""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Validate required settings
        required_settings = ['DJANGO_SECRET_KEY']
        
        # Add database-specific required settings
        db_engine = self.get_optional('DB_ENGINE', 'django.db.backends.sqlite3')
        if db_engine != 'django.db.backends.sqlite3':
            required_settings.extend(['DB_NAME', 'DB_HOST', 'DB_USER', 'DB_PASSWORD'])

        for setting in required_settings:
            try:
                self.get_required(setting)
            except ValueError as e:
                results['valid'] = False
                results['errors'].append(str(e))

        # Validate optional but important settings
        if not self.get_optional('GEMINI_API_KEY'):
            results['warnings'].append('GEMINI_API_KEY not set - AI features will be disabled')

        if not self.get_optional('EMAIL_HOST_USER'):
            results['warnings'].append('EMAIL_HOST_USER not set - email notifications will not work')

        if not self.get_optional('FIELD_ENCRYPTION_KEY'):
            results['warnings'].append('FIELD_ENCRYPTION_KEY not set - sensitive data will not be encrypted')

        return results


# Global configuration manager instance
config_manager = ConfigManager()
