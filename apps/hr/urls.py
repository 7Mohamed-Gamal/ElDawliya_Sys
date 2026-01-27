"""
HR API URLs.
"""

from django.urls import path, include

app_name = 'hr'

urlpatterns = [
    # API endpoints will be added here
    path('employees/', include('apps.hr.employees.urls')),
    path('attendance/', include('apps.hr.attendance.urls')),
    path('payroll/', include('apps.hr.payroll.urls')),
    path('leaves/', include('apps.hr.leaves.urls')),
    path('evaluations/', include('apps.hr.evaluations.urls')),
    path('training/', include('apps.hr.training.urls')),
]