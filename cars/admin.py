from django.contrib import admin
from .models import Car, Trip, Settings, Supplier, RoutePoint

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email')
    search_fields = ('name', 'contact_person', 'phone', 'email')
    ordering = ('name',)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('car_code', 'car_name', 'car_type', 'supplier', 'fuel_type', 'passengers_count', 'car_status')
    list_filter = ('car_type', 'fuel_type', 'car_status', 'supplier')
    search_fields = ('car_code', 'car_name', 'supplier__name')
    ordering = ('car_code',)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('date', 'car', 'distance', 'fuel_cost', 'final_price')
    list_filter = ('date', 'car__car_type', 'car__supplier')
    date_hierarchy = 'date'
    ordering = ('-date',)
    
    def has_change_permission(self, request, obj=None):
        # Allow viewing but not editing via admin (calculations are handled by model)
        if request.method == 'GET':
            return True
        return False


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('diesel_price', 'gasoline_price', 'gas_price', 'maintenance_rate', 'tax_rate', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one Settings object
        return not Settings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deleting the Settings object
        return False

admin.site.register(RoutePoint)
