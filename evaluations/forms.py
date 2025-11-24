from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from .models import EvaluationPeriod, EmployeeEvaluation
from employees.models import Employee
from org.models import Department


class EvaluationPeriodForm(forms.ModelForm):
    """نموذج إضافة وتعديل فترات التقييم"""

    class Meta:
        """Meta class"""
        model = EvaluationPeriod
        fields = ['period_name', 'start_date', 'end_date']

        widgets = {
            'period_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم فترة التقييم'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

        labels = {
            'period_name': 'اسم فترة التقييم',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية'
        }

    def clean_start_date(self):
        """التحقق من تاريخ البداية"""
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            # للفترات الجديدة، التحقق من أن التاريخ ليس في الماضي البعيد
            if not self.instance.pk and start_date < date.today() - timedelta(days=365):
                raise ValidationError('تاريخ البداية قديم جداً.')
        return start_date

    def clean_end_date(self):
        """التحقق من تاريخ النهاية"""
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        if end_date and start_date:
            if end_date <= start_date:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

            # التحقق من أن مدة الفترة معقولة
            duration = (end_date - start_date).days
            if duration < 30:
                raise ValidationError('مدة فترة التقييم يجب أن تكون شهر على الأقل.')
            if duration > 365:
                raise ValidationError('مدة فترة التقييم لا يمكن أن تزيد عن سنة.')

        return end_date

    def clean(self):
        """التحقق الشامل من البيانات"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            # التحقق من عدم تداخل الفترات
            overlapping_periods = EvaluationPeriod.objects.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exclude(pk=self.instance.pk if self.instance.pk else None)

            if overlapping_periods.exists():
                period = overlapping_periods.first()
                raise ValidationError(
                    f'يوجد تداخل مع فترة التقييم "{period.period_name}" '
                    f'من {period.start_date} إلى {period.end_date}.'
                )

        return cleaned_data


class EmployeeEvaluationForm(forms.ModelForm):
    """نموذج إضافة وتعديل تقييمات الموظفين"""

    class Meta:
        """Meta class"""
        model = EmployeeEvaluation
        fields = ['emp', 'period', 'manager_id', 'score', 'notes', 'eval_date', 'status']

        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-select'
            }),
            'period': forms.Select(attrs={
                'class': 'form-select'
            }),
            'manager_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'معرف المدير المقيم'
            }),
            'score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'الدرجة (0-100)',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'ملاحظات التقييم'
            }),
            'eval_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }

        labels = {
            'emp': 'الموظف',
            'period': 'فترة التقييم',
            'manager_id': 'المدير المقيم',
            'score': 'الدرجة',
            'notes': 'ملاحظات',
            'eval_date': 'تاريخ التقييم',
            'status': 'الحالة'
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # تخصيص خيارات القوائم المنسدلة
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')

        self.fields['period'].queryset = EvaluationPeriod.objects.all().order_by('-start_date')

        # إضافة خيارات فارغة
        self.fields['emp'].empty_label = "اختر الموظف"
        self.fields['period'].empty_label = "اختر فترة التقييم"

        # تعيين تاريخ التقييم الافتراضي
        if not self.instance.pk:
            self.fields['eval_date'].initial = date.today()

    def clean_score(self):
        """التحقق من الدرجة"""
        score = self.cleaned_data.get('score')
        if score is not None:
            if score < 0 or score > 100:
                raise ValidationError('الدرجة يجب أن تكون بين 0 و 100.')
        return score

    def clean_eval_date(self):
        """التحقق من تاريخ التقييم"""
        eval_date = self.cleaned_data.get('eval_date')
        period = self.cleaned_data.get('period')

        if eval_date and period:
            if eval_date < period.start_date or eval_date > period.end_date:
                raise ValidationError(
                    f'تاريخ التقييم يجب أن يكون ضمن فترة التقييم '
                    f'من {period.start_date} إلى {period.end_date}.'
                )

        return eval_date

    def clean(self):
        """التحقق الشامل من البيانات"""
        cleaned_data = super().clean()
        emp = cleaned_data.get('emp')
        period = cleaned_data.get('period')

        if emp and period:
            # التحقق من عدم وجود تقييم مسبق للموظف في نفس الفترة
            existing_evaluation = EmployeeEvaluation.objects.filter(
                emp=emp,
                period=period
            ).exclude(pk=self.instance.pk if self.instance.pk else None)

            if existing_evaluation.exists():
                raise ValidationError(
                    f'يوجد تقييم مسبق للموظف {emp.first_name} {emp.last_name} '
                    f'في فترة التقييم {period.period_name}.'
                )

        return cleaned_data


class EvaluationSearchForm(forms.Form):
    """نموذج البحث في التقييمات"""

    search = forms.CharField(
        label='البحث',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم الموظف أو ملاحظات التقييم'
        })
    )

    period = forms.ModelChoiceField(
        label='فترة التقييم',
        queryset=EvaluationPeriod.objects.all().order_by('-start_date'),
        required=False,
        empty_label='جميع الفترات',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    department = forms.ModelChoiceField(
        label='القسم',
        queryset=Department.objects.filter(is_active=True).order_by('dept_name'),
        required=False,
        empty_label='جميع الأقسام',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    score_range = forms.ChoiceField(
        label='نطاق الدرجات',
        choices=[
            ('', 'جميع الدرجات'),
            ('excellent', 'ممتاز (90-100)'),
            ('very_good', 'جيد جداً (80-89)'),
            ('good', 'جيد (70-79)'),
            ('acceptable', 'مقبول (60-69)'),
            ('poor', 'ضعيف (أقل من 60)'),
            ('pending', 'غير مكتمل')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class BulkEvaluationForm(forms.Form):
    """نموذج إنشاء تقييمات بالجملة"""

    period = forms.ModelChoiceField(
        label='فترة التقييم',
        queryset=EvaluationPeriod.objects.all().order_by('-start_date'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    department = forms.ModelChoiceField(
        label='القسم',
        queryset=Department.objects.filter(is_active=True).order_by('dept_name'),
        required=False,
        empty_label='جميع الأقسام',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    employees = forms.ModelMultipleChoiceField(
        label='الموظفين',
        queryset=Employee.objects.filter(emp_status='Active').order_by('first_name', 'last_name'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # إضافة JavaScript لفلترة الموظفين حسب القسم
        self.fields['employees'].widget.attrs.update({
            'data-department-filter': 'true'
        })


class EvaluationReportForm(forms.Form):
    """نموذج تقارير التقييمات"""

    REPORT_TYPES = [
        ('summary', 'تقرير ملخص'),
        ('detailed', 'تقرير مفصل'),
        ('comparison', 'تقرير مقارنة'),
        ('performance_trend', 'اتجاه الأداء')
    ]

    report_type = forms.ChoiceField(
        label='نوع التقرير',
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    period = forms.ModelChoiceField(
        label='فترة التقييم',
        queryset=EvaluationPeriod.objects.all().order_by('-start_date'),
        required=False,
        empty_label='جميع الفترات',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    department = forms.ModelChoiceField(
        label='القسم',
        queryset=Department.objects.filter(is_active=True).order_by('dept_name'),
        required=False,
        empty_label='جميع الأقسام',
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

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # تعيين التواريخ الافتراضية
        today = date.today()
        self.fields['date_from'].initial = today.replace(month=1, day=1)  # بداية السنة
        self.fields['date_to'].initial = today

    def clean(self):
        """التحقق من صحة فترة التقرير"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

        return cleaned_data


class PerformanceComparisonForm(forms.Form):
    """نموذج مقارنة الأداء"""

    COMPARISON_TYPES = [
        ('employees', 'مقارنة الموظفين'),
        ('departments', 'مقارنة الأقسام'),
        ('periods', 'مقارنة الفترات')
    ]

    comparison_type = forms.ChoiceField(
        label='نوع المقارنة',
        choices=COMPARISON_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    employees = forms.ModelMultipleChoiceField(
        label='الموظفين للمقارنة',
        queryset=Employee.objects.filter(emp_status='Active').order_by('first_name', 'last_name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    departments = forms.ModelMultipleChoiceField(
        label='الأقسام للمقارنة',
        queryset=Department.objects.filter(is_active=True).order_by('dept_name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    periods = forms.ModelMultipleChoiceField(
        label='الفترات للمقارنة',
        queryset=EvaluationPeriod.objects.all().order_by('-start_date'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    def clean(self):
        """التحقق من صحة البيانات"""
        cleaned_data = super().clean()
        comparison_type = cleaned_data.get('comparison_type')

        if comparison_type == 'employees':
            employees = cleaned_data.get('employees')
            if not employees or len(employees) < 2:
                raise ValidationError('يجب اختيار موظفين اثنين على الأقل للمقارنة.')

        elif comparison_type == 'departments':
            departments = cleaned_data.get('departments')
            if not departments or len(departments) < 2:
                raise ValidationError('يجب اختيار قسمين على الأقل للمقارنة.')

        elif comparison_type == 'periods':
            periods = cleaned_data.get('periods')
            if not periods or len(periods) < 2:
                raise ValidationError('يجب اختيار فترتين على الأقل للمقارنة.')

        return cleaned_data


class EvaluationTemplateForm(forms.Form):
    """نموذج قوالب التقييم"""

    template_name = forms.CharField(
        label='اسم القالب',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم قالب التقييم'
        })
    )

    criteria = forms.CharField(
        label='معايير التقييم',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'معايير التقييم (كل معيار في سطر منفصل)'
        })
    )

    weights = forms.CharField(
        label='أوزان المعايير',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'أوزان المعايير (نسب مئوية)'
        })
    )

    description = forms.CharField(
        label='وصف القالب',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'وصف القالب واستخداماته'
        })
    )


class GoalSettingForm(forms.Form):
    """نموذج تحديد الأهداف"""

    employee = forms.ModelChoiceField(
        label='الموظف',
        queryset=Employee.objects.filter(emp_status='Active').order_by('first_name', 'last_name'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    period = forms.ModelChoiceField(
        label='فترة التقييم',
        queryset=EvaluationPeriod.objects.all().order_by('-start_date'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    goals = forms.CharField(
        label='الأهداف',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'أهداف الموظف للفترة (كل هدف في سطر منفصل)'
        })
    )

    success_criteria = forms.CharField(
        label='معايير النجاح',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'معايير قياس نجاح الأهداف'
        })
    )

    target_date = forms.DateField(
        label='تاريخ الإنجاز المستهدف',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean_target_date(self):
        """التحقق من تاريخ الإنجاز المستهدف"""
        target_date = self.cleaned_data.get('target_date')
        period = self.cleaned_data.get('period')

        if target_date and period:
            if target_date > period.end_date:
                raise ValidationError(
                    f'تاريخ الإنجاز المستهدف يجب أن يكون قبل انتهاء فترة التقييم '
                    f'({period.end_date}).'
                )

        return target_date
