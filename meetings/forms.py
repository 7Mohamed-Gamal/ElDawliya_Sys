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
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'أدخل المهام مفصولة بسطر جديد لكل مهمة'}),
        required=False,
        help_text='أدخل كل مهمة في سطر منفصل. سيتم إنشاؤها تلقائيًا وربطها بالاجتماع.'
    )
    
    class Meta:
        model = Meeting
        fields = ['title', 'date', 'topic', 'attendees']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان الاجتماع'}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'topic': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'موضوع الاجتماع'}),
        }
