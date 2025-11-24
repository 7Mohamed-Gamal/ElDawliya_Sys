from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationsConfig(AppConfig):
    """NotificationsConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = _('التنبيهات')

    def ready(self):
        """ready function"""
        # استيراد إشارات التنبيهات
        import notifications.signals
