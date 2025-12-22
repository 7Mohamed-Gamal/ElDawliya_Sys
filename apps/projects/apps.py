"""
Projects application configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProjectsConfig(AppConfig):
    """Projects application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.projects'
    verbose_name = _('إدارة المشاريع')

    def ready(self):
        """Import signals when the app is ready."""
        try:
            import apps.projects.signals  # noqa F401
        except ImportError:
            pass
