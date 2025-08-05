"""
Employee Document Models for HRMS
Handles employee document management and archiving
Enhanced version with advanced features
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db.models import Q
import os
import uuid
import hashlib
from datetime import date, timedelta


class EmployeeDocumentEnhanced(models.Model):
    """
    Employee Document model for managing employee files and documents
    Supports document categorization, version control, and expiry tracking
    """
    
    # Relationship to Employee
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_("الموظف")
    )
    
    # Document Type and Category
    DOCUMENT_TYPES = [
        ('personal', _('وثائق شخصية')),
        ('identification', _('وثائق هوية')),
        ('education', _('شهادات تعليمية')),
        ('professional', _('شهادات مهنية')),
        ('medical', _('وثائق طبية')),
        ('contract', _('عقود ووثائق عمل')),
        ('insurance', _('وثائق تأمين')),
        ('financial', _('وثائق مالية')),
        ('legal', _('وثائق قانونية')),
        ('training', _('شهادات تدريب')),
        ('performance', _('تقييمات أداء')),
        ('disciplinary', _('إجراءات تأديبية')),
        ('other', _('أخرى')),
    ]
    
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        verbose_name=_("نوع الوثيقة")
    )
    
    # Document Information
    title = models.CharField(
        max_length=200,
        verbose_name=_("عنوان الوثيقة")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف الوثيقة")
    )
    
    document_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("رقم الوثيقة"),
        help_text=_("رقم الوثيقة الرسمي إن وجد")
    )
    
    # File Information
    file = models.FileField(
        upload_to='employee_documents/',
        verbose_name=_("الملف")
    )
    
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("حجم الملف (بايت)")
    )
    
    mime_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("نوع الملف")
    )
    
    # Date Information
    issue_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الإصدار")
    )
    
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الانتهاء")
    )
    
    # Issuing Authority
    issuing_authority = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("جهة الإصدار")
    )
    
    issuing_country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("دولة الإصدار")
    )
    
    # Verification and Status
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("تم التحقق")
    )
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents',
        verbose_name=_("تم التحقق بواسطة")
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التحقق")
    )
    
    # Document Status
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('expired', _('منتهي الصلاحية')),
        ('replaced', _('تم استبداله')),
        ('archived', _('مؤرشف')),
        ('pending_verification', _('في انتظار التحقق')),
        ('rejected', _('مرفوض')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_verification',
        verbose_name=_("حالة الوثيقة")
    )
    
    # Version Control
    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_("الإصدار")
    )
    
    replaced_document = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replacement_documents',
        verbose_name=_("الوثيقة المستبدلة")
    )
    
    # Access Control
    is_confidential = models.BooleanField(
        default=False,
        verbose_name=_("سري"),
        help_text=_("هل هذه الوثيقة سرية؟")
    )
    
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', _('عام')),
            ('internal', _('داخلي')),
            ('confidential', _('سري')),
            ('restricted', _('مقيد')),
        ],
        default='internal',
        verbose_name=_("مستوى الوصول")
    )
    
    # Reminder Settings
    reminder_days_before_expiry = models.PositiveIntegerField(
        default=30,
        verbose_name=_("تذكير قبل انتهاء الصلاحية (أيام)")
    )
    
    # Additional Information
    tags = models.JSONField(
        default=list,
        verbose_name=_("العلامات"),
        help_text=_("علامات للبحث والتصنيف")
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # Metadata
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
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
        verbose_name = _("وثيقة موظف")
        verbose_name_plural = _("وثائق الموظفين")
        db_table = 'hrms_employee_document'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'document_type']),
            models.Index(fields=['status']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"
    
    def clean(self):
        """Validate document data"""
        super().clean()
        
        # Validate dates
        if self.issue_date and self.expiry_date:
            if self.issue_date > self.expiry_date:
                raise ValidationError(_("تاريخ الإصدار لا يمكن أن يكون بعد تاريخ الانتهاء"))
        
        # Validate file size (max 50MB)
        if self.file and hasattr(self.file, 'size'):
            if self.file.size > 50 * 1024 * 1024:  # 50MB
                raise ValidationError(_("حجم الملف لا يمكن أن يتجاوز 50 ميجابايت"))
    
    @property
    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def needs_renewal_reminder(self):
        """Check if document needs renewal reminder"""
        if self.expiry_date:
            days_until_expiry = self.days_until_expiry
            if days_until_expiry is not None:
                return days_until_expiry <= self.reminder_days_before_expiry
        return False
    
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
        return None
    
    def verify_document(self, verified_by_user):
        """Mark document as verified"""
        self.is_verified = True
        self.verified_by = verified_by_user
        self.verified_at = timezone.now()
        self.status = 'active'
        self.save()
    
    def reject_document(self, reason=None):
        """Reject document"""
        self.status = 'rejected'
        if reason:
            self.notes = f"{self.notes or ''}\nسبب الرفض: {reason}"
        self.save()
    
    def replace_with_new_version(self, new_document):
        """Replace this document with a new version"""
        self.status = 'replaced'
        new_document.replaced_document = self
        new_document.version = self.version + 1
        self.save()
        new_document.save()
    
    def save(self, *args, **kwargs):
        """Override save to set file metadata"""
        if self.file:
            # Set file size
            if hasattr(self.file, 'size'):
                self.file_size = self.file.size
            
            # Set MIME type based on file extension
            extension = self.file_extension
            mime_types = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.txt': 'text/plain',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.xls': 'application/vnd.ms-excel',
            }
            if extension in mime_types:
                self.mime_type = mime_types[extension]
        
        # Update status based on expiry
        if self.is_expired and self.status == 'active':
            self.status = 'expired'
        
        super().save(*args, **kwargs)
    
    # Advanced Methods
    def get_status_display_with_icon(self):
        """Get status with visual indicator"""
        status_icons = {
            'active': '✅ نشط',
            'expired': '❌ منتهي الصلاحية',
            'replaced': '🔄 تم استبداله',
            'archived': '📦 مؤرشف',
            'pending_verification': '⏳ في انتظار التحقق',
            'rejected': '🚫 مرفوض',
        }
        return status_icons.get(self.status, self.get_status_display())
    
    def get_access_level_display_with_icon(self):
        """Get access level with visual indicator"""
        access_icons = {
            'public': '🌐 عام',
            'internal': '🏢 داخلي',
            'confidential': '🔒 سري',
            'restricted': '🚨 مقيد',
        }
        return access_icons.get(self.access_level, self.get_access_level_display())
    
    def get_expiry_status(self):
        """Get detailed expiry status"""
        if not self.expiry_date:
            return {'status': 'no_expiry', 'message': 'لا ينتهي', 'color': 'success'}
        
        days = self.days_until_expiry
        if days is None:
            return {'status': 'no_expiry', 'message': 'لا ينتهي', 'color': 'success'}
        
        if days < 0:
            return {
                'status': 'expired',
                'message': f'منتهي منذ {abs(days)} يوم',
                'color': 'danger'
            }
        elif days <= 7:
            return {
                'status': 'critical',
                'message': f'ينتهي خلال {days} يوم',
                'color': 'danger'
            }
        elif days <= 30:
            return {
                'status': 'warning',
                'message': f'ينتهي خلال {days} يوم',
                'color': 'warning'
            }
        else:
            return {
                'status': 'valid',
                'message': f'صالح لـ {days} يوم',
                'color': 'success'
            }
    
    def get_file_type_icon(self):
        """Get file type icon based on extension"""
        extension = self.file_extension
        if not extension:
            return '📄'
        
        icons = {
            '.pdf': '📄',
            '.doc': '📝',
            '.docx': '📝',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.txt': '📃',
            '.xlsx': '📊',
            '.xls': '📊',
            '.zip': '🗜️',
            '.rar': '🗜️',
        }
        return icons.get(extension, '📄')
    
    def get_document_summary(self):
        """Get comprehensive document summary"""
        return {
            'title': self.title,
            'type': self.get_document_type_display(),
            'status': self.get_status_display_with_icon(),
            'access_level': self.get_access_level_display_with_icon(),
            'expiry_status': self.get_expiry_status(),
            'file_info': {
                'size': f"{self.file_size_mb} MB" if self.file_size_mb else "غير محدد",
                'type': self.mime_type or "غير محدد",
                'icon': self.get_file_type_icon()
            },
            'verification': {
                'is_verified': self.is_verified,
                'verified_by': self.verified_by.get_full_name() if self.verified_by else None,
                'verified_at': self.verified_at
            },
            'metadata': {
                'version': self.version,
                'uploaded_by': self.uploaded_by.get_full_name() if self.uploaded_by else None,
                'created_at': self.created_at,
                'tags': self.tags
            }
        }
    
    def get_security_score(self):
        """Calculate document security score"""
        score = 0
        
        # Base score for having the document
        score += 20
        
        # Verification bonus
        if self.is_verified:
            score += 30
        
        # Access level security
        access_scores = {
            'public': 5,
            'internal': 10,
            'confidential': 20,
            'restricted': 25
        }
        score += access_scores.get(self.access_level, 0)
        
        # Status bonus
        if self.status == 'active':
            score += 15
        elif self.status == 'expired':
            score -= 20
        elif self.status == 'rejected':
            score -= 30
        
        # Expiry penalty
        if self.is_expired:
            score -= 25
        elif self.needs_renewal_reminder:
            score -= 10
        
        # File type bonus (PDF is more secure)
        if self.file_extension == '.pdf':
            score += 5
        
        return max(0, min(100, score))
    
    def get_related_documents(self):
        """Get related documents (same type, same employee)"""
        return EmployeeDocument.objects.filter(
            employee=self.employee,
            document_type=self.document_type
        ).exclude(id=self.id).order_by('-created_at')[:5]
    
    def get_version_history(self):
        """Get version history of this document"""
        # Get all documents that were replaced by this one
        older_versions = []
        current = self.replaced_document
        while current:
            older_versions.append(current)
            current = current.replaced_document
        
        # Get newer versions
        newer_versions = list(self.replacement_documents.all().order_by('version'))
        
        return {
            'older_versions': older_versions,
            'current_version': self,
            'newer_versions': newer_versions
        }
    
    def can_be_accessed_by(self, user):
        """Check if user can access this document"""
        # System admin can access everything
        if user.is_superuser:
            return True
        
        # Employee can access their own documents (except restricted)
        if self.employee.user == user and self.access_level != 'restricted':
            return True
        
        # HR staff can access internal and public documents
        if hasattr(user, 'profile') and user.profile.department == 'hr':
            return self.access_level in ['public', 'internal']
        
        # Manager can access their team's documents
        if hasattr(user, 'managed_employees'):
            if self.employee in user.managed_employees.all():
                return self.access_level in ['public', 'internal', 'confidential']
        
        # Public documents can be accessed by anyone
        return self.access_level == 'public'
    
    def generate_download_token(self, user, expires_in_hours=24):
        """Generate secure download token"""
        import jwt
        from datetime import datetime, timedelta
        
        payload = {
            'document_id': str(self.id),
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours)
        }
        
        # Use Django secret key for signing
        from django.conf import settings
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token
    
    @classmethod
    def get_expiring_documents(cls, days_ahead=30, employee=None):
        """Get documents expiring within specified days"""
        from datetime import date, timedelta
        
        end_date = date.today() + timedelta(days=days_ahead)
        queryset = cls.objects.filter(
            expiry_date__lte=end_date,
            expiry_date__gte=date.today(),
            status='active'
        )
        
        if employee:
            queryset = queryset.filter(employee=employee)
        
        return queryset.order_by('expiry_date')
    
    @classmethod
    def get_document_statistics(cls, employee=None):
        """Get document statistics"""
        queryset = cls.objects.all()
        if employee:
            queryset = queryset.filter(employee=employee)
        
        stats = {
            'total': queryset.count(),
            'by_type': {},
            'by_status': {},
            'verified': queryset.filter(is_verified=True).count(),
            'expired': queryset.filter(status='expired').count(),
            'expiring_soon': 0,
            'confidential': queryset.filter(is_confidential=True).count(),
        }
        
        # Count by document type
        for doc_type, _ in cls.DOCUMENT_TYPES:
            stats['by_type'][doc_type] = queryset.filter(document_type=doc_type).count()
        
        # Count by status
        for status, _ in cls.STATUS_CHOICES:
            stats['by_status'][status] = queryset.filter(status=status).count()
        
        # Count expiring soon
        expiring_docs = cls.get_expiring_documents(30, employee)
        stats['expiring_soon'] = expiring_docs.count()
        
        return stats
    
    def create_audit_log(self, action, user, details=None):
        """Create audit log entry for document actions"""
        # This would integrate with the audit system
        log_entry = {
            'document_id': str(self.id),
            'document_title': self.title,
            'employee': self.employee.full_name,
            'action': action,
            'user': user.get_full_name(),
            'timestamp': timezone.now(),
            'details': details or {}
        }
        return log_entry
    
    def get_backup_info(self):
        """Get backup information for this document"""
        return {
            'original_filename': os.path.basename(self.file.name) if self.file else None,
            'storage_path': self.file.name if self.file else None,
            'backup_needed': self.is_confidential or self.access_level == 'restricted',
            'retention_period': '7 years' if self.document_type in ['contract', 'legal'] else '5 years'
        }
