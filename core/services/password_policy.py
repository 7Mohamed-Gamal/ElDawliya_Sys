"""
Password Policy and Security Configuration Service
خدمة سياسة كلمات المرور والتكوين الأمني

This service enforces password policies and manages security configurations
to ensure strong authentication and data protection.
"""

import re
import string
import secrets
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)


@dataclass
class PasswordPolicyConfig:
    """
    Password policy configuration
    تكوين سياسة كلمات المرور
    """
    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special_chars: bool = True
    min_special_chars: int = 1
    min_digits: int = 1
    min_uppercase: int = 1
    min_lowercase: int = 1
    
    # History and reuse
    password_history_count: int = 5
    min_password_age_hours: int = 1
    max_password_age_days: int = 90
    
    # Complexity rules
    max_repeated_chars: int = 2
    max_sequential_chars: int = 3
    forbidden_patterns: List[str] = None
    
    # Account lockout
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    
    # Two-factor authentication
    require_2fa_for_admin: bool = True
    require_2fa_for_sensitive_ops: bool = True
    
    def __post_init__(self):
        if self.forbidden_patterns is None:
            self.forbidden_patterns = [
                'password', '123456', 'qwerty', 'admin', 'user',
                'كلمة', 'مرور', 'سر', 'رقم'
            ]


class PasswordPolicyService:
    """
    Service for enforcing password policies and security rules
    خدمة فرض سياسات كلمات المرور والقواعد الأمنية
    """
    
    def __init__(self, config: Optional[PasswordPolicyConfig] = None):
        self.config = config or self._load_default_config()
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def _load_default_config(self) -> PasswordPolicyConfig:
        """
        Load password policy configuration from settings
        تحميل تكوين سياسة كلمات المرور من الإعدادات
        """
        policy_settings = getattr(settings, 'PASSWORD_POLICY', {})
        return PasswordPolicyConfig(**policy_settings)
    
    def validate_password(self, password: str, user: Optional[User] = None) -> Tuple[bool, List[str]]:
        """
        Validate password against policy rules
        التحقق من كلمة المرور مقابل قواعد السياسة
        """
        errors = []
        
        # Length validation
        if len(password) < self.config.min_length:
            errors.append(f'كلمة المرور يجب أن تكون على الأقل {self.config.min_length} أحرف')
        
        if len(password) > self.config.max_length:
            errors.append(f'كلمة المرور يجب ألا تتجاوز {self.config.max_length} حرف')
        
        # Character type validation
        if self.config.require_uppercase:
            uppercase_count = sum(1 for c in password if c.isupper())
            if uppercase_count < self.config.min_uppercase:
                errors.append(f'كلمة المرور يجب أن تحتوي على {self.config.min_uppercase} حرف كبير على الأقل')
        
        if self.config.require_lowercase:
            lowercase_count = sum(1 for c in password if c.islower())
            if lowercase_count < self.config.min_lowercase:
                errors.append(f'كلمة المرور يجب أن تحتوي على {self.config.min_lowercase} حرف صغير على الأقل')
        
        if self.config.require_digits:
            digit_count = sum(1 for c in password if c.isdigit())
            if digit_count < self.config.min_digits:
                errors.append(f'كلمة المرور يجب أن تحتوي على {self.config.min_digits} رقم على الأقل')
        
        if self.config.require_special_chars:
            special_count = sum(1 for c in password if c in self.special_chars)
            if special_count < self.config.min_special_chars:
                errors.append(f'كلمة المرور يجب أن تحتوي على {self.config.min_special_chars} رمز خاص على الأقل')
        
        # Complexity validation
        errors.extend(self._validate_complexity(password))
        
        # User-specific validation
        if user:
            errors.extend(self._validate_user_specific(password, user))
        
        return len(errors) == 0, errors
    
    def _validate_complexity(self, password: str) -> List[str]:
        """
        Validate password complexity rules
        التحقق من قواعد تعقيد كلمة المرور
        """
        errors = []
        
        # Check for repeated characters
        if self.config.max_repeated_chars > 0:
            for i in range(len(password) - self.config.max_repeated_chars):
                if all(c == password[i] for c in password[i:i+self.config.max_repeated_chars+1]):
                    errors.append(f'كلمة المرور لا يجب أن تحتوي على أكثر من {self.config.max_repeated_chars} أحرف متكررة متتالية')
                    break
        
        # Check for sequential characters
        if self.config.max_sequential_chars > 0:
            if self._has_sequential_chars(password, self.config.max_sequential_chars):
                errors.append(f'كلمة المرور لا يجب أن تحتوي على أكثر من {self.config.max_sequential_chars} أحرف متتالية')
        
        # Check forbidden patterns
        password_lower = password.lower()
        for pattern in self.config.forbidden_patterns:
            if pattern.lower() in password_lower:
                errors.append(f'كلمة المرور لا يجب أن تحتوي على الكلمة المحظورة: {pattern}')
        
        return errors
    
    def _has_sequential_chars(self, password: str, max_sequential: int) -> bool:
        """
        Check if password contains sequential characters
        التحقق من احتواء كلمة المرور على أحرف متتالية
        """
        # Check for ascending sequences
        for i in range(len(password) - max_sequential):
            sequence = password[i:i+max_sequential+1]
            if self._is_ascending_sequence(sequence) or self._is_descending_sequence(sequence):
                return True
        
        return False
    
    def _is_ascending_sequence(self, sequence: str) -> bool:
        """Check if sequence is ascending (e.g., 'abc', '123')"""
        for i in range(1, len(sequence)):
            if ord(sequence[i]) != ord(sequence[i-1]) + 1:
                return False
        return True
    
    def _is_descending_sequence(self, sequence: str) -> bool:
        """Check if sequence is descending (e.g., 'cba', '321')"""
        for i in range(1, len(sequence)):
            if ord(sequence[i]) != ord(sequence[i-1]) - 1:
                return False
        return True
    
    def _validate_user_specific(self, password: str, user: User) -> List[str]:
        """
        Validate password against user-specific rules
        التحقق من كلمة المرور مقابل القواعد الخاصة بالمستخدم
        """
        errors = []
        
        # Check against user information
        user_info = [
            user.username.lower(),
            user.first_name.lower() if user.first_name else '',
            user.last_name.lower() if user.last_name else '',
            user.email.split('@')[0].lower() if user.email else ''
        ]
        
        password_lower = password.lower()
        for info in user_info:
            if info and len(info) > 2 and info in password_lower:
                errors.append('كلمة المرور لا يجب أن تحتوي على معلومات شخصية')
                break
        
        # Check password history
        if self._is_password_reused(password, user):
            errors.append(f'لا يمكن إعادة استخدام آخر {self.config.password_history_count} كلمات مرور')
        
        return errors
    
    def _is_password_reused(self, password: str, user: User) -> bool:
        """
        Check if password was recently used
        التحقق من استخدام كلمة المرور مؤخراً
        """
        # This would check against password history
        # Implementation depends on how you store password history
        return False
    
    def generate_secure_password(self, length: Optional[int] = None) -> str:
        """
        Generate a secure password that meets policy requirements
        توليد كلمة مرور آمنة تلبي متطلبات السياسة
        """
        if length is None:
            length = max(12, self.config.min_length)
        
        # Ensure we have enough characters for all requirements
        min_chars_needed = (
            self.config.min_uppercase +
            self.config.min_lowercase +
            self.config.min_digits +
            self.config.min_special_chars
        )
        
        if length < min_chars_needed:
            length = min_chars_needed
        
        # Character pools
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = self.special_chars
        
        # Start with required characters
        password_chars = []
        
        # Add required uppercase
        password_chars.extend(secrets.choice(uppercase) for _ in range(self.config.min_uppercase))
        
        # Add required lowercase
        password_chars.extend(secrets.choice(lowercase) for _ in range(self.config.min_lowercase))
        
        # Add required digits
        password_chars.extend(secrets.choice(digits) for _ in range(self.config.min_digits))
        
        # Add required special characters
        password_chars.extend(secrets.choice(special) for _ in range(self.config.min_special_chars))
        
        # Fill remaining length with random characters from all pools
        all_chars = uppercase + lowercase + digits + special
        remaining_length = length - len(password_chars)
        password_chars.extend(secrets.choice(all_chars) for _ in range(remaining_length))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password_chars)
        
        password = ''.join(password_chars)
        
        # Validate the generated password
        is_valid, errors = self.validate_password(password)
        if not is_valid:
            # Retry if validation fails (shouldn't happen with proper generation)
            return self.generate_secure_password(length)
        
        return password
    
    def check_password_strength(self, password: str) -> Dict[str, any]:
        """
        Analyze password strength and provide score
        تحليل قوة كلمة المرور وتقديم النتيجة
        """
        score = 0
        feedback = []
        
        # Length scoring
        if len(password) >= 12:
            score += 25
        elif len(password) >= 8:
            score += 15
        else:
            feedback.append('استخدم 12 حرف على الأقل لكلمة مرور قوية')
        
        # Character variety scoring
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in self.special_chars for c in password)
        
        variety_score = sum([has_upper, has_lower, has_digit, has_special]) * 15
        score += variety_score
        
        if not has_upper:
            feedback.append('أضف أحرف كبيرة')
        if not has_lower:
            feedback.append('أضف أحرف صغيرة')
        if not has_digit:
            feedback.append('أضف أرقام')
        if not has_special:
            feedback.append('أضف رموز خاصة')
        
        # Complexity bonus
        if len(set(password)) / len(password) > 0.7:  # High character diversity
            score += 10
            
        if not self._has_common_patterns(password):
            score += 10
        else:
            feedback.append('تجنب الأنماط الشائعة')
        
        # Determine strength level
        if score >= 80:
            strength = 'قوية جداً'
            color = 'success'
        elif score >= 60:
            strength = 'قوية'
            color = 'info'
        elif score >= 40:
            strength = 'متوسطة'
            color = 'warning'
        else:
            strength = 'ضعيفة'
            color = 'danger'
        
        return {
            'score': min(score, 100),
            'strength': strength,
            'color': color,
            'feedback': feedback
        }
    
    def _has_common_patterns(self, password: str) -> bool:
        """
        Check for common password patterns
        التحقق من الأنماط الشائعة لكلمات المرور
        """
        common_patterns = [
            r'123+',  # Sequential numbers
            r'abc+',  # Sequential letters
            r'(.)\1{2,}',  # Repeated characters
            r'password',  # Common words
            r'qwerty',
            r'admin',
        ]
        
        password_lower = password.lower()
        for pattern in common_patterns:
            if re.search(pattern, password_lower):
                return True
        
        return False


class AccountLockoutService:
    """
    Service for managing account lockouts due to failed login attempts
    خدمة إدارة قفل الحسابات بسبب محاولات تسجيل الدخول الفاشلة
    """
    
    def __init__(self, config: Optional[PasswordPolicyConfig] = None):
        self.config = config or PasswordPolicyConfig()
    
    def record_failed_attempt(self, username: str, ip_address: str) -> Dict[str, any]:
        """
        Record a failed login attempt
        تسجيل محاولة تسجيل دخول فاشلة
        """
        cache_key_user = f"failed_attempts_user_{username}"
        cache_key_ip = f"failed_attempts_ip_{ip_address}"
        
        # Get current attempt counts
        user_attempts = cache.get(cache_key_user, 0) + 1
        ip_attempts = cache.get(cache_key_ip, 0) + 1
        
        # Set cache with expiration
        timeout = self.config.lockout_duration_minutes * 60
        cache.set(cache_key_user, user_attempts, timeout)
        cache.set(cache_key_ip, ip_attempts, timeout)
        
        # Check if account should be locked
        user_locked = user_attempts >= self.config.max_failed_attempts
        ip_locked = ip_attempts >= self.config.max_failed_attempts * 2  # Higher threshold for IP
        
        if user_locked:
            self._lock_user_account(username)
        
        return {
            'user_attempts': user_attempts,
            'ip_attempts': ip_attempts,
            'user_locked': user_locked,
            'ip_locked': ip_locked,
            'remaining_attempts': max(0, self.config.max_failed_attempts - user_attempts)
        }
    
    def clear_failed_attempts(self, username: str, ip_address: str):
        """
        Clear failed attempts after successful login
        مسح المحاولات الفاشلة بعد تسجيل الدخول الناجح
        """
        cache_key_user = f"failed_attempts_user_{username}"
        cache_key_ip = f"failed_attempts_ip_{ip_address}"
        
        cache.delete(cache_key_user)
        cache.delete(cache_key_ip)
        
        self._unlock_user_account(username)
    
    def is_account_locked(self, username: str) -> bool:
        """
        Check if user account is locked
        التحقق من قفل حساب المستخدم
        """
        cache_key = f"account_locked_{username}"
        return cache.get(cache_key, False)
    
    def is_ip_locked(self, ip_address: str) -> bool:
        """
        Check if IP address is locked
        التحقق من قفل عنوان IP
        """
        cache_key = f"failed_attempts_ip_{ip_address}"
        attempts = cache.get(cache_key, 0)
        return attempts >= self.config.max_failed_attempts * 2
    
    def _lock_user_account(self, username: str):
        """
        Lock user account
        قفل حساب المستخدم
        """
        cache_key = f"account_locked_{username}"
        timeout = self.config.lockout_duration_minutes * 60
        cache.set(cache_key, True, timeout)
        
        logger.warning(f"User account locked due to failed attempts: {username}")
    
    def _unlock_user_account(self, username: str):
        """
        Unlock user account
        إلغاء قفل حساب المستخدم
        """
        cache_key = f"account_locked_{username}"
        cache.delete(cache_key)
    
    def get_lockout_info(self, username: str) -> Dict[str, any]:
        """
        Get lockout information for user
        الحصول على معلومات القفل للمستخدم
        """
        cache_key_attempts = f"failed_attempts_user_{username}"
        cache_key_locked = f"account_locked_{username}"
        
        attempts = cache.get(cache_key_attempts, 0)
        is_locked = cache.get(cache_key_locked, False)
        
        # Calculate remaining lockout time
        remaining_time = 0
        if is_locked:
            # This is a simplified calculation
            # In practice, you'd store the lockout timestamp
            remaining_time = self.config.lockout_duration_minutes * 60
        
        return {
            'failed_attempts': attempts,
            'is_locked': is_locked,
            'max_attempts': self.config.max_failed_attempts,
            'remaining_lockout_seconds': remaining_time,
            'lockout_duration_minutes': self.config.lockout_duration_minutes
        }


class TwoFactorAuthService:
    """
    Service for managing two-factor authentication
    خدمة إدارة المصادقة الثنائية
    """
    
    def __init__(self):
        self.totp_issuer = getattr(settings, 'TOTP_ISSUER', 'ElDawliya System')
    
    def generate_totp_secret(self, user: User) -> str:
        """
        Generate TOTP secret for user
        توليد سر TOTP للمستخدم
        """
        import pyotp
        
        secret = pyotp.random_base32()
        
        # Store secret securely (encrypted)
        from .encryption_service import encryption_service
        encrypted_secret = encryption_service.encrypt_string(secret)
        
        # Store in user profile or separate model
        # This is a simplified example
        cache.set(f"totp_secret_{user.id}", encrypted_secret, 3600)
        
        return secret
    
    def generate_qr_code_url(self, user: User, secret: str) -> str:
        """
        Generate QR code URL for TOTP setup
        توليد رابط رمز QR لإعداد TOTP
        """
        import pyotp
        
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email or user.username,
            issuer_name=self.totp_issuer
        )
        
        return provisioning_uri
    
    def verify_totp_token(self, user: User, token: str) -> bool:
        """
        Verify TOTP token
        التحقق من رمز TOTP
        """
        import pyotp
        
        # Get user's secret
        from .encryption_service import encryption_service
        encrypted_secret = cache.get(f"totp_secret_{user.id}")
        
        if not encrypted_secret:
            return False
        
        try:
            secret = encryption_service.decrypt_string(encrypted_secret)
            totp = pyotp.TOTP(secret)
            
            # Verify token with window for clock skew
            return totp.verify(token, valid_window=1)
        except Exception as e:
            logger.error(f"TOTP verification failed: {e}")
            return False
    
    def generate_backup_codes(self, user: User, count: int = 10) -> List[str]:
        """
        Generate backup codes for 2FA
        توليد رموز احتياطية للمصادقة الثنائية
        """
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()  # 8-character hex code
            codes.append(code)
        
        # Store codes securely (hashed)
        from django.contrib.auth.hashers import make_password
        hashed_codes = [make_password(code) for code in codes]
        
        # Store in user profile or separate model
        cache.set(f"backup_codes_{user.id}", hashed_codes, 86400 * 30)  # 30 days
        
        return codes
    
    def verify_backup_code(self, user: User, code: str) -> bool:
        """
        Verify and consume backup code
        التحقق من واستهلاك الرمز الاحتياطي
        """
        hashed_codes = cache.get(f"backup_codes_{user.id}", [])
        
        for i, hashed_code in enumerate(hashed_codes):
            if check_password(code, hashed_code):
                # Remove used code
                hashed_codes.pop(i)
                cache.set(f"backup_codes_{user.id}", hashed_codes, 86400 * 30)
                return True
        
        return False


# Global instances
password_policy_service = PasswordPolicyService()
account_lockout_service = AccountLockoutService()
two_factor_auth_service = TwoFactorAuthService()