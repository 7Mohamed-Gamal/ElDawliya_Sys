"""
Department Models for HRMS
Handles organizational departments structure
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Department(models.Model):
    """
    Department model representing organizational units
    with hierarchical structure
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
        verbose_name=_("اسم القسم")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود القسم")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف القسم")
    )
    
    # Department Settings
    department_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات القسم")
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
    
    # Operational Information
    cost_center = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("مركز التكلفة")
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
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
        ordering = ['company', 'name']
        indexes = [
            models.Index(fields=['company', 'branch']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        branch_name = f" - {self.branch.name}" if self.branch else ""
        return f"{self.company.name}{branch_name} - {self.name}"
    
    def save(self, *args, **kwargs):
        """Override save to set default settings"""
        if not self.department_settings:
            self.department_settings = {
                'approval_required': True,
                'min_staff': 1,
                'max_staff': 20,
                'allow_remote_work': False,
                'default_shift_hours': 8
            }
        
        # Auto-generate code if not provided
        if not self.code:
            self.code = f"DPT{uuid.uuid4().hex[:6].upper()}"
        
        super().save(*args, **kwargs)
