# -*- coding: utf-8 -*-
"""
Payroll Period Models for HRMS
Handles payroll periods and processing cycles
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta


class PayrollPeriod(models.Model):
    """
    نموذج فترة الراتب - يحدد فترات حساب الرواتب
    """
    PERIOD_TYPES = [
        ('monthly', _('شهري')),
        ('bi_weekly', _('كل أسبوعين')),
        ('weekly', _('أسبوعي')),
        ('quarterly', _('ربع سنوي')),
        ('annual', _('سنوي')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('active', _('نشط')),
        ('processing', _('قيد المعالجة')),
        ('completed', _('مكتمل')),
        ('closed', _('مغلق')),
        ('cancelled', _('ملغي')),
    ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name=_('المعرف')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('اسم الفترة'),
        help_text=_('مثال: راتب يناير 2024')
    )
    
    name_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('الاسم بالإنجليزية'),
        help_text=_('January 2024 Payroll')
    )
    
    period_type = models.CharField(
        max_length=20,
        choices=PERIOD_TYPES,
        default='monthly',
        verbose_name=_('نوع الفترة')
    )
    
    start_date = models.DateField(
        verbose_name=_('تاريخ البداية'),
        help_text=_('تاريخ بداية فترة الراتب')
    )
    
    end_date = models.DateField(
        verbose_name=_('تاريخ النهاية'),
        help_text=_('تاريخ نهاية فترة الراتب')
    )
    
    pay_date = models.DateField(
        verbose_name=_('تاريخ الدفع'),
        help_text=_('التاريخ المخطط لدفع الرواتب')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('الحالة')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل هذه الفترة نشطة؟')
    )
    
    total_employees = models.PositiveIntegerField(
        default=0,
        verbose_name=_('إجمالي الموظفين'),
        help_text=_('عدد الموظفين في هذه الفترة')
    )
    
    total_gross_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name=_('إجمالي الراتب الأساسي'),
        help_text=_('مجموع الرواتب الأساسية لجميع الموظفين')
    )
    
    total_deductions = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name=_('إجمالي الخصومات'),
        help_text=_('مجموع جميع الخصومات')
    )
    
    total_allowances = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name=_('إجمالي البدلات'),
        help_text=_('مجموع جميع البدلات')
    )
    
    total_net_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name=_('إجمالي الراتب الصافي'),
        help_text=_('مجموع الرواتب الصافية لجميع الموظفين')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات'),
        help_text=_('ملاحظات إضافية حول فترة الراتب')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_payroll_periods',
        verbose_name=_('أنشئ بواسطة')
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='approved_payroll_periods',
        null=True,
        blank=True,
        verbose_name=_('وافق عليه')
    )
    
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ المعالجة'),
        help_text=_('تاريخ ووقت معالجة الرواتب')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )

    class Meta:
        verbose_name = _('فترة راتب')
        verbose_name_plural = _('فترات الرواتب')
        ordering = ['-start_date', '-created_at']
        unique_together = ['start_date', 'end_date', 'period_type']
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status']),
            models.Index(fields=['period_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    def clean(self):
        """التحقق من صحة البيانات"""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية'))
            
            if self.pay_date and self.pay_date < self.end_date:
                raise ValidationError(_('تاريخ الدفع يجب أن يكون بعد تاريخ نهاية الفترة'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration_days(self):
        """عدد أيام الفترة"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def is_current(self):
        """هل هذه الفترة الحالية؟"""
        today = timezone.now().date()
        return (self.start_date <= today <= self.end_date and 
                self.is_active)

    @property
    def is_overdue(self):
        """هل تأخر دفع الراتب؟"""
        if self.pay_date and self.status not in ['completed', 'closed']:
            return timezone.now().date() > self.pay_date
        return False

    @property
    def progress_percentage(self):
        """نسبة التقدم في الفترة"""
        if not self.start_date or not self.end_date:
            return 0
        
        today = timezone.now().date()
        if today < self.start_date:
            return 0
        elif today > self.end_date:
            return 100
        else:
            total_days = (self.end_date - self.start_date).days
            elapsed_days = (today - self.start_date).days
            return int((elapsed_days / total_days) * 100) if total_days > 0 else 0

    def can_be_processed(self):
        """هل يمكن معالجة هذه الفترة؟"""
        return (self.status == 'active' and 
                self.start_date <= timezone.now().date())

    def can_be_closed(self):
        """هل يمكن إغلاق هذه الفترة؟"""
        return self.status == 'completed'

    @classmethod
    def get_current_period(cls, period_type='monthly'):
        """الحصول على الفترة الحالية"""
        today = timezone.now().date()
        return cls.objects.filter(
            period_type=period_type,
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        ).first()

    @classmethod
    def create_next_period(cls, period_type='monthly', created_by=None):
        """إنشاء الفترة التالية تلقائياً"""
        last_period = cls.objects.filter(
            period_type=period_type,
            is_active=True
        ).order_by('-end_date').first()
        
        if not last_period:
            return None
        
        if period_type == 'monthly':
            start_date = last_period.end_date + timedelta(days=1)
            end_date = start_date.replace(
                month=start_date.month + 1 if start_date.month < 12 else 1,
                year=start_date.year if start_date.month < 12 else start_date.year + 1,
                day=1
            ) - timedelta(days=1)
        elif period_type == 'bi_weekly':
            start_date = last_period.end_date + timedelta(days=1)
            end_date = start_date + timedelta(days=13)
        elif period_type == 'weekly':
            start_date = last_period.end_date + timedelta(days=1)
            end_date = start_date + timedelta(days=6)
        else:
            return None
        
        pay_date = end_date + timedelta(days=5)  # 5 أيام بعد نهاية الفترة
        
        name = f"راتب {start_date.strftime('%B %Y')}"
        name_en = f"{start_date.strftime('%B %Y')} Payroll"
        
        return cls.objects.create(
            name=name,
            name_en=name_en,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            pay_date=pay_date,
            created_by=created_by,
            status='draft'
        )