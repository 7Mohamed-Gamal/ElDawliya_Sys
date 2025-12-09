from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """
    تكوين تطبيق المخزون
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    verbose_name = 'نظام المخزون'
