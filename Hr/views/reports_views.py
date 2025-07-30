"""
Views للتقارير والتحليلات
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
import json

from Hr.models import Employee, Department, JobPosition, Branch
from Hr.services.report_service import ReportService
from Hr.decorators import hr_required


@login_required
@hr_required
def analytics_dashboard(request):
    """
    عرض لوحة التحليلات الرئيسية
    """
    context = {
        'employee_count': Employee.objects.filter(is_active=True).count(),
        'departments': Department.objects.filter(is_active=True),
        'branches': Branch.objects.filter(is_active=True),
        'positions': JobPosition.objects.filter(is_active=True),
    }
    
    return render(request, 'Hr/analytics/analytics_dashboard.html', context)


@login_required
@hr_required
def employee_reports(request):
    """
    عرض صفحة تقارير الموظفين
    """
    context = {
        'departments': Department.objects.filter(is_active=True),
        'branches': Branch.objects.filter(is_active=True),
        'positions': JobPosition.objects.filter(is_active=True),
    }
    
    return render(request, 'Hr/reports/employee_reports.html', context)


@login_required
@hr_required
def attendance_reports(request):
    """
    عرض صفحة تقارير الحضور
    """
    context = {
        'departments': Department.objects.filter(is_active=True),
        'branches': Branch.objects.filter(is_active=True),
    }
    
    return render(request, 'Hr/reports/attendance_reports.html', context)


@login_required
@hr_required
def payroll_reports(request):
    """
    عرض صفحة تقارير الرواتب
    """
    context = {
        'departments': Department.objects.filter(is_active=True),
        'branches': Branch.objects.filter(is_active=True),
    }
    
    return render(request, 'Hr/reports/payroll_reports.html', context)


@login_required
@hr_required
def report_list(request):
    """
    عرض قائمة التقارير المتاحة
    """
    reports = [
        {
            'id': 'employee_summary',
            'name': 'تقرير ملخص الموظفين',
            'description': 'نظرة عامة على جميع الموظفين مع الإحصائيات الأساسية',
            'icon': 'fas fa-users',
            'url': 'Hr:reports:employee_reports'
        },
        {
            'id': 'employee_details',
            'name': 'تقرير تفاصيل الموظفين',
            'description': 'تقرير مفصل بجميع معلومات الموظفين',
            'icon': 'fas fa-address-card',
            'url': 'Hr:reports:employee_reports'
        },
        {
            'id': 'org_structure',
            'name': 'تقرير الهيكل التنظيمي',
            'description': 'عرض الهيكل التنظيمي وتوزيع الموظفين',
            'icon': 'fas fa-sitemap',
            'url': 'Hr:reports:employee_reports'
        },
        {
            'id': 'attendance_summary',
            'name': 'تقرير ملخص الحضور',
            'description': 'إحصائيات الحضور والغياب للموظفين',
            'icon': 'fas fa-clock',
            'url': 'Hr:reports:attendance_reports'
        },
        {
            'id': 'payroll_summary',
            'name': 'تقرير ملخص الرواتب',
            'description': 'تحليل الرواتب والمكافآت',
            'icon': 'fas fa-money-bill-wave',
            'url': 'Hr:reports:payroll_reports'
        },
        {
            'id': 'demographics',
            'name': 'تقرير التركيبة السكانية',
            'description': 'تحليل التركيبة السكانية للموظفين',
            'icon': 'fas fa-chart-pie',
            'url': 'Hr:reports:employee_reports'
        }
    ]
    
    context = {
        'reports': reports
    }
    
    return render(request, 'Hr/reports/report_list.html', context)


# API Views for AJAX requests

@login_required
@hr_required
@require_http_methods(["POST"])
def generate_employee_summary_report(request):
    """
    API لإنشاء تقرير ملخص الموظفين
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', {})
        
        # تحويل التواريخ من string إلى date objects
        if filters.get('start_date'):
            filters['start_date'] = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
        
        if filters.get('end_date'):
            filters['end_date'] = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
        
        report = ReportService.get_employee_summary_report(filters)
        
        return JsonResponse({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
@require_http_methods(["POST"])
def generate_employee_details_report(request):
    """
    API لإنشاء تقرير تفاصيل الموظفين
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', {})
        
        # تحويل التواريخ من string إلى date objects
        if filters.get('start_date'):
            filters['start_date'] = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
        
        if filters.get('end_date'):
            filters['end_date'] = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
        
        report = ReportService.get_employee_details_report(filters)
        
        return JsonResponse({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
@require_http_methods(["GET"])
def generate_organizational_structure_report(request):
    """
    API لإنشاء تقرير الهيكل التنظيمي
    """
    try:
        report = ReportService.get_organizational_structure_report()
        
        return JsonResponse({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
@require_http_methods(["POST"])
def generate_new_employees_report(request):
    """
    API لإنشاء تقرير الموظفين الجدد
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', {})
        
        # تحويل التواريخ من string إلى date objects
        if filters.get('start_date'):
            filters['start_date'] = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
        
        if filters.get('end_date'):
            filters['end_date'] = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
        
        report = ReportService.get_new_employees_report(filters)
        
        return JsonResponse({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
@require_http_methods(["POST"])
def generate_demographics_report(request):
    """
    API لإنشاء تقرير التركيبة السكانية
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', {})
        
        report = ReportService.get_demographics_report(filters)
        
        return JsonResponse({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
@require_http_methods(["POST"])
def generate_birthdays_anniversaries_report(request):
    """
    API لإنشاء تقرير أعياد الميلاد والذكريات
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', {})
        
        # تحويل التواريخ من string إلى date objects
        if filters.get('start_date'):
            filters['start_date'] = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
        
        if filters.get('end_date'):
            filters['end_date'] = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
        
        report = ReportService.get_birthdays_anniversaries_report(filters)
        
        return JsonResponse({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
@require_http_methods(["POST"])
def generate_attendance_analytics(request):
    """
    API لإنشاء تحليلات الحضور
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', {})
        
        # تحويل التواريخ من string إلى date objects
        if filters.get('start_date'):
            filters['start_date'] = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
        
        if filters.get('end_date'):
            filters['end_date'] = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
        
        report = ReportService.get_attendance_analytics(filters)
        
        return JsonResponse({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
@require_http_methods(["POST"])
def generate_salary_analytics(request):
    """
    API لإنشاء تحليلات الرواتب
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', {})
        
        report = ReportService.get_salary_analytics(filters)
        
        return JsonResponse({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
@require_http_methods(["POST"])
def export_report(request):
    """
    API لتصدير التقارير
    """
    try:
        data = json.loads(request.body)
        report_type = data.get('report_type')
        export_format = data.get('format', 'excel')
        filters = data.get('filters', {})
        
        if not report_type:
            return JsonResponse({
                'success': False,
                'error': 'نوع التقرير مطلوب'
            }, status=400)
        
        # تحويل التواريخ من string إلى date objects
        if filters.get('start_date'):
            filters['start_date'] = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
        
        if filters.get('end_date'):
            filters['end_date'] = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
        
        # إنشاء بيانات التقرير
        if report_type == 'employee_summary':
            report_data = ReportService.get_employee_summary_report(filters)
        elif report_type == 'employee_details':
            report_data = ReportService.get_employee_details_report(filters)
        elif report_type == 'org_structure':
            report_data = ReportService.get_organizational_structure_report()
        elif report_type == 'new_employees':
            report_data = ReportService.get_new_employees_report(filters)
        elif report_type == 'demographics':
            report_data = ReportService.get_demographics_report(filters)
        elif report_type == 'birthdays_anniversaries':
            report_data = ReportService.get_birthdays_anniversaries_report(filters)
        else:
            return JsonResponse({
                'success': False,
                'error': 'نوع تقرير غير صحيح'
            }, status=400)
        
        # تصدير التقرير
        if export_format == 'excel':
            file_content = ReportService.export_report_to_excel(report_data, report_type)
            response = HttpResponse(
                file_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
            return response
        
        elif export_format == 'pdf':
            file_content = ReportService.export_report_to_pdf(report_data, report_type)
            response = HttpResponse(file_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
            return response
        
        else:
            return JsonResponse({
                'success': False,
                'error': 'صيغة تصدير غير صحيحة'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
def get_dashboard_analytics(request):
    """
    API للحصول على تحليلات لوحة التحكم
    """
    try:
        # إحصائيات الموظفين
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(is_active=True).count()
        inactive_employees = Employee.objects.filter(is_active=False).count()
        
        # الموظفين الجدد (آخر 30 يوم)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        new_employees = Employee.objects.filter(
            hire_date__gte=thirty_days_ago
        ).count()
        
        # التوزيع حسب القسم
        department_distribution = list(
            Employee.objects.values('department__name_ar')
            .annotate(count=models.Count('id'))
            .order_by('-count')[:5]
        )
        
        # التوزيع حسب الجنس
        gender_distribution = list(
            Employee.objects.values('gender')
            .annotate(count=models.Count('id'))
        )
        
        analytics = {
            'employee_stats': {
                'total': total_employees,
                'active': active_employees,
                'inactive': inactive_employees,
                'new_this_month': new_employees
            },
            'department_distribution': department_distribution,
            'gender_distribution': gender_distribution,
            'last_updated': timezone.now().isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'data': analytics
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@hr_required
def schedule_report(request):
    """
    API لجدولة التقارير
    """
    try:
        data = json.loads(request.body)
        report_type = data.get('report_type')
        frequency = data.get('frequency')
        email = data.get('email')
        filters = data.get('filters', {})
        
        if not all([report_type, frequency, email]):
            return JsonResponse({
                'success': False,
                'error': 'جميع الحقول مطلوبة'
            }, status=400)
        
        # هنا يمكن إضافة منطق جدولة التقارير
        # مثل إنشاء مهمة في Celery أو إضافة إلى قاعدة البيانات
        
        return JsonResponse({
            'success': True,
            'message': f'تم جدولة التقرير بنجاح. سيتم إرساله {frequency} إلى {email}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)