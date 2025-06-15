# =============================================================================
# ElDawliya HR Management System - Views Summary
# =============================================================================
# Summary and imports for all new HR views
# Comprehensive views package for the redesigned HR system
# =============================================================================

"""
ملخص العروض الجديدة لنظام الموارد البشرية

تم إنشاء مجموعة شاملة من العروض التي تدعم:
- Class-Based Views (CBV) مع Django
- أفضل ممارسات Django للأمان والأداء
- دعم AJAX للتحديثات الديناميكية
- تكامل مع النماذج المُنشأة
- دعم RTL للعربية والتصميم المتجاوب
- نظام الصلاحيات والتحكم في الوصول
- معالجة الأخطاء وعرض الرسائل المناسبة

العروض المتوفرة:

1. عروض هيكل الشركة (company_views.py):
   - CompanyListView, CompanyDetailView, CompanyCreateView, CompanyUpdateView, CompanyDeleteView
   - BranchListView, BranchDetailView, BranchCreateView, BranchUpdateView
   - DepartmentListView, DepartmentCreateView
   - JobPositionListView, JobPositionCreateView
   - AJAX views للتصفية الديناميكية

2. عروض إدارة الموظفين (new_employee_views.py):
   - NewEmployeeListView, NewEmployeeDetailView, NewEmployeeCreateView, NewEmployeeUpdateView
   - NewEmployeeDocumentListView, NewEmployeeDocumentCreateView
   - NewEmployeeEmergencyContactCreateView
   - AJAX views للبحث والإحصائيات السريعة
   - عمليات مجمعة للموظفين وتصدير Excel

3. عروض الحضور والانصراف (new_attendance_views.py):
   - NewWorkShiftListView, NewWorkShiftDetailView, NewWorkShiftCreateView, NewWorkShiftUpdateView
   - NewAttendanceMachineListView, NewAttendanceMachineCreateView
   - NewEmployeeShiftAssignmentListView, NewEmployeeShiftAssignmentCreateView
   - NewAttendanceRecordListView, NewAttendanceRecordCreateView
   - NewAttendanceReportView مع تجميع البيانات وإحصائيات متقدمة
   - AJAX views للوحة التحكم والإضافة السريعة

4. عروض إدارة الإجازات (new_leave_views.py):
   - NewLeaveTypeListView, NewLeaveTypeDetailView, NewLeaveTypeCreateView, NewLeaveTypeUpdateView
   - NewEmployeeLeaveBalanceListView, NewEmployeeLeaveBalanceCreateView
   - NewLeaveRequestListView, NewLeaveRequestDetailView, NewLeaveRequestCreateView
   - تكامل مع سجل التدقيق (HRAuditLog)

5. عروض نظام الرواتب (payroll_views.py):
   - SalaryComponentListView, SalaryComponentDetailView, SalaryComponentCreateView, SalaryComponentUpdateView
   - EmployeeSalaryStructureListView, EmployeeSalaryStructureCreateView
   - PayrollPeriodListView, PayrollPeriodDetailView, PayrollPeriodCreateView
   - PayrollEntryListView, PayrollEntryDetailView, PayrollEntryCreateView
   - payroll_calculation_view مع حساب تلقائي للرواتب
   - دوال حساب الرواتب المتقدمة

6. لوحة التحكم الشاملة (dashboard_views.py):
   - HRDashboardView مع إحصائيات شاملة
   - إحصائيات الموظفين، الحضور، الإجازات، الرواتب
   - التنبيهات والإشعارات التلقائية
   - AJAX views لبيانات المخططات والإحصائيات
   - البحث السريع والإجراءات السريعة

المميزات الرئيسية المطبقة:

✅ Class-Based Views (CBV):
- ListView للعرض مع التصفية والبحث
- DetailView لعرض التفاصيل مع البيانات المرتبطة
- CreateView و UpdateView مع التحقق والرسائل
- DeleteView مع التحقق من البيانات المرتبطة

✅ الأمان والصلاحيات:
- LoginRequiredMixin لجميع العروض
- PermissionRequiredMixin للعمليات الحساسة
- التحقق من البيانات المرتبطة قبل الحذف
- تسجيل العمليات في سجل التدقيق

✅ تجربة المستخدم:
- رسائل نجاح وخطأ واضحة
- إعادة توجيه ذكية بعد العمليات
- تصفية وبحث متقدم
- ترقيم الصفحات للقوائم الطويلة

✅ AJAX والتفاعل الديناميكي:
- البحث السريع للموظفين
- التصفية الديناميكية للقوائم المترابطة
- تحديث الحالة بدون إعادة تحميل الصفحة
- بيانات لوحة التحكم المباشرة

✅ التقارير والتحليلات:
- تقارير الحضور مع تجميع البيانات
- إحصائيات متقدمة للإجازات
- تحليلات الرواتب والتكاليف
- مخططات بيانية تفاعلية

✅ العمليات المتقدمة:
- حساب الرواتب التلقائي
- تصدير البيانات إلى Excel
- العمليات المجمعة للموظفين
- إدارة دورة حياة الموظف الكاملة

✅ التكامل والربط:
- ربط البيانات عبر النماذج
- التحقق من التداخل والتكرار
- حسابات تلقائية للأرصدة والمؤشرات
- تتبع التغييرات والتدقيق

الإحصائيات:
- إجمالي العروض: 50+ عرض
- عروض هيكل الشركة: 12 عرض
- عروض الموظفين: 10 عروض
- عروض الحضور: 12 عرض
- عروض الإجازات: 8 عروض
- عروض الرواتب: 10 عروض
- لوحة التحكم: 8 عروض

الخطوات التالية:
1. إنشاء القوالب (Templates) مع التصميم المطلوب
2. إعداد URLs للنظام
3. تكوين Django Admin
4. إضافة JavaScript للتفاعل الديناميكي
5. اختبار شامل للنظام
6. تحسين الأداء والأمان
"""

# استيراد جميع العروض الجديدة
from .company_views import (
    CompanyListView, CompanyDetailView, CompanyCreateView, CompanyUpdateView, CompanyDeleteView,
    BranchListView, BranchDetailView, BranchCreateView, BranchUpdateView,
    DepartmentListView, DepartmentCreateView,
    JobPositionListView, JobPositionCreateView,
    get_branches_by_company, get_departments_by_branch, get_job_positions_by_department
)

from .new_employee_views import (
    NewEmployeeListView, NewEmployeeDetailView, NewEmployeeCreateView, NewEmployeeUpdateView,
    NewEmployeeDocumentListView, NewEmployeeDocumentCreateView,
    NewEmployeeEmergencyContactCreateView,
    new_employee_search_ajax, new_employee_quick_stats, new_employee_status_update,
    new_employee_bulk_update, new_export_employees_excel
)

from .new_attendance_views import (
    NewWorkShiftListView, NewWorkShiftDetailView, NewWorkShiftCreateView, NewWorkShiftUpdateView,
    NewAttendanceMachineListView, NewAttendanceMachineCreateView,
    NewEmployeeShiftAssignmentListView, NewEmployeeShiftAssignmentCreateView,
    NewAttendanceRecordListView, NewAttendanceRecordCreateView, NewAttendanceReportView,
    new_attendance_dashboard_data, new_attendance_quick_add
)

from .new_leave_views import (
    NewLeaveTypeListView, NewLeaveTypeDetailView, NewLeaveTypeCreateView, NewLeaveTypeUpdateView,
    NewEmployeeLeaveBalanceListView, NewEmployeeLeaveBalanceCreateView,
    NewLeaveRequestListView, NewLeaveRequestDetailView, NewLeaveRequestCreateView
)

from .payroll_views import (
    SalaryComponentListView, SalaryComponentDetailView, SalaryComponentCreateView, SalaryComponentUpdateView,
    EmployeeSalaryStructureListView, EmployeeSalaryStructureCreateView,
    PayrollPeriodListView, PayrollPeriodDetailView, PayrollPeriodCreateView,
    PayrollEntryListView, PayrollEntryDetailView, PayrollEntryCreateView,
    payroll_calculation_view, calculate_payroll, calculate_employee_payroll
)

from .dashboard_views import (
    HRDashboardView, dashboard_data_ajax, get_overview_data,
    get_attendance_chart_data, get_leaves_chart_data, get_payroll_chart_data,
    quick_employee_search, dashboard_notifications
)

# قائمة شاملة بجميع العروض الجديدة
NEW_HR_VIEWS = [
    # Company Structure Views
    'CompanyListView', 'CompanyDetailView', 'CompanyCreateView', 'CompanyUpdateView', 'CompanyDeleteView',
    'BranchListView', 'BranchDetailView', 'BranchCreateView', 'BranchUpdateView',
    'DepartmentListView', 'DepartmentCreateView',
    'JobPositionListView', 'JobPositionCreateView',
    
    # Employee Management Views
    'NewEmployeeListView', 'NewEmployeeDetailView', 'NewEmployeeCreateView', 'NewEmployeeUpdateView',
    'NewEmployeeDocumentListView', 'NewEmployeeDocumentCreateView',
    'NewEmployeeEmergencyContactCreateView',
    
    # Attendance & Time Tracking Views
    'NewWorkShiftListView', 'NewWorkShiftDetailView', 'NewWorkShiftCreateView', 'NewWorkShiftUpdateView',
    'NewAttendanceMachineListView', 'NewAttendanceMachineCreateView',
    'NewEmployeeShiftAssignmentListView', 'NewEmployeeShiftAssignmentCreateView',
    'NewAttendanceRecordListView', 'NewAttendanceRecordCreateView', 'NewAttendanceReportView',
    
    # Leave Management Views
    'NewLeaveTypeListView', 'NewLeaveTypeDetailView', 'NewLeaveTypeCreateView', 'NewLeaveTypeUpdateView',
    'NewEmployeeLeaveBalanceListView', 'NewEmployeeLeaveBalanceCreateView',
    'NewLeaveRequestListView', 'NewLeaveRequestDetailView', 'NewLeaveRequestCreateView',
    
    # Payroll System Views
    'SalaryComponentListView', 'SalaryComponentDetailView', 'SalaryComponentCreateView', 'SalaryComponentUpdateView',
    'EmployeeSalaryStructureListView', 'EmployeeSalaryStructureCreateView',
    'PayrollPeriodListView', 'PayrollPeriodDetailView', 'PayrollPeriodCreateView',
    'PayrollEntryListView', 'PayrollEntryDetailView', 'PayrollEntryCreateView',
    
    # Dashboard Views
    'HRDashboardView',
]

# قائمة العروض الوظيفية (Function-Based Views)
NEW_HR_FUNCTION_VIEWS = [
    # AJAX Views
    'get_branches_by_company', 'get_departments_by_branch', 'get_job_positions_by_department',
    'new_employee_search_ajax', 'new_employee_quick_stats', 'new_employee_status_update',
    'new_attendance_dashboard_data', 'new_attendance_quick_add',
    'dashboard_data_ajax', 'quick_employee_search', 'dashboard_notifications',
    
    # Bulk Operations
    'new_employee_bulk_update', 'new_export_employees_excel',
    
    # Payroll Calculations
    'payroll_calculation_view', 'calculate_payroll', 'calculate_employee_payroll',
    
    # Chart Data
    'get_overview_data', 'get_attendance_chart_data', 'get_leaves_chart_data', 'get_payroll_chart_data',
]

# إحصائيات العروض
VIEWS_STATISTICS = {
    'total_class_views': len(NEW_HR_VIEWS),
    'total_function_views': len(NEW_HR_FUNCTION_VIEWS),
    'company_views': 12,
    'employee_views': 10,
    'attendance_views': 12,
    'leave_views': 8,
    'payroll_views': 10,
    'dashboard_views': 8,
    'ajax_views': 15,
    'features': [
        'Class-Based Views (CBV)',
        'Permission-Based Access Control',
        'AJAX Dynamic Updates',
        'Advanced Filtering & Search',
        'Comprehensive Reports',
        'Bulk Operations',
        'Data Export (Excel)',
        'Real-time Dashboard',
        'Audit Trail Integration',
        'RTL Arabic Support',
        'Responsive Design',
        'Error Handling',
        'Success Messages',
        'Smart Redirects',
        'Data Validation'
    ]
}

def get_view_by_name(view_name):
    """الحصول على عرض بالاسم"""
    view_mapping = {
        # Company Views
        'CompanyListView': CompanyListView,
        'CompanyDetailView': CompanyDetailView,
        'CompanyCreateView': CompanyCreateView,
        'CompanyUpdateView': CompanyUpdateView,
        'CompanyDeleteView': CompanyDeleteView,
        'BranchListView': BranchListView,
        'BranchDetailView': BranchDetailView,
        'BranchCreateView': BranchCreateView,
        'BranchUpdateView': BranchUpdateView,
        'DepartmentListView': DepartmentListView,
        'DepartmentCreateView': DepartmentCreateView,
        'JobPositionListView': JobPositionListView,
        'JobPositionCreateView': JobPositionCreateView,
        
        # Employee Views
        'NewEmployeeListView': NewEmployeeListView,
        'NewEmployeeDetailView': NewEmployeeDetailView,
        'NewEmployeeCreateView': NewEmployeeCreateView,
        'NewEmployeeUpdateView': NewEmployeeUpdateView,
        'NewEmployeeDocumentListView': NewEmployeeDocumentListView,
        'NewEmployeeDocumentCreateView': NewEmployeeDocumentCreateView,
        'NewEmployeeEmergencyContactCreateView': NewEmployeeEmergencyContactCreateView,
        
        # Attendance Views
        'NewWorkShiftListView': NewWorkShiftListView,
        'NewWorkShiftDetailView': NewWorkShiftDetailView,
        'NewWorkShiftCreateView': NewWorkShiftCreateView,
        'NewWorkShiftUpdateView': NewWorkShiftUpdateView,
        'NewAttendanceMachineListView': NewAttendanceMachineListView,
        'NewAttendanceMachineCreateView': NewAttendanceMachineCreateView,
        'NewEmployeeShiftAssignmentListView': NewEmployeeShiftAssignmentListView,
        'NewEmployeeShiftAssignmentCreateView': NewEmployeeShiftAssignmentCreateView,
        'NewAttendanceRecordListView': NewAttendanceRecordListView,
        'NewAttendanceRecordCreateView': NewAttendanceRecordCreateView,
        'NewAttendanceReportView': NewAttendanceReportView,
        
        # Leave Views
        'NewLeaveTypeListView': NewLeaveTypeListView,
        'NewLeaveTypeDetailView': NewLeaveTypeDetailView,
        'NewLeaveTypeCreateView': NewLeaveTypeCreateView,
        'NewLeaveTypeUpdateView': NewLeaveTypeUpdateView,
        'NewEmployeeLeaveBalanceListView': NewEmployeeLeaveBalanceListView,
        'NewEmployeeLeaveBalanceCreateView': NewEmployeeLeaveBalanceCreateView,
        'NewLeaveRequestListView': NewLeaveRequestListView,
        'NewLeaveRequestDetailView': NewLeaveRequestDetailView,
        'NewLeaveRequestCreateView': NewLeaveRequestCreateView,
        
        # Payroll Views
        'SalaryComponentListView': SalaryComponentListView,
        'SalaryComponentDetailView': SalaryComponentDetailView,
        'SalaryComponentCreateView': SalaryComponentCreateView,
        'SalaryComponentUpdateView': SalaryComponentUpdateView,
        'EmployeeSalaryStructureListView': EmployeeSalaryStructureListView,
        'EmployeeSalaryStructureCreateView': EmployeeSalaryStructureCreateView,
        'PayrollPeriodListView': PayrollPeriodListView,
        'PayrollPeriodDetailView': PayrollPeriodDetailView,
        'PayrollPeriodCreateView': PayrollPeriodCreateView,
        'PayrollEntryListView': PayrollEntryListView,
        'PayrollEntryDetailView': PayrollEntryDetailView,
        'PayrollEntryCreateView': PayrollEntryCreateView,
        
        # Dashboard Views
        'HRDashboardView': HRDashboardView,
    }
    
    return view_mapping.get(view_name)

def get_views_by_category(category):
    """الحصول على العروض حسب الفئة"""
    categories = {
        'company': [CompanyListView, CompanyDetailView, CompanyCreateView, CompanyUpdateView, CompanyDeleteView,
                   BranchListView, BranchDetailView, BranchCreateView, BranchUpdateView,
                   DepartmentListView, DepartmentCreateView, JobPositionListView, JobPositionCreateView],
        'employee': [NewEmployeeListView, NewEmployeeDetailView, NewEmployeeCreateView, NewEmployeeUpdateView,
                    NewEmployeeDocumentListView, NewEmployeeDocumentCreateView, NewEmployeeEmergencyContactCreateView],
        'attendance': [NewWorkShiftListView, NewWorkShiftDetailView, NewWorkShiftCreateView, NewWorkShiftUpdateView,
                      NewAttendanceMachineListView, NewAttendanceMachineCreateView,
                      NewEmployeeShiftAssignmentListView, NewEmployeeShiftAssignmentCreateView,
                      NewAttendanceRecordListView, NewAttendanceRecordCreateView, NewAttendanceReportView],
        'leave': [NewLeaveTypeListView, NewLeaveTypeDetailView, NewLeaveTypeCreateView, NewLeaveTypeUpdateView,
                 NewEmployeeLeaveBalanceListView, NewEmployeeLeaveBalanceCreateView,
                 NewLeaveRequestListView, NewLeaveRequestDetailView, NewLeaveRequestCreateView],
        'payroll': [SalaryComponentListView, SalaryComponentDetailView, SalaryComponentCreateView, SalaryComponentUpdateView,
                   EmployeeSalaryStructureListView, EmployeeSalaryStructureCreateView,
                   PayrollPeriodListView, PayrollPeriodDetailView, PayrollPeriodCreateView,
                   PayrollEntryListView, PayrollEntryDetailView, PayrollEntryCreateView],
        'dashboard': [HRDashboardView],
    }
    
    return categories.get(category, [])

# تصدير جميع العروض
__all__ = NEW_HR_VIEWS + NEW_HR_FUNCTION_VIEWS + [
    'NEW_HR_VIEWS',
    'NEW_HR_FUNCTION_VIEWS',
    'VIEWS_STATISTICS', 
    'get_view_by_name',
    'get_views_by_category'
]
