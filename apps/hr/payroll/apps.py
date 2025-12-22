from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PayrollsConfig(AppConfig):
    """PayrollsConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hr.payroll'
    verbose_name = _('الرواتب')
