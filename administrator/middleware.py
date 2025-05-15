import re
from django.db import OperationalError, DatabaseError
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib.parse import quote

class DatabaseConnectionMiddleware:
    """
    Middleware to catch database connection errors and redirect to database settings page.

    This middleware intercepts database connection errors that occur during request processing
    and redirects the user to a custom database configuration page where they can update
    connection settings or create a new database.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if we're already on the database setup page to avoid redirect loops
        if request.path.startswith('/administrator/database-setup/'):
            try:
                # Try to process the request normally
                response = self.get_response(request)
                return response
            except Exception:
                # If there's an error on the database setup page itself,
                # we need to handle it specially to avoid redirect loops
                from django.shortcuts import render
                context = {
                    'connection_error': 'تعذر الاتصال بقاعدة البيانات. يرجى التأكد من صحة إعدادات الاتصال.',
                    'setup_mode': True
                }
                return render(request, 'administrator/database_setup.html', context)

        try:
            # Try to process the request normally
            response = self.get_response(request)
            return response
        except (OperationalError, DatabaseError) as e:
            # Check if the error is related to a database connection failure
            error_message = str(e).lower()

            # Check for common database connection failure messages
            connection_error = any(msg in error_message for msg in [
                'could not connect',
                'connection refused',
                'server is not found',
                'login failed',
                'unable to open database',
                'timeout expired',
                'network-related',
                'connection timed out',
                'no such table',
                'failed to connect'
            ])

            # If it's a connection error, redirect to the database settings page
            if connection_error:
                # Encode the error message to include it in the URL
                encoded_error = quote(str(e))
                db_config_url = f"/administrator/database-setup/?error={encoded_error}"

                # Don't redirect if we're already on the db config page (to avoid redirect loops)
                if not request.path.startswith('/administrator/database-setup/'):
                    return HttpResponseRedirect(db_config_url)

            # If not a connection error or we can't handle it, re-raise the exception
            raise
