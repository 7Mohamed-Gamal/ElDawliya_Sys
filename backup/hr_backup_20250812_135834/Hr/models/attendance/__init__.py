"""
Attendance Models Package for HRMS
Contains models for attendance tracking, shifts, and time management
"""

from .attendance_models import (
    AttendanceRecordEnhanced,
    EmployeeShiftAssignmentEnhanced,
)

from .attendance_machine_models import (
    AttendanceMachine,
    MachineUser,
    AttendanceMachineEnhanced,
    AttendanceMachineLog,
    AttendanceMachineGroup,
)

from .work_shift_models import (
    WorkShift,
    ShiftAssignment,
    WorkShiftEnhanced,
    ShiftPatternEnhanced,
    ShiftPatternAssignment,
)

from .attendance_summary_models import (
    AttendanceSummaryEnhanced,
    MonthlyAttendanceSummary,
)

__all__ = [
    # Work Shifts
    'WorkShift',
    'ShiftAssignment',
    'WorkShiftEnhanced',
    'ShiftPatternEnhanced',
    'ShiftPatternAssignment',
    
    # Attendance Machines
    'AttendanceMachine',
    'MachineUser',
    'AttendanceMachineEnhanced',
    'AttendanceMachineLog',
    'AttendanceMachineGroup',
    
    # Attendance Records
    'AttendanceRecordEnhanced',
    'EmployeeShiftAssignmentEnhanced',
    
    # Attendance Summaries
    'AttendanceSummaryEnhanced',
    'MonthlyAttendanceSummary',
]