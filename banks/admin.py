from django.contrib import admin
from .models import Bank

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    """BankAdmin class"""
    list_display = ('bank_id', 'bank_name', 'swift_code')
    search_fields = ('bank_name', 'swift_code')
