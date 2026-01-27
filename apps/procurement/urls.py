"""
Procurement API URLs.
"""

from django.urls import path, include
from django.views.generic import RedirectView

app_name = 'procurement'

urlpatterns = [
    path('purchase-orders/', include('apps.procurement.purchase_orders.urls')),
    
    # Aliases for dashboard links
    # 'procurement:contracts' -> Redirect to purchase orders dashboard
    path('contracts/', RedirectView.as_view(pattern_name='procurement:Purchase_orders:dashboard', permanent=False), name='contracts'),
    
    # 'procurement:tenders' -> Redirect to purchase orders dashboard
    path('tenders/', RedirectView.as_view(pattern_name='procurement:Purchase_orders:dashboard', permanent=False), name='tenders'),
    
    # 'procurement:suppliers' -> Redirect to vendors list in purchase_orders
    path('suppliers/', RedirectView.as_view(pattern_name='procurement:Purchase_orders:vendors', permanent=False), name='suppliers'),
]