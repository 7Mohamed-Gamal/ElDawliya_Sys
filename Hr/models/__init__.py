# Importar todos los modelos para que estén disponibles desde Hr.models
from django.utils.translation import gettext_lazy as _

# Importar modelos existentes
from Hr.models.base_models import Department, Job, JobInsurance, Car
from Hr.models.employee_model import Employee
from Hr.models.salary_models import SalaryItem, EmployeeSalaryItem, PayrollPeriod, PayrollEntry, PayrollItemDetail
from Hr.models.attendance_models import (
    AttendanceRule, EmployeeAttendanceRule, OfficialHoliday,
    AttendanceMachine, AttendanceRecord, AttendanceSummary
)

# Importar nuevos modelos (se crearán a continuación)
from Hr.models.pickup_point_models import PickupPoint
from Hr.models.task_models import EmployeeTask
from Hr.models.note_models import EmployeeNote, EmployeeNoteHistory
from Hr.models.file_models import EmployeeFile
from Hr.models.hr_task_models import HrTask
from Hr.models.leave_models import LeaveType, EmployeeLeave
from Hr.models.evaluation_models import EmployeeEvaluation

# Exportar todos los modelos
__all__ = [
    'Department', 'Job', 'JobInsurance', 'Car', 'Employee',
    'PickupPoint', 'EmployeeTask', 'EmployeeNote', 'EmployeeNoteHistory', 'EmployeeFile',
    'HrTask', 'LeaveType', 'EmployeeLeave',
    'SalaryItem', 'EmployeeSalaryItem', 'PayrollPeriod', 'PayrollEntry', 'PayrollItemDetail',
    'AttendanceRule', 'EmployeeAttendanceRule', 'OfficialHoliday',
    'AttendanceMachine', 'AttendanceRecord', 'AttendanceSummary',
    'EmployeeEvaluation'
]
