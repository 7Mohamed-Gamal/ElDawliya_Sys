from django.db import models
from django.utils.translation import gettext_lazy as _
from Hr.models.employee_model import Employee

class EmployeeEvaluation(models.Model):
    """
    Modelo para evaluaciones de empleados
    """
    RATING_CHOICES = [
        (1, _('ضعيف')),
        (2, _('مقبول')),
        (3, _('جيد')),
        (4, _('جيد جدا')),
        (5, _('ممتاز')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='evaluations', verbose_name=_('الموظف'))
    evaluation_date = models.DateField(verbose_name=_('تاريخ التقييم'))
    period_start = models.DateField(verbose_name=_('بداية فترة التقييم'))
    period_end = models.DateField(verbose_name=_('نهاية فترة التقييم'))
    evaluator = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, related_name='conducted_evaluations', verbose_name=_('المقيم'))
    
    # Criterios de evaluación
    performance_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name=_('تقييم الأداء'))
    attendance_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name=_('تقييم الحضور'))
    teamwork_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name=_('تقييم العمل الجماعي'))
    initiative_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name=_('تقييم المبادرة'))
    communication_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name=_('تقييم التواصل'))
    
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, verbose_name=_('التقييم الإجمالي'))
    strengths = models.TextField(verbose_name=_('نقاط القوة'))
    areas_for_improvement = models.TextField(verbose_name=_('مجالات التحسين'))
    goals = models.TextField(verbose_name=_('الأهداف للفترة القادمة'))
    employee_comments = models.TextField(blank=True, null=True, verbose_name=_('تعليقات الموظف'))
    is_acknowledged = models.BooleanField(default=False, verbose_name=_('تم الاطلاع من قبل الموظف'))
    acknowledgement_date = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الاطلاع'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.employee} - {self.evaluation_date}"

    def save(self, *args, **kwargs):
        # Calcular el promedio de las calificaciones
        ratings = [
            self.performance_rating,
            self.attendance_rating,
            self.teamwork_rating,
            self.initiative_rating,
            self.communication_rating
        ]
        self.overall_rating = sum(ratings) / len(ratings)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('تقييم الموظف')
        verbose_name_plural = _('تقييمات الموظفين')
        db_table = 'Hr_EmployeeEvaluation'
        ordering = ['-evaluation_date']
        managed = True
