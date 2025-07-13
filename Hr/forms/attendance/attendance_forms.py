"""
Attendance Forms for HRMS
Comprehensive forms for attendance management and tracking
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date, time, timedelta

from Hr.models.attendance.attendance_record_models import AttendanceRecord
from Hr.models.attendance.work_shift_models import WorkShift
from Hr.models.attendance.employee_shift_assignment_models import EmployeeShiftAssignment
from Hr.models.attendance.attendance_summary_models import AttendanceSummary


class AttendanceRecordForm(forms.ModelForm):
    """
    Form for creating and editing attendance records
    """
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'employee', 'record_date', 'record_time', 'record_type',
            'source', 'machine', 'location', 'notes', 'is_manual'
        ]
        
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'record_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'record_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'record_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'source': forms.Select(attrs={
                'class': 'form-select'
            }),
            'machine': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موقع التسجيل'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
            'is_manual': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
        labels = {
            'employee': _('الموظف'),
            'record_date': _('تاريخ التسجيل'),
            'record_time': _('وقت التسجيل'),
            'record_type': _('نوع التسجيل'),
            'source': _('مصدر التسجيل'),
            'machine': _('الجهاز'),
            'location': _('الموقع'),
            'notes': _('ملاحظات'),
            'is_manual': _('تسجيل يدوي')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['record_date'].initial = date.today()
            self.fields['record_time'].initial = timezone.now().time()
        
        # Filter employees to active only
        from Hr.models import Employee
        self.fields['employee'].queryset = Employee.objects.filter(status='active')

    def clean(self):
        """Validate the attendance record"""
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        record_date = cleaned_data.get('record_date')
        record_time = cleaned_data.get('record_time')
        record_type = cleaned_data.get('record_type')
        
        if employee and record_date and record_time:
            # Create datetime for validation
            record_datetime = datetime.combine(record_date, record_time)
            
            # Check for future records
            if record_datetime > timezone.now():
                raise ValidationError(_('لا يمكن تسجيل حضور في المستقبل'))
            
            # Check for duplicate records (within 1 minute)
            existing_records = AttendanceRecord.objects.filter(
                employee=employee,
                record_date=record_date,
                record_time__range=(
                    (datetime.combine(date.min, record_time) - timedelta(minutes=1)).time(),
                    (datetime.combine(date.min, record_time) + timedelta(minutes=1)).time()
                )
            )
            
            if self.instance.pk:
                existing_records = existing_records.exclude(pk=self.instance.pk)
            
            if existing_records.exists():
                raise ValidationError(_('يوجد تسجيل مشابه في نفس الوقت تقريباً'))
        
        return cleaned_data

    def save(self, commit=True):
        """Save the attendance record with additional processing"""
        record = super().save(commit=False)
        
        # Set record_datetime
        if record.record_date and record.record_time:
            record.record_datetime = datetime.combine(record.record_date, record.record_time)
        
        # Set source if not provided
        if not record.source:
            record.source = 'manual' if record.is_manual else 'system'
        
        if commit:
            record.save()
            # Trigger attendance summary update
            record.update_attendance_summary()
        
        return record


class WorkShiftForm(forms.ModelForm):
    """
    Form for creating and editing work shifts
    """
    
    class Meta:
        model = WorkShift
        fields = [
            'name', 'code', 'description', 'shift_type',
            'start_time', 'end_time', 'break_duration',
            'grace_period_in', 'grace_period_out',
            'overtime_threshold', 'is_overnight',
            'working_days', 'is_active'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الوردية',
                'required': True
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود الوردية',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الوردية'
            }),
            'shift_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'break_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 15,
                'placeholder': 'بالدقائق'
            }),
            'grace_period_in': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 5,
                'placeholder': 'بالدقائق'
            }),
            'grace_period_out': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 5,
                'placeholder': 'بالدقائق'
            }),
            'overtime_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 15,
                'placeholder': 'بالدقائق'
            }),
            'is_overnight': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'working_days': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
        labels = {
            'name': _('اسم الوردية'),
            'code': _('كود الوردية'),
            'description': _('الوصف'),
            'shift_type': _('نوع الوردية'),
            'start_time': _('وقت البداية'),
            'end_time': _('وقت النهاية'),
            'break_duration': _('مدة الراحة (دقيقة)'),
            'grace_period_in': _('فترة السماح للدخول (دقيقة)'),
            'grace_period_out': _('فترة السماح للخروج (دقيقة)'),
            'overtime_threshold': _('حد العمل الإضافي (دقيقة)'),
            'is_overnight': _('وردية ليلية'),
            'working_days': _('أيام العمل'),
            'is_active': _('نشط')
        }

    def clean(self):
        """Validate work shift data"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        is_overnight = cleaned_data.get('is_overnight')
        
        if start_time and end_time:
            # For non-overnight shifts, end time should be after start time
            if not is_overnight and end_time <= start_time:
                raise ValidationError(_('وقت النهاية يجب أن يكون بعد وقت البداية'))
            
            # For overnight shifts, validate the logic
            if is_overnight and end_time >= start_time:
                raise ValidationError(_('في الورديات الليلية، وقت النهاية يجب أن يكون قبل وقت البداية'))
        
        return cleaned_data


class AttendanceSearchForm(forms.Form):
    """
    Form for searching and filtering attendance records
    """
    
    employee = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label=_('جميع الموظفين'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('الموظف')
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label=_('من تاريخ')
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label=_('إلى تاريخ')
    )
    
    record_type = forms.ChoiceField(
        choices=[('', _('جميع الأنواع'))] + AttendanceRecord.RECORD_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('نوع التسجيل')
    )
    
    source = forms.ChoiceField(
        choices=[('', _('جميع المصادر'))] + AttendanceRecord.SOURCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('مصدر التسجيل')
    )
    
    department = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label=_('جميع الأقسام'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('القسم')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set employee queryset
        from Hr.models import Employee
        self.fields['employee'].queryset = Employee.objects.filter(status='active').order_by('full_name')
        
        # Set department queryset
        from Hr.models import Department
        self.fields['department'].queryset = Department.objects.filter(is_active=True).order_by('name')
        
        # Set default date range (current month)
        today = date.today()
        first_day = today.replace(day=1)
        self.fields['date_from'].initial = first_day
        self.fields['date_to'].initial = today


class BulkAttendanceForm(forms.Form):
    """
    Form for bulk attendance operations
    """
    
    ACTION_CHOICES = [
        ('approve', _('اعتماد')),
        ('reject', _('رفض')),
        ('delete', _('حذف')),
        ('export', _('تصدير'))
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('الإجراء')
    )
    
    record_ids = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'ملاحظات الإجراء'
        }),
        label=_('ملاحظات')
    )

    def clean_record_ids(self):
        """Validate record IDs"""
        record_ids = self.cleaned_data.get('record_ids', '')
        if not record_ids:
            raise ValidationError(_('لم يتم تحديد أي سجل'))
        
        try:
            ids = [int(id.strip()) for id in record_ids.split(',') if id.strip()]
            if not ids:
                raise ValidationError(_('لم يتم تحديد أي سجل'))
            return ids
        except ValueError:
            raise ValidationError(_('معرفات السجلات غير صحيحة'))
