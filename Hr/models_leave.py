# =============================================================================
# Leave Management Models - نماذج إدارة الإجازات
# =============================================================================

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid
from datetime import date, timedelta


# =============================================================================
# LEAVE TYPE MODEL
# =============================================================================
class LeaveType(models.Model):
    """نموذج أنواع الإجازات"""
    
    LEAVE_CATEGORY_CHOICES = [
        ('annual', _('إجازة سنوية')),
        ('sick', _('إجازة مرضية')),
        ('maternity', _('إجازة أمومة')),
        ('paternity', _('إجازة أبوة')),
        ('emergency', _('إجازة طارئة')),
        ('study', _('إجازة دراسية')),
        ('pilgrimage', _('إجازة حج')),
        ('unpaid', _('إجازة بدون راتب')),
        ('compensatory', _('إجازة تعويضية')),
        ('other', _('أخرى')),
    ]
    
    ACCRUAL_METHOD_CHOICES = [
        ('monthly', _('شهرياً')),
        ('yearly', _('سنوياً')),
        ('fixed', _('ثابت')),
        ('none', _('لا يوجد')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='leave_types', verbose_name=_('الشركة'))
    
    # Basic Information
    name = models.CharField(max_length=100, verbose_name=_('اسم نوع الإجازة'))
    name_english = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    code = models.CharField(max_length=20, verbose_name=_('كود نوع الإجازة'))
    category = models.CharField(max_length=20, choices=LEAVE_CATEGORY_CHOICES, verbose_name=_('فئة الإجازة'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    color = models.CharField(max_length=7, default='#007bff', verbose_name=_('لون العرض'))
    
    # Leave Rules
    default_days = models.PositiveIntegerField(default=0, verbose_name=_('الأيام الافتراضية'))
    max_days_per_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('الحد الأقصى سنوياً'))
    max_consecutive_days = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('الحد الأقصى متتالي'))
    min_notice_days = models.PositiveIntegerField(default=0, verbose_name=_('الحد الأدنى للإشعار المسبق'))
    
    # Accrual Settings
    accrual_method = models.CharField(max_length=20, choices=ACCRUAL_METHOD_CHOICES, default='yearly', verbose_name=_('طريقة الاستحقاق'))
    accrual_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_('معدل الاستحقاق'))
    
    # Carryover Settings
    allow_carryover = models.BooleanField(default=False, verbose_name=_('السماح بالترحيل'))
    max_carryover_days = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('الحد الأقصى للترحيل'))
    carryover_expiry_months = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('انتهاء الترحيل (شهور)'))
    
    # Approval Settings
    requires_approval = models.BooleanField(default=True, verbose_name=_('يتطلب موافقة'))
    approval_levels = models.PositiveIntegerField(default=1, verbose_name=_('مستويات الموافقة'))
    auto_approve_days = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('الموافقة التلقائية للأيام'))
    
    # Calculation Settings
    exclude_weekends = models.BooleanField(default=True, verbose_name=_('استبعاد عطل نهاية الأسبوع'))
    exclude_holidays = models.BooleanField(default=True, verbose_name=_('استبعاد العطل الرسمية'))
    is_paid = models.BooleanField(default=True, verbose_name=_('مدفوعة الأجر'))
    
    # Gender and Employment Type Restrictions
    gender_restriction = models.CharField(
        max_length=10, 
        choices=[('male', _('ذكور فقط')), ('female', _('إناث فقط')), ('all', _('الجميع'))],
        default='all',
        verbose_name=_('قيود الجنس')
    )
    employment_type_restriction = models.CharField(
        max_length=20,
        choices=[('permanent', _('دائم فقط')), ('contract', _('تعاقد فقط')), ('all', _('الجميع'))],
        default='all',
        verbose_name=_('قيود نوع التوظيف')
    )
    
    # Service Requirements
    min_service_months = models.PositiveIntegerField(default=0, verbose_name=_('الحد الأدنى لشهور الخدمة'))
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    effective_from = models.DateField(default=timezone.now, verbose_name=_('ساري من'))
    effective_to = models.DateField(blank=True, null=True, verbose_name=_('ساري حتى'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('نوع الإجازة')
        verbose_name_plural = _('أنواع الإجازات')
        unique_together = ['company', 'code']
        ordering = ['company', 'name']
        indexes = [
            models.Index(fields=['company', 'code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"
    
    @property
    def is_gender_eligible(self, employee):
        """هل الموظف مؤهل حسب الجنس"""
        if self.gender_restriction == 'all':
            return True
        return self.gender_restriction == employee.gender
    
    @property
    def is_employment_type_eligible(self, employee):
        """هل الموظف مؤهل حسب نوع التوظيف"""
        if self.employment_type_restriction == 'all':
            return True
        return self.employment_type_restriction == employee.employment_type
    
    def is_employee_eligible(self, employee):
        """هل الموظف مؤهل لهذا النوع من الإجازة"""
        # Check gender restriction
        if not self.is_gender_eligible(employee):
            return False, "غير مؤهل حسب الجنس"
        
        # Check employment type restriction
        if not self.is_employment_type_eligible(employee):
            return False, "غير مؤهل حسب نوع التوظيف"
        
        # Check service months
        if self.min_service_months > 0:
            service_months = employee.service_months
            if service_months < self.min_service_months:
                return False, f"يتطلب {self.min_service_months} شهر خدمة على الأقل"
        
        return True, "مؤهل"


# =============================================================================
# LEAVE BALANCE MODEL
# =============================================================================
class LeaveBalance(models.Model):
    """نموذج رصيد الإجازات"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='leave_balances', verbose_name=_('الموظف'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='balances', verbose_name=_('نوع الإجازة'))
    year = models.PositiveIntegerField(verbose_name=_('السنة'))
    
    # Balance Information
    allocated_days = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_('الأيام المخصصة'))
    used_days = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_('الأيام المستخدمة'))
    remaining_days = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_('الأيام المتبقية'))
    
    # Carryover Information
    carried_over_days = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_('الأيام المرحلة'))
    carryover_expiry_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الترحيل'))
    
    # Accrual Information
    accrued_days = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_('الأيام المستحقة'))
    last_accrual_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ آخر استحقاق'))
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('رصيد الإجازة')
        verbose_name_plural = _('أرصدة الإجازات')
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['employee', 'leave_type', '-year']
        indexes = [
            models.Index(fields=['employee', 'year']),
            models.Index(fields=['leave_type', 'year']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} - {self.year}"
    
    @property
    def available_days(self):
        """الأيام المتاحة (المتبقية - المعلقة)"""
        pending_days = self.employee.leave_requests.filter(
            leave_type=self.leave_type,
            status='pending',
            start_date__year=self.year
        ).aggregate(total=models.Sum('days_requested'))['total'] or 0
        
        return self.remaining_days - pending_days
    
    @property
    def utilization_percentage(self):
        """نسبة الاستخدام"""
        if self.allocated_days > 0:
            return (self.used_days / self.allocated_days) * 100
        return 0
    
    def calculate_accrual(self):
        """حساب الاستحقاق"""
        if self.leave_type.accrual_method == 'none':
            return 0
        
        today = date.today()
        if self.last_accrual_date and self.last_accrual_date >= today:
            return 0
        
        if self.leave_type.accrual_method == 'monthly':
            # Calculate monthly accrual
            months_since_last = self._months_between(self.last_accrual_date or date(self.year, 1, 1), today)
            accrual = months_since_last * self.leave_type.accrual_rate
        elif self.leave_type.accrual_method == 'yearly':
            # Yearly accrual at the beginning of the year
            if not self.last_accrual_date and today.year == self.year:
                accrual = self.leave_type.accrual_rate
            else:
                accrual = 0
        else:
            accrual = 0
        
        return accrual
    
    def apply_accrual(self, days):
        """تطبيق الاستحقاق"""
        self.accrued_days += days
        self.remaining_days += days
        self.last_accrual_date = date.today()
        self.save()
    
    def _months_between(self, start_date, end_date):
        """حساب الشهور بين تاريخين"""
        return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month


# =============================================================================
# LEAVE REQUEST MODEL
# =============================================================================
class LeaveRequest(models.Model):
    """نموذج طلب الإجازة"""
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('pending', _('معلق')),
        ('approved', _('معتمد')),
        ('rejected', _('مرفوض')),
        ('cancelled', _('ملغي')),
        ('expired', _('منتهي الصلاحية')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('normal', _('عادية')),
        ('high', _('عالية')),
        ('urgent', _('عاجلة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='leave_requests', verbose_name=_('الموظف'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='requests', verbose_name=_('نوع الإجازة'))
    
    # Request Information
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    days_requested = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_('الأيام المطلوبة'))
    reason = models.TextField(blank=True, null=True, verbose_name=_('السبب'))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name=_('الأولوية'))
    
    # Contact Information
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('هاتف الاتصال'))
    contact_address = models.TextField(blank=True, null=True, verbose_name=_('عنوان الاتصال'))
    emergency_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('جهة الاتصال الطارئة'))
    
    # Status and Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))
    current_approval_level = models.PositiveIntegerField(default=1, verbose_name=_('مستوى الموافقة الحالي'))
    
    # Request Timestamps
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الطلب'))
    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التقديم'))
    
    # Approval Information
    approved_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leave_requests', verbose_name=_('معتمد بواسطة'))
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الاعتماد'))
    approved_days = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name=_('الأيام المعتمدة'))
    approval_comments = models.TextField(blank=True, null=True, verbose_name=_('تعليقات الاعتماد'))
    
    # Rejection Information
    rejected_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_leave_requests', verbose_name=_('مرفوض بواسطة'))
    rejected_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الرفض'))
    rejection_reason = models.TextField(blank=True, null=True, verbose_name=_('سبب الرفض'))
    
    # Cancellation Information
    cancelled_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_leave_requests', verbose_name=_('ملغي بواسطة'))
    cancelled_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الإلغاء'))
    cancellation_reason = models.TextField(blank=True, null=True, verbose_name=_('سبب الإلغاء'))
    
    # Return Information
    actual_return_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ العودة الفعلي'))
    return_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات العودة'))
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('طلب الإجازة')
        verbose_name_plural = _('طلبات الإجازات')
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['leave_type', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status', 'requested_at']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} - {self.start_date} to {self.end_date}"
    
    @property
    def duration_days(self):
        """مدة الإجازة بالأيام"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def is_current(self):
        """هل الإجازة جارية حالياً"""
        today = date.today()
        return self.status == 'approved' and self.start_date <= today <= self.end_date
    
    @property
    def is_future(self):
        """هل الإجازة في المستقبل"""
        return self.start_date > date.today()
    
    @property
    def is_past(self):
        """هل الإجازة في الماضي"""
        return self.end_date < date.today()
    
    @property
    def days_until_start(self):
        """الأيام المتبقية حتى بداية الإجازة"""
        if self.is_future:
            return (self.start_date - date.today()).days
        return 0
    
    @property
    def can_be_cancelled(self):
        """هل يمكن إلغاء الطلب"""
        return self.status in ['pending', 'approved'] and self.is_future
    
    def clean(self):
        """التحقق من صحة البيانات"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
            
            if self.start_date < date.today() and self.status == 'draft':
                raise ValidationError("لا يمكن طلب إجازة في الماضي")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


# =============================================================================
# LEAVE BALANCE TRANSACTION MODEL
# =============================================================================
class LeaveBalanceTransaction(models.Model):
    """نموذج معاملات رصيد الإجازة"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('allocation', _('تخصيص')),
        ('accrual', _('استحقاق')),
        ('deduction', _('خصم')),
        ('adjustment', _('تعديل')),
        ('carryover', _('ترحيل')),
        ('expiry', _('انتهاء صلاحية')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    balance = models.ForeignKey(LeaveBalance, on_delete=models.CASCADE, related_name='transactions', verbose_name=_('الرصيد'))
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='balance_transactions', verbose_name=_('طلب الإجازة'))
    
    # Transaction Information
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, verbose_name=_('نوع المعاملة'))
    days = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_('الأيام'))
    description = models.TextField(verbose_name=_('الوصف'))
    
    # Balance Snapshots
    balance_before = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_('الرصيد قبل'))
    balance_after = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_('الرصيد بعد'))
    
    # System Information
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('أنشئ بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    
    class Meta:
        verbose_name = _('معاملة رصيد الإجازة')
        verbose_name_plural = _('معاملات أرصدة الإجازات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['balance', 'transaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.balance} - {self.get_transaction_type_display()} - {self.days} days"


# =============================================================================
# LEAVE APPROVAL WORKFLOW MODEL
# =============================================================================
class LeaveApprovalWorkflow(models.Model):
    """نموذج سير عمل الموافقة على الإجازات"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='approval_workflow', verbose_name=_('طلب الإجازة'))
    
    # Approval Level Information
    level = models.PositiveIntegerField(verbose_name=_('المستوى'))
    approver = models.ForeignKey('accounts.Users_Login_New', on_delete=models.CASCADE, related_name='leave_approvals', verbose_name=_('المعتمد'))
    
    # Status and Timestamps
    status = models.CharField(
        max_length=20,
        choices=[('pending', _('معلق')), ('approved', _('معتمد')), ('rejected', _('مرفوض'))],
        default='pending',
        verbose_name=_('الحالة')
    )
    comments = models.TextField(blank=True, null=True, verbose_name=_('التعليقات'))
    action_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الإجراء'))
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('سير عمل الموافقة على الإجازة')
        verbose_name_plural = _('سير عمل الموافقات على الإجازات')
        unique_together = ['leave_request', 'level']
        ordering = ['leave_request', 'level']
        indexes = [
            models.Index(fields=['leave_request', 'level']),
            models.Index(fields=['approver', 'status']),
        ]
    
    def __str__(self):
        return f"{self.leave_request} - Level {self.level} - {self.approver.username}"


# =============================================================================
# HOLIDAY MODEL
# =============================================================================
class Holiday(models.Model):
    """نموذج العطل الرسمية"""
    
    HOLIDAY_TYPE_CHOICES = [
        ('national', _('عطلة وطنية')),
        ('religious', _('عطلة دينية')),
        ('company', _('عطلة الشركة')),
        ('regional', _('عطلة إقليمية')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='holidays', verbose_name=_('الشركة'))
    
    # Holiday Information
    name = models.CharField(max_length=100, verbose_name=_('اسم العطلة'))
    name_english = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPE_CHOICES, verbose_name=_('نوع العطلة'))
    date = models.DateField(verbose_name=_('التاريخ'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    
    # Settings
    is_paid = models.BooleanField(default=True, verbose_name=_('مدفوعة الأجر'))
    is_recurring = models.BooleanField(default=False, verbose_name=_('متكررة سنوياً'))
    applies_to_all = models.BooleanField(default=True, verbose_name=_('تطبق على الجميع'))
    
    # Restrictions
    departments = models.ManyToManyField('Department', blank=True, related_name='holidays', verbose_name=_('الأقسام'))
    branches = models.ManyToManyField('Branch', blank=True, related_name='holidays', verbose_name=_('الفروع'))
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('عطلة رسمية')
        verbose_name_plural = _('العطل الرسمية')
        unique_together = ['company', 'date', 'name']
        ordering = ['date']
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['holiday_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    @property
    def is_today(self):
        """هل العطلة اليوم"""
        return self.date == date.today()
    
    @property
    def is_upcoming(self):
        """هل العطلة قادمة"""
        return self.date > date.today()
    
    def applies_to_employee(self, employee):
        """هل تطبق العطلة على الموظف"""
        if self.applies_to_all:
            return True
        
        if self.departments.exists() and employee.department not in self.departments.all():
            return False
        
        if self.branches.exists() and employee.branch not in self.branches.all():
            return False
        
        return True