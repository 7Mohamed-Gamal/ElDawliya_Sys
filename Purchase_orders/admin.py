from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PurchaseRequest, PurchaseRequestItem, Vendor

class PurchaseRequestItemInline(admin.TabularInline):
    model = PurchaseRequestItem
    extra = 0
    fields = ('product', 'quantity_requested', 'status', 'notes')
    readonly_fields = ()

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'request_date', 'requested_by', 'status', 'approved_by')
    list_filter = ('status', 'request_date')
    search_fields = ('request_number', 'requested_by__username', 'notes')
    inlines = [PurchaseRequestItemInline]
    readonly_fields = ('request_date', 'requested_by')

    fieldsets = (
        (_('معلومات الطلب'), {
            'fields': ('request_number', 'request_date', 'requested_by')
        }),
        (_('حالة الطلب'), {
            'fields': ('status', 'approved_by', 'approval_date')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان إنشاء جديد
            obj.requested_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # السماح للمستخدم بتعديل الطلبات التي أنشأها أو للمشرفين
        if obj is not None and (obj.requested_by == request.user or request.user.is_superuser or request.user.has_perm('Purchase_orders.change_purchaserequest')):
            return True
        return super().has_change_permission(request, obj)

@admin.register(PurchaseRequestItem)
class PurchaseRequestItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_request', 'product', 'quantity_requested', 'status')
    list_filter = ('status', 'created_at', 'purchase_request__status')
    search_fields = ('product__product_name', 'notes', 'purchase_request__request_number')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('معلومات الطلب'), {
            'fields': ('purchase_request', 'product')
        }),
        (_('الكمية'), {
            'fields': ('quantity_requested',)
        }),
        (_('الحالة'), {
            'fields': ('status', 'notes')
        }),
        (_('التواريخ'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def has_change_permission(self, request, obj=None):
        # السماح للمستخدم بتعديل عناصر الطلبات التي أنشأها أو للمشرفين
        if obj is not None and (obj.purchase_request.requested_by == request.user or request.user.is_superuser or request.user.has_perm('Purchase_orders.change_purchaserequestitem')):
            return True
        return super().has_change_permission(request, obj)



@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email')
    search_fields = ('name', 'contact_person', 'phone', 'email', 'address')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('معلومات المورد'), {
            'fields': ('name', 'contact_person', 'phone', 'email', 'address')
        }),
        (_('التواريخ'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
