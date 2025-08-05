"""
نماذج تأمينات الموظفين - النسخة المحسنة
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from datetime import date, timedelta
from decimal import Decimal


class EmployeeInsuranceEnhanced(models.Model):
    """نموذج تأمينات الموظف المحسن"""
    
    INSURANCE_TYPE_CHOICES = [
        ('social', _('تأمين اجتماعي')),
        ('medical', _('تأمين صحي')),
        ('life', _('تأمين على الحياة')),
        ('disability', _('تأمين ضد العجز')),
        ('unemployment', _('تأمين ضد البطالة')),
        ('professional', _('تأمين مهني')),
        ('travel', _('تأمين سفر')),
        ('dental', _('تأمين أسنان')),
        ('vision', _('تأمين نظر')),
        ('maternity', _('تأمين أمومة')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('suspended', _('موقوف')),
        ('expired', _('منتهي')),
        ('cancelled', _('ملغى')),
        ('pending', _('في الانتظار')),
    ]
    
    COVERAGE_TYPE_CHOICES = [
        ('individual', _('فردي')),
        ('family', _('عائلي')),
        ('spouse', _('الزوج/الزوجة')),
        ('children', _('الأطفال')),
        ('parents', _('الوالدين')),
    ]
    
    PAYMENT_FREQUENCY_CHOICES = [
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('semi_annual', _('نصف سنوي')),
        ('annual', _('سنوي')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced', 
        on_delete=models.CASCADE, 
        related_name='insurance_records_enhanced', 
        verbose_name=_('الموظف')
    )
    
    # Insurance Details
    insurance_type = models.CharField(
        max_length=20, 
        choices=INSURANCE_TYPE_CHOICES, 
        verbose_name=_('نوع التأمين')
    )
    
    policy_number = models.CharField(
        max_length=100, 
        verbose_name=_('رقم البوليصة'),
        unique=True
    )
    
    provider = models.CharField(
        max_length=200, 
        verbose_name=_('مقدم التأمين')
    )
    
    provider_contact = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name=_('جهة الاتصال')
    )
    
    provider_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('هاتف مقدم التأمين')
    )
    
    provider_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('بريد مقدم التأمين')
    )
    
    # Coverage Details
    coverage_type = models.CharField(
        max_length=20,
        choices=COVERAGE_TYPE_CHOICES,
        default='individual',
        verbose_name=_('نوع التغطية')
    )
    
    coverage_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف التغطية')
    )
    
    # Dates
    start_date = models.DateField(
        verbose_name=_('تاريخ البداية')
    )
    
    end_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('تاريخ النهاية')
    )
    
    renewal_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('تاريخ التجديد')
    )
    
    last_renewal_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ آخر تجديد')
    )
    
    # Financial Information
    premium_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('قسط التأمين'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    coverage_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name=_('مبلغ التغطية'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    employee_contribution = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name=_('مساهمة الموظف'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    employer_contribution = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name=_('مساهمة صاحب العمل'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    deductible = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name=_('المبلغ المقتطع'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCY_CHOICES,
        default='monthly',
        verbose_name=_('تكرار الدفع')
    )
    
    currency = models.CharField(
        max_length=10,
        default='SAR',
        verbose_name=_('العملة')
    )
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active', 
        verbose_name=_('الحالة')
    )
    
    # Beneficiaries
    beneficiaries = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_('المستفيدون')
    )
    
    # Family Members Covered
    spouse_covered = models.BooleanField(
        default=False,
        verbose_name=_('يشمل الزوج/الزوجة')
    )
    
    children_covered = models.PositiveIntegerField(
        default=0,
        verbose_name=_('عدد الأطفال المشمولين'),
        validators=[MaxValueValidator(20)]
    )
    
    parents_covered = models.BooleanField(
        default=False,
        verbose_name=_('يشمل الوالدين')
    )
    
    # Claims Information
    total_claims_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('إجمالي المطالبات'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    claims_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('عدد المطالبات')
    )
    
    last_claim_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ آخر مطالبة')
    )
    
    # Files
    policy_document = models.FileField(
        upload_to='insurance/policies/', 
        blank=True, 
        null=True, 
        verbose_name=_('وثيقة التأمين')
    )
    
    terms_document = models.FileField(
        upload_to='insurance/terms/',
        blank=True,
        null=True,
        verbose_name=_('شروط وأحكام التأمين')
    )
    
    # Additional Information
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_('ملاحظات')
    )
    
    special_conditions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('شروط خاصة')
    )
    
    # Approval Information
    approved_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_insurance_records',
        verbose_name=_('تم الاعتماد بواسطة')
    )
    
    approval_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ الاعتماد')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('تاريخ الإنشاء')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('تاريخ التحديث')
    )
    
    created_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='created_insurance_records',
        verbose_name=_('تم الإنشاء بواسطة')
    )

    class Meta:
        verbose_name = _('تأمين موظف محسن')
        verbose_name_plural = _('تأمينات الموظفين المحسنة')
        ordering = ['employee', 'insurance_type', '-start_date']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['insurance_type']),
            models.Index(fields=['policy_number']),
            models.Index(fields=['status']),
            models.Index(fields=['end_date']),
            models.Index(fields=['renewal_date']),
            models.Index(fields=['provider']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='end_after_start_insurance'
            ),
            models.CheckConstraint(
                check=models.Q(employee_contribution__lte=models.F('premium_amount')),
                name='employee_contribution_valid'
            ),
            models.CheckConstraint(
                check=models.Q(employer_contribution__lte=models.F('premium_amount')),
                name='employer_contribution_valid'
            ),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_insurance_type_display()} - {self.policy_number}"

    @property
    def is_active_insurance(self):
        """هل التأمين نشط"""
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < timezone.now().date():
            return False
        return True

    @property
    def days_until_expiry(self):
        """عدد الأيام حتى انتهاء التأمين"""
        if not self.end_date:
            return None
        return (self.end_date - timezone.now().date()).days
    
    @property
    def days_until_renewal(self):
        """عدد الأيام حتى التجديد"""
        if not self.renewal_date:
            return None
        return (self.renewal_date - timezone.now().date()).days

    @property
    def is_expiring_soon(self, warning_days=30):
        """هل ينتهي التأمين قريباً"""
        days_left = self.days_until_expiry
        return days_left is not None and 0 <= days_left <= warning_days
    
    @property
    def needs_renewal_soon(self, warning_days=60):
        """هل يحتاج للتجديد قريباً"""
        days_left = self.days_until_renewal
        return days_left is not None and 0 <= days_left <= warning_days
    
    @property
    def total_family_members_covered(self):
        """إجمالي أفراد العائلة المشمولين"""
        total = 1  # الموظف نفسه
        if self.spouse_covered:
            total += 1
        total += self.children_covered
        if self.parents_covered:
            total += 2  # الأب والأم
        return total
    
    @property
    def monthly_premium(self):
        """القسط الشهري"""
        if self.payment_frequency == 'monthly':
            return self.premium_amount
        elif self.payment_frequency == 'quarterly':
            return self.premium_amount / 3
        elif self.payment_frequency == 'semi_annual':
            return self.premium_amount / 6
        elif self.payment_frequency == 'annual':
            return self.premium_amount / 12
        return self.premium_amount
    
    @property
    def annual_premium(self):
        """القسط السنوي"""
        if self.payment_frequency == 'monthly':
            return self.premium_amount * 12
        elif self.payment_frequency == 'quarterly':
            return self.premium_amount * 4
        elif self.payment_frequency == 'semi_annual':
            return self.premium_amount * 2
        elif self.payment_frequency == 'annual':
            return self.premium_amount
        return self.premium_amount * 12
    
    @property
    def coverage_utilization_rate(self):
        """معدل استخدام التغطية"""
        if self.coverage_amount == 0:
            return 0
        return (self.total_claims_amount / self.coverage_amount) * 100
    
    @property
    def is_high_utilization(self):
        """هل معدل الاستخدام مرتفع"""
        return self.coverage_utilization_rate > 50
    
    @property
    def insurance_duration_years(self):
        """مدة التأمين بالسنوات"""
        if not self.end_date:
            return None
        return (self.end_date - self.start_date).days / 365.25

    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}
        
        if self.end_date and self.start_date > self.end_date:
            errors['end_date'] = _('تاريخ النهاية لا يمكن أن يكون قبل تاريخ البداية')
        
        if self.renewal_date and self.renewal_date <= self.start_date:
            errors['renewal_date'] = _('تاريخ التجديد يجب أن يكون بعد تاريخ البداية')
        
        # التحقق من مجموع المساهمات
        total_contribution = self.employee_contribution + self.employer_contribution
        if total_contribution > self.premium_amount:
            errors['premium_amount'] = _('مجموع مساهمة الموظف وصاحب العمل لا يمكن أن يتجاوز قسط التأمين')
        
        # التحقق من منطقية مبلغ التغطية
        if self.coverage_amount < self.premium_amount:
            errors['coverage_amount'] = _('مبلغ التغطية يجب أن يكون أكبر من قسط التأمين')
        
        # التحقق من المطالبات
        if self.total_claims_amount > self.coverage_amount:
            errors['total_claims_amount'] = _('إجمالي المطالبات لا يمكن أن يتجاوز مبلغ التغطية')
        
        if errors:
            raise ValidationError(errors)
    
    def calculate_next_payment_date(self):
        """حساب تاريخ الدفعة القادمة"""
        if not self.start_date:
            return None
        
        today = timezone.now().date()
        
        if self.payment_frequency == 'monthly':
            delta = timedelta(days=30)
        elif self.payment_frequency == 'quarterly':
            delta = timedelta(days=90)
        elif self.payment_frequency == 'semi_annual':
            delta = timedelta(days=180)
        elif self.payment_frequency == 'annual':
            delta = timedelta(days=365)
        else:
            delta = timedelta(days=30)
        
        next_payment = self.start_date
        while next_payment <= today:
            next_payment += delta
        
        return next_payment
    
    def add_claim(self, amount, description=None):
        """إضافة مطالبة جديدة"""
        self.total_claims_amount += amount
        self.claims_count += 1
        self.last_claim_date = timezone.now().date()
        self.save()
    
    def renew_insurance(self, new_end_date, new_premium=None):
        """تجديد التأمين"""
        self.last_renewal_date = timezone.now().date()
        self.end_date = new_end_date
        
        if new_premium:
            self.premium_amount = new_premium
        
        # حساب تاريخ التجديد القادم
        if self.payment_frequency == 'annual':
            self.renewal_date = new_end_date
        else:
            self.renewal_date = new_end_date - timedelta(days=30)
        
        self.status = 'active'
        self.save()
    
    def cancel_insurance(self, reason=None):
        """إلغاء التأمين"""
        self.status = 'cancelled'
        if reason:
            self.notes = f"{self.notes or ''}\nتم الإلغاء: {reason}"
        self.save()
    
    def suspend_insurance(self, reason=None):
        """تعليق التأمين"""
        self.status = 'suspended'
        if reason:
            self.notes = f"{self.notes or ''}\nتم التعليق: {reason}"
        self.save()
    
    def reactivate_insurance(self):
        """إعادة تفعيل التأمين"""
        if self.end_date and self.end_date >= timezone.now().date():
            self.status = 'active'
            self.save()
            return True
        return False

    def save(self, *args, **kwargs):
        """تجاوز الحفظ للتحقق من البيانات"""
        # تحديث الحالة تلقائياً بناءً على التاريخ
        if self.end_date and self.end_date < timezone.now().date() and self.status == 'active':
            self.status = 'expired'
        
        self.full_clean()
        super().save(*args, **kwargs)