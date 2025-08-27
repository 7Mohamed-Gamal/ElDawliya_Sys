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
from employees.models import Employee
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
            generated_by = None\n            if hasattr(request.user, 'employee'):\n                generated_by = request.user.employee\n            \n            report = GeneratedReport.objects.create(\n                template=template,\n                name=f\"{template.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}\",\n                parameters=parameters,\n                output_format=output_format,\n                status='pending',\n                generated_by=generated_by\n            )\n            \n            # إنتاج التقرير في الخلفية (يمكن استخدام Celery)\n            result = _generate_report_sync(report)\n            \n            if result['success']:\n                messages.success(request, 'تم إنتاج التقرير بنجاح')\n                return redirect('reports:report_detail', report_id=report.report_id)\n            else:\n                messages.error(request, f'فشل في إنتاج التقرير: {result[\"error\"]}')\n                \n        except Exception as e:\n            logger.error(f'Error generating report: {str(e)}')\n            messages.error(request, f'حدث خطأ أثناء إنتاج التقرير: {str(e)}')\n    \n    # الحصول على البيانات المطلوبة للنموذج\n    departments = Department.objects.filter(is_active=True)\n    employees = Employee.objects.filter(emp_status='Active')\n    \n    context = {\n        'template': template,\n        'departments': departments,\n        'employees': employees,\n    }\n    \n    return render(request, 'reports/generate_report.html', context)\n\n\n@login_required\ndef report_detail(request, report_id):\n    \"\"\"تفاصيل التقرير المُنتج\"\"\"\n    report = get_object_or_404(GeneratedReport, report_id=report_id)\n    \n    # تسجيل الوصول\n    ReportAccessLog.objects.create(\n        report=report,\n        user=request.user,\n        employee=getattr(request.user, 'employee', None),\n        access_type='view',\n        ip_address=request.META.get('REMOTE_ADDR'),\n        user_agent=request.META.get('HTTP_USER_AGENT')\n    )\n    \n    context = {\n        'report': report,\n    }\n    \n    return render(request, 'reports/report_detail.html', context)\n\n\n@login_required\ndef download_report(request, report_id):\n    \"\"\"تحميل التقرير\"\"\"\n    report = get_object_or_404(GeneratedReport, report_id=report_id)\n    \n    if report.status != 'completed':\n        messages.error(request, 'التقرير غير جاهز للتحميل')\n        return redirect('reports:report_detail', report_id=report_id)\n    \n    if report.is_expired:\n        messages.error(request, 'انتهت صلاحية التقرير')\n        return redirect('reports:report_detail', report_id=report_id)\n    \n    try:\n        # قراءة ملف التقرير\n        with open(report.file_path, 'rb') as f:\n            content = f.read()\n        \n        # تحديد نوع المحتوى\n        content_type = {\n            'pdf': 'application/pdf',\n            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',\n            'csv': 'text/csv',\n            'html': 'text/html'\n        }.get(report.output_format, 'application/octet-stream')\n        \n        # إنشاء الاستجابة\n        response = HttpResponse(content, content_type=content_type)\n        filename = f\"{report.name}.{report.output_format}\"\n        response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'\n        \n        # تحديث عداد التحميل\n        report.download_count += 1\n        report.save()\n        \n        # تسجيل الوصول\n        ReportAccessLog.objects.create(\n            report=report,\n            user=request.user,\n            employee=getattr(request.user, 'employee', None),\n            access_type='download',\n            ip_address=request.META.get('REMOTE_ADDR')\n        )\n        \n        return response\n        \n    except FileNotFoundError:\n        messages.error(request, 'ملف التقرير غير موجود')\n        return redirect('reports:report_detail', report_id=report_id)\n    except Exception as e:\n        logger.error(f'Error downloading report {report_id}: {str(e)}')\n        messages.error(request, 'حدث خطأ أثناء تحميل التقرير')\n        return redirect('reports:report_detail', report_id=report_id)\n\n\n@login_required\ndef my_reports(request):\n    \"\"\"تقاريري الشخصية\"\"\"\n    employee = getattr(request.user, 'employee', None)\n    \n    if not employee:\n        messages.error(request, 'لا يمكن الوصول لهذه الصفحة')\n        return redirect('reports:dashboard')\n    \n    reports = GeneratedReport.objects.filter(\n        generated_by=employee\n    ).select_related('template').order_by('-generated_at')\n    \n    # فلترة حسب الحالة\n    status = request.GET.get('status')\n    if status:\n        reports = reports.filter(status=status)\n    \n    # فلترة حسب الفترة\n    period = request.GET.get('period')\n    if period:\n        today = date.today()\n        if period == 'today':\n            reports = reports.filter(generated_at__date=today)\n        elif period == 'week':\n            week_ago = today - timedelta(days=7)\n            reports = reports.filter(generated_at__date__gte=week_ago)\n        elif period == 'month':\n            month_ago = today - timedelta(days=30)\n            reports = reports.filter(generated_at__date__gte=month_ago)\n    \n    # التقسيم إلى صفحات\n    paginator = Paginator(reports, 20)\n    page_number = request.GET.get('page')\n    reports = paginator.get_page(page_number)\n    \n    context = {\n        'reports': reports,\n    }\n    \n    return render(request, 'reports/my_reports.html', context)\n\n\n@login_required\ndef scheduled_reports(request):\n    \"\"\"التقارير المجدولة\"\"\"\n    schedules = ReportSchedule.objects.select_related(\n        'template', 'created_by'\n    ).order_by('-created_at')\n    \n    # فلترة حسب الحالة\n    status = request.GET.get('status')\n    if status:\n        schedules = schedules.filter(status=status)\n    \n    # التقسيم إلى صفحات\n    paginator = Paginator(schedules, 20)\n    page_number = request.GET.get('page')\n    schedules = paginator.get_page(page_number)\n    \n    context = {\n        'schedules': schedules,\n    }\n    \n    return render(request, 'reports/scheduled_reports.html', context)\n\n\n@login_required\ndef create_schedule(request, template_id):\n    \"\"\"إنشاء جدولة تقرير\"\"\"\n    template = get_object_or_404(ReportTemplate, template_id=template_id)\n    \n    if request.method == 'POST':\n        try:\n            # استخراج بيانات الجدولة\n            name = request.POST.get('name')\n            frequency = request.POST.get('frequency')\n            start_date = request.POST.get('start_date')\n            email_recipients = request.POST.getlist('email_recipients')\n            \n            # استخراج معاملات التقرير\n            parameters = {}\n            for param in template.get_parameters():\n                param_name = param.get('name')\n                if param_name in request.POST:\n                    parameters[param_name] = request.POST[param_name]\n            \n            # إنشاء الجدولة\n            employee = getattr(request.user, 'employee', None)\n            \n            schedule = ReportSchedule.objects.create(\n                template=template,\n                name=name,\n                frequency=frequency,\n                start_date=start_date,\n                next_run=start_date,\n                parameters=parameters,\n                email_recipients=email_recipients,\n                created_by=employee\n            )\n            \n            messages.success(request, 'تم إنشاء جدولة التقرير بنجاح')\n            return redirect('reports:scheduled_reports')\n            \n        except Exception as e:\n            logger.error(f'Error creating schedule: {str(e)}')\n            messages.error(request, f'حدث خطأ أثناء إنشاء الجدولة: {str(e)}')\n    \n    context = {\n        'template': template,\n    }\n    \n    return render(request, 'reports/create_schedule.html', context)\n\n\n@login_required\ndef analytics(request):\n    \"\"\"تحليلات التقارير\"\"\"\n    analytics_service = ReportAnalyticsService()\n    \n    # إحصائيات الاستخدام\n    usage_stats = analytics_service.get_usage_statistics()\n    \n    # إحصائيات شهرية\n    monthly_stats = GeneratedReport.objects.extra(\n        select={\n            'month': \"DATE_FORMAT(generated_at, '%%Y-%%m')\"\n        }\n    ).values('month').annotate(\n        count=Count('report_id'),\n        completed=Count('report_id', filter=Q(status='completed')),\n        failed=Count('report_id', filter=Q(status='failed'))\n    ).order_by('-month')[:12]\n    \n    # أكثر الفئات استخداماً\n    category_stats = ReportCategory.objects.annotate(\n        report_count=Count('reporttemplate__generatedreport')\n    ).order_by('-report_count')[:10]\n    \n    context = {\n        'usage_stats': usage_stats,\n        'monthly_stats': list(monthly_stats),\n        'category_stats': category_stats,\n    }\n    \n    return render(request, 'reports/analytics.html', context)\n\n\n# AJAX Views\n@login_required\n@csrf_exempt\ndef check_report_status(request, report_id):\n    \"\"\"فحص حالة التقرير (AJAX)\"\"\"\n    try:\n        report = GeneratedReport.objects.get(report_id=report_id)\n        \n        data = {\n            'status': report.status,\n            'progress': 100 if report.status == 'completed' else 50,\n            'message': report.get_status_display(),\n            'download_url': f'/reports/{report_id}/download/' if report.status == 'completed' else None\n        }\n        \n        return JsonResponse(data)\n        \n    except GeneratedReport.DoesNotExist:\n        return JsonResponse({'error': 'التقرير غير موجود'}, status=404)\n    except Exception as e:\n        logger.error(f'Error checking report status: {str(e)}')\n        return JsonResponse({'error': 'حدث خطأ أثناء فحص الحالة'}, status=500)\n\n\n@login_required\ndef get_template_parameters(request, template_id):\n    \"\"\"الحصول على معاملات قالب التقرير (AJAX)\"\"\"\n    try:\n        template = ReportTemplate.objects.get(template_id=template_id)\n        \n        data = {\n            'parameters': template.get_parameters(),\n            'supported_formats': template.get_supported_formats(),\n            'default_format': template.default_format\n        }\n        \n        return JsonResponse(data)\n        \n    except ReportTemplate.DoesNotExist:\n        return JsonResponse({'error': 'قالب التقرير غير موجود'}, status=404)\n\n\n@login_required\n@require_http_methods([\"POST\"])\ndef delete_report(request, report_id):\n    \"\"\"حذف تقرير\"\"\"\n    report = get_object_or_404(GeneratedReport, report_id=report_id)\n    \n    # التحقق من الصلاحيات\n    if report.generated_by != getattr(request.user, 'employee', None):\n        messages.error(request, 'ليس لديك صلاحية لحذف هذا التقرير')\n        return redirect('reports:my_reports')\n    \n    try:\n        # حذف الملف إذا كان موجوداً\n        if report.file_path:\n            import os\n            if os.path.exists(report.file_path):\n                os.remove(report.file_path)\n        \n        # حذف السجل\n        report.delete()\n        \n        messages.success(request, 'تم حذف التقرير بنجاح')\n        \n    except Exception as e:\n        logger.error(f'Error deleting report {report_id}: {str(e)}')\n        messages.error(request, 'حدث خطأ أثناء حذف التقرير')\n    \n    return redirect('reports:my_reports')\n\n\n# Helper Functions\ndef _generate_report_sync(report):\n    \"\"\"إنتاج التقرير بشكل متزامن\"\"\"\n    try:\n        report.status = 'processing'\n        report.started_at = timezone.now()\n        report.save()\n        \n        # إنشاء خدمة الإنتاج\n        generator = ReportGeneratorService()\n        \n        # إنتاج التقرير حسب النوع\n        if 'attendance' in report.template.code:\n            result = generator.generate_attendance_report(report.parameters)\n        elif 'payroll' in report.template.code:\n            result = generator.generate_payroll_report(report.parameters)\n        elif 'leave' in report.template.code:\n            result = generator.generate_leave_report(report.parameters)\n        elif 'comprehensive' in report.template.code:\n            result = generator.generate_comprehensive_hr_report(report.parameters)\n        else:\n            raise ValueError(f'Unknown report type: {report.template.code}')\n        \n        # حفظ الملف\n        file_path = _save_report_file(report, result)\n        \n        # تحديث التقرير\n        report.file_path = file_path\n        report.file_size = len(result['content'])\n        report.status = 'completed'\n        report.completed_at = timezone.now()\n        \n        if report.started_at:\n            execution_time = (report.completed_at - report.started_at).total_seconds()\n            report.execution_time = execution_time\n        \n        report.save()\n        \n        return {'success': True, 'report_id': report.report_id}\n        \n    except Exception as e:\n        logger.error(f'Error generating report {report.report_id}: {str(e)}')\n        \n        report.status = 'failed'\n        report.error_message = str(e)\n        report.completed_at = timezone.now()\n        report.save()\n        \n        return {'success': False, 'error': str(e)}\n\n\ndef _save_report_file(report, result):\n    \"\"\"حفظ ملف التقرير\"\"\"\n    import os\n    from django.conf import settings\n    \n    # إنشاء مجلد التقارير إذا لم يكن موجوداً\n    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')\n    os.makedirs(reports_dir, exist_ok=True)\n    \n    # إنشاء اسم الملف\n    filename = f\"report_{report.report_id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{report.output_format}\"\n    file_path = os.path.join(reports_dir, filename)\n    \n    # حفظ المحتوى\n    with open(file_path, 'wb') as f:\n        if isinstance(result['content'], str):\n            f.write(result['content'].encode('utf-8'))\n        else:\n            f.write(result['content'])\n    \n    return file_path