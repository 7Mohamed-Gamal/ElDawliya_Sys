# =============================================================================
# ElDawliya HR Management System - New Main URLs Configuration
# =============================================================================
# Main URL patterns for the HR application
# Includes all sub-modules with proper namespacing and organization
# =============================================================================

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import JsonResponse
from django.utils import timezone
from django.db import connection
import django
import platform

# Import main views
from .views.dashboard_views import HRDashboardView

# Application namespace
app_name = 'hr'

# Main URL patterns
urlpatterns = [
    # =============================================================================
    # MAIN DASHBOARD AND REDIRECTS
    # =============================================================================
    
    # Main HR dashboard
    path('', HRDashboardView.as_view(), name='hr_dashboard'),
    path('dashboard/', HRDashboardView.as_view(), name='dashboard'),
    
    # Default redirect to dashboard
    path('home/', RedirectView.as_view(pattern_name='hr:hr_dashboard', permanent=False), name='home'),
    
    # =============================================================================
    # COMPANY STRUCTURE URLS
    # =============================================================================
    
    # Company structure management
    path('company/', include('Hr.urls.company_urls'), name='company'),
    path('structure/', include('Hr.urls.company_urls'), name='structure'),
    
    # =============================================================================
    # EMPLOYEE MANAGEMENT URLS
    # =============================================================================
    
    # Employee management
    path('employees/', include('Hr.urls.employee_urls'), name='employees'),
    path('staff/', include('Hr.urls.employee_urls'), name='staff'),
    
    # =============================================================================
    # ATTENDANCE & TIME TRACKING URLS
    # =============================================================================
    
    # Attendance and time tracking
    path('attendance/', include('Hr.urls.attendance_urls'), name='attendance'),
    path('time/', include('Hr.urls.attendance_urls'), name='time'),
    
    # =============================================================================
    # LEAVE MANAGEMENT URLS
    # =============================================================================
    
    # Leave management
    path('leave/', include('Hr.urls.leave_urls'), name='leave'),
    path('vacation/', include('Hr.urls.leave_urls'), name='vacation'),
    
    # =============================================================================
    # PAYROLL SYSTEM URLS
    # =============================================================================
    
    # Payroll system
    path('payroll/', include('Hr.urls.payroll_urls'), name='payroll'),
    path('salary/', include('Hr.urls.payroll_urls'), name='salary'),
    
    # =============================================================================
    # DASHBOARD AND REPORTS URLS
    # =============================================================================
    
    # Dashboard and analytics
    path('analytics/', include('Hr.urls.dashboard_urls'), name='analytics'),
    path('reports/', include('Hr.urls.dashboard_urls'), name='reports'),
    
    # =============================================================================
    # API ENDPOINTS (AJAX)
    # =============================================================================
    
    # AJAX endpoints for dynamic functionality
    path('api/', include([
        # Dashboard API
        path('dashboard/', include('Hr.urls.dashboard_urls'), name='dashboard_api'),
        
        # Employee API
        path('employees/', include('Hr.urls.employee_urls'), name='employee_api'),
        
        # Attendance API
        path('attendance/', include('Hr.urls.attendance_urls'), name='attendance_api'),
        
        # Leave API
        path('leave/', include('Hr.urls.leave_urls'), name='leave_api'),
        
        # Payroll API
        path('payroll/', include('Hr.urls.payroll_urls'), name='payroll_api'),
        
        # Company API
        path('company/', include('Hr.urls.company_urls'), name='company_api'),
    ])),
    
    # =============================================================================
    # LEGACY SUPPORT (for backward compatibility)
    # =============================================================================
    
    # Legacy URL patterns for backward compatibility
    path('legacy/', include('Hr.urls'), name='legacy'),  # Include old URLs
    
    # =============================================================================
    # UTILITY URLS
    # =============================================================================
    
    # Health check and status
    path('health/', include([
        path('', lambda request: JsonResponse({
            'status': 'ok', 
            'timestamp': timezone.now().isoformat(),
            'version': '2.0.0'
        }), name='health_check'),
        path('db/', lambda request: JsonResponse({
            'database': 'connected' if connection.ensure_connection() else 'disconnected'
        }), name='db_check'),
    ])),
    
    # System information (for admins only)
    path('system/', include([
        path('info/', lambda request: JsonResponse({
            'version': '2.0.0',
            'django_version': django.get_version(),
            'python_version': platform.python_version(),
            'server_time': timezone.now().isoformat(),
        }) if request.user.is_superuser else JsonResponse({'error': 'Unauthorized'}, status=403), name='system_info'),
    ])),
]

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar if available
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# =============================================================================
# ERROR HANDLING
# =============================================================================

# Custom error handlers
handler404 = 'Hr.views.error_views.handler404'
handler500 = 'Hr.views.error_views.handler500'
handler403 = 'Hr.views.error_views.handler403'
handler400 = 'Hr.views.error_views.handler400'

# =============================================================================
# URL PATTERNS SUMMARY
# =============================================================================

"""
URL Structure Summary:

Main Routes:
- /hr/ - Main dashboard
- /hr/dashboard/ - Dashboard (alternative)

Module Routes:
- /hr/company/ - Company structure management
- /hr/employees/ - Employee management
- /hr/attendance/ - Attendance & time tracking
- /hr/leave/ - Leave management
- /hr/payroll/ - Payroll system
- /hr/analytics/ - Dashboard and reports

API Routes:
- /hr/api/dashboard/ - Dashboard AJAX endpoints
- /hr/api/employees/ - Employee AJAX endpoints
- /hr/api/attendance/ - Attendance AJAX endpoints
- /hr/api/leave/ - Leave AJAX endpoints
- /hr/api/payroll/ - Payroll AJAX endpoints
- /hr/api/company/ - Company AJAX endpoints

Utility Routes:
- /hr/health/ - System health check
- /hr/system/ - System information (admin only)
- /hr/legacy/ - Legacy URL patterns

Each module has its own URL file with detailed patterns:
- company_urls.py - Company, Branch, Department, Job Position URLs
- employee_urls.py - Employee management URLs
- attendance_urls.py - Attendance and time tracking URLs
- leave_urls.py - Leave management URLs
- payroll_urls.py - Payroll system URLs
- dashboard_urls.py - Dashboard and analytics URLs

URL Naming Convention:
- List views: module_model_list (e.g., 'employee_list')
- Detail views: module_model_detail (e.g., 'employee_detail')
- Create views: module_model_create (e.g., 'employee_create')
- Update views: module_model_update (e.g., 'employee_update')
- Delete views: module_model_delete (e.g., 'employee_delete')
- AJAX views: module_model_ajax_action (e.g., 'employee_search_ajax')

Security Features:
- Permission-based access control
- CSRF protection for all forms
- Secure file upload handling
- Rate limiting for API endpoints
- Input validation and sanitization
"""
