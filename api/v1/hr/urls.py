"""
HR API v1 URLs.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'hr_api_v1'

urlpatterns = [
    # Employee endpoints
    path('employees/', include('api.v1.hr.employees.urls')),
    
    # Attendance endpoints
    path('attendance/', include('api.v1.hr.attendance.urls')),
    
    # Payroll endpoints
    path('payroll/', include('api.v1.hr.payroll.urls')),
    
    # Leave endpoints
    path('leaves/', include('api.v1.hr.leaves.urls')),
    
    # Evaluation endpoints
    path('evaluations/', include('api.v1.hr.evaluations.urls')),
    
    # Training endpoints
    path('training/', include('api.v1.hr.training.urls')),
    
    # Router URLs
    path('', include(router.urls)),
]