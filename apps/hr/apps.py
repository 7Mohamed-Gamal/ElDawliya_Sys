"""
HR application configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HrConfig(AppConfig):
    """HR application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hr'
    verbose_name = _('إدارة الموارد البشرية')
    
    def ready(self):
        """Import signals when the app is ready."""
        try:
            import apps.hr.signals  # noqa F401
        except ImportError:
            pass