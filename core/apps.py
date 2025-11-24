from django.apps import AppConfig


class CoreConfig(AppConfig):
    """CoreConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """ready function"""
        # Import the custom collations module to register the collations
        import core.db_collations

        # Import synchronization signals to register them
        import core.synchronization
