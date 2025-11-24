"""
Secure Configuration Management Service
خدمة إدارة التكوين الآمن

This service manages secure storage and retrieval of configuration data,
secrets, and sensitive settings with encryption and access control.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .encryption_service import encryption_service

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """
    Security configuration settings
    إعدادات التكوين الأمني
    """
    # SSL/TLS Settings
    force_https: bool = True
    ssl_redirect: bool = True
    secure_cookies: bool = True
    secure_headers: bool = True

    # Session Security
    session_timeout_minutes: int = 30
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = 'Strict'

    # CSRF Protection
    csrf_cookie_secure: bool = True
    csrf_cookie_httponly: bool = True
    csrf_trusted_origins: list = None

    # Content Security Policy
    csp_enabled: bool = True
    csp_default_src: str = "'self'"
    csp_script_src: str = "'self' 'unsafe-inline'"
    csp_style_src: str = "'self' 'unsafe-inline'"
    csp_img_src: str = "'self' data: https:"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst: int = 10

    # File Upload Security
    max_upload_size_mb: int = 10
    allowed_file_extensions: list = None
    scan_uploads_for_malware: bool = True

    # Database Security
    db_connection_encryption: bool = True
    db_query_logging: bool = False
    db_slow_query_threshold_ms: int = 1000

    # API Security
    api_rate_limit_per_hour: int = 1000
    api_require_authentication: bool = True
    api_cors_allowed_origins: list = None

    # Audit and Monitoring
    audit_all_requests: bool = True
    audit_sensitive_operations: bool = True
    security_event_retention_days: int = 365

    def __post_init__(self):
        """__post_init__ function"""
        if self.csrf_trusted_origins is None:
            self.csrf_trusted_origins = []
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.txt', '.csv', '.jpg', '.jpeg', '.png', '.gif'
            ]
        if self.api_cors_allowed_origins is None:
            self.api_cors_allowed_origins = []


class SecureConfigManager:
    """
    Secure configuration manager for sensitive settings
    مدير التكوين الآمن للإعدادات الحساسة
    """

    def __init__(self):
        """__init__ function"""
        self.config_dir = Path(getattr(settings, 'SECURE_CONFIG_DIR', '/etc/eldawliya/config'))
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.secrets_file = self.config_dir / 'secrets.enc'
        self.config_file = self.config_dir / 'config.enc'

        self._secrets_cache = {}
        self._config_cache = {}
        self._cache_timeout = 300  # 5 minutes

    def store_secret(self, key: str, value: str, category: str = 'general') -> bool:
        """
        Store a secret securely
        تخزين سر بأمان
        """
        try:
            secrets = self._load_secrets()

            if category not in secrets:
                secrets[category] = {}

            secrets[category][key] = {
                'value': value,
                'created_at': timezone.now().isoformat(),
                'updated_at': timezone.now().isoformat()
            }

            self._save_secrets(secrets)
            self._invalidate_secrets_cache()

            logger.info(f"Secret stored: {category}.{key}")
            return True

        except Exception as e:
            logger.error(f"Failed to store secret {category}.{key}: {e}")
            return False

    def get_secret(self, key: str, category: str = 'general', default: Any = None) -> Any:
        """
        Retrieve a secret
        استرداد سر
        """
        try:
            secrets = self._load_secrets()

            if category in secrets and key in secrets[category]:
                return secrets[category][key]['value']

            return default

        except Exception as e:
            logger.error(f"Failed to retrieve secret {category}.{key}: {e}")
            return default

    def delete_secret(self, key: str, category: str = 'general') -> bool:
        """
        Delete a secret
        حذف سر
        """
        try:
            secrets = self._load_secrets()

            if category in secrets and key in secrets[category]:
                del secrets[category][key]
                self._save_secrets(secrets)
                self._invalidate_secrets_cache()

                logger.info(f"Secret deleted: {category}.{key}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete secret {category}.{key}: {e}")
            return False

    def list_secrets(self, category: str = None) -> Dict[str, Any]:
        """
        List all secrets (without values)
        قائمة جميع الأسرار (بدون القيم)
        """
        try:
            secrets = self._load_secrets()

            result = {}
            categories_to_list = [category] if category else secrets.keys()

            for cat in categories_to_list:
                if cat in secrets:
                    result[cat] = {}
                    for key, data in secrets[cat].items():
                        result[cat][key] = {
                            'created_at': data.get('created_at'),
                            'updated_at': data.get('updated_at'),
                            'has_value': bool(data.get('value'))
                        }

            return result

        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return {}

    def store_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Store configuration data
        تخزين بيانات التكوين
        """
        try:
            config_data['updated_at'] = timezone.now().isoformat()

            encrypted_data = encryption_service.encrypt_dict(config_data)

            with open(self.config_file, 'w') as f:
                f.write(encrypted_data)

            self._invalidate_config_cache()

            logger.info("Configuration data stored")
            return True

        except Exception as e:
            logger.error(f"Failed to store configuration: {e}")
            return False

    def get_config(self, key: str = None, default: Any = None) -> Any:
        """
        Retrieve configuration data
        استرداد بيانات التكوين
        """
        try:
            config = self._load_config()

            if key is None:
                return config

            return config.get(key, default)

        except Exception as e:
            logger.error(f"Failed to retrieve configuration: {e}")
            return default if key else {}

    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update configuration data
        تحديث بيانات التكوين
        """
        try:
            config = self._load_config()
            config.update(updates)

            return self.store_config(config)

        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False

    def _load_secrets(self) -> Dict[str, Any]:
        """
        Load secrets from encrypted file
        تحميل الأسرار من الملف المشفر
        """
        cache_key = 'secure_secrets'
        cached_secrets = cache.get(cache_key)

        if cached_secrets is not None:
            return cached_secrets

        if not self.secrets_file.exists():
            return {}

        try:
            with open(self.secrets_file, 'r') as f:
                encrypted_data = f.read()

            secrets = encryption_service.decrypt_dict(encrypted_data)

            # Cache for performance
            cache.set(cache_key, secrets, self._cache_timeout)

            return secrets

        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            return {}

    def _save_secrets(self, secrets: Dict[str, Any]) -> None:
        """
        Save secrets to encrypted file
        حفظ الأسرار في الملف المشفر
        """
        encrypted_data = encryption_service.encrypt_dict(secrets)

        with open(self.secrets_file, 'w') as f:
            f.write(encrypted_data)

        # Set restrictive permissions
        os.chmod(self.secrets_file, 0o600)

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from encrypted file
        تحميل التكوين من الملف المشفر
        """
        cache_key = 'secure_config'
        cached_config = cache.get(cache_key)

        if cached_config is not None:
            return cached_config

        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, 'r') as f:
                encrypted_data = f.read()

            config = encryption_service.decrypt_dict(encrypted_data)

            # Cache for performance
            cache.set(cache_key, config, self._cache_timeout)

            return config

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}

    def _invalidate_secrets_cache(self):
        """Invalidate secrets cache"""
        cache.delete('secure_secrets')

    def _invalidate_config_cache(self):
        """Invalidate config cache"""
        cache.delete('secure_config')

    def backup_secrets(self, backup_path: str) -> bool:
        """
        Create encrypted backup of secrets
        إنشاء نسخة احتياطية مشفرة من الأسرار
        """
        try:
            secrets = self._load_secrets()

            backup_data = {
                'secrets': secrets,
                'backup_created_at': timezone.now().isoformat(),
                'version': '1.0'
            }

            encrypted_backup = encryption_service.encrypt_dict(backup_data)

            with open(backup_path, 'w') as f:
                f.write(encrypted_backup)

            os.chmod(backup_path, 0o600)

            logger.info(f"Secrets backup created: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to backup secrets: {e}")
            return False

    def restore_secrets(self, backup_path: str) -> bool:
        """
        Restore secrets from encrypted backup
        استعادة الأسرار من النسخة الاحتياطية المشفرة
        """
        try:
            with open(backup_path, 'r') as f:
                encrypted_backup = f.read()

            backup_data = encryption_service.decrypt_dict(encrypted_backup)

            if 'secrets' not in backup_data:
                raise ValueError("Invalid backup format")

            self._save_secrets(backup_data['secrets'])
            self._invalidate_secrets_cache()

            logger.info(f"Secrets restored from backup: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore secrets: {e}")
            return False


class EnvironmentConfigManager:
    """
    Manager for environment-specific configuration
    مدير التكوين الخاص بالبيئة
    """

    def __init__(self):
        """__init__ function"""
        self.environment = self._detect_environment()
        self.security_config = self._load_security_config()

    def _detect_environment(self) -> str:
        """
        Detect current environment (development, staging, production)
        اكتشاف البيئة الحالية (تطوير، اختبار، إنتاج)
        """
        env = os.environ.get('DJANGO_ENV', 'development').lower()

        if env in ['production', 'prod']:
            return 'production'
        elif env in ['staging', 'stage']:
            return 'staging'
        else:
            return 'development'

    def _load_security_config(self) -> SecurityConfig:
        """
        Load security configuration based on environment
        تحميل التكوين الأمني بناءً على البيئة
        """
        # Base configuration
        config_data = {}

        # Environment-specific overrides
        if self.environment == 'production':
            config_data.update({
                'force_https': True,
                'ssl_redirect': True,
                'secure_cookies': True,
                'session_cookie_secure': True,
                'csrf_cookie_secure': True,
                'csp_enabled': True,
                'rate_limit_enabled': True,
                'audit_all_requests': True,
                'db_query_logging': False,
            })
        elif self.environment == 'staging':
            config_data.update({
                'force_https': True,
                'ssl_redirect': True,
                'secure_cookies': True,
                'db_query_logging': True,
                'audit_all_requests': True,
            })
        else:  # development
            config_data.update({
                'force_https': False,
                'ssl_redirect': False,
                'secure_cookies': False,
                'session_cookie_secure': False,
                'csrf_cookie_secure': False,
                'csp_enabled': False,
                'rate_limit_enabled': False,
                'db_query_logging': True,
                'audit_all_requests': False,
            })

        return SecurityConfig(**config_data)

    def get_security_headers(self) -> Dict[str, str]:
        """
        Get security headers based on configuration
        الحصول على رؤوس الأمان بناءً على التكوين
        """
        headers = {}

        if self.security_config.secure_headers:
            headers.update({
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            })

            if self.security_config.force_https:
                headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        if self.security_config.csp_enabled:
            csp_directives = [
                f"default-src {self.security_config.csp_default_src}",
                f"script-src {self.security_config.csp_script_src}",
                f"style-src {self.security_config.csp_style_src}",
                f"img-src {self.security_config.csp_img_src}",
            ]
            headers['Content-Security-Policy'] = '; '.join(csp_directives)

        return headers

    def get_session_config(self) -> Dict[str, Any]:
        """
        Get session configuration
        الحصول على تكوين الجلسة
        """
        return {
            'SESSION_COOKIE_SECURE': self.security_config.session_cookie_secure,
            'SESSION_COOKIE_HTTPONLY': self.security_config.session_cookie_httponly,
            'SESSION_COOKIE_SAMESITE': self.security_config.session_cookie_samesite,
            'SESSION_COOKIE_AGE': self.security_config.session_timeout_minutes * 60,
        }

    def get_csrf_config(self) -> Dict[str, Any]:
        """
        Get CSRF configuration
        الحصول على تكوين CSRF
        """
        return {
            'CSRF_COOKIE_SECURE': self.security_config.csrf_cookie_secure,
            'CSRF_COOKIE_HTTPONLY': self.security_config.csrf_cookie_httponly,
            'CSRF_TRUSTED_ORIGINS': self.security_config.csrf_trusted_origins,
        }

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == 'production'

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == 'development'

    def get_allowed_hosts(self) -> list:
        """
        Get allowed hosts based on environment
        الحصول على المضيفين المسموحين بناءً على البيئة
        """
        if self.environment == 'production':
            return os.environ.get('ALLOWED_HOSTS', '').split(',')
        elif self.environment == 'staging':
            return ['staging.eldawliya.com', 'test.eldawliya.com']
        else:
            return ['localhost', '127.0.0.1', '0.0.0.0']


class SecretsRotationService:
    """
    Service for rotating secrets and API keys
    خدمة تدوير الأسرار ومفاتيح API
    """

    def __init__(self, config_manager: SecureConfigManager):
        """__init__ function"""
        self.config_manager = config_manager

    def rotate_secret(self, key: str, category: str = 'general') -> Dict[str, Any]:
        """
        Rotate a secret by generating a new value
        تدوير سر بتوليد قيمة جديدة
        """
        try:
            # Generate new secret
            new_secret = encryption_service.generate_secure_token(32)

            # Get old secret for backup
            old_secret = self.config_manager.get_secret(key, category)

            # Store new secret
            success = self.config_manager.store_secret(key, new_secret, category)

            if success:
                # Store old secret as backup
                backup_key = f"{key}_backup_{int(timezone.now().timestamp())}"
                self.config_manager.store_secret(backup_key, old_secret, f"{category}_backups")

                logger.info(f"Secret rotated: {category}.{key}")

                return {
                    'success': True,
                    'new_secret': new_secret,
                    'backup_key': backup_key
                }
            else:
                return {'success': False, 'error': 'Failed to store new secret'}

        except Exception as e:
            logger.error(f"Failed to rotate secret {category}.{key}: {e}")
            return {'success': False, 'error': str(e)}

    def schedule_rotation(self, key: str, category: str, rotation_days: int):
        """
        Schedule automatic secret rotation
        جدولة تدوير الأسرار التلقائي
        """
        # This would integrate with a task scheduler like Celery
        # For now, we'll store the rotation schedule
        schedule_data = {
            'key': key,
            'category': category,
            'rotation_days': rotation_days,
            'next_rotation': (timezone.now() + timezone.timedelta(days=rotation_days)).isoformat(),
            'created_at': timezone.now().isoformat()
        }

        schedule_key = f"rotation_schedule_{category}_{key}"
        return self.config_manager.store_secret(schedule_key, json.dumps(schedule_data), 'rotation_schedules')


# Global instances
secure_config_manager = SecureConfigManager()
environment_config_manager = EnvironmentConfigManager()
secrets_rotation_service = SecretsRotationService(secure_config_manager)
