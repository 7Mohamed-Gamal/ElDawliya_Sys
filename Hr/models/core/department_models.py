"""
Department Models for HRMS
Handles organizational departments with hierarchical structure
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings
from django.core.exceptions import ValidationError


class Department(models.Model):
    """
    Department model for managing organizational structure
    Supports hierarchical departments with parent-child relationships
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationship to Branch
    branch = models.ForeignKey(
        'Branch',
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name=_("الفرع")
    )
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        verbose_name=_("اسم القسم")
    )
    
    name_english = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("الاسم بالإنجليزية")
    )
    
    code = models.CharField(
        max_length=20,
        verbose_name=_("كود القسم"),
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
    
    # Hierarchical Structure
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_departments',
        verbose_name=_("القسم الأب")
    )
    
    level = models.PositiveIntegerField(
        default=0,
        verbose_name=_("مستوى القسم"),
        help_text=_("مستوى القسم في الهيكل التنظيمي")
    )
    
    # Management
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_("مدير القسم")
    )
    
    assistant_manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assistant_managed_departments',
        verbose_name=_("مساعد مدير القسم")
    )
    
    # Department Type and Function
    DEPARTMENT_TYPES = [
        ('administrative', _('إداري')),
        ('operational', _('تشغيلي')),
        ('support', _('دعم')),
        ('technical', _('تقني')),
        ('sales', _('مبيعات')),
        ('marketing', _('تسويق')),
        ('finance', _('مالي')),
        ('hr', _('موارد بشرية')),
        ('it', _('تكنولوجيا المعلومات')),
        ('legal', _('قانوني')),
        ('procurement', _('مشتريات')),
        ('quality', _('جودة')),
        ('research', _('بحث وتطوير')),
        ('production', _('إنتاج')),
        ('logistics', _('لوجستيات')),
        ('customer_service', _('خدمة العملاء')),
        ('other', _('أخرى')),
    ]
    
    department_type = models.CharField(
        max_length=20,
        choices=DEPARTMENT_TYPES,
        default='administrative',
        verbose_name=_("نوع القسم")
    )
    
    # Budget and Cost Center
    cost_center_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_("كود مركز التكلفة")
    )
    
    annual_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الميزانية السنوية")
    )
    
    # Location and Physical Information
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("الموقع")
    )
    
    floor = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الطابق")
    )
    
    extension = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم التحويلة")
    )
    
    # Department Goals and KPIs
    objectives = models.JSONField(
        default=list,
        verbose_name=_("أهداف القسم"),
        help_text=_("الأهداف الاستراتيجية للقسم")
    )
    
    kpis = models.JSONField(
        default=list,
        verbose_name=_("مؤشرات الأداء الرئيسية"),
        help_text=_("مؤشرات الأداء الرئيسية للقسم")
    )
    
    # Working Conditions
    working_hours = models.JSONField(
        default=dict,
        verbose_name=_("ساعات العمل"),
        help_text=_("ساعات العمل الخاصة بالقسم")
    )
    
    # Department Settings
    department_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات القسم"),
        help_text=_("إعدادات خاصة بالقسم")
    )
    
    # Capacity and Headcount
    max_employees = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("العدد الأقصى للموظفين")
    )
    
    current_employees = models.PositiveIntegerField(
        default=0,
        verbose_name=_("العدد الحالي للموظفين")
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_profit_center = models.BooleanField(
        default=False,
        verbose_name=_("مركز ربح"),
        help_text=_("هل هذا القسم مركز ربح؟")
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
        ordering = ['branch', 'level', 'name']
        unique_together = [['branch', 'code']]
        indexes = [
            models.Index(fields=['branch', 'code']),
            models.Index(fields=['parent']),
            models.Index(fields=['level']),
            models.Index(fields=['department_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['cost_center_code']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.branch.name}"
    
    def clean(self):
        """Validate department data"""
        super().clean()
        
        # Ensure code is uppercase
        if self.code:
            self.code = self.code.upper()
        
        # Prevent circular parent relationships
        if self.parent:
            if self.parent == self:
                raise ValidationError(_("القسم لا يمكن أن يكون أباً لنفسه"))
            
            # Check for circular reference
            parent = self.parent
            while parent:
                if parent == self:
                    raise ValidationError(_("لا يمكن إنشاء علاقة دائرية في هيكل الأقسام"))
                parent = parent.parent
        
        # Validate employee count
        if self.max_employees and self.current_employees > self.max_employees:
            raise ValidationError(_("العدد الحالي للموظفين لا يمكن أن يتجاوز العدد الأقصى"))
    
    def save(self, *args, **kwargs):
        """Override save to set level and auto-generate code"""
        # Set department level based on parent
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        
        # Auto-generate code if not provided
        if not self.code:
            branch_code = self.branch.code
            dept_count = Department.objects.filter(branch=self.branch).count()
            self.code = f"{branch_code}-DEPT{dept_count + 1:03d}"
        
        # Set default settings
        if not self.department_settings:
            self.department_settings = {
                'allow_overtime': True,
                'require_approval_for_leave': True,
                'default_work_hours': 8,
                'break_duration_minutes': 60,
                'flexible_hours': False,
            }
        
        # Update current employee count
        if self.pk:
            self.current_employees = self.employees.filter(is_active=True).count()
        
        super().save(*args, **kwargs)
    
    def get_full_path(self):
        """Get full hierarchical path of the department"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)
    
    def get_all_children(self):
        """Get all child departments recursively"""
        children = list(self.sub_departments.filter(is_active=True))
        for child in list(children):
            children.extend(child.get_all_children())
        return children
    
    def get_all_employees(self):
        """Get all employees in this department and its sub-departments"""
        from .employee_models import Employee
        
        # Get direct employees
        employees = list(self.employees.filter(is_active=True))
        
        # Get employees from sub-departments
        for sub_dept in self.sub_departments.filter(is_active=True):
            employees.extend(sub_dept.get_all_employees())
        
        return employees
    
    def get_total_employees_count(self):
        """Get total count of employees including sub-departments"""
        return len(self.get_all_employees())
    
    def get_available_positions(self):
        """Get number of available positions"""
        if self.max_employees:
            return self.max_employees - self.current_employees
        return None
    
    def is_position_available(self):
        """Check if department has available positions"""
        available = self.get_available_positions()
        return available is None or available > 0
    
    def get_department_hierarchy(self):
        """Get department hierarchy as a tree structure"""
        def build_tree(dept):
            return {
                'id': str(dept.id),
                'name': dept.name,
                'code': dept.code,
                'level': dept.level,
                'employee_count': dept.current_employees,
                'children': [build_tree(child) for child in dept.sub_departments.filter(is_active=True)]
            }
        
        return build_tree(self)
    
    @property
    def budget_utilization(self):
        """Calculate budget utilization percentage"""
        if not self.annual_budget:
            return None
        
        # This would typically calculate actual spending vs budget
        # For now, return a placeholder
        return 0.0
    
    @property
    def is_over_capacity(self):
        """Check if department is over capacity"""
        if not self.max_employees:
            return False
        return self.current_employees > self.max_employees
    
    def get_manager_hierarchy(self):
        """Get management hierarchy for this department"""
        hierarchy = []
        
        if self.manager:
            hierarchy.append({
                'level': 'manager',
                'title': _('مدير القسم'),
                'employee': self.manager
            })
        
        if self.assistant_manager:
            hierarchy.append({
                'level': 'assistant_manager',
                'title': _('مساعد مدير القسم'),
                'employee': self.assistant_manager
            })
        
        return hierarchy