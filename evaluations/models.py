from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from employees.models import Employee


class EvaluationPeriod(models.Model):
    """EvaluationPeriod class"""
    period_id = models.AutoField(primary_key=True, db_column='PeriodID')
    period_name = models.CharField(max_length=100, db_column='PeriodName', verbose_name='اسم الفترة')
    start_date = models.DateField(db_column='StartDate', verbose_name='تاريخ البداية')
    end_date = models.DateField(db_column='EndDate', verbose_name='تاريخ النهاية')
    is_active = models.BooleanField(default=True, db_column='IsActive', verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, db_column='CreatedAt', verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'EvaluationPeriods'
        verbose_name = 'فترة تقييم'
        verbose_name_plural = 'فترات التقييم'
        ordering = ['-start_date']

    def __str__(self):
        """__str__ function"""
        return self.period_name

    def clean(self):
        """clean function"""
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('تاريخ البداية يجب أن يكون قبل تاريخ النهاية')


class EmployeeEvaluation(models.Model):
    """EmployeeEvaluation class"""
    EVALUATION_STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('submitted', 'مقدم'),
        ('approved', 'معتمد'),
        ('rejected', 'مرفوض'),
    ]

    eval_id = models.AutoField(primary_key=True, db_column='EvalID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID',
                           related_name='evaluations', verbose_name='الموظف')
    period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE, db_column='PeriodID',
                              related_name='evaluations', verbose_name='فترة التقييم')
    manager_id = models.IntegerField(db_column='ManagerID', blank=True, null=True, verbose_name='المدير المقيم')
    score = models.DecimalField(max_digits=5, decimal_places=2, db_column='Score',
                               blank=True, null=True, verbose_name='الدرجة',
                               validators=[MinValueValidator(0), MaxValueValidator(100)])
    notes = models.TextField(db_column='Notes', blank=True, null=True, verbose_name='ملاحظات')
    eval_date = models.DateField(db_column='EvalDate', blank=True, null=True, verbose_name='تاريخ التقييم')
    status = models.CharField(max_length=20, choices=EVALUATION_STATUS_CHOICES,
                             default='draft', db_column='Status', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, db_column='CreatedAt', verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, db_column='UpdatedAt', verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeEvaluations'
        verbose_name = 'تقييم موظف'
        verbose_name_plural = 'تقييمات الموظفين'
        unique_together = ['emp', 'period']
        ordering = ['-eval_date', '-created_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.emp} - {self.period}"

    def clean(self):
        """clean function"""
        from django.core.exceptions import ValidationError
        if self.score is not None and (self.score < 0 or self.score > 100):
            raise ValidationError('الدرجة يجب أن تكون بين 0 و 100')

    @property
    def performance_level(self):
        """تحديد مستوى الأداء بناءً على الدرجة"""
        if self.score is None:
            return 'غير محدد'
        elif self.score >= 90:
            return 'ممتاز'
        elif self.score >= 80:
            return 'جيد جداً'
        elif self.score >= 70:
            return 'جيد'
        elif self.score >= 60:
            return 'مقبول'
        else:
            return 'ضعيف'

    def get_manager_name(self):
        """الحصول على اسم المدير"""
        if self.manager_id:
            try:
                from employees.models import Employee
                manager = Employee.objects.get(emp_id=self.manager_id)
                return f"{manager.first_name} {manager.last_name}"
            except Employee.DoesNotExist:
                return f"Manager ID: {self.manager_id}"
        return ''
