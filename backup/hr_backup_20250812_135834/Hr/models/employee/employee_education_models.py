"""
نماذج المؤهلات الدراسية للموظفين - النسخة المحسنة
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from datetime import date


class EmployeeEducationEnhanced(models.Model):
    """نموذج المؤهلات الدراسية المحسن للموظف"""
    
    DEGREE_CHOICES = [
        ('elementary', _('ابتدائية')),
        ('intermediate', _('متوسطة')),
        ('high_school', _('ثانوية عامة')),
        ('vocational', _('مهني')),
        ('diploma', _('دبلوم')),
        ('associate', _('دبلوم عالي')),
        ('bachelor', _('بكالوريوس')),
        ('master', _('ماجستير')),
        ('phd', _('دكتوراه')),
        ('certificate', _('شهادة مهنية')),
        ('training', _('دورة تدريبية')),
        ('professional', _('شهادة احترافية')),
    ]
    
    GRADE_SYSTEM_CHOICES = [
        ('percentage', _('نسبة مئوية')),
        ('gpa_4', _('GPA من 4')),
        ('gpa_5', _('GPA من 5')),
        ('letter', _('حروف (A, B, C)')),
        ('pass_fail', _('نجح/راسب')),
        ('honors', _('مرتبة الشرف')),
    ]
    
    STUDY_MODE_CHOICES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('distance', _('تعليم عن بُعد')),
        ('evening', _('مسائي')),
        ('weekend', _('نهاية الأسبوع')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced', 
        on_delete=models.CASCADE, 
        related_name='education_records_enhanced', 
        verbose_name=_('الموظف')
    )
    
    # Education Details
    degree_type = models.CharField(
        max_length=20, 
        choices=DEGREE_CHOICES, 
        verbose_name=_('نوع الشهادة')
    )
    
    major = models.CharField(
        max_length=200, 
        verbose_name=_('التخصص الرئيسي')
    )
    
    minor = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name=_('التخصص الفرعي')
    )
    
    institution = models.CharField(
        max_length=200, 
        verbose_name=_('الجامعة/المؤسسة')
    )
    
    institution_english = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name=_('اسم المؤسسة بالإنجليزية')
    )
    
    # Academic Information
    graduation_year = models.PositiveIntegerField(
        verbose_name=_('سنة التخرج'),
        validators=[
            MinValueValidator(1950),
            MaxValueValidator(date.today().year + 10)
        ]
    )
    
    start_year = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        verbose_name=_('سنة البداية'),
        validators=[
            MinValueValidator(1950),
            MaxValueValidator(date.today().year + 10)
        ]
    )
    
    study_duration_years = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('مدة الدراسة بالسنوات'),
        validators=[MinValueValidator(1), MaxValueValidator(15)]
    )
    
    study_mode = models.CharField(
        max_length=20,
        choices=STUDY_MODE_CHOICES,
        default='full_time',
        verbose_name=_('نظام الدراسة')
    )
    
    grade_system = models.CharField(
        max_length=20, 
        choices=GRADE_SYSTEM_CHOICES, 
        default='percentage', 
        verbose_name=_('نظام الدرجات')
    )
    
    grade = models.CharField(
        max_length=10, 
        blank=True, 
        null=True, 
        verbose_name=_('المعدل/الدرجة')
    )
    
    # Location
    country = models.CharField(
        max_length=100, 
        verbose_name=_('الدولة')
    )
    
    city = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name=_('المدينة')
    )
    
    # Verification
    is_verified = models.BooleanField(
        default=False, 
        verbose_name=_('تم التحقق')
    )
    
    verification_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('تاريخ التحقق')
    )
    
    verification_notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_('ملاحظات التحقق')
    )
    
    verified_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_education_records',
        verbose_name=_('تم التحقق بواسطة')
    )
    
    # Files
    certificate_file = models.FileField(
        upload_to='education/certificates/', 
        blank=True, 
        null=True, 
        verbose_name=_('ملف الشهادة')
    )
    
    transcript_file = models.FileField(
        upload_to='education/transcripts/', 
        blank=True, 
        null=True, 
        verbose_name=_('كشف الدرجات')
    )
    
    # Additional Information
    honors = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name=_('مرتبة الشرف')
    )
    
    thesis_title = models.CharField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name=_('عنوان الرسالة/المشروع')
    )
    
    thesis_title_en = models.CharField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name=_('عنوان الرسالة بالإنجليزية')
    )
    
    supervisor_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('اسم المشرف')
    )
    
    # Ranking and Recognition
    class_rank = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('الترتيب على الدفعة')
    )
    
    class_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('عدد طلاب الدفعة')
    )
    
    awards = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الجوائز والتكريمات')
    )
    
    # Relevance to Job
    is_relevant_to_job = models.BooleanField(
        default=True,
        verbose_name=_('مرتبط بالوظيفة')
    )
    
    relevance_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات الصلة بالوظيفة')
    )
    
    # Status and Timestamps
    is_active = models.BooleanField(
        default=True, 
        verbose_name=_('نشط')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('تاريخ الإنشاء')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('تاريخ التحديث')
    )
    
    created_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='created_education_records',
        verbose_name=_('تم الإنشاء بواسطة')
    )

    class Meta:
        verbose_name = _('مؤهل دراسي محسن')
        verbose_name_plural = _('المؤهلات الدراسية المحسنة')
        ordering = ['-graduation_year', 'degree_type']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['degree_type']),
            models.Index(fields=['graduation_year']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['country']),
            models.Index(fields=['is_relevant_to_job']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_year__lte=models.F('graduation_year')),
                name='start_before_graduation'
            ),
            models.CheckConstraint(
                check=models.Q(class_rank__lte=models.F('class_size')),
                name='rank_within_class_size'
            ),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_degree_type_display()} - {self.major}"

    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}
        
        if self.start_year and self.graduation_year and self.start_year > self.graduation_year:
            errors['graduation_year'] = _('سنة التخرج لا يمكن أن تكون أقل من سنة البداية')
        
        if self.graduation_year > date.today().year:
            errors['graduation_year'] = _('سنة التخرج لا يمكن أن تكون في المستقبل')
        
        if self.class_rank and self.class_size and self.class_rank > self.class_size:
            errors['class_rank'] = _('الترتيب لا يمكن أن يكون أكبر من عدد الطلاب')
        
        # التحقق من منطقية مدة الدراسة
        if self.start_year and self.graduation_year and self.study_duration_years:
            actual_duration = self.graduation_year - self.start_year + 1
            if abs(actual_duration - self.study_duration_years) > 2:
                errors['study_duration_years'] = _('مدة الدراسة لا تتطابق مع سنوات البداية والتخرج')
        
        if errors:
            raise ValidationError(errors)
    
    @property
    def study_duration_calculated(self):
        """حساب مدة الدراسة من سنة البداية والتخرج"""
        if self.start_year and self.graduation_year:
            return self.graduation_year - self.start_year + 1
        return None
    
    @property
    def years_since_graduation(self):
        """عدد السنوات منذ التخرج"""
        return date.today().year - self.graduation_year
    
    @property
    def is_recent_graduate(self):
        """هل هو خريج حديث (خلال 3 سنوات)"""
        return self.years_since_graduation <= 3
    
    @property
    def grade_percentage(self):
        """تحويل الدرجة إلى نسبة مئوية إذا أمكن"""
        if not self.grade:
            return None
        
        try:
            if self.grade_system == 'percentage':
                return float(self.grade)
            elif self.grade_system == 'gpa_4':
                return (float(self.grade) / 4.0) * 100
            elif self.grade_system == 'gpa_5':
                return (float(self.grade) / 5.0) * 100
            elif self.grade_system == 'letter':
                grade_map = {'A+': 95, 'A': 90, 'B+': 85, 'B': 80, 'C+': 75, 'C': 70, 'D': 60, 'F': 50}
                return grade_map.get(self.grade.upper(), None)
        except (ValueError, TypeError):
            return None
        
        return None
    
    @property
    def is_high_achiever(self):
        """هل هو متفوق أكاديمياً"""
        grade_pct = self.grade_percentage
        if grade_pct and grade_pct >= 85:
            return True
        if self.honors or self.awards:
            return True
        if self.class_rank and self.class_size and (self.class_rank / self.class_size) <= 0.1:
            return True
        return False
    
    def get_degree_level_order(self):
        """ترتيب مستوى الشهادة للفرز"""
        level_order = {
            'elementary': 1,
            'intermediate': 2,
            'high_school': 3,
            'vocational': 4,
            'certificate': 5,
            'diploma': 6,
            'associate': 7,
            'bachelor': 8,
            'master': 9,
            'phd': 10,
            'professional': 11,
            'training': 12,
        }
        return level_order.get(self.degree_type, 0)
    
    def save(self, *args, **kwargs):
        """تجاوز الحفظ لحساب مدة الدراسة تلقائياً"""
        if self.start_year and self.graduation_year and not self.study_duration_years:
            self.study_duration_years = self.graduation_year - self.start_year + 1
        
        self.full_clean()
        super().save(*args, **kwargs)