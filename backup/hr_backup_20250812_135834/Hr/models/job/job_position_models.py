"""
نماذج المناصب الوظيفية والوظائف

هذا الملف يحتوي على نماذج المناصب الوظيفية، الدرجات الوظيفية،
والمسارات المهنية التي تشكل الهيكل الوظيفي للمؤسسة
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from Hr.models.core.base_model import HrBaseModel

class JobGrade(HrBaseModel):
    """
    نموذج الدرجة الوظيفية

    يستخدم لتصنيف الوظائف حسب المستوى الوظيفي
    ويرتبط بنطاق الرواتب ومستوى الصلاحيات
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("اسم الدرجة الوظيفية")
    )

    name_en = models.CharField(
        max_length=50,
        verbose_name=_("الاسم بالإنجليزية"),
        null=True,
        blank=True
    )

    code = models.CharField(
        max_length=20,
        verbose_name=_("كود الدرجة")
    )

    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='job_grades',
        verbose_name=_("الشركة")
    )

    level = models.PositiveIntegerField(
        verbose_name=_("المستوى"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ],
        help_text=_("المستوى الهرمي للدرجة الوظيفية (1 هو الأعلى)")
    )

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

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف")
    )

    class Meta:
        verbose_name = _("درجة وظيفية")
        verbose_name_plural = _("الدرجات الوظيفية")
        unique_together = ['company', 'code']
        ordering = ['company', 'level']

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    def clean(self):
        """
        التحقق من صحة البيانات قبل الحفظ
        """
        if self.min_salary and self.max_salary and self.min_salary > self.max_salary:
            raise ValidationError({
                'min_salary': _("الحد الأدنى للراتب يجب ألا يتجاوز الحد الأقصى")
            })


class JobCategory(HrBaseModel):
    """
    نموذج فئة الوظائف

    يستخدم لتصنيف الوظائف حسب المجال أو التخصص
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الفئة")
    )

    name_en = models.CharField(
        max_length=100,
        verbose_name=_("الاسم بالإنجليزية"),
        null=True,
        blank=True
    )

    code = models.CharField(
        max_length=20,
        verbose_name=_("كود الفئة")
    )

    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='job_categories',
        verbose_name=_("الشركة")
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف")
    )

    class Meta:
        verbose_name = _("فئة وظيفية")
        verbose_name_plural = _("الفئات الوظيفية")
        unique_together = ['company', 'code']
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class JobPosition(HrBaseModel):
    """
    نموذج المنصب الوظيفي

    يمثل المنصب أو المسمى الوظيفي ويرتبط بالقسم والدرجة الوظيفية
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("المسمى الوظيفي")
    )

    name_en = models.CharField(
        max_length=100,
        verbose_name=_("المسمى بالإنجليزية"),
        null=True,
        blank=True
    )

    code = models.CharField(
        max_length=20,
        verbose_name=_("كود الوظيفة")
    )

    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='job_positions',
        verbose_name=_("الشركة")
    )

    department = models.ForeignKey(
        'core.Department',
        on_delete=models.CASCADE,
        related_name='job_positions',
        verbose_name=_("القسم")
    )

    job_grade = models.ForeignKey(
        JobGrade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_positions',
        verbose_name=_("الدرجة الوظيفية")
    )

    job_category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_positions',
        verbose_name=_("الفئة الوظيفية")
    )

    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinate_positions',
        verbose_name=_("يتبع لوظيفة")
    )

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

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف الوظيفي")
    )

    responsibilities = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("المسؤوليات")
    )

    qualifications = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("المؤهلات المطلوبة")
    )

    skills = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("المهارات المطلوبة")
    )

    experience_years = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("سنوات الخبرة المطلوبة")
    )

    vacancies = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("عدد الشواغر")
    )

    class Meta:
        verbose_name = _("منصب وظيفي")
        verbose_name_plural = _("المناصب الوظيفية")
        unique_together = ['company', 'code']
        ordering = ['company', 'department', 'name']

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    @property
    def full_name(self):
        """
        الاسم الكامل للوظيفة مع القسم
        """
        return f"{self.name} - {self.department.name}"

    def get_filled_positions_count(self):
        """
        حساب عدد المناصب المشغولة
        """
        return self.employees.filter(is_active=True).count()

    def get_vacancy_percentage(self):
        """
        حساب نسبة الشواغر المشغولة
        """
        if self.vacancies == 0:
            return 0
        filled = self.get_filled_positions_count()
        return (filled / self.vacancies) * 100 if self.vacancies > 0 else 0

    def clean(self):
        """
        التحقق من صحة البيانات قبل الحفظ
        """
        # التأكد من أن القسم ينتمي لنفس الشركة
        if self.department and self.department.company != self.company:
            raise ValidationError({
                'department': _("القسم يجب أن يكون من نفس الشركة")
            })

        # التأكد من أن الدرجة الوظيفية تنتمي لنفس الشركة
        if self.job_grade and self.job_grade.company != self.company:
            raise ValidationError({
                'job_grade': _("الدرجة الوظيفية يجب أن تكون من نفس الشركة")
            })

        # التأكد من أن الفئة الوظيفية تنتمي لنفس الشركة
        if self.job_category and self.job_category.company != self.company:
            raise ValidationError({
                'job_category': _("الفئة الوظيفية يجب أن تكون من نفس الشركة")
            })

        # التأكد من أن المنصب الذي يتبع له ينتمي لنفس الشركة
        if self.reports_to and self.reports_to.company != self.company:
            raise ValidationError({
                'reports_to': _("المنصب الأعلى يجب أن يكون من نفس الشركة")
            })

        # التحقق من نطاق الراتب
        if self.min_salary and self.max_salary and self.min_salary > self.max_salary:
            raise ValidationError({
                'min_salary': _("الحد الأدنى للراتب يجب ألا يتجاوز الحد الأقصى")
            })


class JobOpeningStatus(models.TextChoices):
    """
    خيارات حالة الوظيفة الشاغرة
    """
    DRAFT = 'draft', _('مسودة')
    OPEN = 'open', _('مفتوحة')
    INTERVIEWING = 'interviewing', _('مقابلات')
    OFFERING = 'offering', _('عرض وظيفي')
    FILLED = 'filled', _('تم شغلها')
    CANCELED = 'canceled', _('ملغاة')


class JobOpening(HrBaseModel):
    """
    نموذج الوظيفة الشاغرة

    يمثل إعلان عن وظيفة شاغرة للتوظيف
    """
    title = models.CharField(
        max_length=200,
        verbose_name=_("عنوان الوظيفة")
    )

    job_position = models.ForeignKey(
        JobPosition,
        on_delete=models.CASCADE,
        related_name='job_openings',
        verbose_name=_("المنصب الوظيفي")
    )

    department = models.ForeignKey(
        'core.Department',
        on_delete=models.CASCADE,
        related_name='job_openings',
        verbose_name=_("القسم")
    )

    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='job_openings',
        verbose_name=_("الشركة")
    )

    location = models.ForeignKey(
        'core.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_openings',
        verbose_name=_("الموقع")
    )

    job_type = models.CharField(
        max_length=20,
        choices=[
            ('full_time', _("دوام كامل")),
            ('part_time', _("دوام جزئي")),
            ('contract', _("عقد")),
            ('temporary', _("مؤقت")),
            ('internship', _("تدريب"))
        ],
        default='full_time',
        verbose_name=_("نوع الوظيفة")
    )

    status = models.CharField(
        max_length=20,
        choices=JobOpeningStatus.choices,
        default=JobOpeningStatus.DRAFT,
        verbose_name=_("الحالة")
    )

    hiring_manager = models.ForeignKey(
        'employee.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_job_openings',
        verbose_name=_("مسؤول التوظيف")
    )

    published_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ النشر")
    )

    closing_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الإغلاق")
    )

    number_of_vacancies = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("عدد الشواغر")
    )

    description = models.TextField(
        verbose_name=_("وصف الوظيفة")
    )

    requirements = models.TextField(
        verbose_name=_("المتطلبات")
    )

    salary_from = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الراتب من")
    )

    salary_to = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الراتب إلى")
    )

    hide_salary = models.BooleanField(
        default=True,
        verbose_name=_("إخفاء الراتب")
    )

    external_link = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("رابط خارجي")
    )

    class Meta:
        verbose_name = _("وظيفة شاغرة")
        verbose_name_plural = _("الوظائف الشاغرة")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def clean(self):
        """
        التحقق من صحة البيانات قبل الحفظ
        """
        # التأكد من أن المنصب الوظيفي ينتمي لنفس الشركة
        if self.job_position and self.job_position.company != self.company:
            raise ValidationError({
                'job_position': _("المنصب الوظيفي يجب أن يكون من نفس الشركة")
            })

        # التأكد من أن القسم ينتمي لنفس الشركة
        if self.department and self.department.company != self.company:
            raise ValidationError({
                'department': _("القسم يجب أن يكون من نفس الشركة")
            })

        # التأكد من أن الموقع ينتمي لنفس الشركة
        if self.location and self.location.company != self.company:
            raise ValidationError({
                'location': _("الموقع يجب أن يكون من نفس الشركة")
            })

        # التحقق من نطاق الراتب
        if self.salary_from and self.salary_to and self.salary_from > self.salary_to:
            raise ValidationError({
                'salary_from': _("الحد الأدنى للراتب يجب ألا يتجاوز الحد الأقصى")
            })
