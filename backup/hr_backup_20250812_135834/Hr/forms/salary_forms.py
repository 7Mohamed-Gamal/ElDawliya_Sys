from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.salary_models import HrSalaryItem as SalaryItem, HrEmployeeSalaryItem as EmployeeSalaryItem, HrPayrollPeriod as PayrollPeriod
from Hr.models.employee.employee_models import Employee
from Hr.models.core.department_models import Department


class SalaryItemForm(forms.ModelForm):
    """
    Form for creating and editing salary items.
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
    Form for creating and editing employee salary items.
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
        # Use the modern Employee model and its status field
        self.fields['employee'].queryset = Employee.objects.filter(status=Employee.ACTIVE)
        self.fields['salary_item'].queryset = SalaryItem.objects.filter(is_active=True)


class EmployeeSalaryItemBulkForm(forms.Form):
    """
    Form for bulk creation of employee salary items.
    """
    salary_item = forms.ModelChoiceField(
        queryset=SalaryItem.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('بند الراتب')
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('القسم'),
        empty_label=_('جميع الأقسام')
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
        queryset=Employee.objects.filter(status=Employee.ACTIVE),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'}),
        label=_('الموظفين')
    )


class PayrollCalculationForm(forms.Form):
    """
    Form for calculating payroll.
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
    Form for managing payroll periods.
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
