"""
Employee File Management Models for HRMS
Enhanced file management system with advanced features
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os
import uuid
import hashlib
from datetime import date, timedelta


def employee_file_upload_path(instance, filename):
    """Generate upload path for employee files"""
    # Create path: employee_files/employee_id/year/month/filename
    return f'employee_files/{instance.employee.id}/{timezone.now().year}/{timezone.now().month}/{filename}'


class EmployeeFileCategory(models.Model):
    """
    File categories for better organization
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("اسم الفئة")
    )
    
    name_en = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الاسم بالإنجليزية")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف")
    )
    
    icon = models.CharField(
        max_length=50,
        default='📁',
        verbose_name=_("الأيقونة")
    )
    
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name=_("اللون"),
        help_text=_("كود اللون بصيغة hex")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("ترتيب العرض")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    class Meta:
        verbose_name = _("فئة الملفات")
        verbose_name_plural = _("فئات الملفات")
        db_table = 'hrms_employee_file_category'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class EmployeeFileEnhanced(models.Model):
    """
    Enhanced Employee File model with advanced features
    """
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Relationship to Employee
    employee = models.ForeignKey(
        'EmployeeEnhanced',
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_("الموظف")
    )
    
    # File Information
    title = models.CharField(
        max_length=200,
        verbose_name=_("عنوان الملف")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف الملف")
    )
    
    file = models.FileField(
        upload_to=employee_file_upload_path,
        verbose_name=_("الملف"),
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'pdf', 'doc', 'docx', 'txt', 'rtf',
                    'jpg', 'jpeg', 'png', 'gif', 'bmp',
                    'xls', 'xlsx', 'csv',
                    'ppt', 'pptx',
                    'zip', 'rar', '7z'
                ]
            )
        ]
    )
    
    # File Metadata
    original_filename = models.CharField(
        max_length=255,
        verbose_name=_("اسم الملف الأصلي")
    )
    
    file_size = models.PositiveIntegerField(
        verbose_name=_("حجم الملف (بايت)")
    )
    
    mime_type = models.CharField(
        max_length=100,
        verbose_name=_("نوع الملف")
    )
    
    file_hash = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("هاش الملف"),
        help_text=_("SHA-256 hash للتحقق من سلامة الملف")
    )
    
    # Categorization
    category = models.ForeignKey(
        EmployeeFileCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files',
        verbose_name=_("الفئة")
    )
    
    tags = models.JSONField(
        default=list,
        verbose_name=_("العلامات"),
        help_text=_("علامات للبحث والتصنيف")
    )
    
    # Access Control
    ACCESS_LEVELS = [
        ('public', _('عام - يمكن للجميع الوصول')),
        ('internal', _('داخلي - الموظفون والإدارة')),
        ('confidential', _('سري - الإدارة العليا فقط')),
        ('restricted', _('مقيد - أشخاص محددون فقط')),
        ('personal', _('شخصي - الموظف فقط')),
    ]
    
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVELS,
        default='internal',
        verbose_name=_("مستوى الوصول")
    )
    
    is_confidential = models.BooleanField(
        default=False,
        verbose_name=_("ملف سري")
    )
    
    # Version Control
    version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name=_("الإصدار")
    )
    
    parent_file = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='versions',
        verbose_name=_("الملف الأصلي")
    )
    
    # Status and Workflow
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('pending_review', _('في انتظار المراجعة')),
        ('approved', _('معتمد')),
        ('rejected', _('مرفوض')),
        ('archived', _('مؤرشف')),
        ('deleted', _('محذوف')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_review',
        verbose_name=_("الحالة")
    )
    
    # Expiry and Renewal
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء الصلاحية")
    )
    
    renewal_required = models.BooleanField(
        default=False,
        verbose_name=_("يتطلب تجديد")
    )
    
    reminder_days = models.PositiveIntegerField(
        default=30,
        verbose_name=_("تذكير قبل (أيام)")
    )
    
    # Security and Encryption
    is_encrypted = models.BooleanField(
        default=False,
        verbose_name=_("مشفر")
    )
    
    encryption_key_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("معرف مفتاح التشفير")
    )
    
    # Download and Access Tracking
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("عدد مرات التحميل")
    )
    
    last_accessed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("آخر وصول")
    )
    
    # Approval Workflow
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_files',
        verbose_name=_("معتمد بواسطة")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الاعتماد")
    )
    
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("سبب الرفض")
    )
    
    # Additional Metadata
    keywords = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("كلمات مفتاحية"),
        help_text=_("كلمات مفتاحية للبحث")
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # System Fields
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_files',
        verbose_name=_("رفع بواسطة")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الرفع")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("ملف موظف")
        verbose_name_plural = _("ملفات الموظفين")
        db_table = 'hrms_employee_file_enhanced'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'category']),
            models.Index(fields=['status']),
            models.Index(fields=['access_level']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"
    
    def clean(self):
        """Validate file data"""
        super().clean()
        
        # Validate file size (max 100MB)
        if self.file and hasattr(self.file, 'size'):
            max_size = 100 * 1024 * 1024  # 100MB
            if self.file.size > max_size:
                raise ValidationError(_("حجم الملف لا يمكن أن يتجاوز 100 ميجابايت"))
        
        # Validate expiry date
        if self.expiry_date and self.expiry_date <= date.today():
            raise ValidationError(_("تاريخ انتهاء الصلاحية يجب أن يكون في المستقبل"))
    
    def save(self, *args, **kwargs):
        """Override save to set metadata"""
        if self.file:
            # Set original filename
            if not self.original_filename:
                self.original_filename = os.path.basename(self.file.name)
            
            # Set file size
            if hasattr(self.file, 'size'):
                self.file_size = self.file.size
            
            # Set MIME type
            import mimetypes
            mime_type, _ = mimetypes.guess_type(self.file.name)
            if mime_type:
                self.mime_type = mime_type
            
            # Calculate file hash
            if not self.file_hash:
                self.file_hash = self._calculate_file_hash()
        
        super().save(*args, **kwargs)
    
    def _calculate_file_hash(self):
        """Calculate SHA-256 hash of the file"""
        if self.file:
            hash_sha256 = hashlib.sha256()
            for chunk in self.file.chunks():
                hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        return None
    
    # Properties
    @property
    def file_extension(self):
        """Get file extension"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return None
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def is_expired(self):
        """Check if file is expired"""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.expiry_date:
            delta = self.expiry_date - date.today()
            return delta.days
        return None
    
    @property
    def needs_renewal_reminder(self):
        """Check if file needs renewal reminder"""
        if self.expiry_date and self.renewal_required:
            days_until_expiry = self.days_until_expiry
            if days_until_expiry is not None:
                return days_until_expiry <= self.reminder_days
        return False
    
    # Methods
    def get_file_type_icon(self):
        """Get file type icon"""
        extension = self.file_extension
        if not extension:
            return '📄'
        
        icons = {
            '.pdf': '📄',
            '.doc': '📝', '.docx': '📝',
            '.txt': '📃', '.rtf': '📃',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.bmp': '🖼️',
            '.xls': '📊', '.xlsx': '📊', '.csv': '📊',
            '.ppt': '📊', '.pptx': '📊',
            '.zip': '🗜️', '.rar': '🗜️', '.7z': '🗜️',
        }
        return icons.get(extension, '📄')
    
    def get_status_display_with_icon(self):
        """Get status with icon"""
        status_icons = {
            'draft': '✏️ مسودة',
            'pending_review': '⏳ في انتظار المراجعة',
            'approved': '✅ معتمد',
            'rejected': '❌ مرفوض',
            'archived': '📦 مؤرشف',
            'deleted': '🗑️ محذوف',
        }
        return status_icons.get(self.status, self.get_status_display())
    
    def get_access_level_display_with_icon(self):
        """Get access level with icon"""
        access_icons = {
            'public': '🌐 عام',
            'internal': '🏢 داخلي',
            'confidential': '🔒 سري',
            'restricted': '🚨 مقيد',
            'personal': '👤 شخصي',
        }
        return access_icons.get(self.access_level, self.get_access_level_display())
    
    def approve(self, approved_by_user, notes=None):
        """Approve the file"""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        if notes:
            self.notes = f"{self.notes or ''}\nملاحظات الاعتماد: {notes}"
        self.save()
    
    def reject(self, reason):
        """Reject the file"""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.save()
    
    def archive(self):
        """Archive the file"""
        self.status = 'archived'
        self.save()
    
    def track_access(self, user=None):
        """Track file access"""
        self.download_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['download_count', 'last_accessed'])
    
    def create_new_version(self, new_file, uploaded_by, version=None):
        """Create a new version of this file"""
        if not version:
            # Auto-increment version
            current_version = float(self.version)
            version = str(current_version + 0.1)
        
        new_file_obj = EmployeeFileEnhanced(
            employee=self.employee,
            title=self.title,
            description=self.description,
            file=new_file,
            category=self.category,
            tags=self.tags.copy(),
            access_level=self.access_level,
            is_confidential=self.is_confidential,
            version=version,
            parent_file=self,
            expiry_date=self.expiry_date,
            renewal_required=self.renewal_required,
            reminder_days=self.reminder_days,
            uploaded_by=uploaded_by
        )
        new_file_obj.save()
        
        # Archive the current version
        self.archive()
        
        return new_file_obj
    
    def can_be_accessed_by(self, user):
        """Check if user can access this file"""
        # System admin can access everything
        if user.is_superuser:
            return True
        
        # Check based on access level
        if self.access_level == 'public':
            return True
        elif self.access_level == 'personal':
            return self.employee.user == user
        elif self.access_level == 'internal':
            # Internal users can access
            return hasattr(user, 'employee_profile')
        elif self.access_level == 'confidential':
            # Only HR and managers
            return (hasattr(user, 'profile') and 
                   user.profile.department in ['hr', 'management'])
        elif self.access_level == 'restricted':
            # Only specific users (can be extended)
            return user == self.uploaded_by or user == self.approved_by
        
        return False
    
    def get_file_summary(self):
        """Get comprehensive file summary"""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'file_info': {
                'name': self.original_filename,
                'size': f"{self.file_size_mb} MB",
                'type': self.mime_type,
                'extension': self.file_extension,
                'icon': self.get_file_type_icon()
            },
            'status': {
                'current': self.get_status_display_with_icon(),
                'access_level': self.get_access_level_display_with_icon(),
                'is_confidential': self.is_confidential,
                'is_encrypted': self.is_encrypted
            },
            'metadata': {
                'version': self.version,
                'category': self.category.name if self.category else None,
                'tags': self.tags,
                'keywords': self.keywords
            },
            'dates': {
                'created': self.created_at,
                'updated': self.updated_at,
                'expiry': self.expiry_date,
                'last_accessed': self.last_accessed
            },
            'users': {
                'uploaded_by': self.uploaded_by.get_full_name() if self.uploaded_by else None,
                'approved_by': self.approved_by.get_full_name() if self.approved_by else None
            },
            'stats': {
                'download_count': self.download_count,
                'version_count': self.versions.count() if self.parent_file is None else 0
            }
        }
    
    @classmethod
    def get_expiring_files(cls, days_ahead=30, employee=None):
        """Get files expiring within specified days"""
        end_date = date.today() + timedelta(days=days_ahead)
        queryset = cls.objects.filter(
            expiry_date__lte=end_date,
            expiry_date__gte=date.today(),
            status='approved',
            renewal_required=True
        )
        
        if employee:
            queryset = queryset.filter(employee=employee)
        
        return queryset.order_by('expiry_date')
    
    @classmethod
    def get_file_statistics(cls, employee=None):
        """Get file statistics"""
        queryset = cls.objects.all()
        if employee:
            queryset = queryset.filter(employee=employee)
        
        stats = {
            'total': queryset.count(),
            'by_status': {},
            'by_access_level': {},
            'by_category': {},
            'total_size_mb': 0,
            'approved': queryset.filter(status='approved').count(),
            'pending': queryset.filter(status='pending_review').count(),
            'expired': queryset.filter(expiry_date__lt=date.today()).count(),
            'confidential': queryset.filter(is_confidential=True).count(),
            'encrypted': queryset.filter(is_encrypted=True).count(),
        }
        
        # Calculate total size
        total_size = sum(f.file_size for f in queryset if f.file_size)
        stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        # Count by status
        for status, _ in cls.STATUS_CHOICES:
            stats['by_status'][status] = queryset.filter(status=status).count()
        
        # Count by access level
        for access_level, _ in cls.ACCESS_LEVELS:
            stats['by_access_level'][access_level] = queryset.filter(access_level=access_level).count()
        
        return stats


class EmployeeFileAccessLog(models.Model):
    """
    Log file access for audit purposes
    """
    file = models.ForeignKey(
        EmployeeFileEnhanced,
        on_delete=models.CASCADE,
        related_name='access_logs',
        verbose_name=_("الملف")
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("المستخدم")
    )
    
    ACTION_CHOICES = [
        ('view', _('عرض')),
        ('download', _('تحميل')),
        ('edit', _('تعديل')),
        ('delete', _('حذف')),
        ('approve', _('اعتماد')),
        ('reject', _('رفض')),
    ]
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name=_("الإجراء")
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("عنوان IP")
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("معلومات المتصفح")
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("وقت الإجراء")
    )
    
    class Meta:
        verbose_name = _("سجل وصول الملف")
        verbose_name_plural = _("سجلات وصول الملفات")
        db_table = 'hrms_employee_file_access_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['file', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_action_display()} - {self.file.title}"