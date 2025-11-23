"""
Procurement application configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProcurementConfig(AppConfig):
    """Procurement application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.procurement'
    verbose_name = _('إدارة المشتريات')
    
    def ready(self):
        """Import signals when the app is ready."""
        try:
            import apps.procurement.signals  # noqa F401
        except ImportError:
            pass