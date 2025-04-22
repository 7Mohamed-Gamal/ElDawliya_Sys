from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Customize admin site
admin.site.site_header = _('نظام الدولية للموارد البشرية')
admin.site.site_title = _('إدارة الموارد البشرية')
admin.site.index_title = _('لوحة تحكم الموارد البشرية')

# Import models from Hr.models
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

# Register base models
admin.site.register(Department)
admin.site.register(Job)
admin.site.register(JobInsurance)
admin.site.register(Car)

# Register employee models
admin.site.register(Employee)

# Register salary models
admin.site.register(SalaryItem)
admin.site.register(EmployeeSalaryItem)
admin.site.register(PayrollPeriod)
admin.site.register(PayrollEntry)
admin.site.register(PayrollItemDetail)

# Register attendance models
admin.site.register(AttendanceRule)
admin.site.register(EmployeeAttendanceRule)
admin.site.register(OfficialHoliday)
admin.site.register(AttendanceMachine)
admin.site.register(AttendanceRecord)
admin.site.register(AttendanceSummary)

# Register pickup point models
admin.site.register(PickupPoint)

# Register task models
admin.site.register(EmployeeTask)

# Register note models
admin.site.register(EmployeeNote)

# Register file models
admin.site.register(EmployeeFile)

# Register HR task models
admin.site.register(HrTask)

# Register leave models
admin.site.register(LeaveType)
admin.site.register(EmployeeLeave)

# Register evaluation models
admin.site.register(EmployeeEvaluation)
