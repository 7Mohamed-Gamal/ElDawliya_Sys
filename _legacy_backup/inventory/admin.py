# ملف admin.py لتطبيق المخزون
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import TblProducts, TblCustomers, TblCategories, TblSuppliers, TblInvoices, TblInvoiceitems
from .models_local import (
    Category, Product, Supplier, Customer, Department,
    Voucher, VoucherItem, LocalSystemSettings, Unit, PurchaseRequest
)

# النماذج القديمة
@admin.register(TblProducts)
class TblProductsAdmin(admin.ModelAdmin):
    """TblProductsAdmin class"""
    list_display = ['product_id', 'product_name', 'unit_price', 'qte_in_stock']
    search_fields = ['product_name']
    list_filter = ['cat']

@admin.register(TblCustomers)
class TblCustomersAdmin(admin.ModelAdmin):
    """TblCustomersAdmin class"""
    list_display = ['customer_id', 'customer_name']
    search_fields = ['customer_name']

@admin.register(TblCategories)
class TblCategoriesAdmin(admin.ModelAdmin):
    """TblCategoriesAdmin class"""
    list_display = ['cat_id', 'cat_name']
    search_fields = ['cat_name']

@admin.register(TblSuppliers)
class TblSuppliersAdmin(admin.ModelAdmin):
    """TblSuppliersAdmin class"""
    list_display = ['supplier_id', 'supplier_name']
    search_fields = ['supplier_name']

@admin.register(TblInvoices)
class TblInvoicesAdmin(admin.ModelAdmin):
    """TblInvoicesAdmin class"""
    list_display = ['invoice_id', 'invoice_date', 'invoice_type', 'total_invoice_value']
    search_fields = ['invoice_number']
    list_filter = ['invoice_date']
    date_hierarchy = 'invoice_date'

@admin.register(TblInvoiceitems)
class TblInvoiceitemsAdmin(admin.ModelAdmin):
    """TblInvoiceitemsAdmin class"""
    list_display = ['invoice_code_programing', 'invoice_number', 'product_name', 'invoice_date']
    search_fields = ['invoice_number', 'product_name']
    list_filter = ['invoice_date']

# النماذج المحلية
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """CategoryAdmin class"""
    list_display = ['name', 'description']
    search_fields = ['name', 'description']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """ProductAdmin class"""
    list_display = ['product_id', 'name', 'category', 'unit', 'quantity']
    search_fields = ['product_id', 'name', 'description']
    list_filter = ['category', 'unit']
    fieldsets = (
        (_('معلومات المنتج الأساسية'), {
            'fields': ('product_id', 'name', 'description', 'category', 'unit', 'image')
        }),
        (_('معلومات المخزون'), {
            'fields': ('initial_quantity', 'quantity', 'minimum_threshold', 'maximum_threshold')
        }),
        (_('معلومات السعر'), {
            'fields': ('unit_price',)
        }),
        (_('معلومات إضافية'), {
            'fields': ('location',)
        }),
    )

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """SupplierAdmin class"""
    list_display = ['name', 'contact_person', 'phone', 'email']
    search_fields = ['name', 'contact_person', 'phone', 'email']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """CustomerAdmin class"""
    list_display = ['name', 'contact_person', 'phone', 'email']
    search_fields = ['name', 'contact_person', 'phone', 'email']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """DepartmentAdmin class"""
    list_display = ['name', 'description']
    search_fields = ['name', 'description']

class VoucherItemInline(admin.TabularInline):
    """VoucherItemInline class"""
    model = VoucherItem
    extra = 1

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    """VoucherAdmin class"""
    list_display = ['voucher_number', 'voucher_type', 'date', 'supplier', 'department']
    search_fields = ['voucher_number', 'notes']
    list_filter = ['voucher_type', 'date']
    date_hierarchy = 'date'
    inlines = [VoucherItemInline]

@admin.register(VoucherItem)
class VoucherItemAdmin(admin.ModelAdmin):
    """VoucherItemAdmin class"""
    list_display = ['voucher', 'product', 'unit_price']
    search_fields = ['voucher__voucher_number', 'product__name']
    list_filter = ['voucher__voucher_type']

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    """PurchaseRequestAdmin class"""
    list_display = ['product', 'requested_date', 'status']
    search_fields = ['product__name']
    list_filter = ['status', 'requested_date']
    date_hierarchy = 'requested_date'

@admin.register(LocalSystemSettings)
class LocalSystemSettingsAdmin(admin.ModelAdmin):
    """LocalSystemSettingsAdmin class"""
    list_display = ['company_name']

    def has_add_permission(self, request):
        """has_add_permission function"""
        # Only allow one settings object
        return not LocalSystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """has_delete_permission function"""
        # Don't allow deleting the settings object
        return False

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """UnitAdmin class"""
    list_display = ['name', 'symbol']
    search_fields = ['name', 'symbol']
