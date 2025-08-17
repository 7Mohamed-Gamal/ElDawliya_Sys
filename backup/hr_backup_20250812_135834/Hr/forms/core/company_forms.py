"""
Company Forms for HRMS
Forms for company management operations
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from Hr.models.core.company_models import Company


class CompanyForm(forms.ModelForm):
    """Form for creating and editing companies"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'legal_name', 'tax_id', 'registration_number',
            'email', 'phone', 'website', 'address', 'city', 'country', 'postal_code',
            'logo', 'primary_color', 'secondary_color', 'industry', 'established_date',
            'employee_count', 'timezone', 'currency', 'fiscal_year_start',
            'is_active'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم الشركة'),
                'required': True
            }),
            'legal_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الاسم القانوني للشركة')
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الرقم الضريبي')
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم السجل التجاري')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('البريد الإلكتروني')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الهاتف')
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('الموقع الإلكتروني')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('العنوان')
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('المدينة')
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'مصر'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الرمز البريدي')
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'primary_color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#007bff'
            }),
            'secondary_color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#6c757d'
            }),
            'industry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('نوع النشاط')
            }),
            'established_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'employee_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'timezone': forms.Select(attrs={
                'class': 'form-control'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fiscal_year_start': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'name': _('اسم الشركة'),
            'legal_name': _('الاسم القانوني'),
            'tax_id': _('الرقم الضريبي'),
            'registration_number': _('رقم السجل التجاري'),
            'email': _('البريد الإلكتروني'),
            'phone': _('رقم الهاتف'),
            'website': _('الموقع الإلكتروني'),
            'address': _('العنوان'),
            'city': _('المدينة'),
            'country': _('الدولة'),
            'postal_code': _('الرمز البريدي'),
            'logo': _('شعار الشركة'),
            'primary_color': _('اللون الأساسي'),
            'secondary_color': _('اللون الثانوي'),
            'industry': _('نوع النشاط'),
            'established_date': _('تاريخ التأسيس'),
            'employee_count': _('عدد الموظفين'),
            'timezone': _('المنطقة الزمنية'),
            'currency': _('العملة'),
            'fiscal_year_start': _('بداية السنة المالية'),
            'is_active': _('نشط'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add timezone choices
        self.fields['timezone'].choices = [
            ('Africa/Cairo', _('القاهرة (GMT+2)')),
            ('Asia/Riyadh', _('الرياض (GMT+3)')),
            ('Asia/Dubai', _('دبي (GMT+4)')),
            ('Europe/London', _('لندن (GMT+0)')),
            ('America/New_York', _('نيويورك (GMT-5)')),
        ]
        
        # Add currency choices
        self.fields['currency'].choices = [
            ('EGP', _('جنيه مصري')),
            ('SAR', _('ريال سعودي')),
            ('AED', _('درهم إماراتي')),
            ('USD', _('دولار أمريكي')),
            ('EUR', _('يورو')),
        ]
        
        # Make certain fields required
        self.fields['name'].required = True
        self.fields['email'].required = False
        self.fields['phone'].required = False
    
    def clean_tax_id(self):
        """Validate tax ID uniqueness"""
        tax_id = self.cleaned_data.get('tax_id')
        if tax_id:
            # Check if tax_id already exists (excluding current instance)
            existing = Company.objects.filter(tax_id=tax_id)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(_('الرقم الضريبي موجود بالفعل'))
        
        return tax_id
    
    def clean_registration_number(self):
        """Validate registration number uniqueness"""
        registration_number = self.cleaned_data.get('registration_number')
        if registration_number:
            # Check if registration_number already exists (excluding current instance)
            existing = Company.objects.filter(registration_number=registration_number)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(_('رقم السجل التجاري موجود بالفعل'))
        
        return registration_number
    
    def clean_logo(self):
        """Validate logo file"""
        logo = self.cleaned_data.get('logo')
        if logo:
            # Check file size (max 5MB)
            if logo.size > 5 * 1024 * 1024:
                raise ValidationError(_('حجم الملف يجب أن يكون أقل من 5 ميجابايت'))
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if hasattr(logo, 'content_type') and logo.content_type not in allowed_types:
                raise ValidationError(_('نوع الملف غير مدعوم. يرجى استخدام JPG أو PNG أو GIF'))
        
        return logo
    
    def save(self, commit=True):
        """Save the company with additional processing"""
        company = super().save(commit=False)
        
        # Set legal name to name if not provided
        if not company.legal_name:
            company.legal_name = company.name
        
        if commit:
            company.save()
        
        return company


class CompanySearchForm(forms.Form):
    """Form for searching companies"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('البحث في الشركات...'),
            'autocomplete': 'off'
        }),
        label=_('البحث')
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', _('جميع الحالات')),
            ('active', _('نشط')),
            ('inactive', _('غير نشط')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('الحالة')
    )
    
    industry = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('نوع النشاط')
        }),
        label=_('نوع النشاط')
    )
