"""
Job Position Models for HRMS
Handles job positions and levels within the organization
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class JobPosition(models.Model):
    """
    Job Position model representing roles within the company
    with defined levels and career paths
    """
    
    # Position Levels
    ENTRY = 1
    JUNIOR = 2
    MID = 3
    SENIOR = 4
    MANAGER = 5
    DIRECTOR = 6
    EXECUTIVE = 7

    LEVEL_CHOICES = (
        (ENTRY, _("مبتدئ")),
        (JUNIOR, _("مبتدئ متقدم")),
        (MID, _("متوسط")),
        (SENIOR, _("خبير")),
        (MANAGER, _("مدير")),
        (DIRECTOR, _("مدير إدارة")),
        (EXECUTIVE, _("تنفيذي")),
    )

    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Core Fields
    title = models.CharField(
        max_length=100,
        verbose_name=_("المسمى الوظيفي")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود الوظيفة")
    )
    
    level = models.PositiveSmallIntegerField(
        choices=LEVEL_CHOICES,
        default=MID,
        verbose_name=_("المستوى الوظيفي")
    )
    
    description = models.TextField(
        verbose_name=_("وصف الوظيفة")
    )
    
    # Relationships
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_("القسم")
    )
    
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_("المدير المباشر")
    )
    
    # Compensation
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("الراتب الأساسي")
    )
    
    # Requirements
    qualifications = models.TextField(
        verbose_name=_("المؤهلات المطلوبة")
    )
    
    experience_years = models.PositiveSmallIntegerField(
        verbose_name=_("سنوات الخبرة المطلوبة")
    )
    
    # Status
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
        verbose_name = _("وظيفة")
        verbose_name_plural = _("الوظائف")
        db_table = 'hrms_jobposition'
        ordering = ['department', 'level', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_level_display()}) - {self.department.name}"
