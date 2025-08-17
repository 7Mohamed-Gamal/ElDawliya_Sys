"""
Compatibility shim for enhanced HR models.
This module re-exports canonical models from Hr.models and provides
aliases expected by API tests/serializers (e.g., AttendanceSummary, EmployeeShiftAssignment).
"""

# Core and organizational
from Hr.models import (
    Company,
    Branch,
    Department,
    JobPosition,
    # Employee models
    Employee,
    EmployeeEducationEnhanced,
    EmployeeInsuranceEnhanced,
    EmployeeVehicleEnhanced,
    EmployeeFileEnhanced,
)

# Attendance
from Hr.models.attendance.attendance_models import (
    AttendanceRecordEnhanced,
    EmployeeShiftAssignmentEnhanced,
)
from Hr.models.attendance.attendance_machine_models import AttendanceMachineEnhanced
from Hr.models.attendance.work_shift_models import WorkShiftEnhanced
from Hr.models.attendance.attendance_summary_models import AttendanceSummaryEnhanced

# Leave
from Hr.models.leave.leave_type_models import LeaveType
from Hr.models.leave.leave_request_models import LeaveRequest
from Hr.models.leave.leave_balance_models import LeaveBalance

# Provide aliases to match names referenced by API layer/tests
AttendanceSummary = AttendanceSummaryEnhanced
EmployeeShiftAssignment = EmployeeShiftAssignmentEnhanced

# Provide simplified aliases for enhanced employee-related models
EmployeeEducation = EmployeeEducationEnhanced
EmployeeInsurance = EmployeeInsuranceEnhanced
EmployeeVehicle = EmployeeVehicleEnhanced
EmployeeFile = EmployeeFileEnhanced

