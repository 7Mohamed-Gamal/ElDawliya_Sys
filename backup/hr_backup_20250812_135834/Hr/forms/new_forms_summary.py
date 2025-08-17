# =============================================================================
# ElDawliya HR Management System - New Forms Summary
# =============================================================================
# Summary and imports for all new HR forms
# Comprehensive forms package for the redesigned HR system
# =============================================================================

"""
ملخص النماذج الجديدة لنظام الموارد البشرية

تم إنشاء مجموعة شاملة من النماذج التي تدعم:
- واجهة RTL للعربية
- تصميم Bootstrap 5 المتجاوب
- التحقق من صحة البيانات
- تجربة مستخدم محسنة
- أفضل ممارسات Django

النماذج المتوفرة:

1. نماذج هيكل الشركة (company_forms.py):
   - CompanyForm: إنشاء وتحديث الشركات
   - BranchForm: إدارة الفروع
   - DepartmentForm: إدارة الأقسام
   - JobPositionForm: إدارة المناصب الوظيفية

2. نماذج إدارة الموظفين (new_employee_forms.py):
   - NewEmployeeForm: نموذج شامل للموظفين مع تبويبات
   - EmployeeDocumentForm: رفع وإدارة وثائق الموظفين
   - EmployeeEmergencyContactForm: جهات الاتصال في الطوارئ

3. نماذج الحضور والانصراف (new_attendance_forms.py):
   - WorkShiftForm: إنشاء وإدارة الورديات
   - AttendanceMachineForm: إعداد أجهزة الحضور
   - EmployeeShiftAssignmentForm: تعيين الورديات للموظفين
   - AttendanceRecordForm: تسجيل الحضور اليدوي
   - AttendanceReportForm: تقارير الحضور المتقدمة

4. نماذج إدارة الإجازات (new_leave_forms.py):
   - LeaveTypeForm: إنشاء أنواع الإجازات
   - EmployeeLeaveBalanceForm: إدارة أرصدة الإجازات
   - LeaveRequestForm: طلبات الإجازة مع التحقق التلقائي
   - LeaveRequestApprovalForm: الموافقة على الطلبات
   - LeaveReportForm: تقارير الإجازات

5. نماذج نظام الرواتب (new_payroll_forms.py):
   - SalaryComponentForm: مكونات الراتب المرنة
   - EmployeeSalaryStructureForm: هيكل راتب الموظف
   - PayrollPeriodForm: فترات الرواتب
   - PayrollEntryForm: سجلات الرواتب التفصيلية
   - PayrollCalculationForm: حساب الرواتب التلقائي
   - PayrollReportForm: تقارير الرواتب

المميزات الرئيسية:

✅ دعم كامل للغة العربية مع RTL
✅ تصميم متجاوب مع Bootstrap 5
✅ استخدام Crispy Forms للتخطيط المتقدم
✅ التحقق من صحة البيانات على مستوى النموذج والحقل
✅ رسائل خطأ واضحة باللغة العربية
✅ تصفية ديناميكية للبيانات المترابطة
✅ نماذج تقارير متقدمة مع خيارات التصدير
✅ واجهة مستخدم بديهية ومهنية
✅ دعم رفع الملفات والصور
✅ نماذج الموافقة والسير العمل
✅ حسابات تلقائية للرواتب والإجازات
✅ تكامل مع نماذج البيانات الجديدة

الخطوات التالية:
1. إنشاء العروض (Views) للنماذج
2. إنشاء القوالب (Templates) مع التصميم المطلوب
3. إعداد URLs للنظام
4. تكوين Django Admin
5. إضافة JavaScript للتفاعل الديناميكي
6. اختبار شامل للنظام
"""

# استيراد جميع النماذج الجديدة
from .company_forms import (
    CompanyForm, BranchForm, DepartmentForm, JobPositionForm
)

from .new_employee_forms import (
    NewEmployeeForm, EmployeeDocumentForm, EmployeeEmergencyContactForm
)

from .new_attendance_forms import (
    WorkShiftForm, AttendanceMachineForm, EmployeeShiftAssignmentForm,
    AttendanceRecordForm, AttendanceReportForm
)

from .new_leave_forms import (
    LeaveTypeForm, EmployeeLeaveBalanceForm, LeaveRequestForm,
    LeaveRequestApprovalForm, LeaveReportForm
)

from .new_payroll_forms import (
    SalaryComponentForm, EmployeeSalaryStructureForm, PayrollPeriodForm,
    PayrollEntryForm, PayrollCalculationForm, PayrollReportForm
)

# قائمة شاملة بجميع النماذج الجديدة
NEW_HR_FORMS = [
    # Company Structure Forms
    'CompanyForm',
    'BranchForm', 
    'DepartmentForm',
    'JobPositionForm',
    
    # Employee Management Forms
    'NewEmployeeForm',
    'EmployeeDocumentForm',
    'EmployeeEmergencyContactForm',
    
    # Attendance & Time Tracking Forms
    'WorkShiftForm',
    'AttendanceMachineForm',
    'EmployeeShiftAssignmentForm',
    'AttendanceRecordForm',
    'AttendanceReportForm',
    
    # Leave Management Forms
    'LeaveTypeForm',
    'EmployeeLeaveBalanceForm',
    'LeaveRequestForm',
    'LeaveRequestApprovalForm',
    'LeaveReportForm',
    
    # Payroll System Forms
    'SalaryComponentForm',
    'EmployeeSalaryStructureForm',
    'PayrollPeriodForm',
    'PayrollEntryForm',
    'PayrollCalculationForm',
    'PayrollReportForm',
]

# إحصائيات النماذج
FORMS_STATISTICS = {
    'total_forms': len(NEW_HR_FORMS),
    'company_forms': 4,
    'employee_forms': 3,
    'attendance_forms': 5,
    'leave_forms': 5,
    'payroll_forms': 6,
    'features': [
        'RTL Arabic Support',
        'Bootstrap 5 Responsive Design',
        'Crispy Forms Layout',
        'Advanced Validation',
        'Dynamic Filtering',
        'File Upload Support',
        'Report Generation',
        'Workflow Management',
        'Auto Calculations',
        'Professional UI/UX'
    ]
}

def get_form_by_name(form_name):
    """الحصول على نموذج بالاسم"""
    form_mapping = {
        # Company Forms
        'CompanyForm': CompanyForm,
        'BranchForm': BranchForm,
        'DepartmentForm': DepartmentForm,
        'JobPositionForm': JobPositionForm,
        
        # Employee Forms
        'NewEmployeeForm': NewEmployeeForm,
        'EmployeeDocumentForm': EmployeeDocumentForm,
        'EmployeeEmergencyContactForm': EmployeeEmergencyContactForm,
        
        # Attendance Forms
        'WorkShiftForm': WorkShiftForm,
        'AttendanceMachineForm': AttendanceMachineForm,
        'EmployeeShiftAssignmentForm': EmployeeShiftAssignmentForm,
        'AttendanceRecordForm': AttendanceRecordForm,
        'AttendanceReportForm': AttendanceReportForm,
        
        # Leave Forms
        'LeaveTypeForm': LeaveTypeForm,
        'EmployeeLeaveBalanceForm': EmployeeLeaveBalanceForm,
        'LeaveRequestForm': LeaveRequestForm,
        'LeaveRequestApprovalForm': LeaveRequestApprovalForm,
        'LeaveReportForm': LeaveReportForm,
        
        # Payroll Forms
        'SalaryComponentForm': SalaryComponentForm,
        'EmployeeSalaryStructureForm': EmployeeSalaryStructureForm,
        'PayrollPeriodForm': PayrollPeriodForm,
        'PayrollEntryForm': PayrollEntryForm,
        'PayrollCalculationForm': PayrollCalculationForm,
        'PayrollReportForm': PayrollReportForm,
    }
    
    return form_mapping.get(form_name)

def get_forms_by_category(category):
    """الحصول على النماذج حسب الفئة"""
    categories = {
        'company': [CompanyForm, BranchForm, DepartmentForm, JobPositionForm],
        'employee': [NewEmployeeForm, EmployeeDocumentForm, EmployeeEmergencyContactForm],
        'attendance': [WorkShiftForm, AttendanceMachineForm, EmployeeShiftAssignmentForm, 
                      AttendanceRecordForm, AttendanceReportForm],
        'leave': [LeaveTypeForm, EmployeeLeaveBalanceForm, LeaveRequestForm, 
                 LeaveRequestApprovalForm, LeaveReportForm],
        'payroll': [SalaryComponentForm, EmployeeSalaryStructureForm, PayrollPeriodForm,
                   PayrollEntryForm, PayrollCalculationForm, PayrollReportForm],
    }
    
    return categories.get(category, [])

# تصدير جميع النماذج
__all__ = NEW_HR_FORMS + [
    'NEW_HR_FORMS',
    'FORMS_STATISTICS', 
    'get_form_by_name',
    'get_forms_by_category'
]
