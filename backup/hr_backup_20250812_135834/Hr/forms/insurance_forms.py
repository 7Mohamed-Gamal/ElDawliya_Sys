from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.insurance_models import JobInsurance

class JobInsuranceForm(forms.ModelForm):
    class Meta:
        model = JobInsurance
        fields = ['job_code_insurance', 'job_name_insurance']
        widgets = {
            'job_code_insurance': forms.NumberInput(attrs={'class': 'form-control'}),
            'job_name_insurance': forms.TextInput(attrs={'class': 'form-control'})
        }
