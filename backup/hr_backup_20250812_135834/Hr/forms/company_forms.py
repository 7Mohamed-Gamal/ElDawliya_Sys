# =============================================================================
# ElDawliya HR Management System - Company Forms
# =============================================================================
# Forms for company structure management (Company, Branch, Department, JobPosition)
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Submit, HTML
from crispy_forms.bootstrap import Field, FormActions

from Hr.models import Company, Branch, Department, JobPosition


class CompanyForm(forms.ModelForm):
    """نموذج إنشاء وتحديث الشركة"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'name_english', 'code', 'tax_number', 'commercial_register',
            'address', 'phone', 'email', 'website', 'logo', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل اسم الشركة'),
                'dir': 'rtl'
            }),
            'name_english': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل الاسم بالإنجليزية'),
                'dir': 'ltr'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل كود الشركة'),
                'maxlength': '20'
            }),
            'tax_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل الرقم الضريبي')
            }),
            'commercial_register': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل رقم السجل التجاري')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('أدخل عنوان الشركة'),
                'dir': 'rtl'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل رقم الهاتف')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل البريد الإلكتروني')
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل الموقع الإلكتروني')
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
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
        self.helper.attrs = {'novalidate': ''}
        
        self.helper.layout = Layout(
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-building me-2"></i>معلومات الشركة الأساسية</h4>'),
                Row(
                    Column('name', css_class='col-md-6'),
                    Column('name_english', css_class='col-md-6'),
                ),
                Row(
                    Column('code', css_class='col-md-4'),
                    Column('tax_number', css_class='col-md-4'),
                    Column('commercial_register', css_class='col-md-4'),
                ),
                css_class='card-body'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-address-card me-2"></i>معلومات الاتصال</h4>'),
                'address',
                Row(
                    Column('phone', css_class='col-md-4'),
                    Column('email', css_class='col-md-4'),
                    Column('website', css_class='col-md-4'),
                ),
                css_class='card-body'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-cog me-2"></i>الإعدادات</h4>'),
                Row(
                    Column('logo', css_class='col-md-6'),
                    Column('is_active', css_class='col-md-6'),
                ),
                css_class='card-body'
            ),
            FormActions(
                Submit('submit', _('حفظ'), css_class='btn btn-primary'),
                HTML('<a href="{% url "hr:company_list" %}" class="btn btn-secondary ms-2">إلغاء</a>'),
                css_class='text-center'
            )
        )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Check for duplicate codes
            qs = Company.objects.filter(code=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(_('كود الشركة موجود مسبقاً'))
        return code


class BranchForm(forms.ModelForm):
    """نموذج إنشاء وتحديث الفرع"""
    
    class Meta:
        model = Branch
        fields = ['company', 'name', 'code', 'address', 'phone', 'manager', 'is_active']
        widgets = {
            'company': forms.Select(attrs={
                'class': 'form-select'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل اسم الفرع'),
                'dir': 'rtl'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل كود الفرع'),
                'maxlength': '20'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('أدخل عنوان الفرع'),
                'dir': 'rtl'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل رقم الهاتف')
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            self.fields['company'].initial = company
            self.fields['company'].widget.attrs['readonly'] = True
            # Filter managers by company
            from Hr.models import Employee
            self.fields['manager'].queryset = Employee.objects.filter(
                company=company, status='active'
            )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        
        self.helper.layout = Layout(
            Row(
                Column('company', css_class='col-md-6'),
                Column('name', css_class='col-md-6'),
            ),
            Row(
                Column('code', css_class='col-md-6'),
                Column('manager', css_class='col-md-6'),
            ),
            'address',
            Row(
                Column('phone', css_class='col-md-6'),
                Column('is_active', css_class='col-md-6'),
            ),
            FormActions(
                Submit('submit', _('حفظ'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class DepartmentForm(forms.ModelForm):
    """نموذج إنشاء وتحديث القسم"""
    
    class Meta:
        model = Department
        fields = [
            'company', 'branch', 'name', 'code', 'parent_department',
            'manager', 'description', 'budget', 'is_active'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل اسم القسم'),
                'dir': 'rtl'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل كود القسم'),
                'maxlength': '20'
            }),
            'parent_department': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('أدخل وصف القسم'),
                'dir': 'rtl'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل ميزانية القسم'),
                'step': '0.01'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Add JavaScript for dynamic filtering
        self.helper.layout = Layout(
            Row(
                Column('company', css_class='col-md-6'),
                Column('branch', css_class='col-md-6'),
            ),
            Row(
                Column('name', css_class='col-md-6'),
                Column('code', css_class='col-md-6'),
            ),
            Row(
                Column('parent_department', css_class='col-md-6'),
                Column('manager', css_class='col-md-6'),
            ),
            'description',
            Row(
                Column('budget', css_class='col-md-6'),
                Column('is_active', css_class='col-md-6'),
            ),
            FormActions(
                Submit('submit', _('حفظ'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class JobPositionForm(forms.ModelForm):
    """نموذج إنشاء وتحديث المنصب الوظيفي"""
    
    class Meta:
        model = JobPosition
        fields = [
            'company', 'department', 'title', 'title_english', 'code',
            'level', 'description', 'requirements', 'min_salary', 'max_salary', 'is_active'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل المسمى الوظيفي'),
                'dir': 'rtl'
            }),
            'title_english': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل المسمى بالإنجليزية'),
                'dir': 'ltr'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل كود المنصب'),
                'maxlength': '20'
            }),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('أدخل الوصف الوظيفي'),
                'dir': 'rtl'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('أدخل المتطلبات الوظيفية'),
                'dir': 'rtl'
            }),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('الحد الأدنى للراتب'),
                'step': '0.01'
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('الحد الأقصى للراتب'),
                'step': '0.01'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Row(
                Column('company', css_class='col-md-6'),
                Column('department', css_class='col-md-6'),
            ),
            Row(
                Column('title', css_class='col-md-6'),
                Column('title_english', css_class='col-md-6'),
            ),
            Row(
                Column('code', css_class='col-md-6'),
                Column('level', css_class='col-md-6'),
            ),
            'description',
            'requirements',
            Row(
                Column('min_salary', css_class='col-md-4'),
                Column('max_salary', css_class='col-md-4'),
                Column('is_active', css_class='col-md-4'),
            ),
            FormActions(
                Submit('submit', _('حفظ'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise ValidationError(_('الحد الأدنى للراتب يجب أن يكون أقل من الحد الأقصى'))
        
        return cleaned_data
