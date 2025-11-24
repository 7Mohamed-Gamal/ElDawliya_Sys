from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SyssettingsConfig(AppConfig):
    """SyssettingsConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'syssettings'
    verbose_name = _('الإعدادات العامة')
