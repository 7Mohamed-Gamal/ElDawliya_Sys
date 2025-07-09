"""
Employee Document Models for HRMS
Handles employee document management and archiving
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import os


class EmployeeDocument(models.Model):
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
