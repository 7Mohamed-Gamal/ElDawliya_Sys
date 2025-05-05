from django import forms
from django.utils.translation import gettext_lazy as _
from .models import TaskCategory, EmployeeTask, TaskStep, TaskReminder


class TaskCategoryForm(forms.ModelForm):
    """
    نموذج إنشاء وتعديل تصنيفات المهام
    """
    class Meta:
        model = TaskCategory
        fields = ['name', 'description', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'color': forms.TextInput(attrs={'class': 'form-control color-picker'}),
            'icon': forms.TextInput(attrs={'class': 'form-control icon-picker'}),
        }


class EmployeeTaskForm(forms.ModelForm):
    """
    نموذج إنشاء وتعديل مهام الموظفين
    """
    class Meta:
        model = EmployeeTask
        fields = ['title', 'description', 'category', 'assigned_to', 'status', 
                 'priority', 'start_date', 'due_date', 'progress', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # إذا كان المستخدم ليس مشرفًا، قم بتعيين حقل created_by تلقائيًا
        if self.user and not self.user.is_superuser:
            self.instance.created_by = self.user


class TaskStepForm(forms.ModelForm):
    """
    نموذج إنشاء وتعديل خطوات المهام
    """
    class Meta:
        model = TaskStep
        fields = ['description', 'completed']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.task = kwargs.pop('task', None)
        super().__init__(*args, **kwargs)
        
        # إذا تم تمرير المهمة، قم بتعيين حقل task تلقائيًا
        if self.task:
            self.instance.task = self.task
        
        # إذا تم تمرير المستخدم، قم بتعيين حقل created_by تلقائيًا
        if self.user:
            self.instance.created_by = self.user


class TaskReminderForm(forms.ModelForm):
    """
    نموذج إنشاء وتعديل تذكيرات المهام
    """
    class Meta:
        model = TaskReminder
        fields = ['reminder_date']
        widgets = {
            'reminder_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop('task', None)
        super().__init__(*args, **kwargs)
        
        # إذا تم تمرير المهمة، قم بتعيين حقل task تلقائيًا
        if self.task:
            self.instance.task = self.task


class TaskFilterForm(forms.Form):
    """
    نموذج تصفية المهام
    """
    STATUS_CHOICES = [('', _('جميع الحالات'))] + list(EmployeeTask.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', _('جميع الأولويات'))] + list(EmployeeTask.PRIORITY_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=TaskCategory.objects.all(),
        required=False,
        empty_label=_('جميع التصنيفات'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('بحث...')})
    )
