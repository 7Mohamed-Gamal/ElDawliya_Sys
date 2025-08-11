from django.contrib import admin
from .models import SysSetting

@admin.register(SysSetting)
class SysSettingAdmin(admin.ModelAdmin):
    list_display = ('setting_id', 'setting_key', 'setting_value')
    search_fields = ('setting_key',)
