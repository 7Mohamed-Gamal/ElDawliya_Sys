# =============================================================================
# ElDawliya HR Management System - Payroll Forms
# =============================================================================
# Forms for payroll management (Salary Components, Payroll Entries, etc.)
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Submit, HTML
from crispy_forms.bootstrap import Field, FormActions
from datetime import date, timedelta
from decimal import Decimal

from Hr.models import (
    SalaryComponent, EmployeeSalaryStructure, PayrollPeriod,
    PayrollEntry, Employee, Company
)


class SalaryComponentForm(forms.ModelForm):
    """نموذج إنشاء وتحديث مكون الراتب"""
    
    class Meta:
        model = SalaryComponent
        fields = [
            'company', 'name', 'code', 'component_type', 'calculation_method',
            'default_value', 'is_taxable', 'affects_overtime', 'description',
            'formula', 'is_active'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم مكون الراتب'),
                'dir': 'rtl'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('كود المكون'),
                'maxlength': '20'
            }),
            'component_type': forms.Select(attrs={'class': 'form-select'}),
            'calculation_method': forms.Select(attrs={'class': 'form-select'}),
            'default_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('القيمة الافتراضية'),
                'step': '0.01',
                'min': '0'
            }),
            'is_taxable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'affects_overtime': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('وصف المكون'),
                'dir': 'rtl'
            }),
            'formula': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('المعادلة (للحساب التلقائي)'),
                'dir': 'ltr'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        
        # Set default values
        if not self.instance.pk:
            self.fields['is_taxable'].initial = True
            self.fields['is_active'].initial = True
        
        self.helper.layout = Layout(
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-money-bill me-2"></i>معلومات مكون الراتب الأساسية</h4>'),
                Row(
                    Column('company', css_class='col-md-6'),
                    Column('name', css_class='col-md-6'),
                ),
                Row(
                    Column('code', css_class='col-md-6'),
                    Column('component_type', css_class='col-md-6'),
                ),
                'description',
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-calculator me-2"></i>طريقة الحساب</h4>'),
                Row(
                    Column('calculation_method', css_class='col-md-6'),
                    Column('default_value', css_class='col-md-6'),
                ),
                'formula',
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-cog me-2"></i>الإعدادات</h4>'),
                Row(
                    Column('is_taxable', css_class='col-md-4'),
                    Column('affects_overtime', css_class='col-md-4'),
                    Column('is_active', css_class='col-md-4'),
                ),
                css_class='card-body mb-3'
            ),
            FormActions(
                Submit('submit', _('حفظ مكون الراتب'), css_class='btn btn-primary'),
                HTML('<a href="{% url "hr:salary_component_list" %}" class="btn btn-secondary ms-2">إلغاء</a>'),
                css_class='text-center'
            )
        )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        company = self.cleaned_data.get('company')
        
        if code and company:
            qs = SalaryComponent.objects.filter(company=company, code=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(_('كود مكون الراتب موجود مسبقاً في هذه الشركة'))
        
        return code


class EmployeeSalaryStructureForm(forms.ModelForm):
    """نموذج هيكل راتب الموظف"""
    
    class Meta:
        model = EmployeeSalaryStructure
        fields = [
            'employee', 'salary_component', 'amount', 'percentage',
            'effective_date', 'end_date', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'salary_component': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('المبلغ'),
                'step': '0.01',
                'min': '0'
            }),
            'percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('النسبة المئوية'),
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'effective_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('ملاحظات'),
                'dir': 'rtl'
            })
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        
        if employee:
            self.fields['employee'].initial = employee
            # Filter salary components by employee's company
            self.fields['salary_component'].queryset = SalaryComponent.objects.filter(
                company=employee.company, is_active=True
            )
        
        # Set default effective date to today
        if not self.instance.pk:
            self.fields['effective_date'].initial = date.today()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            'employee',
            'salary_component',
            Row(
                Column('amount', css_class='col-md-6'),
                Column('percentage', css_class='col-md-6'),
            ),
            Row(
                Column('effective_date', css_class='col-md-6'),
                Column('end_date', css_class='col-md-6'),
            ),
            'notes',
            FormActions(
                Submit('submit', _('حفظ هيكل الراتب'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        percentage = cleaned_data.get('percentage')
        effective_date = cleaned_data.get('effective_date')
        end_date = cleaned_data.get('end_date')
        
        # Either amount or percentage should be provided
        if not amount and not percentage:
            raise ValidationError(_('يجب تحديد المبلغ أو النسبة المئوية'))
        
        # Check date order
        if effective_date and end_date and effective_date > end_date:
            raise ValidationError(_('تاريخ السريان يجب أن يكون قبل تاريخ الانتهاء'))
        
        return cleaned_data


class PayrollPeriodForm(forms.ModelForm):
    """نموذج فترة الراتب"""
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'company', 'name', 'start_date', 'end_date', 'pay_date', 'notes'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم فترة الراتب'),
                'dir': 'rtl'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'pay_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('ملاحظات'),
                'dir': 'rtl'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Set default values for current month
        if not self.instance.pk:
            today = date.today()
            first_day = today.replace(day=1)
            last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            self.fields['start_date'].initial = first_day
            self.fields['end_date'].initial = last_day
            self.fields['pay_date'].initial = last_day + timedelta(days=5)
            self.fields['name'].initial = f"راتب {today.strftime('%B %Y')}"
        
        self.helper.layout = Layout(
            'company',
            'name',
            Row(
                Column('start_date', css_class='col-md-4'),
                Column('end_date', css_class='col-md-4'),
                Column('pay_date', css_class='col-md-4'),
            ),
            'notes',
            FormActions(
                Submit('submit', _('إنشاء فترة الراتب'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        pay_date = cleaned_data.get('pay_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية'))
        
        if end_date and pay_date:
            if pay_date < end_date:
                raise ValidationError(_('تاريخ الدفع يجب أن يكون بعد تاريخ انتهاء الفترة'))
        
        return cleaned_data


class PayrollEntryForm(forms.ModelForm):
    """نموذج سجل الراتب"""
    
    class Meta:
        model = PayrollEntry
        fields = [
            'payroll_period', 'employee', 'basic_salary', 'total_allowances',
            'total_bonuses', 'overtime_amount', 'total_deductions',
            'tax_amount', 'insurance_amount', 'working_days', 'present_days',
            'absent_days', 'leave_days', 'overtime_hours', 'notes'
        ]
        widgets = {
            'payroll_period': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'basic_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'total_allowances': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'total_bonuses': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'overtime_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'total_deductions': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'insurance_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'working_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '31'
            }),
            'present_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '31'
            }),
            'absent_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '31'
            }),
            'leave_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '31'
            }),
            'overtime_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('ملاحظات'),
                'dir': 'rtl'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-user-tie me-2"></i>معلومات الموظف والفترة</h4>'),
                Row(
                    Column('payroll_period', css_class='col-md-6'),
                    Column('employee', css_class='col-md-6'),
                ),
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-money-bill-wave me-2"></i>مكونات الراتب</h4>'),
                Row(
                    Column('basic_salary', css_class='col-md-6'),
                    Column('total_allowances', css_class='col-md-6'),
                ),
                Row(
                    Column('total_bonuses', css_class='col-md-6'),
                    Column('overtime_amount', css_class='col-md-6'),
                ),
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-minus-circle me-2"></i>الخصومات</h4>'),
                Row(
                    Column('total_deductions', css_class='col-md-4'),
                    Column('tax_amount', css_class='col-md-4'),
                    Column('insurance_amount', css_class='col-md-4'),
                ),
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-calendar-check me-2"></i>بيانات الحضور</h4>'),
                Row(
                    Column('working_days', css_class='col-md-3'),
                    Column('present_days', css_class='col-md-3'),
                    Column('absent_days', css_class='col-md-3'),
                    Column('leave_days', css_class='col-md-3'),
                ),
                'overtime_hours',
                css_class='card-body mb-3'
            ),
            'notes',
            FormActions(
                Submit('submit', _('حفظ سجل الراتب'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class PayrollCalculationForm(forms.Form):
    """نموذج حساب الرواتب التلقائي"""
    
    payroll_period = forms.ModelChoiceField(
        queryset=PayrollPeriod.objects.filter(status='draft'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(status='active'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    include_attendance = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_overtime = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_leaves = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            self.fields['payroll_period'].queryset = PayrollPeriod.objects.filter(
                company=company, status='draft'
            )
            self.fields['employees'].queryset = Employee.objects.filter(
                company=company, status='active'
            )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-calculator me-2"></i>إعدادات حساب الرواتب</h4>'),
                'payroll_period',
                HTML('<h5 class="mt-3">خيارات الحساب:</h5>'),
                Row(
                    Column('include_attendance', css_class='col-md-3'),
                    Column('include_overtime', css_class='col-md-3'),
                    Column('include_leaves', css_class='col-md-3'),
                ),
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-users me-2"></i>اختيار الموظفين</h4>'),
                HTML('<p class="text-muted">اتركه فارغاً لحساب رواتب جميع الموظفين النشطين</p>'),
                'employees',
                css_class='card-body mb-3'
            ),
            FormActions(
                Submit('calculate', _('حساب الرواتب'), css_class='btn btn-primary btn-lg'),
                css_class='text-center'
            )
        )


class PayrollReportForm(forms.Form):
    """نموذج تقرير الرواتب"""
    
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        empty_label=_('جميع الشركات'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    payroll_period = forms.ModelChoiceField(
        queryset=PayrollPeriod.objects.all(),
        required=False,
        empty_label=_('جميع الفترات'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='active'),
        required=False,
        empty_label=_('جميع الموظفين'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', _('جميع الحالات'))] + PayrollEntry.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row g-3'
        
        self.helper.layout = Layout(
            Row(
                Column('company', css_class='col-md-3'),
                Column('payroll_period', css_class='col-md-3'),
                Column('employee', css_class='col-md-3'),
                Column('status', css_class='col-md-3'),
            ),
            Row(
                Column(
                    Submit('generate_report', _('إنشاء التقرير'), css_class='btn btn-primary'),
                    Submit('export_excel', _('تصدير Excel'), css_class='btn btn-success ms-2'),
                    Submit('export_pdf', _('تصدير PDF'), css_class='btn btn-danger ms-2'),
                    css_class='col-12 text-center'
                )
            )
        )
