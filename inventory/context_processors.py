from django.db.models import F
from django.db import connection, OperationalError
from django.conf import settings
from .models import TblProducts

def inventory_stats(request):
    """
    Add inventory stats to the template context for all views.
    Specifically, the count of products with quantity below minimum threshold.
    """
    # Default value
    low_stock_count = 0

    # Only calculate if the user is authenticated to avoid unnecessary DB queries
    if request.user.is_authenticated:
        # Check if we're using SQLite (development mode)
        using_sqlite = 'sqlite' in settings.DATABASES['default']['ENGINE']

        if not using_sqlite:  # Only try to access the table if not using SQLite
            try:
                # Try to access the table
                low_stock_count = TblProducts.objects.filter(
                    qte_in_stock__lt=F('minimum_threshold'),
                    minimum_threshold__isnull=False
                ).exclude(minimum_threshold=0).count()
            except OperationalError:
                # Table doesn't exist or other database error
                low_stock_count = 0

    return {'low_stock_count': low_stock_count}
