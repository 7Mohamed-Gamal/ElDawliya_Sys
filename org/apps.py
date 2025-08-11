from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrgConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'org'
    verbose_name = _('الهيكل التنظيمي')
