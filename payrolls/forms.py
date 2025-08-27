from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from decimal import Decimal
from .models import EmployeeSalary, PayrollRun, PayrollDetail
from employees.models import Employee
from org.models import Department


class EmployeeSalaryForm(forms.ModelForm):
    """نموذج إضافة وتعديل رواتب الموظفين"""
    
    class Meta:
        model = EmployeeSalary
        fields = [
            'emp', 'basic_salary', 'housing_allow', 'transport_allow', 'other_allow',
            'gosi_deduction', 'tax_deduction', 'currency', 'effective_date',
            'end_date', 'is_current'
        ]
        
        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-select'
            }),
            'basic_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'الراتب الأساسي',
                'step': '0.01',
                'min': '0'
            }),
            'housing_allow': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'بدل السكن',
                'step': '0.01',
                'min': '0'
            }),
            'transport_allow': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'بدل النقل',
                'step': '0.01',
                'min': '0'
            }),
            'other_allow': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'بدلات أخرى',
                'step': '0.01',
                'min': '0'
            }),
            'gosi_deduction': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'استقطاع GOSI',
                'step': '0.01',
                'min': '0'
            }),
            'tax_deduction': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'استقطاع الضريبة',
                'step': '0.01',
                'min': '0'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('SAR', 'ريال سعودي'),
                ('USD', 'دولار أمريكي'),
                ('EUR', 'يورو')
            ]),
            'effective_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_current': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
        labels = {
            'emp': 'الموظف',
            'basic_salary': 'الراتب الأساسي',
            'housing_allow': 'بدل السكن',
            'transport_allow': 'بدل النقل',
            'other_allow': 'بدلات أخرى',
            'gosi_deduction': 'استقطاع GOSI',
            'tax_deduction': 'استقطاع الضريبة',
            'currency': 'العملة',
            'effective_date': 'تاريخ السريان',
            'end_date': 'تاريخ الانتهاء',
            'is_current': 'راتب حالي'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص خيارات الموظفين
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')
        
        # إضافة خيار فارغ
        self.fields['emp'].empty_label = "اختر الموظف"
        
        # تعيين التاريخ الافتراضي
        if not self.instance.pk:
            self.fields['effective_date'].initial = date.today()
            self.fields['currency'].initial = 'SAR'

    def clean_basic_salary(self):
        """التحقق من الراتب الأساسي"""
        basic_salary = self.cleaned_data.get('basic_salary')
        if basic_salary is not None:
            if basic_salary <= 0:
                raise ValidationError('الراتب الأساسي يجب أن يكون أكبر من صفر.')
            if basic_salary > 999999.99:
                raise ValidationError('الراتب الأساسي كبير جداً.')
        return basic_salary

    def clean_effective_date(self):
        """التحقق من تاريخ السريان"""
        effective_date = self.cleaned_data.get('effective_date')
        if effective_date:
            # للرواتب الجديدة، التحقق من أن التاريخ ليس في المستقبل البعيد
            if not self.instance.pk and effective_date > date.today() + timedelta(days=365):
                raise ValidationError('تاريخ السريان بعيد جداً في المستقبل.')
        return effective_date

    def clean_end_date(self):
        """التحقق من تاريخ الانتهاء"""
        end_date = self.cleaned_data.get('end_date')
        effective_date = self.cleaned_data.get('effective_date')
        
        if end_date and effective_date:
            if end_date <= effective_date:
                raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ السريان.')
        
        return end_date

    def clean(self):
        """التحقق الشامل من البيانات"""
        cleaned_data = super().clean()
        emp = cleaned_data.get('emp')
        is_current = cleaned_data.get('is_current')
        effective_date = cleaned_data.get('effective_date')

        if emp and is_current and effective_date:
            # التحقق من عدم وجود راتب حالي آخر للموظف
            existing_current = EmployeeSalary.objects.filter(
                emp=emp,
                is_current=True
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing_current.exists():
                raise ValidationError(
                    f'يوجد راتب حالي للموظف {emp.first_name} {emp.last_name} مسبقاً. '
                    'يجب إنهاء الراتب الحالي أولاً.'
                )

        return cleaned_data


class PayrollRunForm(forms.ModelForm):
    """نموذج إضافة وتعديل تشغيل الرواتب"""
    
    class Meta:
        model = PayrollRun
        fields = ['run_date', 'month_year', 'status']
        
        widgets = {
            'run_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'month_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM',
                'pattern': r'\d{4}-\d{2}'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('Draft', 'مسودة'),
                ('Confirmed', 'مؤكد'),
                ('Paid', 'مدفوع')
            ])
        }
        
        labels = {
            'run_date': 'تاريخ التشغيل',
            'month_year': 'شهر/سنة الراتب',
            'status': 'الحالة'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تعيين القيم الافتراضية
        if not self.instance.pk:
            self.fields['run_date'].initial = date.today()
            self.fields['status'].initial = 'Draft'

    def clean_month_year(self):
        """التحقق من صيغة الشهر/السنة"""
        month_year = self.cleaned_data.get('month_year')
        if month_year:
            try:
                year, month = month_year.split('-')
                year = int(year)
                month = int(month)
                
                if year < 2020 or year > 2030:
                    raise ValidationError('السنة يجب أن تكون بين 2020 و 2030.')
                
                if month < 1 or month > 12:
                    raise ValidationError('الشهر يجب أن يكون بين 1 و 12.')
                
            except (ValueError, AttributeError):
                raise ValidationError('صيغة الشهر/السنة غير صحيحة. استخدم YYYY-MM.')
        
        return month_year

    def clean(self):
        """التحقق الشامل من البيانات"""
        cleaned_data = super().clean()
        month_year = cleaned_data.get('month_year')

        if month_year:
            # التحقق من عدم وجود تشغيل آخر لنفس الشهر
            existing_run = PayrollRun.objects.filter(
                month_year=month_year
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing_run.exists():
                raise ValidationError(
                    f'يوجد تشغيل رواتب لشهر {month_year} مسبقاً.'
                )

        return cleaned_data


class PayrollDetailForm(forms.ModelForm):
    """نموذج تفاصيل الراتب"""
    
    class Meta:
        model = PayrollDetail
        fields = [
            'run', 'emp', 'basic_salary', 'housing_allowance', 'transport_allowance', 'overtime_amount',
            'gosi_deduction', 'tax_deduction', 'loan_deduction', 'net_salary', 'paid_date'
        ]
        
        widgets = {
            'run': forms.Select(attrs={
                'class': 'form-select'
            }),
            'emp': forms.Select(attrs={
                'class': 'form-select'
            }),
            'basic_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'housing_allowance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'transport_allowance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'overtime_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'gosi_deduction': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tax_deduction': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'loan_deduction': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'net_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'readonly': True
            }),
            'paid_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص خيارات القوائم المنسدلة
        self.fields['run'].queryset = PayrollRun.objects.all().order_by('-run_date')
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')

    def clean(self):
        """حساب الراتب الصافي تلقائياً"""
        cleaned_data = super().clean()
        
        basic_salary = cleaned_data.get('basic_salary') or Decimal('0')
        housing_allowance = cleaned_data.get('housing_allowance') or Decimal('0')
        transport_allowance = cleaned_data.get('transport_allowance') or Decimal('0')
        overtime_amount = cleaned_data.get('overtime_amount') or Decimal('0')
        gosi_deduction = cleaned_data.get('gosi_deduction') or Decimal('0')
        tax_deduction = cleaned_data.get('tax_deduction') or Decimal('0')
        loan_deduction = cleaned_data.get('loan_deduction') or Decimal('0')
        
        # حساب الراتب الصافي
        net_salary = basic_salary + housing_allowance + transport_allowance + overtime_amount - gosi_deduction - tax_deduction - loan_deduction
        cleaned_data['net_salary'] = net_salary
        
        return cleaned_data


class PayrollSearchForm(forms.Form):
    """نموذج البحث في الرواتب"""
    
    search = forms.CharField(
        label='البحث',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم الموظف أو كود الموظف'
        })
    )
    
    department = forms.ModelChoiceField(
        label='القسم',
        queryset=Department.objects.filter(is_active=True).order_by('dept_name'),
        required=False,
        empty_label='جميع الأقسام',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    salary_range = forms.ChoiceField(
        label='نطاق الراتب',
        choices=[
            ('', 'جميع النطاقات'),
            ('high', 'عالي (15000+)'),
            ('medium_high', 'متوسط عالي (10000-14999)'),
            ('medium', 'متوسط (5000-9999)'),
            ('low', 'منخفض (3000-4999)'),
            ('very_low', 'منخفض جداً (أقل من 3000)')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    currency = forms.ChoiceField(
        label='العملة',
        choices=[
            ('', 'جميع العملات'),
            ('SAR', 'ريال سعودي'),
            ('USD', 'دولار أمريكي'),
            ('EUR', 'يورو')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class BulkSalaryUpdateForm(forms.Form):
    """نموذج التحديث الجماعي للرواتب"""
    
    UPDATE_TYPES = [
        ('percentage', 'زيادة نسبة مئوية'),
        ('fixed_amount', 'زيادة مبلغ ثابت'),
        ('new_allowance', 'إضافة بدل جديد')
    ]
    
    update_type = forms.ChoiceField(
        label='نوع التحديث',
        choices=UPDATE_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    department = forms.ModelChoiceField(
        label='القسم',
        queryset=Department.objects.filter(is_active=True).order_by('dept_name'),
        required=False,
        empty_label='جميع الأقسام',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    employees = forms.ModelMultipleChoiceField(
        label='الموظفين',
        queryset=Employee.objects.filter(emp_status='Active').order_by('first_name', 'last_name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    percentage = forms.DecimalField(
        label='النسبة المئوية',
        required=False,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 10.5',
            'step': '0.01'
        })
    )
    
    fixed_amount = forms.DecimalField(
        label='المبلغ الثابت',
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 500.00',
            'step': '0.01'
        })
    )
    
    allowance_type = forms.ChoiceField(
        label='نوع البدل',
        choices=[
            ('housing', 'بدل السكن'),
            ('transport', 'بدل النقل'),
            ('other', 'بدلات أخرى')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    effective_date = forms.DateField(
        label='تاريخ السريان',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['effective_date'].initial = date.today()

    def clean(self):
        """التحقق من صحة البيانات"""
        cleaned_data = super().clean()
        update_type = cleaned_data.get('update_type')
        percentage = cleaned_data.get('percentage')
        fixed_amount = cleaned_data.get('fixed_amount')
        allowance_type = cleaned_data.get('allowance_type')
        
        if update_type == 'percentage' and not percentage:
            raise ValidationError('يجب تحديد النسبة المئوية.')
        
        if update_type == 'fixed_amount' and not fixed_amount:
            raise ValidationError('يجب تحديد المبلغ الثابت.')
        
        if update_type == 'new_allowance' and (not fixed_amount or not allowance_type):
            raise ValidationError('يجب تحديد نوع البدل والمبلغ.')
        
        return cleaned_data


class PayrollReportForm(forms.Form):
    """نموذج تقارير الرواتب"""
    
    REPORT_TYPES = [
        ('summary', 'تقرير ملخص'),
        ('detailed', 'تقرير مفصل'),
        ('department_comparison', 'مقارنة الأقسام'),
        ('salary_analysis', 'تحليل الرواتب')
    ]
    
    report_type = forms.ChoiceField(
        label='نوع التقرير',
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    month_year = forms.CharField(
        label='شهر/سنة',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'YYYY-MM',
            'pattern': r'\d{4}-\d{2}'
        })
    )
    
    department = forms.ModelChoiceField(
        label='القسم',
        queryset=Department.objects.filter(is_active=True).order_by('dept_name'),
        required=False,
        empty_label='جميع الأقسام',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    currency = forms.ChoiceField(
        label='العملة',
        choices=[
            ('', 'جميع العملات'),
            ('SAR', 'ريال سعودي'),
            ('USD', 'دولار أمريكي'),
            ('EUR', 'يورو')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تعيين الشهر الحالي كافتراضي
        self.fields['month_year'].initial = date.today().strftime('%Y-%m')

    def clean_month_year(self):
        """التحقق من صيغة الشهر/السنة"""
        month_year = self.cleaned_data.get('month_year')
        if month_year:
            try:
                year, month = month_year.split('-')
                year = int(year)
                month = int(month)
                
                if year < 2020 or year > 2030:
                    raise ValidationError('السنة يجب أن تكون بين 2020 و 2030.')
                
                if month < 1 or month > 12:
                    raise ValidationError('الشهر يجب أن يكون بين 1 و 12.')
                
            except (ValueError, AttributeError):
                raise ValidationError('صيغة الشهر/السنة غير صحيحة. استخدم YYYY-MM.')
        
        return month_year