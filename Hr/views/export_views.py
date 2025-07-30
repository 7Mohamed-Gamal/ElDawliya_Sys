"""
عروض التصدير المتقدم
"""

import json
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..decorators import hr_permission_required
from ..models_reports import ReportTemplate, ReportInstance, ScheduledReport
from ..services.export_service import export_service
from ..tasks.export_tasks import generate_bulk_reports, export_report_to_multiple_formats

User = get_user_model()


@login_required
@hr_permission_required('export_reports')
def export_options(request, instance_id):
    """خيارات التصدير المتقدمة"""
    try:
        instance = get_object_or_404(
            ReportInstance,
            id=instance_id,
            created_by=request.user,
            status='completed'
        )
        
        # الصيغ المدعومة
        supported_formats = export_service.supported_formats
        
        context = {
            'instance': instance,
            'supported_formats': supported_formats,
        }
        
        return render(request, 'Hr/reports/export_options.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل خيارات التصدير: {e}')
        return redirect('Hr:my_reports')


@login_required
@hr_permission_required('export_reports')
@require_http_methods(["POST"])
def export_multiple_formats(request, instance_id):
    """تصدير التقرير بصيغ متعددة"""
    try:
        instance = get_object_or_404(
            ReportInstance,
            id=instance_id,
            created_by=request.user,
            status='completed'
        )
        
        # الحصول على الصيغ المطلوبة
        formats = request.POST.getlist('formats')
        if not formats:
            messages.error(request, 'يجب اختيار صيغة واحدة على الأقل')
            return redirect('Hr:export_options', instance_id=instance_id)
        
        # تشغيل مهمة التصدير
        task = export_report_to_multiple_formats.delay(str(instance_id), formats)
        
        messages.success(request, 'تم بدء عملية التصدير. ستتلقى إشعاراً عند الانتهاء.')
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'message': 'تم بدء عملية التصدير'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في التصدير: {e}'
        })


@login_required
@hr_permission_required('schedule_reports')
def schedule_report(request, template_id):
    """جدولة تقرير"""
    try:
        template = get_object_or_404(ReportTemplate, id=template_id, is_active=True)
        
        if request.method == 'POST':
            # الحصول على بيانات الجدولة
            frequency = request.POST.get('frequency')
            parameters = json.loads(request.POST.get('parameters', '{}'))
            output_format = request.POST.get('output_format', 'pdf')
            
            # إعدادات البريد الإلكتروني
            email_recipients = request.POST.getlist('email_recipients')
            email_subject = request.POST.get('email_subject', f'تقرير {template.name}')
            email_body = request.POST.get('email_body', '')
            
            # إنشاء الجدولة
            schedule_config = {
                'frequency': frequency,
                'email_recipients': email_recipients,
                'email_subject': email_subject,
                'email_body': email_body
            }
            
            scheduled_report = export_service.schedule_export(
                template_id=template_id,
                parameters=parameters,
                format_type=output_format,
                schedule_config=schedule_config,
                user=request.user
            )
            
            messages.success(request, 'تم جدولة التقرير بنجاح')
            return redirect('Hr:scheduled_reports')
        
        # الحصول على المستخدمين للبريد الإلكتروني
        users = User.objects.filter(is_active=True).values('id', 'email', 'first_name', 'last_name')
        
        context = {
            'template': template,
            'users': users,
        }
        
        return render(request, 'Hr/reports/schedule_report.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في جدولة التقرير: {e}')
        return redirect('Hr:report_template_detail', template_id=template_id)


@login_required
@hr_permission_required('view_scheduled_reports')
def scheduled_reports(request):
    """التقارير المجدولة"""
    try:
        # الحصول على التقارير المجدولة للمستخدم
        scheduled_reports = ScheduledReport.objects.filter(
            created_by=request.user
        ).select_related('template').order_by('-created_at')
        
        context = {
            'scheduled_reports': scheduled_reports,
        }
        
        return render(request, 'Hr/reports/scheduled_reports.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل التقارير المجدولة: {e}')
        return redirect('Hr:reports_dashboard')


@login_required
@hr_permission_required('manage_scheduled_reports')
@require_http_methods(["POST"])
def toggle_scheduled_report(request, scheduled_id):
    """تفعيل/إلغاء تفعيل تقرير مجدول"""
    try:
        scheduled_report = get_object_or_404(
            ScheduledReport,
            id=scheduled_id,
            created_by=request.user
        )
        
        scheduled_report.is_active = not scheduled_report.is_active
        scheduled_report.save()
        
        status = 'تم تفعيل' if scheduled_report.is_active else 'تم إلغاء تفعيل'
        
        return JsonResponse({
            'success': True,
            'is_active': scheduled_report.is_active,
            'message': f'{status} التقرير المجدول'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في تحديث التقرير المجدول: {e}'
        })


@login_required
@hr_permission_required('delete_scheduled_reports')
@require_http_methods(["DELETE"])
def delete_scheduled_report(request, scheduled_id):
    """حذف تقرير مجدول"""
    try:
        scheduled_report = get_object_or_404(
            ScheduledReport,
            id=scheduled_id,
            created_by=request.user
        )
        
        scheduled_report.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'تم حذف التقرير المجدول'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في حذف التقرير المجدول: {e}'
        })


@login_required
@hr_permission_required('bulk_export')
def bulk_export(request):
    """التصدير المجمع"""
    try:
        if request.method == 'POST':
            # الحصول على القوالب المحددة
            template_ids = request.POST.getlist('template_ids')
            output_format = request.POST.get('output_format', 'excel')
            
            if not template_ids:
                messages.error(request, 'يجب اختيار قالب واحد على الأقل')
                return redirect('Hr:bulk_export')
            
            # إعداد المعاملات لكل قالب
            parameters_list = []
            for template_id in template_ids:
                # يمكن تخصيص المعاملات لكل قالب
                parameters_list.append({})
            
            # تشغيل مهمة التصدير المجمع
            task = generate_bulk_reports.delay(
                template_ids=template_ids,
                parameters_list=parameters_list,
                user_id=request.user.id,
                output_format=output_format
            )
            
            messages.success(request, 'تم بدء عملية التصدير المجمع. ستتلقى إشعاراً عند الانتهاء.')
            
            return JsonResponse({
                'success': True,
                'task_id': task.id,
                'message': 'تم بدء عملية التصدير المجمع'
            })
        
        # الحصول على القوالب المتاحة
        from ..services.report_service import report_service
        templates = report_service.get_available_templates(request.user)
        
        context = {
            'templates': templates,
        }
        
        return render(request, 'Hr/reports/bulk_export.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في التصدير المجمع: {e}')
        return redirect('Hr:reports_dashboard')


@login_required
@hr_permission_required('send_reports')
@require_http_methods(["POST"])
def send_report_email(request, instance_id):
    """إرسال التقرير عبر البريد الإلكتروني"""
    try:
        instance = get_object_or_404(
            ReportInstance,
            id=instance_id,
            created_by=request.user,
            status='completed'
        )
        
        # الحصول على بيانات البريد الإلكتروني
        recipients = request.POST.getlist('recipients')
        subject = request.POST.get('subject', f'تقرير {instance.template.name}')
        body = request.POST.get('body', '')
        
        if not recipients:
            return JsonResponse({
                'success': False,
                'message': 'يجب تحديد مستقبل واحد على الأقل'
            })
        
        # إرسال البريد الإلكتروني
        export_service.send_report_email(
            report_instance=instance,
            recipients=recipients,
            subject=subject,
            body=body
        )
        
        return JsonResponse({
            'success': True,
            'message': 'تم إرسال التقرير بنجاح'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في إرسال التقرير: {e}'
        })


@login_required
@hr_permission_required('view_export_history')
def export_history(request):
    """تاريخ التصدير"""
    try:
        # الحصول على تاريخ التصدير للمستخدم
        instances = ReportInstance.objects.filter(
            created_by=request.user
        ).select_related('template').order_by('-created_at')[:50]
        
        # إحصائيات التصدير
        stats = {
            'total_exports': instances.count(),
            'successful_exports': instances.filter(status='completed').count(),
            'failed_exports': instances.filter(status='failed').count(),
            'formats_used': {}
        }
        
        # إحصائيات الصيغ
        for instance in instances:
            format_name = instance.output_format
            stats['formats_used'][format_name] = stats['formats_used'].get(format_name, 0) + 1
        
        context = {
            'instances': instances,
            'stats': stats,
        }
        
        return render(request, 'Hr/reports/export_history.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل تاريخ التصدير: {e}')
        return redirect('Hr:reports_dashboard')


@login_required
@hr_permission_required('view_export_stats')
def export_statistics(request):
    """إحصائيات التصدير"""
    try:
        # إحصائيات شاملة للتصدير
        from django.db.models import Count, Q
        from django.utils import timezone
        
        # الفترة الزمنية (آخر 30 يوم)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # إحصائيات عامة
        stats = {
            'total_reports': ReportInstance.objects.count(),
            'recent_reports': ReportInstance.objects.filter(created_at__gte=thirty_days_ago).count(),
            'successful_reports': ReportInstance.objects.filter(status='completed').count(),
            'failed_reports': ReportInstance.objects.filter(status='failed').count(),
        }
        
        # إحصائيات الصيغ
        format_stats = ReportInstance.objects.values('output_format').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # إحصائيات القوالب الأكثر استخداماً
        template_stats = ReportInstance.objects.values(
            'template__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # إحصائيات المستخدمين
        user_stats = ReportInstance.objects.values(
            'created_by__first_name', 'created_by__last_name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        context = {
            'stats': stats,
            'format_stats': format_stats,
            'template_stats': template_stats,
            'user_stats': user_stats,
        }
        
        return render(request, 'Hr/reports/export_statistics.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل إحصائيات التصدير: {e}')
        return redirect('Hr:reports_dashboard')


@login_required
@hr_permission_required('view_reports')
def get_export_progress(request, task_id):
    """الحصول على تقدم عملية التصدير"""
    try:
        from celery.result import AsyncResult
        
        result = AsyncResult(task_id)
        
        response_data = {
            'state': result.state,
            'ready': result.ready(),
        }
        
        if result.ready():
            if result.successful():
                response_data['result'] = result.result
            else:
                response_data['error'] = str(result.info)
        else:
            # معلومات التقدم إذا كانت متاحة
            if hasattr(result, 'info') and isinstance(result.info, dict):
                response_data.update(result.info)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'state': 'FAILURE',
            'error': str(e)
        })