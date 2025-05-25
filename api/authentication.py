from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import authentication, exceptions
from .models import APIKey

User = get_user_model()


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for API key authentication
    """
    keyword = 'ApiKey'
    
    def authenticate(self, request):
        """
        Authenticate the request using API key
        """
        auth_header = authentication.get_authorization_header(request).split()
        
        if not auth_header or auth_header[0].lower() != self.keyword.lower().encode():
            return None
        
        if len(auth_header) == 1:
            msg = 'Invalid API key header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth_header) > 2:
            msg = 'Invalid API key header. API key string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        
        try:
            api_key = auth_header[1].decode()
        except UnicodeError:
            msg = 'Invalid API key header. API key string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)
        
        return self.authenticate_credentials(api_key, request)
    
    def authenticate_credentials(self, key, request):
        """
        Authenticate the API key and return user
        """
        try:
            api_key_obj = APIKey.objects.select_related('user').get(
                key=key,
                is_active=True
            )
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key.')
        
        # Check if API key is expired
        if api_key_obj.is_expired():
            raise exceptions.AuthenticationFailed('API key has expired.')
        
        # Check if user is active
        if not api_key_obj.user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled.')
        
        # Update last used timestamp
        api_key_obj.last_used = timezone.now()
        api_key_obj.save(update_fields=['last_used'])
        
        # Store API key in request for logging
        request.api_key = api_key_obj
        
        return (api_key_obj.user, api_key_obj)
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return self.keyword


class CombinedAuthentication(authentication.BaseAuthentication):
    """
    Combined authentication that tries session authentication first,
    then falls back to API key authentication
    """
    
    def authenticate(self, request):
        """
        Try session authentication first, then API key
        """
        # Try session authentication first
        session_auth = authentication.SessionAuthentication()
        try:
            result = session_auth.authenticate(request)
            if result:
                return result
        except exceptions.AuthenticationFailed:
            pass
        
        # Fall back to API key authentication
        api_key_auth = APIKeyAuthentication()
        return api_key_auth.authenticate(request)
    
    def authenticate_header(self, request):
        """
        Return authentication header for API key
        """
        return 'ApiKey'
