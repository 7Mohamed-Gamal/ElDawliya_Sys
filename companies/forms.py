from django import forms
from .models import Company


class CompanyForm(forms.ModelForm):
    """CompanyForm class"""
    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        # Ensure is_active defaults to True for new companies
        if not self.instance.pk:
            self.fields['is_active'].initial = True
        # Hide the is_active field from the form since we handle it programmatically
        self.fields['is_active'].widget = forms.HiddenInput()

    class Meta:
        """Meta class"""
        model = Company
        fields = [
            'name','name_en','tax_number','commercial_register','phone','email','website',
            'address','city','country','postal_code','is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'اسم الشركة',
                'required': True
            }),
            'name_en': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Company Name (EN)'
            }),
            'tax_number': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'الرقم الضريبي'
            }),
            'commercial_register': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'رقم السجل التجاري'
            }),
            'phone': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'رقم الهاتف'
            }),
            'email': forms.EmailInput(attrs={
                'class':'form-control',
                'placeholder':'البريد الإلكتروني'
            }),
            'website': forms.URLInput(attrs={
                'class':'form-control',
                'placeholder':'الموقع الإلكتروني'
            }),
            'address': forms.Textarea(attrs={
                'class':'form-control',
                'placeholder':'العنوان',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'المدينة'
            }),
            'country': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'الدولة'
            }),
            'postal_code': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'الرمز البريدي'
            }),
        }
        labels = {
            'name': 'اسم الشركة',
            'name_en': 'اسم الشركة (بالإنجليزية)',
            'tax_number': 'الرقم الضريبي',
            'commercial_register': 'رقم السجل التجاري',
            'phone': 'رقم الهاتف',
            'email': 'البريد الإلكتروني',
            'website': 'الموقع الإلكتروني',
            'address': 'العنوان',
            'city': 'المدينة',
            'country': 'الدولة',
            'postal_code': 'الرمز البريدي',
            'is_active': 'نشط',
        }

    def clean_name(self):
        """clean_name function"""
        name = self.cleaned_data.get('name','').strip()
        if not name:
            raise forms.ValidationError('اسم الشركة مطلوب')

        # Check for duplicate company names
        if Company.objects.filter(name__iexact=name, is_active=True).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError('يوجد شركة أخرى بنفس الاسم')

        return name

    def clean_tax_number(self):
        """clean_tax_number function"""
        tax_number = self.cleaned_data.get('tax_number')
        if tax_number:
            tax_number = tax_number.strip()
            # Check for duplicate tax numbers
            if Company.objects.filter(tax_number=tax_number, is_active=True).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError('يوجد شركة أخرى بنفس الرقم الضريبي')
        return tax_number

    def clean_commercial_register(self):
        """clean_commercial_register function"""
        commercial_register = self.cleaned_data.get('commercial_register')
        if commercial_register:
            commercial_register = commercial_register.strip()
            # Check for duplicate commercial register numbers
            if Company.objects.filter(commercial_register=commercial_register, is_active=True).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError('يوجد شركة أخرى بنفس رقم السجل التجاري')
        return commercial_register

    def clean_email(self):
        """clean_email function"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            # Check for duplicate emails
            if Company.objects.filter(email__iexact=email, is_active=True).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError('يوجد شركة أخرى بنفس البريد الإلكتروني')
        return email

