"""
Alerts URLs for HR module
"""

from django.urls import path
from Hr.views.alert_views import alert_list

app_name = 'alerts'

urlpatterns = [
    path('', alert_list, name='alert_list'),
]