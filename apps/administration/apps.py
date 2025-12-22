"""
Administration application configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AdministrationConfig(AppConfig):
    """Administration application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.administration'
    verbose_name = _('الإدارة العامة')

    def ready(self):
        """Import signals when the app is ready."""
        try:
            import apps.administration.signals  # noqa F401
        except ImportError:
            pass
