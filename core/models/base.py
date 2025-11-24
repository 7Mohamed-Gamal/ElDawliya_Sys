"""
النماذج الأساسية المشتركة
Base Models for the ElDawliya System
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = get_user_model()


class BaseModel(models.Model):
    """
    النموذج الأساسي المشترك لجميع النماذج في النظام
    Base model with common fields for all models in the system
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('المعرف الفريد')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء'),
        help_text=_('تاريخ ووقت إنشاء السجل')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث'),
        help_text=_('تاريخ ووقت آخر تحديث للسجل')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name=_('أنشئ بواسطة'),
        help_text=_('المستخدم الذي أنشأ هذا السجل')
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name=_('حُدث بواسطة'),
        help_text=_('المستخدم الذي قام بآخر تحديث لهذا السجل')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل هذا السجل نشط أم لا')
    )

    class Meta:
        """Meta class"""
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.__class__.__name__} - {self.id}"

    def save(self, *args, **kwargs):
        """Override save to handle audit fields"""
        user = kwargs.pop('user', None)
        if user:
            if not self.pk:  # New record
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)


class AuditableModel(BaseModel):
    """
    نموذج قابل للمراجعة مع تتبع الإصدارات
    Auditable model with version tracking
    """
    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_('رقم الإصدار'),
        help_text=_('رقم إصدار السجل للتتبع')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات'),
        help_text=_('ملاحظات إضافية حول السجل')
    )

    class Meta:
        """Meta class"""
        abstract = True

    def save(self, *args, **kwargs):
        """Override save to increment version"""
        if self.pk:  # Existing record
            self.version += 1
        super().save(*args, **kwargs)


class SoftDeleteModel(BaseModel):
    """
    نموذج الحذف الناعم
    Soft delete model - marks records as deleted instead of removing them
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الحذف'),
        help_text=_('تاريخ ووقت حذف السجل')
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        verbose_name=_('حُذف بواسطة'),
        help_text=_('المستخدم الذي حذف هذا السجل')
    )

    class Meta:
        """Meta class"""
        abstract = True

    def delete(self, using=None, keep_parents=False, user=None):
        """Soft delete - mark as deleted instead of removing"""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.is_active = False
        self.save(update_fields=['deleted_at', 'deleted_by', 'is_active'])

    def restore(self, user=None):
        """Restore a soft-deleted record"""
        self.deleted_at = None
        self.deleted_by = None
        self.is_active = True
        if user:
            self.updated_by = user
        self.save(update_fields=['deleted_at', 'deleted_by', 'is_active', 'updated_by'])

    @property
    def is_deleted(self):
        """Check if record is soft-deleted"""
        return self.deleted_at is not None


class TimestampedModel(models.Model):
    """
    نموذج بسيط مع الطوابع الزمنية فقط
    Simple model with only timestamps
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )

    class Meta:
        """Meta class"""
        abstract = True
        ordering = ['-created_at']


class AddressModel(models.Model):
    """
    نموذج العنوان المشترك
    Shared address model
    """
    street_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('عنوان الشارع')
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('المدينة')
    )
    state_province = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('المحافظة/الولاية')
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('الرمز البريدي')
    )
    country = models.CharField(
        max_length=100,
        default='السعودية',
        verbose_name=_('البلد')
    )

    class Meta:
        """Meta class"""
        abstract = True

    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [
            self.street_address,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ', '.join([part for part in parts if part])


class ContactModel(models.Model):
    """
    نموذج معلومات الاتصال المشترك
    Shared contact information model
    """
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('رقم الهاتف')
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('رقم الجوال')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('البريد الإلكتروني')
    )
    fax = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('رقم الفاكس')
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('الموقع الإلكتروني')
    )

    class Meta:
        """Meta class"""
        abstract = True
