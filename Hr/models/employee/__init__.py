"""
نماذج الموظفين - تجميع جميع النماذج (القديمة والمحسنة)
"""

# Legacy Employee Models
from .employee_models import Employee
from .employee_experience_models import EmployeeExperience
from .employee_family_models import EmployeeFamily
from .employee_bank_models import EmployeeBank
from .employee_contact_models import EmployeeContact

# Enhanced Employee Models
from .employee_models_enhanced import EmployeeEnhanced
from .employee_education_models import EmployeeEducationEnhanced
from .employee_insurance_models import EmployeeInsuranceEnhanced
from .employee_vehicle_models import EmployeeVehicleEnhanced
from .employee_file_models import EmployeeFileEnhanced, EmployeeFileCategory, EmployeeFileAccessLog
from .employee_emergency_contact_models import EmployeeEmergencyContactEnhanced
from .employee_document_models import EmployeeDocumentEnhanced
from .employee_training_models import EmployeeTrainingEnhanced, TrainingCategory, TrainingProvider

__all__ = [
    # Legacy Models
    'Employee',
    'EmployeeExperience',
    'EmployeeFamily',
    'EmployeeBank',
    'EmployeeContact',
    
    # Enhanced Models
    'EmployeeEnhanced',
    'EmployeeEducationEnhanced', 
    'EmployeeInsuranceEnhanced',
    'EmployeeVehicleEnhanced',
    'EmployeeFileEnhanced',
    'EmployeeFileCategory',
    'EmployeeFileAccessLog',
    'EmployeeEmergencyContactEnhanced',
    'EmployeeDocumentEnhanced',
    'EmployeeTrainingEnhanced',
    'TrainingCategory',
    'TrainingProvider',
]