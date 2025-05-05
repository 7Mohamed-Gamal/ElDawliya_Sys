# ملف admin.py لتطبيق المخزون
from django.contrib import admin
from .models import TblProducts, TblCustomers, TblCategories, TblSuppliers, TblInvoices, TblInvoiceitems
from .models_local import (
    Category, Product, Supplier, Customer, Department,
    Voucher, VoucherItem, LocalSystemSettings, Unit, PurchaseRequest
)

# تسجيل النماذج القديمة
admin.site.register(TblProducts)
admin.site.register(TblCustomers)
admin.site.register(TblCategories)
admin.site.register(TblSuppliers)
admin.site.register(TblInvoices)
admin.site.register(TblInvoiceitems)

# تسجيل النماذج المحلية
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Department)
admin.site.register(Voucher)
admin.site.register(VoucherItem)
admin.site.register(PurchaseRequest)
admin.site.register(LocalSystemSettings)
admin.site.register(Unit)
