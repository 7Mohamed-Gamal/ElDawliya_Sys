from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.note_models import EmployeeNote

class EmployeeNoteForm(forms.ModelForm):
    class Meta:
        model = EmployeeNote
        fields = ['employee', 'title', 'content', 'is_important']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
