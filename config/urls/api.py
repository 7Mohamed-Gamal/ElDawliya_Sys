"""
API URL configuration for ElDawliya System.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Create the main API router
router = DefaultRouter()

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/', include('api.authentication.urls')),

    # API v1 endpoints
    path('v1/', include('api.v1.urls')),

    # Core API endpoints
    path('core/', include('core.urls')),

    # Module-specific API endpoints
    path('hr/', include('apps.hr.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('procurement/', include('apps.procurement.urls')),
    path('projects/', include('apps.projects.urls')),
    path('finance/', include('apps.finance.urls')),
    path('administration/', include('apps.administration.urls')),

    # Router URLs (for ViewSets)
    path('', include(router.urls)),
]
