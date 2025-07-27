"""
نماذج البحث المتقدم والذكي
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.indexes import GinIndex
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
import json


class SearchIndex(models.Model):
    """فهرس البحث الموحد"""
    
    CONTENT_TYPES = [
        ('employee', _('موظف')),
        ('department', _('قسم')),
        ('job', _('وظيفة')),
        ('company', _('شركة')),
        ('branch', _('فرع')),
        ('leave_request', _('طلب إجازة')),
        ('attendance_record', _('سجل حضور')),
        ('payroll_entry', _('كشف راتب')),
        ('employee_file', _('ملف موظف')),
        ('evaluation', _('تقييم')),
        ('notification', _('إشعار')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # المحتوى المفهرس
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('نوع المحتوى')
    )
    object_id = models.PositiveIntegerField(verbose_name=_('معرف الكائن'))
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # بيانات البحث
    title = models.CharField(_('العنوان'), max_length=500)
    content = models.TextField(_('المحتوى'))
    keywords = models.TextField(_('الكلمات المفتاحية'), blank=True)
    
    # فهرس البحث النصي
    search_vector = models.TextField(_('فهرس البحث'), blank=True)
    
    # معلومات إضافية
    metadata = models.JSONField(
        _('البيانات الوصفية'),
        default=dict,
        blank=True,
        help_text=_('معلومات إضافية للبحث والفلترة')
    )
    
    # معلومات الشركة والقسم للفلترة
    company_id = models.PositiveIntegerField(_('معرف الشركة'), null=True, blank=True)
    department_id = models.PositiveIntegerField(_('معرف القسم'), null=True, blank=True)
    branch_id = models.PositiveIntegerField(_('معرف الفرع'), null=True, blank=True)
    
    # تواريخ
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    indexed_at = models.DateTimeField(_('تاريخ الفهرسة'), auto_now=True)
    
    # حالة الفهرسة
    is_active = models.BooleanField(_('نشط'), default=True)
    
    class Meta:
        verbose_name = _('فهرس البحث')
        verbose_name_plural = _('فهارس البحث')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['company_id']),
            models.Index(fields=['department_id']),
            models.Index(fields=['branch_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
            # فهرس البحث النصي (PostgreSQL)
            # GinIndex(fields=['search_vector']),
        ]
        unique_together = ['content_type', 'object_id']
    
    def __str__(self):
        return f"{self.title} ({self.content_type})"
    
    def update_search_vector(self):
        """تحديث فهرس البحث النصي"""
        # دمج العنوان والمحتوى والكلمات المفتاحية
        search_text = f"{self.title} {self.content} {self.keywords}"
        
        # إنشاء فهرس البحث (مبسط للتوافق مع جميع قواعد البيانات)
        self.search_vector = search_text.lower()
        
    def save(self, *args, **kwargs):
        self.update_search_vector()
        super().save(*args, **kwargs)


class SavedSearch(models.Model):
    """عمليات البحث المحفوظة"""
    
    SEARCH_TYPES = [
        ('simple', _('بحث بسيط')),
        ('advanced', _('بحث متقدم')),
        ('filter', _('فلترة')),
        ('smart', _('بحث ذكي')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_searches',
        verbose_name=_('المستخدم')
    )
    
    # معلومات البحث
    name = models.CharField(_('اسم البحث'), max_length=200)
    description = models.TextField(_('الوصف'), blank=True)
    
    search_type = models.CharField(
        _('نوع البحث'),
        max_length=20,
        choices=SEARCH_TYPES,
        default='simple'
    )
    
    # معايير البحث
    query = models.TextField(_('استعلام البحث'))
    filters = models.JSONField(
        _('الفلاتر'),
        default=dict,
        blank=True,
        help_text=_('فلاتر البحث المطبقة')
    )
    
    # إعدادات البحث
    content_types = models.JSONField(
        _('أنواع المحتوى'),
        default=list,
        blank=True,
        help_text=_('أنواع المحتوى المشمولة في البحث')
    )
    
    # إحصائيات
    usage_count = models.PositiveIntegerField(_('عدد الاستخدام'), default=0)
    last_used_at = models.DateTimeField(_('آخر استخدام'), null=True, blank=True)
    
    # إعدادات المشاركة
    is_public = models.BooleanField(_('عام'), default=False)
    is_favorite = models.BooleanField(_('مفضل'), default=False)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('بحث محفوظ')
        verbose_name_plural = _('عمليات البحث المحفوظة')
        ordering = ['-last_used_at', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_favorite']),
            models.Index(fields=['is_public']),
            models.Index(fields=['search_type']),
            models.Index(fields=['usage_count']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.get_full_name()}"
    
    def increment_usage(self):
        """زيادة عداد الاستخدام"""
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])


class SearchSuggestion(models.Model):
    """اقتراحات البحث"""
    
    SUGGESTION_TYPES = [
        ('keyword', _('كلمة مفتاحية')),
        ('phrase', _('عبارة')),
        ('filter', _('فلتر')),
        ('correction', _('تصحيح')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # الاقتراح
    text = models.CharField(_('النص'), max_length=200)
    suggestion_type = models.CharField(
        _('نوع الاقتراح'),
        max_length=20,
        choices=SUGGESTION_TYPES,
        default='keyword'
    )
    
    # الشعبية والاستخدام
    usage_count = models.PositiveIntegerField(_('عدد الاستخدام'), default=0)
    success_rate = models.FloatField(_('معدل النجاح'), default=0.0)
    
    # السياق
    context = models.JSONField(
        _('السياق'),
        default=dict,
        blank=True,
        help_text=_('معلومات السياق للاقتراح')
    )
    
    # الفئات
    categories = models.JSONField(
        _('الفئات'),
        default=list,
        blank=True,
        help_text=_('فئات المحتوى المرتبطة')
    )
    
    # حالة الاقتراح
    is_active = models.BooleanField(_('نشط'), default=True)
    is_auto_generated = models.BooleanField(_('مُولد تلقائياً'), default=False)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('اقتراح البحث')
        verbose_name_plural = _('اقتراحات البحث')
        ordering = ['-usage_count', '-success_rate']
        indexes = [
            models.Index(fields=['text']),
            models.Index(fields=['suggestion_type']),
            models.Index(fields=['usage_count']),
            models.Index(fields=['success_rate']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.text} ({self.get_suggestion_type_display()})"
    
    def increment_usage(self, successful=True):
        """تحديث إحصائيات الاستخدام"""
        self.usage_count += 1
        
        if successful:
            # حساب معدل النجاح الجديد
            total_successes = (self.success_rate * (self.usage_count - 1)) + 1
            self.success_rate = total_successes / self.usage_count
        else:
            # إعادة حساب معدل النجاح
            total_successes = self.success_rate * (self.usage_count - 1)
            self.success_rate = total_successes / self.usage_count
        
        self.save(update_fields=['usage_count', 'success_rate', 'updated_at'])


class SearchLog(models.Model):
    """سجل عمليات البحث"""
    
    SEARCH_RESULTS = [
        ('success', _('نجح')),
        ('no_results', _('لا توجد نتائج')),
        ('error', _('خطأ')),
        ('cancelled', _('ملغي')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # المستخدم والجلسة
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='search_logs',
        verbose_name=_('المستخدم')
    )
    session_key = models.CharField(_('مفتاح الجلسة'), max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(_('عنوان IP'), null=True, blank=True)
    
    # تفاصيل البحث
    query = models.TextField(_('استعلام البحث'))
    search_type = models.CharField(_('نوع البحث'), max_length=20, default='simple')
    filters_applied = models.JSONField(_('الفلاتر المطبقة'), default=dict, blank=True)
    
    # النتائج
    result_count = models.PositiveIntegerField(_('عدد النتائج'), default=0)
    result_status = models.CharField(
        _('حالة النتائج'),
        max_length=20,
        choices=SEARCH_RESULTS,
        default='success'
    )
    
    # الأداء
    execution_time = models.FloatField(_('وقت التنفيذ (ثانية)'), default=0.0)
    
    # معلومات إضافية
    user_agent = models.TextField(_('وكيل المستخدم'), blank=True)
    referer = models.URLField(_('المرجع'), blank=True)
    
    created_at = models.DateTimeField(_('تاريخ البحث'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('سجل البحث')
        verbose_name_plural = _('سجلات البحث')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['query']),
            models.Index(fields=['search_type']),
            models.Index(fields=['result_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'مجهول'
        return f"{self.query[:50]} - {user_name}"


class SearchFilter(models.Model):
    """فلاتر البحث المخصصة"""
    
    FILTER_TYPES = [
        ('text', _('نص')),
        ('number', _('رقم')),
        ('date', _('تاريخ')),
        ('choice', _('اختيار')),
        ('boolean', _('منطقي')),
        ('range', _('نطاق')),
    ]
    
    OPERATORS = [
        ('equals', _('يساوي')),
        ('not_equals', _('لا يساوي')),
        ('contains', _('يحتوي على')),
        ('not_contains', _('لا يحتوي على')),
        ('starts_with', _('يبدأ بـ')),
        ('ends_with', _('ينتهي بـ')),
        ('greater_than', _('أكبر من')),
        ('less_than', _('أصغر من')),
        ('greater_equal', _('أكبر من أو يساوي')),
        ('less_equal', _('أصغر من أو يساوي')),
        ('between', _('بين')),
        ('in', _('في')),
        ('not_in', _('ليس في')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الفلتر
    name = models.CharField(_('اسم الفلتر'), max_length=100)
    field_name = models.CharField(_('اسم الحقل'), max_length=100)
    display_name = models.CharField(_('الاسم المعروض'), max_length=100)
    
    filter_type = models.CharField(
        _('نوع الفلتر'),
        max_length=20,
        choices=FILTER_TYPES,
        default='text'
    )
    
    # العمليات المدعومة
    supported_operators = models.JSONField(
        _('العمليات المدعومة'),
        default=list,
        help_text=_('قائمة بالعمليات المدعومة لهذا الفلتر')
    )
    
    # الخيارات (للفلاتر من نوع choice)
    choices = models.JSONField(
        _('الخيارات'),
        default=list,
        blank=True,
        help_text=_('خيارات الفلتر للأنواع المحددة')
    )
    
    # أنواع المحتوى المطبقة عليها
    content_types = models.JSONField(
        _('أنواع المحتوى'),
        default=list,
        help_text=_('أنواع المحتوى التي يطبق عليها هذا الفلتر')
    )
    
    # الإعدادات
    is_active = models.BooleanField(_('نشط'), default=True)
    is_required = models.BooleanField(_('مطلوب'), default=False)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    
    # معلومات إضافية
    description = models.TextField(_('الوصف'), blank=True)
    help_text = models.CharField(_('نص المساعدة'), max_length=200, blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('فلتر البحث')
        verbose_name_plural = _('فلاتر البحث')
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['field_name']),
            models.Index(fields=['filter_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.get_filter_type_display()})"
    
    def get_choices_dict(self):
        """الحصول على الخيارات كقاموس"""
        if self.filter_type == 'choice' and self.choices:
            return {choice['value']: choice['label'] for choice in self.choices}
        return {}


class SmartSearchPattern(models.Model):
    """أنماط البحث الذكي"""
    
    PATTERN_TYPES = [
        ('synonym', _('مرادف')),
        ('abbreviation', _('اختصار')),
        ('common_typo', _('خطأ شائع')),
        ('related_term', _('مصطلح مرتبط')),
        ('category', _('فئة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # النمط
    pattern = models.CharField(_('النمط'), max_length=200)
    replacement = models.CharField(_('البديل'), max_length=200)
    
    pattern_type = models.CharField(
        _('نوع النمط'),
        max_length=20,
        choices=PATTERN_TYPES,
        default='synonym'
    )
    
    # الوزن والأولوية
    weight = models.FloatField(_('الوزن'), default=1.0)
    priority = models.PositiveIntegerField(_('الأولوية'), default=0)
    
    # السياق
    context_filters = models.JSONField(
        _('فلاتر السياق'),
        default=dict,
        blank=True,
        help_text=_('شروط تطبيق النمط')
    )
    
    # الإحصائيات
    usage_count = models.PositiveIntegerField(_('عدد الاستخدام'), default=0)
    success_rate = models.FloatField(_('معدل النجاح'), default=0.0)
    
    # الحالة
    is_active = models.BooleanField(_('نشط'), default=True)
    is_case_sensitive = models.BooleanField(_('حساس للأحرف'), default=False)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('نمط البحث الذكي')
        verbose_name_plural = _('أنماط البحث الذكي')
        ordering = ['-priority', '-weight']
        indexes = [
            models.Index(fields=['pattern']),
            models.Index(fields=['pattern_type']),
            models.Index(fields=['weight']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.pattern} → {self.replacement}"
    
    def apply_pattern(self, query):
        """تطبيق النمط على الاستعلام"""
        if not self.is_active:
            return query
        
        if self.is_case_sensitive:
            return query.replace(self.pattern, self.replacement)
        else:
            import re
            return re.sub(
                re.escape(self.pattern), 
                self.replacement, 
                query, 
                flags=re.IGNORECASE
            )