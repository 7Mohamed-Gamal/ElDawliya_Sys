from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from datetime import datetime, timedelta
from .models import TaskStep, Task

User = get_user_model()

class TaskStepForm(forms.ModelForm):
    """Enhanced form for creating task steps"""

    class Meta:
        model = TaskStep
        fields = ['description', 'notes', 'completed']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'اكتب وصف الخطوة المتخذة...',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'ملاحظات إضافية (اختياري)...'
            }),
            'completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'description': 'وصف الخطوة',
            'notes': 'ملاحظات',
            'completed': 'تم إنجاز هذه الخطوة'
        }

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise ValidationError('وصف الخطوة يجب أن يكون 10 أحرف على الأقل')
        return description

class TaskForm(forms.ModelForm):
    """Enhanced form for creating and editing tasks"""

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان المهمة (اختياري)'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'وصف تفصيلي للمهمة والمطلوب إنجازه...',
                'required': True
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'title': 'عنوان المهمة',
            'description': 'وصف المهمة',
            'assigned_to': 'المكلف بالمهمة',
            'priority': 'الأولوية',
            'start_date': 'تاريخ البدء',
            'end_date': 'تاريخ الانتهاء',
            'status': 'حالة المهمة'
        }
        help_texts = {
            'title': 'عنوان مختصر للمهمة (اختياري)',
            'description': 'وصف تفصيلي للمهمة والمطلوب إنجازه',
            'priority': 'أولوية المهمة تؤثر على ترتيب العرض',
            'start_date': 'تاريخ ووقت بدء العمل على المهمة',
            'end_date': 'تاريخ ووقت الانتهاء المتوقع من المهمة'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set default dates if creating new task
        if not self.instance.pk:
            now = timezone.now()
            self.fields['start_date'].initial = now
            self.fields['end_date'].initial = now + timedelta(days=7)

        # Limit assigned_to choices for non-superusers
        if self.user and not self.user.is_superuser:
            self.fields['assigned_to'].queryset = User.objects.filter(id=self.user.id)
            self.fields['assigned_to'].initial = self.user
            self.fields['assigned_to'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        description = cleaned_data.get('description')

        # Validate dates
        if start_date and end_date:
            if end_date < start_date:
                self.add_error('end_date', "تاريخ الانتهاء لا يمكن أن يكون قبل تاريخ البدء")

            # Warn if task duration is too long
            duration = end_date - start_date
            if duration.days > 365:
                self.add_error('end_date', "مدة المهمة لا يمكن أن تزيد عن سنة واحدة")

        # Validate description length
        if description and len(description.strip()) < 20:
            self.add_error('description', 'وصف المهمة يجب أن يكون 20 حرف على الأقل')

        return cleaned_data

    def clean_assigned_to(self):
        assigned_to = self.cleaned_data.get('assigned_to')

        # Non-superusers can only assign tasks to themselves
        if self.user and not self.user.is_superuser:
            if assigned_to != self.user:
                raise ValidationError('يمكنك فقط تكليف نفسك بالمهام')

        return assigned_to

class TaskFilterForm(forms.Form):
    """Form for filtering tasks in list view"""

    STATUS_CHOICES = [('', 'جميع الحالات')] + Task.STATUS_CHOICES
    PRIORITY_CHOICES = [('', 'جميع الأولويات')] + Task.PRIORITY_CHOICES

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في العنوان أو الوصف...'
        }),
        label='البحث'
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الحالة'
    )

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الأولوية'
    )

    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label='جميع المكلفين',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='المكلف'
    )

    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='المهام المتأخرة فقط'
    )

class BulkTaskUpdateForm(forms.Form):
    """Form for bulk updating tasks"""

    ACTION_CHOICES = [
        ('', 'اختر إجراء...'),
        ('update_status', 'تحديث الحالة'),
        ('update_priority', 'تحديث الأولوية'),
        ('reassign', 'إعادة تكليف'),
        ('delete', 'حذف'),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الإجراء'
    )

    new_status = forms.ChoiceField(
        choices=Task.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الحالة الجديدة'
    )

    new_priority = forms.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الأولوية الجديدة'
    )

    new_assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='المكلف الجديد'
    )

    task_ids = forms.CharField(
        widget=forms.HiddenInput(),
        label='معرفات المهام'
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')

        if action == 'update_status' and not cleaned_data.get('new_status'):
            self.add_error('new_status', 'يجب اختيار الحالة الجديدة')

        if action == 'update_priority' and not cleaned_data.get('new_priority'):
            self.add_error('new_priority', 'يجب اختيار الأولوية الجديدة')

        if action == 'reassign' and not cleaned_data.get('new_assigned_to'):
            self.add_error('new_assigned_to', 'يجب اختيار المكلف الجديد')

        return cleaned_data

class TaskStatusUpdateForm(forms.Form):
    """Simple form for updating task status via AJAX"""

    status = forms.ChoiceField(
        choices=Task.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class TaskCommentForm(forms.Form):
    """Form for adding comments to tasks"""

    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'اكتب تعليقك هنا...'
        }),
        label='التعليق'
    )

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if comment and len(comment.strip()) < 5:
            raise ValidationError('التعليق يجب أن يكون 5 أحرف على الأقل')
        return comment


class UnifiedTaskFilterForm(forms.Form):
    """Enhanced form for filtering unified tasks (regular + meeting tasks)"""

    STATUS_CHOICES = [('', 'جميع الحالات')] + Task.STATUS_CHOICES
    PRIORITY_CHOICES = [('', 'جميع الأولويات')] + Task.PRIORITY_CHOICES
    TASK_TYPE_CHOICES = [
        ('', 'جميع الأنواع'),
        ('regular', 'المهام العادية'),
        ('meeting', 'مهام الاجتماعات'),
    ]

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في العنوان أو الوصف...'
        }),
        label='البحث'
    )

    task_type = forms.ChoiceField(
        choices=TASK_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='نوع المهمة'
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الحالة'
    )

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الأولوية'
    )

    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label='جميع المكلفين',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='المكلف'
    )

    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='المهام المتأخرة فقط'
    )

    meeting = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label='جميع الاجتماعات',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الاجتماع'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set meeting queryset based on user permissions
        from meetings.models import Meeting
        if user:
            if user.is_superuser:
                self.fields['meeting'].queryset = Meeting.objects.all()
            else:
                # Show meetings where user is attendee or has tasks
                self.fields['meeting'].queryset = Meeting.objects.filter(
                    Q(attendees__user=user) |
                    Q(meeting_tasks__assigned_to=user) |
                    Q(tasks__assigned_to=user)
                ).distinct()


class UnifiedTaskStepForm(forms.Form):
    """Form for adding steps to unified tasks (works for both types)"""

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'اكتب وصف الخطوة المتخذة...',
            'required': True
        }),
        label='وصف الخطوة'
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'ملاحظات إضافية (اختياري)...'
        }),
        label='ملاحظات'
    )

    completed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='تم إنجاز هذه الخطوة'
    )

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise ValidationError('وصف الخطوة يجب أن يكون 10 أحرف على الأقل')
        return description


class UnifiedTaskStatusForm(forms.Form):
    """Form for updating task status (works for both task types)"""

    def __init__(self, *args, **kwargs):
        task_type = kwargs.pop('task_type', 'regular')
        super().__init__(*args, **kwargs)

        if task_type == 'meeting':
            # Meeting tasks have limited status choices
            from meetings.models import MeetingTask
            choices = MeetingTask.STATUS_CHOICES
        else:
            # Regular tasks have full status choices
            choices = Task.STATUS_CHOICES

        self.fields['status'] = forms.ChoiceField(
            choices=choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            label='الحالة'
        )


class MeetingTaskEditForm(forms.Form):
    """Form for editing meeting tasks from the tasks interface"""

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'وصف تفصيلي للمهمة...',
            'required': True
        }),
        label='وصف المهمة'
    )

    status = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='حالة المهمة'
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='تاريخ الانتهاء المتوقع'
    )

    def __init__(self, *args, **kwargs):
        meeting_task = kwargs.pop('meeting_task', None)
        super().__init__(*args, **kwargs)

        # Set status choices for meeting tasks
        from meetings.models import MeetingTask
        self.fields['status'].choices = MeetingTask.STATUS_CHOICES

        # Pre-populate fields if editing existing task
        if meeting_task:
            self.fields['description'].initial = meeting_task.description
            self.fields['status'].initial = meeting_task.status
            self.fields['end_date'].initial = meeting_task.end_date

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 20:
            raise ValidationError('وصف المهمة يجب أن يكون 20 حرف على الأقل')
        return description
