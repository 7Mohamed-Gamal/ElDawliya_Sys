"""
Enhanced Security Middleware
وسطاء الأمان المحسن

This middleware provides comprehensive security features including
session management, CSRF protection, rate limiting, and threat detection.
"""

import time
import logging
import hashlib
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.urls import resolve
from django.views.decorators.csrf import csrf_exempt

from ..services.secure_config import environment_config_manager
from ..services.security_service import SecurityAnalyzer, ThreatIntelligence

logger = logging.getLogger(__name__)


class EnhancedSessionMiddleware(MiddlewareMixin):
    """
    Enhanced session middleware with security features
    وسطاء الجلسة المحسن مع ميزات الأمان
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.session_timeout = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 30) * 60
        self.max_sessions_per_user = getattr(settings, 'MAX_SESSIONS_PER_USER', 5)
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process request for session security"""
        if not hasattr(request, 'session'):
            return None
        
        # Check session validity
        if not self._is_session_valid(request):
            self._invalidate_session(request)
            return None
        
        # Update session activity
        self._update_session_activity(request)
        
        # Check for session hijacking
        if self._detect_session_hijacking(request):
            logger.warning(f"Potential session hijacking detected for session: {request.session.session_key}")
            self._invalidate_session(request)
            return HttpResponseForbidden("Session security violation detected")
        
        # Enforce concurrent session limits
        if request.user.is_authenticated:
            self._enforce_session_limits(request)
        
        return None
    
    def _is_session_valid(self, request) -> bool:
        """
        Check if session is valid and not expired
        التحقق من صحة الجلسة وعدم انتهاء صلاحيتها
        """
        if not request.session.session_key:
            return True  # New session
        
        # Check session expiry
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            if timezone.now() - last_activity_time > timedelta(seconds=self.session_timeout):
                return False
        
        # Check if session exists in database
        try:
            Session.objects.get(session_key=request.session.session_key)
            return True
        except Session.DoesNotExist:
            return False
    
    def _update_session_activity(self, request):
        """
        Update session activity timestamp
        تحديث طابع وقت نشاط الجلسة
        """
        request.session['last_activity'] = timezone.now().isoformat()
        
        # Store additional security metadata
        if not request.session.get('created_at'):
            request.session['created_at'] = timezone.now().isoformat()
        
        request.session['ip_address'] = self._get_client_ip(request)
        request.session['user_agent_hash'] = hashlib.sha256(
            request.META.get('HTTP_USER_AGENT', '').encode()
        ).hexdigest()[:16]
    
    def _detect_session_hijacking(self, request) -> bool:
        """
        Detect potential session hijacking
        اكتشاف اختطاف الجلسة المحتمل
        """
        if not request.session.session_key:
            return False
        
        # Check IP address consistency
        stored_ip = request.session.get('ip_address')
        current_ip = self._get_client_ip(request)
        
        if stored_ip and stored_ip != current_ip:
            # Allow IP changes for mobile users with some tolerance
            if not self._is_ip_change_allowed(stored_ip, current_ip):
                return True
        
        # Check User-Agent consistency
        stored_ua_hash = request.session.get('user_agent_hash')
        current_ua_hash = hashlib.sha256(
            request.META.get('HTTP_USER_AGENT', '').encode()
        ).hexdigest()[:16]
        
        if stored_ua_hash and stored_ua_hash != current_ua_hash:
            return True
        
        return False
    
    def _is_ip_change_allowed(self, old_ip: str, new_ip: str) -> bool:
        """
        Check if IP address change is allowed
        التحقق من السماح بتغيير عنوان IP
        """
        # Allow changes within same subnet for mobile users
        try:
            import ipaddress
            old_network = ipaddress.ip_network(f"{old_ip}/24", strict=False)
            new_ip_obj = ipaddress.ip_address(new_ip)
            return new_ip_obj in old_network
        except ValueError:
            return False
    
    def _enforce_session_limits(self, request):
        """
        Enforce concurrent session limits per user
        فرض حدود الجلسات المتزامنة لكل مستخدم
        """
        if not request.user.is_authenticated:
            return
        
        # Get all active sessions for user
        user_sessions = Session.objects.filter(
            expire_date__gt=timezone.now()
        )
        
        active_sessions = []
        for session in user_sessions:
            session_data = session.get_decoded()
            if session_data.get('_auth_user_id') == str(request.user.id):
                active_sessions.append(session)
        
        # Remove oldest sessions if limit exceeded
        if len(active_sessions) > self.max_sessions_per_user:
            sessions_to_remove = sorted(
                active_sessions, 
                key=lambda s: s.expire_date
            )[:-self.max_sessions_per_user]
            
            for session in sessions_to_remove:
                session.delete()
                logger.info(f"Removed old session for user {request.user.username}")
    
    def _invalidate_session(self, request):
        """
        Invalidate current session
        إبطال الجلسة الحالية
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            logout(request)
        
        request.session.flush()
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CSRFEnhancementMiddleware(MiddlewareMixin):
    """
    Enhanced CSRF protection middleware
    وسطاء حماية CSRF المحسن
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = getattr(settings, 'CSRF_EXEMPT_PATHS', [])
        super().__init__(get_response)
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Enhanced CSRF validation"""
        # Skip if path is exempt
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return None
        
        # Skip if view is explicitly exempt
        if getattr(view_func, 'csrf_exempt', False):
            return None
        
        # Additional CSRF checks for sensitive operations
        if self._is_sensitive_operation(request):
            if not self._validate_enhanced_csrf(request):
                logger.warning(f"Enhanced CSRF validation failed for {request.path}")
                return JsonResponse({'error': 'CSRF validation failed'}, status=403)
        
        return None
    
    def _is_sensitive_operation(self, request) -> bool:
        """
        Check if request is for sensitive operation
        التحقق من كون الطلب لعملية حساسة
        """
        sensitive_paths = [
            '/admin/', '/api/v1/users/', '/api/v1/permissions/',
            '/api/v1/roles/', '/api/v1/export/', '/api/v1/import/'
        ]
        
        return (
            request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and
            any(request.path.startswith(path) for path in sensitive_paths)
        )
    
    def _validate_enhanced_csrf(self, request) -> bool:
        """
        Enhanced CSRF validation for sensitive operations
        التحقق المحسن من CSRF للعمليات الحساسة
        """
        # Check for custom CSRF header
        csrf_header = request.META.get('HTTP_X_CSRF_TOKEN')
        if not csrf_header:
            return False
        
        # Validate CSRF token format and timing
        try:
            from django.middleware.csrf import get_token
            expected_token = get_token(request)
            
            # Simple timing-safe comparison
            import hmac
            return hmac.compare_digest(csrf_header, expected_token)
        except Exception:
            return False


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware with multiple strategies
    وسطاء تحديد المعدل مع استراتيجيات متعددة
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limits = self._load_rate_limits()
        super().__init__(get_response)
    
    def _load_rate_limits(self) -> Dict[str, Dict[str, int]]:
        """Load rate limiting configuration"""
        return {
            'global': {
                'requests_per_minute': 60,
                'burst': 10
            },
            'api': {
                'requests_per_minute': 100,
                'requests_per_hour': 1000
            },
            'auth': {
                'requests_per_minute': 10,
                'requests_per_hour': 50
            },
            'admin': {
                'requests_per_minute': 30,
                'requests_per_hour': 200
            }
        }
    
    def process_request(self, request):
        """Apply rate limiting"""
        if not getattr(settings, 'ENABLE_RATE_LIMITING', True):
            return None
        
        # Determine rate limit category
        category = self._get_rate_limit_category(request)
        
        # Check rate limits
        if not self._check_rate_limit(request, category):
            logger.warning(f"Rate limit exceeded for {self._get_client_ip(request)} on {request.path}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'تم تجاوز الحد المسموح من الطلبات'
            }, status=429)
        
        return None
    
    def _get_rate_limit_category(self, request) -> str:
        """
        Determine rate limit category for request
        تحديد فئة تحديد المعدل للطلب
        """
        path = request.path.lower()
        
        if path.startswith('/api/'):
            return 'api'
        elif path.startswith('/admin/'):
            return 'admin'
        elif any(auth_path in path for auth_path in ['/login', '/logout', '/register']):
            return 'auth'
        else:
            return 'global'
    
    def _check_rate_limit(self, request, category: str) -> bool:
        """
        Check if request is within rate limits
        التحقق من كون الطلب ضمن حدود المعدل
        """
        client_ip = self._get_client_ip(request)
        user_id = request.user.id if request.user.is_authenticated else None
        
        # Create cache keys
        ip_key = f"rate_limit_{category}_{client_ip}"
        user_key = f"rate_limit_{category}_user_{user_id}" if user_id else None
        
        limits = self.rate_limits.get(category, self.rate_limits['global'])
        
        # Check per-minute limit
        if 'requests_per_minute' in limits:
            if not self._check_limit(ip_key + '_minute', limits['requests_per_minute'], 60):
                return False
            
            if user_key and not self._check_limit(user_key + '_minute', limits['requests_per_minute'], 60):
                return False
        
        # Check per-hour limit
        if 'requests_per_hour' in limits:
            if not self._check_limit(ip_key + '_hour', limits['requests_per_hour'], 3600):
                return False
            
            if user_key and not self._check_limit(user_key + '_hour', limits['requests_per_hour'], 3600):
                return False
        
        return True
    
    def _check_limit(self, cache_key: str, limit: int, window: int) -> bool:
        """
        Check individual rate limit
        التحقق من حد المعدل الفردي
        """
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return False
        
        # Increment counter
        try:
            cache.set(cache_key, current_count + 1, window)
        except Exception:
            # If cache fails, allow request but log error
            logger.error(f"Failed to update rate limit cache for {cache_key}")
        
        return True
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ThreatDetectionMiddleware(MiddlewareMixin):
    """
    Real-time threat detection middleware
    وسطاء اكتشاف التهديدات في الوقت الفعلي
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.security_analyzer = SecurityAnalyzer()
        self.threat_intelligence = ThreatIntelligence()
        super().__init__(get_response)
    
    def process_request(self, request):
        """Analyze request for threats"""
        # Check IP reputation
        client_ip = self._get_client_ip(request)
        ip_reputation = self.threat_intelligence.check_ip_reputation(client_ip)
        
        if ip_reputation['is_malicious']:
            logger.warning(f"Malicious IP detected: {client_ip}")
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Check for malicious patterns in request
        if self._contains_malicious_patterns(request):
            logger.warning(f"Malicious patterns detected in request from {client_ip}")
            return JsonResponse({'error': 'Request blocked'}, status=400)
        
        # Check for suspicious user agent
        if self._is_suspicious_user_agent(request):
            logger.info(f"Suspicious user agent from {client_ip}: {request.META.get('HTTP_USER_AGENT', '')}")
            # Don't block, but log for analysis
        
        return None
    
    def _contains_malicious_patterns(self, request) -> bool:
        """
        Check for malicious patterns in request
        التحقق من الأنماط الخبيثة في الطلب
        """
        # Check URL for malicious patterns
        malicious_url_patterns = [
            '../', '..\\', '/etc/passwd', '/proc/', 'cmd.exe',
            '<script', 'javascript:', 'vbscript:', 'onload=',
            'union select', 'drop table', 'insert into'
        ]
        
        url_lower = request.path.lower()
        query_lower = request.META.get('QUERY_STRING', '').lower()
        
        for pattern in malicious_url_patterns:
            if pattern in url_lower or pattern in query_lower:
                return True
        
        # Check request body for malicious content
        if hasattr(request, 'body') and request.body:
            try:
                body_str = request.body.decode('utf-8', errors='ignore').lower()
                for pattern in malicious_url_patterns:
                    if pattern in body_str:
                        return True
            except Exception:
                pass
        
        return False
    
    def _is_suspicious_user_agent(self, request) -> bool:
        """
        Check if user agent is suspicious
        التحقق من كون وكيل المستخدم مشبوه
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        suspicious_agents = [
            'bot', 'crawler', 'spider', 'scraper', 'scanner',
            'curl', 'wget', 'python-requests', 'libwww-perl'
        ]
        
        return any(agent in user_agent for agent in suspicious_agents)
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Security headers middleware
    وسطاء رؤوس الأمان
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.security_headers = environment_config_manager.get_security_headers()
        super().__init__(get_response)
    
    def process_response(self, request, response):
        """Add security headers to response"""
        for header, value in self.security_headers.items():
            response[header] = value
        
        return response


class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """
    Content Security Policy middleware
    وسطاء سياسة أمان المحتوى
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.csp_config = self._load_csp_config()
        super().__init__(get_response)
    
    def _load_csp_config(self) -> Dict[str, str]:
        """Load CSP configuration"""
        return {
            'default-src': "'self'",
            'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
            'style-src': "'self' 'unsafe-inline'",
            'img-src': "'self' data: https:",
            'font-src': "'self' https:",
            'connect-src': "'self'",
            'frame-ancestors': "'none'",
            'base-uri': "'self'",
            'form-action': "'self'",
        }
    
    def process_response(self, request, response):
        """Add CSP header to response"""
        if environment_config_manager.security_config.csp_enabled:
            csp_directives = []
            for directive, sources in self.csp_config.items():
                csp_directives.append(f"{directive} {sources}")
            
            csp_header = '; '.join(csp_directives)
            response['Content-Security-Policy'] = csp_header
        
        return response


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Additional session security features
    ميزات أمان الجلسة الإضافية
    """
    
    def process_response(self, request, response):
        """Apply session security measures"""
        if hasattr(request, 'session') and request.session.session_key:
            # Regenerate session ID periodically
            if self._should_regenerate_session(request):
                request.session.cycle_key()
            
            # Set secure session cookie attributes
            if hasattr(response, 'cookies'):
                session_cookie_name = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
                if session_cookie_name in response.cookies:
                    cookie = response.cookies[session_cookie_name]
                    
                    # Apply security attributes
                    cookie['secure'] = environment_config_manager.security_config.session_cookie_secure
                    cookie['httponly'] = environment_config_manager.security_config.session_cookie_httponly
                    cookie['samesite'] = environment_config_manager.security_config.session_cookie_samesite
        
        return response
    
    def _should_regenerate_session(self, request) -> bool:
        """
        Check if session ID should be regenerated
        التحقق من ضرورة إعادة توليد معرف الجلسة
        """
        # Regenerate session ID every hour for security
        last_regeneration = request.session.get('last_regeneration')
        if not last_regeneration:
            request.session['last_regeneration'] = timezone.now().isoformat()
            return True
        
        last_regen_time = datetime.fromisoformat(last_regeneration)
        if timezone.now() - last_regen_time > timedelta(hours=1):
            request.session['last_regeneration'] = timezone.now().isoformat()
            return True
        
        return False