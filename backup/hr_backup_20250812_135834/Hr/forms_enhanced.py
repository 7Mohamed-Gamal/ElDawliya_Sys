"""
Enhanced Django Forms for HR Models
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML
from crispy_forms.bootstrap import TabHolder, Tab
from .models import (
    Employee, EmployeeEducation, EmployeeInsurance, EmployeeVehicle,
    Company, Branch, Department, JobPosition
)


# =============================================================================
# ENHANCED EMPLOYEE FORMS
# =============================================================================

class EmployeeEducationForm(forms.ModelForm):
    """نموذج المؤهلات الدراسية"""
    
    class Meta:
        model = EmployeeEducation
        fields = [
            'degree_type', 'major', 'institution', 'graduation_year', 
            'grade', 'country', 'certificate_file', 'is_verified'
        ]
        widgets = {
            'graduation_year': forms.NumberInput(attrs={'min': 1950, 'max': 2030}),
            'grade': forms.TextInput(attrs={'placeholder': 'مثال: 3.5 أو 85% أو امتياز'}),
            'country': forms.TextInput(attrs={'placeholder': 'مثال: المملكة العربية السعودية'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        
        self.helper.layout = Layout(
            Fieldset(
                'المؤهل الدراسي',
                Row(
                    Column('degree_type', css_class='form-group col-md-6 mb-0'),
                    Column('major', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('institution', css_class='form-group col-md-8 mb-0'),
                    Column('graduation_year', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('grade', css_class='form-group col-md-4 mb-0'),
                    Column('country', css_class='form-group col-md-8 mb-0'),
                    css_class='form-row'
                ),
                'certificate_file',
                'is_verified',
            ),
            Submit('submit', 'حفظ', css_class='btn btn-primary')
        )
    
    def clean_graduation_year(self):
        graduation_year = self.cleaned_data.get('graduation_year')
        from datetime import date
        current_year = date.today().year
        
        if graduation_year and graduation_year > current_year:
            raise ValidationError(_('سنة التخرج لا يمكن أن تكون في المستقبل'))
        
        return graduation_year


class EmployeeInsuranceForm(forms.ModelForm):
    """نموذج تأمينات الموظف"""
    
    class Meta:
        model = EmployeeInsurance
        fields = [
            'insurance_type', 'policy_number', 'provider', 'start_date', 'end_date',
            'premium_amount', 'coverage_amount', 'employee_contribution', 
            'employer_contribution', 'policy_document', 'is_active'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'premium_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'coverage_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'employee_contribution': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'employer_contribution': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        
        self.helper.layout = Layout(
            Fieldset(
                'معلومات التأمين',
                Row(
                    Column('insurance_type', css_class='form-group col-md-6 mb-0'),
                    Column('policy_number', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'provider',
                Row(
                    Column('start_date', css_class='form-group col-md-6 mb-0'),
                    Column('end_date', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'المعلومات المالية',
                Row(
                    Column('premium_amount', css_class='form-group col-md-6 mb-0'),
                    Column('coverage_amount', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('employee_contribution', css_class='form-group col-md-6 mb-0'),
                    Column('employer_contribution', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'الملفات والحالة',
                'policy_document',
                'is_active',
            ),
            Submit('submit', 'حفظ', css_class='btn btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        employee_contribution = cleaned_data.get('employee_contribution', 0)
        employer_contribution = cleaned_data.get('employer_contribution', 0)
        premium_amount = cleaned_data.get('premium_amount', 0)
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError(_('تاريخ البداية لا يمكن أن يكون أكبر من تاريخ النهاية'))
        
        if employee_contribution + employer_contribution != premium_amount:
            raise ValidationError(_('مجموع مساهمة الموظف وصاحب العمل يجب أن يساوي قسط التأمين'))
        
        return cleaned_data


class EmployeeVehicleForm(forms.ModelForm):
    """نموذج سيارات الموظفين"""
    
    class Meta:
        model = EmployeeVehicle
        fields = [
            'vehicle_type', 'make', 'model', 'year', 'license_plate', 'color',
            'assigned_date', 'return_date', 'monthly_allowance',
            'insurance_expiry', 'registration_expiry', 'notes', 'is_active'
        ]
        widgets = {
            'year': forms.NumberInput(attrs={'min': 1990, 'max': 2030}),
            'assigned_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
            'insurance_expiry': forms.DateInput(attrs={'type': 'date'}),
            'registration_expiry': forms.DateInput(attrs={'type': 'date'}),
            'monthly_allowance': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        
        self.helper.layout = Layout(
            Fieldset(
                'معلومات السيارة',
                Row(
                    Column('vehicle_type', css_class='form-group col-md-6 mb-0'),
                    Column('license_plate', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('make', css_class='form-group col-md-4 mb-0'),
                    Column('model', css_class='form-group col-md-4 mb-0'),
                    Column('year', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                'color',
            ),
            Fieldset(
                'معلومات التخصيص',
                Row(
                    Column('assigned_date', css_class='form-group col-md-6 mb-0'),
                    Column('return_date', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'monthly_allowance',
            ),
            Fieldset(
                'المعلومات القانونية',
                Row(
                    Column('insurance_expiry', css_class='form-group col-md-6 mb-0'),
                    Column('registration_expiry', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'ملاحظات وحالة',
                'notes',
                'is_active',
            ),
            Submit('submit', 'حفظ', css_class='btn btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        assigned_date = cleaned_data.get('assigned_date')
        return_date = cleaned_data.get('return_date')
        
        if assigned_date and return_date and assigned_date > return_date:
            raise ValidationError(_('تاريخ التخصيص لا يمكن أن يكون أكبر من تاريخ الإرجاع'))
        
        return cleaned_data


# =============================================================================
# COMPREHENSIVE EMPLOYEE FORM
# =============================================================================

class ComprehensiveEmployeeForm(forms.ModelForm):
    """نموذج الموظف الشامل مع جميع البيانات"""
    
    class Meta:
        model = Employee
        fields = [
            'employee_number', 'first_name', 'middle_name', 'last_name', 'name_english',
            'email', 'phone_primary', 'phone_secondary', 'address',
            'national_id', 'passport_number', 'date_of_birth', 'gender', 'marital_status', 'nationality',
            'company', 'branch', 'department', 'job_position', 'direct_manager',
            'employment_type', 'hire_date', 'probation_end_date', 'contract_start_date', 'contract_end_date',
            'basic_salary', 'status', 'photo', 'notes'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'probation_end_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_start_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'type': 'date'}),
            'basic_salary': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        
        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'البيانات الأساسية',
                    Fieldset(
                        'المعلومات الشخصية',
                        'employee_number',
                        Row(
                            Column('first_name', css_class='form-group col-md-4 mb-0'),
                            Column('middle_name', css_class='form-group col-md-4 mb-0'),
                            Column('last_name', css_class='form-group col-md-4 mb-0'),
                            css_class='form-row'
                        ),
                        'name_english',
                        'photo',
                    ),
                    Fieldset(
                        'معلومات الاتصال',
                        Row(
                            Column('email', css_class='form-group col-md-6 mb-0'),
                            Column('phone_primary', css_class='form-group col-md-6 mb-0'),
                            css_class='form-row'
                        ),
                        'phone_secondary',
                        'address',
                    ),
                ),
                Tab(
                    'البيانات الشخصية',
                    Fieldset(
                        'الهوية والجنسية',
                        Row(
                            Column('national_id', css_class='form-group col-md-6 mb-0'),
                            Column('passport_number', css_class='form-group col-md-6 mb-0'),
                            css_class='form-row'
                        ),
                        Row(
                            Column('date_of_birth', css_class='form-group col-md-4 mb-0'),
                            Column('gender', css_class='form-group col-md-4 mb-0'),
                            Column('marital_status', css_class='form-group col-md-4 mb-0'),
                            css_class='form-row'
                        ),
                        'nationality',
                    ),
                ),
                Tab(
                    'بيانات العمل',
                    Fieldset(
                        'الهيكل التنظيمي',
                        Row(
                            Column('company', css_class='form-group col-md-6 mb-0'),
                            Column('branch', css_class='form-group col-md-6 mb-0'),
                            css_class='form-row'
                        ),
                        Row(
                            Column('department', css_class='form-group col-md-6 mb-0'),
                            Column('job_position', css_class='form-group col-md-6 mb-0'),
                            css_class='form-row'
                        ),
                        'direct_manager',
                    ),
                    Fieldset(
                        'تفاصيل التوظيف',
                        Row(
                            Column('employment_type', css_class='form-group col-md-6 mb-0'),
                            Column('hire_date', css_class='form-group col-md-6 mb-0'),
                            css_class='form-row'
                        ),
                        Row(
                            Column('probation_end_date', css_class='form-group col-md-6 mb-0'),
                            Column('basic_salary', css_class='form-group col-md-6 mb-0'),
                            css_class='form-row'
                        ),
                        Row(
                            Column('contract_start_date', css_class='form-group col-md-6 mb-0'),
                            Column('contract_end_date', css_class='form-group col-md-6 mb-0'),
                            css_class='form-row'
                        ),
                        'status',
                    ),
                ),
                Tab(
                    'ملاحظات',
                    'notes',
                ),
            ),
            HTML('<hr>'),
            Submit('submit', 'حفظ الموظف', css_class='btn btn-primary btn-lg'),
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamic field filtering based on company selection
        if 'company' in self.data:
            try:
                company_id = int(self.data.get('company'))
                self.fields['branch'].queryset = Branch.objects.filter(company_id=company_id).order_by('name')
                self.fields['department'].queryset = Department.objects.filter(company_id=company_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['branch'].queryset = self.instance.company.branches.order_by('name')
            self.fields['department'].queryset = self.instance.company.departments.order_by('name')
    
    def clean_employee_number(self):
        employee_number = self.cleaned_data.get('employee_number')
        if employee_number:
            # Check for uniqueness excluding current instance
            queryset = Employee.objects.filter(employee_number=employee_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError(_('رقم الموظف موجود مسبقاً'))
        
        return employee_number
    
    def clean(self):
        cleaned_data = super().clean()
        hire_date = cleaned_data.get('hire_date')
        probation_end_date = cleaned_data.get('probation_end_date')
        contract_start_date = cleaned_data.get('contract_start_date')
        contract_end_date = cleaned_data.get('contract_end_date')
        
        # Validate date relationships
        if hire_date and probation_end_date and hire_date > probation_end_date:
            raise ValidationError(_('تاريخ التوظيف لا يمكن أن يكون أكبر من تاريخ انتهاء فترة التجربة'))
        
        if contract_start_date and contract_end_date and contract_start_date > contract_end_date:
            raise ValidationError(_('تاريخ بداية العقد لا يمكن أن يكون أكبر من تاريخ انتهاء العقد'))
        
        return cleaned_data


# =============================================================================
# SEARCH AND FILTER FORMS
# =============================================================================

class EmployeeSearchForm(forms.Form):
    """نموذج البحث في الموظفين"""
    
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'البحث بالاسم، رقم الموظف، أو البريد الإلكتروني...',
            'class': 'form-control'
        }),
        label=_('البحث')
    )
    
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        empty_label="جميع الشركات",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('الشركة')
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="جميع الأقسام",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('القسم')
    )
    
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + Employee.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('الحالة')
    )
    
    employment_type = forms.ChoiceField(
        choices=[('', 'جميع أنواع التوظيف')] + Employee.EMPLOYMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('نوع التوظيف')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap4/layout/inline_field.html'
        
        self.helper.layout = Layout(
            Row(
                Column('search_query', css_class='form-group col-md-3 mb-0'),
                Column('company', css_class='form-group col-md-2 mb-0'),
                Column('department', css_class='form-group col-md-2 mb-0'),
                Column('status', css_class='form-group col-md-2 mb-0'),
                Column('employment_type', css_class='form-group col-md-2 mb-0'),
                Column(
                    Submit('submit', 'بحث', css_class='btn btn-primary'),
                    css_class='form-group col-md-1 mb-0'
                ),
                css_class='form-row'
            )
        )