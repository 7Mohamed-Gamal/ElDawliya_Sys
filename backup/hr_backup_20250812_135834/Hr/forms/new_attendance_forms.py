# =============================================================================
# ElDawliya HR Management System - Attendance Forms
# =============================================================================
# Forms for attendance and time tracking management
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Submit, HTML
from crispy_forms.bootstrap import Field, FormActions
from datetime import date, time, datetime, timedelta

from Hr.models import (
    WorkShift, AttendanceMachine, EmployeeShiftAssignment,
    AttendanceRecord, Employee, Company, Branch
)


class WorkShiftForm(forms.ModelForm):
    """نموذج إنشاء وتحديث الوردية"""
    
    class Meta:
        model = WorkShift
        fields = [
            'company', 'name', 'shift_type', 'start_time', 'end_time',
            'break_duration', 'grace_period_minutes', 'overtime_threshold_minutes', 'is_active'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم الوردية'),
                'dir': 'rtl'
            }),
            'shift_type': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'break_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('مثال: 01:00:00 (ساعة واحدة)')
            }),
            'grace_period_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('بالدقائق'),
                'min': '0',
                'max': '60'
            }),
            'overtime_threshold_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('بالدقائق'),
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        
        self.helper.layout = Layout(
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-clock me-2"></i>معلومات الوردية الأساسية</h4>'),
                Row(
                    Column('company', css_class='col-md-6'),
                    Column('name', css_class='col-md-6'),
                ),
                'shift_type',
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-calendar-clock me-2"></i>أوقات العمل</h4>'),
                Row(
                    Column('start_time', css_class='col-md-6'),
                    Column('end_time', css_class='col-md-6'),
                ),
                'break_duration',
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-cog me-2"></i>إعدادات الحضور</h4>'),
                Row(
                    Column('grace_period_minutes', css_class='col-md-6'),
                    Column('overtime_threshold_minutes', css_class='col-md-6'),
                ),
                'is_active',
                css_class='card-body mb-3'
            ),
            FormActions(
                Submit('submit', _('حفظ الوردية'), css_class='btn btn-primary'),
                HTML('<a href="{% url "hr:workshift_list" %}" class="btn btn-secondary ms-2">إلغاء</a>'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            # Convert to datetime for comparison
            start_dt = datetime.combine(date.today(), start_time)
            end_dt = datetime.combine(date.today(), end_time)
            
            # Handle overnight shifts
            if end_time < start_time:
                end_dt += timedelta(days=1)
            
            # Check minimum shift duration (2 hours)
            if (end_dt - start_dt).total_seconds() < 2 * 3600:
                raise ValidationError(_('يجب أن تكون مدة الوردية ساعتين على الأقل'))
        
        return cleaned_data


class AttendanceMachineForm(forms.ModelForm):
    """نموذج إنشاء وتحديث جهاز الحضور"""
    
    class Meta:
        model = AttendanceMachine
        fields = [
            'company', 'branch', 'name', 'machine_type', 'ip_address',
            'port', 'location', 'serial_number', 'is_active'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم الجهاز'),
                'dir': 'rtl'
            }),
            'machine_type': forms.Select(attrs={'class': 'form-select'}),
            'ip_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('مثال: 192.168.1.100')
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('مثال: 4370'),
                'min': '1',
                'max': '65535'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('موقع الجهاز'),
                'dir': 'rtl'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الرقم التسلسلي للجهاز')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Row(
                Column('company', css_class='col-md-6'),
                Column('branch', css_class='col-md-6'),
            ),
            Row(
                Column('name', css_class='col-md-6'),
                Column('machine_type', css_class='col-md-6'),
            ),
            Row(
                Column('ip_address', css_class='col-md-6'),
                Column('port', css_class='col-md-6'),
            ),
            Row(
                Column('location', css_class='col-md-6'),
                Column('serial_number', css_class='col-md-6'),
            ),
            'is_active',
            FormActions(
                Submit('submit', _('حفظ الجهاز'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class EmployeeShiftAssignmentForm(forms.ModelForm):
    """نموذج تعيين الوردية للموظف"""
    
    class Meta:
        model = EmployeeShiftAssignment
        fields = [
            'employee', 'work_shift', 'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'work_shift': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        
        if employee:
            self.fields['employee'].initial = employee
            # Filter work shifts by employee's company
            self.fields['work_shift'].queryset = WorkShift.objects.filter(
                company=employee.company, is_active=True
            )
        
        # Set default start date to today
        if not self.instance.pk:
            self.fields['start_date'].initial = date.today()
            self.fields['is_active'].initial = True
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            'employee',
            'work_shift',
            Row(
                Column('start_date', css_class='col-md-6'),
                Column('end_date', css_class='col-md-6'),
            ),
            'is_active',
            FormActions(
                Submit('submit', _('تعيين الوردية'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        employee = cleaned_data.get('employee')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية'))
        
        # Check for overlapping assignments
        if employee and start_date:
            overlapping = EmployeeShiftAssignment.objects.filter(
                employee=employee,
                is_active=True,
                start_date__lte=end_date or date(9999, 12, 31),
                end_date__gte=start_date
            )
            
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            
            if overlapping.exists():
                raise ValidationError(_('يوجد تعيين وردية متداخل مع هذه الفترة'))
        
        return cleaned_data


class AttendanceRecordForm(forms.ModelForm):
    """نموذج تسجيل الحضور اليدوي"""
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'employee', 'date', 'attendance_type', 'timestamp',
            'status', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'attendance_type': forms.Select(attrs={'class': 'form-select'}),
            'timestamp': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('ملاحظات إضافية'),
                'dir': 'rtl'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default values
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
            self.fields['timestamp'].initial = datetime.now()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            'employee',
            Row(
                Column('date', css_class='col-md-6'),
                Column('attendance_type', css_class='col-md-6'),
            ),
            Row(
                Column('timestamp', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            'notes',
            FormActions(
                Submit('submit', _('تسجيل الحضور'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        date_field = cleaned_data.get('date')
        timestamp = cleaned_data.get('timestamp')
        
        if date_field and timestamp:
            # Ensure timestamp date matches the date field
            if timestamp.date() != date_field:
                raise ValidationError(_('تاريخ الوقت يجب أن يطابق التاريخ المحدد'))
        
        return cleaned_data


class AttendanceReportForm(forms.Form):
    """نموذج تقرير الحضور"""
    
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        empty_label=_('جميع الشركات'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.filter(is_active=True),
        required=False,
        empty_label=_('جميع الفروع'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='active'),
        required=False,
        empty_label=_('جميع الموظفين'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', _('جميع الحالات'))] + AttendanceRecord.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default date range (current month)
        today = date.today()
        first_day = today.replace(day=1)
        self.fields['start_date'].initial = first_day
        self.fields['end_date'].initial = today
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row g-3'
        
        self.helper.layout = Layout(
            Row(
                Column('company', css_class='col-md-2'),
                Column('branch', css_class='col-md-2'),
                Column('employee', css_class='col-md-2'),
                Column('start_date', css_class='col-md-2'),
                Column('end_date', css_class='col-md-2'),
                Column('status', css_class='col-md-2'),
            ),
            Row(
                Column(
                    Submit('generate_report', _('إنشاء التقرير'), css_class='btn btn-primary'),
                    Submit('export_excel', _('تصدير Excel'), css_class='btn btn-success ms-2'),
                    css_class='col-12 text-center'
                )
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية'))
            
            # Limit report range to 1 year
            if (end_date - start_date).days > 365:
                raise ValidationError(_('لا يمكن أن تتجاوز فترة التقرير سنة واحدة'))
        
        return cleaned_data
