from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from .models import LeaveType, EmployeeLeave, PublicHoliday
from employees.models import Employee


class LeaveTypeForm(forms.ModelForm):
    """نموذج إضافة وتعديل أنواع الإجازات"""

    class Meta:
        """Meta class"""
        model = LeaveType
        fields = ['leave_name', 'max_days_per_year', 'is_paid']

        widgets = {
            'leave_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم نوع الإجازة'
            }),
            'max_days_per_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'الحد الأقصى للأيام سنوياً',
                'min': '0'
            }),
            'is_paid': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        labels = {
            'leave_name': 'اسم نوع الإجازة',
            'max_days_per_year': 'الحد الأقصى للأيام سنوياً',
            'is_paid': 'إجازة مدفوعة الأجر'
        }

    def clean_max_days_per_year(self):
        """التحقق من الحد الأقصى للأيام"""
        max_days = self.cleaned_data.get('max_days_per_year')
        if max_days is not None:
            if max_days < 0:
                raise ValidationError('الحد الأقصى للأيام لا يمكن أن يكون سالباً.')
            if max_days > 365:
                raise ValidationError('الحد الأقصى للأيام لا يمكن أن يزيد عن 365 يوماً.')
        return max_days


class EmployeeLeaveForm(forms.ModelForm):
    """نموذج إضافة وتعديل طلبات الإجازات"""

    class Meta:
        """Meta class"""
        model = EmployeeLeave
        fields = ['emp', 'leave_type', 'start_date', 'end_date', 'reason', 'status']

        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-select'
            }),
            'leave_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'سبب طلب الإجازة'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('Pending', 'في الانتظار'),
                ('Approved', 'معتمد'),
                ('Rejected', 'مرفوض')
            ])
        }

        labels = {
            'emp': 'الموظف',
            'leave_type': 'نوع الإجازة',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية',
            'reason': 'سبب الإجازة',
            'status': 'حالة الطلب'
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # تخصيص خيارات القوائم المنسدلة
        self.fields['emp'].queryset = Employee.objects.filter(emp_status='Active').order_by('first_name', 'last_name')
        self.fields['leave_type'].queryset = LeaveType.objects.all().order_by('leave_name')

        # إضافة خيارات فارغة
        self.fields['emp'].empty_label = "اختر الموظف"
        self.fields['leave_type'].empty_label = "اختر نوع الإجازة"

        # تعيين الحالة الافتراضية للطلبات الجديدة
        if not self.instance.pk:
            self.fields['status'].initial = 'Pending'

    def clean_start_date(self):
        """التحقق من تاريخ البداية"""
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            # التحقق من أن التاريخ ليس في الماضي (للطلبات الجديدة)
            if not self.instance.pk and start_date < date.today():
                raise ValidationError('لا يمكن طلب إجازة في تاريخ سابق.')
        return start_date

    def clean_end_date(self):
        """التحقق من تاريخ النهاية"""
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        if end_date and start_date:
            if end_date < start_date:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

            # التحقق من أن مدة الإجازة معقولة
            duration = (end_date - start_date).days + 1
            if duration > 365:
                raise ValidationError('مدة الإجازة لا يمكن أن تزيد عن سنة.')

        return end_date

    def clean(self):
        """التحقق الشامل من البيانات"""
        cleaned_data = super().clean()
        emp = cleaned_data.get('emp')
        leave_type = cleaned_data.get('leave_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if emp and leave_type and start_date and end_date:
            # التحقق من تداخل الإجازات
            overlapping_leaves = EmployeeLeave.objects.filter(
                emp=emp,
                status__in=['Pending', 'Approved']
            ).exclude(pk=self.instance.pk if self.instance.pk else None)

            for leave in overlapping_leaves:
                if (start_date <= leave.end_date and end_date >= leave.start_date):
                    raise ValidationError(
                        f'يوجد تداخل مع إجازة أخرى من {leave.start_date} إلى {leave.end_date}.'
                    )

            # التحقق من رصيد الإجازات
            if leave_type.max_days_per_year:
                current_year = start_date.year
                used_days = EmployeeLeave.objects.filter(
                    emp=emp,
                    leave_type=leave_type,
                    status='Approved',
                    start_date__year=current_year
                ).exclude(pk=self.instance.pk if self.instance.pk else None)

                total_used = sum([(leave.end_date - leave.start_date).days + 1 for leave in used_days])
                requested_days = (end_date - start_date).days + 1

                if total_used + requested_days > leave_type.max_days_per_year:
                    remaining = leave_type.max_days_per_year - total_used
                    raise ValidationError(
                        f'تجاوز الحد المسموح لهذا النوع من الإجازات. '
                        f'الرصيد المتبقي: {remaining} يوم.'
                    )

        return cleaned_data


class PublicHolidayForm(forms.ModelForm):
    """نموذج إضافة وتعديل العطلات الرسمية"""

    class Meta:
        """Meta class"""
        model = PublicHoliday
        fields = ['holiday_date', 'description']

        widgets = {
            'holiday_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'وصف العطلة الرسمية'
            })
        }

        labels = {
            'holiday_date': 'تاريخ العطلة',
            'description': 'وصف العطلة'
        }

    def clean_holiday_date(self):
        """التحقق من تاريخ العطلة"""
        holiday_date = self.cleaned_data.get('holiday_date')
        if holiday_date:
            # التحقق من عدم تكرار التاريخ
            existing = PublicHoliday.objects.filter(holiday_date=holiday_date)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError('يوجد عطلة رسمية مسجلة في هذا التاريخ مسبقاً.')

        return holiday_date


class LeaveSearchForm(forms.Form):
    """نموذج البحث في الإجازات"""

    search = forms.CharField(
        label='البحث',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم الموظف أو سبب الإجازة'
        })
    )

    leave_type = forms.ModelChoiceField(
        label='نوع الإجازة',
        queryset=LeaveType.objects.all().order_by('leave_name'),
        required=False,
        empty_label='جميع الأنواع',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    status = forms.ChoiceField(
        label='الحالة',
        choices=[
            ('', 'جميع الحالات'),
            ('Pending', 'في الانتظار'),
            ('Approved', 'معتمد'),
            ('Rejected', 'مرفوض')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        label='من تاريخ',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        label='إلى تاريخ',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        """التحقق من صحة فترة البحث"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

        return cleaned_data


class LeaveApprovalForm(forms.Form):
    """نموذج اعتماد أو رفض الإجازة"""

    action = forms.ChoiceField(
        label='الإجراء',
        choices=[
            ('approve', 'اعتماد'),
            ('reject', 'رفض')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

    notes = forms.CharField(
        label='ملاحظات',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'ملاحظات حول القرار (اختياري)'
        })
    )


class BulkLeaveActionForm(forms.Form):
    """نموذج الإجراءات الجماعية على الإجازات"""

    action = forms.ChoiceField(
        label='الإجراء',
        choices=[
            ('approve', 'اعتماد المحدد'),
            ('reject', 'رفض المحدد'),
            ('delete', 'حذف المحدد')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    leave_ids = forms.CharField(
        widget=forms.HiddenInput()
    )

    def clean_leave_ids(self):
        """التحقق من معرفات الإجازات"""
        leave_ids = self.cleaned_data.get('leave_ids')
        if leave_ids:
            try:
                ids = [int(id.strip()) for id in leave_ids.split(',') if id.strip()]
                if not ids:
                    raise ValidationError('يجب تحديد إجازة واحدة على الأقل.')
                return ids
            except ValueError:
                raise ValidationError('معرفات الإجازات غير صحيحة.')
        else:
            raise ValidationError('يجب تحديد إجازة واحدة على الأقل.')


class LeaveBalanceForm(forms.Form):
    """نموذج عرض أرصدة الإجازات"""

    employee = forms.ModelChoiceField(
        label='الموظف',
        queryset=Employee.objects.filter(emp_status='Active').order_by('first_name', 'last_name'),
        required=False,
        empty_label='جميع الموظفين',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    department = forms.CharField(
        label='القسم',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    year = forms.IntegerField(
        label='السنة',
        initial=date.today().year,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '2020',
            'max': '2030'
        })
    )

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # إضافة خيارات الأقسام
        from org.models import Department
        departments = Department.objects.filter(is_active=True).order_by('dept_name')
        dept_choices = [('', 'جميع الأقسام')] + [(dept.dept_id, dept.dept_name) for dept in departments]
        self.fields['department'].widget.choices = dept_choices


class LeaveReportForm(forms.Form):
    """نموذج تقارير الإجازات"""

    REPORT_TYPES = [
        ('summary', 'تقرير ملخص'),
        ('detailed', 'تقرير مفصل'),
        ('balance', 'تقرير الأرصدة'),
        ('usage', 'تقرير الاستخدام')
    ]

    report_type = forms.ChoiceField(
        label='نوع التقرير',
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        label='من تاريخ',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        label='إلى تاريخ',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    department = forms.CharField(
        label='القسم',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    leave_type = forms.ModelChoiceField(
        label='نوع الإجازة',
        queryset=LeaveType.objects.all().order_by('leave_name'),
        required=False,
        empty_label='جميع الأنواع',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # تعيين التواريخ الافتراضية
        today = date.today()
        self.fields['date_from'].initial = today.replace(month=1, day=1)  # بداية السنة
        self.fields['date_to'].initial = today

        # إضافة خيارات الأقسام
        from org.models import Department
        departments = Department.objects.filter(is_active=True).order_by('dept_name')
        dept_choices = [('', 'جميع الأقسام')] + [(dept.dept_id, dept.dept_name) for dept in departments]
        self.fields['department'].widget.choices = dept_choices

    def clean(self):
        """التحقق من صحة فترة التقرير"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

            # التحقق من أن الفترة ليست طويلة جداً
            if (date_to - date_from).days > 365:
                raise ValidationError('فترة التقرير لا يمكن أن تزيد عن سنة واحدة.')

        return cleaned_data
