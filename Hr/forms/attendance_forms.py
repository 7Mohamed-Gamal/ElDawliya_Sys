from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models import (
    AttendanceRule, EmployeeAttendanceRule, OfficialHoliday,
    AttendanceMachine, AttendanceRecord, Employee
)


class AttendanceRuleForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل قواعد الحضور
    """
    class Meta:
        model = AttendanceRule
        fields = ['name', 'description', 'work_schedule', 'late_grace_minutes', 'early_leave_grace_minutes', 'weekly_off_days', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'work_schedule': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'late_grace_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'early_leave_grace_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'weekly_off_days': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmployeeAttendanceRuleForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل قواعد حضور الموظفين
    """
    class Meta:
        model = EmployeeAttendanceRule
        fields = ['employee', 'attendance_rule', 'effective_date', 'end_date', 'is_active']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'attendance_rule': forms.Select(attrs={'class': 'form-select'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmployeeAttendanceRuleBulkForm(forms.Form):
    """
    نموذج لإنشاء قواعد حضور الموظفين بالجملة
    """
    attendance_rule = forms.ModelChoiceField(
        queryset=AttendanceRule.objects.all(),
        label=_('قاعدة الحضور'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(working_condition='سارى'),
        label=_('الموظفين'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10})
    )
    effective_date = forms.DateField(
        label=_('تاريخ السريان'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label=_('تاريخ الانتهاء'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    is_active = forms.BooleanField(
        label=_('سارى'),
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class OfficialHolidayForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل الإجازات الرسمية
    """
    class Meta:
        model = OfficialHoliday
        fields = ['name', 'date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AttendanceMachineForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل أجهزة الحضور
    """
    class Meta:
        model = AttendanceMachine
        fields = ['name', 'ip_address', 'port', 'machine_type', 'location', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'machine_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AttendanceRecordForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل سجلات الحضور
    """
    class Meta:
        model = AttendanceRecord
        fields = ['employee', 'record_date', 'record_time', 'record_type', 'source', 'machine', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'record_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'record_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'record_type': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'machine': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FetchAttendanceDataForm(forms.Form):
    """
    نموذج لجلب بيانات الحضور من الأجهزة
    """
    machine = forms.ModelChoiceField(
        queryset=AttendanceMachine.objects.filter(is_active=True),
        label=_('ماكينة الحضور'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        label=_('تاريخ البداية'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label=_('تاريخ النهاية'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    clear_existing = forms.BooleanField(
        label=_('مسح السجلات الموجودة'),
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
