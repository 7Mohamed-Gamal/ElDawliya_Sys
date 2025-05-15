"""
WSGI config for ElDawliya_sys project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

# Import our custom WSGI application that handles database errors
from ElDawliya_sys.db_error_wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')

# Use our custom application instead of the default Django WSGI application
application = get_wsgi_application()
