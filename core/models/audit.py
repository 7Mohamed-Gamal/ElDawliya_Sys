"""
Audit and Monitoring System Models
نماذج نظام التدقيق والمراقبة

This module provides comprehensive audit logging and monitoring capabilities
for tracking all system activities and security events.
"""

import uuid
import json
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AuditLog(models.Model):
    """
    Comprehensive audit log for all system activities
    سجل التدقيق الشامل لجميع أنشطة النظام
    """
    ACTION_TYPES = [
        ('create', _('إنشاء')),
        ('read', _('قراءة')),
        ('update', _('تحديث')),
        ('delete', _('حذف')),
        ('login', _('تسجيل دخول')),
        ('logout', _('تسجيل خروج')),
        ('permission_grant', _('منح صلاحية')),
        ('permission_revoke', _('إلغاء صلاحية')),
        ('role_assign', _('تعيين دور')),
        ('role_revoke', _('إلغاء دور')),
        ('export', _('تصدير')),
        ('import', _('استيراد')),
        ('backup', _('نسخ احتياطي')),
        ('restore', _('استعادة')),
        ('config_change', _('تغيير إعدادات')),
        ('security_event', _('حدث أمني')),
        ('api_access', _('وصول API')),
        ('file_access', _('وصول ملف')),
        ('report_generate', _('توليد تقرير')),
        ('system_maintenance', _('صيانة النظام')),
    ]

    SEVERITY_LEVELS = [
        ('low', _('منخفض')),
        ('medium', _('متوسط')),
        ('high', _('عالي')),
        ('critical', _('حرج')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User and session information
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs',
        verbose_name=_('المستخدم')
    )
    session_key = models.CharField(max_length=40, blank=True, verbose_name=_('مفتاح الجلسة'))
    
    # Action details
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, verbose_name=_('نوع الإجراء'))
    action_description = models.TextField(verbose_name=_('وصف الإجراء'))
    
    # Target object information
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('نوع المحتوى')
    )
    object_id = models.CharField(max_length=255, blank=True, verbose_name=_('معرف الكائن'))
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=500, blank=True, verbose_name=_('تمثيل الكائن'))
    
    # Change tracking
    old_values = models.JSONField(
        default=dict, 
        blank=True, 
        encoder=DjangoJSONEncoder,
        verbose_name=_('القيم القديمة')
    )
    new_values = models.JSONField(
        default=dict, 
        blank=True, 
        encoder=DjangoJSONEncoder,
        verbose_name=_('القيم الجديدة')
    )
    
    # Request information
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('عنوان IP'))
    user_agent = models.TextField(blank=True, verbose_name=_('وكيل المستخدم'))
    request_method = models.CharField(max_length=10, blank=True, verbose_name=_('طريقة الطلب'))
    request_path = models.CharField(max_length=500, blank=True, verbose_name=_('مسار الطلب'))
    request_data = models.JSONField(
        default=dict, 
        blank=True, 
        encoder=DjangoJSONEncoder,
        verbose_name=_('بيانات الطلب')
    )
    
    # Response information
    response_status = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('حالة الاستجابة'))
    response_time = models.FloatField(null=True, blank=True, verbose_name=_('وقت الاستجابة'))
    
    # Security and classification
    severity = models.CharField(
        max_length=20, 
        choices=SEVERITY_LEVELS, 
        default='low',
        verbose_name=_('مستوى الخطورة')
    )
    is_suspicious = models.BooleanField(default=False, verbose_name=_('مشبوه'))
    is_security_relevant = models.BooleanField(default=False, verbose_name=_('متعلق بالأمان'))
    
    # Additional metadata
    module = models.CharField(max_length=100, blank=True, verbose_name=_('الوحدة'))
    tags = models.JSONField(default=list, blank=True, verbose_name=_('العلامات'))
    additional_data = models.JSONField(
        default=dict, 
        blank=True, 
        encoder=DjangoJSONEncoder,
        verbose_name=_('بيانات إضافية')
    )
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('الطابع الزمني'))
    
    class Meta:
        verbose_name = _('سجل التدقيق')
        verbose_name_plural = _('سجلات التدقيق')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['is_suspicious', 'timestamp']),
            models.Index(fields=['is_security_relevant', 'timestamp']),
            models.Index(fields=['module', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.user or 'Anonymous'} - {self.timestamp}"

    def get_changes_summary(self):
        """Get a summary of changes made"""
        if not self.old_values and not self.new_values:
            return None
        
        changes = []
        all_fields = set(self.old_values.keys()) | set(self.new_values.keys())
        
        for field in all_fields:
            old_val = self.old_values.get(field)
            new_val = self.new_values.get(field)
            
            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val
                })
        
        return changes

    def is_failed_login(self):
        """Check if this is a failed login attempt"""
        return (self.action_type == 'login' and 
                self.response_status and 
                self.response_status >= 400)

    def get_risk_score(self):
        """Calculate risk score based on various factors"""
        score = 0
        
        # Base score by severity
        severity_scores = {'low': 1, 'medium': 3, 'high': 7, 'critical': 10}
        score += severity_scores.get(self.severity, 1)
        
        # Add score for suspicious activity
        if self.is_suspicious:
            score += 5
        
        # Add score for security-relevant actions
        if self.is_security_relevant:
            score += 3
        
        # Add score for failed operations
        if self.response_status and self.response_status >= 400:
            score += 2
        
        # Add score for sensitive actions
        sensitive_actions = ['delete', 'permission_grant', 'role_assign', 'config_change']
        if self.action_type in sensitive_actions:
            score += 2
        
        return min(score, 10)  # Cap at 10


class SecurityEvent(models.Model):
    """
    Security-specific events and incidents
    الأحداث والحوادث الأمنية المحددة
    """
    EVENT_TYPES = [
        ('failed_login', _('فشل تسجيل الدخول')),
        ('brute_force', _('هجوم القوة الغاشمة')),
        ('suspicious_activity', _('نشاط مشبوه')),
        ('unauthorized_access', _('وصول غير مصرح')),
        ('privilege_escalation', _('تصعيد الصلاحيات')),
        ('data_breach', _('خرق البيانات')),
        ('malware_detected', _('اكتشاف برمجيات خبيثة')),
        ('ddos_attack', _('هجوم DDoS')),
        ('sql_injection', _('حقن SQL')),
        ('xss_attempt', _('محاولة XSS')),
        ('csrf_attack', _('هجوم CSRF')),
        ('file_upload_threat', _('تهديد رفع الملفات')),
        ('api_abuse', _('إساءة استخدام API')),
        ('session_hijacking', _('اختطاف الجلسة')),
        ('account_takeover', _('استيلاء على الحساب')),
    ]

    THREAT_LEVELS = [
        ('info', _('معلوماتي')),
        ('low', _('منخفض')),
        ('medium', _('متوسط')),
        ('high', _('عالي')),
        ('critical', _('حرج')),
    ]

    STATUS_CHOICES = [
        ('detected', _('مكتشف')),
        ('investigating', _('قيد التحقيق')),
        ('confirmed', _('مؤكد')),
        ('mitigated', _('تم التخفيف')),
        ('resolved', _('محلول')),
        ('false_positive', _('إيجابي خاطئ')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Event classification
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name=_('نوع الحدث'))
    threat_level = models.CharField(max_length=20, choices=THREAT_LEVELS, verbose_name=_('مستوى التهديد'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detected', verbose_name=_('الحالة'))
    
    # Event details
    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    description = models.TextField(verbose_name=_('الوصف'))
    
    # Source information
    source_ip = models.GenericIPAddressField(verbose_name=_('IP المصدر'))
    source_user_agent = models.TextField(blank=True, verbose_name=_('وكيل المستخدم المصدر'))
    source_country = models.CharField(max_length=100, blank=True, verbose_name=_('البلد المصدر'))
    
    # Target information
    target_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='security_events_targeted',
        verbose_name=_('المستخدم المستهدف')
    )
    target_endpoint = models.CharField(max_length=500, blank=True, verbose_name=_('النقطة المستهدفة'))
    target_resource = models.CharField(max_length=500, blank=True, verbose_name=_('المورد المستهدف'))
    
    # Detection information
    detected_by = models.CharField(max_length=100, verbose_name=_('اكتشف بواسطة'))
    detection_method = models.CharField(max_length=100, blank=True, verbose_name=_('طريقة الاكتشاف'))
    confidence_score = models.FloatField(default=0.0, verbose_name=_('درجة الثقة'))
    
    # Response information
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_security_events',
        verbose_name=_('مخصص لـ')
    )
    response_actions = models.JSONField(default=list, blank=True, verbose_name=_('إجراءات الاستجابة'))
    mitigation_steps = models.TextField(blank=True, verbose_name=_('خطوات التخفيف'))
    
    # Evidence and artifacts
    evidence = models.JSONField(default=dict, blank=True, verbose_name=_('الأدلة'))
    artifacts = models.JSONField(default=list, blank=True, verbose_name=_('القطع الأثرية'))
    
    # Related audit logs
    related_logs = models.ManyToManyField(
        AuditLog, 
        blank=True, 
        related_name='security_events',
        verbose_name=_('السجلات المرتبطة')
    )
    
    # Timestamps
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name=_('وقت الاكتشاف'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('وقت التحديث'))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('وقت الحل'))
    
    class Meta:
        verbose_name = _('حدث أمني')
        verbose_name_plural = _('الأحداث الأمنية')
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['event_type', 'detected_at']),
            models.Index(fields=['threat_level', 'detected_at']),
            models.Index(fields=['status', 'detected_at']),
            models.Index(fields=['source_ip', 'detected_at']),
            models.Index(fields=['target_user', 'detected_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_threat_level_display()}"

    def get_duration(self):
        """Get event duration if resolved"""
        if self.resolved_at:
            return self.resolved_at - self.detected_at
        return None

    def is_active(self):
        """Check if event is still active"""
        return self.status not in ['resolved', 'false_positive']

    def get_severity_color(self):
        """Get color code for threat level"""
        colors = {
            'info': '#17a2b8',
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545'
        }
        return colors.get(self.threat_level, '#6c757d')


class SystemMetric(models.Model):
    """
    System performance and health metrics
    مقاييس أداء وصحة النظام
    """
    METRIC_TYPES = [
        ('cpu_usage', _('استخدام المعالج')),
        ('memory_usage', _('استخدام الذاكرة')),
        ('disk_usage', _('استخدام القرص')),
        ('network_io', _('إدخال/إخراج الشبكة')),
        ('database_connections', _('اتصالات قاعدة البيانات')),
        ('active_sessions', _('الجلسات النشطة')),
        ('api_requests', _('طلبات API')),
        ('response_time', _('وقت الاستجابة')),
        ('error_rate', _('معدل الأخطاء')),
        ('login_attempts', _('محاولات تسجيل الدخول')),
        ('failed_logins', _('فشل تسجيل الدخول')),
        ('user_activity', _('نشاط المستخدمين')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Metric identification
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES, verbose_name=_('نوع المقياس'))
    metric_name = models.CharField(max_length=100, verbose_name=_('اسم المقياس'))
    
    # Metric values
    value = models.FloatField(verbose_name=_('القيمة'))
    unit = models.CharField(max_length=20, blank=True, verbose_name=_('الوحدة'))
    
    # Thresholds
    warning_threshold = models.FloatField(null=True, blank=True, verbose_name=_('عتبة التحذير'))
    critical_threshold = models.FloatField(null=True, blank=True, verbose_name=_('العتبة الحرجة'))
    
    # Context information
    host = models.CharField(max_length=100, blank=True, verbose_name=_('المضيف'))
    service = models.CharField(max_length=100, blank=True, verbose_name=_('الخدمة'))
    tags = models.JSONField(default=dict, blank=True, verbose_name=_('العلامات'))
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('الطابع الزمني'))
    
    class Meta:
        verbose_name = _('مقياس النظام')
        verbose_name_plural = _('مقاييس النظام')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['metric_name', 'timestamp']),
            models.Index(fields=['host', 'timestamp']),
            models.Index(fields=['service', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.metric_name}: {self.value} {self.unit}"

    def get_status(self):
        """Get metric status based on thresholds"""
        if self.critical_threshold and self.value >= self.critical_threshold:
            return 'critical'
        elif self.warning_threshold and self.value >= self.warning_threshold:
            return 'warning'
        else:
            return 'normal'

    def is_alerting(self):
        """Check if metric is in alerting state"""
        return self.get_status() in ['warning', 'critical']


class AlertRule(models.Model):
    """
    Rules for generating alerts based on metrics and events
    قواعد توليد التنبيهات بناءً على المقاييس والأحداث
    """
    RULE_TYPES = [
        ('threshold', _('عتبة')),
        ('anomaly', _('شذوذ')),
        ('pattern', _('نمط')),
        ('correlation', _('ارتباط')),
    ]

    SEVERITY_LEVELS = [
        ('info', _('معلوماتي')),
        ('warning', _('تحذير')),
        ('critical', _('حرج')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Rule identification
    name = models.CharField(max_length=200, verbose_name=_('اسم القاعدة'))
    description = models.TextField(verbose_name=_('الوصف'))
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, verbose_name=_('نوع القاعدة'))
    
    # Rule configuration
    conditions = models.JSONField(verbose_name=_('الشروط'))
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name=_('مستوى الخطورة'))
    
    # Notification settings
    notification_channels = models.JSONField(default=list, verbose_name=_('قنوات الإشعار'))
    notification_template = models.TextField(blank=True, verbose_name=_('قالب الإشعار'))
    
    # Rule state
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    last_triggered = models.DateTimeField(null=True, blank=True, verbose_name=_('آخر تفعيل'))
    trigger_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد التفعيلات'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('قاعدة التنبيه')
        verbose_name_plural = _('قواعد التنبيه')
        ordering = ['name']

    def __str__(self):
        return self.name

    def evaluate(self, context):
        """Evaluate rule against given context"""
        # This would contain the logic to evaluate the rule
        # Implementation depends on rule type and conditions
        pass


class Alert(models.Model):
    """
    Generated alerts from alert rules
    التنبيهات المولدة من قواعد التنبيه
    """
    STATUS_CHOICES = [
        ('open', _('مفتوح')),
        ('acknowledged', _('مؤكد')),
        ('resolved', _('محلول')),
        ('suppressed', _('مكبوت')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Alert source
    rule = models.ForeignKey(
        AlertRule, 
        on_delete=models.CASCADE, 
        related_name='alerts',
        verbose_name=_('القاعدة')
    )
    
    # Alert details
    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    message = models.TextField(verbose_name=_('الرسالة'))
    severity = models.CharField(max_length=20, choices=AlertRule.SEVERITY_LEVELS, verbose_name=_('مستوى الخطورة'))
    
    # Alert state
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name=_('الحالة'))
    
    # Response information
    acknowledged_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acknowledged_alerts',
        verbose_name=_('أكد بواسطة')
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name=_('وقت التأكيد'))
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_alerts',
        verbose_name=_('حل بواسطة')
    )
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('وقت الحل'))
    
    # Context data
    context_data = models.JSONField(default=dict, blank=True, verbose_name=_('بيانات السياق'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('تنبيه')
        verbose_name_plural = _('التنبيهات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
            models.Index(fields=['rule', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"

    def get_duration(self):
        """Get alert duration"""
        end_time = self.resolved_at or timezone.now()
        return end_time - self.created_at

    def is_active(self):
        """Check if alert is still active"""
        return self.status in ['open', 'acknowledged']