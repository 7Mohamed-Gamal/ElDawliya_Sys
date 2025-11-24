from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DisciplinaryConfig(AppConfig):
    """DisciplinaryConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'disciplinary'
    verbose_name = _('الانضباط')
