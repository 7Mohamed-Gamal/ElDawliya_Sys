from django.db import models
from apps.hr.employees.models import Employee


class TicketType(models.Model):
    """TicketType class"""
    ticket_type_id = models.AutoField(primary_key=True, db_column='TicketTypeID')
    type_name = models.CharField(max_length=100, db_column='TypeName')
    max_tickets_per_year = models.IntegerField(db_column='MaxTicketsPerYear', blank=True, null=True)

    class Meta:
        """Meta class"""
        db_table = 'TicketTypes'
        verbose_name = 'نوع تذكرة'
        verbose_name_plural = 'أنواع التذاكر'


class EmployeeTicket(models.Model):
    """EmployeeTicket class"""
    ticket_id = models.AutoField(primary_key=True, db_column='TicketID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT, db_column='TicketTypeID', blank=True, null=True)
    destination = models.CharField(max_length=100, db_column='Destination', blank=True, null=True)
    travel_date = models.DateField(db_column='TravelDate', blank=True, null=True)
    return_date = models.DateField(db_column='ReturnDate', blank=True, null=True)
    status = models.CharField(max_length=30, db_column='Status', default='Requested')
    approved_by = models.IntegerField(db_column='ApprovedBy', blank=True, null=True)

    class Meta:
        """Meta class"""
        db_table = 'EmployeeTickets'
        verbose_name = 'تذكرة موظف'
        verbose_name_plural = 'تذاكر الموظفين'

# Create your models here.
