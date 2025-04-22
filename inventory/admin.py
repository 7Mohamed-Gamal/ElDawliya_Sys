# inventory/admin.py
from django.contrib import admin
from .models import TblProducts, TblCustomers, TblCategories, TblSuppliers, TblInvoices, TblInvoiceitems

admin.site.register(TblProducts)
admin.site.register(TblCustomers)
admin.site.register(TblCategories)
admin.site.register(TblSuppliers)
admin.site.register(TblInvoices)
admin.site.register(TblInvoiceitems)