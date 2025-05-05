from django import forms
from .models import Meeting
from django.contrib.auth import get_user_model

User = get_user_model()

class MeetingForm(forms.ModelForm):
    attendees = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2', 'style': 'width: 100%'})
    )

    tasks = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'أدخل المهام مفصولة بسطر جديد لكل مهمة',
            'id': 'tasks-textarea'
        }),
        required=False,
        help_text='أدخل كل مهمة في سطر منفصل. سيتم إنشاؤها تلقائيًا وربطها بالاجتماع.'
    )

    # حقل مخفي لتخزين تعيينات المهام بصيغة JSON
    task_assignments = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'task-assignments'}),
        required=False
    )

    # حقل الحالة مع قيمة افتراضية
    status = forms.ChoiceField(
        choices=Meeting.STATUS_CHOICES,
        initial='pending',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        tasks = cleaned_data.get('tasks', '')
        task_assignments = cleaned_data.get('task_assignments', '')

        # If there are tasks, check if they have assignments
        if tasks:
            task_lines = [line.strip() for line in tasks.split('\n') if line.strip()]
            if task_lines:
                # If there are task lines but no assignments JSON, try to get it from POST data
                if not task_assignments and hasattr(self, 'data'):
                    task_assignments = self.data.get('task_assignments', '')
                    # If we found assignments in POST data, add it to cleaned_data
                    if task_assignments:
                        cleaned_data['task_assignments'] = task_assignments
                        print("Retrieved task_assignments from POST data:", task_assignments)

                # If still no assignments, add an error
                if not task_assignments:
                    self.add_error('tasks', 'يرجى تعيين المهام للحضور')

        return cleaned_data

    class Meta:
        model = Meeting
        fields = ['title', 'date', 'topic', 'status', 'attendees']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان الاجتماع'}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'topic': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'موضوع الاجتماع'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
