"""
Frontend URL configuration for ElDawliya System.
"""

from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
