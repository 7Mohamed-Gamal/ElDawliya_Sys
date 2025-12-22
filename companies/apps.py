from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CompaniesConfig(AppConfig):
    """CompaniesConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'companies'
    verbose_name = _('الشركات')
