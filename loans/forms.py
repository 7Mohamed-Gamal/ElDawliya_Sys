"""
نماذج (Forms) نظام القروض والسلف
Loans Management Forms
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from decimal import Decimal
from .models import LoanType, EmployeeLoan, LoanInstallment
from employees.models import Employee


class LoanTypeForm(forms.ModelForm):
    """نموذج إضافة/تعديل نوع قرض"""
    
    class Meta:
        model = LoanType
        fields = ['type_name', 'max_amount', 'max_installments', 'interest_rate']
        widgets = {
            'type_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم نوع القرض',
                'required': True
            }),
            'max_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'الحد الأقصى للمبلغ',
                'step': '0.01',
                'min': '0'
            }),
            'max_installments': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'الحد الأقصى لعدد الأقساط',
                'min': '1'
            }),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'نسبة الفائدة (%)',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
        }
        labels = {
            'type_name': 'اسم نوع القرض',
            'max_amount': 'الحد الأقصى للمبلغ',
            'max_installments': 'الحد الأقصى لعدد الأقساط',
            'interest_rate': 'نسبة الفائدة (%)',
        }

    def clean_type_name(self):
        type_name = self.cleaned_data.get('type_name')
        if type_name and len(type_name) < 3:
            raise ValidationError('اسم نوع القرض يجب أن يكون 3 أحرف على الأقل')
        
        # Check for duplicate type name
        qs = LoanType.objects.filter(type_name=type_name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('نوع القرض بهذا الاسم موجود بالفعل')
        
        return type_name

    def clean_max_amount(self):
        max_amount = self.cleaned_data.get('max_amount')
        if max_amount and max_amount <= 0:
            raise ValidationError('الحد الأقصى للمبلغ يجب أن يكون أكبر من صفر')
        if max_amount and max_amount > 1000000:
            raise ValidationError('الحد الأقصى للمبلغ يبدو غير منطقي')
        return max_amount

    def clean_max_installments(self):
        max_installments = self.cleaned_data.get('max_installments')
        if max_installments and max_installments <= 0:
            raise ValidationError('عدد الأقساط يجب أن يكون أكبر من صفر')
        if max_installments and max_installments > 120:
            raise ValidationError('عدد الأقساط يبدو كبيراً جداً (الحد الأقصى 120 قسط)')
        return max_installments

    def clean_interest_rate(self):
        interest_rate = self.cleaned_data.get('interest_rate')
        if interest_rate and interest_rate < 0:
            raise ValidationError('نسبة الفائدة لا يمكن أن تكون سالبة')
        if interest_rate and interest_rate > 50:
            raise ValidationError('نسبة الفائدة تبدو مرتفعة جداً')
        return interest_rate


class EmployeeLoanForm(forms.ModelForm):
    """نموذج إضافة/تعديل قرض موظف"""
    
    STATUS_CHOICES = [
        ('Pending', 'في الانتظار'),
        ('Active', 'نشط'),
        ('Completed', 'مكتمل'),
        ('Rejected', 'مرفوض'),
        ('Cancelled', 'ملغي'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الحالة'
    )
    
    class Meta:
        model = EmployeeLoan
        fields = [
            'emp', 'loan_type', 'request_amount', 'approved_amount',
            'installment_amt', 'start_date', 'end_date', 'status'
        ]
        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'loan_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'request_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'المبلغ المطلوب',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'approved_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'المبلغ المعتمد',
                'step': '0.01',
                'min': '0'
            }),
            'installment_amt': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'قيمة القسط الشهري',
                'step': '0.01',
                'min': '0'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'emp': 'الموظف',
            'loan_type': 'نوع القرض',
            'request_amount': 'المبلغ المطلوب',
            'approved_amount': 'المبلغ المعتمد',
            'installment_amt': 'قيمة القسط الشهري',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ الانتهاء',
            'status': 'الحالة',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Improve employee dropdown display
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')
        self.fields['emp'].label_from_instance = lambda obj: f"{obj.emp_code} - {obj.first_name} {obj.last_name}"
        
        # Improve loan type dropdown display
        self.fields['loan_type'].queryset = LoanType.objects.all().order_by('type_name')
        
        # Set default values for new loans
        if not self.instance.pk:
            self.fields['status'].initial = 'Pending'
            self.fields['start_date'].initial = date.today()

    def clean(self):
        cleaned_data = super().clean()
        emp = cleaned_data.get('emp')
        loan_type = cleaned_data.get('loan_type')
        request_amount = cleaned_data.get('request_amount')
        approved_amount = cleaned_data.get('approved_amount')
        installment_amt = cleaned_data.get('installment_amt')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        status = cleaned_data.get('status')
        
        # Validate employee has no active loans exceeding limit
        if emp:
            active_loans_count = EmployeeLoan.objects.filter(
                emp=emp,
                status='Active'
            ).exclude(pk=self.instance.pk if self.instance.pk else None).count()
            
            if active_loans_count >= 3:
                raise ValidationError('الموظف لديه 3 قروض نشطة بالفعل (الحد الأقصى)')
        
        # Validate against loan type limits
        if loan_type and request_amount:
            if loan_type.max_amount and request_amount > loan_type.max_amount:
                raise ValidationError(
                    f'المبلغ المطلوب يتجاوز الحد الأقصى لنوع القرض ({loan_type.max_amount})'
                )
        
        # Validate approved amount doesn't exceed requested amount
        if request_amount and approved_amount:
            if approved_amount > request_amount:
                raise ValidationError('المبلغ المعتمد لا يمكن أن يتجاوز المبلغ المطلوب')
        
        # Validate installment amount
        if approved_amount and installment_amt:
            if installment_amt > approved_amount:
                raise ValidationError('قيمة القسط لا يمكن أن تتجاوز المبلغ المعتمد')
            
            # Calculate number of installments
            installment_count = int(approved_amount / installment_amt)
            if loan_type and loan_type.max_installments:
                if installment_count > loan_type.max_installments:
                    raise ValidationError(
                        f'عدد الأقساط ({installment_count}) يتجاوز الحد الأقصى لنوع القرض ({loan_type.max_installments})'
                    )
        
        # Validate dates
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية')
            
            # Calculate expected duration based on installments
            if approved_amount and installment_amt:
                installment_count = int(approved_amount / installment_amt)
                expected_end_date = start_date + timedelta(days=30 * installment_count)
                
                # Allow some flexibility (±30 days)
                if abs((end_date - expected_end_date).days) > 30:
                    self.add_error('end_date', 
                        f'تاريخ الانتهاء المتوقع بناءً على عدد الأقساط هو {expected_end_date.strftime("%Y-%m-%d")}'
                    )
        
        # Require approved amount for active loans
        if status == 'Active' and not approved_amount:
            raise ValidationError('يجب تحديد المبلغ المعتمد للقروض النشطة')
        
        # Require installment amount for active loans
        if status == 'Active' and not installment_amt:
            raise ValidationError('يجب تحديد قيمة القسط للقروض النشطة')
        
        return cleaned_data


class LoanInstallmentForm(forms.ModelForm):
    """نموذج إضافة/تعديل قسط قرض"""
    
    STATUS_CHOICES = [
        ('Pending', 'معلق'),
        ('Paid', 'مدفوع'),
        ('Overdue', 'متأخر'),
        ('Waived', 'معفى'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الحالة'
    )
    
    class Meta:
        model = LoanInstallment
        fields = ['loan', 'due_date', 'paid_date', 'amount', 'penalty', 'status']
        widgets = {
            'loan': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'paid_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'قيمة القسط',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'penalty': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'غرامة التأخير',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'loan': 'القرض',
            'due_date': 'تاريخ الاستحقاق',
            'paid_date': 'تاريخ الدفع',
            'amount': 'قيمة القسط',
            'penalty': 'غرامة التأخير',
            'status': 'الحالة',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Improve loan dropdown display
        self.fields['loan'].queryset = EmployeeLoan.objects.select_related(
            'emp', 'loan_type'
        ).filter(status='Active').order_by('-start_date')
        self.fields['loan'].label_from_instance = lambda obj: (
            f"{obj.emp.first_name} {obj.emp.last_name} - "
            f"{obj.loan_type.type_name if obj.loan_type else 'قرض'} - "
            f"{obj.approved_amount}"
        )

    def clean(self):
        cleaned_data = super().clean()
        loan = cleaned_data.get('loan')
        due_date = cleaned_data.get('due_date')
        paid_date = cleaned_data.get('paid_date')
        amount = cleaned_data.get('amount')
        status = cleaned_data.get('status')
        
        # Validate due date is after loan start date
        if loan and due_date:
            if loan.start_date and due_date < loan.start_date:
                raise ValidationError('تاريخ استحقاق القسط يجب أن يكون بعد تاريخ بداية القرض')
            
            if loan.end_date and due_date > loan.end_date:
                raise ValidationError('تاريخ استحقاق القسط يجب أن يكون قبل تاريخ انتهاء القرض')
        
        # Validate paid date
        if paid_date:
            if due_date and paid_date < due_date:
                self.add_error('paid_date', 'تاريخ الدفع قبل تاريخ الاستحقاق')
            
            if paid_date > date.today():
                raise ValidationError('تاريخ الدفع لا يمكن أن يكون في المستقبل')
        
        # Require paid date for paid status
        if status == 'Paid' and not paid_date:
            raise ValidationError('يجب تحديد تاريخ الدفع للأقساط المدفوعة')
        
        # Don't allow paid date for non-paid status
        if status in ['Pending', 'Overdue'] and paid_date:
            self.add_error('paid_date', 'لا يمكن تحديد تاريخ دفع للأقساط غير المدفوعة')
        
        # Validate amount doesn't exceed loan installment amount
        if loan and amount:
            if loan.installment_amt and amount > loan.installment_amt * Decimal('1.5'):
                self.add_error('amount', 
                    f'قيمة القسط تبدو كبيرة جداً مقارنة بقيمة القسط المحددة ({loan.installment_amt})'
                )
        
        return cleaned_data

