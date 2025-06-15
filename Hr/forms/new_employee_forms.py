# =============================================================================
# ElDawliya HR Management System - New Employee Forms
# =============================================================================
# Forms for employee management (Employee, Documents, Emergency Contacts, etc.)
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Submit, HTML, Tab, TabHolder
from crispy_forms.bootstrap import Field, FormActions
from datetime import date, timedelta

from Hr.models import (
    Employee, Company, Branch, Department, JobPosition,
    EmployeeDocument, EmployeeEmergencyContact, EmployeeTraining, EmployeeNote
)

User = get_user_model()


class NewEmployeeForm(forms.ModelForm):
    """نموذج إنشاء وتحديث الموظف الجديد"""
    
    class Meta:
        model = Employee
        fields = [
            'employee_number', 'first_name', 'middle_name', 'last_name', 'name_english',
            'email', 'phone_primary', 'phone_secondary', 'address',
            'national_id', 'passport_number', 'date_of_birth', 'place_of_birth',
            'gender', 'marital_status', 'nationality', 'religion',
            'company', 'branch', 'department', 'job_position', 'direct_manager',
            'employment_type', 'hire_date', 'probation_end_date',
            'contract_start_date', 'contract_end_date', 'status', 'photo', 'notes'
        ]
        widgets = {
            'employee_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الموظف')
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الاسم الأول'),
                'dir': 'rtl'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الاسم الأوسط'),
                'dir': 'rtl'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم العائلة'),
                'dir': 'rtl'
            }),
            'name_english': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الاسم بالإنجليزية'),
                'dir': 'ltr'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('البريد الإلكتروني')
            }),
            'phone_primary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الهاتف الأساسي')
            }),
            'phone_secondary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الهاتف الثانوي')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('العنوان'),
                'dir': 'rtl'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الهوية الوطنية')
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم جواز السفر')
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'place_of_birth': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('مكان الميلاد'),
                'dir': 'rtl'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الجنسية'),
                'dir': 'rtl'
            }),
            'religion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الديانة'),
                'dir': 'rtl'
            }),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'job_position': forms.Select(attrs={'class': 'form-select'}),
            'direct_manager': forms.Select(attrs={'class': 'form-select'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'probation_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'contract_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'contract_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('ملاحظات'),
                'dir': 'rtl'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'enctype': 'multipart/form-data'}
        
        # Set default values
        if not self.instance.pk:
            self.fields['hire_date'].initial = date.today()
            self.fields['status'].initial = 'active'

        self.helper.layout = Layout(
            TabHolder(
                Tab(_('المعلومات الشخصية'),
                    Row(
                        Column('employee_number', css_class='col-md-4'),
                        Column('status', css_class='col-md-4'),
                        Column('photo', css_class='col-md-4'),
                    ),
                    Row(
                        Column('first_name', css_class='col-md-4'),
                        Column('middle_name', css_class='col-md-4'),
                        Column('last_name', css_class='col-md-4'),
                    ),
                    'name_english',
                    Row(
                        Column('national_id', css_class='col-md-6'),
                        Column('passport_number', css_class='col-md-6'),
                    ),
                    Row(
                        Column('date_of_birth', css_class='col-md-6'),
                        Column('place_of_birth', css_class='col-md-6'),
                    ),
                    Row(
                        Column('gender', css_class='col-md-4'),
                        Column('marital_status', css_class='col-md-4'),
                        Column('nationality', css_class='col-md-4'),
                    ),
                    'religion',
                ),
                Tab(_('معلومات الاتصال'),
                    'email',
                    Row(
                        Column('phone_primary', css_class='col-md-6'),
                        Column('phone_secondary', css_class='col-md-6'),
                    ),
                    'address',
                ),
                Tab(_('المعلومات الوظيفية'),
                    Row(
                        Column('company', css_class='col-md-6'),
                        Column('branch', css_class='col-md-6'),
                    ),
                    Row(
                        Column('department', css_class='col-md-6'),
                        Column('job_position', css_class='col-md-6'),
                    ),
                    Row(
                        Column('direct_manager', css_class='col-md-6'),
                        Column('employment_type', css_class='col-md-6'),
                    ),
                    Row(
                        Column('hire_date', css_class='col-md-6'),
                        Column('probation_end_date', css_class='col-md-6'),
                    ),
                    Row(
                        Column('contract_start_date', css_class='col-md-6'),
                        Column('contract_end_date', css_class='col-md-6'),
                    ),
                ),
                Tab(_('ملاحظات'),
                    'notes',
                ),
            ),
            FormActions(
                Submit('submit', _('حفظ'), css_class='btn btn-primary btn-lg'),
                HTML('<a href="{% url "hr:employee_list" %}" class="btn btn-secondary btn-lg ms-2">إلغاء</a>'),
                css_class='text-center mt-4'
            )
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = Employee.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(_('البريد الإلكتروني موجود مسبقاً'))
        return email

    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if national_id:
            qs = Employee.objects.filter(national_id=national_id)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(_('رقم الهوية الوطنية موجود مسبقاً'))
        return national_id

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            # Check minimum age (18 years)
            min_date = date.today() - timedelta(days=18*365)
            if date_of_birth > min_date:
                raise ValidationError(_('يجب أن يكون عمر الموظف 18 سنة على الأقل'))
        return date_of_birth


class EmployeeDocumentForm(forms.ModelForm):
    """نموذج إضافة وثائق الموظف"""
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'employee', 'document_type', 'title', 'description',
            'file', 'expiry_date'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('عنوان الوثيقة'),
                'dir': 'rtl'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('وصف الوثيقة'),
                'dir': 'rtl'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        
        if employee:
            self.fields['employee'].initial = employee
            self.fields['employee'].widget = forms.HiddenInput()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.attrs = {'enctype': 'multipart/form-data'}
        
        self.helper.layout = Layout(
            'employee',
            Row(
                Column('document_type', css_class='col-md-6'),
                Column('title', css_class='col-md-6'),
            ),
            'description',
            Row(
                Column('file', css_class='col-md-6'),
                Column('expiry_date', css_class='col-md-6'),
            ),
            FormActions(
                Submit('submit', _('رفع الوثيقة'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class EmployeeEmergencyContactForm(forms.ModelForm):
    """نموذج إضافة جهات الاتصال في حالات الطوارئ"""
    
    class Meta:
        model = EmployeeEmergencyContact
        fields = [
            'employee', 'name', 'relationship', 'phone_primary',
            'phone_secondary', 'email', 'address', 'is_primary'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم جهة الاتصال'),
                'dir': 'rtl'
            }),
            'relationship': forms.Select(attrs={'class': 'form-select'}),
            'phone_primary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الهاتف الأساسي')
            }),
            'phone_secondary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الهاتف الثانوي')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('البريد الإلكتروني')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('العنوان'),
                'dir': 'rtl'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        
        if employee:
            self.fields['employee'].initial = employee
            self.fields['employee'].widget = forms.HiddenInput()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            'employee',
            Row(
                Column('name', css_class='col-md-6'),
                Column('relationship', css_class='col-md-6'),
            ),
            Row(
                Column('phone_primary', css_class='col-md-6'),
                Column('phone_secondary', css_class='col-md-6'),
            ),
            'email',
            'address',
            'is_primary',
            FormActions(
                Submit('submit', _('إضافة جهة الاتصال'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
