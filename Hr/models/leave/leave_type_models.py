"""
Leave Type Models for HRMS
Handles different types of leaves and their configurations
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class LeaveType(models.Model):
    """
    Leave Type model for defining different types of leaves
    Includes leave policies, accrual rules, and approval requirements
    """
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم نوع الإجازة")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود نوع الإجازة")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف نوع الإجازة")
    )
    
    # Leave Category
    LEAVE_CATEGORIES = [
        ('annual', _('إجازة سنوية')),
        ('sick', _('إجازة مرضية')),
        ('maternity', _('إجازة أمومة')),
        ('paternity', _('إجازة أبوة')),
        ('emergency', _('إجازة طارئة')),
        ('bereavement', _('إجازة وفاة')),
        ('study', _('إجازة دراسية')),
        ('pilgrimage', _('إجازة حج/عمرة')),
        ('marriage', _('إجازة زواج')),
        ('unpaid', _('إجازة بدون راتب')),
        ('compensatory', _('إجازة تعويضية')),
        ('sabbatical', _('إجازة تفرغ')),
        ('military', _('إجازة خدمة عسكرية')),
        ('other', _('أخرى')),
    ]
    
    category = models.CharField(
        max_length=20,
        choices=LEAVE_CATEGORIES,
        verbose_name=_("فئة الإجازة")
    )
    
    # Leave Entitlement
    max_days_per_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للأيام سنوياً"),
        help_text=_("الحد الأقصى لأيام الإجازة في السنة")
    )
    
    max_days_per_request = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للأيام في الطلب الواحد")
    )
    
    min_days_per_request = models.PositiveIntegerField(
        default=1,
        verbose_name=_("الحد الأدنى للأيام في الطلب الواحد")
    )
    
    # Accrual Settings
    ACCRUAL_METHODS = [
        ('annual', _('سنوي')),
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('weekly', _('أسبوعي')),
        ('none', _('لا يوجد استحقاق')),
    ]
    
    accrual_method = models.CharField(
        max_length=20,
        choices=ACCRUAL_METHODS,
        default='annual',
        verbose_name=_("طريقة الاستحقاق")
    )
    
    accrual_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("معدل الاستحقاق"),
        help_text=_("عدد الأيام المستحقة حسب طريقة الاستحقاق")
    )
    
    # Carry Forward Rules
    carry_forward_allowed = models.BooleanField(
        default=False,
        verbose_name=_("يسمح بترحيل الرصيد"),
        help_text=_("هل يمكن ترحيل الرصيد للسنة التالية؟")
    )
    
    max_carry_forward_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى لأيام الترحيل")
    )
    
    carry_forward_expiry_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("انتهاء صلاحية الرصيد المرحل (شهور)")
    )
    
    # Approval Requirements
    requires_approval = models.BooleanField(
        default=True,
        verbose_name=_("يتطلب موافقة")
    )
    
    approval_levels = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("مستويات الموافقة")
    )
    
    auto_approve_threshold = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("حد الموافقة التلقائية (أيام)"),
        help_text=_("الطلبات أقل من هذا العدد تتم الموافقة عليها تلقائياً")
    )
    
    # Notice Period
    minimum_notice_days = models.PositiveIntegerField(
        default=1,
        verbose_name=_("الحد الأدنى لفترة الإشعار (أيام)")
    )
    
    maximum_advance_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للحجز المسبق (أيام)")
    )
    
    # Payment Settings
    is_paid = models.BooleanField(
        default=True,
        verbose_name=_("إجازة مدفوعة الأجر")
    )
    
    payment_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("نسبة الدفع (%)"),
        help_text=_("نسبة الراتب المدفوع أثناء الإجازة")
    )
    
    # Gender and Eligibility
    GENDER_ELIGIBILITY = [
        ('all', _('الجميع')),
        ('male', _('ذكور فقط')),
        ('female', _('إناث فقط')),
    ]
    
    gender_eligibility = models.CharField(
        max_length=10,
        choices=GENDER_ELIGIBILITY,
        default='all',
        verbose_name=_("الأهلية حسب الجنس")
    )
    
    minimum_service_months = models.PositiveIntegerField(
        default=0,
        verbose_name=_("الحد الأدنى لشهور الخدمة")
    )
    
    # Documentation Requirements
    requires_medical_certificate = models.BooleanField(
        default=False,
        verbose_name=_("يتطلب شهادة طبية")
    )
    
    medical_certificate_threshold = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("حد الشهادة الطبية (أيام)"),
        help_text=_("عدد الأيام التي تتطلب شهادة طبية")
    )
    
    requires_supporting_documents = models.BooleanField(
        default=False,
        verbose_name=_("يتطلب مستندات داعمة")
    )
    
    # Calendar and Scheduling
    exclude_weekends = models.BooleanField(
        default=True,
        verbose_name=_("استبعاد عطلات نهاية الأسبوع")
    )
    
    exclude_holidays = models.BooleanField(
        default=True,
        verbose_name=_("استبعاد العطل الرسمية")
    )
    
    can_be_split = models.BooleanField(
        default=True,
        verbose_name=_("يمكن تقسيمها"),
        help_text=_("هل يمكن أخذ هذه الإجازة على فترات منفصلة؟")
    )
    
    # Restrictions
    blackout_periods = models.JSONField(
        default=list,
        verbose_name=_("فترات المنع"),
        help_text=_("فترات لا يمكن أخذ إجازة فيها")
    )
    
    max_concurrent_employees = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للموظفين في نفس الوقت")
    )
    
    # Leave Settings
    leave_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات الإجازة"),
        help_text=_("إعدادات إضافية خاصة بنوع الإجازة")
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_system_leave = models.BooleanField(
        default=False,
        verbose_name=_("إجازة نظام"),
        help_text=_("هل هذا نوع إجازة أساسي في النظام؟")
    )
    
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("ترتيب العرض")
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_leave_types',
        verbose_name=_("أنشئ بواسطة")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("نوع إجازة")
        verbose_name_plural = _("أنواع الإجازات")
        db_table = 'hrms_leave_type'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate leave type data"""
        super().clean()
        
        # Validate carry forward settings
        if self.carry_forward_allowed and not self.max_carry_forward_days:
            raise ValidationError(_("يجب تحديد الحد الأقصى لأيام الترحيل عند السماح بالترحيل"))
        
        # Validate medical certificate threshold
        if self.requires_medical_certificate and not self.medical_certificate_threshold:
            raise ValidationError(_("يجب تحديد حد الشهادة الطبية عند طلب شهادة طبية"))
        
        # Validate accrual settings
        if self.accrual_method != 'none' and not self.accrual_rate:
            raise ValidationError(_("يجب تحديد معدل الاستحقاق عند اختيار طريقة استحقاق"))
        
        # Validate min/max days
        if (self.min_days_per_request and self.max_days_per_request and 
            self.min_days_per_request > self.max_days_per_request):
            raise ValidationError(_("الحد الأدنى للأيام لا يمكن أن يكون أكبر من الحد الأقصى"))
    
    def is_eligible_for_employee(self, employee):
        """Check if employee is eligible for this leave type"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        # Check gender eligibility
        if self.gender_eligibility != 'all':
            if employee.gender != self.gender_eligibility:
                return False, _("غير مؤهل حسب الجنس")
        
        # Check minimum service period
        if self.minimum_service_months > 0:
            service_date = employee.hire_date + relativedelta(months=self.minimum_service_months)
            if date.today() < service_date:
                return False, _("لم يكمل فترة الخدمة المطلوبة")
        
        return True, _("مؤهل")
    
    def calculate_accrual(self, employee, period_start, period_end):
        """Calculate leave accrual for given period"""
        if self.accrual_method == 'none' or not self.accrual_rate:
            return 0
        
        # Calculate based on accrual method
        if self.accrual_method == 'annual':
            return float(self.accrual_rate)
        elif self.accrual_method == 'monthly':
            months = (period_end.year - period_start.year) * 12 + (period_end.month - period_start.month)
            return float(self.accrual_rate) * months
        elif self.accrual_method == 'quarterly':
            quarters = ((period_end.year - period_start.year) * 4 + 
                       (period_end.month - 1) // 3 - (period_start.month - 1) // 3)
            return float(self.accrual_rate) * quarters
        elif self.accrual_method == 'weekly':
            weeks = (period_end - period_start).days // 7
            return float(self.accrual_rate) * weeks
        
        return 0
    
    def get_available_balance(self, employee, as_of_date=None):
        """Get available leave balance for employee"""
        from datetime import date
        if as_of_date is None:
            as_of_date = date.today()
        
        # This would typically query the LeaveBalance model
        # For now, return a placeholder
        return 0
    
    def save(self, *args, **kwargs):
        """Override save to set default settings"""
        # Set default leave settings
        if not self.leave_settings:
            self.leave_settings = {
                'allow_half_days': True,
                'allow_hour_based': False,
                'require_return_confirmation': False,
                'send_reminder_notifications': True,
                'auto_deduct_from_balance': True,
            }
        
        # Auto-generate code if not provided
        if not self.code:
            leave_count = LeaveType.objects.count()
            self.code = f"LT{leave_count + 1:03d}"
        
        super().save(*args, **kwargs)
