from django.contrib import admin
from .models import AssetCategory, Asset, EmployeeAsset

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    """AssetCategoryAdmin class"""
    list_display = ('category_id', 'category_name')
    search_fields = ('category_name',)

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """AssetAdmin class"""
    list_display = ('asset_id', 'asset_name', 'category', 'status', 'purchase_date')
    list_filter = ('status', 'category')
    search_fields = ('asset_name', 'serial_no')

@admin.register(EmployeeAsset)
class EmployeeAssetAdmin(admin.ModelAdmin):
    """EmployeeAssetAdmin class"""
    list_display = ('emp_asset_id', 'emp', 'asset', 'assigned_date', 'return_date')
    date_hierarchy = 'assigned_date'
