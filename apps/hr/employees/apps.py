from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EmployeesConfig(AppConfig):
    """EmployeesConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hr.employees'
    verbose_name = _('الموظفون')
