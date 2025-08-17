"""
Employee Training and Development Models for HRMS
Enhanced training management system
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from datetime import date, timedelta


class TrainingCategory(models.Model):
    """
    Training categories for better organization
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
        default='🎓',
        verbose_name=_("الأيقونة")
    )
    
    color = models.CharField(
        max_length=7,
        default='#28a745',
        verbose_name=_("اللون")
    )
    
    is_mandatory = models.BooleanField(
        default=False,
        verbose_name=_("إجباري"),
        help_text=_("هل هذا النوع من التدريب إجباري؟")
    )
    
    renewal_period_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("فترة التجديد (شهور)"),
        help_text=_("كم شهر قبل انتهاء صلاحية الشهادة؟")
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
        verbose_name = _("فئة التدريب")
        verbose_name_plural = _("فئات التدريب")
        db_table = 'hrms_training_category'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class TrainingProvider(models.Model):
    """
    Training providers and institutions
    """
    name = models.CharField(
        max_length=200,
        verbose_name=_("اسم مقدم التدريب")
    )
    
    name_en = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("الاسم بالإنجليزية")
    )
    
    PROVIDER_TYPES = [
        ('internal', _('داخلي')),
        ('external', _('خارجي')),
        ('university', _('جامعة')),
        ('institute', _('معهد')),
        ('online', _('منصة إلكترونية')),
        ('consultant', _('استشاري')),
        ('government', _('حكومي')),
    ]
    
    provider_type = models.CharField(
        max_length=20,
        choices=PROVIDER_TYPES,
        verbose_name=_("نوع مقدم التدريب")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف")
    )
    
    # Contact Information
    contact_person = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الشخص المسؤول")
    )
    
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الهاتف")
    )
    
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني")
    )
    
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("الموقع الإلكتروني")
    )
    
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("العنوان")
    )
    
    # Rating and Accreditation
    accreditation_body = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("جهة الاعتماد")
    )
    
    accreditation_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("رقم الاعتماد")
    )
    
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name=_("التقييم (من 5)")
    )
    
    is_preferred = models.BooleanField(
        default=False,
        verbose_name=_("مقدم مفضل")
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
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("مقدم التدريب")
        verbose_name_plural = _("مقدمو التدريب")
        db_table = 'hrms_training_provider'
        ordering = ['-is_preferred', 'name']
    
    def __str__(self):
        return self.name


class EmployeeTrainingEnhanced(models.Model):
    """
    Enhanced Employee Training model with comprehensive features
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
        related_name='trainings',
        verbose_name=_("الموظف")
    )
    
    # Training Information
    title = models.CharField(
        max_length=200,
        verbose_name=_("عنوان التدريب")
    )
    
    title_en = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("العنوان بالإنجليزية")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف التدريب")
    )
    
    category = models.ForeignKey(
        TrainingCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trainings',
        verbose_name=_("فئة التدريب")
    )
    
    provider = models.ForeignKey(
        TrainingProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trainings',
        verbose_name=_("مقدم التدريب")
    )
    
    # Training Details
    TRAINING_TYPES = [
        ('course', _('دورة تدريبية')),
        ('workshop', _('ورشة عمل')),
        ('seminar', _('ندوة')),
        ('conference', _('مؤتمر')),
        ('certification', _('شهادة مهنية')),
        ('degree', _('درجة علمية')),
        ('online', _('تدريب إلكتروني')),
        ('on_job', _('تدريب على رأس العمل')),
        ('mentoring', _('إرشاد مهني')),
    ]
    
    training_type = models.CharField(
        max_length=20,
        choices=TRAINING_TYPES,
        verbose_name=_("نوع التدريب")
    )
    
    DELIVERY_METHODS = [
        ('in_person', _('حضوري')),
        ('online', _('إلكتروني')),
        ('hybrid', _('مختلط')),
        ('self_paced', _('ذاتي السرعة')),
    ]
    
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHODS,
        default='in_person',
        verbose_name=_("طريقة التقديم")
    )
    
    # Dates and Duration
    start_date = models.DateField(
        verbose_name=_("تاريخ البداية")
    )
    
    end_date = models.DateField(
        verbose_name=_("تاريخ النهاية")
    )
    
    duration_hours = models.PositiveIntegerField(
        verbose_name=_("مدة التدريب (ساعات)")
    )
    
    # Location
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("مكان التدريب")
    )
    
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المدينة")
    )
    
    country = models.CharField(
        max_length=100,
        default="مصر",
        verbose_name=_("الدولة")
    )
    
    # Cost and Budget
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("التكلفة")
    )
    
    currency = models.CharField(
        max_length=3,
        default='EGP',
        verbose_name=_("العملة")
    )
    
    budget_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("رمز الميزانية")
    )
    
    # Status and Progress
    STATUS_CHOICES = [
        ('planned', _('مخطط')),
        ('approved', _('معتمد')),
        ('registered', _('مسجل')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
        ('postponed', _('مؤجل')),
        ('failed', _('فاشل')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name=_("الحالة")
    )
    
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=_("نسبة الإنجاز (%)")
    )
    
    # Assessment and Results
    has_assessment = models.BooleanField(
        default=False,
        verbose_name=_("يتضمن تقييم")
    )
    
    assessment_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("درجة التقييم")
    )
    
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الدرجة العظمى")
    )
    
    pass_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("درجة النجاح")
    )
    
    is_passed = models.BooleanField(
        default=False,
        verbose_name=_("نجح في التقييم")
    )
    
    # Certification
    has_certificate = models.BooleanField(
        default=False,
        verbose_name=_("يحصل على شهادة")
    )
    
    certificate_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("رقم الشهادة")
    )
    
    certificate_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الشهادة")
    )
    
    certificate_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء الشهادة")
    )
    
    certificate_file = models.FileField(
        upload_to='training_certificates/',
        null=True,
        blank=True,
        verbose_name=_("ملف الشهادة")
    )
    
    # Approval Workflow
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_trainings',
        verbose_name=_("طلب بواسطة")
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_trainings',
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
    
    # Priority and Importance
    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('critical', _('حرجة')),
    ]
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_("الأولوية")
    )
    
    is_mandatory = models.BooleanField(
        default=False,
        verbose_name=_("إجباري")
    )
    
    # Skills and Competencies
    skills_gained = models.JSONField(
        default=list,
        verbose_name=_("المهارات المكتسبة"),
        help_text=_("قائمة بالمهارات التي تم اكتسابها")
    )
    
    competencies_improved = models.JSONField(
        default=list,
        verbose_name=_("الكفاءات المحسنة"),
        help_text=_("قائمة بالكفاءات التي تم تحسينها")
    )
    
    # Feedback and Evaluation
    employee_feedback = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("تقييم الموظف للتدريب")
    )
    
    employee_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("تقييم الموظف (من 5)")
    )
    
    trainer_feedback = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("تقييم المدرب للموظف")
    )
    
    trainer_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("تقييم المدرب (من 5)")
    )
    
    # Follow-up and Application
    follow_up_required = models.BooleanField(
        default=False,
        verbose_name=_("يتطلب متابعة")
    )
    
    follow_up_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ المتابعة")
    )
    
    application_plan = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("خطة تطبيق المعرفة المكتسبة")
    )
    
    # Additional Information
    prerequisites = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("المتطلبات المسبقة")
    )
    
    learning_objectives = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("أهداف التعلم")
    )
    
    materials_provided = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("المواد المقدمة")
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # System Fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_trainings',
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
        verbose_name = _("تدريب موظف")
        verbose_name_plural = _("تدريبات الموظفين")
        db_table = 'hrms_employee_training_enhanced'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['category']),
            models.Index(fields=['provider']),
            models.Index(fields=['priority']),
            models.Index(fields=['certificate_expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"
    
    def clean(self):
        """Validate training data"""
        super().clean()
        
        # Validate dates
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_("تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية"))
        
        # Validate assessment scores
        if self.assessment_score and self.max_score:
            if self.assessment_score > self.max_score:
                raise ValidationError(_("درجة التقييم لا يمكن أن تتجاوز الدرجة العظمى"))
        
        # Validate certificate dates
        if self.certificate_date and self.certificate_expiry_date:
            if self.certificate_date > self.certificate_expiry_date:
                raise ValidationError(_("تاريخ الشهادة لا يمكن أن يكون بعد تاريخ انتهائها"))
    
    def save(self, *args, **kwargs):
        """Override save to update calculated fields"""
        # Update progress based on status
        if self.status == 'completed':
            self.progress_percentage = 100
        elif self.status == 'in_progress':
            # Calculate progress based on dates if not manually set
            if self.progress_percentage == 0:
                total_days = (self.end_date - self.start_date).days
                elapsed_days = (date.today() - self.start_date).days
                if total_days > 0:
                    self.progress_percentage = min(100, max(0, int((elapsed_days / total_days) * 100)))
        
        # Update pass status based on scores
        if self.assessment_score and self.pass_score:
            self.is_passed = self.assessment_score >= self.pass_score
        
        super().save(*args, **kwargs)
    
    # Properties
    @property
    def duration_days(self):
        """Calculate training duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0
    
    @property
    def is_current(self):
        """Check if training is currently ongoing"""
        today = date.today()
        return (self.start_date <= today <= self.end_date and 
                self.status == 'in_progress')
    
    @property
    def is_upcoming(self):
        """Check if training is upcoming"""
        return self.start_date > date.today() and self.status in ['approved', 'registered']
    
    @property
    def is_overdue(self):
        """Check if training is overdue"""
        return (self.end_date < date.today() and 
                self.status not in ['completed', 'cancelled'])
    
    @property
    def certificate_is_expired(self):
        """Check if certificate is expired"""
        if self.certificate_expiry_date:
            return date.today() > self.certificate_expiry_date
        return False
    
    @property
    def certificate_expires_soon(self):
        """Check if certificate expires within 30 days"""
        if self.certificate_expiry_date:
            days_until_expiry = (self.certificate_expiry_date - date.today()).days
            return 0 <= days_until_expiry <= 30
        return False
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.assessment_score and self.max_score and self.max_score > 0:
            return round((self.assessment_score / self.max_score) * 100, 2)
        return None
    
    # Methods
    def get_status_display_with_icon(self):
        """Get status with icon"""
        status_icons = {
            'planned': '📋 مخطط',
            'approved': '✅ معتمد',
            'registered': '📝 مسجل',
            'in_progress': '🔄 قيد التنفيذ',
            'completed': '✅ مكتمل',
            'cancelled': '❌ ملغي',
            'postponed': '⏸️ مؤجل',
            'failed': '❌ فاشل',
        }
        return status_icons.get(self.status, self.get_status_display())
    
    def get_priority_display_with_icon(self):
        """Get priority with icon"""
        priority_icons = {
            'low': '🟢 منخفضة',
            'medium': '🟡 متوسطة',
            'high': '🟠 عالية',
            'critical': '🔴 حرجة',
        }
        return priority_icons.get(self.priority, self.get_priority_display())
    
    def approve(self, approved_by_user, notes=None):
        """Approve the training"""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        if notes:
            self.notes = f"{self.notes or ''}\nملاحظات الاعتماد: {notes}"
        self.save()
    
    def reject(self, reason):
        """Reject the training"""
        self.status = 'cancelled'
        self.rejection_reason = reason
        self.save()
    
    def start_training(self):
        """Start the training"""
        if self.status == 'approved' or self.status == 'registered':
            self.status = 'in_progress'
            self.save()
    
    def complete_training(self, certificate_info=None):
        """Complete the training"""
        self.status = 'completed'
        self.progress_percentage = 100
        
        if certificate_info:
            self.has_certificate = True
            self.certificate_number = certificate_info.get('number')
            self.certificate_date = certificate_info.get('date', date.today())
            self.certificate_expiry_date = certificate_info.get('expiry_date')
        
        self.save()
    
    def get_training_summary(self):
        """Get comprehensive training summary"""
        return {
            'id': str(self.id),
            'title': self.title,
            'employee': self.employee.full_name,
            'category': self.category.name if self.category else None,
            'provider': self.provider.name if self.provider else None,
            'type': self.get_training_type_display(),
            'delivery_method': self.get_delivery_method_display(),
            'status': self.get_status_display_with_icon(),
            'priority': self.get_priority_display_with_icon(),
            'dates': {
                'start': self.start_date,
                'end': self.end_date,
                'duration_days': self.duration_days,
                'duration_hours': self.duration_hours
            },
            'location': {
                'venue': self.location,
                'city': self.city,
                'country': self.country
            },
            'cost': {
                'amount': float(self.cost) if self.cost else None,
                'currency': self.currency,
                'budget_code': self.budget_code
            },
            'progress': {
                'percentage': self.progress_percentage,
                'is_current': self.is_current,
                'is_upcoming': self.is_upcoming,
                'is_overdue': self.is_overdue
            },
            'assessment': {
                'has_assessment': self.has_assessment,
                'score': float(self.assessment_score) if self.assessment_score else None,
                'max_score': float(self.max_score) if self.max_score else None,
                'success_rate': self.success_rate,
                'is_passed': self.is_passed
            },
            'certificate': {
                'has_certificate': self.has_certificate,
                'number': self.certificate_number,
                'date': self.certificate_date,
                'expiry_date': self.certificate_expiry_date,
                'is_expired': self.certificate_is_expired,
                'expires_soon': self.certificate_expires_soon
            },
            'skills': {
                'gained': self.skills_gained,
                'competencies_improved': self.competencies_improved
            },
            'feedback': {
                'employee_rating': self.employee_rating,
                'trainer_rating': self.trainer_rating,
                'employee_feedback': self.employee_feedback,
                'trainer_feedback': self.trainer_feedback
            }
        }
    
    @classmethod
    def get_upcoming_trainings(cls, employee=None, days_ahead=30):
        """Get upcoming trainings"""
        end_date = date.today() + timedelta(days=days_ahead)
        queryset = cls.objects.filter(
            start_date__gte=date.today(),
            start_date__lte=end_date,
            status__in=['approved', 'registered']
        )
        
        if employee:
            queryset = queryset.filter(employee=employee)
        
        return queryset.order_by('start_date')
    
    @classmethod
    def get_expiring_certificates(cls, employee=None, days_ahead=30):
        """Get certificates expiring soon"""
        end_date = date.today() + timedelta(days=days_ahead)
        queryset = cls.objects.filter(
            certificate_expiry_date__gte=date.today(),
            certificate_expiry_date__lte=end_date,
            has_certificate=True,
            status='completed'
        )
        
        if employee:
            queryset = queryset.filter(employee=employee)
        
        return queryset.order_by('certificate_expiry_date')
    
    @classmethod
    def get_training_statistics(cls, employee=None, year=None):
        """Get training statistics"""
        queryset = cls.objects.all()
        if employee:
            queryset = queryset.filter(employee=employee)
        if year:
            queryset = queryset.filter(start_date__year=year)
        
        stats = {
            'total': queryset.count(),
            'completed': queryset.filter(status='completed').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
            'planned': queryset.filter(status='planned').count(),
            'cancelled': queryset.filter(status='cancelled').count(),
            'total_hours': sum(t.duration_hours for t in queryset if t.duration_hours),
            'total_cost': sum(t.cost for t in queryset if t.cost),
            'certificates_earned': queryset.filter(has_certificate=True, status='completed').count(),
            'mandatory_completed': queryset.filter(is_mandatory=True, status='completed').count(),
            'average_rating': 0,
            'by_category': {},
            'by_provider': {},
            'by_priority': {}
        }
        
        # Calculate average rating
        ratings = [t.employee_rating for t in queryset if t.employee_rating]
        if ratings:
            stats['average_rating'] = sum(ratings) / len(ratings)
        
        # Count by category
        for training in queryset:
            if training.category:
                category_name = training.category.name
                stats['by_category'][category_name] = stats['by_category'].get(category_name, 0) + 1
        
        # Count by provider
        for training in queryset:
            if training.provider:
                provider_name = training.provider.name
                stats['by_provider'][provider_name] = stats['by_provider'].get(provider_name, 0) + 1
        
        # Count by priority
        for priority, _ in cls.PRIORITY_CHOICES:
            stats['by_priority'][priority] = queryset.filter(priority=priority).count()
        
        return stats
    
    def needs_follow_up(self):
        """Check if training needs follow-up"""
        if self.follow_up_required and self.follow_up_date:
            return date.today() >= self.follow_up_date
        return False
    
    def get_roi_estimate(self):
        """Estimate return on investment (basic calculation)"""
        if not self.cost:
            return None
        
        # Basic ROI calculation based on employee rating and skills gained
        base_value = float(self.cost) * 0.5  # Assume 50% base value
        
        if self.employee_rating:
            rating_multiplier = self.employee_rating / 5.0
            base_value *= rating_multiplier
        
        if self.skills_gained:
            skill_bonus = len(self.skills_gained) * 0.1 * float(self.cost)
            base_value += skill_bonus
        
        roi_percentage = ((base_value - float(self.cost)) / float(self.cost)) * 100
        
        return {
            'estimated_value': round(base_value, 2),
            'cost': float(self.cost),
            'roi_percentage': round(roi_percentage, 2),
            'calculation_method': 'basic_estimate'
        }