"""
Enhanced authentication classes for API with JWT and API key support
فئات المصادقة المحسنة لـ API مع دعم JWT ومفاتيح API
"""

import logging
import hashlib
import hmac
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import APIKey

User = get_user_model()
logger = logging.getLogger(__name__)


class EnhancedAPIKeyAuthentication(authentication.BaseAuthentication):
    """
    Enhanced API key authentication with security features
    مصادقة مفتاح API محسنة مع ميزات الأمان
    """
    keyword = 'ApiKey'

    def authenticate(self, request):
        """
        Authenticate the request using API key with enhanced security
        """
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header or auth_header[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth_header) == 1:
            msg = 'مفتاح API غير صحيح. لم يتم توفير بيانات الاعتماد.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth_header) > 2:
            msg = 'مفتاح API غير صحيح. يجب ألا يحتوي مفتاح API على مسافات.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            api_key = auth_header[1].decode()
        except UnicodeError:
            msg = 'مفتاح API غير صحيح. يحتوي على أحرف غير صالحة.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(api_key, request)

    def authenticate_credentials(self, key, request):
        """
        Authenticate the API key with enhanced security checks
        """
        # Check rate limiting for failed attempts
        client_ip = self.get_client_ip(request)
        failed_attempts_key = f"api_auth_failed_{client_ip}"
        failed_attempts = cache.get(failed_attempts_key, 0)

        if failed_attempts >= 5:  # Max 5 failed attempts per hour
            raise exceptions.AuthenticationFailed(
                'تم تجاوز الحد الأقصى لمحاولات المصادقة الفاشلة. حاول مرة أخرى لاحقاً.'
            )

        try:
            api_key_obj = APIKey.objects.select_related('user').get(
                key=key,
                is_active=True
            )
        except APIKey.DoesNotExist:
            # Increment failed attempts
            cache.set(failed_attempts_key, failed_attempts + 1, 3600)
            logger.warning(f"Invalid API key attempt from IP: {client_ip}")
            raise exceptions.AuthenticationFailed('مفتاح API غير صحيح.')

        # Check if API key is expired
        if api_key_obj.is_expired():
            raise exceptions.AuthenticationFailed('انتهت صلاحية مفتاح API.')

        # Check if user is active
        if not api_key_obj.user.is_active:
            raise exceptions.AuthenticationFailed('حساب المستخدم معطل.')

        # Check IP restrictions if configured
        if hasattr(api_key_obj, 'allowed_ips') and api_key_obj.allowed_ips:
            if client_ip not in api_key_obj.allowed_ips.split(','):
                logger.warning(f"API key access denied for IP: {client_ip}")
                raise exceptions.AuthenticationFailed('الوصول مرفوض من هذا العنوان.')

        # Check usage limits
        if not self.check_usage_limits(api_key_obj):
            raise exceptions.AuthenticationFailed('تم تجاوز حد الاستخدام لمفتاح API.')

        # Update last used timestamp and usage count
        api_key_obj.last_used = timezone.now()
        api_key_obj.save(update_fields=['last_used'])

        # Clear failed attempts on successful auth
        cache.delete(failed_attempts_key)

        # Store API key in request for logging and throttling
        request.api_key = api_key_obj

        # Log successful authentication
        logger.info(f"Successful API key authentication for user: {api_key_obj.user.username}")

        return (api_key_obj.user, api_key_obj)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def check_usage_limits(self, api_key_obj):
        """Check if API key has exceeded usage limits"""
        if not hasattr(api_key_obj, 'daily_limit') or not api_key_obj.daily_limit:
            return True

        # Check daily usage
        today = timezone.now().date()
        usage_key = f"api_usage_{api_key_obj.key}_{today}"
        current_usage = cache.get(usage_key, 0)

        if current_usage >= api_key_obj.daily_limit:
            return False

        # Increment usage counter
        cache.set(usage_key, current_usage + 1, 86400)  # 24 hours
        return True

    def authenticate_header(self, request):
        """Return authentication header"""
        return self.keyword


class EnhancedJWTAuthentication(JWTAuthentication):
    """
    Enhanced JWT authentication with additional security features
    مصادقة JWT محسنة مع ميزات أمان إضافية
    """

    def authenticate(self, request):
        """
        Authenticate with enhanced JWT validation
        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        # Check if token is blacklisted
        if self.is_token_blacklisted(raw_token):
            raise exceptions.AuthenticationFailed('الرمز المميز في القائمة السوداء.')

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        # Additional security checks
        if not self.validate_token_security(validated_token, request):
            raise exceptions.AuthenticationFailed('فشل في التحقق من أمان الرمز المميز.')

        # Store token info in request
        request.jwt_token = validated_token

        return user, validated_token

    def is_token_blacklisted(self, raw_token):
        """Check if token is in blacklist"""
        token_hash = hashlib.sha256(raw_token).hexdigest()
        blacklist_key = f"jwt_blacklist_{token_hash}"
        return cache.get(blacklist_key, False)

    def validate_token_security(self, validated_token, request):
        """Additional security validation for JWT token"""
        # Check if token was issued from same IP (optional)
        if hasattr(validated_token, 'payload'):
            token_ip = validated_token.payload.get('ip')
            current_ip = self.get_client_ip(request)

            # If IP checking is enabled and IPs don't match
            if token_ip and getattr(settings, 'JWT_CHECK_IP', False):
                if token_ip != current_ip:
                    logger.warning(f"JWT token IP mismatch. Token IP: {token_ip}, Current IP: {current_ip}")
                    return False

        return True

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SignatureAuthentication(authentication.BaseAuthentication):
    """
    HMAC signature-based authentication for high-security endpoints
    مصادقة قائمة على توقيع HMAC لنقاط النهاية عالية الأمان
    """

    def authenticate(self, request):
        """
        Authenticate using HMAC signature
        """
        # Get signature from headers
        signature = request.META.get('HTTP_X_SIGNATURE')
        timestamp = request.META.get('HTTP_X_TIMESTAMP')
        api_key = request.META.get('HTTP_X_API_KEY')

        if not all([signature, timestamp, api_key]):
            return None

        # Check timestamp (prevent replay attacks)
        try:
            request_time = int(timestamp)
            current_time = int(timezone.now().timestamp())

            if abs(current_time - request_time) > 300:  # 5 minutes tolerance
                raise exceptions.AuthenticationFailed('الطلب منتهي الصلاحية.')
        except ValueError:
            raise exceptions.AuthenticationFailed('طابع زمني غير صحيح.')

        # Get API key object
        try:
            api_key_obj = APIKey.objects.select_related('user').get(
                key=api_key,
                is_active=True
            )
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('مفتاح API غير صحيح.')

        # Verify signature
        if not self.verify_signature(request, api_key_obj.secret_key, signature):
            raise exceptions.AuthenticationFailed('توقيع غير صحيح.')

        return (api_key_obj.user, api_key_obj)

    def verify_signature(self, request, secret_key, provided_signature):
        """
        Verify HMAC signature
        """
        # Create message to sign
        method = request.method
        path = request.path
        timestamp = request.META.get('HTTP_X_TIMESTAMP')
        body = request.body.decode('utf-8') if request.body else ''

        message = f"{method}\n{path}\n{timestamp}\n{body}"

        # Calculate expected signature
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Compare signatures securely
        return hmac.compare_digest(expected_signature, provided_signature)


class MultiFactorAuthentication(authentication.BaseAuthentication):
    """
    Multi-factor authentication for sensitive operations
    مصادقة متعددة العوامل للعمليات الحساسة
    """

    def authenticate(self, request):
        """
        Require additional authentication factor
        """
        # First, check if user is already authenticated
        if not request.user or not request.user.is_authenticated:
            return None

        # Check if MFA is required for this endpoint
        if not self.requires_mfa(request):
            return None

        # Get MFA token from header
        mfa_token = request.META.get('HTTP_X_MFA_TOKEN')
        if not mfa_token:
            raise exceptions.AuthenticationFailed('مطلوب رمز المصادقة الثنائية.')

        # Verify MFA token
        if not self.verify_mfa_token(request.user, mfa_token):
            raise exceptions.AuthenticationFailed('رمز المصادقة الثنائية غير صحيح.')

        return (request.user, None)

    def requires_mfa(self, request):
        """
        Check if endpoint requires MFA
        """
        sensitive_endpoints = [
            '/api/v1/admin/',
            '/api/v1/users/',
            '/api/v1/api-keys/',
            '/api/v1/export/',
        ]

        return any(request.path.startswith(endpoint) for endpoint in sensitive_endpoints)

    def verify_mfa_token(self, user, token):
        """
        Verify MFA token (simplified implementation)
        """
        # This is a simplified implementation
        # In production, you would integrate with TOTP, SMS, or other MFA providers
        stored_token_key = f"mfa_token_{user.id}"
        stored_token = cache.get(stored_token_key)

        if stored_token and stored_token == token:
            # Remove token after use
            cache.delete(stored_token_key)
            return True

        return False


class CombinedAuthentication(authentication.BaseAuthentication):
    """
    Combined authentication that tries multiple methods
    مصادقة مجمعة تجرب طرق متعددة
    """

    def authenticate(self, request):
        """
        Try multiple authentication methods in order
        """
        # Try JWT authentication first
        jwt_auth = EnhancedJWTAuthentication()
        try:
            result = jwt_auth.authenticate(request)
            if result:
                return result
        except exceptions.AuthenticationFailed:
            pass

        # Try API key authentication
        api_key_auth = EnhancedAPIKeyAuthentication()
        try:
            result = api_key_auth.authenticate(request)
            if result:
                return result
        except exceptions.AuthenticationFailed:
            pass

        # Try session authentication for web interface
        session_auth = authentication.SessionAuthentication()
        try:
            result = session_auth.authenticate(request)
            if result:
                return result
        except exceptions.AuthenticationFailed:
            pass

        return None

    def authenticate_header(self, request):
        """
        Return authentication header
        """
        return 'Bearer, ApiKey'


# Legacy alias for backward compatibility
APIKeyAuthentication = EnhancedAPIKeyAuthentication
