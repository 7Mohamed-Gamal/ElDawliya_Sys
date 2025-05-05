from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# تخصيص موقع الإدارة
admin.site.site_header = _('نظام الدولية للموارد البشرية')
admin.site.site_title = _('إدارة الموارد البشرية')
admin.site.index_title = _('لوحة تحكم الموارد البشرية')

# استيراد النماذج من Hr.models
from Hr.models import (
    Department, Job, JobInsurance, Car,
    Employee,
    SalaryItem, EmployeeSalaryItem, PayrollPeriod, PayrollEntry, PayrollItemDetail,
    AttendanceRule, EmployeeAttendanceRule, OfficialHoliday, AttendanceMachine, AttendanceRecord, AttendanceSummary,
    PickupPoint,
    EmployeeTask,
    EmployeeNote,
    EmployeeFile,
    HrTask,
    LeaveType, EmployeeLeave,
    EmployeeEvaluation
)

# تسجيل النماذج الأساسية
admin.site.register(Department)
admin.site.register(Job)
admin.site.register(JobInsurance)
admin.site.register(Car)

# تسجيل نماذج الموظفين
admin.site.register(Employee)

# تسجيل نماذج الرواتب
admin.site.register(SalaryItem)
admin.site.register(EmployeeSalaryItem)
admin.site.register(PayrollPeriod)
admin.site.register(PayrollEntry)
admin.site.register(PayrollItemDetail)

# تسجيل نماذج الحضور
admin.site.register(AttendanceRule)
admin.site.register(EmployeeAttendanceRule)
admin.site.register(OfficialHoliday)
admin.site.register(AttendanceMachine)
admin.site.register(AttendanceRecord)
admin.site.register(AttendanceSummary)

# تسجيل نماذج نقاط الالتقاط
admin.site.register(PickupPoint)

# تسجيل نماذج المهام
admin.site.register(EmployeeTask)

# تسجيل نماذج الملاحظات
admin.site.register(EmployeeNote)

# تسجيل نماذج الملفات
admin.site.register(EmployeeFile)

# تسجيل نماذج مهام الموارد البشرية
admin.site.register(HrTask)

# تسجيل نماذج الإجازات
admin.site.register(LeaveType)
admin.site.register(EmployeeLeave)

# تسجيل نماذج التقييمات
admin.site.register(EmployeeEvaluation)
