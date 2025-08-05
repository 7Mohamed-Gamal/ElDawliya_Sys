"""
Attendance Machine Models for HRMS
Handles attendance machines and device management
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta


class AttendanceMachine(models.Model):
    """
    نموذج جهاز الحضور - إدارة أجهزة تسجيل الحضور والانصراف
    """
    MACHINE_TYPES = [
        ('fingerprint', _('بصمة الإصبع')),
        ('face_recognition', _('التعرف على الوجه')),
        ('card_reader', _('قارئ البطاقات')),
        ('pin_code', _('رمز PIN')),
        ('hybrid', _('مختلط')),
    ]
    
    STATUS_CHOICES = [
        ('online', _('متصل')),
        ('offline', _('غير متصل')),
        ('maintenance', _('صيانة')),
        ('error', _('خطأ')),
        ('disabled', _('معطل')),
    ]
    
    CONNECTION_TYPES = [
        ('tcp_ip', _('TCP/IP')),
        ('usb', _('USB')),
        ('serial', _('Serial')),
        ('wifi', _('WiFi')),
        ('ethernet', _('Ethernet')),
    ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name=_('المعرف')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('اسم الجهاز'),
        help_text=_('مثال: جهاز الحضور - المدخل الرئيسي')
    )
    
    name_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('الاسم بالإنجليزية'),
        help_text=_('Main Entrance Attendance Machine')
    )
    
    machine_type = models.CharField(
        max_length=20,
        choices=MACHINE_TYPES,
        default='fingerprint',
        verbose_name=_('نوع الجهاز')
    )
    
    brand = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('الماركة'),
        help_text=_('مثال: ZKTeco, Hikvision')
    )
    
    model = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('الموديل'),
        help_text=_('رقم موديل الجهاز')
    )
    
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('الرقم التسلسلي'),
        help_text=_('الرقم التسلسلي للجهاز')
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('عنوان IP'),
        help_text=_('عنوان IP للجهاز (للاتصال الشبكي)')
    )
    
    port = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=4370,
        verbose_name=_('المنفذ'),
        help_text=_('منفذ الاتصال (افتراضي: 4370)')
    )
    
    connection_type = models.CharField(
        max_length=20,
        choices=CONNECTION_TYPES,
        default='tcp_ip',
        verbose_name=_('نوع الاتصال')
    )
    
    location = models.CharField(
        max_length=200,
        default='غير محدد',
        verbose_name=_('الموقع'),
        help_text=_('موقع الجهاز (مثال: المدخل الرئيسي، الطابق الثاني)')
    )
    
    branch = models.ForeignKey(
        'Hr.Branch',
        on_delete=models.CASCADE,
        related_name='attendance_machines',
        null=True,
        blank=True,
        verbose_name=_('الفرع')
    )
    
    department = models.ForeignKey(
        'Hr.Department',
        on_delete=models.SET_NULL,
        related_name='attendance_machines',
        null=True,
        blank=True,
        verbose_name=_('القسم'),
        help_text=_('القسم المخصص له الجهاز (اختياري)')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offline',
        verbose_name=_('الحالة')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل الجهاز نشط؟')
    )
    
    is_entry_device = models.BooleanField(
        default=True,
        verbose_name=_('جهاز دخول'),
        help_text=_('هل يستخدم لتسجيل الدخول؟')
    )
    
    is_exit_device = models.BooleanField(
        default=True,
        verbose_name=_('جهاز خروج'),
        help_text=_('هل يستخدم لتسجيل الخروج؟')
    )
    
    max_users = models.PositiveIntegerField(
        default=1000,
        verbose_name=_('الحد الأقصى للمستخدمين'),
        help_text=_('الحد الأقصى لعدد المستخدمين المسجلين')
    )
    
    max_records = models.PositiveIntegerField(
        default=100000,
        verbose_name=_('الحد الأقصى للسجلات'),
        help_text=_('الحد الأقصى لعدد سجلات الحضور')
    )
    
    firmware_version = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('إصدار البرنامج الثابت'),
        help_text=_('إصدار firmware الجهاز')
    )
    
    last_sync_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('آخر مزامنة'),
        help_text=_('آخر وقت مزامنة مع الجهاز')
    )
    
    last_ping_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('آخر ping'),
        help_text=_('آخر وقت فحص اتصال')
    )
    
    sync_interval_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name=_('فترة المزامنة (دقيقة)'),
        help_text=_('فترة المزامنة التلقائية بالدقائق')
    )
    
    timezone = models.CharField(
        max_length=50,
        default='Asia/Riyadh',
        verbose_name=_('المنطقة الزمنية'),
        help_text=_('المنطقة الزمنية للجهاز')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات'),
        help_text=_('ملاحظات إضافية حول الجهاز')
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
        verbose_name = _('جهاز حضور')
        verbose_name_plural = _('أجهزة الحضور')
        ordering = ['location', 'name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
            models.Index(fields=['branch']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['serial_number']),
        ]

    def __str__(self):
        return f"{self.name} ({self.location})"

    def clean(self):
        """التحقق من صحة البيانات"""
        if self.connection_type in ['tcp_ip', 'wifi', 'ethernet']:
            if not self.ip_address:
                raise ValidationError(_('عنوان IP مطلوب لهذا النوع من الاتصال'))
        
        if self.port and (self.port < 1 or self.port > 65535):
            raise ValidationError(_('رقم المنفذ يجب أن يكون بين 1 و 65535'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_online(self):
        """هل الجهاز متصل؟"""
        return self.status == 'online'

    @property
    def connection_string(self):
        """سلسلة الاتصال بالجهاز"""
        if self.connection_type in ['tcp_ip', 'wifi', 'ethernet']:
            return f"{self.ip_address}:{self.port}"
        return self.serial_number

    @property
    def last_sync_ago(self):
        """منذ متى آخر مزامنة؟"""
        if not self.last_sync_time:
            return None
        
        now = timezone.now()
        diff = now - self.last_sync_time
        
        if diff.days > 0:
            return f"{diff.days} يوم"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ساعة"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} دقيقة"
        else:
            return "الآن"

    @property
    def needs_sync(self):
        """هل يحتاج الجهاز للمزامنة؟"""
        if not self.last_sync_time:
            return True
        
        now = timezone.now()
        sync_threshold = now - timedelta(minutes=self.sync_interval_minutes)
        return self.last_sync_time < sync_threshold

    def update_status(self, new_status):
        """تحديث حالة الجهاز"""
        self.status = new_status
        self.last_ping_time = timezone.now()
        self.save(update_fields=['status', 'last_ping_time'])

    def mark_sync_completed(self):
        """تسجيل اكتمال المزامنة"""
        self.last_sync_time = timezone.now()
        self.save(update_fields=['last_sync_time'])

    def test_connection(self):
        """اختبار الاتصال بالجهاز"""
        # سيتم تنفيذ منطق اختبار الاتصال هنا
        # يمكن استخدام مكتبة مثل pyzk للاتصال بأجهزة ZKTeco
        try:
            # منطق اختبار الاتصال
            self.update_status('online')
            return True
        except Exception as e:
            self.update_status('offline')
            return False

    @classmethod
    def get_online_machines(cls):
        """الحصول على الأجهزة المتصلة"""
        return cls.objects.filter(status='online', is_active=True)

    @classmethod
    def get_machines_needing_sync(cls):
        """الحصول على الأجهزة التي تحتاج للمزامنة"""
        now = timezone.now()
        machines = cls.objects.filter(is_active=True, status='online')
        
        needing_sync = []
        for machine in machines:
            if machine.needs_sync:
                needing_sync.append(machine)
        
        return needing_sync
    
    def get_status_display_with_icon(self):
        """Get status with visual indicator"""
        status_icons = {
            'online': '🟢 متصل',
            'offline': '🔴 غير متصل',
            'maintenance': '🔧 صيانة',
            'error': '⚠️ خطأ',
            'disabled': '⚫ معطل',
        }
        return status_icons.get(self.status, self.get_status_display())
    
    def get_connection_health_score(self):
        """Calculate connection health score"""
        score = 100
        
        # Deduct points for offline status
        if self.status == 'offline':
            score -= 50
        elif self.status == 'error':
            score -= 30
        elif self.status == 'maintenance':
            score -= 20
        
        # Deduct points for old sync
        if self.last_sync_time:
            hours_since_sync = (timezone.now() - self.last_sync_time).total_seconds() / 3600
            if hours_since_sync > 24:
                score -= 30
            elif hours_since_sync > 12:
                score -= 15
            elif hours_since_sync > 6:
                score -= 10
        else:
            score -= 40  # Never synced
        
        # Deduct points for old ping
        if self.last_ping_time:
            hours_since_ping = (timezone.now() - self.last_ping_time).total_seconds() / 3600
            if hours_since_ping > 1:
                score -= 20
        else:
            score -= 30  # Never pinged
        
        return max(0, min(100, score))
    
    def get_machine_statistics(self):
        """Get comprehensive machine statistics"""
        from django.db.models import Count
        
        stats = {
            'total_users': self.machine_users.count(),
            'enrolled_users': self.machine_users.filter(is_enrolled=True).count(),
            'active_users': self.machine_users.filter(is_active=True).count(),
            'fingerprint_users': self.machine_users.filter(fingerprint_templates__gt=0).count(),
            'face_users': self.machine_users.filter(face_template_exists=True).count(),
            'card_users': self.machine_users.exclude(card_number='').count(),
            'pin_users': self.machine_users.exclude(pin_code='').count(),
        }
        
        # Get attendance records count for today
        from datetime import date
        today = date.today()
        stats['today_records'] = getattr(self, 'attendance_records', self.__class__.objects.none()).filter(
            date=today
        ).count()
        
        return stats
    
    @classmethod
    def get_fleet_status(cls):
        """Get status of all machines"""
        machines = cls.objects.filter(is_active=True)
        
        status_summary = {
            'total_machines': machines.count(),
            'online': machines.filter(status='online').count(),
            'offline': machines.filter(status='offline').count(),
            'maintenance': machines.filter(status='maintenance').count(),
            'error': machines.filter(status='error').count(),
            'disabled': machines.filter(status='disabled').count(),
        }
        
        status_summary['health_percentage'] = (
            status_summary['online'] / status_summary['total_machines'] * 100
        ) if status_summary['total_machines'] > 0 else 0
        
        return status_summary


class MachineUser(models.Model):
    """
    نموذج مستخدم الجهاز - ربط الموظفين بأجهزة الحضور
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name=_('المعرف')
    )
    
    machine = models.ForeignKey(
        AttendanceMachine,
        on_delete=models.CASCADE,
        related_name='machine_users',
        verbose_name=_('الجهاز')
    )
    
    employee = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.CASCADE,
        related_name='machine_users',
        verbose_name=_('الموظف')
    )
    
    user_id = models.CharField(
        max_length=20,
        verbose_name=_('معرف المستخدم في الجهاز'),
        help_text=_('معرف الموظف في جهاز الحضور')
    )
    
    is_enrolled = models.BooleanField(
        default=False,
        verbose_name=_('مسجل'),
        help_text=_('هل تم تسجيل الموظف في الجهاز؟')
    )
    
    enrollment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ التسجيل'),
        help_text=_('تاريخ تسجيل الموظف في الجهاز')
    )
    
    fingerprint_templates = models.PositiveIntegerField(
        default=0,
        verbose_name=_('عدد قوالب البصمة'),
        help_text=_('عدد قوالب البصمة المسجلة')
    )
    
    face_template_exists = models.BooleanField(
        default=False,
        verbose_name=_('قالب الوجه موجود'),
        help_text=_('هل يوجد قالب للوجه؟')
    )
    
    card_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('رقم البطاقة'),
        help_text=_('رقم بطاقة الموظف')
    )
    
    pin_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_('رمز PIN'),
        help_text=_('رمز PIN للموظف')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل المستخدم نشط في الجهاز؟')
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
        verbose_name = _('مستخدم جهاز')
        verbose_name_plural = _('مستخدمو الأجهزة')
        unique_together = ['machine', 'employee']
        indexes = [
            models.Index(fields=['machine', 'user_id']),
            models.Index(fields=['employee']),
            models.Index(fields=['is_enrolled']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.machine} ({self.user_id})"

    def enroll_user(self):
        """تسجيل المستخدم في الجهاز"""
        # سيتم تنفيذ منطق التسجيل هنا
        try:
            # منطق تسجيل المستخدم في الجهاز
            self.is_enrolled = True
            self.enrollment_date = timezone.now()
            self.save()
            return True
        except Exception as e:
            return False

    def remove_user(self):
        """إزالة المستخدم من الجهاز"""
        try:
            # منطق إزالة المستخدم من الجهاز
            self.is_enrolled = False
            self.enrollment_date = None
            self.fingerprint_templates = 0
            self.face_template_exists = False
            self.save()
            return True
        except Exception as e:
            return False

    @classmethod
    def sync_users_to_machine(cls, machine):
        """مزامنة جميع المستخدمين إلى الجهاز"""
        machine_users = cls.objects.filter(machine=machine, is_active=True)
        success_count = 0
        
        for machine_user in machine_users:
            if machine_user.enroll_user():
                success_count += 1
        
        return success_count


