"""
عروض نظام التقارير الشاملة
"""

import json
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model

from ..decorators import hr_permission_required
from ..models import Employee, Department, JobPosition
from ..models_reports import (
    ReportCategory, ReportTemplate, ReportInstance, 
    ScheduledReport, ReportFavorite, ReportShare
)
from ..models_enhanced import LeaveType
from ..services.report_service import report_service

User = get_user_model()


@login_required
@hr_permission_required('view_reports')
def reports_dashboard(request):
    """لوحة تحكم التقارير"""
    try:
        # الحصول على الفئات
        categories = ReportCategory.objects.filter(is_active=True).order_by('order')
        
        # الحصول على القوالب المتاحة
        templates = report_service.get_available_templates(request.user)
        
        # الحصول على التقارير الأخيرة للمستخدم
        recent_reports = report_service.get_user_reports(request.user, limit=5)
        
        # الحصول على المفضلة
        favorites = report_service.get_user_favorites(request.user)[:5]
        
        # إحصائيات سريعة
        stats = {
            'total_templates': len(templates),
            'recent_reports_count': len(recent_reports),
            'favorites_count': len(favorites),
            'categories_count': categories.count(),
        }
        
        context = {
            'categories': categories,
            'templates': templates,
            'recent_reports': recent_reports,
            'favorites': favorites,
            'stats': stats,
        }
        
        return render(request, 'Hr/reports/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل لوحة التحكم: {e}')
        return redirect('Hr:dashboard')


@login_required
@hr_permission_required('view_reports')
def report_templates(request):
    """قائمة قوالب التقارير"""
    try:
        # الحصول على المعاملات
        category_id = request.GET.get('category')
        search = request.GET.get('search')
        report_type = request.GET.get('type')
        
        # بناء الاستعلام
        templates = report_service.get_available_templates(request.user)
        
        # تطبيق الفلاتر
        if category_id:
            templates = [t for t in templates if str(t.category.id) == category_id]
        
        if search:
            templates = [t for t in templates if search.lower() in t.name.lower()]
        
        if report_type:
            templates = [t for t in templates if t.report_type == report_type]
        
        # ترقيم الصفحات
        paginator = Paginator(templates, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # البيانات للفلاتر
        categories = ReportCategory.objects.filter(is_active=True).order_by('order')
        report_types = ReportTemplate.REPORT_TYPES
        
        context = {
            'page_obj': page_obj,
            'categories': categories,
            'report_types': report_types,
            'current_category': category_id,
            'current_search': search,
            'current_type': report_type,
        }
        
        return render(request, 'Hr/reports/templates.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل القوالب: {e}')
        return redirect('Hr:reports_dashboard')


@login_required
@hr_permission_required('view_reports')
def report_template_detail(request, template_id):
    """تفاصيل قالب التقرير"""
    try:
        template = get_object_or_404(ReportTemplate, id=template_id, is_active=True)
        
        # فحص الصلاحيات
        if not report_service._check_template_permissions(template, request.user):
            messages.error(request, 'ليس لديك صلاحية لعرض هذا التقرير')
            return redirect('Hr:report_templates')
        
        # الحصول على البيانات للفلاتر
        filter_data = {}
        
        if template.report_type in ['employee', 'attendance', 'payroll', 'leave']:
            filter_data['departments'] = Department.objects.filter(is_active=True)
            filter_data['job_positions'] = JobPosition.objects.filter(is_active=True)
        
        if template.report_type == 'employee':
            filter_data['employees'] = Employee.objects.filter(is_active=True).select_related('department')
        
        if template.report_type == 'leave':
            filter_data['leave_types'] = LeaveType.objects.filter(is_active=True)
        
        # الحصول على التقارير الأخيرة لهذا القالب
        recent_instances = ReportInstance.objects.filter(
            template=template,
            created_by=request.user
        ).order_by('-created_at')[:5]
        
        context = {
            'template': template,
            'filter_data': filter_data,
            'recent_instances': recent_instances,
        }
        
        return render(request, 'Hr/reports/template_detail.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل تفاصيل القالب: {e}')
        return redirect('Hr:report_templates')


@login_required
@hr_permission_required('generate_reports')
@require_http_methods(["POST"])
def generate_report(request, template_id):
    """إنتاج تقرير جديد"""
    try:
        template = get_object_or_404(ReportTemplate, id=template_id, is_active=True)
        
        # الحصول على المعاملات
        parameters = {}
        output_format = request.POST.get('output_format', 'pdf')
        
        # معالجة معاملات التقرير حسب النوع
        if template.report_type in ['employee', 'attendance', 'payroll', 'leave']:
            if request.POST.get('department_id'):
                parameters['department_id'] = request.POST.get('department_id')
            
            if request.POST.get('employee_id'):
                parameters['employee_id'] = request.POST.get('employee_id')
            
            if request.POST.get('search'):
                parameters['search'] = request.POST.get('search')
        
        if template.report_type in ['attendance', 'leave']:
            if request.POST.get('date_from'):
                parameters['date_from'] = request.POST.get('date_from')
            
            if request.POST.get('date_to'):
                parameters['date_to'] = request.POST.get('date_to')
        
        if template.report_type == 'payroll':
            if request.POST.get('month'):
                parameters['month'] = int(request.POST.get('month'))
            
            if request.POST.get('year'):
                parameters['year'] = int(request.POST.get('year'))
        
        if template.report_type == 'leave':
            if request.POST.get('leave_type_id'):
                parameters['leave_type_id'] = request.POST.get('leave_type_id')
            
            if request.POST.get('status'):
                parameters['status'] = request.POST.get('status')
        
        # إنتاج التقرير
        instance = report_service.generate_report(
            template_id=template_id,
            user=request.user,
            parameters=parameters,
            output_format=output_format
        )
        
        messages.success(request, 'تم إنتاج التقرير بنجاح')
        return redirect('Hr:report_instance_detail', instance_id=instance.id)
        
    except Exception as e:
        messages.error(request, f'خطأ في إنتاج التقرير: {e}')
        return redirect('Hr:report_template_detail', template_id=template_id)


@login_required
@hr_permission_required('view_reports')
def report_instance_detail(request, instance_id):
    """تفاصيل مثيل التقرير"""
    try:
        instance = get_object_or_404(
            ReportInstance, 
            id=instance_id,
            created_by=request.user
        )
        
        context = {
            'instance': instance,
        }
        
        return render(request, 'Hr/reports/instance_detail.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل تفاصيل التقرير: {e}')
        return redirect('Hr:reports_dashboard')


@login_required
@hr_permission_required('view_reports')
def download_report(request, instance_id):
    """تحميل ملف التقرير"""
    try:
        instance = get_object_or_404(
            ReportInstance, 
            id=instance_id,
            created_by=request.user,
            status='completed'
        )
        
        if not instance.file_path:
            raise Http404("ملف التقرير غير موجود")
        
        # فتح الملف
        if default_storage.exists(instance.file_path):
            file_content = default_storage.open(instance.file_path).read()
            
            # تحديد نوع المحتوى
            content_types = {
                'pdf': 'application/pdf',
                'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'csv': 'text/csv',
                'html': 'text/html',
                'json': 'application/json',
            }
            
            content_type = content_types.get(instance.output_format, 'application/octet-stream')
            
            # إنشاء الاستجابة
            response = HttpResponse(file_content, content_type=content_type)
            
            # تحديد اسم الملف
            filename = f"{instance.template.name}_{instance.created_at.strftime('%Y%m%d_%H%M')}"
            extensions = {
                'pdf': '.pdf',
                'excel': '.xlsx',
                'csv': '.csv',
                'html': '.html',
                'json': '.json',
            }
            filename += extensions.get(instance.output_format, '.txt')
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            raise Http404("ملف التقرير غير موجود")
            
    except Exception as e:
        messages.error(request, f'خطأ في تحميل التقرير: {e}')
        return redirect('Hr:report_instance_detail', instance_id=instance_id)


@login_required
@hr_permission_required('view_reports')
def my_reports(request):
    """تقاريري"""
    try:
        # الحصول على المعاملات
        status = request.GET.get('status')
        template_id = request.GET.get('template')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # بناء الاستعلام
        instances = ReportInstance.objects.filter(
            created_by=request.user
        ).select_related('template').order_by('-created_at')
        
        # تطبيق الفلاتر
        if status:
            instances = instances.filter(status=status)
        
        if template_id:
            instances = instances.filter(template_id=template_id)
        
        if date_from:
            instances = instances.filter(created_at__date__gte=date_from)
        
        if date_to:
            instances = instances.filter(created_at__date__lte=date_to)
        
        # ترقيم الصفحات
        paginator = Paginator(instances, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # البيانات للفلاتر
        templates = report_service.get_available_templates(request.user)
        status_choices = ReportInstance.STATUS_CHOICES
        
        context = {
            'page_obj': page_obj,
            'templates': templates,
            'status_choices': status_choices,
            'current_status': status,
            'current_template': template_id,
            'current_date_from': date_from,
            'current_date_to': date_to,
        }
        
        return render(request, 'Hr/reports/my_reports.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل التقارير: {e}')
        return redirect('Hr:reports_dashboard')


@login_required
@hr_permission_required('view_reports')
def favorites(request):
    """التقارير المفضلة"""
    try:
        favorites = report_service.get_user_favorites(request.user)
        
        context = {
            'favorites': favorites,
        }
        
        return render(request, 'Hr/reports/favorites.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل المفضلة: {e}')
        return redirect('Hr:reports_dashboard')


@login_required
@hr_permission_required('view_reports')
@require_http_methods(["POST"])
def add_to_favorites(request, template_id):
    """إضافة تقرير للمفضلة"""
    try:
        parameters = json.loads(request.POST.get('parameters', '{}'))
        name = request.POST.get('name')
        
        favorite = report_service.add_to_favorites(
            user=request.user,
            template_id=template_id,
            parameters=parameters,
            name=name
        )
        
        return JsonResponse({
            'success': True,
            'message': 'تم إضافة التقرير للمفضلة'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في إضافة التقرير للمفضلة: {e}'
        })


@login_required
@hr_permission_required('view_reports')
@require_http_methods(["POST"])
def remove_from_favorites(request, favorite_id):
    """إزالة تقرير من المفضلة"""
    try:
        favorite = get_object_or_404(
            ReportFavorite,
            id=favorite_id,
            user=request.user
        )
        favorite.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'تم إزالة التقرير من المفضلة'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في إزالة التقرير من المفضلة: {e}'
        })


@login_required
@hr_permission_required('share_reports')
@require_http_methods(["POST"])
def share_report(request, instance_id):
    """مشاركة تقرير"""
    try:
        shared_with_ids = request.POST.getlist('shared_with')
        message = request.POST.get('message')
        expires_days = int(request.POST.get('expires_days', 30))
        
        shares = report_service.share_report(
            instance_id=instance_id,
            shared_by=request.user,
            shared_with_ids=shared_with_ids,
            message=message,
            expires_days=expires_days
        )
        
        messages.success(request, f'تم مشاركة التقرير مع {len(shares)} مستخدم')
        return redirect('Hr:report_instance_detail', instance_id=instance_id)
        
    except Exception as e:
        messages.error(request, f'خطأ في مشاركة التقرير: {e}')
        return redirect('Hr:report_instance_detail', instance_id=instance_id)


@login_required
@hr_permission_required('view_reports')
def shared_with_me(request):
    """التقارير المشاركة معي"""
    try:
        shares = ReportShare.objects.filter(
            shared_with=request.user
        ).select_related(
            'instance__template', 'shared_by'
        ).order_by('-created_at')
        
        # ترقيم الصفحات
        paginator = Paginator(shares, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        
        return render(request, 'Hr/reports/shared_with_me.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في تحميل التقارير المشاركة: {e}')
        return redirect('Hr:reports_dashboard')


@login_required
@hr_permission_required('view_reports')
def view_shared_report(request, share_id):
    """عرض تقرير مشارك"""
    try:
        share = get_object_or_404(
            ReportShare,
            id=share_id,
            shared_with=request.user
        )
        
        # فحص انتهاء الصلاحية
        if share.is_expired():
            messages.error(request, 'انتهت صلاحية هذا التقرير المشارك')
            return redirect('Hr:shared_with_me')
        
        # تحديد كمقروء
        if not share.is_read:
            share.is_read = True
            share.save(update_fields=['is_read'])
        
        context = {
            'share': share,
            'instance': share.instance,
        }
        
        return render(request, 'Hr/reports/shared_report_detail.html', context)
    except Exception as e:
        messages.error(request, f'خطأ في عرض التقرير المشارك: {e}')
        return redirect('Hr:shared_with_me')


@login_required
@hr_permission_required('view_reports')
def get_filter_data(request, template_id):
    """الحصول على بيانات الفلاتر للتقرير"""
    try:
        template = get_object_or_404(ReportTemplate, id=template_id)
        
        data = {}
        
        if template.report_type in ['employee', 'attendance', 'payroll', 'leave']:
            data['departments'] = [
                {'id': str(dept.id), 'name': dept.name}
                for dept in Department.objects.filter(is_active=True)
            ]
            
            data['job_positions'] = [
                {'id': str(pos.id), 'name': pos.name}
                for pos in JobPosition.objects.filter(is_active=True)
            ]
        
        if template.report_type == 'employee':
            data['employees'] = [
                {
                    'id': str(emp.id), 
                    'name': emp.get_full_name(),
                    'department': emp.department.name if emp.department else ''
                }
                for emp in Employee.objects.filter(is_active=True).select_related('department')
            ]
        
        if template.report_type == 'leave':
            data['leave_types'] = [
                {'id': str(lt.id), 'name': lt.name}
                for lt in LeaveType.objects.filter(is_active=True)
            ]
            
            data['status_choices'] = [
                {'value': choice[0], 'label': choice[1]}
                for choice in LeaveRequest.STATUS_CHOICES
            ]
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)