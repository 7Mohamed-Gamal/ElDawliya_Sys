from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from .models import HealthInsuranceProvider, EmployeeHealthInsurance, EmployeeSocialInsurance
from apps.hr.employees.models import Employee


class HealthInsuranceProviderForm(forms.ModelForm):
    """نموذج إضافة وتعديل مزودي التأمين الصحي"""

    class Meta:
        """Meta class"""
        model = HealthInsuranceProvider
        fields = ['provider_name', 'contact_no']

        widgets = {
            'provider_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم مزود التأمين الصحي'
            }),
            'contact_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الاتصال'
            })
        }

        labels = {
            'provider_name': 'اسم مزود التأمين',
            'contact_no': 'رقم الاتصال'
        }

    def clean_provider_name(self):
        """التحقق من اسم المزود"""
        provider_name = self.cleaned_data.get('provider_name')
        if provider_name:
            # التحقق من عدم تكرار الاسم
            existing = HealthInsuranceProvider.objects.filter(provider_name=provider_name)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError('اسم مزود التأمين موجود مسبقاً.')

        return provider_name


class EmployeeHealthInsuranceForm(forms.ModelForm):
    """نموذج إضافة وتعديل التأمين الصحي للموظفين"""

    class Meta:
        """Meta class"""
        model = EmployeeHealthInsurance
        fields = ['emp', 'provider', 'policy_no', 'start_date', 'end_date', 'premium', 'dependents']

        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-select'
            }),
            'provider': forms.Select(attrs={
                'class': 'form-select'
            }),
            'policy_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم البوليصة'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'premium': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'قسط التأمين الشهري',
                'step': '0.01',
                'min': '0'
            }),
            'dependents': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد المعالين',
                'min': '0'
            })
        }

        labels = {
            'emp': 'الموظف',
            'provider': 'مزود التأمين',
            'policy_no': 'رقم البوليصة',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية',
            'premium': 'قسط التأمين الشهري',
            'dependents': 'عدد المعالين'
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # تخصيص خيارات القوائم المنسدلة
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')

        self.fields['provider'].queryset = HealthInsuranceProvider.objects.all().order_by('provider_name')

        # إضافة خيارات فارغة
        self.fields['emp'].empty_label = "اختر الموظف"
        self.fields['provider'].empty_label = "اختر مزود التأمين"

    def clean_start_date(self):
        """التحقق من تاريخ البداية"""
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            # للتأمينات الجديدة، التحقق من أن التاريخ ليس في الماضي البعيد
            if not self.instance.pk and start_date < date.today() - timedelta(days=365):
                raise ValidationError('تاريخ البداية قديم جداً.')
        return start_date

    def clean_end_date(self):
        """التحقق من تاريخ النهاية"""
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        if end_date and start_date:
            if end_date <= start_date:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

            # التحقق من أن مدة التأمين معقولة
            duration = (end_date - start_date).days
            if duration < 30:
                raise ValidationError('مدة التأمين يجب أن تكون شهر على الأقل.')
            if duration > 1095:  # 3 سنوات
                raise ValidationError('مدة التأمين لا يمكن أن تزيد عن 3 سنوات.')

        return end_date

    def clean_premium(self):
        """التحقق من قسط التأمين"""
        premium = self.cleaned_data.get('premium')
        if premium is not None:
            if premium < 0:
                raise ValidationError('قسط التأمين لا يمكن أن يكون سالباً.')
            if premium > 99999.99:
                raise ValidationError('قسط التأمين كبير جداً.')
        return premium

    def clean_dependents(self):
        """التحقق من عدد المعالين"""
        dependents = self.cleaned_data.get('dependents')
        if dependents is not None:
            if dependents < 0:
                raise ValidationError('عدد المعالين لا يمكن أن يكون سالباً.')
            if dependents > 20:
                raise ValidationError('عدد المعالين كبير جداً.')
        return dependents

    def clean(self):
        """التحقق الشامل من البيانات"""
        cleaned_data = super().clean()
        emp = cleaned_data.get('emp')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if emp and start_date and end_date:
            # التحقق من عدم تداخل فترات التأمين للموظف نفسه
            overlapping_insurance = EmployeeHealthInsurance.objects.filter(
                emp=emp,
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exclude(pk=self.instance.pk if self.instance.pk else None)

            if overlapping_insurance.exists():
                insurance = overlapping_insurance.first()
                raise ValidationError(
                    f'يوجد تداخل مع تأمين آخر للموظف من {insurance.start_date} إلى {insurance.end_date}.'
                )

        return cleaned_data


class EmployeeSocialInsuranceForm(forms.ModelForm):
    """نموذج إضافة وتعديل التأمين الاجتماعي للموظفين"""

    class Meta:
        """Meta class"""
        model = EmployeeSocialInsurance
        fields = ['emp', 'gosi_no', 'start_date', 'end_date', 'contribution']

        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-select'
            }),
            'gosi_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم GOSI'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'contribution': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مساهمة GOSI الشهرية',
                'step': '0.01',
                'min': '0'
            })
        }

        labels = {
            'emp': 'الموظف',
            'gosi_no': 'رقم GOSI',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية',
            'contribution': 'المساهمة الشهرية'
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # تخصيص خيارات الموظفين
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')

        # إضافة خيار فارغ
        self.fields['emp'].empty_label = "اختر الموظف"

    def clean_gosi_no(self):
        """التحقق من رقم GOSI"""
        gosi_no = self.cleaned_data.get('gosi_no')
        if gosi_no:
            # التحقق من عدم تكرار رقم GOSI
            existing = EmployeeSocialInsurance.objects.filter(gosi_no=gosi_no)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError('رقم GOSI موجود مسبقاً.')

        return gosi_no

    def clean_start_date(self):
        """التحقق من تاريخ البداية"""
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            # للتأمينات الجديدة، التحقق من أن التاريخ ليس في الماضي البعيد
            if not self.instance.pk and start_date < date.today() - timedelta(days=365):
                raise ValidationError('تاريخ البداية قديم جداً.')
        return start_date

    def clean_end_date(self):
        """التحقق من تاريخ النهاية"""
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        if end_date and start_date:
            if end_date <= start_date:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

        return end_date

    def clean_contribution(self):
        """التحقق من المساهمة"""
        contribution = self.cleaned_data.get('contribution')
        if contribution is not None:
            if contribution < 0:
                raise ValidationError('المساهمة لا يمكن أن تكون سالبة.')
            if contribution > 99999.99:
                raise ValidationError('المساهمة كبيرة جداً.')
        return contribution

    def clean(self):
        """التحقق الشامل من البيانات"""
        cleaned_data = super().clean()
        emp = cleaned_data.get('emp')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if emp and start_date:
            # التحقق من عدم وجود تأمين اجتماعي نشط آخر للموظف
            active_insurance = EmployeeSocialInsurance.objects.filter(
                emp=emp,
                start_date__lte=start_date if start_date else date.today()
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=start_date if start_date else date.today())
            ).exclude(pk=self.instance.pk if self.instance.pk else None)

            if active_insurance.exists():
                raise ValidationError(
                    f'يوجد تأمين اجتماعي نشط للموظف {emp.first_name} {emp.last_name} مسبقاً.'
                )

        return cleaned_data


class InsuranceSearchForm(forms.Form):
    """نموذج البحث في التأمينات"""

    search = forms.CharField(
        label='البحث',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم الموظف أو رقم البوليصة أو رقم GOSI'
        })
    )

    provider = forms.ModelChoiceField(
        label='مزود التأمين',
        queryset=HealthInsuranceProvider.objects.all().order_by('provider_name'),
        required=False,
        empty_label='جميع المزودين',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    status = forms.ChoiceField(
        label='الحالة',
        choices=[
            ('', 'جميع الحالات'),
            ('active', 'نشط'),
            ('expired', 'منتهي الصلاحية'),
            ('expiring_soon', 'ينتهي قريباً')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        label='من تاريخ',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        label='إلى تاريخ',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        """التحقق من صحة فترة البحث"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

        return cleaned_data


class BulkInsuranceRenewalForm(forms.Form):
    """نموذج تجديد التأمينات بالجملة"""

    insurance_ids = forms.CharField(
        widget=forms.HiddenInput()
    )

    renewal_months = forms.IntegerField(
        label='مدة التجديد (بالأشهر)',
        initial=12,
        min_value=1,
        max_value=36,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )

    new_premium = forms.DecimalField(
        label='قسط التأمين الجديد (اختياري)',
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'اتركه فارغاً للاحتفاظ بالقسط الحالي',
            'step': '0.01'
        })
    )

    start_immediately = forms.BooleanField(
        label='بدء التجديد فوراً',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_insurance_ids(self):
        """التحقق من معرفات التأمينات"""
        insurance_ids = self.cleaned_data.get('insurance_ids')
        if insurance_ids:
            try:
                ids = [int(id.strip()) for id in insurance_ids.split(',') if id.strip()]
                if not ids:
                    raise ValidationError('يجب تحديد تأمين واحد على الأقل.')
                return ids
            except ValueError:
                raise ValidationError('معرفات التأمينات غير صحيحة.')
        else:
            raise ValidationError('يجب تحديد تأمين واحد على الأقل.')


class InsuranceReportForm(forms.Form):
    """نموذج تقارير التأمينات"""

    REPORT_TYPES = [
        ('summary', 'تقرير ملخص'),
        ('detailed', 'تقرير مفصل'),
        ('expiry', 'تقرير انتهاء الصلاحية'),
        ('cost_analysis', 'تحليل التكلفة')
    ]

    report_type = forms.ChoiceField(
        label='نوع التقرير',
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    insurance_type = forms.ChoiceField(
        label='نوع التأمين',
        choices=[
            ('all', 'جميع الأنواع'),
            ('health', 'تأمين صحي'),
            ('social', 'تأمين اجتماعي')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    provider = forms.ModelChoiceField(
        label='مزود التأمين',
        queryset=HealthInsuranceProvider.objects.all().order_by('provider_name'),
        required=False,
        empty_label='جميع المزودين',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        label='من تاريخ',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        label='إلى تاريخ',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # تعيين التواريخ الافتراضية
        today = date.today()
        self.fields['date_from'].initial = today.replace(month=1, day=1)  # بداية السنة
        self.fields['date_to'].initial = today

    def clean(self):
        """التحقق من صحة فترة التقرير"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

            # التحقق من أن الفترة ليست طويلة جداً
            if (date_to - date_from).days > 1095:  # 3 سنوات
                raise ValidationError('فترة التقرير لا يمكن أن تزيد عن 3 سنوات.')

        return cleaned_data


class InsuranceExpiryAlertForm(forms.Form):
    """نموذج تنبيهات انتهاء صلاحية التأمين"""

    ALERT_PERIODS = [
        (7, 'خلال أسبوع'),
        (30, 'خلال شهر'),
        (60, 'خلال شهرين'),
        (90, 'خلال 3 أشهر')
    ]

    alert_period = forms.ChoiceField(
        label='فترة التنبيه',
        choices=ALERT_PERIODS,
        initial=30,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    provider = forms.ModelChoiceField(
        label='مزود التأمين',
        queryset=HealthInsuranceProvider.objects.all().order_by('provider_name'),
        required=False,
        empty_label='جميع المزودين',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    send_email = forms.BooleanField(
        label='إرسال تنبيه بالبريد الإلكتروني',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    include_expired = forms.BooleanField(
        label='تضمين التأمينات المنتهية الصلاحية',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
