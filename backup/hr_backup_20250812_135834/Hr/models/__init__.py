# HRMS Models - Comprehensive Human Resources Management System
from django.utils.translation import gettext_lazy as _

# Core Organizational Models
from Hr.models.core.company_models import Company
from Hr.models.core.branch_models import Branch
from Hr.models.core.department_models import Department
from Hr.models.core.job_position_models import JobPosition, JobLevel

# Employee Management Models (Legacy)
from Hr.models.employee.employee_models import Employee
from Hr.models.employee.employee_contact_models import EmployeeContact
from Hr.models.employee.employee_experience_models import EmployeeExperience
from Hr.models.employee.employee_family_models import EmployeeFamily
from Hr.models.employee.employee_bank_models import EmployeeBank

# Employee Management Models (Enhanced)
from Hr.models.employee.employee_models_enhanced import EmployeeEnhanced
from Hr.models.employee.employee_document_models import EmployeeDocumentEnhanced
from Hr.models.employee.employee_education_models import EmployeeEducationEnhanced
from Hr.models.employee.employee_insurance_models import EmployeeInsuranceEnhanced
from Hr.models.employee.employee_vehicle_models import EmployeeVehicleEnhanced
from Hr.models.employee.employee_file_models import EmployeeFileEnhanced, EmployeeFileCategory, EmployeeFileAccessLog
from Hr.models.employee.employee_emergency_contact_models import EmployeeEmergencyContactEnhanced
from Hr.models.employee.employee_training_models import EmployeeTrainingEnhanced, TrainingCategory, TrainingProvider

# Attendance & Time Management Models (Modern - for new development)
from Hr.models.attendance.work_shift_models import WorkShift, ShiftAssignment
from Hr.models.attendance.attendance_machine_models import AttendanceMachine, MachineUser
# from Hr.models.attendance.attendance_models import AttendanceRecord, AttendanceSummary, EmployeeShiftAssignment

# Legacy Attendance Models (Currently used by working views)
from Hr.models.attendance_models import (
    HrAttendanceRule as LegacyAttendanceRule,
    HrAttendanceRecord as LegacyAttendanceRecord,
    HrAttendanceSummary as LegacyAttendanceSummary,
    HrAttendanceMachine as LegacyAttendanceMachine,
    HrEmployeeAttendanceRule as LegacyEmployeeAttendanceRule,
    HrOfficialHoliday as LegacyOfficialHoliday
)

# Leave Management Models (Modern - for new development)
from Hr.models.leave.leave_type_models import LeaveType
from Hr.models.leave.leave_policy_models import LeavePolicy
from Hr.models.leave.leave_request_models import LeaveRequest, LeaveApproval
from Hr.models.leave.leave_balance_models import LeaveBalance, LeaveTransaction

# Legacy Leave Models (Currently used by some views)
from Hr.models.leave_models import (
    HrLeaveType as LegacyLeaveType,
    HrEmployeeLeave as LegacyEmployeeLeave
)

# Payroll Management Models (Modern - for new development)
from Hr.models.payroll.salary_component_models import SalaryComponent
from Hr.models.payroll.payroll_period_models import PayrollPeriod
from Hr.models.payroll.employee_salary_structure_models import EmployeeSalaryStructure, EmployeeSalaryComponent
from Hr.models.payroll.payroll_entry_models import PayrollEntry
from Hr.models.payroll.payroll_detail_models import PayrollDetail, PayrollDetailHistory

# Legacy Salary/Payroll Models (Currently used by working views)
from Hr.models.salary_models import (
    HrSalaryItem as LegacySalaryItem,
    HrEmployeeSalaryItem as LegacyEmployeeSalaryItem,
    HrPayrollPeriod as LegacyPayrollPeriod,
    HrPayrollEntry as LegacyPayrollEntry
)

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
    Job, JobInsurance, Car, HrJob, LegacyDepartment,
    LegacyPayrollEntry, PayrollItemDetail, SalaryItem, EmployeeSalaryItem,
    AttendanceRule, EmployeeAttendanceRule, OfficialHoliday,
    PickupPoint, EmployeeNote, EmployeeNoteHistory, EmployeeFile, 
    HrTask, EmployeeLeave, EmployeeEvaluation
)

# Import task models (avoiding conflicts with legacy models)
# Temporarily disabled due to model conflicts
# from Hr.models.task_models import EmployeeTask, TaskStep

# Export all models
__all__ = [
    # Core Organizational Models
    'Company', 'Branch', 'Department', 'JobPosition', 'JobLevel',

    # Employee Management Models (Legacy)
    'Employee', 'EmployeeContact',
    'EmployeeExperience', 'EmployeeFamily', 'EmployeeBank',
    
    # Employee Management Models (Enhanced)
    'EmployeeEnhanced', 'EmployeeDocumentEnhanced', 'EmployeeEducationEnhanced',
    'EmployeeInsuranceEnhanced', 'EmployeeVehicleEnhanced', 'EmployeeFileEnhanced',
    'EmployeeFileCategory', 'EmployeeFileAccessLog', 'EmployeeEmergencyContactEnhanced',
    'EmployeeTrainingEnhanced', 'TrainingCategory', 'TrainingProvider',

    # Attendance & Time Management Models (Modern)
    'WorkShift', 'ShiftAssignment', 'AttendanceMachine', 'MachineUser',
    'AttendanceRecord', 'AttendanceSummary',

    # Legacy Attendance Models (Currently used)
    'LegacyAttendanceRule', 'LegacyAttendanceRecord', 'LegacyAttendanceSummary',
    'LegacyAttendanceMachine', 'LegacyEmployeeAttendanceRule', 'LegacyOfficialHoliday',

    # Leave Management Models (Modern)
    'LeaveType', 'LeavePolicy', 'LeaveRequest', 'LeaveApproval',
    'LeaveBalance', 'LeaveTransaction',

    # Legacy Leave Models (Currently used)
    'LegacyLeaveType', 'LegacyEmployeeLeave',

    # Payroll Management Models (Modern)
    'SalaryComponent', 'PayrollPeriod', 'EmployeeSalaryStructure', 'EmployeeSalaryComponent',
    'PayrollEntry', 'PayrollDetail', 'PayrollDetailHistory',

    # Legacy Salary/Payroll Models (Currently used)
    'LegacySalaryItem', 'LegacyEmployeeSalaryItem', 'LegacyPayrollPeriod', 'LegacyPayrollEntry',

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
    'Job', 'JobInsurance', 'Car', 'HrJob', 'LegacyDepartment',
    'LegacyPayrollEntry', 'PayrollItemDetail', 'SalaryItem', 'EmployeeSalaryItem',
    'AttendanceRule', 'EmployeeAttendanceRule', 'OfficialHoliday',
    'PickupPoint', 'EmployeeNote', 'EmployeeNoteHistory', 'EmployeeFile', 
    'HrTask', 'EmployeeLeave', 'EmployeeEvaluation'

    # Task Models - temporarily disabled due to conflicts
    # 'EmployeeTask', 'TaskStep'
]
