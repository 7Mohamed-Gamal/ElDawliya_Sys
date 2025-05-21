from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin  # Import Django's default admin
from .views import test_view

# Import the database setup view directly to avoid database dependency
# This allows the database setup URL to work even when the database is unavailable
from administrator.views import database_setup

# Special URL patterns that should work even when the database is unavailable
# These URLs are defined first to ensure they're accessible during database errors
special_urlpatterns = [
    # Direct access to database setup page - this must work even when DB is down
    path('administrator/database-setup/', database_setup, name='database_setup'),
]

# Regular URL patterns that require database access
urlpatterns = [
    path('test/', test_view, name='test'),  # Test path
    path('admin/', admin.site.urls),  # Default Django admin site
    path('accounts/', include('accounts.urls')),  # Accounts app URLs
    path('meetings/', include('meetings.urls')),  # Meetings app URLs
    path('tasks/', include('tasks.urls')),  # Tasks app URLs
    path('Hr/', include('Hr.urls')), # HR app URLs
    path('inventory/', include('inventory.urls')), # Inventory app URLs
    path('purchase/', include('Purchase_orders.urls')), # Purchase orders app URLs
    path('administrator/', include('administrator.urls')),  # Administrator app URLs
    path('notifications/', include('notifications.urls')),  # Notifications app URLs
    path('audit/', include('audit.urls')),  # Audit app URLs
    path('employee-tasks/', include('employee_tasks.urls')),  # Employee tasks app URLs
    path('cars/', include('cars.urls')),  # Cars app URLs
    path('', lambda request: redirect('accounts:login'), name='home'),  # Redirect home to login page
]

# Combine special and regular URL patterns
urlpatterns = special_urlpatterns + urlpatterns

# Add media URLs in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
