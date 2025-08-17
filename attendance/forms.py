from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import AttendanceRules, EmployeeAttendance
from employees.models import Employee


class AttendanceRulesForm(forms.ModelForm):
    """نموذج إضافة وتعديل قواعد الحضور"""
    
    class Meta:
        model = AttendanceRules
        fields = [
            'rule_name', 'shift_start', 'shift_end', 'late_threshold',
            'early_threshold', 'overtime_start_after', 'week_end_days', 'is_default'
        ]
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
        widgets = {
            'rule_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم القاعدة'
            }),
            'shift_start': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'shift_end': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'late_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'عدد الدقائق'
            }),
            'early_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'عدد الدقائق'
            }),
            'overtime_start_after': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'week_end_days': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: الجمعة,السبت'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'rule_name': 'اسم مميز لقاعدة الحضور',
            'late_threshold': 'عدد الدقائق المسموح بها للتأخير',
            'early_threshold': 'عدد الدقائق المسموح بها للمغادرة المبكرة',
            'week_end_days': 'أيام العطل الأسبوعية مفصولة بفاصلة',
            'is_default': 'ستطبق هذه القاعدة على الموظفين الجدد تلقائياً'
        }

    def clean(self):
        cleaned_data = super().clean()
        shift_start = cleaned_data.get('shift_start')
        shift_end = cleaned_data.get('shift_end')
        late_threshold = cleaned_data.get('late_threshold')
        early_threshold = cleaned_data.get('early_threshold')

        # التحقق من أوقات الوردية
        if shift_start and shift_end:
            if shift_start >= shift_end:
                raise ValidationError('وقت بداية الوردية يجب أن يكون قبل وقت النهاية')

        # التحقق من القيم الموجبة
        if late_threshold is not None and late_threshold < 0:
            raise ValidationError('حد التأخير يجب أن يكون رقماً موجباً')

        if early_threshold is not None and early_threshold < 0:
            raise ValidationError('حد المغادرة المبكرة يجب أن يكون رقماً موجباً')

        return cleaned_data


class EmployeeAttendanceForm(forms.ModelForm):
    """نموذج إضافة وتعديل سجلات الحضور"""
    
    class Meta:
        model = EmployeeAttendance
        fields = [
            'emp', 'att_date', 'check_in', 'check_out', 'status', 'rule'
        ]
        labels = {
            'emp': 'الموظف',
            'att_date': 'التاريخ',
            'check_in': 'وقت الدخول',
            'check_out': 'وقت الخروج',
            'status': 'الحالة',
            'rule': 'قاعدة الحضور'
        }
        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'اختر الموظف'
            }),
            'att_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'check_in': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'check_out': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'rule': forms.Select(attrs={
                'class': 'form-control',
                'data-placeholder': 'اختر قاعدة الحضور'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تحديد خيارات الحالة
        self.fields['status'].choices = [
            ('', 'اختر الحالة'),
            ('Present', 'حاضر'),
            ('Absent', 'غائب'),
            ('Late', 'متأخر'),
            ('EarlyLeave', 'مغادرة مبكرة'),
            ('Holiday', 'عطلة'),
            ('Leave', 'إجازة')
        ]
        
        # تحديد الموظفين النشطين فقط
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')
        
        # تحديد قواعد الحضور النشطة
        self.fields['rule'].queryset = AttendanceRules.objects.all().order_by('rule_name')

    def clean(self):
        cleaned_data = super().clean()
        emp = cleaned_data.get('emp')
        att_date = cleaned_data.get('att_date')
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        # التحقق من عدم تكرار السجل لنفس الموظف في نفس اليوم
        if emp and att_date:
            existing_record = EmployeeAttendance.objects.filter(
                emp=emp,
                att_date=att_date
            )
            
            # استثناء السجل الحالي في حالة التعديل
            if self.instance.pk:
                existing_record = existing_record.exclude(pk=self.instance.pk)
            
            if existing_record.exists():
                raise ValidationError(f'يوجد سجل حضور للموظف {emp} في تاريخ {att_date}')

        # التحقق من أوقات الدخول والخروج
        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError('وقت الدخول يجب أن يكون قبل وقت الخروج')

        # التحقق من التاريخ
        if att_date:
            from datetime import date
            if att_date > date.today():
                raise ValidationError('لا يمكن تسجيل حضور لتاريخ مستقبلي')

        return cleaned_data


class AttendanceSearchForm(forms.Form):
    """نموذج البحث في سجلات الحضور"""
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(emp_status='Active').order_by('first_name'),
        required=False,
        empty_label='جميع الموظفين',
        label='الموظف',
        widget=forms.Select(attrs={
            'class': 'form-control select2'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        label='من تاريخ',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        label='إلى تاريخ',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        label='الحالة',
        choices=[
            ('', 'جميع الحالات'),
            ('Present', 'حاضر'),
            ('Absent', 'غائب'),
            ('Late', 'متأخر'),
            ('EarlyLeave', 'مغادرة مبكرة'),
            ('Holiday', 'عطلة'),
            ('Leave', 'إجازة')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_from > date_to:
                raise ValidationError('تاريخ البداية يجب أن يكون قبل تاريخ النهاية')

        return cleaned_data


class QuickAttendanceForm(forms.Form):
    """نموذج تسجيل الحضور السريع"""
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(emp_status='Active').order_by('first_name'),
        label='الموظف',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'required': True
        })
    )
    
    action = forms.ChoiceField(
        choices=[
            ('check_in', 'تسجيل دخول'),
            ('check_out', 'تسجيل خروج')
        ],
        label='العملية',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

