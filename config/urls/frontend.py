"""
Frontend URL configuration for ElDawliya System.
"""

from django.urls import path, include
from django.contrib.auth import views as auth_views
from frontend import views

app_name = 'frontend'

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),

    # Module URLs
    path('hr/', include('apps.hr.frontend_urls')),
    path('inventory/', include('apps.inventory.frontend_urls')),
    path('procurement/', include('apps.procurement.frontend_urls')),
    path('projects/', include('apps.projects.frontend_urls')),
    path('finance/', include('apps.finance.frontend_urls')),
    path('administration/', include('apps.administration.frontend_urls')),

    # Reports
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('reports/<str:report_type>/', views.ReportDetailView.as_view(), name='report_detail'),

    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),

    # Help and Support
    path('help/', views.HelpView.as_view(), name='help'),
    path('support/', views.SupportView.as_view(), name='support'),
]
