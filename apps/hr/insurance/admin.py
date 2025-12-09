from django.contrib import admin
from .models import HealthInsuranceProvider, EmployeeHealthInsurance, EmployeeSocialInsurance

@admin.register(HealthInsuranceProvider)
class HealthInsuranceProviderAdmin(admin.ModelAdmin):
    """HealthInsuranceProviderAdmin class"""
    list_display = ('provider_id', 'provider_name', 'contact_no')
    search_fields = ('provider_name',)

@admin.register(EmployeeHealthInsurance)
class EmployeeHealthInsuranceAdmin(admin.ModelAdmin):
    """EmployeeHealthInsuranceAdmin class"""
    list_display = ('ins_id', 'emp', 'provider', 'policy_no', 'start_date', 'end_date')
    search_fields = ('emp__emp_code', 'policy_no')
    date_hierarchy = 'start_date'

@admin.register(EmployeeSocialInsurance)
class EmployeeSocialInsuranceAdmin(admin.ModelAdmin):
    """EmployeeSocialInsuranceAdmin class"""
    list_display = ('social_id', 'emp', 'gosi_no', 'start_date', 'end_date', 'contribution')
    search_fields = ('emp__emp_code', 'gosi_no')
    date_hierarchy = 'start_date'
