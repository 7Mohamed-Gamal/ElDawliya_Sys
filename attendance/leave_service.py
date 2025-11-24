from typing import Optional
from django.db.models import QuerySet

def get_leave_types() -> QuerySet:
    """get_leave_types function"""
    from leaves.models import LeaveType
    return LeaveType.objects.filter(is_active=True).order_by('sort_order', 'leave_name')

def get_employee_leaves(employee, start_date=None, end_date=None) -> QuerySet:
    """get_employee_leaves function"""
    from leaves.models import EmployeeLeave
    qs = EmployeeLeave.objects.filter(emp=employee)
    if start_date and end_date:
        qs = qs.filter(start_date__lte=end_date, end_date__gte=start_date)
    return qs.order_by('-start_date')

def get_leave_balance(employee, leave_type) -> Optional[float]:
    """get_leave_balance function"""
    from leaves.models import LeaveBalance
    try:
        lb = LeaveBalance.objects.get(emp=employee, leave_type=leave_type, year=_current_year())
        return float(lb.remaining_days)
    except LeaveBalance.DoesNotExist:
        return None

def _current_year() -> int:
    """_current_year function"""
    from datetime import date
    return date.today().year