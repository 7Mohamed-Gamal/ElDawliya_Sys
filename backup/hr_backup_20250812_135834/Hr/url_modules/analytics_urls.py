"""
Analytics URLs for HR module
"""

from django.urls import path
from Hr.views import analytics_dashboard, analytics_chart

app_name = 'analytics'

urlpatterns = [
    path('', analytics_dashboard, name='analytics_dashboard'),
    path('dashboard/', analytics_dashboard, name='dashboard'),
    path('chart/', analytics_chart, name='analytics_chart'),
    path('data/', analytics_chart, name='analytics_data'),  # For AJAX requests
]