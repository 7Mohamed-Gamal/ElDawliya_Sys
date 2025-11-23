"""
Inventory application configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InventoryConfig(AppConfig):
    """Inventory application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'
    verbose_name = _('إدارة المخزون')
    
    def ready(self):
        """Import signals when the app is ready."""
        try:
            import apps.inventory.signals  # noqa F401
        except ImportError:
            pass