from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from Hr.models.employee_model import Employee

User = get_user_model()

class EmployeeNote(models.Model):
    """
    نموذج شامل لإدارة ملاحظات الموظفين مع ربط التقييمات
    """

    NOTE_TYPE_CHOICES = [
        ('positive', _('إيجابية/جيدة')),
        ('negative', _('سلبية/ضعيفة')),
        ('general', _('عامة/محايدة')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('urgent', _('عاجلة')),
    ]

    # Basic Information
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('الموظف')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان الملاحظة')
    )
    content = models.TextField(
        verbose_name=_('محتوى الملاحظة'),
        help_text=_('اكتب تفاصيل الملاحظة هنا')
    )

    # Note Classification
    note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPE_CHOICES,
        default='general',
        verbose_name=_('نوع الملاحظة')
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('الأولوية')
    )

    # Evaluation Linking
    evaluation_link = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('رابط التقييم'),
        help_text=_('رابط اختياري لربط الملاحظة بتقييم الأداء')
    )
    evaluation_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('درجة التقييم'),
        help_text=_('درجة التقييم المرتبطة بالملاحظة (اختياري)')
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_employee_notes',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_employee_notes',
        verbose_name=_('آخر تعديل بواسطة')
    )

    # Flags
    is_important = models.BooleanField(
        default=False,
        verbose_name=_('ملاحظة مهمة')
    )
    is_confidential = models.BooleanField(
        default=False,
        verbose_name=_('سرية'),
        help_text=_('ملاحظة سرية - محدودة الوصول')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشطة'),
        help_text=_('إلغاء تفعيل الملاحظة بدلاً من حذفها')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ آخر تحديث')
    )

    # Additional Fields
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('العلامات'),
        help_text=_('علامات مفصولة بفواصل للبحث والتصنيف')
    )
    follow_up_required = models.BooleanField(
        default=False,
        verbose_name=_('يتطلب متابعة')
    )
    follow_up_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ المتابعة')
    )

    def __str__(self):
        return f"{self.title} - {self.employee.emp_full_name or self.employee.emp_first_name}"

    def get_note_type_display_color(self):
        """إرجاع لون مناسب لنوع الملاحظة"""
        colors = {
            'positive': 'success',
            'negative': 'danger',
            'general': 'info'
        }
        return colors.get(self.note_type, 'secondary')

    def get_priority_display_color(self):
        """إرجاع لون مناسب للأولوية"""
        colors = {
            'low': 'secondary',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'dark'
        }
        return colors.get(self.priority, 'secondary')

    class Meta:
        verbose_name = _('ملاحظة الموظف')
        verbose_name_plural = _('ملاحظات الموظفين')
        ordering = ['-created_at']
        managed = True
        permissions = [
            ('view_confidential_notes', 'يمكن عرض الملاحظات السرية'),
            ('manage_all_notes', 'يمكن إدارة جميع الملاحظات'),
        ]


class EmployeeNoteHistory(models.Model):
    """
    نموذج لتتبع تاريخ تعديل الملاحظات (Audit Trail)
    """

    ACTION_CHOICES = [
        ('created', _('تم الإنشاء')),
        ('updated', _('تم التحديث')),
        ('deleted', _('تم الحذف')),
        ('restored', _('تم الاستعادة')),
    ]

    note = models.ForeignKey(
        EmployeeNote,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('الملاحظة')
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name=_('الإجراء')
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('تم التغيير بواسطة')
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ التغيير')
    )
    old_values = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('القيم السابقة')
    )
    new_values = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('القيم الجديدة')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات التغيير')
    )

    def __str__(self):
        return f"{self.note.title} - {self.get_action_display()} - {self.changed_at}"

    class Meta:
        verbose_name = _('تاريخ ملاحظة الموظف')
        verbose_name_plural = _('تاريخ ملاحظات الموظفين')
        ordering = ['-changed_at']
        managed = True
