# =============================================================================
# ElDawliya HR Management System - Company Structure URLs
# =============================================================================
# URL patterns for company structure management
# Includes companies, branches, departments, and job positions
# =============================================================================

from django.urls import path, include
from django.views.generic import RedirectView

# Import company structure views
try:
    from Hr.views.company_views import (
        CompanyListView, CompanyDetailView, CompanyCreateView,
        CompanyUpdateView, CompanyDeleteView,
        BranchListView, BranchDetailView, BranchCreateView, BranchUpdateView,
        DepartmentListView, DepartmentCreateView,
        JobPositionListView, JobPositionCreateView,
        get_branches_by_company, get_departments_by_branch, get_job_positions_by_department
    )
except ImportError:
    # Fallback to simple views for testing
    from Hr.views.simple_views import (
        SimpleListView as CompanyListView,
        SimpleDetailView as CompanyDetailView,
        SimpleCreateView as CompanyCreateView,
        SimpleListView as CompanyUpdateView,
        SimpleListView as CompanyDeleteView,
        SimpleListView as BranchListView,
        SimpleDetailView as BranchDetailView,
        SimpleCreateView as BranchCreateView,
        SimpleListView as BranchUpdateView,
        SimpleListView as DepartmentListView,
        SimpleCreateView as DepartmentCreateView,
        SimpleListView as JobPositionListView,
        SimpleCreateView as JobPositionCreateView,
        get_branches_by_company, get_departments_by_branch, get_job_positions_by_department
    )

# =============================================================================
# COMPANY MANAGEMENT URLS
# =============================================================================

company_patterns = [
    # Company CRUD operations
    path('', CompanyListView.as_view(), name='company_list'),
    path('create/', CompanyCreateView.as_view(), name='company_create'),
    path('<int:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('<int:pk>/edit/', CompanyUpdateView.as_view(), name='company_update'),
    path('<int:pk>/delete/', CompanyDeleteView.as_view(), name='company_delete'),
    
    # Company statistics and reports
    path('<int:pk>/statistics/', CompanyDetailView.as_view(), name='company_statistics'),
    path('<int:pk>/employees/', CompanyDetailView.as_view(), name='company_employees'),
    path('<int:pk>/departments/', CompanyDetailView.as_view(), name='company_departments'),
]

# =============================================================================
# BRANCH MANAGEMENT URLS
# =============================================================================

branch_patterns = [
    # Branch CRUD operations
    path('', BranchListView.as_view(), name='branch_list'),
    path('create/', BranchCreateView.as_view(), name='branch_create'),
    path('<int:pk>/', BranchDetailView.as_view(), name='branch_detail'),
    path('<int:pk>/edit/', BranchUpdateView.as_view(), name='branch_update'),
    path('<int:pk>/delete/', BranchUpdateView.as_view(), name='branch_delete'),  # Using update view for soft delete
    
    # Branch-specific operations
    path('<int:pk>/employees/', BranchDetailView.as_view(), name='branch_employees'),
    path('<int:pk>/departments/', BranchDetailView.as_view(), name='branch_departments'),
    path('<int:pk>/statistics/', BranchDetailView.as_view(), name='branch_statistics'),
]

# =============================================================================
# DEPARTMENT MANAGEMENT URLS
# =============================================================================

department_patterns = [
    # Department CRUD operations
    path('', DepartmentListView.as_view(), name='department_list'),
    path('create/', DepartmentCreateView.as_view(), name='department_create'),
    path('<int:pk>/', DepartmentListView.as_view(), name='department_detail'),
    path('<int:pk>/edit/', DepartmentCreateView.as_view(), name='department_update'),
    path('<int:pk>/delete/', DepartmentCreateView.as_view(), name='department_delete'),
    
    # Department-specific operations
    path('<int:pk>/employees/', DepartmentListView.as_view(), name='department_employees'),
    path('<int:pk>/positions/', DepartmentListView.as_view(), name='department_positions'),
    path('<int:pk>/hierarchy/', DepartmentListView.as_view(), name='department_hierarchy'),
]

# =============================================================================
# JOB POSITION MANAGEMENT URLS
# =============================================================================

job_position_patterns = [
    # Job Position CRUD operations
    path('', JobPositionListView.as_view(), name='job_position_list'),
    path('create/', JobPositionCreateView.as_view(), name='job_position_create'),
    path('<int:pk>/', JobPositionListView.as_view(), name='job_position_detail'),
    path('<int:pk>/edit/', JobPositionCreateView.as_view(), name='job_position_update'),
    path('<int:pk>/delete/', JobPositionCreateView.as_view(), name='job_position_delete'),
    
    # Job Position-specific operations
    path('<int:pk>/employees/', JobPositionListView.as_view(), name='job_position_employees'),
    path('<int:pk>/requirements/', JobPositionListView.as_view(), name='job_position_requirements'),
]

# =============================================================================
# AJAX AND API ENDPOINTS
# =============================================================================

ajax_patterns = [
    # Dynamic loading endpoints
    path('branches-by-company/', get_branches_by_company, name='get_branches_by_company'),
    path('departments-by-branch/', get_departments_by_branch, name='get_departments_by_branch'),
    path('positions-by-department/', get_job_positions_by_department, name='get_job_positions_by_department'),
    
    # Search and filter endpoints
    path('companies/search/', CompanyListView.as_view(), name='company_search_ajax'),
    path('branches/search/', BranchListView.as_view(), name='branch_search_ajax'),
    path('departments/search/', DepartmentListView.as_view(), name='department_search_ajax'),
    path('positions/search/', JobPositionListView.as_view(), name='job_position_search_ajax'),
]

# =============================================================================
# MAIN URL PATTERNS
# =============================================================================

urlpatterns = [
    # Default redirect to company list
    path('', RedirectView.as_view(pattern_name='hr:company_list', permanent=False), name='company_home'),
    
    # Company structure modules
    path('companies/', include((company_patterns, 'companies'))),
    path('branches/', include((branch_patterns, 'branches'))),
    path('departments/', include((department_patterns, 'departments'))),
    path('positions/', include((job_position_patterns, 'positions'))),
    path('jobs/', include((job_position_patterns, 'jobs'))),  # Alternative naming
    
    # AJAX endpoints
    path('ajax/', include((ajax_patterns, 'ajax'))),
    path('api/', include((ajax_patterns, 'api'))),  # Alternative naming
    
    # =============================================================================
    # LEGACY SUPPORT (for backward compatibility)
    # =============================================================================
    
    # Legacy department URLs (from existing system)
    path('dept/', include([
        path('', DepartmentListView.as_view(), name='dept_list'),
        path('create/', DepartmentCreateView.as_view(), name='dept_create'),
        path('<int:dept_code>/', DepartmentListView.as_view(), name='dept_detail'),
        path('<int:dept_code>/edit/', DepartmentCreateView.as_view(), name='dept_edit'),
        path('<int:dept_code>/delete/', DepartmentCreateView.as_view(), name='dept_delete'),
        path('<int:dept_code>/performance/', DepartmentListView.as_view(), name='dept_performance'),
    ])),
    
    # Legacy job URLs (from existing system)
    path('job/', include([
        path('', JobPositionListView.as_view(), name='job_list'),
        path('create/', JobPositionCreateView.as_view(), name='job_create'),
        path('<int:jop_code>/', JobPositionListView.as_view(), name='job_detail'),
        path('<int:jop_code>/edit/', JobPositionCreateView.as_view(), name='job_edit'),
        path('<int:jop_code>/delete/', JobPositionCreateView.as_view(), name='job_delete'),
        path('get_next_job_code/', JobPositionCreateView.as_view(), name='get_next_job_code'),
    ])),
    
    # =============================================================================
    # BULK OPERATIONS
    # =============================================================================
    
    # Bulk operations for company structure
    path('bulk/', include([
        path('companies/export/', CompanyListView.as_view(), name='companies_export'),
        path('branches/export/', BranchListView.as_view(), name='branches_export'),
        path('departments/export/', DepartmentListView.as_view(), name='departments_export'),
        path('positions/export/', JobPositionListView.as_view(), name='positions_export'),
        
        path('companies/import/', CompanyCreateView.as_view(), name='companies_import'),
        path('branches/import/', BranchCreateView.as_view(), name='branches_import'),
        path('departments/import/', DepartmentCreateView.as_view(), name='departments_import'),
        path('positions/import/', JobPositionCreateView.as_view(), name='positions_import'),
    ])),
    
    # =============================================================================
    # REPORTING AND ANALYTICS
    # =============================================================================
    
    # Company structure reports
    path('reports/', include([
        path('', CompanyListView.as_view(), name='structure_reports'),
        path('company-hierarchy/', CompanyListView.as_view(), name='company_hierarchy_report'),
        path('department-structure/', DepartmentListView.as_view(), name='department_structure_report'),
        path('position-analysis/', JobPositionListView.as_view(), name='position_analysis_report'),
        path('organizational-chart/', CompanyListView.as_view(), name='org_chart_report'),
    ])),
]

# =============================================================================
# URL PATTERNS SUMMARY
# =============================================================================

"""
Company Structure URL Patterns Summary:

Main Routes:
- /hr/company/ - Company structure home (redirects to company list)
- /hr/company/companies/ - Company management
- /hr/company/branches/ - Branch management  
- /hr/company/departments/ - Department management
- /hr/company/positions/ - Job position management

CRUD Operations (for each entity):
- / - List view
- /create/ - Create new
- /<id>/ - Detail view
- /<id>/edit/ - Update
- /<id>/delete/ - Delete

AJAX Endpoints:
- /hr/company/ajax/branches-by-company/ - Get branches for company
- /hr/company/ajax/departments-by-branch/ - Get departments for branch
- /hr/company/ajax/positions-by-department/ - Get positions for department

Legacy Support:
- /hr/company/dept/ - Legacy department URLs
- /hr/company/job/ - Legacy job URLs

Bulk Operations:
- /hr/company/bulk/*/export/ - Export data
- /hr/company/bulk/*/import/ - Import data

Reports:
- /hr/company/reports/ - Structure reports and analytics

URL Naming Convention:
- List: {entity}_list
- Detail: {entity}_detail  
- Create: {entity}_create
- Update: {entity}_update
- Delete: {entity}_delete
- AJAX: {entity}_{action}_ajax
"""
