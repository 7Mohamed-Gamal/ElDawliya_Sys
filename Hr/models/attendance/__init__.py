"""
Attendance Models Package
Contains all attendance-related models for the HR system
"""

from .work_shift_models import WorkShift, ShiftAssignment
from .attendance_machine_models import AttendanceMachine, MachineUser
from .attendance_record_models import AttendanceRecord, AttendanceSummary

__all__ = [
    'WorkShift',
    'ShiftAssignment', 
    'AttendanceMachine',
    'MachineUser',
    'AttendanceRecord',
    'AttendanceSummary',
]