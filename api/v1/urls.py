"""
API Version 1 URL Configuration
تكوين URLs للإصدار الأول من API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Import viewsets from different modules
from . import views
from .hr import urls as hr_urls
from .inventory import urls as inventory_urls
from .projects import urls as projects_urls
from .reports import urls as reports_urls

# Create router for ViewSets
router = DefaultRouter()

# Core API endpoints
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'api-keys', views.APIKeyViewSet, basename='apikey')

app_name = 'api_v1'

urlpatterns = [
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),

    # Core API endpoints
    path('status/', views.APIStatusView.as_view(), name='api_status'),
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    path('usage-stats/', views.UsageStatsView.as_view(), name='usage_stats'),

    # Module-specific endpoints
    path('hr/', include(hr_urls)),
    path('inventory/', include(inventory_urls)),
    path('projects/', include(projects_urls)),
    path('reports/', include(reports_urls)),

    # AI and integration endpoints (commented out - modules not implemented)
    # path('ai/', include('api.v1.ai.urls')),
    # path('integration/', include('api.v1.integration.urls')),

    # ViewSet URLs
    path('', include(router.urls)),
]
