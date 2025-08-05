"""
Attendance Models Package for HRMS
Contains models for attendance tracking, shifts, and time management
"""

from .attendance_models import (
    AttendanceRecordEnhanced,
    EmployeeShiftAssignmentEnhanced,
    AttendanceSummaryEnhanced
)

from .attendance_machine_models import (
    AttendanceMachine,
    MachineUser
)

from .work_shift_models import (
    WorkShift
)

__all__ = [
    'WorkShift',
    'AttendanceMachine',
    'MachineUser',
    'AttendanceRecordEnhanced',
    'EmployeeShiftAssignmentEnhanced',
    'AttendanceSummaryEnhanced',
]