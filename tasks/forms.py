from django import forms
from .models import TaskStep, Task
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskStepForm(forms.ModelForm):
    class Meta:
        model = TaskStep
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان المهمة (اختياري)'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'وصف تفصيلي للمهمة'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'title': 'عنوان المهمة',
            'description': 'وصف المهمة',
            'assigned_to': 'المكلف بالمهمة',
            'start_date': 'تاريخ البدء',
            'end_date': 'تاريخ الانتهاء',
            'status': 'حالة المهمة'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate that end_date is not before start_date
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', "تاريخ الانتهاء لا يمكن أن يكون قبل تاريخ البدء")
        
        return cleaned_data
