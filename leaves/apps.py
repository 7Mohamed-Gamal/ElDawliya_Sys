from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LeavesConfig(AppConfig):
    """LeavesConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leaves'
    verbose_name = _('الإجازات')
