"""
A minimal test script to check if the server is working.
"""

import os
import sys
import django
from django.conf import settings
from django.http import HttpResponse
from django.urls import path
from django.core.management import execute_from_command_line

# Configure minimal settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='test-key',
    ROOT_URLCONF=__name__,
    MIDDLEWARE=[
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
        },
    ],
)

# Initialize Django
django.setup()

# Define a simple view
def test_view(request):
    return HttpResponse("Test server is working!")

# Define URL patterns
urlpatterns = [
    path('', test_view),
]

# Run the server
if __name__ == '__main__':
    execute_from_command_line(['manage.py', 'runserver', '8001'])
