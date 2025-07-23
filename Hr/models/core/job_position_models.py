"""
نماذج الوظائف والمستويات الوظيفية لنظام إدارة الموارد البشرية (HRMS)
تتعامل مع تعريف الوظائف، الأدوار، والمسارات المهنية
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError


class JobLevel(models.Model):
    """
    نموذج مستوى وظيفي لتعريف الدرجات والمسارات المهنية
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم المستوى الوظيفي")
    )
    
    name_en = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الاسم بالإنجليزية")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود المستوى")
    )
    
    # Hierarchical Level
    level_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("ترتيب المستوى"),
        help_text=_("ترتيب المستوى في الهيكل التنظيمي (الأقل هو الأعلى)")
    )
    
    # Description
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف المستوى")
    )
    
    # Salary Range
    min_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأدنى للراتب")
    )
    
    max_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للراتب")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("مستوى وظيفي")
        verbose_name_plural = _("مستويات وظيفية")
        ordering = ['level_order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['level_order']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate job level data"""
        super().clean()
        
        # Validate salary range
        if self.min_salary and self.max_salary:
            if self.min_salary > self.max_salary:
                raise ValidationError(_("الحد الأدنى للراتب لا يمكن أن يكون أكبر من الحد الأقصى"))
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate code if not provided"""
        if not self.code:
            level_count = JobLevel.objects.count()
            self.code = f"JL{level_count + 1:03d}"
        
        super().save(*args, **kwargs)


class JobPosition(models.Model):
    """
    نموذج الوظيفة لتعريف الدور الوظيفي والمتطلبات والمسؤوليات
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationship to Department
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        related_name='job_positions',
        verbose_name=_("القسم")
    )
    
    # Basic Information
    title = models.CharField(
        max_length=200,
        verbose_name=_("المسمى الوظيفي")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود الوظيفة"),
        help_text=_("كود فريد للوظيفة"),
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-]+$',
                message=_("كود الوظيفة يجب أن يحتوي على أحرف كبيرة وأرقام فقط")
            )
        ]
    )
    
    title_english = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("المسمى الوظيفي بالإنجليزية")
    )
    
    description = models.TextField(
        verbose_name=_("وصف الوظيفة"),
        help_text=_("وصف مفصل للوظيفة ومسؤولياتها")
    )
    
    # Job Requirements
    requirements = models.TextField(
        verbose_name=_("متطلبات الوظيفة"),
        help_text=_("المؤهلات والخبرات المطلوبة")
    )
    
    responsibilities = models.TextField(
        verbose_name=_("المسؤوليات"),
        help_text=_("المسؤوليات الأساسية للوظيفة")
    )
    
    skills_required = models.JSONField(
        default=list,
        verbose_name=_("المهارات المطلوبة"),
        help_text=_("قائمة بالمهارات المطلوبة للوظيفة")
    )
    
    # Education and Experience Requirements
    EDUCATION_LEVELS = [
        ('high_school', _('ثانوية عامة')),
        ('diploma', _('دبلوم')),
        ('bachelor', _('بكالوريوس')),
        ('master', _('ماجستير')),
        ('phd', _('دكتوراه')),
        ('professional', _('شهادة مهنية')),
    ]
    
    minimum_education = models.CharField(
        max_length=20,
        choices=EDUCATION_LEVELS,
        default='high_school',
        verbose_name=_("الحد الأدنى للتعليم")
    )
    
    preferred_education = models.CharField(
        max_length=20,
        choices=EDUCATION_LEVELS,
        null=True,
        blank=True,
        verbose_name=_("التعليم المفضل")
    )
    
    minimum_experience_years = models.PositiveIntegerField(
        default=0,
        verbose_name=_("سنوات الخبرة المطلوبة (الحد الأدنى)")
    )
    
    preferred_experience_years = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("سنوات الخبرة المفضلة")
    )
    
    # Job Level and Career Path
    JOB_LEVELS = [
        (1, _('مبتدئ')),
        (2, _('متوسط')),
        (3, _('أول')),
        (4, _('رئيس')),
        (5, _('مدير')),
        (6, _('مدير أول')),
        (7, _('مدير عام')),
        (8, _('نائب رئيس')),
        (9, _('رئيس')),
        (10, _('رئيس تنفيذي')),
    ]
    
    level = models.PositiveIntegerField(
        choices=JOB_LEVELS,
        default=1,
        verbose_name=_("مستوى الوظيفة"),
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinate_positions',
        verbose_name=_("يرفع تقارير إلى")
    )
    
    # Employment Type
    EMPLOYMENT_TYPES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('تعاقد')),
        ('temporary', _('مؤقت')),
        ('intern', _('متدرب')),
        ('consultant', _('استشاري')),
    ]
    
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPES,
        default='full_time',
        verbose_name=_("نوع التوظيف")
    )
    
    # Salary Information
    min_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأدنى للراتب")
    )
    
    max_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للراتب")
    )
    
    currency = models.CharField(
        max_length=3,
        default="EGP",
        verbose_name=_("العملة")
    )
    
    # Benefits and Allowances
    benefits = models.JSONField(
        default=list,
        verbose_name=_("المزايا والبدلات"),
        help_text=_("قائمة بالمزايا والبدلات المرتبطة بالوظيفة")
    )
    
    # Working Conditions
    working_hours_per_week = models.PositiveIntegerField(
        default=40,
        verbose_name=_("ساعات العمل الأسبوعية")
    )
    
    travel_required = models.BooleanField(
        default=False,
        verbose_name=_("يتطلب سفر")
    )
    
    remote_work_allowed = models.BooleanField(
        default=False,
        verbose_name=_("يسمح بالعمل عن بُعد")
    )
    
    overtime_eligible = models.BooleanField(
        default=True,
        verbose_name=_("مؤهل للعمل الإضافي")
    )
    
    # Performance Metrics
    kpis = models.JSONField(
        default=list,
        verbose_name=_("مؤشرات الأداء الرئيسية"),
        help_text=_("مؤشرات الأداء الرئيسية للوظيفة")
    )
    
    performance_goals = models.JSONField(
        default=list,
        verbose_name=_("أهداف الأداء"),
        help_text=_("الأهداف المتوقعة من شاغل الوظيفة")
    )
    
    # Job Settings
    job_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات الوظيفة"),
        help_text=_("إعدادات خاصة بالوظيفة")
    )
    
    # Capacity and Headcount
    max_headcount = models.PositiveIntegerField(
        default=1,
        verbose_name=_("العدد الأقصى للموظفين"),
        help_text=_("العدد الأقصى للموظفين في هذه الوظيفة")
    )
    
    current_headcount = models.PositiveIntegerField(
        default=0,
        verbose_name=_("العدد الحالي للموظفين")
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_critical = models.BooleanField(
        default=False,
        verbose_name=_("وظيفة حرجة"),
        help_text=_("هل هذه الوظيفة حرجة لعمل المؤسسة؟")
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_job_positions',
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
        verbose_name = _("وظيفة")
        verbose_name_plural = _("الوظائف")
        db_table = 'hrms_job_position'
        ordering = ['department', 'level', 'title']
        unique_together = [['department', 'code']]
        indexes = [
            models.Index(fields=['department', 'title']),
            models.Index(fields=['code']),
            models.Index(fields=['level']),
            models.Index(fields=['employment_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        """إرجاع المسمى الوظيفي مع اسم القسم"""
        return f"{self.title} - {self.department.name}"
    
    def clean(self):
        """التحقق من صحة بيانات الوظيفة (الرواتب، سنوات الخبرة، العدد)"""
        super().clean()
        
        # Validate salary range
        if self.min_salary and self.max_salary:
            if self.min_salary > self.max_salary:
                raise ValidationError(_("الحد الأدنى للراتب لا يمكن أن يكون أكبر من الحد الأقصى"))
        
        # Validate experience years
        if (self.minimum_experience_years and self.preferred_experience_years and
            self.minimum_experience_years > self.preferred_experience_years):
            raise ValidationError(_("سنوات الخبرة المطلوبة لا يمكن أن تكون أكثر من المفضلة"))
        
        # Validate headcount
        if self.current_headcount > self.max_headcount:
            raise ValidationError(_("العدد الحالي للموظفين لا يمكن أن يتجاوز العدد الأقصى"))
    
    def get_current_employees(self):
        """الحصول على الموظفين الحاليين في هذه الوظيفة"""
        return self.employees.filter(status='active')
    
    def get_available_positions(self):
        """الحصول على عدد الوظائف الشاغرة"""
        return self.max_headcount - self.current_headcount
    
    def is_position_available(self):
        """التحقق من توفر وظيفة شاغرة"""
        return self.get_available_positions() > 0
    
    @property
    def salary_range_display(self):
        """عرض نطاق الراتب بشكل منسق"""
        if self.min_salary and self.max_salary:
            return f"{self.min_salary:,.2f} - {self.max_salary:,.2f} {self.currency}"
        elif self.min_salary:
            return f"من {self.min_salary:,.2f} {self.currency}"
        elif self.max_salary:
            return f"حتى {self.max_salary:,.2f} {self.currency}"
        return _("غير محدد")
    
    def save(self, *args, **kwargs):
        """تجاوز الحفظ لتوليد كود الوظيفة وتعيين الإعدادات الافتراضية وتحديث العدد الحالي"""
        # Set default job settings
        if not self.job_settings:
            self.job_settings = {
                'probation_period_days': 90,
                'notice_period_days': 30,
                'performance_review_frequency': 'annual',
                'training_required': [],
                'certifications_required': [],
            }
        
        # Auto-generate code if not provided
        if not self.code:
            dept_code = self.department.code
            job_count = JobPosition.objects.filter(department=self.department).count()
            self.code = f"{dept_code}-JOB{job_count + 1:03d}"
        
        # Update current headcount
        if self.pk:
            self.current_headcount = self.get_current_employees().count()
        
        super().save(*args, **kwargs)
