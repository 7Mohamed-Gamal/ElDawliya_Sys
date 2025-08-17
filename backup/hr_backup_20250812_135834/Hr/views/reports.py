from ..utils.permissions import require_report_permission, require_export_permission

@require_report_permission('salary')
def salary_report_view(request):
    # ...existing code...

@require_export_permission('salary')
def export_salary_report(request):
    # ...existing code...

@require_report_permission('attendance')
def attendance_report_view(request):
    # ...existing code...

@require_export_permission('attendance')
def export_attendance_report(request):
    # ...existing code...

@require_report_permission('leave')
def leave_report_view(request):
    # ...existing code...

@require_export_permission('leave')
def export_leave_report(request):
    # ...existing code...

@require_report_permission('task')
def task_report_view(request):
    # ...existing code...

@require_export_permission('task')
def export_task_report(request):
    # ...existing code...