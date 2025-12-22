"""
وسطاء التدقيق والمراجعة
Audit Middleware for tracking user activities
"""
import time
import json
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from core.models.audit import AuditLog


class AuditMiddleware(MiddlewareMixin):
    """
    وسطاء المراجعة والتدقيق
    Middleware for auditing user actions and system activities
    """

    # URLs to exclude from audit logging
    EXCLUDED_PATHS = [
        '/static/',
        '/media/',
        '/favicon.ico',
        '/admin/jsi18n/',
        '/api/health/',
    ]

    # HTTP methods to audit
    AUDITED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

    def process_request(self, request):
        """Process incoming request"""
        request._audit_start_time = time.time()
        return None

    def process_response(self, request, response):
        """Process outgoing response"""
        # Skip if path should be excluded
        if self._should_exclude_path(request.path):
            return response

        # Skip if method should not be audited
        if request.method not in self.AUDITED_METHODS:
            return response

        # Calculate request duration
        duration = None
        if hasattr(request, '_audit_start_time'):
            duration = time.time() - request._audit_start_time

        # Determine result based on status code
        result = 'success' if 200 <= response.status_code < 400 else 'failure'

        # Get request data
        request_data = self._get_request_data(request)

        # Create audit log entry
        try:
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action=self._get_action_from_method(request.method),
                resource=request.path,
                details={
                    'method': request.method,
                    'status_code': response.status_code,
                    'duration': duration,
                    'request_data': request_data,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'referer': request.META.get('HTTP_REFERER', ''),
                },
                result=result,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_key=getattr(request.session, 'session_key', None),
                duration=duration,
            )
        except Exception as e:
            # Don't let audit logging break the application
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create audit log: {e}")

        return response

    def process_exception(self, request, exception):
        """Process exceptions"""
        # Skip if path should be excluded
        if self._should_exclude_path(request.path):
            return None

        # Calculate request duration
        duration = None
        if hasattr(request, '_audit_start_time'):
            duration = time.time() - request._audit_start_time

        # Get request data
        request_data = self._get_request_data(request)

        # Create audit log entry for exception
        try:
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action=self._get_action_from_method(request.method),
                resource=request.path,
                details={
                    'method': request.method,
                    'exception': str(exception),
                    'exception_type': type(exception).__name__,
                    'duration': duration,
                    'request_data': request_data,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'referer': request.META.get('HTTP_REFERER', ''),
                },
                result='failure',
                message=str(exception),
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_key=getattr(request.session, 'session_key', None),
                duration=duration,
            )
        except Exception as e:
            # Don't let audit logging break the application
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create audit log for exception: {e}")

        return None

    def _should_exclude_path(self, path):
        """Check if path should be excluded from audit"""
        return any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS)

    def _get_action_from_method(self, method):
        """Get action name from HTTP method"""
        method_mapping = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
            'GET': 'read',
        }
        return method_mapping.get(method, method.lower())

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _get_request_data(self, request):
        """Get request data for logging"""
        data = {}

        try:
            # Get POST data
            if request.method == 'POST' and request.POST:
                data['POST'] = dict(request.POST)
                # Remove sensitive fields
                self._remove_sensitive_data(data['POST'])

            # Get GET parameters
            if request.GET:
                data['GET'] = dict(request.GET)

            # Get JSON data for PUT/PATCH requests
            if request.method in ['PUT', 'PATCH'] and hasattr(request, 'body'):
                try:
                    json_data = json.loads(request.body)
                    if isinstance(json_data, dict):
                        self._remove_sensitive_data(json_data)
                        data['JSON'] = json_data
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass

        except Exception:
            # If we can't parse the data, just skip it
            pass

        return data

    def _remove_sensitive_data(self, data):
        """Remove sensitive data from request data"""
        sensitive_fields = [
            'password', 'password1', 'password2', 'old_password', 'new_password',
            'csrfmiddlewaretoken', 'api_key', 'secret', 'token', 'auth_token',
            'credit_card', 'ssn', 'social_security', 'bank_account'
        ]

        if isinstance(data, dict):
            for field in sensitive_fields:
                if field in data:
                    data[field] = '[REDACTED]'

                # Also check for fields containing sensitive keywords
                for key in list(data.keys()):
                    if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'token']):
                        data[key] = '[REDACTED]'
