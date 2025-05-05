# استيراد النماذج الموجودة
from .employee_forms import (
    EmployeeForm, EmployeeFilterForm, DepartmentForm, JobForm, CarForm, EmployeeSearchForm
)
from .salary_forms import (
    SalaryItemForm, EmployeeSalaryItemForm, EmployeeSalaryItemBulkForm,
    PayrollPeriodForm, PayrollCalculationForm
)
from .attendance_forms import (
    AttendanceRuleForm, EmployeeAttendanceRuleForm, EmployeeAttendanceRuleBulkForm,
    OfficialHolidayForm, AttendanceMachineForm, AttendanceRecordForm,
    FetchAttendanceDataForm
)

# استيراد النماذج الجديدة
from .pickup_point_forms import PickupPointForm
from .insurance_forms import JobInsuranceForm
from .task_forms import EmployeeTaskForm
from .note_forms import EmployeeNoteForm
from .file_forms import EmployeeFileForm
from .hr_task_forms import HrTaskForm
from .leave_forms import LeaveTypeForm, EmployeeLeaveForm
from .evaluation_forms import EmployeeEvaluationForm

__all__ = [
    # النماذج الموجودة
    'EmployeeForm', 'EmployeeFilterForm', 'DepartmentForm', 'JobForm', 'CarForm', 'EmployeeSearchForm',
    'SalaryItemForm', 'EmployeeSalaryItemForm', 'EmployeeSalaryItemBulkForm',
    'PayrollPeriodForm', 'PayrollCalculationForm',
    'AttendanceRuleForm', 'EmployeeAttendanceRuleForm', 'EmployeeAttendanceRuleBulkForm',
    'OfficialHolidayForm', 'AttendanceMachineForm', 'AttendanceRecordForm',
    'FetchAttendanceDataForm',

    # النماذج الجديدة
    'PickupPointForm', 'JobInsuranceForm', 'EmployeeTaskForm', 'EmployeeNoteForm',
    'EmployeeFileForm', 'HrTaskForm', 'LeaveTypeForm', 'EmployeeLeaveForm',
    'EmployeeEvaluationForm'
]
