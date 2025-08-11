from django import forms
from .models import AttendanceRules, EmployeeAttendance


class AttendanceRulesForm(forms.ModelForm):
    class Meta:
        model = AttendanceRules
        fields = [
            'rule_name', 'shift_start', 'shift_end', 'late_threshold',
            'early_threshold', 'overtime_start_after', 'week_end_days', 'is_default'
        ]
        widgets = {
            'shift_start': forms.TimeInput(attrs={'type': 'time'}),
            'shift_end': forms.TimeInput(attrs={'type': 'time'}),
            'overtime_start_after': forms.TimeInput(attrs={'type': 'time'}),
        }


class EmployeeAttendanceForm(forms.ModelForm):
    class Meta:
        model = EmployeeAttendance
        fields = [
            'emp', 'att_date', 'check_in', 'check_out', 'status', 'rule'
        ]
        widgets = {
            'att_date': forms.DateInput(attrs={'type': 'date'}),
            'check_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

