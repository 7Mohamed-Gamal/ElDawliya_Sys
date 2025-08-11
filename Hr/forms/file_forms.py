from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.legacy.legacy_models import EmployeeFile

class EmployeeFileForm(forms.ModelForm):
    class Meta:
        model = EmployeeFile
        fields = ['employee', 'title', 'file_type', 'file']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
