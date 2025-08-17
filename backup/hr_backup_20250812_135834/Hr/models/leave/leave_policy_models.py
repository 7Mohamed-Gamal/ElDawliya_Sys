"""
Leave Policy Models for HRMS
Handles leave policies and rules for different employee groups
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError


class LeavePolicy(models.Model):
    """
    Leave Policy model for defining leave rules for different employee groups
    Allows customization of leave entitlements based on various criteria
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        verbose_name=_("اسم سياسة الإجازات")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود السياسة")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف السياسة")
    )
    
    # Applicability
    company = models.ForeignKey(
        'Hr.Company',
        on_delete=models.CASCADE,
        related_name='leave_policies',
        null=True,
        blank=True,
        verbose_name=_("الشركة"),
        help_text=_("إذا لم يتم تحديد شركة، ستطبق على جميع الشركات")
    )

    branches = models.ManyToManyField(
        'Hr.Branch',
        blank=True,
        related_name='leave_policies',
        verbose_name=_("الفروع"),
        help_text=_("الفروع التي تطبق عليها هذه السياسة")
    )

    departments = models.ManyToManyField(
        'Hr.Department',
        blank=True,
        related_name='leave_policies',
        verbose_name=_("الأقسام"),
        help_text=_("الأقسام التي تطبق عليها هذه السياسة")
    )

    job_positions = models.ManyToManyField(
        'Hr.JobPosition',
        blank=True,
        related_name='leave_policies',
        verbose_name=_("الوظائف"),
        help_text=_("الوظائف التي تطبق عليها هذه السياسة")
    )
    
    # Employee Criteria
    EMPLOYMENT_TYPES = [
        ('all', _('جميع أنواع التوظيف')),
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('تعاقد')),
        ('temporary', _('مؤقت')),
        ('intern', _('متدرب')),
    ]
    
    employment_types = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPES,
        default='all',
        verbose_name=_("أنواع التوظيف")
    )
    
    GENDER_CRITERIA = [
        ('all', _('الجميع')),
        ('male', _('ذكور فقط')),
        ('female', _('إناث فقط')),
    ]
    
    gender_criteria = models.CharField(
        max_length=10,
        choices=GENDER_CRITERIA,
        default='all',
        verbose_name=_("معايير الجنس")
    )
    
    minimum_service_months = models.PositiveIntegerField(
        default=0,
        verbose_name=_("الحد الأدنى لشهور الخدمة")
    )
    
    maximum_service_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى لشهور الخدمة")
    )
    
    # Policy Rules
    policy_rules = models.JSONField(
        default=dict,
        verbose_name=_("قواعد السياسة"),
        help_text=_("قواعد مخصصة للسياسة")
    )
    
    # Leave Type Entitlements
    leave_entitlements = models.JSONField(
        default=dict,
        verbose_name=_("استحقاقات الإجازات"),
        help_text=_("استحقاقات مخصصة لكل نوع إجازة")
    )
    
    # Approval Workflow
    approval_workflow = models.JSONField(
        default=list,
        verbose_name=_("سير عمل الموافقة"),
        help_text=_("تسلسل الموافقات المطلوبة")
    )
    
    # Calendar Settings
    CALENDAR_YEAR_TYPES = [
        ('calendar', _('سنة ميلادية')),
        ('fiscal', _('سنة مالية')),
        ('hire_date', _('من تاريخ التوظيف')),
        ('custom', _('مخصص')),
    ]
    
    calendar_year_type = models.CharField(
        max_length=20,
        choices=CALENDAR_YEAR_TYPES,
        default='calendar',
        verbose_name=_("نوع السنة")
    )
    
    fiscal_year_start_month = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("شهر بداية السنة المالية"),
        help_text=_("رقم الشهر (1-12)")
    )
    
    # Carry Forward Rules
    global_carry_forward_allowed = models.BooleanField(
        default=False,
        verbose_name=_("السماح بالترحيل العام")
    )
    
    global_max_carry_forward_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("النسبة القصوى للترحيل العام (%)")
    )
    
    # Encashment Rules
    allow_leave_encashment = models.BooleanField(
        default=False,
        verbose_name=_("السماح بصرف الإجازات")
    )
    
    max_encashment_days_per_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى لأيام الصرف سنوياً")
    )
    
    encashment_rate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("نسبة صرف الإجازات (%)")
    )
    
    # Notification Settings
    notification_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات التنبيهات"),
        help_text=_("إعدادات التنبيهات والإشعارات")
    )
    
    # Priority and Status
    priority = models.PositiveIntegerField(
        default=1,
        verbose_name=_("الأولوية"),
        help_text=_("أولوية تطبيق السياسة (الأقل رقماً له الأولوية)")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("افتراضي"),
        help_text=_("هل هذه السياسة الافتراضية؟")
    )
    
    # Effective Dates
    effective_from = models.DateField(
        verbose_name=_("ساري من تاريخ")
    )
    
    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("ساري حتى تاريخ")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_leave_policies',
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
        verbose_name = _("سياسة إجازات")
        verbose_name_plural = _("سياسات الإجازات")
        db_table = 'hrms_leave_policy'
        ordering = ['priority', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['priority']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate leave policy data"""
        super().clean()
        
        # Validate effective dates
        if self.effective_to and self.effective_from > self.effective_to:
            raise ValidationError(_("تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية"))
        
        # Validate service months
        if (self.maximum_service_months and 
            self.minimum_service_months > self.maximum_service_months):
            raise ValidationError(_("الحد الأدنى لشهور الخدمة لا يمكن أن يكون أكبر من الحد الأقصى"))
        
        # Validate fiscal year start month
        if (self.calendar_year_type == 'fiscal' and 
            (not self.fiscal_year_start_month or 
             self.fiscal_year_start_month < 1 or 
             self.fiscal_year_start_month > 12)):
            raise ValidationError(_("شهر بداية السنة المالية يجب أن يكون بين 1 و 12"))
    
    def is_applicable_to_employee(self, employee):
        """Check if this policy applies to the given employee"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        # Check if policy is active and within effective dates
        if not self.is_active:
            return False
        
        today = date.today()
        if today < self.effective_from:
            return False
        
        if self.effective_to and today > self.effective_to:
            return False
        
        # Check company
        if self.company and employee.company != self.company:
            return False
        
        # Check branch
        if self.branches.exists() and employee.branch not in self.branches.all():
            return False
        
        # Check department
        if self.departments.exists() and employee.department not in self.departments.all():
            return False
        
        # Check job position
        if self.job_positions.exists() and employee.job_position not in self.job_positions.all():
            return False
        
        # Check employment type
        if (self.employment_types != 'all' and 
            employee.employment_type != self.employment_types):
            return False
        
        # Check gender
        if (self.gender_criteria != 'all' and 
            employee.gender != self.gender_criteria):
            return False
        
        # Check service period
        service_months = relativedelta(today, employee.hire_date).months
        service_months += relativedelta(today, employee.hire_date).years * 12
        
        if service_months < self.minimum_service_months:
            return False
        
        if (self.maximum_service_months and 
            service_months > self.maximum_service_months):
            return False
        
        return True
    
    def get_leave_entitlement(self, leave_type_code):
        """Get leave entitlement for specific leave type"""
        return self.leave_entitlements.get(leave_type_code, {})
    
    def get_approval_workflow_for_leave(self, leave_type_code, days_requested):
        """Get approval workflow for specific leave request"""
        # Default workflow if none specified
        default_workflow = [
            {'level': 1, 'approver_type': 'manager', 'required': True},
        ]
        
        # Check if there's a specific workflow for this leave type
        workflow = self.approval_workflow
        if isinstance(workflow, dict) and leave_type_code in workflow:
            return workflow[leave_type_code]
        elif isinstance(workflow, list) and workflow:
            return workflow
        
        return default_workflow
    
    def calculate_leave_year_dates(self, employee, reference_date=None):
        """Calculate leave year start and end dates for employee"""
        from datetime import date
        if reference_date is None:
            reference_date = date.today()
        
        if self.calendar_year_type == 'calendar':
            year_start = date(reference_date.year, 1, 1)
            year_end = date(reference_date.year, 12, 31)
        elif self.calendar_year_type == 'fiscal':
            if reference_date.month >= self.fiscal_year_start_month:
                year_start = date(reference_date.year, self.fiscal_year_start_month, 1)
                year_end = date(reference_date.year + 1, self.fiscal_year_start_month - 1, 31)
            else:
                year_start = date(reference_date.year - 1, self.fiscal_year_start_month, 1)
                year_end = date(reference_date.year, self.fiscal_year_start_month - 1, 31)
        elif self.calendar_year_type == 'hire_date':
            hire_anniversary = employee.hire_date.replace(year=reference_date.year)
            if reference_date >= hire_anniversary:
                year_start = hire_anniversary
                year_end = hire_anniversary.replace(year=reference_date.year + 1) - timedelta(days=1)
            else:
                year_start = hire_anniversary.replace(year=reference_date.year - 1)
                year_end = hire_anniversary - timedelta(days=1)
        else:  # custom
            # Default to calendar year for custom
            year_start = date(reference_date.year, 1, 1)
            year_end = date(reference_date.year, 12, 31)
        
        return year_start, year_end
    
    def save(self, *args, **kwargs):
        """Override save to set default settings"""
        # Set default policy rules
        if not self.policy_rules:
            self.policy_rules = {
                'allow_negative_balance': False,
                'require_manager_approval': True,
                'allow_backdated_requests': False,
                'max_backdated_days': 7,
                'allow_future_requests': True,
                'max_future_days': 365,
            }
        
        # Set default notification settings
        if not self.notification_settings:
            self.notification_settings = {
                'notify_manager_on_request': True,
                'notify_hr_on_request': True,
                'notify_employee_on_approval': True,
                'notify_employee_on_rejection': True,
                'reminder_days_before_leave': 1,
            }
        
        # Ensure only one default policy per company
        if self.is_default:
            LeavePolicy.objects.filter(
                company=self.company,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        # Auto-generate code if not provided
        if not self.code:
            policy_count = LeavePolicy.objects.count()
            self.code = f"LP{policy_count + 1:03d}"
        
        super().save(*args, **kwargs)
