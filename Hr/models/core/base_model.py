"""
النموذج الأساسي للموارد البشرية

هذا الملف يحتوي على النموذج الأساسي الذي ترث منه جميع نماذج الموارد البشرية
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class HrBaseModel(models.Model):
    """
    النموذج الأساسي لجميع نماذج الموارد البشرية
    يحتوي على الحقول المشتركة بين جميع النماذج
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name=_("أنشئ بواسطة")
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name=_("عدل بواسطة")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )

    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        تخصيص عملية الحفظ لتسجيل التغييرات
        """
        super().save(*args, **kwargs)

    def soft_delete(self):
        """
        تنفيذ الحذف الناعم (تعطيل بدلاً من الحذف)
        """
        self.is_active = False
        self.updated_at = timezone.now()
        self.save()

    def restore(self):
        """
        استعادة العنصر المحذوف ناعماً
        """
        self.is_active = True
        self.updated_at = timezone.now()
        self.save()
