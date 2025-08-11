from django import forms
from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name','name_en','tax_number','commercial_register','phone','email','website',
            'address','city','country','postal_code','is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control','placeholder':'اسم الشركة'}),
            'name_en': forms.TextInput(attrs={'class':'form-control','placeholder':'Company Name (EN)'}),
            'tax_number': forms.TextInput(attrs={'class':'form-control'}),
            'commercial_register': forms.TextInput(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'website': forms.URLInput(attrs={'class':'form-control'}),
            'address': forms.TextInput(attrs={'class':'form-control'}),
            'city': forms.TextInput(attrs={'class':'form-control'}),
            'country': forms.TextInput(attrs={'class':'form-control'}),
            'postal_code': forms.TextInput(attrs={'class':'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name','').strip()
        if not name:
            raise forms.ValidationError('اسم الشركة مطلوب')
        return name

