from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.task_models import EmployeeTask, TaskStep

class EmployeeTaskForm(forms.ModelForm):
    class Meta:
        model = EmployeeTask
        fields = ['title', 'description', 'employee', 'status', 'priority', 'start_date', 'due_date', 'progress', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TaskStepForm(forms.ModelForm):
    class Meta:
        model = TaskStep
        fields = ['description', 'completed']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'أدخل وصف الخطوة هنا...'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # لا نحتاج إلى حقل task_id في النموذج لأننا سنقوم بتعيينه في وظيفة العرض
