"""
API v1 URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router for v1 API
router = DefaultRouter()

app_name = 'api_v1'

urlpatterns = [
    # HR API endpoints
    path('hr/', include('api.v1.hr.urls')),
    
    # Inventory API endpoints
    path('inventory/', include('api.v1.inventory.urls')),
    
    # Procurement API endpoints
    path('procurement/', include('api.v1.procurement.urls')),
    
    # Projects API endpoints
    path('projects/', include('api.v1.projects.urls')),
    
    # Finance API endpoints
    path('finance/', include('api.v1.finance.urls')),
    
    # Administration API endpoints
    path('administration/', include('api.v1.administration.urls')),
    
    # Router URLs
    path('', include(router.urls)),
]