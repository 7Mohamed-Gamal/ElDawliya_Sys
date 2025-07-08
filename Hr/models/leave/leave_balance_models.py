"""
Leave Balance Models for HRMS
Handles leave balance tracking, accruals, and transactions
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal


class LeaveBalance(models.Model):
    """
    Leave Balance model for tracking employee leave balances
    Maintains current balance, accruals, and usage for each leave type
    """
    
    # Employee and Leave Type
    employee = models.ForeignKey(
        'employee.Employee',
        on_delete=models.CASCADE,
        related_name='leave_balances',
        verbose_name=_("الموظف")
    )
    
    leave_type = models.ForeignKey(
        'LeaveType',
        on_delete=models.CASCADE,
        related_name='employee_balances',
        verbose_name=_("نوع الإجازة")
    )
    
    # Balance Period
    balance_year = models.PositiveIntegerField(
        verbose_name=_("سنة الرصيد")
    )
    
    period_start_date = models.DateField(
        verbose_name=_("تاريخ بداية الفترة")
    )
    
    period_end_date = models.DateField(
        verbose_name=_("تاريخ نهاية الفترة")
    )
    
    # Balance Information
    opening_balance = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("الرصيد الافتتاحي")
    )
    
    accrued_balance = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("الرصيد المستحق")
    )
    
    used_balance = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("الرصيد المستخدم")
    )
    
    pending_balance = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("الرصيد المعلق"),
        help_text=_("الرصيد المحجوز للطلبات المعلقة")
    )
    
    carried_forward_balance = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("الرصيد المرحل")
    )
    
    adjustment_balance = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("تعديل الرصيد")
    )
    
    encashed_balance = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("الرصيد المصروف")
    )
    
    # Calculated Fields
    current_balance = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("الرصيد الحالي")
    )
    
    available_balance = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("الرصيد المتاح")
    )
    
    # Carry Forward Information
    carry_forward_from_previous = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name=_("مرحل من السنة السابقة")
    )
    
    carry_forward_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء الرصيد المرحل")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_frozen = models.BooleanField(
        default=False,
        verbose_name=_("مجمد"),
        help_text=_("هل الرصيد مجمد ولا يمكن استخدامه؟")
    )
    
    freeze_reason = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("سبب التجميد")
    )
    
    # Last Update Information
    last_accrual_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ آخر استحقاق")
    )
    
    last_calculation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ آخر حساب")
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("رصيد إجازة")
        verbose_name_plural = _("أرصدة الإجازات")
        db_table = 'hrms_leave_balance'
        unique_together = [['employee', 'leave_type', 'balance_year']]
        ordering = ['employee', 'leave_type', '-balance_year']
        indexes = [
            models.Index(fields=['employee', 'leave_type']),
            models.Index(fields=['balance_year']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.balance_year})"
    
    def clean(self):
        """Validate leave balance data"""
        super().clean()
        
        # Validate period dates
        if self.period_start_date and self.period_end_date:
            if self.period_start_date > self.period_end_date:
                raise ValidationError(_("تاريخ بداية الفترة لا يمكن أن يكون بعد تاريخ النهاية"))
    
    @property
    def total_entitlement(self):
        """Calculate total entitlement for the period"""
        return (self.opening_balance + self.accrued_balance + 
                self.carried_forward_balance + self.adjustment_balance)
    
    @property
    def total_deductions(self):
        """Calculate total deductions"""
        return self.used_balance + self.encashed_balance
    
    def calculate_current_balance(self):
        """Calculate current balance"""
        return self.total_entitlement - self.total_deductions
    
    def calculate_available_balance(self):
        """Calculate available balance (current - pending)"""
        return self.calculate_current_balance() - self.pending_balance
    
    def can_request_leave(self, days_requested):
        """Check if employee can request specified days"""
        if self.is_frozen:
            return False, _("الرصيد مجمد")
        
        if not self.is_active:
            return False, _("الرصيد غير نشط")
        
        available = self.calculate_available_balance()
        if days_requested > available:
            return False, _("الرصيد المتاح غير كافي")
        
        return True, _("يمكن طلب الإجازة")
    
    def reserve_balance(self, days_to_reserve, reason=""):
        """Reserve balance for pending leave request"""
        available = self.calculate_available_balance()
        if days_to_reserve > available:
            raise ValidationError(_("لا يمكن حجز أكثر من الرصيد المتاح"))
        
        self.pending_balance += Decimal(str(days_to_reserve))
        self.save()
        
        # Create transaction record
        LeaveTransaction.objects.create(
            leave_balance=self,
            transaction_type='reserve',
            amount=days_to_reserve,
            description=reason or _("حجز رصيد لطلب إجازة"),
            balance_after_transaction=self.calculate_available_balance()
        )
    
    def release_reserved_balance(self, days_to_release, reason=""):
        """Release reserved balance"""
        if days_to_release > self.pending_balance:
            raise ValidationError(_("لا يمكن إلغاء حجز أكثر من الرصيد المحجوز"))
        
        self.pending_balance -= Decimal(str(days_to_release))
        self.save()
        
        # Create transaction record
        LeaveTransaction.objects.create(
            leave_balance=self,
            transaction_type='release',
            amount=days_to_release,
            description=reason or _("إلغاء حجز رصيد"),
            balance_after_transaction=self.calculate_available_balance()
        )
    
    def deduct_balance(self, days_to_deduct, reason=""):
        """Deduct balance for taken leave"""
        # First release from pending if exists
        if self.pending_balance >= days_to_deduct:
            self.pending_balance -= Decimal(str(days_to_deduct))
        else:
            remaining = days_to_deduct - float(self.pending_balance)
            self.pending_balance = 0
            
            # Check if enough balance available
            available = self.calculate_available_balance()
            if remaining > available:
                raise ValidationError(_("الرصيد المتاح غير كافي"))
        
        self.used_balance += Decimal(str(days_to_deduct))
        self.save()
        
        # Create transaction record
        LeaveTransaction.objects.create(
            leave_balance=self,
            transaction_type='deduct',
            amount=days_to_deduct,
            description=reason or _("خصم رصيد لإجازة مأخوذة"),
            balance_after_transaction=self.calculate_current_balance()
        )
    
    def add_accrual(self, days_to_add, reason=""):
        """Add accrued leave"""
        self.accrued_balance += Decimal(str(days_to_add))
        self.last_accrual_date = date.today()
        self.save()
        
        # Create transaction record
        LeaveTransaction.objects.create(
            leave_balance=self,
            transaction_type='accrual',
            amount=days_to_add,
            description=reason or _("استحقاق إجازة"),
            balance_after_transaction=self.calculate_current_balance()
        )
    
    def adjust_balance(self, adjustment_amount, reason):
        """Adjust balance (positive or negative)"""
        self.adjustment_balance += Decimal(str(adjustment_amount))
        self.save()
        
        # Create transaction record
        LeaveTransaction.objects.create(
            leave_balance=self,
            transaction_type='adjustment',
            amount=adjustment_amount,
            description=reason,
            balance_after_transaction=self.calculate_current_balance()
        )
    
    def encash_balance(self, days_to_encash, reason=""):
        """Encash leave balance"""
        available = self.calculate_available_balance()
        if days_to_encash > available:
            raise ValidationError(_("لا يمكن صرف أكثر من الرصيد المتاح"))
        
        self.encashed_balance += Decimal(str(days_to_encash))
        self.save()
        
        # Create transaction record
        LeaveTransaction.objects.create(
            leave_balance=self,
            transaction_type='encashment',
            amount=days_to_encash,
            description=reason or _("صرف رصيد إجازة"),
            balance_after_transaction=self.calculate_current_balance()
        )
    
    def freeze_balance(self, reason):
        """Freeze the balance"""
        self.is_frozen = True
        self.freeze_reason = reason
        self.save()
    
    def unfreeze_balance(self):
        """Unfreeze the balance"""
        self.is_frozen = False
        self.freeze_reason = None
        self.save()
    
    def recalculate_balance(self):
        """Recalculate all balance fields"""
        self.current_balance = self.calculate_current_balance()
        self.available_balance = self.calculate_available_balance()
        self.last_calculation_date = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate balances"""
        self.current_balance = self.calculate_current_balance()
        self.available_balance = self.calculate_available_balance()
        self.last_calculation_date = timezone.now()
        super().save(*args, **kwargs)


class LeaveTransaction(models.Model):
    """
    Leave Transaction model for tracking all balance changes
    Provides audit trail for leave balance modifications
    """
    
    leave_balance = models.ForeignKey(
        LeaveBalance,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_("رصيد الإجازة")
    )
    
    TRANSACTION_TYPES = [
        ('accrual', _('استحقاق')),
        ('deduct', _('خصم')),
        ('adjustment', _('تعديل')),
        ('carry_forward', _('ترحيل')),
        ('encashment', _('صرف')),
        ('reserve', _('حجز')),
        ('release', _('إلغاء حجز')),
        ('opening', _('رصيد افتتاحي')),
        ('expiry', _('انتهاء صلاحية')),
    ]
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        verbose_name=_("نوع المعاملة")
    )
    
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        verbose_name=_("المبلغ")
    )
    
    description = models.CharField(
        max_length=500,
        verbose_name=_("الوصف")
    )
    
    reference_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("رقم المرجع"),
        help_text=_("رقم مرجعي للمعاملة (مثل رقم طلب الإجازة)")
    )
    
    balance_before_transaction = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name=_("الرصيد قبل المعاملة")
    )
    
    balance_after_transaction = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        verbose_name=_("الرصيد بعد المعاملة")
    )
    
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_transactions',
        verbose_name=_("تم بواسطة")
    )
    
    processed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ المعاملة")
    )
    
    class Meta:
        verbose_name = _("معاملة رصيد إجازة")
        verbose_name_plural = _("معاملات أرصدة الإجازات")
        db_table = 'hrms_leave_transaction'
        ordering = ['-processed_at']
        indexes = [
            models.Index(fields=['leave_balance', 'processed_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['reference_id']),
        ]
    
    def __str__(self):
        return f"{self.leave_balance} - {self.get_transaction_type_display()} - {self.amount}"
