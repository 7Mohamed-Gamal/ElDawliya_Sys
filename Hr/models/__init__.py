# HRMS Models - Comprehensive Human Resources Management System
from django.utils.translation import gettext_lazy as _

# Core Organizational Models
from Hr.models.core.company_models import Company
from Hr.models.core.branch_models import Branch
from Hr.models.core.department_models import Department
from Hr.models.core.job_position_models import JobPosition

# Employee Management Models
from Hr.models.employee.employee_models import Employee
from Hr.models.employee.employee_document_models import EmployeeDocument
from Hr.models.employee.employee_emergency_contact_models import EmployeeEmergencyContact
from Hr.models.employee.employee_training_models import EmployeeTraining

# Attendance & Time Management Models
from Hr.models.attendance.work_shift_models import WorkShift
from Hr.models.attendance.attendance_machine_models import AttendanceMachine
from Hr.models.attendance.attendance_record_models import AttendanceRecord
from Hr.models.attendance.attendance_summary_models import AttendanceSummary
from Hr.models.attendance.employee_shift_assignment_models import EmployeeShiftAssignment

# Leave Management Models
from Hr.models.leave.leave_type_models import LeaveType
from Hr.models.leave.leave_policy_models import LeavePolicy
from Hr.models.leave.leave_request_models import LeaveRequest
from Hr.models.leave.leave_balance_models import LeaveBalance

# Payroll Management Models
from Hr.models.payroll.salary_component_models import SalaryComponent
# TODO: Create missing payroll model files
# from Hr.models.payroll.employee_salary_structure_models import EmployeeSalaryStructure
# from Hr.models.payroll.payroll_period_models import PayrollPeriod
# from Hr.models.payroll.payroll_entry_models import PayrollEntry
# from Hr.models.payroll.tax_configuration_models import TaxConfiguration

# Performance Management Models
# TODO: Create missing performance model files
# from Hr.models.performance.performance_review_models import PerformanceReview
# from Hr.models.performance.performance_goal_models import PerformanceGoal
# from Hr.models.performance.performance_rating_models import PerformanceRating

# Document Management Models
# TODO: Create missing document model files
# from Hr.models.document.document_category_models import DocumentCategory
# from Hr.models.document.document_template_models import DocumentTemplate

# Notification Models
# TODO: Create missing notification model files
# from Hr.models.notification.hr_notification_models import HRNotification

# Legacy Models (for backward compatibility)
from Hr.models.legacy.legacy_models import (
    Job, JobInsurance, Car
    # TODO: Add back when other legacy model files are created
    # SalaryItem, EmployeeSalaryItem,
    # AttendanceRule, EmployeeAttendanceRule, OfficialHoliday,
    # PayrollItemDetail, PickupPoint, EmployeeNote,
    # EmployeeNoteHistory, EmployeeFile, HrTask, EmployeeLeave,
    # EmployeeEvaluation
)

# Import task models (avoiding conflicts with legacy models)
# Temporarily disabled due to model conflicts
# from Hr.models.task_models import EmployeeTask, TaskStep

# Export all models
__all__ = [
    # Core Organizational Models
    'Company', 'Branch', 'Department', 'JobPosition',

    # Employee Management Models
    'Employee', 'EmployeeDocument', 'EmployeeEmergencyContact', 'EmployeeTraining',

    # Attendance & Time Management Models
    'WorkShift', 'AttendanceMachine', 'AttendanceRecord', 'AttendanceSummary',
    'EmployeeShiftAssignment',

    # Leave Management Models
    'LeaveType', 'LeavePolicy', 'LeaveRequest', 'LeaveBalance',

    # Payroll Management Models
    'SalaryComponent',
    # TODO: Add back when model files are created
    # 'EmployeeSalaryStructure', 'PayrollPeriod',
    # 'PayrollEntry', 'TaxConfiguration',

    # Performance Management Models
    # TODO: Add back when model files are created
    # 'PerformanceReview', 'PerformanceGoal', 'PerformanceRating',

    # Document Management Models
    # TODO: Add back when model files are created
    # 'DocumentCategory', 'DocumentTemplate',

    # Notification Models
    # TODO: Add back when model files are created
    # 'HRNotification',

    # Legacy Models (backward compatibility)
    'Job', 'JobInsurance', 'Car',

    # Task Models - temporarily disabled due to conflicts
    # 'EmployeeTask', 'TaskStep',

    # TODO: Add back when other legacy model files are created
    # 'SalaryItem', 'EmployeeSalaryItem',
    # 'AttendanceRule', 'EmployeeAttendanceRule', 'OfficialHoliday',
    # 'PayrollItemDetail', 'PickupPoint', 'EmployeeNote',
    # 'EmployeeNoteHistory', 'EmployeeFile', 'HrTask', 'EmployeeLeave',
    # 'EmployeeEvaluation'
]
