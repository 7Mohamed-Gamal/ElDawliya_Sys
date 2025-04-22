from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.hr_task_models import HrTask

class HrTaskForm(forms.ModelForm):
    class Meta:
        model = HrTask
        fields = ['title', 'description', 'task_type', 'assigned_to', 'status', 'priority', 
                 'start_date', 'due_date', 'progress', 'steps_taken', 'reminder_days']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'task_type': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'steps_taken': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reminder_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
