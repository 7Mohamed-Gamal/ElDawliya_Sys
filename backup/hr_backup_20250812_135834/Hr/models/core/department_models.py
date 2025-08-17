"""
نماذج الأقسام لنظام إدارة الموارد البشرية (HRMS)
تتعامل مع الهيكل التنظيمي للأقسام والفروع
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date

User = get_user_model()


class Department(models.Model):
    """
    نموذج القسم التنظيمي يمثل وحدة تنظيمية مع دعم الهيكل الهرمي
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Hierarchy Relationship
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("القسم الرئيسي")
    )
    
    # Company/Branch Relationship
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name=_("الشركة")
    )
    
    branch = models.ForeignKey(
        'Branch',
        on_delete=models.CASCADE,
        related_name='departments',
        null=True,
        blank=True,
        verbose_name=_("الفرع")
    )
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        verbose_name=_("اسم القسم"),
        help_text=_("اسم القسم باللغة العربية")
    )
    
    name_english = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("الاسم بالإنجليزية"),
        help_text=_("اسم القسم باللغة الإنجليزية")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود القسم"),
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]{2,20}$',
            message=_('كود القسم يجب أن يحتوي على أحرف إنجليزية كبيرة وأرقام فقط')
        )]
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف القسم")
    )
    
    # Department Type and Level
    department_type = models.CharField(
        max_length=20,
        choices=[
            ('operational', _('تشغيلي')),
            ('administrative', _('إداري')),
            ('technical', _('تقني')),
            ('support', _('دعم')),
            ('management', _('إدارة')),
            ('finance', _('مالي')),
            ('hr', _('موارد بشرية')),
            ('sales', _('مبيعات')),
            ('marketing', _('تسويق')),
            ('production', _('إنتاج')),
        ],
        default='operational',
        verbose_name=_("نوع القسم")
    )
    
    level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_("مستوى القسم"),
        help_text=_("المستوى الهرمي للقسم (1 = أعلى مستوى)")
    )
    
    # Management
    manager = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_("مدير القسم")
    )
    
    assistant_manager = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assistant_managed_departments',
        verbose_name=_("مساعد المدير")
    )
    
    # Operational Information
    cost_center = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("مركز التكلفة")
    )
    
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الميزانية السنوية")
    )
    
    # Capacity and Staffing
    min_employees = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_("الحد الأدنى للموظفين")
    )
    
    max_employees = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(1)],
        verbose_name=_("الحد الأقصى للموظفين")
    )
    
    # Location Information
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("الموقع")
    )
    
    floor = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_("الطابق")
    )
    
    phone_extension = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_("رقم الداخلي")
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("البريد الإلكتروني")
    )
    
    # Department Settings
    department_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات القسم")
    )
    
    # Working Hours
    working_hours_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("بداية ساعات العمل")
    )
    
    working_hours_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("نهاية ساعات العمل")
    )
    
    # Establishment Information
    establishment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التأسيس")
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("ملاحظات")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_departments',
        verbose_name=_('أنشأ بواسطة')
    )
    
    class Meta:
        verbose_name = _("قسم")
        verbose_name_plural = _("الأقسام")
        db_table = 'hrms_department'
        ordering = ['company', 'level', 'name']
        unique_together = ['company', 'code']
        indexes = [
            models.Index(fields=['company', 'branch']),
            models.Index(fields=['parent']),
            models.Index(fields=['department_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['level']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """إرجاع اسم القسم مع الشركة والفرع (إن وجد)"""
        branch_name = f" - {self.branch.name}" if self.branch else ""
        return f"{self.company.name}{branch_name} - {self.name}"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        if self.establishment_date and self.establishment_date > date.today():
            raise ValidationError(_('تاريخ التأسيس لا يمكن أن يكون في المستقبل'))
        
        if self.parent and self.parent.company != self.company:
            raise ValidationError(_('القسم الرئيسي يجب أن يكون من نفس الشركة'))
        
        if self.min_employees > self.max_employees:
            raise ValidationError(_('الحد الأدنى للموظفين لا يمكن أن يكون أكبر من الحد الأقصى'))
        
        if self.working_hours_start and self.working_hours_end:
            if self.working_hours_start >= self.working_hours_end:
                raise ValidationError(_('وقت بداية العمل يجب أن يكون قبل وقت النهاية'))
    
    def save(self, *args, **kwargs):
        """تجاوز الحفظ لتوليد كود القسم وتعيين الإعدادات الافتراضية"""
        if not self.department_settings:
            self.department_settings = {
                'approval_required': True,
                'allow_remote_work': False,
                'default_shift_hours': 8,
                'overtime_allowed': True,
                'flexible_hours': False,
                'break_duration': 60,  # minutes
                'weekend_work': False,
                'holiday_work': False,
            }
        
        # Auto-generate code if not provided
        if not self.code:
            self.code = f"DPT{uuid.uuid4().hex[:6].upper()}"
        
        # Set level based on parent
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1
        
        super().save(*args, **kwargs)
    
    @property
    def employee_count(self):
        """عدد الموظفين في القسم"""
        return self.employees.filter(is_active=True).count()
    
    @property
    def subdepartment_count(self):
        """عدد الأقسام الفرعية"""
        return self.children.filter(is_active=True).count()
    
    @property
    def total_employee_count(self):
        """إجمالي عدد الموظفين في القسم والأقسام الفرعية"""
        count = self.employee_count
        for child in self.children.filter(is_active=True):
            count += child.total_employee_count
        return count
    
    @property
    def hierarchy_path(self):
        """مسار القسم في الهيكل الهرمي"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)
    
    @property
    def is_over_capacity(self):
        """هل القسم يتجاوز الحد الأقصى للموظفين"""
        return self.employee_count > self.max_employees
    
    @property
    def is_under_capacity(self):
        """هل القسم أقل من الحد الأدنى للموظفين"""
        return self.employee_count < self.min_employees
    
    @property
    def capacity_percentage(self):
        """نسبة الإشغال الحالية"""
        if self.max_employees == 0:
            return 0
        return (self.employee_count / self.max_employees) * 100
    
    def get_all_children(self):
        """الحصول على جميع الأقسام الفرعية (بما في ذلك الأقسام الفرعية للأقسام الفرعية)"""
        children = list(self.children.filter(is_active=True))
        for child in self.children.filter(is_active=True):
            children.extend(child.get_all_children())
        return children
    
    def get_managers_hierarchy(self):
        """الحصول على تسلسل المدراء في الهيكل الهرمي"""
        managers = []
        if self.manager:
            managers.append(self.manager)
        if self.assistant_manager:
            managers.append(self.assistant_manager)
        
        parent = self.parent
        while parent:
            if parent.manager:
                managers.append(parent.manager)
            parent = parent.parent
        
        return managers
