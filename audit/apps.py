from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuditConfig(AppConfig):
    """AuditConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'
    verbose_name = _('سجلات التدقيق')

    def ready(self):
        """ready function"""
        # Import signals to register them
        import audit.signals
