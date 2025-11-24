from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Max, Min
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import date, datetime, timedelta
import logging
from .models import EvaluationPeriod, EmployeeEvaluation
from employees.models import Employee
from org.models import Department
from .forms import EvaluationPeriodForm, EmployeeEvaluationForm

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """لوحة تحكم التقييمات"""
    today = date.today()

    # إحصائيات عامة
    total_periods = EvaluationPeriod.objects.count()
    total_evaluations = EmployeeEvaluation.objects.count()
    completed_evaluations = EmployeeEvaluation.objects.filter(score__isnull=False).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
    pending_evaluations = EmployeeEvaluation.objects.filter(score__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

    # الفترة النشطة الحالية
    try:
        active_period = EvaluationPeriod.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()
    except Exception as e:
        logger.error(f"Error fetching active evaluation period: {str(e)}")
        active_period = None

    # إحصائيات الفترة النشطة
    active_period_stats = None
    if active_period:
        active_period_stats = EmployeeEvaluation.objects.filter(
            period=active_period
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.aggregate(
            total_evaluations=Count('eval_id'),
            completed_evaluations=Count('eval_id', filter=Q(score__isnull=False)),
            average_score=Avg('score'),
            highest_score=Max('score'),
            lowest_score=Min('score')
        )

    # أحدث التقييمات
    recent_evaluations = EmployeeEvaluation.objects.select_related(
        'emp', 'period'
    ).filter(score__isnull=False).order_by('-eval_date')[:5]

    # إحصائيات الأقسام
    department_stats = Department.objects.annotate(
        evaluation_count=Count('employee__evaluations'),
        avg_score=Avg('employee__evaluations__score')
    ).filter(evaluation_count__gt=0).order_by('-avg_score')[:5]

    # توزيع الدرجات
    score_distribution = EmployeeEvaluation.objects.filter(
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.extra(
        select={
            'score_range': """
                CASE
                    WHEN score >= 90 THEN 'ممتاز (90-100)'
                    WHEN score >= 80 THEN 'جيد جداً (80-89)'
                    WHEN score >= 70 THEN 'جيد (70-79)'
                    WHEN score >= 60 THEN 'مقبول (60-69)'
                    ELSE 'ضعيف (أقل من 60)'
                END
            """
        }
    ).values('score_range').annotate(
        count=Count('eval_id')
    ).order_by('-count')

    context = {
        'total_periods': total_periods,
        'total_evaluations': total_evaluations,
        'completed_evaluations': completed_evaluations,
        'pending_evaluations': pending_evaluations,
        'active_period': active_period,
        'active_period_stats': active_period_stats,
        'recent_evaluations': recent_evaluations,
        'department_stats': department_stats,
        'score_distribution': score_distribution,
    }

    return render(request, 'evaluations/dashboard.html', context)


@login_required
def evaluation_list(request):
    """قائمة التقييمات"""
    evaluations = EmployeeEvaluation.objects.select_related('emp', 'period').all()

    # البحث والفلترة
    search = request.GET.get('search')
    if search:
        evaluations = evaluations.filter(
            Q(emp__first_name__icontains=search) |
            Q(emp__last_name__icontains=search) |
            Q(emp__emp_code__icontains=search) |
            Q(notes__icontains=search)
        )

    # فلترة حسب الفترة
    period = request.GET.get('period')
    if period:
        evaluations = evaluations.filter(period_id=period)

    # فلترة حسب القسم
    department = request.GET.get('department')
    if department:
        evaluations = evaluations.filter(emp__dept_id=department)

    # فلترة حسب نطاق الدرجات
    score_range = request.GET.get('score_range')
    if score_range:
        if score_range == 'excellent':
            evaluations = evaluations.filter(score__gte=90)
        elif score_range == 'very_good':
            evaluations = evaluations.filter(score__gte=80, score__lt=90)
        elif score_range == 'good':
            evaluations = evaluations.filter(score__gte=70, score__lt=80)
        elif score_range == 'acceptable':
            evaluations = evaluations.filter(score__gte=60, score__lt=70)
        elif score_range == 'poor':
            evaluations = evaluations.filter(score__lt=60)
        elif score_range == 'pending':
            evaluations = evaluations.filter(score__isnull=True)

    # ترتيب النتائج
    evaluations = evaluations.order_by('-eval_date', '-score')

    # التقسيم إلى صفحات
    paginator = Paginator(evaluations, 20)
    page_number = request.GET.get('page')
    evaluations = paginator.get_page(page_number)

    # قوائم للفلترة
    periods = EvaluationPeriod.objects.all().select_related()  # TODO: Add appropriate select_related fields.order_by('-start_date')
    departments = Department.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('dept_name')

    context = {
        'evaluations': evaluations,
        'periods': periods,
        'departments': departments,
    }

    return render(request, 'evaluations/evaluation_list.html', context)


@login_required
def create_evaluation(request):
    """إنشاء تقييم جديد"""
    if request.method == 'POST':
        form = EmployeeEvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save()
            messages.success(request, f'تم إنشاء التقييم بنجاح.')
            return redirect('evaluations:evaluation_detail', eval_id=evaluation.eval_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeEvaluationForm()

    context = {
        'form': form,
        'title': 'تقييم جديد'
    }

    return render(request, 'evaluations/evaluation_form.html', context)


@login_required
def evaluation_detail(request, eval_id):
    """تفاصيل التقييم"""
    evaluation = get_object_or_404(EmployeeEvaluation, eval_id=eval_id)

    # تقييمات الموظف السابقة
    previous_evaluations = EmployeeEvaluation.objects.filter(
        emp=evaluation.emp,
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exclude(eval_id=eval_id).order_by('-eval_date')[:5]

    # حساب متوسط درجات الموظف
    employee_avg = EmployeeEvaluation.objects.filter(
        emp=evaluation.emp,
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.aggregate(avg_score=Avg('score'))['avg_score']

    # تحديد مستوى الأداء
    performance_level = None
    if evaluation.score:
        if evaluation.score >= 90:
            performance_level = 'ممتاز'
        elif evaluation.score >= 80:
            performance_level = 'جيد جداً'
        elif evaluation.score >= 70:
            performance_level = 'جيد'
        elif evaluation.score >= 60:
            performance_level = 'مقبول'
        else:
            performance_level = 'ضعيف'

    context = {
        'evaluation': evaluation,
        'previous_evaluations': previous_evaluations,
        'employee_avg': employee_avg,
        'performance_level': performance_level,
    }

    return render(request, 'evaluations/evaluation_detail.html', context)


@login_required
def edit_evaluation(request, eval_id):
    """تعديل تقييم"""
    evaluation = get_object_or_404(EmployeeEvaluation, eval_id=eval_id)

    if request.method == 'POST':
        form = EmployeeEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            evaluation = form.save()
            messages.success(request, 'تم تحديث التقييم بنجاح.')
            return redirect('evaluations:evaluation_detail', eval_id=evaluation.eval_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeEvaluationForm(instance=evaluation)

    context = {
        'form': form,
        'evaluation': evaluation,
        'title': 'تعديل التقييم'
    }

    return render(request, 'evaluations/evaluation_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_evaluation(request, eval_id):
    """حذف تقييم"""
    evaluation = get_object_or_404(EmployeeEvaluation, eval_id=eval_id)

    try:
        evaluation.delete()
        messages.success(request, 'تم حذف التقييم بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف التقييم: {str(e)}')

    return redirect('evaluations:evaluation_list')


@login_required
def print_evaluation(request, eval_id):
    """طباعة التقييم"""
    evaluation = get_object_or_404(EmployeeEvaluation, eval_id=eval_id)

    context = {
        'evaluation': evaluation,
    }

    return render(request, 'evaluations/evaluation_print.html', context)


# إدارة فترات التقييم
@login_required
def periods(request):
    """قائمة فترات التقييم"""
    periods = EvaluationPeriod.objects.annotate(
        evaluation_count=Count('evaluations'),
        completed_count=Count('evaluations', filter=Q(evaluations__score__isnull=False)),
        avg_score=Avg('evaluations__score')
    ).order_by('-start_date')

    context = {
        'periods': periods,
    }

    return render(request, 'evaluations/periods.html', context)


@login_required
def add_period(request):
    """إضافة فترة تقييم جديدة"""
    if request.method == 'POST':
        form = EvaluationPeriodForm(request.POST)
        if form.is_valid():
            period = form.save()
            messages.success(request, f'تم إضافة فترة التقييم {period.period_name} بنجاح.')
            return redirect('evaluations:periods')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EvaluationPeriodForm()

    context = {
        'form': form,
        'title': 'إضافة فترة تقييم جديدة'
    }

    return render(request, 'evaluations/period_form.html', context)


@login_required
def get_period(request, period_id):
    """عرض تفاصيل فترة التقييم"""
    period = get_object_or_404(EvaluationPeriod, period_id=period_id)

    # إحصائيات الفترة
    period_stats = EmployeeEvaluation.objects.filter(period=period).prefetch_related()  # TODO: Add appropriate prefetch_related fields.aggregate(
        total_evaluations=Count('eval_id'),
        completed_evaluations=Count('eval_id', filter=Q(score__isnull=False)),
        pending_evaluations=Count('eval_id', filter=Q(score__isnull=True)),
        average_score=Avg('score'),
        highest_score=Max('score'),
        lowest_score=Min('score')
    )

    # تقييمات الفترة
    evaluations = EmployeeEvaluation.objects.filter(
        period=period
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('emp').order_by('-score', 'emp__first_name')

    # توزيع الدرجات
    score_distribution = evaluations.filter(
        score__isnull=False
    ).extra(
        select={
            'score_range': """
                CASE
                    WHEN score >= 90 THEN 'ممتاز'
                    WHEN score >= 80 THEN 'جيد جداً'
                    WHEN score >= 70 THEN 'جيد'
                    WHEN score >= 60 THEN 'مقبول'
                    ELSE 'ضعيف'
                END
            """
        }
    ).values('score_range').annotate(
        count=Count('eval_id')
    )

    context = {
        'period': period,
        'period_stats': period_stats,
        'evaluations': evaluations,
        'score_distribution': score_distribution,
    }

    return render(request, 'evaluations/period_details.html', context)


@login_required
def update_period(request, period_id):
    """تحديث فترة التقييم"""
    period = get_object_or_404(EvaluationPeriod, period_id=period_id)

    if request.method == 'POST':
        form = EvaluationPeriodForm(request.POST, instance=period)
        if form.is_valid():
            period = form.save()
            messages.success(request, f'تم تحديث فترة التقييم {period.period_name} بنجاح.')
            return redirect('evaluations:get_period', period_id=period_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EvaluationPeriodForm(instance=period)

    context = {
        'form': form,
        'period': period,
        'title': 'تعديل فترة التقييم'
    }

    return render(request, 'evaluations/period_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_period(request, period_id):
    """حذف فترة التقييم"""
    period = get_object_or_404(EvaluationPeriod, period_id=period_id)

    try:
        # التحقق من وجود تقييمات مرتبطة
        if EmployeeEvaluation.objects.filter(period=period).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exists():
            messages.error(request, f'لا يمكن حذف فترة التقييم {period.period_name} لأنها تحتوي على تقييمات.')
        else:
            period.delete()
            messages.success(request, f'تم حذف فترة التقييم {period.period_name} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف فترة التقييم: {str(e)}')

    return redirect('evaluations:periods')


# التقارير
@login_required
def reports(request):
    """تقارير التقييمات"""
    today = date.today()

    # إحصائيات عامة
    total_evaluations = EmployeeEvaluation.objects.count()
    completed_evaluations = EmployeeEvaluation.objects.filter(score__isnull=False).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

    # متوسط الدرجات العام
    overall_avg = EmployeeEvaluation.objects.filter(
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.aggregate(avg_score=Avg('score'))['avg_score']

    # إحصائيات الأقسام
    department_stats = Department.objects.annotate(
        evaluation_count=Count('employee__evaluations'),
        completed_count=Count('employee__evaluations',
                            filter=Q(employee__evaluations__score__isnull=False)),
        avg_score=Avg('employee__evaluations__score')
    ).filter(evaluation_count__gt=0).order_by('-avg_score')

    # أفضل الموظفين
    top_performers = EmployeeEvaluation.objects.filter(
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('emp').order_by('-score')[:10]

    # توزيع الدرجات الشهري
    monthly_stats = EmployeeEvaluation.objects.filter(
        eval_date__isnull=False,
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.extra(
        select={'month': "MONTH(eval_date)", 'year': "YEAR(eval_date)"}
    ).values('month', 'year').annotate(
        count=Count('eval_id'),
        avg_score=Avg('score')
    ).order_by('year', 'month')

    context = {
        'total_evaluations': total_evaluations,
        'completed_evaluations': completed_evaluations,
        'overall_avg': overall_avg,
        'department_stats': department_stats,
        'top_performers': top_performers,
        'monthly_stats': monthly_stats,
    }

    return render(request, 'evaluations/reports.html', context)


@login_required
def export_evaluations(request):
    """تصدير بيانات التقييمات"""
    import csv

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="evaluations.csv"'

    writer = csv.writer(response)
    writer.writerow(['الموظف', 'الفترة', 'الدرجة', 'تاريخ التقييم', 'المقيم', 'الملاحظات'])

    evaluations = EmployeeEvaluation.objects.select_related('emp', 'period').all()
    for evaluation in evaluations:
        writer.writerow([
            evaluation.emp.get_full_name(),
            evaluation.period.period_name,
            evaluation.score or 'غير مكتمل',
            evaluation.eval_date or 'غير محدد',
            'غير محدد',  # Manager info not available in current model
            evaluation.notes or ''
        ])

    return response


@login_required
def performance_comparison(request):
    """مقارنة الأداء"""
    # مقارنة الأداء بين الموظفين والأقسام والفترات

    # أفضل الموظفين
    top_employees = EmployeeEvaluation.objects.filter(
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('emp').order_by('-score')[:10]

    # مقارنة الأقسام
    department_comparison = Department.objects.annotate(
        avg_score=Avg('employee__evaluations__score'),
        evaluation_count=Count('employee__evaluations')
    ).filter(evaluation_count__gt=0).order_by('-avg_score')

    # مقارنة الفترات
    period_comparison = EvaluationPeriod.objects.annotate(
        avg_score=Avg('evaluations__score'),
        evaluation_count=Count('evaluations')
    ).filter(evaluation_count__gt=0).order_by('-start_date')

    context = {
        'top_employees': top_employees,
        'department_comparison': department_comparison,
        'period_comparison': period_comparison,
    }

    return render(request, 'evaluations/performance_comparison.html', context)


# بوابة الموظف
@login_required
def my_evaluations(request):
    """تقييماتي الشخصية"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('evaluations:dashboard')

    employee = request.user.employee

    # تقييمات الموظف
    my_evaluations = EmployeeEvaluation.objects.filter(
        emp=employee
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('period').order_by('-eval_date')

    # إحصائيات شخصية
    personal_stats = my_evaluations.filter(score__isnull=False).aggregate(
        total_evaluations=Count('eval_id'),
        average_score=Avg('score'),
        highest_score=Max('score'),
        lowest_score=Min('score')
    )

    context = {
        'my_evaluations': my_evaluations,
        'personal_stats': personal_stats,
        'employee': employee,
    }

    return render(request, 'evaluations/my_evaluations.html', context)


@login_required
def my_performance(request):
    """أدائي الشخصي"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('evaluations:dashboard')

    employee = request.user.employee

    # تطور الأداء عبر الوقت
    performance_trend = EmployeeEvaluation.objects.filter(
        emp=employee,
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('eval_date')

    # مقارنة مع متوسط القسم
    department_avg = EmployeeEvaluation.objects.filter(
        emp__dept=employee.dept,
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.aggregate(avg_score=Avg('score'))['avg_score']

    # مقارنة مع متوسط الشركة
    company_avg = EmployeeEvaluation.objects.filter(
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.aggregate(avg_score=Avg('score'))['avg_score']

    context = {
        'employee': employee,
        'performance_trend': performance_trend,
        'department_avg': department_avg,
        'company_avg': company_avg,
    }

    return render(request, 'evaluations/my_performance.html', context)


# AJAX Views
@login_required
def employee_performance_ajax(request, emp_id):
    """جلب أداء الموظف عبر AJAX"""
    try:
        employee = Employee.objects.get(emp_id=emp_id)

        evaluations = EmployeeEvaluation.objects.filter(
            emp=employee,
            score__isnull=False
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('eval_date')

        data = {
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'evaluations': [
                {
                    'period': eval.period.period_name,
                    'score': float(eval.score),
                    'date': eval.eval_date.strftime('%Y-%m-%d') if eval.eval_date else None
                }
                for eval in evaluations
            ]
        }

        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'الموظف غير موجود'}, status=404)


@login_required
def evaluation_stats_ajax(request):
    """إحصائيات التقييمات عبر AJAX"""
    stats = EmployeeEvaluation.objects.filter(
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.aggregate(
        total=Count('eval_id'),
        average=Avg('score'),
        highest=Max('score'),
        lowest=Min('score')
    )

    # توزيع الدرجات
    distribution = EmployeeEvaluation.objects.filter(
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.extra(
        select={
            'range': """
                CASE
                    WHEN score >= 90 THEN 'excellent'
                    WHEN score >= 80 THEN 'very_good'
                    WHEN score >= 70 THEN 'good'
                    WHEN score >= 60 THEN 'acceptable'
                    ELSE 'poor'
                END
            """
        }
    ).values('range').annotate(count=Count('eval_id'))

    stats['distribution'] = {item['range']: item['count'] for item in distribution}

    return JsonResponse(stats)


# Bulk Operations
@login_required
def bulk_create_evaluations(request):
    """إنشاء تقييمات بالجملة"""
    if request.method == 'POST':
        period_id = request.POST.get('period_id')
        employee_ids = request.POST.getlist('employee_ids')

        if period_id and employee_ids:
            period = get_object_or_404(EvaluationPeriod, period_id=period_id)
            created_count = 0

            for emp_id in employee_ids:
                employee = get_object_or_404(Employee, emp_id=emp_id)

                # التحقق من عدم وجود تقييم مسبق
                if not EmployeeEvaluation.objects.filter(emp=employee, period=period).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exists():
                    EmployeeEvaluation.objects.create(
                        emp=employee,
                        period=period
                    )
                    created_count += 1

            messages.success(request, f'تم إنشاء {created_count} تقييم جديد.')
        else:
            messages.error(request, 'يرجى تحديد الفترة والموظفين.')

    return redirect('evaluations:evaluation_list')


@login_required
def bulk_export_evaluations(request):
    """تصدير التقييمات بالجملة"""
    return export_evaluations(request)


# Performance Analytics
@login_required
def performance_analytics(request):
    """تحليلات الأداء"""
    # تحليلات متقدمة للأداء

    # اتجاهات الأداء الشهرية
    monthly_trends = EmployeeEvaluation.objects.filter(
        eval_date__isnull=False,
        score__isnull=False
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.extra(
        select={'month': "MONTH(eval_date)", 'year': "YEAR(eval_date)"}
    ).values('month', 'year').annotate(
        avg_score=Avg('score'),
        count=Count('eval_id')
    ).order_by('year', 'month')

    # توزيع الأداء حسب الأقسام
    department_distribution = Department.objects.annotate(
        excellent=Count('employee__evaluations',
                       filter=Q(employee__evaluations__score__gte=90)),
        very_good=Count('employee__evaluations',
                       filter=Q(employee__evaluations__score__gte=80,
                               employee__evaluations__score__lt=90)),
        good=Count('employee__evaluations',
                  filter=Q(employee__evaluations__score__gte=70,
                           employee__evaluations__score__lt=80)),
        acceptable=Count('employee__evaluations',
                        filter=Q(employee__evaluations__score__gte=60,
                                 employee__evaluations__score__lt=70)),
        poor=Count('employee__evaluations',
                  filter=Q(employee__evaluations__score__lt=60))
    ).filter(is_active=True)

    context = {
        'monthly_trends': monthly_trends,
        'department_distribution': department_distribution,
    }

    return render(request, 'evaluations/performance_analytics.html', context)
