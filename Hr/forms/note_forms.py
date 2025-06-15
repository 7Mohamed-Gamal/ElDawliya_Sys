from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from Hr.models.note_models import EmployeeNote
from Hr.models.employee_model import Employee
from Hr.models.base_models import Department, Car


class EmployeeSearchForm(forms.Form):
    """نموذج البحث عن الموظفين"""

    # البحث السريع
    quick_search = forms.CharField(
        label=_('البحث السريع'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'ابحث بالاسم، الكود، الرقم القومي، أو الهاتف...',
            'autocomplete': 'off'
        })
    )

    # معايير البحث المتقدمة
    employee_id = forms.CharField(
        label=_('رقم الموظف'),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'رقم الموظف'
        })
    )

    full_name = forms.CharField(
        label=_('الاسم الكامل'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الاسم الكامل'
        })
    )

    national_id = forms.CharField(
        label=_('الرقم القومي'),
        max_length=14,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الرقم القومي'
        })
    )

    phone = forms.CharField(
        label=_('رقم الهاتف'),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'رقم الهاتف'
        })
    )

    department = forms.ModelChoiceField(
        label=_('القسم'),
        queryset=Department.objects.all(),
        required=False,
        empty_label=_('جميع الأقسام'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    car = forms.ModelChoiceField(
        label=_('السيارة'),
        queryset=Car.objects.all(),
        required=False,
        empty_label=_('جميع السيارات'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class EmployeeNoteForm(forms.ModelForm):
    """نموذج إنشاء وتعديل ملاحظات الموظفين"""

    class Meta:
        model = EmployeeNote
        fields = [
            'title', 'content', 'note_type', 'priority',
            'evaluation_link', 'evaluation_score', 'tags',
            'is_important', 'is_confidential', 'follow_up_required',
            'follow_up_date'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'عنوان الملاحظة',
                'maxlength': '200'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'اكتب تفاصيل الملاحظة هنا...'
            }),
            'note_type': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'evaluation_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'رابط التقييم (اختياري)'
            }),
            'evaluation_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'درجة التقييم'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'علامات مفصولة بفواصل (مثال: أداء، تطوير، تدريب)'
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'form-check-input form-check-input-lg'
            }),
            'is_confidential': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'follow_up_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

        labels = {
            'title': _('عنوان الملاحظة'),
            'content': _('محتوى الملاحظة'),
            'note_type': _('نوع الملاحظة'),
            'priority': _('الأولوية'),
            'evaluation_link': _('رابط التقييم'),
            'evaluation_score': _('درجة التقييم'),
            'tags': _('العلامات'),
            'is_important': _('ملاحظة مهمة'),
            'is_confidential': _('سرية'),
            'follow_up_required': _('يتطلب متابعة'),
            'follow_up_date': _('تاريخ المتابعة'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # إضافة CSS classes إضافية
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'dir': 'rtl'})

        # جعل بعض الحقول مطلوبة
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['note_type'].required = True

    def clean_evaluation_score(self):
        """التحقق من صحة درجة التقييم"""
        score = self.cleaned_data.get('evaluation_score')
        if score is not None:
            if score < 0 or score > 100:
                raise forms.ValidationError(_('درجة التقييم يجب أن تكون بين 0 و 100'))
        return score

    def clean(self):
        """التحقق من صحة البيانات المترابطة"""
        cleaned_data = super().clean()
        follow_up_required = cleaned_data.get('follow_up_required')
        follow_up_date = cleaned_data.get('follow_up_date')

        if follow_up_required and not follow_up_date:
            raise forms.ValidationError({
                'follow_up_date': _('يجب تحديد تاريخ المتابعة عند تفعيل خيار "يتطلب متابعة"')
            })

        return cleaned_data


class EmployeeNoteFilterForm(forms.Form):
    """نموذج تصفية ملاحظات الموظفين"""

    search = forms.CharField(
        label=_('البحث'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ابحث في العنوان أو المحتوى...'
        })
    )

    note_type = forms.ChoiceField(
        label=_('نوع الملاحظة'),
        choices=[('', _('جميع الأنواع'))] + EmployeeNote.NOTE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    priority = forms.ChoiceField(
        label=_('الأولوية'),
        choices=[('', _('جميع الأولويات'))] + EmployeeNote.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    is_important = forms.BooleanField(
        label=_('الملاحظات المهمة فقط'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    is_confidential = forms.BooleanField(
        label=_('الملاحظات السرية فقط'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    follow_up_required = forms.BooleanField(
        label=_('تتطلب متابعة'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    date_from = forms.DateField(
        label=_('من تاريخ'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        label=_('إلى تاريخ'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    created_by = forms.ModelChoiceField(
        label=_('تم الإنشاء بواسطة'),
        queryset=None,  # سيتم تعيينه في __init__
        required=False,
        empty_label=_('جميع المستخدمين'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def __init__(self, *args, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        super().__init__(*args, **kwargs)

        # تعيين queryset للمستخدمين الذين أنشأوا ملاحظات
        self.fields['created_by'].queryset = User.objects.filter(
            created_employee_notes__isnull=False
        ).distinct().order_by('first_name', 'last_name')


class EmployeeNoteReportForm(forms.Form):
    """نموذج تقارير ملاحظات الموظفين"""

    REPORT_TYPE_CHOICES = [
        ('employee_summary', _('ملخص حسب الموظف')),
        ('department_summary', _('ملخص حسب القسم')),
        ('type_summary', _('ملخص حسب النوع')),
        ('date_range', _('ملخص حسب الفترة الزمنية')),
        ('performance_trends', _('اتجاهات الأداء')),
    ]

    report_type = forms.ChoiceField(
        label=_('نوع التقرير'),
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg'
        })
    )

    date_from = forms.DateField(
        label=_('من تاريخ'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        label=_('إلى تاريخ'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    department = forms.ModelChoiceField(
        label=_('القسم'),
        queryset=Department.objects.all(),
        required=False,
        empty_label=_('جميع الأقسام'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    employee = forms.ModelChoiceField(
        label=_('الموظف'),
        queryset=Employee.objects.all(),
        required=False,
        empty_label=_('جميع الموظفين'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    include_confidential = forms.BooleanField(
        label=_('تضمين الملاحظات السرية'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    export_format = forms.ChoiceField(
        label=_('تنسيق التصدير'),
        choices=[
            ('pdf', 'PDF'),
            ('excel', 'Excel'),
            ('csv', 'CSV'),
        ],
        initial='pdf',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
