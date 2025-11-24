from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorkflowConfig(AppConfig):
    """WorkflowConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workflow'
    verbose_name = _('سير العمل')
