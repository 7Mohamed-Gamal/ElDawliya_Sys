from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Import employee views
from Hr.views.employee_views import (
    employee_list, employee_create, employee_detail,
    employee_edit, employee_delete
)

# Import department views from updated file
from Hr.views.department_views_updated import (
    department_list, department_detail, department_create,
    department_edit, department_delete, department_employee_list,
    department_performance
)

# Import job views
from Hr.views.job_views import (
    job_list, job_create, job_detail, job_edit, job_delete
)

# Import car views
from Hr.views.car_views import (
    car_list, car_create, car_detail, car_edit, car_delete
)

# Import pickup point views
from Hr.views.pickup_point_views import (
    pickup_point_list, pickup_point_create, pickup_point_detail,
    pickup_point_edit, pickup_point_delete
)

# Import insurance job views
from Hr.views.insurance_views import (
    insurance_job_list, insurance_job_create, insurance_job_detail,
    insurance_job_edit, insurance_job_delete
)

# Import task views
from Hr.views.task_views import (
    employee_task_list, employee_task_create, employee_task_detail,
    employee_task_edit, employee_task_delete
)

# Import note views
from Hr.views.note_views import (
    employee_note_list, employee_note_create, employee_note_detail,
    employee_note_edit, employee_note_delete
)

# Import file views
from Hr.views.file_views import (
    employee_file_list, employee_file_create, employee_file_detail,
    employee_file_edit, employee_file_delete
)

# Import HR task views
from Hr.views.hr_task_views import (
    hr_task_list, hr_task_create, hr_task_detail,
    hr_task_edit, hr_task_delete
)

# Import leave type views
from Hr.views.leave_views import (
    leave_type_list, leave_type_create, leave_type_detail,
    leave_type_edit, leave_type_delete,
    employee_leave_list, employee_leave_create, employee_leave_detail,
    employee_leave_edit, employee_leave_delete, employee_leave_approve,
    employee_leave_reject
)

# Import evaluation views
from Hr.views.evaluation_views import (
    employee_evaluation_list, employee_evaluation_create, employee_evaluation_detail,
    employee_evaluation_edit, employee_evaluation_delete
)

# Import updated report views
from Hr.views.report_views_updated import (
    report_list, report_detail, export_data, department_report
)

# Import updated alert views
from Hr.views.alert_views_updated import (
    alert_list, alert_settings, renew_contract, renew_health_card
)

# Import updated analytics views
from Hr.views.analytics_views_updated import (
    analytics_dashboard, analytics_chart
)

# Import updated org chart views
from Hr.views.org_chart_views_updated import (
    org_chart, org_chart_data, department_org_chart, employee_hierarchy
)

# Import dashboard view
from Hr.views.employee_views import dashboard

# Placeholder for salary views
def salary_item_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة بنود الرواتب'})

def salary_item_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء بند راتب'})

def salary_item_edit(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تعديل بند راتب'})

def salary_item_delete(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'حذف بند راتب'})

def employee_salary_item_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة بنود رواتب الموظفين'})

def employee_salary_item_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء بند راتب موظف'})

def employee_salary_item_bulk_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء بنود رواتب للموظفين بالجملة'})

def employee_salary_item_edit(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تعديل بند راتب موظف'})

def employee_salary_item_delete(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'حذف بند راتب موظف'})

def payroll_period_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة فترات الرواتب'})

def payroll_period_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء فترة راتب'})

def payroll_period_edit(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تعديل فترة راتب'})

def payroll_period_delete(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'حذف فترة راتب'})

def payroll_calculate(request):
    return render(request, 'Hr/under_construction.html', {'title': 'حساب الرواتب'})

def payroll_entry_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة سجلات الرواتب'})

def payroll_entry_detail(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تفاصيل سجل راتب'})

# Placeholder for attendance views
def attendance_rule_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة قواعد الحضور'})

def attendance_rule_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء قاعدة حضور'})

def attendance_rule_edit(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تعديل قاعدة حضور'})

def attendance_rule_delete(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'حذف قاعدة حضور'})

def employee_attendance_rule_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة قواعد حضور الموظفين'})

def employee_attendance_rule_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء قاعدة حضور موظف'})

def employee_attendance_rule_bulk_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء قواعد حضور للموظفين بالجملة'})

def employee_attendance_rule_edit(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تعديل قاعدة حضور موظف'})

def employee_attendance_rule_delete(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'حذف قاعدة حضور موظف'})

def official_holiday_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة الإجازات الرسمية'})

def official_holiday_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء إجازة رسمية'})

def official_holiday_edit(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تعديل إجازة رسمية'})

def official_holiday_delete(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'حذف إجازة رسمية'})

def attendance_machine_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة ماكينات الحضور'})

def attendance_machine_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء ماكينة حضور'})

def attendance_machine_edit(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تعديل ماكينة حضور'})

def attendance_machine_delete(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'حذف ماكينة حضور'})

def attendance_record_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة سجلات الحضور'})

def attendance_record_create(request):
    return render(request, 'Hr/under_construction.html', {'title': 'إنشاء سجل حضور'})

def attendance_record_edit(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تعديل سجل حضور'})

def attendance_record_delete(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'حذف سجل حضور'})

def fetch_attendance_data(request):
    return render(request, 'Hr/under_construction.html', {'title': 'جلب بيانات الحضور'})

def attendance_summary_list(request):
    return render(request, 'Hr/under_construction.html', {'title': 'قائمة ملخصات الحضور'})

def attendance_summary_detail(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'تفاصيل ملخص الحضور'})

# Completion task function for HR task
def hr_task_complete(request, pk):
    return render(request, 'Hr/under_construction.html', {'title': 'إكمال مهمة'})
