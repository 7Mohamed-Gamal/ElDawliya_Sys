"""
HR System Main Models
===================

This file contains central HR system models and configurations
that are shared across all HR applications.
"""

from django.db import models
from django.conf import settings


# Placeholder for any central HR models
# Most models are in their respective apps (employees, payrolls, etc.)

class HRSystemConfig(models.Model):
    """إعدادات النظام المركزية"""
    
    key = models.CharField(max_length=100, unique=True, verbose_name='المفتاح')
    value = models.TextField(verbose_name='القيمة')
    description = models.TextField(blank=True, verbose_name='الوصف')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'إعداد النظام'
        verbose_name_plural = 'إعدادات النظام'
        db_table = 'hr_system_config'
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class HRSystemLog(models.Model):
    """سجل أحداث النظام"""
    
    ACTION_CHOICES = [
        ('create', 'إنشاء'),
        ('update', 'تحديث'),
        ('delete', 'حذف'),
        ('view', 'عرض'),
        ('export', 'تصدير'),
        ('import', 'استيراد'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='المستخدم')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='الإجراء')
    module = models.CharField(max_length=50, verbose_name='الوحدة')
    object_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='معرف الكائن')
    description = models.TextField(verbose_name='الوصف')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='عنوان IP')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الحدث')
    
    class Meta:
        verbose_name = 'سجل النظام'
        verbose_name_plural = 'سجلات النظام'
        db_table = 'hr_system_log'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.module} - {self.created_at}"