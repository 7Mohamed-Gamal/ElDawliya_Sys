from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.evaluation_models import EmployeeEvaluation

class EmployeeEvaluationForm(forms.ModelForm):
    class Meta:
        model = EmployeeEvaluation
        fields = ['employee', 'evaluation_date', 'period_start', 'period_end',
                 'performance_rating', 'attendance_rating', 'teamwork_rating',
                 'initiative_rating', 'communication_rating',
                 'strengths', 'areas_for_improvement', 'goals']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'evaluation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'performance_rating': forms.Select(attrs={'class': 'form-select'}),
            'attendance_rating': forms.Select(attrs={'class': 'form-select'}),
            'teamwork_rating': forms.Select(attrs={'class': 'form-select'}),
            'initiative_rating': forms.Select(attrs={'class': 'form-select'}),
            'communication_rating': forms.Select(attrs={'class': 'form-select'}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'areas_for_improvement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
