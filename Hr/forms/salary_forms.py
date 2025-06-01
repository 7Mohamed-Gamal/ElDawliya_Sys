from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.salary_models import SalaryItem, EmployeeSalaryItem, PayrollPeriod
from Hr.models.employee_model import Employee


class SalaryItemForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل بنود الرواتب
    """
    class Meta:
        model = SalaryItem
        fields = ['item_code', 'name', 'type', 'default_value', 'is_auto_applied', 'is_active', 'description']
        widgets = {
            'item_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'default_value': forms.NumberInput(attrs={'class': 'form-control money-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EmployeeSalaryItemForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل بنود رواتب الموظفين
    """
    class Meta:
        model = EmployeeSalaryItem
        fields = ['employee', 'salary_item', 'amount', 'start_date', 'end_date', 'is_active']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'salary_item': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control money-input'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active employees
        self.fields['employee'].queryset = Employee.objects.filter(working_condition='سارى')
        # Only show active salary items
        self.fields['salary_item'].queryset = SalaryItem.objects.filter(is_active=True)


class EmployeeSalaryItemBulkForm(forms.Form):
    """
    نموذج لإنشاء بنود رواتب الموظفين بالجملة
    """
    salary_item = forms.ModelChoiceField(
        queryset=SalaryItem.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('بند الراتب')
    )
    department = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('القسم')
    )
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control money-input'}),
        label=_('القيمة')
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('تاريخ البدء')
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('تاريخ الانتهاء')
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(working_condition='سارى'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'}),
        label=_('الموظفين')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get unique departments from active employees
        departments = Employee.objects.filter(working_condition='سارى').values_list(
            'department__id', 'department__name'
        ).distinct()
        self.fields['department'].choices = [('', _('جميع الأقسام'))] + list(departments)


class PayrollCalculationForm(forms.Form):
    """
    نموذج لحساب الرواتب
    """
    period = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label=_('فترة الراتب'),
        help_text=_('اختر شهر وسنة فترة الراتب')
    )
    include_inactive = forms.BooleanField(
        required=False,
        initial=False,
        label=_('تضمين الموظفين غير النشطين'),
        help_text=_('حدد هذا الخيار لتضمين الموظفين غير النشطين في حساب الرواتب')
    )
    recalculate = forms.BooleanField(
        required=False,
        initial=False,
        label=_('إعادة الحساب'),
        help_text=_('حدد هذا الخيار لإعادة حساب الرواتب التي تم حسابها مسبقاً لهذه الفترة')
    )


class PayrollPeriodForm(forms.ModelForm):
    """
    نموذج لإدارة فترات الرواتب
    """
    class Meta:
        model = PayrollPeriod
        fields = ['period', 'status', 'total_amount']
        widgets = {
            'period': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control money-input', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # If creating new period
            self.fields['status'].initial = 'draft'
            self.fields['status'].widget.attrs['readonly'] = True
