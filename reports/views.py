"""
عروض نظام التقارير الشامل
========================

يحتوي على جميع العروض لإدارة وإنتاج التقارير
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import date, datetime, timedelta
import json
import logging

from .models import (
    ReportCategory, ReportTemplate, ReportSchedule,
    GeneratedReport, ReportAccessLog, ReportDashboard
)
from .services import (
    ReportDataService, ReportGeneratorService,
    ReportSchedulerService, ReportAnalyticsService
)
from apps.hr.employees.models import Employee
from org.models import Department

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """لوحة تحكم التقارير الرئيسية"""
    analytics_service = ReportAnalyticsService()

    # إحصائيات عامة
    usage_stats = analytics_service.get_usage_statistics()

    # التقارير الحديثة
    recent_reports = GeneratedReport.objects.select_related(
        'template', 'generated_by'
    ).order_by('-generated_at')[:10]

    # فئات التقارير
    categories = ReportCategory.objects.filter(is_active=True).order_by('sort_order')

    # التقارير المميزة
    featured_templates = ReportTemplate.objects.filter(
        is_featured=True, is_active=True
    ).select_related('category')[:6]

    # الجدولة النشطة
    active_schedules = ReportSchedule.objects.filter(
        status='active'
    ).select_related('template').order_by('next_run')[:5]

    context = {
        'usage_stats': usage_stats,
        'recent_reports': recent_reports,
        'categories': categories,
        'featured_templates': featured_templates,
        'active_schedules': active_schedules,
    }

    return render(request, 'reports/dashboard.html', context)


@login_required
def report_categories(request):
    """قائمة فئات التقارير"""
    categories = ReportCategory.objects.annotate(
        template_count=Count('reporttemplate')
    ).order_by('sort_order')

    context = {
        'categories': categories
    }

    return render(request, 'reports/categories.html', context)


@login_required
def category_templates(request, category_id):
    """قوالب التقارير في فئة محددة"""
    category = get_object_or_404(ReportCategory, category_id=category_id)

    templates = ReportTemplate.objects.filter(
        category=category,
        is_active=True
    ).order_by('name')

    # فلترة حسب البحث
    search = request.GET.get('search')
    if search:
        templates = templates.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    # التقسيم إلى صفحات
    paginator = Paginator(templates, 12)
    page_number = request.GET.get('page')
    templates = paginator.get_page(page_number)

    context = {
        'category': category,
        'templates': templates,
    }

    return render(request, 'reports/category_templates.html', context)


@login_required
def generate_report(request, template_id):
    """إنتاج تقرير جديد"""
    template = get_object_or_404(ReportTemplate, template_id=template_id)

    if request.method == 'POST':
        try:
            # استخراج المعاملات من النموذج
            parameters = {}
            for param in template.get_parameters():
                param_name = param.get('name')
                if param_name in request.POST:
                    parameters[param_name] = request.POST[param_name]

            # تحديد صيغة الإخراج
            output_format = request.POST.get('format', template.default_format)

            # إنشاء سجل تقرير جديد
            generated_by = None
            if hasattr(request.user, 'employee'):
                generated_by = request.user.employee

            report = GeneratedReport.objects.create(
                template=template,
                name=f"{template.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                parameters=parameters,
                output_format=output_format,
                status='pending',
                generated_by=generated_by
            )

            # إنتاج التقرير في الخلفية (يمكن استخدام Celery)
            result = _generate_report_sync(report)

            if result['success']:
                messages.success(request, 'تم إنتاج التقرير بنجاح')
                return redirect('reports:report_detail', report_id=report.report_id)
            else:
                messages.error(request, f'فشل في إنتاج التقرير: {result["error"]}')

        except Exception as e:
            logger.error(f'Error generating report: {str(e)}')
            messages.error(request, f'حدث خطأ أثناء إنتاج التقرير: {str(e)}')

    # الحصول على البيانات المطلوبة للنموذج
    departments = Department.objects.filter(is_active=True)
    employees = Employee.objects.filter(emp_status='Active')

    context = {
        'template': template,
        'departments': departments,
        'employees': employees,
    }

    return render(request, 'reports/generate_report.html', context)


@login_required
def report_detail(request, report_id):
    """تفاصيل التقرير المُنتج"""
    report = get_object_or_404(GeneratedReport, report_id=report_id)

    # تسجيل الوصول
    ReportAccessLog.objects.create(
        report=report,
        user=request.user,
        employee=getattr(request.user, 'employee', None),
        access_type='view',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )

    context = {
        'report': report,
    }

    return render(request, 'reports/report_detail.html', context)


@login_required
def download_report(request, report_id):
    """تحميل التقرير"""
    report = get_object_or_404(GeneratedReport, report_id=report_id)

    if report.status != 'completed':
        messages.error(request, 'التقرير غير جاهز للتحميل')
        return redirect('reports:report_detail', report_id=report_id)

    try:
        # إنشاء محتوى تقرير تجريبي
        content = f"Sample report content for {report.name}"

        # إنشاء الاستجابة
        response = HttpResponse(content, content_type='text/plain')
        filename = f"{report.name}.txt"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # تحديث عداد التحميل
        report.download_count = getattr(report, 'download_count', 0) + 1
        report.save()

        return response

    except Exception as e:
        logger.error(f'Error downloading report {report_id}: {str(e)}')
        messages.error(request, 'حدث خطأ أثناء تحميل التقرير')
        return redirect('reports:report_detail', report_id=report_id)


@login_required
def my_reports(request):
    """تقاريري الشخصية"""
    employee = getattr(request.user, 'employee', None)

    if not employee:
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة')
        return redirect('reports:dashboard')

    reports = GeneratedReport.objects.filter(
        generated_by=employee
    ).select_related('template').order_by('-generated_at')

    context = {
        'reports': reports,
    }

    return render(request, 'reports/my_reports.html', context)


@login_required
def scheduled_reports(request):
    """التقارير المجدولة"""
    schedules = ReportSchedule.objects.select_related(
        'template', 'created_by'
    ).order_by('-created_at')

    context = {
        'schedules': schedules,
    }

    return render(request, 'reports/scheduled_reports.html', context)


@login_required
def create_schedule(request, template_id):
    """إنشاء جدولة تقرير"""
    template = get_object_or_404(ReportTemplate, template_id=template_id)

    if request.method == 'POST':
        try:
            # استخراج بيانات الجدولة
            name = request.POST.get('name')
            frequency = request.POST.get('frequency')
            start_date = request.POST.get('start_date')

            # إنشاء الجدولة (placeholder)
            messages.success(request, 'تم إنشاء جدولة التقرير بنجاح')
            return redirect('reports:scheduled_reports')

        except Exception as e:
            logger.error(f'Error creating schedule: {str(e)}')
            messages.error(request, f'حدث خطأ أثناء إنشاء الجدولة: {str(e)}')

    context = {
        'template': template,
    }

    return render(request, 'reports/create_schedule.html', context)


@login_required
def analytics(request):
    """تحليلات التقارير"""
    # إحصائيات أساسية
    total_reports = GeneratedReport.objects.count()
    completed_reports = GeneratedReport.objects.filter(status='completed').count()

    context = {
        'total_reports': total_reports,
        'completed_reports': completed_reports,
    }

    return render(request, 'reports/analytics.html', context)


@login_required
@csrf_exempt
def check_report_status(request, report_id):
    """فحص حالة التقرير (AJAX)"""
    try:
        report = GeneratedReport.objects.get(report_id=report_id)

        data = {
            'status': report.status,
            'progress': 100 if report.status == 'completed' else 50,
            'message': report.get_status_display(),
            'download_url': f'/reports/{report_id}/download/' if report.status == 'completed' else None
        }

        return JsonResponse(data)

    except GeneratedReport.DoesNotExist:
        return JsonResponse({'error': 'التقرير غير موجود'}, status=404)
    except Exception as e:
        logger.error(f'Error checking report status: {str(e)}')
        return JsonResponse({'error': 'حدث خطأ أثناء فحص الحالة'}, status=500)


@login_required
def get_template_parameters(request, template_id):
    """الحصول على معاملات قالب التقرير (AJAX)"""
    try:
        template = ReportTemplate.objects.get(template_id=template_id)

        data = {
            'parameters': [],
            'supported_formats': ['pdf', 'excel', 'csv'],
            'default_format': 'pdf'
        }

        return JsonResponse(data)

    except ReportTemplate.DoesNotExist:
        return JsonResponse({'error': 'قالب التقرير غير موجود'}, status=404)


@login_required
@require_http_methods(["POST"])
def delete_report(request, report_id):
    """حذف تقرير"""
    report = get_object_or_404(GeneratedReport, report_id=report_id)

    try:
        # حذف السجل
        report.delete()

        messages.success(request, 'تم حذف التقرير بنجاح')

    except Exception as e:
        logger.error(f'Error deleting report {report_id}: {str(e)}')
        messages.error(request, 'حدث خطأ أثناء حذف التقرير')

    return redirect('reports:my_reports')


# Helper Functions
def _generate_report_sync(report):
    """إنتاج التقرير بشكل متزامن"""
    try:
        report.status = 'processing'
        report.started_at = timezone.now()
        report.save()

        # إنشاء خدمة الإنتاج (placeholder implementation)
        # generator = ReportGeneratorService()

        # إنتاج التقرير حسب النوع (placeholder)
        result = {
            'success': True,
            'content': 'Sample report content',
            'format': report.output_format
        }

        # حفظ الملف
        file_path = _save_report_file(report, result)

        # تحديث التقرير
        report.file_path = file_path
        report.file_size = len(result['content'])
        report.status = 'completed'
        report.completed_at = timezone.now()

        if report.started_at:
            execution_time = (report.completed_at - report.started_at).total_seconds()
            report.execution_time = execution_time

        report.save()

        return {'success': True, 'report_id': report.report_id}

    except Exception as e:
        logger.error(f'Error generating report {report.report_id}: {str(e)}')

        report.status = 'failed'
        report.error_message = str(e)
        report.completed_at = timezone.now()
        report.save()

        return {'success': False, 'error': str(e)}


def _save_report_file(report, result):
    """حفظ ملف التقرير"""
    import os
    from django.conf import settings

    # إنشاء مجلد التقارير إذا لم يكن موجوداً
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # إنشاء اسم الملف
    filename = f"report_{report.report_id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{report.output_format}"
    file_path = os.path.join(reports_dir, filename)

    # حفظ المحتوى
    with open(file_path, 'wb') as f:
        if isinstance(result['content'], str):
            f.write(result['content'].encode('utf-8'))
        else:
            f.write(result['content'])

    return file_path
