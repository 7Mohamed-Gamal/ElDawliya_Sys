from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.attendance_models import (
    AttendanceRule, EmployeeAttendanceRule, OfficialHoliday,
    AttendanceMachine, AttendanceRecord
)
from Hr.models.employee_model import Employee


class AttendanceRuleForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل قواعد الحضور
    """
    WEEKDAY_CHOICES = [
        (0, _('الاثنين')),
        (1, _('الثلاثاء')), 
        (2, _('الأربعاء')),
        (3, _('الخميس')),
        (4, _('الجمعة')),
        (5, _('السبت')),
        (6, _('الأحد')),
    ]

    weekdays = forms.MultipleChoiceField(
        choices=WEEKDAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label=_('أيام الإجازة الأسبوعية')
    )

    class Meta:
        model = AttendanceRule
        fields = [
            'name', 'description', 'late_grace_minutes', 'early_leave_grace_minutes',
            'work_schedule', 'weekly_off_days', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'late_grace_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'early_leave_grace_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'work_schedule': forms.Textarea(attrs={'rows': 3}),
            'weekly_off_days': forms.SelectMultiple(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['weekdays'].initial = self.instance.get_weekly_off_days()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.weekly_off_days = self.cleaned_data.get('weekdays', [])
        
        # Initialize empty work schedule
        work_schedule = {}
        # Get the schedule data from POST
        for day in range(7):
            start_time = self.data.get(f'start_time_{day}')
            end_time = self.data.get(f'end_time_{day}')
            if start_time and end_time:
                work_schedule[str(day)] = {
                    'start_time': start_time,
                    'end_time': end_time
                }
        
        instance.work_schedule = work_schedule
        
        if commit:
            instance.save()
        return instance


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
        queryset=AttendanceRule.objects.filter(is_active=True),
        label=_('قاعدة الحضور'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(working_condition='سارى'),
        label=_('الموظفين'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    effective_date = forms.DateField(
        label=_('تاريخ السريان'),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        label=_('تاريخ الانتهاء'),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        label=_('نشط'),
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
        fields = ['name', 'date', 'description', 'is_recurring']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'})
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
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('موقع الجهاز')}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AttendanceRecordForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل سجلات الحضور
    """
    class Meta:
        model = AttendanceRecord
        fields = ['employee', 'record_date', 'record_time', 'record_type', 'machine', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'record_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'record_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'record_type': forms.Select(attrs={'class': 'form-select'}),
            'machine': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class FetchAttendanceDataForm(forms.Form):
    """
    نموذج لجلب بيانات الحضور من الأجهزة
    """
    machine = forms.ModelChoiceField(
        queryset=AttendanceMachine.objects.filter(is_active=True),
        label=_('جهاز البصمة'),
        empty_label=_('-- اختر جهاز البصمة --'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        label=_('تاريخ البداية'),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        label=_('تاريخ النهاية'),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    clear_existing = forms.BooleanField(
        label=_('حذف السجلات الموجودة'),
        required=False,
        initial=False,
        help_text=_('احذف أي سجلات موجودة في نفس الفترة قبل جلب البيانات الجديدة'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
