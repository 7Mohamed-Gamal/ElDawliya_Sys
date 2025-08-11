from django.contrib import admin
from .models import TicketType, EmployeeTicket

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('ticket_type_id', 'type_name', 'max_tickets_per_year')
    search_fields = ('type_name',)

@admin.register(EmployeeTicket)
class EmployeeTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'emp', 'ticket_type', 'destination', 'travel_date', 'status')
    list_filter = ('status', 'ticket_type')
    search_fields = ('emp__emp_code', 'destination')
    date_hierarchy = 'travel_date'
