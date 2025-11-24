from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReportsConfig(AppConfig):
    """ReportsConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    verbose_name = _('HR Reports System')

    def ready(self):
        """Initialize the reports app."""
        pass
