"""
WSGI config for ElDawliya_sys project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

# Import standard Django WSGI application for testing
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ElDawliya_sys.settings.development")

# Use standard Django WSGI application for testing
application = get_wsgi_application()
