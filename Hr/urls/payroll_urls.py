# =============================================================================
# ElDawliya HR Management System - Payroll System URLs
# =============================================================================
# URL patterns for payroll system management
# Includes salary components, structures, periods, entries, and calculations
# =============================================================================

from django.urls import path, include
from django.views.generic import RedirectView

# Import payroll system views
try:
    from Hr.views.payroll_views import (
        SalaryComponentListView, SalaryComponentDetailView, SalaryComponentCreateView, SalaryComponentUpdateView,
        EmployeeSalaryStructureListView, EmployeeSalaryStructureCreateView,
        PayrollPeriodListView, PayrollPeriodDetailView, PayrollPeriodCreateView,
        PayrollEntryListView, PayrollEntryDetailView, PayrollEntryCreateView,
        payroll_calculation_view, calculate_payroll, calculate_employee_payroll
    )
except ImportError:
    # Fallback to simple views for testing
    from Hr.views.simple_views import (
        SimpleListView as SalaryComponentListView,
        SimpleDetailView as SalaryComponentDetailView,
        SimpleCreateView as SalaryComponentCreateView,
        SimpleListView as SalaryComponentUpdateView,
        SimpleListView as EmployeeSalaryStructureListView,
        SimpleCreateView as EmployeeSalaryStructureCreateView,
        SimpleListView as PayrollPeriodListView,
        SimpleDetailView as PayrollPeriodDetailView,
        SimpleCreateView as PayrollPeriodCreateView,
        SimpleListView as PayrollEntryListView,
        SimpleDetailView as PayrollEntryDetailView,
        SimpleCreateView as PayrollEntryCreateView,
        payroll_calculation_view, calculate_payroll, calculate_employee_payroll
    )

# =============================================================================
# SALARY COMPONENT MANAGEMENT
# =============================================================================

component_patterns = [
    # Salary component CRUD operations
    path('', SalaryComponentListView.as_view(), name='salary_component_list'),
    path('create/', SalaryComponentCreateView.as_view(), name='salary_component_create'),
    path('<int:pk>/', SalaryComponentDetailView.as_view(), name='salary_component_detail'),
    path('<int:pk>/edit/', SalaryComponentUpdateView.as_view(), name='salary_component_update'),
    path('<int:pk>/delete/', SalaryComponentUpdateView.as_view(), name='salary_component_delete'),
    
    # Component specific operations
    path('<int:pk>/employees/', SalaryComponentDetailView.as_view(), name='component_employees'),
    path('<int:pk>/statistics/', SalaryComponentDetailView.as_view(), name='component_statistics'),
    path('<int:pk>/copy/', SalaryComponentCreateView.as_view(), name='component_copy'),
    
    # Component categories
    path('earnings/', SalaryComponentListView.as_view(), name='earnings_components'),
    path('deductions/', SalaryComponentListView.as_view(), name='deductions_components'),
    path('benefits/', SalaryComponentListView.as_view(), name='benefits_components'),
]

# =============================================================================
# EMPLOYEE SALARY STRUCTURE MANAGEMENT
# =============================================================================

structure_patterns = [
    # Salary structure CRUD operations
    path('', EmployeeSalaryStructureListView.as_view(), name='employee_salary_structure_list'),
    path('create/', EmployeeSalaryStructureCreateView.as_view(), name='employee_salary_structure_create'),
    path('<int:pk>/', EmployeeSalaryStructureListView.as_view(), name='employee_salary_structure_detail'),
    path('<int:pk>/edit/', EmployeeSalaryStructureCreateView.as_view(), name='employee_salary_structure_update'),
    path('<int:pk>/delete/', EmployeeSalaryStructureCreateView.as_view(), name='employee_salary_structure_delete'),
    
    # Structure specific operations
    path('employee/<int:employee_id>/', EmployeeSalaryStructureListView.as_view(), name='employee_salary_structures'),
    path('bulk-create/', EmployeeSalaryStructureCreateView.as_view(), name='salary_structure_bulk_create'),
    path('bulk-update/', EmployeeSalaryStructureCreateView.as_view(), name='salary_structure_bulk_update'),
    path('template/', EmployeeSalaryStructureCreateView.as_view(), name='salary_structure_template'),
]

# =============================================================================
# PAYROLL PERIOD MANAGEMENT
# =============================================================================

period_patterns = [
    # Payroll period CRUD operations
    path('', PayrollPeriodListView.as_view(), name='payroll_period_list'),
    path('create/', PayrollPeriodCreateView.as_view(), name='payroll_period_create'),
    path('<int:pk>/', PayrollPeriodDetailView.as_view(), name='payroll_period_detail'),
    path('<int:pk>/edit/', PayrollPeriodCreateView.as_view(), name='payroll_period_update'),
    path('<int:pk>/delete/', PayrollPeriodCreateView.as_view(), name='payroll_period_delete'),
    
    # Period specific operations
    path('<int:pk>/calculate/', payroll_calculation_view, name='payroll_period_calculate'),
    path('<int:pk>/finalize/', PayrollPeriodDetailView.as_view(), name='payroll_period_finalize'),
    path('<int:pk>/reopen/', PayrollPeriodDetailView.as_view(), name='payroll_period_reopen'),
    path('<int:pk>/entries/', PayrollPeriodDetailView.as_view(), name='payroll_period_entries'),
    path('<int:pk>/summary/', PayrollPeriodDetailView.as_view(), name='payroll_period_summary'),
    
    # Period reports
    path('<int:pk>/report/', PayrollPeriodDetailView.as_view(), name='payroll_period_report'),
    path('<int:pk>/export/', PayrollPeriodDetailView.as_view(), name='payroll_period_export'),
    path('<int:pk>/payslips/', PayrollPeriodDetailView.as_view(), name='payroll_period_payslips'),
]

# =============================================================================
# PAYROLL ENTRY MANAGEMENT
# =============================================================================

entry_patterns = [
    # Payroll entry CRUD operations
    path('', PayrollEntryListView.as_view(), name='payroll_entry_list'),
    path('create/', PayrollEntryCreateView.as_view(), name='payroll_entry_create'),
    path('<int:pk>/', PayrollEntryDetailView.as_view(), name='payroll_entry_detail'),
    path('<int:pk>/edit/', PayrollEntryCreateView.as_view(), name='payroll_entry_update'),
    path('<int:pk>/delete/', PayrollEntryCreateView.as_view(), name='payroll_entry_delete'),
    
    # Entry specific operations
    path('<int:pk>/calculate/', calculate_employee_payroll, name='payroll_entry_calculate'),
    path('<int:pk>/approve/', PayrollEntryDetailView.as_view(), name='payroll_entry_approve'),
    path('<int:pk>/reject/', PayrollEntryDetailView.as_view(), name='payroll_entry_reject'),
    path('<int:pk>/payslip/', PayrollEntryDetailView.as_view(), name='payroll_entry_payslip'),
    path('<int:pk>/breakdown/', PayrollEntryDetailView.as_view(), name='payroll_entry_breakdown'),
    
    # Employee specific entries
    path('employee/<int:employee_id>/', PayrollEntryListView.as_view(), name='employee_payroll_entries'),
    path('period/<int:period_id>/', PayrollEntryListView.as_view(), name='period_payroll_entries'),
]

# =============================================================================
# PAYROLL CALCULATION AND PROCESSING
# =============================================================================

calculation_patterns = [
    # Main calculation operations
    path('', payroll_calculation_view, name='payroll_calculation'),
    path('run/', calculate_payroll, name='payroll_run_calculation'),
    path('preview/', payroll_calculation_view, name='payroll_calculation_preview'),
    
    # Specific calculations
    path('employee/<int:employee_id>/', calculate_employee_payroll, name='employee_payroll_calculation'),
    path('period/<int:period_id>/', calculate_payroll, name='period_payroll_calculation'),
    path('department/<int:department_id>/', calculate_payroll, name='department_payroll_calculation'),
    
    # Calculation validation
    path('validate/', payroll_calculation_view, name='payroll_calculation_validate'),
    path('test/', payroll_calculation_view, name='payroll_calculation_test'),
    path('simulate/', payroll_calculation_view, name='payroll_calculation_simulate'),
]

# =============================================================================
# PAYROLL REPORTS AND ANALYTICS
# =============================================================================

report_patterns = [
    # Main reports
    path('', PayrollPeriodListView.as_view(), name='payroll_reports_dashboard'),
    path('summary/', PayrollPeriodListView.as_view(), name='payroll_summary_report'),
    
    # Specific reports
    path('cost-analysis/', PayrollEntryListView.as_view(), name='payroll_cost_analysis'),
    path('tax-report/', PayrollEntryListView.as_view(), name='payroll_tax_report'),
    path('benefits-report/', PayrollEntryListView.as_view(), name='payroll_benefits_report'),
    path('variance-report/', PayrollEntryListView.as_view(), name='payroll_variance_report'),
    
    # Period reports
    path('period/<int:period_id>/', PayrollPeriodDetailView.as_view(), name='period_payroll_report'),
    path('comparison/', PayrollPeriodListView.as_view(), name='payroll_period_comparison'),
    
    # Employee reports
    path('employee/<int:employee_id>/', PayrollEntryListView.as_view(), name='employee_payroll_report'),
    path('department/<int:department_id>/', PayrollEntryListView.as_view(), name='department_payroll_report'),
    
    # Export reports
    path('export/excel/', PayrollEntryListView.as_view(), name='payroll_export_excel'),
    path('export/pdf/', PayrollEntryListView.as_view(), name='payroll_export_pdf'),
    path('export/csv/', PayrollEntryListView.as_view(), name='payroll_export_csv'),
]

# =============================================================================
# AJAX AND API ENDPOINTS
# =============================================================================

ajax_patterns = [
    # Calculation operations
    path('calculate/preview/', payroll_calculation_view, name='payroll_calculate_preview_ajax'),
    path('calculate/employee/<int:employee_id>/', calculate_employee_payroll, name='employee_payroll_calculate_ajax'),
    
    # Data fetching
    path('components/fetch/', SalaryComponentListView.as_view(), name='salary_components_fetch_ajax'),
    path('structures/fetch/', EmployeeSalaryStructureListView.as_view(), name='salary_structures_fetch_ajax'),
    path('entries/fetch/', PayrollEntryListView.as_view(), name='payroll_entries_fetch_ajax'),
    
    # Validation
    path('validate/period/', PayrollPeriodCreateView.as_view(), name='payroll_period_validate_ajax'),
    path('validate/structure/', EmployeeSalaryStructureCreateView.as_view(), name='salary_structure_validate_ajax'),
    
    # Statistics
    path('statistics/dashboard/', PayrollEntryListView.as_view(), name='payroll_statistics_ajax'),
    path('statistics/period/<int:period_id>/', PayrollPeriodDetailView.as_view(), name='period_statistics_ajax'),
]

# =============================================================================
# MAIN URL PATTERNS
# =============================================================================

urlpatterns = [
    # Default redirect to payroll entries
    path('', RedirectView.as_view(pattern_name='hr:payroll_entry_list', permanent=False), name='payroll_home'),
    
    # Salary components management
    path('components/', include((component_patterns, 'components'))),
    path('elements/', include((component_patterns, 'elements'))),  # Alternative naming
    
    # Employee salary structures
    path('structures/', include((structure_patterns, 'structures'))),
    path('templates/', include((structure_patterns, 'templates'))),  # Alternative naming
    
    # Payroll periods
    path('periods/', include((period_patterns, 'periods'))),
    path('cycles/', include((period_patterns, 'cycles'))),  # Alternative naming
    
    # Payroll entries
    path('entries/', include((entry_patterns, 'entries'))),
    path('records/', include((entry_patterns, 'records'))),  # Alternative naming
    
    # Include entry patterns at root level for convenience
    *entry_patterns,
    
    # Payroll calculation and processing
    path('calculation/', include((calculation_patterns, 'calculation'))),
    path('processing/', include((calculation_patterns, 'processing'))),  # Alternative naming
    
    # Reports and analytics
    path('reports/', include((report_patterns, 'reports'))),
    path('analytics/', include((report_patterns, 'analytics'))),  # Alternative naming
    
    # AJAX endpoints
    path('ajax/', include((ajax_patterns, 'ajax'))),
    path('api/', include((ajax_patterns, 'api'))),  # Alternative naming
    
    # =============================================================================
    # LEGACY SUPPORT (for backward compatibility)
    # =============================================================================
    
    # Legacy payroll URLs (from existing system)
    path('legacy/', include([
        # Legacy salary components
        path('components/', SalaryComponentListView.as_view(), name='salary_component_list_legacy'),
        path('components/create/', SalaryComponentCreateView.as_view(), name='salary_component_create_legacy'),
        
        # Legacy payroll entries
        path('entries/', PayrollEntryListView.as_view(), name='payroll_entry_list_legacy'),
        path('entries/create/', PayrollEntryCreateView.as_view(), name='payroll_entry_create_legacy'),
        
        # Legacy calculations
        path('calculate/', payroll_calculation_view, name='payroll_calculate_legacy'),
    ])),
    
    # =============================================================================
    # PAYROLL APPROVAL WORKFLOW
    # =============================================================================
    
    # Approval workflow
    path('approvals/', include([
        path('', PayrollEntryListView.as_view(), name='payroll_approvals'),
        path('pending/', PayrollEntryListView.as_view(), name='pending_payroll_approvals'),
        path('approved/', PayrollEntryListView.as_view(), name='approved_payroll_entries'),
        path('rejected/', PayrollEntryListView.as_view(), name='rejected_payroll_entries'),
        
        path('bulk-approve/', PayrollEntryListView.as_view(), name='payroll_bulk_approve'),
        path('bulk-reject/', PayrollEntryListView.as_view(), name='payroll_bulk_reject'),
        path('workflow/', PayrollEntryListView.as_view(), name='payroll_approval_workflow'),
    ])),
    
    # =============================================================================
    # PAYROLL TAXES AND DEDUCTIONS
    # =============================================================================
    
    # Tax and deduction management
    path('taxes/', include([
        path('', SalaryComponentListView.as_view(), name='payroll_taxes'),
        path('income-tax/', SalaryComponentListView.as_view(), name='income_tax_components'),
        path('social-security/', SalaryComponentListView.as_view(), name='social_security_components'),
        path('insurance/', SalaryComponentListView.as_view(), name='insurance_components'),
        
        path('calculate/', payroll_calculation_view, name='tax_calculation'),
        path('reports/', PayrollEntryListView.as_view(), name='tax_reports'),
    ])),
    
    # =============================================================================
    # PAYROLL BENEFITS AND ALLOWANCES
    # =============================================================================
    
    # Benefits and allowances
    path('benefits/', include([
        path('', SalaryComponentListView.as_view(), name='payroll_benefits'),
        path('allowances/', SalaryComponentListView.as_view(), name='payroll_allowances'),
        path('bonuses/', SalaryComponentListView.as_view(), name='payroll_bonuses'),
        path('overtime/', SalaryComponentListView.as_view(), name='payroll_overtime'),
        
        path('calculate/', payroll_calculation_view, name='benefits_calculation'),
        path('reports/', PayrollEntryListView.as_view(), name='benefits_reports'),
    ])),
    
    # =============================================================================
    # PAYROLL INTEGRATION AND EXPORT
    # =============================================================================
    
    # Integration and export
    path('integration/', include([
        path('', PayrollEntryListView.as_view(), name='payroll_integration'),
        path('bank-transfer/', PayrollEntryListView.as_view(), name='payroll_bank_transfer'),
        path('accounting/', PayrollEntryListView.as_view(), name='payroll_accounting_export'),
        path('government/', PayrollEntryListView.as_view(), name='payroll_government_reports'),
        
        path('export/bank-file/', PayrollEntryListView.as_view(), name='payroll_bank_file_export'),
        path('export/accounting-file/', PayrollEntryListView.as_view(), name='payroll_accounting_file_export'),
    ])),
    
    # =============================================================================
    # PAYROLL AUDIT AND COMPLIANCE
    # =============================================================================
    
    # Audit and compliance
    path('audit/', include([
        path('', PayrollEntryListView.as_view(), name='payroll_audit'),
        path('trail/', PayrollEntryListView.as_view(), name='payroll_audit_trail'),
        path('compliance/', PayrollEntryListView.as_view(), name='payroll_compliance'),
        path('reconciliation/', PayrollEntryListView.as_view(), name='payroll_reconciliation'),
        
        path('reports/', PayrollEntryListView.as_view(), name='payroll_audit_reports'),
        path('logs/', PayrollEntryListView.as_view(), name='payroll_audit_logs'),
    ])),
]

# =============================================================================
# URL PATTERNS SUMMARY
# =============================================================================

"""
Payroll System URL Patterns Summary:

Main Routes:
- /hr/payroll/ - Payroll home (redirects to entries)
- /hr/payroll/components/ - Salary component management
- /hr/payroll/structures/ - Employee salary structures
- /hr/payroll/periods/ - Payroll period management
- /hr/payroll/entries/ - Payroll entry management
- /hr/payroll/calculation/ - Payroll calculation and processing
- /hr/payroll/reports/ - Reports and analytics

Salary Components:
- /hr/payroll/components/ - List all components
- /hr/payroll/components/create/ - Create new component
- /hr/payroll/components/<id>/ - Component details
- /hr/payroll/components/earnings/ - Earnings components
- /hr/payroll/components/deductions/ - Deduction components

Employee Salary Structures:
- /hr/payroll/structures/ - List all structures
- /hr/payroll/structures/create/ - Create new structure
- /hr/payroll/structures/employee/<id>/ - Employee structures
- /hr/payroll/structures/bulk-create/ - Bulk create structures

Payroll Periods:
- /hr/payroll/periods/ - List all periods
- /hr/payroll/periods/create/ - Create new period
- /hr/payroll/periods/<id>/ - Period details
- /hr/payroll/periods/<id>/calculate/ - Calculate period
- /hr/payroll/periods/<id>/finalize/ - Finalize period

Payroll Entries:
- /hr/payroll/entries/ - List all entries
- /hr/payroll/entries/create/ - Create new entry
- /hr/payroll/<id>/ - Entry details (root level)
- /hr/payroll/<id>/edit/ - Edit entry
- /hr/payroll/<id>/payslip/ - Generate payslip

Payroll Calculation:
- /hr/payroll/calculation/ - Main calculation interface
- /hr/payroll/calculation/run/ - Run calculation
- /hr/payroll/calculation/employee/<id>/ - Employee calculation
- /hr/payroll/calculation/preview/ - Preview calculation

Reports and Analytics:
- /hr/payroll/reports/ - Main reports dashboard
- /hr/payroll/reports/cost-analysis/ - Cost analysis
- /hr/payroll/reports/tax-report/ - Tax reports
- /hr/payroll/reports/employee/<id>/ - Employee reports

AJAX Endpoints:
- /hr/payroll/ajax/calculate/preview/ - Preview calculation
- /hr/payroll/ajax/components/fetch/ - Fetch components
- /hr/payroll/ajax/validate/period/ - Validate period

Approval Workflow:
- /hr/payroll/approvals/ - Approval dashboard
- /hr/payroll/approvals/pending/ - Pending approvals
- /hr/payroll/approvals/bulk-approve/ - Bulk approve

Taxes and Deductions:
- /hr/payroll/taxes/ - Tax management
- /hr/payroll/taxes/income-tax/ - Income tax components
- /hr/payroll/taxes/calculate/ - Tax calculation

Benefits and Allowances:
- /hr/payroll/benefits/ - Benefits management
- /hr/payroll/benefits/allowances/ - Allowances
- /hr/payroll/benefits/bonuses/ - Bonuses

Integration and Export:
- /hr/payroll/integration/ - Integration dashboard
- /hr/payroll/integration/bank-transfer/ - Bank transfers
- /hr/payroll/integration/export/bank-file/ - Bank file export

Audit and Compliance:
- /hr/payroll/audit/ - Audit dashboard
- /hr/payroll/audit/trail/ - Audit trail
- /hr/payroll/audit/compliance/ - Compliance reports

Legacy Support:
- /hr/payroll/legacy/ - Legacy URL patterns for backward compatibility

URL Naming Convention:
- {entity}_{action} - Standard URLs
- {entity}_{action}_ajax - AJAX endpoints
- {entity}_{action}_legacy - Legacy URLs
"""
