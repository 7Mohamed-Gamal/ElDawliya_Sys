"""
Main URL configuration for ElDawliya System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="ElDawliya System API",
        default_version='v1',
        description="Comprehensive API for ElDawliya Enterprise Management System",
        terms_of_service="https://www.eldawliya.com/terms/",
        contact=openapi.Contact(email="api@eldawliya.com"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API URLs
    path('api/', include('config.urls.api')),

    # Frontend URLs
    path('', include('config.urls.frontend')),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # Redirect root to dashboard
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom error handlers
handler400 = 'frontend.views.error_400'
handler403 = 'frontend.views.error_403'
handler404 = 'frontend.views.error_404'
handler500 = 'frontend.views.error_500'
