"""
Finance API URLs.
"""

from django.urls import path, include
from django.views.generic import RedirectView

app_name = 'finance'

urlpatterns = [
    path('banks/', include('apps.finance.banks.urls')),
    
    # Aliases for dashboard links
    # 'finance:accounts' in dashboard likely refers to bank accounts or general accounts
    # Redirecting to bank list for now
    path('accounts/', RedirectView.as_view(pattern_name='finance:banks:list', permanent=False), name='accounts'),
    
    # 'finance:invoices' - Placeholder, redirect to dashboard or banks for now
    path('invoices/', RedirectView.as_view(pattern_name='finance:banks:list', permanent=False), name='invoices'),
    
    # 'finance:reports' - Placeholder
    path('reports/', RedirectView.as_view(pattern_name='finance:banks:list', permanent=False), name='reports'),
]