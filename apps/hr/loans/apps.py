from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LoansConfig(AppConfig):
    """LoansConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hr.loans'
    verbose_name = _('السلف')
