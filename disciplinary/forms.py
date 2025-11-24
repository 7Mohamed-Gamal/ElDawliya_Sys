"""
نماذج (Forms) نظام الإجراءات الانضباطية
Disciplinary Actions Management Forms
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from .models import DisciplinaryAction
from employees.models import Employee


class DisciplinaryActionForm(forms.ModelForm):
    """نموذج إضافة/تعديل إجراء انضباطي"""

    ACTION_TYPE_CHOICES = [
        ('', '-- اختر نوع الإجراء --'),
        ('Verbal Warning', 'إنذار شفهي'),
        ('Written Warning', 'إنذار كتابي'),
        ('Final Warning', 'إنذار نهائي'),
        ('Suspension', 'إيقاف عن العمل'),
        ('Salary Deduction', 'خصم من الراتب'),
        ('Demotion', 'تخفيض درجة'),
        ('Termination', 'فصل من العمل'),
        ('Other', 'أخرى'),
    ]

    SEVERITY_CHOICES = [
        ('', '-- اختر مستوى الخطورة --'),
        (1, 'بسيط (1)'),
        (2, 'متوسط (2)'),
        (3, 'خطير (3)'),
        (4, 'خطير جداً (4)'),
        (5, 'حرج (5)'),
    ]

    action_type = forms.ChoiceField(
        choices=ACTION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='نوع الإجراء',
        required=True
    )

    severity_level = forms.ChoiceField(
        choices=SEVERITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='مستوى الخطورة',
        required=False
    )

    class Meta:
        """Meta class"""
        model = DisciplinaryAction
        fields = [
            'emp', 'action_type', 'action_date', 'reason',
            'severity_level', 'valid_until', 'notes'
        ]
        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'action_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اذكر سبب الإجراء الانضباطي بالتفصيل',
                'required': True
            }),
            'valid_until': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
        }
        labels = {
            'emp': 'الموظف',
            'action_type': 'نوع الإجراء',
            'action_date': 'تاريخ الإجراء',
            'reason': 'السبب',
            'severity_level': 'مستوى الخطورة',
            'valid_until': 'صالح حتى',
            'notes': 'ملاحظات',
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        # Improve employee dropdown display
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')
        self.fields['emp'].label_from_instance = lambda obj: f"{obj.emp_code} - {obj.first_name} {obj.last_name}"

        # Set default values for new actions
        if not self.instance.pk:
            self.fields['action_date'].initial = date.today()
            self.fields['severity_level'].initial = 2  # Default to medium severity

    def clean_action_date(self):
        """clean_action_date function"""
        action_date = self.cleaned_data.get('action_date')
        if action_date:
            # Don't allow future dates
            if action_date > date.today():
                raise ValidationError('تاريخ الإجراء لا يمكن أن يكون في المستقبل')

            # Don't allow dates too far in the past (more than 1 year)
            if (date.today() - action_date).days > 365:
                raise ValidationError('تاريخ الإجراء قديم جداً (أكثر من سنة)')

        return action_date

    def clean_reason(self):
        """clean_reason function"""
        reason = self.cleaned_data.get('reason')
        if reason and len(reason) < 10:
            raise ValidationError('يجب أن يكون السبب 10 أحرف على الأقل')
        return reason

    def clean(self):
        """clean function"""
        cleaned_data = super().clean()
        action_type = cleaned_data.get('action_type')
        action_date = cleaned_data.get('action_date')
        valid_until = cleaned_data.get('valid_until')
        severity_level = cleaned_data.get('severity_level')
        emp = cleaned_data.get('emp')

        # Validate valid_until date
        if valid_until:
            if action_date and valid_until <= action_date:
                raise ValidationError('تاريخ انتهاء الصلاحية يجب أن يكون بعد تاريخ الإجراء')

            # Suggest valid_until based on action type
            if action_date:
                if action_type == 'Verbal Warning' and (valid_until - action_date).days > 90:
                    self.add_error('valid_until', 'الإنذار الشفهي عادة يكون صالحاً لمدة 3 أشهر فقط')
                elif action_type == 'Written Warning' and (valid_until - action_date).days > 180:
                    self.add_error('valid_until', 'الإنذار الكتابي عادة يكون صالحاً لمدة 6 أشهر فقط')

        # Require high severity for termination
        if action_type == 'Termination':
            if severity_level and int(severity_level) < 4:
                raise ValidationError('إجراء الفصل من العمل يتطلب مستوى خطورة 4 أو 5')

        # Check for recent similar actions
        if emp and action_date:
            recent_actions = DisciplinaryAction.objects.filter(
                emp=emp,
                action_date__gte=action_date - timedelta(days=30)
            ).exclude(pk=self.instance.pk if self.instance.pk else None)

            if recent_actions.count() >= 3:
                self.add_error('emp',
                    f'تحذير: هذا الموظف لديه {recent_actions.count()} إجراءات انضباطية في آخر 30 يوم'
                )

        return cleaned_data


class DisciplinaryActionSearchForm(forms.Form):
    """نموذج البحث في الإجراءات الانضباطية"""

    ACTION_TYPE_CHOICES = [
        ('', 'الكل'),
        ('Verbal Warning', 'إنذار شفهي'),
        ('Written Warning', 'إنذار كتابي'),
        ('Final Warning', 'إنذار نهائي'),
        ('Suspension', 'إيقاف عن العمل'),
        ('Salary Deduction', 'خصم من الراتب'),
        ('Demotion', 'تخفيض درجة'),
        ('Termination', 'فصل من العمل'),
        ('Other', 'أخرى'),
    ]

    SEVERITY_CHOICES = [
        ('', 'الكل'),
        (1, 'بسيط (1)'),
        (2, 'متوسط (2)'),
        (3, 'خطير (3)'),
        (4, 'خطير جداً (4)'),
        (5, 'حرج (5)'),
    ]

    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(emp_status='Active').order_by('first_name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الموظف'
    )

    action_type = forms.ChoiceField(
        choices=ACTION_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='نوع الإجراء'
    )

    severity_level = forms.ChoiceField(
        choices=SEVERITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='مستوى الخطورة'
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='من تاريخ'
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='إلى تاريخ'
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث في السبب أو الملاحظات'
        }),
        label='بحث'
    )


class BulkDisciplinaryActionForm(forms.Form):
    """نموذج الإجراءات الجماعية"""

    action = forms.ChoiceField(
        label='الإجراء',
        choices=[
            ('delete', 'حذف المحدد'),
            ('export', 'تصدير المحدد'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    action_ids = forms.CharField(
        widget=forms.HiddenInput()
    )

    def clean_action_ids(self):
        """التحقق من معرفات الإجراءات"""
        action_ids = self.cleaned_data.get('action_ids')
        if action_ids:
            try:
                ids = [int(id.strip()) for id in action_ids.split(',') if id.strip()]
                if not ids:
                    raise ValidationError('يجب تحديد إجراء واحد على الأقل.')
                return ids
            except ValueError:
                raise ValidationError('معرفات الإجراءات غير صحيحة.')
        else:
            raise ValidationError('يجب تحديد إجراء واحد على الأقل.')

