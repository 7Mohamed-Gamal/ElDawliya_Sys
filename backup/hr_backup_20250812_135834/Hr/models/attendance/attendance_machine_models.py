# -*- coding: utf-8 -*-
"""
نماذج أجهزة الحضور المتقدمة لنظام إدارة الموارد البشرية (HRMS)
Enhanced Attendance Machine Models with Advanced Features
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


# Legacy models for backward compatibility
class AttendanceMachine(models.Model):
    """نموذج جهاز الحضور الأساسي للتوافق مع النظام القديم"""
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الجهاز")
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("عنوان IP")
    )
    
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("الموقع")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    class Meta:
        verbose_name = _("جهاز حضور")
        verbose_name_plural = _("أجهزة الحضور")
        db_table = 'hrms_attendance_machine'
    
    def __str__(self):
        return self.name


class MachineUser(models.Model):
    """نموذج مستخدم الجهاز للتوافق مع النظام القديم"""
    
    machine = models.ForeignKey(
        AttendanceMachine,
        on_delete=models.CASCADE,
        verbose_name=_("الجهاز")
    )
    
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced',
        on_delete=models.CASCADE,
        verbose_name=_("الموظف")
    )
    
    user_id = models.CharField(
        max_length=50,
        verbose_name=_("معرف المستخدم في الجهاز")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    class Meta:
        verbose_name = _("مستخدم جهاز")
        verbose_name_plural = _("مستخدمو الأجهزة")
        db_table = 'hrms_machine_user'
        unique_together = [['machine', 'employee']]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.machine.name}"


class AttendanceMachineEnhanced(models.Model):
    """نموذج جهاز الحضور المحسن مع ميزات متقدمة"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الجهاز")
    )
    
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("الرقم التسلسلي")
    )
    
    model = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الموديل")
    )
    
    manufacturer = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الشركة المصنعة")
    )
    
    # Machine Type and Capabilities
    MACHINE_TYPES = [
        ('fingerprint', _('بصمة الإصبع')),
        ('face_recognition', _('التعرف على الوجه')),
        ('card_reader', _('قارئ البطاقات')),
        ('pin_pad', _('لوحة الأرقام')),
        ('iris_scanner', _('ماسح القزحية')),
        ('palm_reader', _('قارئ الكف')),
        ('mobile_app', _('تطبيق الجوال')),
        ('web_portal', _('البوابة الإلكترونية')),
        ('hybrid', _('متعدد الوسائل')),
    ]
    
    machine_type = models.CharField(
        max_length=20,
        choices=MACHINE_TYPES,
        default='fingerprint',
        verbose_name=_("نوع الجهاز")
    )
    
    # Supported Authentication Methods
    supported_methods = models.JSONField(
        default=list,
        verbose_name=_("طرق المصادقة المدعومة"),
        help_text=_("قائمة بطرق المصادقة التي يدعمها الجهاز")
    )
    
    # Location Information
    location_name = models.CharField(
        max_length=200,
        verbose_name=_("اسم الموقع")
    )
    
    building = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المبنى")
    )
    
    floor = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الطابق")
    )
    
    room = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الغرفة")
    )
    
    # GPS Coordinates
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name=_("خط العرض")
    )
    
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name=_("خط الطول")
    )
    
    # Network Configuration
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("عنوان IP")
    )
    
    port = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name=_("المنفذ")
    )
    
    mac_address = models.CharField(
        max_length=17,
        null=True,
        blank=True,
        verbose_name=_("عنوان MAC")
    )
    
    # Connection Settings
    CONNECTION_TYPES = [
        ('tcp', _('TCP/IP')),
        ('udp', _('UDP')),
        ('serial', _('منفذ تسلسلي')),
        ('usb', _('USB')),
        ('wifi', _('WiFi')),
        ('bluetooth', _('Bluetooth')),
        ('cloud', _('السحابة')),
        ('api', _('API')),
    ]
    
    connection_type = models.CharField(
        max_length=20,
        choices=CONNECTION_TYPES,
        default='tcp',
        verbose_name=_("نوع الاتصال")
    )
    
    connection_string = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("سلسلة الاتصال")
    )
    
    # Authentication and Security
    username = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم المستخدم")
    )
    
    password = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("كلمة المرور")
    )
    
    api_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("مفتاح API")
    )
    
    encryption_enabled = models.BooleanField(
        default=False,
        verbose_name=_("التشفير مفعل")
    )
    
    # Device Status and Health
    STATUS_CHOICES = [
        ('online', _('متصل')),
        ('offline', _('غير متصل')),
        ('maintenance', _('صيانة')),
        ('error', _('خطأ')),
        ('disabled', _('معطل')),
        ('testing', _('اختبار')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offline',
        verbose_name=_("الحالة")
    )
    
    last_ping = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("آخر اتصال")
    )
    
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("آخر مزامنة")
    )
    
    # Capacity and Limits
    max_users = models.PositiveIntegerField(
        default=1000,
        verbose_name=_("الحد الأقصى للمستخدمين")
    )
    
    max_records = models.PositiveIntegerField(
        default=100000,
        verbose_name=_("الحد الأقصى للسجلات")
    )
    
    current_users = models.PositiveIntegerField(
        default=0,
        verbose_name=_("المستخدمون الحاليون")
    )
    
    current_records = models.PositiveIntegerField(
        default=0,
        verbose_name=_("السجلات الحالية")
    )
    
    # Firmware and Software
    firmware_version = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("إصدار البرنامج الثابت")
    )
    
    software_version = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("إصدار البرنامج")
    )
    
    last_firmware_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("آخر تحديث للبرنامج الثابت")
    )
    
    # Sync Configuration
    auto_sync_enabled = models.BooleanField(
        default=True,
        verbose_name=_("المزامنة التلقائية مفعلة")
    )
    
    sync_interval_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name=_("فترة المزامنة (دقيقة)")
    )
    
    sync_start_time = models.TimeField(
        default=time(0, 0),
        verbose_name=_("وقت بداية المزامنة")
    )
    
    sync_end_time = models.TimeField(
        default=time(23, 59),
        verbose_name=_("وقت نهاية المزامنة")
    )
    
    # Department and Access Control
    department = models.ForeignKey(
        'Hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_machines',
        verbose_name=_("القسم")
    )
    
    allowed_departments = models.ManyToManyField(
        'Hr.Department',
        blank=True,
        related_name='accessible_machines',
        verbose_name=_("الأقسام المسموحة")
    )
    
    # Time Zone and Locale
    timezone_name = models.CharField(
        max_length=50,
        default='Asia/Riyadh',
        verbose_name=_("المنطقة الزمنية")
    )
    
    date_format = models.CharField(
        max_length=20,
        default='YYYY-MM-DD',
        verbose_name=_("تنسيق التاريخ")
    )
    
    time_format = models.CharField(
        max_length=20,
        default='HH:mm:ss',
        verbose_name=_("تنسيق الوقت")
    )
    
    # Notification Settings
    send_alerts = models.BooleanField(
        default=True,
        verbose_name=_("إرسال التنبيهات")
    )
    
    alert_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("بريد التنبيهات")
    )
    
    offline_alert_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name=_("تنبيه انقطاع الاتصال (دقيقة)")
    )
    
    # Maintenance Information
    installation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التركيب")
    )
    
    warranty_expiry = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("انتهاء الضمان")
    )
    
    last_maintenance = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("آخر صيانة")
    )
    
    next_maintenance = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("الصيانة القادمة")
    )
    
    maintenance_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات الصيانة")
    )
    
    # Status and Activation
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("جهاز رئيسي"),
        help_text=_("هل هذا الجهاز الرئيسي للموقع؟")
    )
    
    # System Fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_attendance_machines',
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
    
    # Configuration and Metadata
    configuration = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات الجهاز")
    )
    
    metadata = models.JSONField(
        default=dict,
        verbose_name=_("بيانات إضافية")
    )
    
    class Meta:
        verbose_name = _("جهاز حضور محسن")
        verbose_name_plural = _("أجهزة الحضور المحسنة")
        db_table = 'hrms_attendance_machine_enhanced'
        ordering = ['location_name', 'name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
            models.Index(fields=['machine_type']),
            models.Index(fields=['department']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['serial_number']),
            models.Index(fields=['last_ping']),
            models.Index(fields=['last_sync']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.location_name})"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        super().clean()
        
        # التحقق من عنوان IP والمنفذ للاتصال الشبكي
        if self.connection_type in ['tcp', 'udp'] and not self.ip_address:
            raise ValidationError(_("عنوان IP مطلوب لنوع الاتصال المحدد"))
        
        # التحقق من أوقات المزامنة
        if self.sync_start_time and self.sync_end_time:
            if self.sync_start_time >= self.sync_end_time:
                raise ValidationError(_("وقت بداية المزامنة يجب أن يكون قبل وقت النهاية"))
        
        # التحقق من الحد الأقصى للمستخدمين والسجلات
        if self.current_users > self.max_users:
            raise ValidationError(_("عدد المستخدمين الحاليين يتجاوز الحد الأقصى"))
        
        if self.current_records > self.max_records:
            raise ValidationError(_("عدد السجلات الحالية يتجاوز الحد الأقصى"))
    
    def save(self, *args, **kwargs):
        """حفظ الجهاز مع التحقق من الصحة"""
        # تحديد طرق المصادقة المدعومة تلقائياً
        if not self.supported_methods:
            self._set_default_supported_methods()
        
        # تحديث حالة الاتصال
        self._update_connection_status()
        
        super().save(*args, **kwargs)
    
    def _set_default_supported_methods(self):
        """تحديد طرق المصادقة الافتراضية"""
        method_mapping = {
            'fingerprint': ['fingerprint'],
            'face_recognition': ['face'],
            'card_reader': ['card'],
            'pin_pad': ['pin'],
            'iris_scanner': ['iris'],
            'palm_reader': ['palm'],
            'mobile_app': ['mobile', 'pin'],
            'web_portal': ['web', 'pin'],
            'hybrid': ['fingerprint', 'face', 'card', 'pin'],
        }
        
        self.supported_methods = method_mapping.get(self.machine_type, ['fingerprint'])
    
    def _update_connection_status(self):
        """تحديث حالة الاتصال"""
        if self.last_ping:
            time_diff = timezone.now() - self.last_ping
            if time_diff.total_seconds() > (self.offline_alert_minutes * 60):
                if self.status == 'online':
                    self.status = 'offline'
    
    # Properties
    @property
    def is_online(self):
        """هل الجهاز متصل؟"""
        return self.status == 'online'
    
    @property
    def is_overloaded(self):
        """هل الجهاز محمل بشكل زائد؟"""
        user_percentage = (self.current_users / self.max_users) * 100
        record_percentage = (self.current_records / self.max_records) * 100
        return user_percentage > 90 or record_percentage > 90
    
    @property
    def capacity_status(self):
        """حالة السعة"""
        user_percentage = (self.current_users / self.max_users) * 100
        record_percentage = (self.current_records / self.max_records) * 100
        
        return {
            'users': {
                'current': self.current_users,
                'max': self.max_users,
                'percentage': round(user_percentage, 2)
            },
            'records': {
                'current': self.current_records,
                'max': self.max_records,
                'percentage': round(record_percentage, 2)
            }
        }
    
    @property
    def location_display(self):
        """عرض الموقع الكامل"""
        parts = [self.location_name]
        if self.building:
            parts.append(f"مبنى {self.building}")
        if self.floor:
            parts.append(f"طابق {self.floor}")
        if self.room:
            parts.append(f"غرفة {self.room}")
        
        return " - ".join(parts)
    
    @property
    def connection_info(self):
        """معلومات الاتصال"""
        info = {
            'type': self.get_connection_type_display(),
            'status': self.get_status_display()
        }
        
        if self.ip_address:
            info['ip'] = self.ip_address
        if self.port:
            info['port'] = self.port
        if self.mac_address:
            info['mac'] = self.mac_address
        
        return info
    
    @property
    def uptime_percentage(self):
        """نسبة وقت التشغيل"""
        # حساب نسبة وقت التشغيل خلال آخر 30 يوم
        from Hr.models.attendance.attendance_models import AttendanceMachineLog
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        logs = AttendanceMachineLog.objects.filter(
            machine=self,
            timestamp__gte=thirty_days_ago
        )
        
        if not logs.exists():
            return 0
        
        online_logs = logs.filter(status='online').count()
        total_logs = logs.count()
        
        return round((online_logs / total_logs) * 100, 2) if total_logs > 0 else 0
    
    # Methods
    def ping(self):
        """اختبار الاتصال مع الجهاز"""
        try:
            # هنا يمكن تنفيذ منطق اختبار الاتصال الفعلي
            # مثل ping للشبكة أو استدعاء API
            
            if self.connection_type == 'tcp' and self.ip_address:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.ip_address, self.port or 80))
                sock.close()
                
                if result == 0:
                    self.status = 'online'
                    self.last_ping = timezone.now()
                    self.save(update_fields=['status', 'last_ping'])
                    return True
                else:
                    self.status = 'offline'
                    self.save(update_fields=['status'])
                    return False
            
            # للأنواع الأخرى، افتراض أنها متصلة
            self.status = 'online'
            self.last_ping = timezone.now()
            self.save(update_fields=['status', 'last_ping'])
            return True
            
        except Exception as e:
            self.status = 'error'
            self.save(update_fields=['status'])
            return False
    
    def sync_data(self, force=False):
        """مزامنة البيانات مع الجهاز"""
        if not self.is_active and not force:
            return False
        
        try:
            # هنا يمكن تنفيذ منطق المزامنة الفعلي
            # مثل جلب السجلات من الجهاز أو إرسال بيانات المستخدمين
            
            # تحديث وقت آخر مزامنة
            self.last_sync = timezone.now()
            self.save(update_fields=['last_sync'])
            
            # تسجيل عملية المزامنة
            self.log_activity('sync', 'تمت المزامنة بنجاح')
            
            return True
            
        except Exception as e:
            self.log_activity('sync_error', f'خطأ في المزامنة: {str(e)}')
            return False
    
    def reset_device(self):
        """إعادة تشغيل الجهاز"""
        try:
            # هنا يمكن تنفيذ منطق إعادة التشغيل
            self.status = 'maintenance'
            self.save(update_fields=['status'])
            
            # تسجيل العملية
            self.log_activity('reset', 'تم إعادة تشغيل الجهاز')
            
            return True
            
        except Exception as e:
            self.log_activity('reset_error', f'خطأ في إعادة التشغيل: {str(e)}')
            return False
    
    def clear_data(self, data_type='all'):
        """مسح البيانات من الجهاز"""
        try:
            # هنا يمكن تنفيذ منطق مسح البيانات
            
            if data_type in ['all', 'records']:
                self.current_records = 0
            
            if data_type in ['all', 'users']:
                self.current_users = 0
            
            self.save(update_fields=['current_records', 'current_users'])
            
            # تسجيل العملية
            self.log_activity('clear_data', f'تم مسح البيانات: {data_type}')
            
            return True
            
        except Exception as e:
            self.log_activity('clear_error', f'خطأ في مسح البيانات: {str(e)}')
            return False
    
    def update_firmware(self, firmware_file=None):
        """تحديث البرنامج الثابت"""
        try:
            # هنا يمكن تنفيذ منطق تحديث البرنامج الثابت
            
            self.status = 'maintenance'
            self.save(update_fields=['status'])
            
            # محاكاة عملية التحديث
            self.last_firmware_update = timezone.now()
            self.status = 'online'
            self.save(update_fields=['last_firmware_update', 'status'])
            
            # تسجيل العملية
            self.log_activity('firmware_update', 'تم تحديث البرنامج الثابت')
            
            return True
            
        except Exception as e:
            self.status = 'error'
            self.save(update_fields=['status'])
            self.log_activity('firmware_error', f'خطأ في تحديث البرنامج الثابت: {str(e)}')
            return False
    
    def log_activity(self, activity_type, description):
        """تسجيل نشاط الجهاز"""
        from Hr.models.attendance.attendance_models import AttendanceMachineLog
        
        AttendanceMachineLog.objects.create(
            machine=self,
            activity_type=activity_type,
            description=description,
            status=self.status,
            timestamp=timezone.now()
        )
    
    def get_daily_records_count(self, date_obj=None):
        """عدد السجلات اليومية"""
        if not date_obj:
            date_obj = timezone.now().date()
        
        from Hr.models.attendance.attendance_models import AttendanceRecordEnhanced
        
        return AttendanceRecordEnhanced.objects.filter(
            models.Q(check_in_machine=self) | models.Q(check_out_machine=self),
            date=date_obj
        ).count()
    
    def get_monthly_stats(self, year=None, month=None):
        """إحصائيات شهرية للجهاز"""
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month
        
        from Hr.models.attendance.attendance_models import AttendanceRecordEnhanced, AttendanceMachineLog
        
        # سجلات الحضور
        records = AttendanceRecordEnhanced.objects.filter(
            models.Q(check_in_machine=self) | models.Q(check_out_machine=self),
            date__year=year,
            date__month=month
        )
        
        # سجلات النشاط
        logs = AttendanceMachineLog.objects.filter(
            machine=self,
            timestamp__year=year,
            timestamp__month=month
        )
        
        return {
            'total_records': records.count(),
            'check_in_records': records.filter(check_in_machine=self).count(),
            'check_out_records': records.filter(check_out_machine=self).count(),
            'unique_employees': records.values('employee').distinct().count(),
            'total_activities': logs.count(),
            'sync_activities': logs.filter(activity_type='sync').count(),
            'error_activities': logs.filter(activity_type__contains='error').count(),
            'uptime_percentage': self.uptime_percentage,
        }
    
    @classmethod
    def get_online_machines(cls):
        """الحصول على الأجهزة المتصلة"""
        return cls.objects.filter(status='online', is_active=True)
    
    @classmethod
    def get_offline_machines(cls):
        """الحصول على الأجهزة غير المتصلة"""
        return cls.objects.filter(status='offline', is_active=True)
    
    @classmethod
    def get_machines_by_location(cls, location_name):
        """الحصول على الأجهزة حسب الموقع"""
        return cls.objects.filter(
            location_name__icontains=location_name,
            is_active=True
        )
    
    @classmethod
    def get_machines_needing_maintenance(cls):
        """الأجهزة التي تحتاج صيانة"""
        today = timezone.now().date()
        
        return cls.objects.filter(
            models.Q(next_maintenance__lte=today) |
            models.Q(warranty_expiry__lte=today + timedelta(days=30)),
            is_active=True
        )
    
    @classmethod
    def get_overloaded_machines(cls):
        """الأجهزة المحملة بشكل زائد"""
        machines = []
        for machine in cls.objects.filter(is_active=True):
            if machine.is_overloaded:
                machines.append(machine)
        return machines


class AttendanceMachineLog(models.Model):
    """سجل أنشطة أجهزة الحضور"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    machine = models.ForeignKey(
        AttendanceMachineEnhanced,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name=_("الجهاز")
    )
    
    ACTIVITY_TYPES = [
        ('ping', _('اختبار اتصال')),
        ('sync', _('مزامنة')),
        ('sync_error', _('خطأ مزامنة')),
        ('reset', _('إعادة تشغيل')),
        ('reset_error', _('خطأ إعادة تشغيل')),
        ('clear_data', _('مسح البيانات')),
        ('clear_error', _('خطأ مسح البيانات')),
        ('firmware_update', _('تحديث البرنامج الثابت')),
        ('firmware_error', _('خطأ تحديث البرنامج الثابت')),
        ('maintenance', _('صيانة')),
        ('configuration', _('تكوين')),
        ('status_change', _('تغيير الحالة')),
        ('user_add', _('إضافة مستخدم')),
        ('user_delete', _('حذف مستخدم')),
        ('record_download', _('تحميل السجلات')),
        ('error', _('خطأ عام')),
    ]
    
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPES,
        verbose_name=_("نوع النشاط")
    )
    
    description = models.TextField(
        verbose_name=_("الوصف")
    )
    
    status = models.CharField(
        max_length=20,
        verbose_name=_("الحالة")
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("الوقت")
    )
    
    # Additional Data
    data = models.JSONField(
        default=dict,
        verbose_name=_("بيانات إضافية")
    )
    
    # User Information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم")
    )
    
    class Meta:
        verbose_name = _("سجل نشاط جهاز الحضور")
        verbose_name_plural = _("سجلات أنشطة أجهزة الحضور")
        db_table = 'hrms_attendance_machine_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['machine', 'timestamp']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['status']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.machine.name} - {self.get_activity_type_display()} ({self.timestamp})"


class AttendanceMachineGroup(models.Model):
    """مجموعة أجهزة الحضور"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم المجموعة")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف")
    )
    
    machines = models.ManyToManyField(
        AttendanceMachineEnhanced,
        related_name='machine_groups',
        verbose_name=_("الأجهزة")
    )
    
    # Group Settings
    sync_all_together = models.BooleanField(
        default=False,
        verbose_name=_("مزامنة جماعية")
    )
    
    shared_configuration = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات مشتركة")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    # System Fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        verbose_name = _("مجموعة أجهزة حضور")
        verbose_name_plural = _("مجموعات أجهزة الحضور")
        db_table = 'hrms_attendance_machine_group'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def sync_all_machines(self):
        """مزامنة جميع الأجهزة في المجموعة"""
        results = []
        for machine in self.machines.filter(is_active=True):
            result = machine.sync_data()
            results.append({
                'machine': machine.name,
                'success': result
            })
        return results
    
    def ping_all_machines(self):
        """اختبار اتصال جميع الأجهزة"""
        results = []
        for machine in self.machines.filter(is_active=True):
            result = machine.ping()
            results.append({
                'machine': machine.name,
                'online': result
            })
        return results
    
    @property
    def machines_count(self):
        """عدد الأجهزة في المجموعة"""
        return self.machines.count()
    
    @property
    def online_machines_count(self):
        """عدد الأجهزة المتصلة"""
        return self.machines.filter(status='online').count()
    
    @property
    def group_status(self):
        """حالة المجموعة"""
        total = self.machines_count
        online = self.online_machines_count
        
        if total == 0:
            return 'empty'
        elif online == total:
            return 'all_online'
        elif online == 0:
            return 'all_offline'
        else:
            return 'partial_online'