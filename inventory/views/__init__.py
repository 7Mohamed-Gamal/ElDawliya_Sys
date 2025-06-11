"""
Views package for the inventory application.
This file imports all views from their respective modules to maintain backward compatibility.
"""

# Import all views from their respective modules
from .dashboard_views import *
from .product_views import *
from .category_views import *
from .unit_views import *
from .supplier_views import *
from .customer_views import *
from .department_views import *
from .voucher_views import *
from .purchase_request_views import *
from .report_views import *
from .api_views import *
from .settings_views import *
from .utility_views import *
from .api_functions import *  # Import the new API functions
from .product_movement_views import *  # Import product movement views
