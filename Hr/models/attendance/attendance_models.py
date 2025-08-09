# -*- coding: utf-8 -*-
"""
نماذج الحضور والوقت المتقدمة لنظام إدارة الموارد البشرية (HRMS)
Enhanced Attendance Models with Advanced Features
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from django.conf import settings
from decimal import Decimal
import json

User = get_user_model()


class AttendanceRecordEnhanced(models.Model):
    """نموذج سجل الحضور المفصل والمتقدم"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_("الموظف")
    )
    
    # Date and Time Information
    date = models.DateField(verbose_name=_("التاريخ"))
    
    # Check-in Information
    check_in_time = models.TimeField(
        null=True, 
        blank=True, 
        verbose_name=_("وقت الدخول")
    )
    
    check_out_time = models.TimeField(
        null=True, 
        blank=True, 
        verbose_name=_("وقت الخروج")
    )
    
    # Status and Calculations
    STATUS_CHOICES = [
        ('present', _('حاضر')),
        ('absent', _('غائب')),
        ('late', _('متأخر')),
        ('early_departure', _('انصراف مبكر')),
        ('half_day', _('نصف يوم')),
        ('overtime', _('وقت إضافي')),
        ('holiday', _('عطلة')),
        ('leave', _('إجازة')),
        ('sick_leave', _('إجازة مرضية')),
        ('business_trip', _('مهمة عمل')),
        ('training', _('تدريب')),
        ('pending', _('في انتظار المراجعة')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name=_("الحالة")
    )
    
    # Time Calculations
    total_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("إجمالي الساعات")
    )
    
    regular_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الساعات العادية")
    )
    
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("ساعات الوقت الإضافي")
    )
    
    late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق التأخير")
    )
    
    early_departure_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق الانصراف المبكر")
    )
    
    # System Fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("سجل حضور محسن")
        verbose_name_plural = _("سجلات الحضور المحسنة")
        db_table = 'hrms_attendance_record_enhanced'
        ordering = ['-date', '-check_in_time']
        unique_together = [['employee', 'date']]
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.get_status_display()})"


class EmployeeShiftAssignmentEnhanced(models.Model):
    """نموذج تعيين الورديات المحسن للموظفين"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced',
        on_delete=models.CASCADE,
        related_name='shift_assignments',
        verbose_name=_("الموظف")
    )
    
    shift = models.ForeignKey(
        'Hr.WorkShift',
        on_delete=models.CASCADE,
        related_name='employee_assignments',
        verbose_name=_("الوردية")
    )
    
    # Assignment Details
    ASSIGNMENT_TYPES = [
        ('permanent', _('دائم')),
        ('temporary', _('مؤقت')),
        ('rotating', _('متناوب')),
        ('seasonal', _('موسمي')),
        ('project_based', _('مشروع محدد')),
        ('emergency', _('طوارئ')),
    ]
    
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPES,
        default='permanent',
        verbose_name=_("نوع التعيين")
    )
    
    # Date Range
    start_date = models.DateField(verbose_name=_("تاريخ البداية"))
    end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("تاريخ النهاية")
    )
    
    # Status and Priority
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    # System Fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("تعيين وردية محسن")
        verbose_name_plural = _("تعيينات الورديات المحسنة")
        db_table = 'hrms_employee_shift_assignment_enhanced'
        ordering = ['-start_date']
        unique_together = [['employee', 'shift', 'start_date']]
        indexes = [
            models.Index(fields=['employee', 'is_active']),
            models.Index(fields=['shift', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.shift.name} ({self.start_date})"
    
    @property
    def is_current(self):
        """هل هذا التعيين حالي؟"""
        today = timezone.now().date()
        if not self.is_active:
            return False
        
        if self.start_date > today:
            return False
        
        if self.end_date and self.end_date < today:
            return False
        
        return True
    
    @property
    def duration_days(self):
        """مدة التعيين بالأيام"""
        if not self.end_date:
            return None
        
        return (self.end_date - self.start_date).days