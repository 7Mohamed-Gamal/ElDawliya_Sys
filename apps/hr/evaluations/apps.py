from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EvaluationsConfig(AppConfig):
    """EvaluationsConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hr.evaluations'
    verbose_name = _('التقييمات')
