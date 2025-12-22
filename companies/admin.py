from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """CompanyAdmin class"""
    list_display = ('company_id', 'name', 'tax_number', 'is_active')
    search_fields = ('name', 'tax_number', 'commercial_register')
    list_filter = ('is_active',)

# Register your models here.
