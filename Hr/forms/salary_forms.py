from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models import SalaryItem, EmployeeSalaryItem, PayrollPeriod, Employee


class SalaryItemForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل بنود الرواتب
    """
    class Meta:
        model = SalaryItem
        fields = ['name', 'item_type', 'calculation_method', 'affects_total', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'calculation_method': forms.Select(attrs={'class': 'form-select'}),
            'affects_total': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EmployeeSalaryItemForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل بنود رواتب الموظفين
    """
    class Meta:
        model = EmployeeSalaryItem
        fields = ['employee', 'salary_item', 'value', 'effective_date', 'end_date', 'is_active']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'salary_item': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmployeeSalaryItemBulkForm(forms.Form):
    """
    نموذج لإنشاء بنود رواتب الموظفين بالجملة
    """
    salary_item = forms.ModelChoiceField(
        queryset=SalaryItem.objects.all(),
        label=_('بند الراتب'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(working_condition='سارى'),
        label=_('الموظفين'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10})
    )
    value = forms.DecimalField(
        label=_('القيمة'),
        widget=forms.NumberInput(attrs={'class': 'form-control'})
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
        label=_('نشط'),
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class PayrollPeriodForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل فترات الرواتب
    """
    class Meta:
        model = PayrollPeriod
        fields = ['name', 'start_date', 'end_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class PayrollCalculationForm(forms.Form):
    """
    نموذج لحساب الرواتب
    """
    payroll_period = forms.ModelChoiceField(
        queryset=PayrollPeriod.objects.all(),
        label=_('فترة الراتب'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(working_condition='سارى'),
        label=_('الموظفين'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10})
    )
    recalculate = forms.BooleanField(
        label=_('إعادة حساب الرواتب الموجودة'),
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
