# Payroll Views Package

from . import salary_component_views
from . import employee_salary_structure_views
from . import payroll_period_views_new
from . import payroll_entry_views_new
from . import payroll_calculation_views
from . import tax_configuration_views

__all__ = [
    'salary_component_views',
    'employee_salary_structure_views',
    'payroll_period_views_new',
    'payroll_entry_views_new',
    'payroll_calculation_views',
    'tax_configuration_views',
]
