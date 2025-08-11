from django import forms
from .models import LeaveType, EmployeeLeave, PublicHoliday

class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['leave_name', 'max_days_per_year', 'is_paid']

class EmployeeLeaveForm(forms.ModelForm):
    class Meta:
        model = EmployeeLeave
        fields = ['emp', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'approved_by', 'approved_date']
        widgets = {
            'approved_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class PublicHolidayForm(forms.ModelForm):
    class Meta:
        model = PublicHoliday
        fields = ['holiday_date', 'description']
        widgets = {
            'holiday_date': forms.DateInput(attrs={'type': 'date'})
        }

