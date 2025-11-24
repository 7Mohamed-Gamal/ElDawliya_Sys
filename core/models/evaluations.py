"""
نماذج التقييمات المحسنة
Enhanced Evaluation Models
"""
from decimal import Decimal
from datetime import date, timedelta
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .base import BaseModel, AuditableModel
from .hr import Employee


class EvaluationPeriod(BaseModel):
    """فترات التقييم المحسنة"""
    PERIOD_TYPES = [
        ('annual', _('سنوي')),
        ('semi_annual', _('نصف سنوي')),
        ('quarterly', _('ربع سنوي')),
        ('monthly', _('شهري')),
        ('probation', _('فترة تجربة')),
        ('project', _('مشروع')),
        ('custom', _('مخصص')),
    ]

    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('active', _('نشط')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغى')),
    ]

    name = models.CharField(max_length=200, verbose_name=_('اسم فترة التقييم'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES, default='annual', verbose_name=_('نوع الفترة'))

    # Period Dates
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    evaluation_deadline = models.DateField(verbose_name=_('الموعد النهائي للتقييم'))

    # Status and Settings
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))
    is_mandatory = models.BooleanField(default=True, verbose_name=_('إجباري'))
    auto_create_evaluations = models.BooleanField(default=True, verbose_name=_('إنشاء التقييمات تلقائياً'))

    # Notification Settings
    reminder_days_before = models.PositiveIntegerField(default=7, verbose_name=_('تذكير قبل (أيام)'))
    send_notifications = models.BooleanField(default=True, verbose_name=_('إرسال إشعارات'))

    class Meta:
        """Meta class"""
        verbose_name = _('فترة تقييم')
        verbose_name_plural = _('فترات التقييم')
        ordering = ['-start_date']

    def __str__(self):
        """__str__ function"""
        return self.name

    @property
    def is_current(self):
        """فحص إذا كانت الفترة حالية"""
        today = date.today()
        return self.start_date <= today <= self.end_date

    @property
    def is_overdue(self):
        """فحص إذا كانت الفترة متأخرة"""
        return date.today() > self.evaluation_deadline

    @property
    def days_remaining(self):
        """الأيام المتبقية للموعد النهائي"""
        if self.evaluation_deadline:
            delta = self.evaluation_deadline - date.today()
            return delta.days if delta.days > 0 else 0
        return 0

    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}

        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                errors['end_date'] = _('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')

        if self.evaluation_deadline and self.end_date:
            if self.evaluation_deadline < self.end_date:
                errors['evaluation_deadline'] = _('الموعد النهائي يجب أن يكون بعد تاريخ نهاية الفترة')

        if errors:
            raise ValidationError(errors)

    def activate(self):
        """تفعيل فترة التقييم"""
        if self.status == 'draft':
            self.status = 'active'
            self.save()

            if self.auto_create_evaluations:
                self.create_evaluations_for_all_employees()

    def create_evaluations_for_all_employees(self):
        """إنشاء تقييمات لجميع الموظفين النشطين"""
        active_employees = Employee.objects.filter(
            emp_status='active',
            hire_date__lte=self.end_date
        )

        for employee in active_employees:
            EmployeeEvaluation.objects.get_or_create(
                employee=employee,
                period=self,
                defaults={
                    'evaluator': employee.manager,
                    'created_by': self.created_by
                }
            )


class EvaluationTemplate(BaseModel):
    """قوالب التقييم"""
    name = models.CharField(max_length=200, verbose_name=_('اسم القالب'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))

    # Template Settings
    is_default = models.BooleanField(default=False, verbose_name=_('قالب افتراضي'))
    is_system_template = models.BooleanField(default=False, verbose_name=_('قالب النظام'))

    # Scoring Settings
    max_score = models.PositiveIntegerField(default=100, verbose_name=_('الدرجة القصوى'))
    passing_score = models.PositiveIntegerField(default=60, verbose_name=_('درجة النجاح'))

    # Applicable To - Temporarily disabled until HR app is restored
    # departments = models.ManyToManyField('hr.Department', blank=True, verbose_name=_('الأقسام'))
    # job_positions = models.ManyToManyField('hr.JobPosition', blank=True, verbose_name=_('المناصب'))

    class Meta:
        """Meta class"""
        verbose_name = _('قالب تقييم')
        verbose_name_plural = _('قوالب التقييم')
        ordering = ['name']

    def __str__(self):
        """__str__ function"""
        return self.name

    def is_applicable_to_employee(self, employee):
        """فحص إذا كان القالب قابل للتطبيق على الموظف"""
        # فحص الأقسام
        if self.departments.exists():
            if not self.departments.filter(id=employee.department.id).exists():
                return False

        # فحص المناصب
        if self.job_positions.exists():
            if not self.job_positions.filter(id=employee.job_position.id).exists():
                return False

        return True


class EvaluationCriteria(BaseModel):
    """معايير التقييم"""
    CRITERIA_TYPES = [
        ('performance', _('الأداء')),
        ('behavior', _('السلوك')),
        ('skills', _('المهارات')),
        ('goals', _('الأهداف')),
        ('competency', _('الكفاءة')),
        ('leadership', _('القيادة')),
        ('teamwork', _('العمل الجماعي')),
        ('communication', _('التواصل')),
        ('innovation', _('الابتكار')),
        ('customer_service', _('خدمة العملاء')),
    ]

    template = models.ForeignKey(EvaluationTemplate, on_delete=models.CASCADE, related_name='criteria', verbose_name=_('القالب'))
    name = models.CharField(max_length=200, verbose_name=_('اسم المعيار'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    criteria_type = models.CharField(max_length=20, choices=CRITERIA_TYPES, verbose_name=_('نوع المعيار'))

    # Scoring
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1, verbose_name=_('الوزن'))
    max_score = models.PositiveIntegerField(default=5, verbose_name=_('الدرجة القصوى'))

    # Display
    order = models.PositiveIntegerField(default=0, verbose_name=_('الترتيب'))
    is_required = models.BooleanField(default=True, verbose_name=_('مطلوب'))

    class Meta:
        """Meta class"""
        verbose_name = _('معيار تقييم')
        verbose_name_plural = _('معايير التقييم')
        ordering = ['template', 'order', 'name']

    def __str__(self):
        """__str__ function"""
        return f"{self.template.name} - {self.name}"

    @property
    def weighted_max_score(self):
        """الدرجة القصوى المرجحة"""
        return float(self.max_score) * float(self.weight)


class EmployeeEvaluation(AuditableModel):
    """تقييمات الموظفين المحسنة"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('self_assessment', _('تقييم ذاتي')),
        ('manager_review', _('مراجعة المدير')),
        ('hr_review', _('مراجعة الموارد البشرية')),
        ('completed', _('مكتمل')),
        ('approved', _('معتمد')),
        ('rejected', _('مرفوض')),
    ]

    OVERALL_RATINGS = [
        ('outstanding', _('متميز')),
        ('exceeds_expectations', _('يفوق التوقعات')),
        ('meets_expectations', _('يلبي التوقعات')),
        ('below_expectations', _('أقل من التوقعات')),
        ('unsatisfactory', _('غير مرضي')),
    ]

    # Basic Information
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='evaluations', verbose_name=_('الموظف'))
    period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE, related_name='evaluations', verbose_name=_('فترة التقييم'))
    template = models.ForeignKey(EvaluationTemplate, on_delete=models.PROTECT, blank=True, null=True, verbose_name=_('قالب التقييم'))

    # Evaluators
    evaluator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='conducted_evaluations', verbose_name=_('المقيم'))
    secondary_evaluator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='secondary_evaluations', verbose_name=_('المقيم الثانوي'))

    # Status and Dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))
    evaluation_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ التقييم'))
    due_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الاستحقاق'))
    completed_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الإكمال'))

    # Scores
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_('إجمالي الدرجة'))
    max_possible_score = models.DecimalField(max_digits=6, decimal_places=2, default=100, verbose_name=_('الدرجة القصوى الممكنة'))
    percentage_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_('النسبة المئوية'))
    overall_rating = models.CharField(max_length=20, choices=OVERALL_RATINGS, blank=True, null=True, verbose_name=_('التقييم العام'))

    # Comments and Feedback
    employee_comments = models.TextField(blank=True, null=True, verbose_name=_('تعليقات الموظف'))
    evaluator_comments = models.TextField(blank=True, null=True, verbose_name=_('تعليقات المقيم'))
    strengths = models.TextField(blank=True, null=True, verbose_name=_('نقاط القوة'))
    areas_for_improvement = models.TextField(blank=True, null=True, verbose_name=_('مجالات التحسين'))
    development_plan = models.TextField(blank=True, null=True, verbose_name=_('خطة التطوير'))

    # Goals and Objectives
    goals_achieved = models.TextField(blank=True, null=True, verbose_name=_('الأهداف المحققة'))
    goals_for_next_period = models.TextField(blank=True, null=True, verbose_name=_('أهداف الفترة القادمة'))

    # Approval Workflow
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_evaluations', verbose_name=_('معتمد بواسطة'))
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الاعتماد'))

    # Self Assessment
    self_assessment_completed = models.BooleanField(default=False, verbose_name=_('اكتمل التقييم الذاتي'))
    self_assessment_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ التقييم الذاتي'))

    class Meta:
        """Meta class"""
        verbose_name = _('تقييم موظف')
        verbose_name_plural = _('تقييمات الموظفين')
        unique_together = ['employee', 'period']
        ordering = ['-period__start_date', 'employee__emp_code']

    def __str__(self):
        """__str__ function"""
        return f"{self.employee.get_full_name()} - {self.period.name}"

    @property
    def is_overdue(self):
        """فحص إذا كان التقييم متأخر"""
        if self.due_date and self.status not in ['completed', 'approved']:
            return date.today() > self.due_date
        return False

    @property
    def performance_level(self):
        """تحديد مستوى الأداء بناءً على النسبة المئوية"""
        if self.percentage_score >= 90:
            return 'outstanding'
        elif self.percentage_score >= 80:
            return 'exceeds_expectations'
        elif self.percentage_score >= 70:
            return 'meets_expectations'
        elif self.percentage_score >= 60:
            return 'below_expectations'
        else:
            return 'unsatisfactory'

    def calculate_total_score(self):
        """حساب إجمالي الدرجة"""
        criteria_scores = self.criteria_scores.all()

        total_weighted_score = 0
        total_possible_weighted_score = 0

        for score in criteria_scores:
            weighted_score = float(score.score) * float(score.criteria.weight)
            weighted_max_score = float(score.criteria.max_score) * float(score.criteria.weight)

            total_weighted_score += weighted_score
            total_possible_weighted_score += weighted_max_score

        self.total_score = Decimal(str(total_weighted_score))
        self.max_possible_score = Decimal(str(total_possible_weighted_score))

        # حساب النسبة المئوية
        if self.max_possible_score > 0:
            self.percentage_score = (self.total_score / self.max_possible_score * 100).quantize(Decimal('0.01'))
        else:
            self.percentage_score = 0

        # تحديد التقييم العام
        self.overall_rating = self.performance_level

    def complete_evaluation(self, completed_by=None):
        """إكمال التقييم"""
        if self.status in ['draft', 'self_assessment', 'manager_review']:
            self.calculate_total_score()
            self.status = 'completed'
            self.completed_date = date.today()
            if completed_by:
                self.updated_by = completed_by.user_account
            self.save()

    def approve(self, approved_by):
        """اعتماد التقييم"""
        if self.status == 'completed':
            self.status = 'approved'
            self.approved_by = approved_by
            self.approved_at = timezone.now()
            self.save()

    def save(self, *args, **kwargs):
        """حفظ محسن مع تحديد القالب والتاريخ المستحق"""
        # تحديد القالب إذا لم يكن محدداً
        if not self.template:
            default_template = EvaluationTemplate.objects.filter(is_default=True).first()
            if default_template and default_template.is_applicable_to_employee(self.employee):
                self.template = default_template

        # تحديد التاريخ المستحق
        if not self.due_date and self.period:
            self.due_date = self.period.evaluation_deadline

        super().save(*args, **kwargs)


class EvaluationCriteriaScore(BaseModel):
    """درجات معايير التقييم"""
    evaluation = models.ForeignKey(EmployeeEvaluation, on_delete=models.CASCADE, related_name='criteria_scores', verbose_name=_('التقييم'))
    criteria = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE, verbose_name=_('المعيار'))

    # Scores
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('الدرجة'))
    self_assessment_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_('درجة التقييم الذاتي'))

    # Comments
    comments = models.TextField(blank=True, null=True, verbose_name=_('التعليقات'))
    self_assessment_comments = models.TextField(blank=True, null=True, verbose_name=_('تعليقات التقييم الذاتي'))

    # Evidence and Examples
    evidence = models.TextField(blank=True, null=True, verbose_name=_('الأدلة والأمثلة'))
    improvement_suggestions = models.TextField(blank=True, null=True, verbose_name=_('اقتراحات التحسين'))

    class Meta:
        """Meta class"""
        verbose_name = _('درجة معيار التقييم')
        verbose_name_plural = _('درجات معايير التقييم')
        unique_together = ['evaluation', 'criteria']
        ordering = ['criteria__order']

    def __str__(self):
        """__str__ function"""
        return f"{self.evaluation} - {self.criteria.name}: {self.score}"

    @property
    def weighted_score(self):
        """الدرجة المرجحة"""
        return float(self.score) * float(self.criteria.weight)

    @property
    def percentage_score(self):
        """النسبة المئوية للدرجة"""
        if self.criteria.max_score > 0:
            return (float(self.score) / float(self.criteria.max_score)) * 100
        return 0

    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}

        if self.score > self.criteria.max_score:
            errors['score'] = _('الدرجة لا يمكن أن تتجاوز الحد الأقصى: {}').format(self.criteria.max_score)

        if self.score < 0:
            errors['score'] = _('الدرجة لا يمكن أن تكون سالبة')

        if self.self_assessment_score is not None:
            if self.self_assessment_score > self.criteria.max_score:
                errors['self_assessment_score'] = _('درجة التقييم الذاتي لا يمكن أن تتجاوز الحد الأقصى: {}').format(self.criteria.max_score)

            if self.self_assessment_score < 0:
                errors['self_assessment_score'] = _('درجة التقييم الذاتي لا يمكن أن تكون سالبة')

        if errors:
            raise ValidationError(errors)


class EvaluationGoal(BaseModel):
    """أهداف التقييم"""
    GOAL_STATUS = [
        ('not_started', _('لم يبدأ')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
        ('exceeded', _('تم تجاوزه')),
        ('not_achieved', _('لم يتحقق')),
    ]

    PRIORITY_LEVELS = [
        ('low', _('منخفض')),
        ('medium', _('متوسط')),
        ('high', _('عالي')),
        ('critical', _('حرج')),
    ]

    evaluation = models.ForeignKey(EmployeeEvaluation, on_delete=models.CASCADE, related_name='goals', verbose_name=_('التقييم'))
    title = models.CharField(max_length=200, verbose_name=_('عنوان الهدف'))
    description = models.TextField(verbose_name=_('وصف الهدف'))

    # Goal Details
    target_date = models.DateField(verbose_name=_('التاريخ المستهدف'))
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium', verbose_name=_('الأولوية'))
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1, verbose_name=_('الوزن'))

    # Progress Tracking
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='not_started', verbose_name=_('الحالة'))
    progress_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name=_('نسبة الإنجاز'))
    achievement_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_('درجة الإنجاز'))

    # Comments
    progress_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات التقدم'))
    final_comments = models.TextField(blank=True, null=True, verbose_name=_('التعليقات النهائية'))

    class Meta:
        """Meta class"""
        verbose_name = _('هدف التقييم')
        verbose_name_plural = _('أهداف التقييم')
        ordering = ['-priority', 'target_date']

    def __str__(self):
        """__str__ function"""
        return f"{self.evaluation.employee.get_full_name()} - {self.title}"

    @property
    def is_overdue(self):
        """فحص إذا كان الهدف متأخر"""
        return date.today() > self.target_date and self.status not in ['completed', 'exceeded']

    @property
    def days_remaining(self):
        """الأيام المتبقية للهدف"""
        if self.target_date:
            delta = self.target_date - date.today()
            return delta.days if delta.days > 0 else 0
        return 0
