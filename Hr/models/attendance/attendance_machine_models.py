"""
Attendance Machine Models for HRMS
Handles ZK attendance machines and device management
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class AttendanceMachine(models.Model):
    """
    Attendance Machine model for managing ZK and other attendance devices
    Handles device configuration, connectivity, and data synchronization
    """
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الجهاز")
    )
    
    device_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("معرف الجهاز")
    )
    
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("الرقم التسلسلي")
    )
    
    model = models.CharField(
        max_length=100,
        verbose_name=_("موديل الجهاز")
    )
    
    manufacturer = models.CharField(
        max_length=100,
        default="ZKTeco",
        verbose_name=_("الشركة المصنعة")
    )
    
    # Location Information
    branch = models.ForeignKey(
        'Hr.Branch',
        on_delete=models.CASCADE,
        related_name='attendance_machines',
        verbose_name=_("الفرع")
    )
    
    location_description = models.CharField(
        max_length=200,
        verbose_name=_("وصف الموقع"),
        help_text=_("مثل: المدخل الرئيسي، مدخل الموظفين، إلخ")
    )
    
    floor = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("الطابق")
    )
    
    # Network Configuration
    ip_address = models.GenericIPAddressField(
        verbose_name=_("عنوان IP"),
        validators=[
            RegexValidator(
                regex=r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
                message=_("عنوان IP غير صحيح")
            )
        ]
    )
    
    port = models.PositiveIntegerField(
        default=4370,
        verbose_name=_("رقم المنفذ")
    )
    
    password = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("كلمة مرور الجهاز")
    )
    
    # Device Capabilities
    DEVICE_TYPES = [
        ('fingerprint', _('بصمة الإصبع')),
        ('face', _('التعرف على الوجه')),
        ('card', _('بطاقة')),
        ('password', _('كلمة مرور')),
        ('mixed', _('مختلط')),
    ]
    
    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_TYPES,
        verbose_name=_("نوع الجهاز")
    )
    
    supports_fingerprint = models.BooleanField(
        default=True,
        verbose_name=_("يدعم بصمة الإصبع")
    )
    
    supports_face_recognition = models.BooleanField(
        default=False,
        verbose_name=_("يدعم التعرف على الوجه")
    )
    
    supports_card = models.BooleanField(
        default=False,
        verbose_name=_("يدعم البطاقة")
    )
    
    supports_password = models.BooleanField(
        default=False,
        verbose_name=_("يدعم كلمة المرور")
    )
    
    # Capacity Information
    max_users = models.PositiveIntegerField(
        default=1000,
        verbose_name=_("الحد الأقصى للمستخدمين")
    )
    
    max_fingerprints = models.PositiveIntegerField(
        default=2000,
        verbose_name=_("الحد الأقصى للبصمات")
    )
    
    max_records = models.PositiveIntegerField(
        default=100000,
        verbose_name=_("الحد الأقصى للسجلات")
    )
    
    current_users = models.PositiveIntegerField(
        default=0,
        verbose_name=_("عدد المستخدمين الحالي")
    )
    
    current_records = models.PositiveIntegerField(
        default=0,
        verbose_name=_("عدد السجلات الحالي")
    )
    
    # Synchronization Settings
    auto_sync_enabled = models.BooleanField(
        default=True,
        verbose_name=_("المزامنة التلقائية مفعلة")
    )
    
    sync_interval_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name=_("فترة المزامنة (دقائق)")
    )
    
    last_sync_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("آخر وقت مزامنة")
    )
    
    last_sync_status = models.CharField(
        max_length=20,
        choices=[
            ('success', _('نجحت')),
            ('failed', _('فشلت')),
            ('partial', _('جزئية')),
            ('pending', _('معلقة')),
        ],
        null=True,
        blank=True,
        verbose_name=_("حالة آخر مزامنة")
    )
    
    # Device Status
    STATUS_CHOICES = [
        ('online', _('متصل')),
        ('offline', _('غير متصل')),
        ('error', _('خطأ')),
        ('maintenance', _('صيانة')),
        ('disabled', _('معطل')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offline',
        verbose_name=_("حالة الجهاز")
    )
    
    last_online_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("آخر وقت اتصال")
    )
    
    # Device Settings
    device_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات الجهاز"),
        help_text=_("إعدادات خاصة بالجهاز")
    )
    
    # Firmware Information
    firmware_version = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("إصدار البرنامج الثابت")
    )
    
    platform = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("المنصة")
    )
    
    # Installation Information
    installation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التركيب")
    )
    
    warranty_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء الضمان")
    )
    
    # Maintenance Information
    last_maintenance_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ آخر صيانة")
    )
    
    next_maintenance_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الصيانة القادمة")
    )
    
    maintenance_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات الصيانة")
    )
    
    # Access Control
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_entry_device = models.BooleanField(
        default=True,
        verbose_name=_("جهاز دخول"),
        help_text=_("هل يستخدم هذا الجهاز لتسجيل الدخول؟")
    )
    
    is_exit_device = models.BooleanField(
        default=True,
        verbose_name=_("جهاز خروج"),
        help_text=_("هل يستخدم هذا الجهاز لتسجيل الخروج؟")
    )
    
    # Metadata
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
    
    class Meta:
        verbose_name = _("جهاز حضور")
        verbose_name_plural = _("أجهزة الحضور")
        db_table = 'hrms_attendance_machine'
        ordering = ['branch', 'name']
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['status']),
            models.Index(fields=['branch']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.ip_address})"
    
    def clean(self):
        """Validate attendance machine data"""
        super().clean()
        
        # Validate port range
        if self.port < 1 or self.port > 65535:
            raise ValidationError(_("رقم المنفذ يجب أن يكون بين 1 و 65535"))
        
        # Validate capacity
        if self.current_users > self.max_users:
            raise ValidationError(_("عدد المستخدمين الحالي لا يمكن أن يتجاوز الحد الأقصى"))
        
        if self.current_records > self.max_records:
            raise ValidationError(_("عدد السجلات الحالي لا يمكن أن يتجاوز الحد الأقصى"))
    
    @property
    def is_online(self):
        """Check if device is online"""
        return self.status == 'online'
    
    @property
    def users_capacity_percentage(self):
        """Calculate users capacity percentage"""
        if self.max_users > 0:
            return round((self.current_users / self.max_users) * 100, 2)
        return 0
    
    @property
    def records_capacity_percentage(self):
        """Calculate records capacity percentage"""
        if self.max_records > 0:
            return round((self.current_records / self.max_records) * 100, 2)
        return 0
    
    @property
    def needs_maintenance(self):
        """Check if device needs maintenance"""
        from datetime import date
        if self.next_maintenance_date:
            return date.today() >= self.next_maintenance_date
        return False
    
    @property
    def warranty_expired(self):
        """Check if warranty has expired"""
        from datetime import date
        if self.warranty_expiry_date:
            return date.today() > self.warranty_expiry_date
        return False
    
    def test_connection(self):
        """Test connection to the device"""
        # This would implement actual device connection testing
        # For now, return a placeholder
        try:
            # Implement ZK device connection test here
            # Example: ping device, try to connect via SDK
            return True, _("الاتصال ناجح")
        except Exception as e:
            return False, str(e)
    
    def sync_users(self):
        """Synchronize users with the device"""
        # This would implement user synchronization
        # For now, return a placeholder
        try:
            # Implement user sync logic here
            return True, _("تم مزامنة المستخدمين بنجاح")
        except Exception as e:
            return False, str(e)
    
    def fetch_attendance_records(self):
        """Fetch attendance records from the device"""
        # This would implement attendance record fetching
        # For now, return a placeholder
        try:
            # Implement attendance record fetching here
            return True, _("تم جلب سجلات الحضور بنجاح")
        except Exception as e:
            return False, str(e)
    
    def clear_device_records(self):
        """Clear all records from the device"""
        # This would implement record clearing
        # For now, return a placeholder
        try:
            # Implement record clearing here
            self.current_records = 0
            self.save()
            return True, _("تم مسح السجلات بنجاح")
        except Exception as e:
            return False, str(e)
    
    def update_device_time(self):
        """Update device time to match server time"""
        # This would implement time synchronization
        # For now, return a placeholder
        try:
            # Implement time sync here
            return True, _("تم تحديث وقت الجهاز بنجاح")
        except Exception as e:
            return False, str(e)
    
    def get_device_info(self):
        """Get device information"""
        # This would implement device info retrieval
        # For now, return basic info
        return {
            'name': self.name,
            'model': self.model,
            'serial_number': self.serial_number,
            'firmware_version': self.firmware_version,
            'status': self.get_status_display(),
            'users_count': self.current_users,
            'records_count': self.current_records,
            'last_sync': self.last_sync_time,
        }
    
    def save(self, *args, **kwargs):
        """Override save to set default settings"""
        # Set default device settings
        if not self.device_settings:
            self.device_settings = {
                'voice_enabled': True,
                'auto_poweroff_time': 0,  # 0 means disabled
                'lock_control_time': 5,
                'door_sensor_enabled': False,
                'anti_passback_enabled': False,
                'wiegand_enabled': False,
                'backup_time': '02:00',  # Daily backup time
                'log_stamp_enabled': True,
            }
        
        super().save(*args, **kwargs)
