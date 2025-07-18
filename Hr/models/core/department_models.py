"""
Department Models for HRMS
Handles department structure and hierarchy
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings
from django.core.exceptions import ValidationError


class Department(models.Model):
    """
    Department model for organizational structure
    Supports hierarchical department structure with parent-child relationships
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationship to Company and Branch
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
    
    # Hierarchical Structure
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_departments',
        verbose_name=_("القسم الأب")
    )
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        verbose_name=_("اسم القسم")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود القسم"),
        help_text=_("كود فريد للقسم"),
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-]+$',
                message=_("كود القسم يجب أن يحتوي على أحرف كبيرة وأرقام فقط")
            )
        ]
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف القسم")
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
        verbose_name=_("مساعد مدير القسم")
    )
    
    # Contact Information
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني")
    )
    
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الهاتف")
    )
    
    extension = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_("رقم التحويلة")
    )
    
    # Location Information
    floor = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("الطابق")
    )
    
    room_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم المكتب")
    )
    
    location_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات الموقع")
    )
    
    # Financial Information
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الميزانية السنوية")
    )
    
    cost_center_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("كود مركز التكلفة")
    )
    
    # Operational Information
    employee_capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("السعة القصوى للموظفين")
    )
    
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
    
    # Department Type and Category
    DEPARTMENT_TYPES = [
        ('operational', _('تشغيلي')),
        ('administrative', _('إداري')),
        ('support', _('دعم')),
        ('technical', _('تقني')),
        ('sales', _('مبيعات')),
        ('finance', _('مالي')),
        ('hr', _('موارد بشرية')),
        ('it', _('تكنولوجيا المعلومات')),
        ('marketing', _('تسويق')),
        ('production', _('إنتاج')),
        ('quality', _('جودة')),
        ('research', _('بحث وتطوير')),
    ]
    
    department_type = models.CharField(
        max_length=20,
        choices=DEPARTMENT_TYPES,
        default='operational',
        verbose_name=_("نوع القسم")
    )
    
    # Department Level in Hierarchy
    level = models.PositiveIntegerField(
        default=1,
        verbose_name=_("مستوى القسم"),
        help_text=_("مستوى القسم في الهيكل التنظيمي")
    )
    
    # Department Settings
    department_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات القسم"),
        help_text=_("إعدادات خاصة بالقسم")
    )
    
    # Goals and KPIs
    annual_goals = models.JSONField(
        default=list,
        verbose_name=_("الأهداف السنوية"),
        help_text=_("قائمة بالأهداف السنوية للقسم")
    )
    
    kpis = models.JSONField(
        default=list,
        verbose_name=_("مؤشرات الأداء الرئيسية"),
        help_text=_("مؤشرات الأداء الرئيسية للقسم")
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    established_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التأسيس")
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_departments',
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
        verbose_name = _("قسم")
        verbose_name_plural = _("الأقسام")
        db_table = 'hrms_department'
        ordering = ['company', 'level', 'name']
        unique_together = [['company', 'code']]
        indexes = [
            models.Index(fields=['company', 'name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['department_type']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        if self.parent_department:
            return f"{self.parent_department.name} > {self.name}"
        return self.name
    
    def clean(self):
        """Validate department data"""
        super().clean()
        
        # Prevent circular references in parent-child relationships
        if self.parent_department:
            if self.parent_department == self:
                raise ValidationError(_("القسم لا يمكن أن يكون أب لنفسه"))
            
            # Check for circular reference
            parent = self.parent_department
            while parent:
                if parent == self:
                    raise ValidationError(_("لا يمكن إنشاء مرجع دائري في هيكل الأقسام"))
                parent = parent.parent_department
        
        # Validate branch belongs to same company
        if self.branch and self.branch.company != self.company:
            raise ValidationError(_("الفرع يجب أن ينتمي لنفس الشركة"))
    
    def get_active_employees_count(self):
        """Get count of active employees in this department"""
        return self.employees.filter(status='active').count()
    
    def get_sub_departments_count(self):
        """Get count of sub-departments"""
        return self.sub_departments.filter(is_active=True).count()
    
    def get_all_sub_departments(self):
        """Get all sub-departments recursively"""
        sub_departments = []
        for sub_dept in self.sub_departments.filter(is_active=True):
            sub_departments.append(sub_dept)
            sub_departments.extend(sub_dept.get_all_sub_departments())
        return sub_departments
    
    def get_department_hierarchy(self):
        """Get full department hierarchy path"""
        hierarchy = [self.name]
        parent = self.parent_department
        while parent:
            hierarchy.insert(0, parent.name)
            parent = parent.parent_department
        return " > ".join(hierarchy)
    
    @property
    def full_location(self):
        """Get formatted full location"""
        location_parts = []
        if self.branch:
            location_parts.append(self.branch.name)
        if self.floor:
            location_parts.append(f"الطابق {self.floor}")
        if self.room_number:
            location_parts.append(f"مكتب {self.room_number}")
        return ", ".join(location_parts)
    
    def save(self, *args, **kwargs):
        """Override save to set level and default settings"""
        # Calculate department level
        if self.parent_department:
            self.level = self.parent_department.level + 1
        else:
            self.level = 1
        
        # Set default department settings
        if not self.department_settings:
            self.department_settings = {
                'allow_overtime': True,
                'require_manager_approval_for_leave': True,
                'max_leave_days_without_approval': 3,
                'performance_review_frequency': 'annual',
                'budget_tracking_enabled': True,
                'goal_tracking_enabled': True,
            }
        
        # Auto-generate code if not provided
        if not self.code:
            company_code = self.company.name[:2].upper()
            dept_count = Department.objects.filter(company=self.company).count()
            self.code = f"{company_code}-DEPT{dept_count + 1:03d}"
        
        super().save(*args, **kwargs)
