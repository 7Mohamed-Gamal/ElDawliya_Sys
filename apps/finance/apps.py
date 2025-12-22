"""
Finance application configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FinanceConfig(AppConfig):
    """Finance application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance'
    verbose_name = _('إدارة المالية')

    def ready(self):
        """Import signals when the app is ready."""
        try:
            import apps.finance.signals  # noqa F401
        except ImportError:
            pass
