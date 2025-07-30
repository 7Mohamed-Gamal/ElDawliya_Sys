"""
عروض مراقبة النظام
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.utils import timezone
from Hr.services.monitoring_service import monitoring_service
# from Hr.decorators.query_decorators import cache_query_result, monitor_query_performance

# Temporary decorators until the module is fixed
def cache_query_result(timeout=300, key_prefix='query', vary_on=None):
    def decorator(func):
        return func
    return decorator

def monitor_query_performance():
    def decorator(func):
        return func
    return decorator
import json


@method_decorator([login_required, staff_member_required], name='dispatch')
class SystemMonitoringDashboard(TemplateView):
    """لوحة تحكم مراقبة النظام"""
    template_name = 'Hr/monitoring/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # المقاييس الحالية
            current_metrics = monitoring_service.get_current_metrics()
            
            # نقاط صحة النظام
            health_score = monitoring_service.get_system_health_score()
            
            # التنبيهات النشطة
            active_alerts = monitoring_service.get_alerts(acknowledged=False)
            
            # الملخص اليومي
            daily_summary = monitoring_service.get_daily_summary()
            
            context.update({
                'current_metrics': current_metrics,
                'health_score': health_score,
                'active_alerts': active_alerts,
                'daily_summary': daily_summary,
                'critical_alerts_count': len([a for a in active_alerts if a.get('severity') == 'critical']),
                'warning_alerts_count': len([a for a in active_alerts if a.get('severity') == 'warning']),
            })
            
        except Exception as e:
            context['error'] = f'خطأ في تحميل بيانات المراقبة: {e}'
        
        return context


@login_required
@staff_member_required
@monitor_query_performance()
def get_current_metrics_api(request):
    """API للحصول على المقاييس الحالية"""
    try:
        metrics = monitoring_service.get_current_metrics()
        return JsonResponse({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@staff_member_required
@cache_query_result(timeout=60)
def get_metrics_history_api(request):
    """API للحصول على تاريخ المقاييس"""
    try:
        category = request.GET.get('category')
        hours = int(request.GET.get('hours', 24))
        
        history = monitoring_service.get_metrics_history(category, hours)
        
        return JsonResponse({
            'success': True,
            'data': history
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@staff_member_required
def get_alerts_api(request):
    """API للحصول على التنبيهات"""
    try:
        date = request.GET.get('date')
        acknowledged = request.GET.get('acknowledged')
        
        if acknowledged is not None:
            acknowledged = acknowledged.lower() == 'true'
        
        alerts = monitoring_service.get_alerts(date, acknowledged)
        
        return JsonResponse({
            'success': True,
            'data': alerts
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@staff_member_required
def acknowledge_alert_api(request):
    """API للإقرار بالتنبيه"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'طريقة غير مدعومة'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        alert_id = data.get('alert_id')
        
        if not alert_id:
            return JsonResponse({
                'success': False,
                'error': 'معرف التنبيه مطلوب'
            }, status=400)
        
        success = monitoring_service.acknowledge_alert(alert_id, request.user.id)
        
        return JsonResponse({
            'success': success,
            'message': 'تم الإقرار بالتنبيه' if success else 'فشل في الإقرار بالتنبيه'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@staff_member_required
def get_health_score_api(request):
    """API للحصول على نقاط صحة النظام"""
    try:
        health_score = monitoring_service.get_system_health_score()
        
        # تحديد الحالة
        if health_score >= 90:
            status = 'excellent'
            status_text = 'ممتاز'
        elif health_score >= 70:
            status = 'good'
            status_text = 'جيد'
        elif health_score >= 50:
            status = 'average'
            status_text = 'متوسط'
        else:
            status = 'poor'
            status_text = 'ضعيف'
        
        return JsonResponse({
            'success': True,
            'data': {
                'score': health_score,
                'status': status,
                'status_text': status_text
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@staff_member_required
@cache_query_result(timeout=300)
def get_daily_summary_api(request):
    """API للحصول على الملخص اليومي"""
    try:
        date = request.GET.get('date')
        summary = monitoring_service.get_daily_summary(date)
        
        return JsonResponse({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@method_decorator([login_required, staff_member_required], name='dispatch')
class SystemMetricsDetailView(TemplateView):
    """عرض تفاصيل مقاييس النظام"""
    template_name = 'Hr/monitoring/metrics_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            category = self.kwargs.get('category', 'system')
            hours = int(self.request.GET.get('hours', 24))
            
            # المقاييس الحالية
            current_metrics = monitoring_service.get_current_metrics()
            
            # تاريخ المقاييس
            metrics_history = monitoring_service.get_metrics_history(category, hours)
            
            context.update({
                'category': category,
                'hours': hours,
                'current_metrics': current_metrics,
                'metrics_history': metrics_history,
            })
            
        except Exception as e:
            context['error'] = f'خطأ في تحميل تفاصيل المقاييس: {e}'
        
        return context


@method_decorator([login_required, staff_member_required], name='dispatch')
class AlertsManagementView(TemplateView):
    """عرض إدارة التنبيهات"""
    template_name = 'Hr/monitoring/alerts_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # جميع التنبيهات
            all_alerts = monitoring_service.get_alerts()
            
            # التنبيهات غير المقرة
            unacknowledged_alerts = monitoring_service.get_alerts(acknowledged=False)
            
            # التنبيهات المقرة
            acknowledged_alerts = monitoring_service.get_alerts(acknowledged=True)
            
            # تصنيف التنبيهات حسب النوع
            alerts_by_type = {}
            for alert in all_alerts:
                alert_type = alert.get('type', 'unknown')
                if alert_type not in alerts_by_type:
                    alerts_by_type[alert_type] = []
                alerts_by_type[alert_type].append(alert)
            
            context.update({
                'all_alerts': all_alerts,
                'unacknowledged_alerts': unacknowledged_alerts,
                'acknowledged_alerts': acknowledged_alerts,
                'alerts_by_type': alerts_by_type,
                'critical_count': len([a for a in all_alerts if a.get('severity') == 'critical']),
                'warning_count': len([a for a in all_alerts if a.get('severity') == 'warning']),
            })
            
        except Exception as e:
            context['error'] = f'خطأ في تحميل التنبيهات: {e}'
        
        return context


@login_required
@staff_member_required
def system_performance_report(request):
    """تقرير أداء النظام"""
    try:
        # فترة التقرير
        days = int(request.GET.get('days', 7))
        
        # جمع البيانات لعدة أيام
        report_data = []
        for i in range(days):
            date = (timezone.now().date() - timezone.timedelta(days=i)).isoformat()
            daily_summary = monitoring_service.get_daily_summary(date)
            if daily_summary:
                report_data.append(daily_summary)
        
        # حساب الإحصائيات الإجمالية
        total_samples = sum(day.get('samples_count', 0) for day in report_data)
        total_alerts = sum(day.get('alerts_count', 0) for day in report_data)
        
        avg_cpu = sum(day.get('system', {}).get('cpu_avg', 0) for day in report_data) / len(report_data) if report_data else 0
        avg_memory = sum(day.get('system', {}).get('memory_avg', 0) for day in report_data) / len(report_data) if report_data else 0
        avg_disk = sum(day.get('system', {}).get('disk_avg', 0) for day in report_data) / len(report_data) if report_data else 0
        
        max_cpu = max((day.get('system', {}).get('cpu_max', 0) for day in report_data), default=0)
        max_memory = max((day.get('system', {}).get('memory_max', 0) for day in report_data), default=0)
        max_disk = max((day.get('system', {}).get('disk_max', 0) for day in report_data), default=0)
        
        context = {
            'days': days,
            'report_data': report_data,
            'summary': {
                'total_samples': total_samples,
                'total_alerts': total_alerts,
                'avg_cpu': avg_cpu,
                'avg_memory': avg_memory,
                'avg_disk': avg_disk,
                'max_cpu': max_cpu,
                'max_memory': max_memory,
                'max_disk': max_disk,
            }
        }
        
        return render(request, 'Hr/monitoring/performance_report.html', context)
        
    except Exception as e:
        return render(request, 'Hr/monitoring/performance_report.html', {
            'error': f'خطأ في إنتاج التقرير: {e}'
        })


@login_required
@staff_member_required
def export_metrics_data(request):
    """تصدير بيانات المقاييس"""
    try:
        format_type = request.GET.get('format', 'json')
        category = request.GET.get('category')
        hours = int(request.GET.get('hours', 24))
        
        # جمع البيانات
        if category:
            data = monitoring_service.get_metrics_history(category, hours)
        else:
            data = {
                'current_metrics': monitoring_service.get_current_metrics(),
                'daily_summary': monitoring_service.get_daily_summary(),
                'alerts': monitoring_service.get_alerts(),
                'health_score': monitoring_service.get_system_health_score()
            }
        
        if format_type == 'json':
            response = JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 2})
            response['Content-Disposition'] = f'attachment; filename="system_metrics_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
            return response
        
        elif format_type == 'csv':
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="system_metrics_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            
            # كتابة البيانات (مثال بسيط)
            if isinstance(data, list):
                if data:
                    # كتابة العناوين
                    headers = list(data[0].keys()) if data[0] else []
                    writer.writerow(headers)
                    
                    # كتابة البيانات
                    for row in data:
                        writer.writerow([row.get(header, '') for header in headers])
            
            return response
        
        else:
            return JsonResponse({
                'success': False,
                'error': 'تنسيق غير مدعوم'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)