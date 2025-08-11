from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PayrollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payrolls'
    verbose_name = _('الرواتب')
