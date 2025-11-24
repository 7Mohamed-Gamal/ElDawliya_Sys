"""
نماذج (Forms) نظام الحضور والانصراف
Attendance Management Forms
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date, time
from .models import (
    AttendanceRules,
    EmployeeAttendance,
    ZKDevice,
    EmployeeDeviceMapping,
    AttendanceSummary,
    AttendanceRecord,
    LeaveBalance,
    EmployeeAttendanceProfile
)
from employees.models import Employee


class AttendanceRulesForm(forms.ModelForm):
    """نموذج إضافة/تعديل قواعد الحضور"""

    class Meta:
        """Meta class"""
        model = AttendanceRules
        fields = [
            'rule_name', 'shift_start', 'shift_end',
            'late_threshold', 'early_threshold',
            'overtime_start_after', 'week_end_days', 'is_default'
        ]

        widgets = {
            'rule_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم القاعدة'
            }),
            'shift_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'shift_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'late_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'بالدقائق',
                'min': 0
            }),
            'early_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'بالدقائق',
                'min': 0
            }),
            'overtime_start_after': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'week_end_days': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: الجمعة,السبت'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        labels = {
            'rule_name': 'اسم القاعدة',
            'shift_start': 'بداية الوردية',
            'shift_end': 'نهاية الوردية',
            'late_threshold': 'حد التأخير (دقائق)',
            'early_threshold': 'حد المغادرة المبكرة (دقائق)',
            'overtime_start_after': 'بداية الوقت الإضافي',
            'week_end_days': 'أيام نهاية الأسبوع',
            'is_default': 'قاعدة افتراضية'
        }

    def clean(self):
        """clean function"""
        cleaned_data = super().clean()
        shift_start = cleaned_data.get('shift_start')
        shift_end = cleaned_data.get('shift_end')
        overtime_start = cleaned_data.get('overtime_start_after')

        if shift_start and shift_end:
            if shift_start >= shift_end:
                raise ValidationError('وقت بداية الوردية يجب أن يكون قبل وقت النهاية')

        if overtime_start and shift_end:
            if overtime_start <= shift_end:
                raise ValidationError('بداية الوقت الإضافي يجب أن تكون بعد نهاية الوردية')

        return cleaned_data


class EmployeeAttendanceForm(forms.ModelForm):
    """نموذج إضافة/تعديل سجل حضور الموظف"""

    class Meta:
        """Meta class"""
        model = EmployeeAttendance
        fields = ['emp', 'att_date', 'check_in', 'check_out', 'status', 'rule']

        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'اختر الموظف'
            }),
            'att_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'check_in': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'check_out': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'rule': forms.Select(attrs={
                'class': 'form-control'
            })
        }

        labels = {
            'emp': 'الموظف',
            'att_date': 'التاريخ',
            'check_in': 'وقت الدخول',
            'check_out': 'وقت الخروج',
            'status': 'الحالة',
            'rule': 'قاعدة الحضور'
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # تحديد خيارات الموظفين النشطين
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('emp_code')

        # تحديد خيارات قواعد الحضور
        self.fields['rule'].queryset = AttendanceRules.objects.all()

        # خيارات الحالة
        STATUS_CHOICES = [
            ('Present', 'حاضر'),
            ('Absent', 'غائب'),
            ('Late', 'متأخر'),
            ('EarlyLeave', 'مغادرة مبكرة'),
            ('Holiday', 'عطلة'),
            ('Leave', 'إجازة')
        ]
        self.fields['status'].choices = STATUS_CHOICES

    def clean(self):
        """clean function"""
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        att_date = cleaned_data.get('att_date')

        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError('وقت الدخول يجب أن يكون قبل وقت الخروج')

        if att_date and att_date > date.today():
            raise ValidationError('لا يمكن تسجيل حضور لتاريخ مستقبلي')

        return cleaned_data


class ZKDeviceForm(forms.ModelForm):
    """نموذج إضافة/تعديل جهاز ZK"""

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        # Make timezone field optional
        self.fields['timezone'].required = False

    class Meta:
        """Meta class"""
        model = ZKDevice
        fields = [
            'device_name', 'device_serial', 'ip_address',
            'port', 'location', 'status', 'timezone'
        ]

        widgets = {
            'device_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم الجهاز'
            }),
            'device_serial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الرقم التسلسلي للجهاز'
            }),
            'ip_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '192.168.1.100'
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 4370,
                'min': 1,
                'max': 65535
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موقع الجهاز'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'timezone': forms.Select(attrs={
                'class': 'form-control'
            })
        }

        labels = {
            'device_name': 'اسم الجهاز',
            'device_serial': 'الرقم التسلسلي',
            'ip_address': 'عنوان IP',
            'port': 'المنفذ',
            'location': 'الموقع',
            'status': 'الحالة',
            'timezone': 'المنطقة الزمنية'
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # خيارات المنطقة الزمنية
        TIMEZONE_CHOICES = [
            ('Asia/Riyadh', 'توقيت الرياض'),
            ('Asia/Dubai', 'توقيت دبي'),
            ('Asia/Kuwait', 'توقيت الكويت'),
            ('Asia/Qatar', 'توقيت قطر'),
            ('Asia/Bahrain', 'توقيت البحرين'),
            ('UTC', 'التوقيت العالمي')
        ]
        self.fields['timezone'].choices = TIMEZONE_CHOICES

    def clean_ip_address(self):
        """clean_ip_address function"""
        ip_address = self.cleaned_data['ip_address']

        # التحقق من صحة عنوان IP
        import re
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

        if not re.match(ip_pattern, ip_address):
            raise ValidationError('عنوان IP غير صحيح')

        return ip_address


class EmployeeDeviceMappingForm(forms.ModelForm):
    """نموذج ربط الموظف بجهاز ZK"""

    class Meta:
        """Meta class"""
        model = EmployeeDeviceMapping
        fields = ['employee', 'device', 'device_user_id', 'is_active']

        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'اختر الموظف'
            }),
            'device': forms.Select(attrs={
                'class': 'form-control',
                'data-placeholder': 'اختر الجهاز'
            }),
            'device_user_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'معرف المستخدم في الجهاز'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        labels = {
            'employee': 'الموظف',
            'device': 'الجهاز',
            'device_user_id': 'معرف المستخدم في الجهاز',
            'is_active': 'نشط'
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # تحديد الموظفين النشطين
        self.fields['employee'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('emp_code')

        # تحديد الأجهزة النشطة
        self.fields['device'].queryset = ZKDevice.objects.filter(
            status='active'
        ).order_by('device_name')

    def clean(self):
        """clean function"""
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        device = cleaned_data.get('device')
        device_user_id = cleaned_data.get('device_user_id')

        if employee and device and device_user_id:
            # التحقق من عدم تكرار الربط
            existing = EmployeeDeviceMapping.objects.filter(
                device=device,
                device_user_id=device_user_id
            ).exclude(pk=self.instance.pk if self.instance else None)

            if existing.exists():
                raise ValidationError('معرف المستخدم مستخدم بالفعل في هذا الجهاز')

        return cleaned_data


class AttendanceFilterForm(forms.Form):
    """نموذج تصفية سجلات الحضور"""

    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(emp_status='Active').order_by('emp_code'),
        required=False,
        empty_label='جميع الموظفين',
        widget=forms.Select(attrs={
            'class': 'form-control select2'
        }),
        label='الموظف'
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='من تاريخ'
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='إلى تاريخ'
    )

    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + [
            ('Present', 'حاضر'),
            ('Absent', 'غائب'),
            ('Late', 'متأخر'),
            ('EarlyLeave', 'مغادرة مبكرة'),
            ('Holiday', 'عطلة'),
            ('Leave', 'إجازة')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='الحالة'
    )

    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم القسم'
        }),
        label='القسم'
    )


class QuickAttendanceForm(forms.Form):
    """نموذج تسجيل الحضور السريع"""

    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(emp_status='Active').order_by('emp_code'),
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'اختر الموظف'
        }),
        label='الموظف'
    )

    action = forms.ChoiceField(
        choices=[
            ('check_in', 'تسجيل دخول'),
            ('check_out', 'تسجيل خروج')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='نوع التسجيل'
    )


class BulkAttendanceForm(forms.Form):
    """نموذج تسجيل الحضور بالجملة"""

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='التاريخ'
    )

    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(emp_status='Active').order_by('emp_code'),
        widget=forms.CheckboxSelectMultiple(),
        label='الموظفين'
    )

    status = forms.ChoiceField(
        choices=[
            ('Present', 'حاضر'),
            ('Absent', 'غائب'),
            ('Holiday', 'عطلة'),
            ('Leave', 'إجازة')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='الحالة'
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'ملاحظات إضافية'
        }),
        label='ملاحظات'
    )


class AttendanceReportForm(forms.Form):
    """نموذج تقرير الحضور"""

    REPORT_TYPE_CHOICES = [
        ('daily', 'تقرير يومي'),
        ('weekly', 'تقرير أسبوعي'),
        ('monthly', 'تقرير شهري'),
        ('custom', 'فترة مخصصة')
    ]

    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'toggleDateFields()'
        }),
        label='نوع التقرير'
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='من تاريخ'
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='إلى تاريخ'
    )

    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(emp_status='Active').order_by('emp_code'),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'multiple': True,
            'data-placeholder': 'اختر الموظفين (اختياري)'
        }),
        label='الموظفين'
    )

    include_summary = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='تضمين الملخص'
    )

    include_details = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='تضمين التفاصيل'
    )

    export_format = forms.ChoiceField(
        choices=[
            ('html', 'عرض في المتصفح'),
            ('pdf', 'ملف PDF'),
            ('excel', 'ملف Excel'),
            ('csv', 'ملف CSV')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='تنسيق التصدير'
    )


class LeaveRequestForm(forms.ModelForm):
    """نموذج طلب إجازة"""

    class Meta:
        """Meta class"""
        model = LeaveBalance  # سيتم ربطها بنموذج الإجازات لاحقاً
        fields = ['leave_type', 'allocated_days']

        widgets = {
            'leave_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'allocated_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.5,
                'step': 0.5
            })
        }


class EmployeeAttendanceProfileForm(forms.ModelForm):
    """نموذج ملف الحضور للموظف"""

    class Meta:
        """Meta class"""
        model = EmployeeAttendanceProfile
        fields = [
            'employee', 'attendance_rule', 'work_hours_per_day',
            'salary_status', 'attendance_status'
        ]

        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'attendance_rule': forms.Select(attrs={
                'class': 'form-control'
            }),
            'work_hours_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 24,
                'step': 0.5
            }),
            'salary_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'attendance_status': forms.Select(attrs={
                'class': 'form-control'
            })
        }


class ZKSyncForm(forms.Form):
    """نموذج مزامنة أجهزة ZK"""

    device = forms.ModelChoiceField(
        queryset=ZKDevice.objects.filter(status='active'),
        required=False,
        empty_label='جميع الأجهزة',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='الجهاز'
    )

    days = forms.IntegerField(
        initial=7,
        min_value=1,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'عدد الأيام للمزامنة'
        }),
        label='عدد الأيام'
    )

    force_sync = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='مزامنة قسرية (تجاهل آخر مزامنة)'
    )

    clear_device_data = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='مسح البيانات من الجهاز بعد المزامنة'
    )


class AttendanceImportForm(forms.Form):
    """نموذج استيراد بيانات الحضور"""

    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        }),
        label='ملف البيانات'
    )

    file_type = forms.ChoiceField(
        choices=[
            ('csv', 'ملف CSV'),
            ('excel', 'ملف Excel')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='نوع الملف'
    )

    has_header = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='الملف يحتوي على عناوين الأعمدة'
    )

    skip_existing = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='تجاهل السجلات الموجودة'
    )
