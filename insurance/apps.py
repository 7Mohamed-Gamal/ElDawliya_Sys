from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InsuranceConfig(AppConfig):
    """InsuranceConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'insurance'
    verbose_name = _('التأمينات')
