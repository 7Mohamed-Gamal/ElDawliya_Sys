from django.contrib import admin
from .models import PurchaseRequest, PurchaseRequestItem, Vendor

class PurchaseRequestItemInline(admin.TabularInline):
    model = PurchaseRequestItem
    extra = 0

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'request_date', 'requested_by', 'status', 'approved_by')
    list_filter = ('status', 'request_date')
    search_fields = ('request_number', 'requested_by__username', 'notes')
    inlines = [PurchaseRequestItemInline]
    readonly_fields = ('request_date',)

@admin.register(PurchaseRequestItem)
class PurchaseRequestItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_request', 'product', 'quantity_requested', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('product__product_name', 'notes')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email')
    search_fields = ('name', 'contact_person', 'phone', 'email', 'address')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
