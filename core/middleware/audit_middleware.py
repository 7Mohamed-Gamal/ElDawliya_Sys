"""
Audit Middleware for automatic logging of all system activities
وسطاء التدقيق للتسجيل التلقائي لجميع أنشطة النظام
"""

import json
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse

from ..models.audit import AuditLog, SecurityEvent
from ..services.security_service import SecurityAnalyzer

logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware for comprehensive audit logging
    وسطاء التسجيل الشامل للتدقيق
    """

    def __init__(self, get_response):
        """__init__ function"""
        self.get_response = get_response
        self.security_analyzer = SecurityAnalyzer()

        # Configure which paths to exclude from logging
        self.excluded_paths = getattr(settings, 'AUDIT_EXCLUDED_PATHS', [
            '/static/',
            '/media/',
            '/favicon.ico',
            '/health/',
            '/metrics/',
        ])

        # Configure which methods to log
        self.logged_methods = getattr(settings, 'AUDIT_LOGGED_METHODS', [
            'POST', 'PUT', 'PATCH', 'DELETE'
        ])

        # Configure sensitive data fields to mask
        self.sensitive_fields = getattr(settings, 'AUDIT_SENSITIVE_FIELDS', [
            'password', 'token', 'secret', 'key', 'api_key', 'csrf_token'
        ])

        super().__init__(get_response)

    def __call__(self, request):
        """__call__ function"""
        # Record start time
        start_time = time.time()

        # Skip logging for excluded paths
        if self._should_skip_logging(request):
            return self.get_response(request)

        # Prepare request data
        request_data = self._prepare_request_data(request)

        # Get response
        response = self.get_response(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Log the request/response
        try:
            self._log_request_response(request, response, request_data, response_time)
        except Exception as e:
            logger.error(f"Error logging audit entry: {e}")

        return response

    def _should_skip_logging(self, request):
        """
        Determine if request should be skipped from logging
        تحديد ما إذا كان يجب تخطي الطلب من التسجيل
        """
        # Skip static files and excluded paths
        for excluded_path in self.excluded_paths:
            if request.path.startswith(excluded_path):
                return True

        # Skip GET requests unless configured otherwise
        if request.method == 'GET' and 'GET' not in self.logged_methods:
            return True

        # Skip if audit logging is disabled
        if not getattr(settings, 'ENABLE_AUDIT_LOGGING', True):
            return True

        return False

    def _prepare_request_data(self, request):
        """
        Prepare request data for logging
        إعداد بيانات الطلب للتسجيل
        """
        request_data = {}

        # Get request parameters
        if request.method == 'GET':
            request_data = dict(request.GET)
        elif request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.content_type == 'application/json':
                    request_data = json.loads(request.body.decode('utf-8'))
                else:
                    request_data = dict(request.POST)
            except (json.JSONDecodeError, UnicodeDecodeError):
                request_data = {'_raw_body': str(request.body)[:1000]}

        # Mask sensitive data
        request_data = self._mask_sensitive_data(request_data)

        return request_data

    def _mask_sensitive_data(self, data):
        """
        Mask sensitive data in request/response
        إخفاء البيانات الحساسة في الطلب/الاستجابة
        """
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if any(sensitive_field in key.lower() for sensitive_field in self.sensitive_fields):
                    masked_data[key] = '***MASKED***'
                elif isinstance(value, (dict, list)):
                    masked_data[key] = self._mask_sensitive_data(value)
                else:
                    masked_data[key] = value
            return masked_data
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        else:
            return data

    def _log_request_response(self, request, response, request_data, response_time):
        """
        Log the request and response
        تسجيل الطلب والاستجابة
        """
        # Determine action type
        action_type = self._determine_action_type(request, response)

        # Get user information
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key if hasattr(request, 'session') else None

        # Get client information
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        # Determine severity and security relevance
        severity = self._determine_severity(request, response)
        is_security_relevant = self._is_security_relevant(request, response)
        is_suspicious = self._is_suspicious_activity(request, response, user)

        # Create audit log entry
        try:
            with transaction.atomic():
                audit_log = AuditLog.objects.create(
                    user=user,
                    session_key=session_key,
                    action_type=action_type,
                    action_description=self._generate_action_description(request, response),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_method=request.method,
                    request_path=request.path,
                    request_data=request_data,
                    response_status=response.status_code,
                    response_time=response_time,
                    severity=severity,
                    is_suspicious=is_suspicious,
                    is_security_relevant=is_security_relevant,
                    module=self._determine_module(request),
                    tags=self._generate_tags(request, response),
                    additional_data={
                        'referer': request.META.get('HTTP_REFERER', ''),
                        'content_type': request.content_type,
                        'response_size': len(getattr(response, 'content', b'')),
                    }
                )

                # Analyze for security threats
                if is_security_relevant or is_suspicious:
                    self._analyze_security_threat(audit_log, request, response)

        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")

    def _determine_action_type(self, request, response):
        """
        Determine the action type based on request and response
        تحديد نوع الإجراء بناءً على الطلب والاستجابة
        """
        method = request.method.upper()
        path = request.path.lower()

        # Login/logout detection
        if 'login' in path:
            return 'login'
        elif 'logout' in path:
            return 'logout'

        # API access
        if path.startswith('/api/'):
            return 'api_access'

        # CRUD operations
        if method == 'POST':
            return 'create'
        elif method == 'GET':
            return 'read'
        elif method in ['PUT', 'PATCH']:
            return 'update'
        elif method == 'DELETE':
            return 'delete'

        # Export/import operations
        if 'export' in path:
            return 'export'
        elif 'import' in path:
            return 'import'

        # Default
        return 'read'

    def _determine_severity(self, request, response):
        """
        Determine severity level of the action
        تحديد مستوى خطورة الإجراء
        """
        # Critical for failed authentication
        if response.status_code == 401:
            return 'critical'

        # High for server errors
        if response.status_code >= 500:
            return 'high'

        # Medium for client errors
        if response.status_code >= 400:
            return 'medium'

        # High for sensitive operations
        if request.method in ['DELETE'] or 'admin' in request.path:
            return 'high'

        # Medium for write operations
        if request.method in ['POST', 'PUT', 'PATCH']:
            return 'medium'

        # Low for read operations
        return 'low'

    def _is_security_relevant(self, request, response):
        """
        Check if the action is security-relevant
        التحقق من كون الإجراء متعلقاً بالأمان
        """
        security_paths = [
            '/admin/', '/api/', '/login', '/logout',
            '/permissions/', '/users/', '/roles/'
        ]

        # Check path
        if any(path in request.path for path in security_paths):
            return True

        # Check for authentication failures
        if response.status_code in [401, 403]:
            return True

        # Check for sensitive operations
        if request.method in ['DELETE'] and response.status_code < 400:
            return True

        return False

    def _is_suspicious_activity(self, request, response, user):
        """
        Detect suspicious activity patterns
        اكتشاف أنماط النشاط المشبوه
        """
        # Failed login attempts
        if 'login' in request.path and response.status_code >= 400:
            return True

        # Multiple rapid requests from same IP
        ip_address = self._get_client_ip(request)
        recent_requests = AuditLog.objects.filter(
            ip_address=ip_address,
            timestamp__gte=timezone.now().timedelta(minutes=1)
        ).count()

        if recent_requests > 20:  # More than 20 requests per minute
            return True

        # Access to admin areas by non-staff users
        if '/admin/' in request.path and user and not user.is_staff:
            return True

        # Unusual user agent patterns
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['bot', 'crawler', 'scanner', 'curl', 'wget']
        if any(agent in user_agent for agent in suspicious_agents):
            return True

        return False

    def _generate_action_description(self, request, response):
        """
        Generate human-readable action description
        توليد وصف مقروء للإجراء
        """
        method = request.method
        path = request.path
        status = response.status_code

        if method == 'GET':
            return f"عرض الصفحة {path}"
        elif method == 'POST':
            return f"إنشاء بيانات في {path}"
        elif method in ['PUT', 'PATCH']:
            return f"تحديث بيانات في {path}"
        elif method == 'DELETE':
            return f"حذف بيانات من {path}"

        return f"{method} {path} - الحالة: {status}"

    def _determine_module(self, request):
        """
        Determine which module the request belongs to
        تحديد الوحدة التي ينتمي إليها الطلب
        """
        path = request.path.lower()

        if path.startswith('/api/v1/hr/'):
            return 'hr'
        elif path.startswith('/api/v1/inventory/'):
            return 'inventory'
        elif path.startswith('/api/v1/projects/'):
            return 'projects'
        elif path.startswith('/api/v1/procurement/'):
            return 'procurement'
        elif path.startswith('/api/v1/finance/'):
            return 'finance'
        elif path.startswith('/admin/'):
            return 'administration'
        elif path.startswith('/api/'):
            return 'api'

        # Try to determine from URL patterns
        path_parts = path.strip('/').split('/')
        if path_parts:
            return path_parts[0]

        return 'unknown'

    def _generate_tags(self, request, response):
        """
        Generate tags for categorizing the audit log
        توليد العلامات لتصنيف سجل التدقيق
        """
        tags = []

        # Add method tag
        tags.append(f"method:{request.method.lower()}")

        # Add status code category
        if response.status_code < 300:
            tags.append("success")
        elif response.status_code < 400:
            tags.append("redirect")
        elif response.status_code < 500:
            tags.append("client_error")
        else:
            tags.append("server_error")

        # Add authentication status
        if request.user.is_authenticated:
            tags.append("authenticated")
        else:
            tags.append("anonymous")

        # Add API tag
        if request.path.startswith('/api/'):
            tags.append("api")

        # Add mobile tag
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone']):
            tags.append("mobile")

        return tags

    def _analyze_security_threat(self, audit_log, request, response):
        """
        Analyze potential security threats
        تحليل التهديدات الأمنية المحتملة
        """
        try:
            threat_analysis = self.security_analyzer.analyze_request(
                audit_log, request, response
            )

            if threat_analysis and threat_analysis.get('is_threat'):
                # Create security event
                SecurityEvent.objects.create(
                    event_type=threat_analysis.get('threat_type', 'suspicious_activity'),
                    threat_level=threat_analysis.get('threat_level', 'medium'),
                    title=threat_analysis.get('title', 'Suspicious Activity Detected'),
                    description=threat_analysis.get('description', ''),
                    source_ip=audit_log.ip_address,
                    source_user_agent=audit_log.user_agent,
                    target_user=audit_log.user,
                    target_endpoint=audit_log.request_path,
                    detected_by='audit_middleware',
                    detection_method='pattern_analysis',
                    confidence_score=threat_analysis.get('confidence', 0.5),
                    evidence=threat_analysis.get('evidence', {}),
                )

        except Exception as e:
            logger.error(f"Error analyzing security threat: {e}")

    def _get_client_ip(self, request):
        """
        Get client IP address from request
        الحصول على عنوان IP للعميل من الطلب
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware for additional security monitoring
    وسطاء للمراقبة الأمنية الإضافية
    """

    def __init__(self, get_response):
        """__init__ function"""
        self.get_response = get_response
        self.security_analyzer = SecurityAnalyzer()
        super().__init__(get_response)

    def __call__(self, request):
        """__call__ function"""
        # Pre-request security checks
        security_check = self._pre_request_security_check(request)
        if security_check:
            return security_check

        response = self.get_response(request)

        # Post-request security analysis
        self._post_request_security_analysis(request, response)

        return response

    def _pre_request_security_check(self, request):
        """
        Perform security checks before processing request
        إجراء فحوصات أمنية قبل معالجة الطلب
        """
        # Check for blocked IPs
        ip_address = self._get_client_ip(request)
        if self._is_ip_blocked(ip_address):
            logger.warning(f"Blocked IP attempted access: {ip_address}")
            return JsonResponse({'error': 'Access denied'}, status=403)

        # Check for rate limiting
        if self._is_rate_limited(request):
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            return JsonResponse({'error': 'Rate limit exceeded'}, status=429)

        # Check for malicious patterns
        if self._contains_malicious_patterns(request):
            logger.warning(f"Malicious pattern detected from IP: {ip_address}")
            return JsonResponse({'error': 'Request blocked'}, status=400)

        return None

    def _post_request_security_analysis(self, request, response):
        """
        Analyze request/response for security issues
        تحليل الطلب/الاستجابة للمشاكل الأمنية
        """
        # This would contain additional security analysis logic
        pass

    def _is_ip_blocked(self, ip_address):
        """Check if IP is in blocklist"""
        # Implementation would check against a blocklist
        return False

    def _is_rate_limited(self, request):
        """Check if request should be rate limited"""
        # Implementation would check rate limits
        return False

    def _contains_malicious_patterns(self, request):
        """Check for malicious patterns in request"""
        # Implementation would check for SQL injection, XSS, etc.
        return False

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
