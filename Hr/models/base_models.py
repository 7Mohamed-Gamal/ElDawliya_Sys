# Base models imports - Updated to use new structure
from django.utils.translation import gettext_lazy as _

# Import from new core models
from Hr.models.core.department_models import Department
from Hr.models.core.company_models import Company
from Hr.models.core.branch_models import Branch
from Hr.models.core.job_position_models import JobPosition

# Import legacy models for backward compatibility
from Hr.models.legacy.legacy_models import (
    LegacyDepartment, Job, JobInsurance, Car
)
