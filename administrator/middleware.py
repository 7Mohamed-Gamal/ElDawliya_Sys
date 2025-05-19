import django.db.utils
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class DatabaseConnectionMiddleware:
    """
    Middleware to handle database connection errors and redirect to setup page when needed.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if we're already on the database setup page to avoid redirect loops
        if request.path == reverse('database_setup'):
            return self.get_response(request)
            
        try:
            # Try to make a simple database query to test the connection
            from django.contrib.auth.models import Group
            Group.objects.first()
            
        except django.db.utils.OperationalError:
            # If primary database fails, try switching to default
            if settings.ACTIVE_DB == 'primary':
                settings.ACTIVE_DB = 'default'
                try:
                    Group.objects.first()
                    return self.get_response(request)
                except django.db.utils.OperationalError:
                    pass
            
            # Both databases failed, redirect to setup page
            return redirect('database_setup')
            
        except django.db.utils.InterfaceError:
            # Handle connection interface errors
            return redirect('database_setup')
            
        except Exception as e:
            # Log other database errors but don't redirect
            # This prevents hiding other types of errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Database error: {str(e)}")
            
        return self.get_response(request)