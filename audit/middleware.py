import json
import re
import logging
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from .models import AuditLog

logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log user actions for audit purposes.
    """
    
    # List of URL patterns to exclude from audit logging
    EXCLUDED_URLS = [
        r'^/static/',
        r'^/media/',
        r'^/favicon.ico$',
        r'^/__debug__/',  # Django Debug Toolbar
        r'^/admin/jsi18n/',
    ]
    
    # List of view names to exclude from audit logging (keep this configurable)
    EXCLUDED_VIEWS = [
        'admin:jsi18n',
    ]
    
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.excluded_urls_regex = [re.compile(pattern) for pattern in self.EXCLUDED_URLS]
        super().__init__(get_response)
    
    def is_excluded_path(self, path):
        """Check if the current path should be excluded from logging."""
        for pattern in self.excluded_urls_regex:
            if pattern.match(path):
                return True
        return False
    
    def process_request(self, request):
        """Store the initial request time and data."""
        # Skip excluded paths
        if self.is_excluded_path(request.path):
            return None
            
        # Store request method for later use
        request.audit_request_method = request.method
        
        # For POST/PUT/PATCH, store a copy of the request data
        if request.method in ('POST', 'PUT', 'PATCH') and hasattr(request, 'body'):
            try:
                # Store request body for later comparison
                if request.content_type and 'application/json' in request.content_type:
                    request.audit_request_data = json.loads(request.body)
                else:
                    request.audit_request_data = request.POST.dict()
            except Exception as e:
                logger.warning(f"Could not parse request body for audit: {e}")
                request.audit_request_data = {}
                
        return None
    
    def process_response(self, request, response):
        """Process the response and log the action."""
        # Skip logging for excluded paths
        if self.is_excluded_path(request.path) or not hasattr(request, 'audit_request_method'):
            return response
            
        # Try to determine the action type based on request method
        if request.audit_request_method == 'GET':
            action = AuditLog.VIEW
        elif request.audit_request_method == 'POST':
            action = AuditLog.CREATE
        elif request.audit_request_method in ('PUT', 'PATCH'):
            action = AuditLog.UPDATE
        elif request.audit_request_method == 'DELETE':
            action = AuditLog.DELETE
        else:
            action = AuditLog.OTHER
            
        # Try to get the view information
        try:
            resolver_match = resolve(request.path)
            view_name = f"{resolver_match.app_name}:{resolver_match.url_name}" if resolver_match.app_name else resolver_match.url_name
            app_name = resolver_match.app_name or resolver_match.func.__module__.split('.')[0]
            
            # Skip excluded views
            if view_name in self.EXCLUDED_VIEWS:
                return response
                
        except Exception as e:
            logger.warning(f"Could not resolve view for audit logging: {e}")
            view_name = "unknown"
            app_name = "unknown"
            
        # Get user information
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Get client IP address
        ip_address = self.get_client_ip(request)
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get object information if available
        content_type, object_id, object_repr = None, None, None
        
        # Create the audit log entry
        try:
            change_data = {}
            if hasattr(request, 'audit_request_data'):
                change_data = request.audit_request_data
                
            AuditLog.objects.create(
                user=user,
                action=action,
                ip_address=ip_address,
                user_agent=user_agent,
                app_name=app_name,
                content_type=content_type,
                object_id=object_id,
                object_repr=object_repr,
                action_details=f"{request.audit_request_method} {request.path} - {view_name}",
                change_data=change_data
            )
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            
        return response
        
    def get_client_ip(self, request):
        """Get the client IP address accounting for proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
