"""
عروض مراقبة النظام
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views import View
from Hr.services.monitoring_service import monitoring_service
from Hr.decorators.performance_decorators import cache_result, monitor_performance
import json


@method_decorator(staff_member_required, name='dispatch')
class SystemMonitoringDashboard(TemplateView):
    """لوحة تحكم مراقبة النظام"""
    template_name = 'Hr/monitoring/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # الحصول على حالة النظام
            system_status = monitoring_service.get_system_status()
            
            context.update({
                'system_status': system_status,
                'page_title': 'مراقبة النظام',
                'monitoring_enabled': monitoring_service.monitoring_enabled
            })
        
        except Exception as e:
            context['error'] = str(e)
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class SystemStatusAPI(View):
    """API لحالة النظام"""
    
    @monitor_performance()
    @cache_result(timeout=60, key_prefix='system_status_api')
    def get(self, request):
        """الحصول على حالة النظام"""
        try:
            status = monitoring_service.get_system_status()
            return JsonResponse(status)
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)


@method_decorator(staff_member_required, name='dispatch')
class SystemAlertsAPI(View):
    """API للتنبيهات"""
    
    def get(self, request):
        """الحصول على التنبيهات النشطة"""
        try:
            alerts = monitoring_service.get_active_alerts()
            return JsonResponse({
                'alerts': alerts,
                'count': len(alerts)
            })
        
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


@method_decorator(staff_member_required, name='dispatch')
class MonitoringHistoryAPI(View):
    """API لتاريخ المراقبة"""
    
    def get(self, request):
        """الحصول على تاريخ المراقبة"""
        try:
            hours = int(request.GET.get('hours', 24))
            history = monitoring_service.get_monitoring_history(hours)
            
            return JsonResponse({
                'history': history,
                'hours': hours
            })
        
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


@method_decorator(staff_member_required, name='dispatch')
class SystemMetricsAPI(View):
    """API لمقاييس النظام المفصلة"""
    
    def get(self, request):
        """الحصول على مقاييس النظام"""
        try:
            metric_type = request.GET.get('type', 'all')
            status = monitoring_service.get_system_status()
            
            if metric_type == 'system':
                data = status.get('system', {})
            elif metric_type == 'database':
                data = status.get('database', {})
            elif metric_type == 'application':
                data = status.get('application', {})
            elif metric_type == 'performance':
                data = status.get('performance', {})
            else:
                data = status
            
            return JsonResponse(data)
        
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


@method_decorator(staff_member_required, name='dispatch')
class TriggerSystemCheckAPI(View):
    """API لتشغيل فحص النظام يدوياً"""
    
    def post(self, request):
        """تشغيل فحص النظام"""
        try:
            alerts = monitoring_service.check_and_alert()
            monitoring_service.save_monitoring_snapshot()
            
            return JsonResponse({
                'success': True,
                'alerts': alerts,
                'alert_count': len(alerts),
                'message': 'تم تشغيل فحص النظام بنجاح'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(staff_member_required, name='dispatch')
class ClearAlertsAPI(View):
    """API لمسح التنبيهات"""
    
    def post(self, request):
        """مسح التنبيهات النشطة"""
        try:
            from django.core.cache import cache
            
            # مسح التنبيهات النشطة
            cache.delete('active_alerts')
            
            return JsonResponse({
                'success': True,
                'message': 'تم مسح التنبيهات بنجاح'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(staff_member_required, name='dispatch')
class MonitoringSettingsAPI(View):
    """API لإعدادات المراقبة"""
    
    def get(self, request):
        """الحصول على إعدادات المراقبة"""
        try:
            settings_data = {
                'monitoring_enabled': monitoring_service.monitoring_enabled,
                'alert_thresholds': monitoring_service.alert_thresholds,
                'check_interval': monitoring_service.check_interval,
                'alert_emails': monitoring_service.alert_emails
            }
            
            return JsonResponse(settings_data)
        
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """تحديث إعدادات المراقبة"""
        try:
            data = json.loads(request.body)
            
            # تحديث الإعدادات (يمكن تحسين هذا لحفظ الإعدادات في قاعدة البيانات)
            if 'alert_thresholds' in data:
                monitoring_service.alert_thresholds.update(data['alert_thresholds'])
            
            if 'check_interval' in data:
                monitoring_service.check_interval = data['check_interval']
            
            return JsonResponse({
                'success': True,
                'message': 'تم تحديث الإعدادات بنجاح'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@staff_member_required
def monitoring_dashboard_view(request):
    """عرض لوحة تحكم المراقبة"""
    try:
        # الحصول على حالة النظام
        system_status = monitoring_service.get_system_status()
        
        # الحصول على التنبيهات النشطة
        active_alerts = monitoring_service.get_active_alerts()
        
        # الحصول على تاريخ مختصر (آخر 6 ساعات)
        history = monitoring_service.get_monitoring_history(6)
        
        context = {
            'system_status': system_status,
            'active_alerts': active_alerts,
            'history': history,
            'page_title': 'مراقبة النظام',
            'monitoring_enabled': monitoring_service.monitoring_enabled
        }
        
        return render(request, 'Hr/monitoring/dashboard.html', context)
    
    except Exception as e:
        context = {
            'error': str(e),
            'page_title': 'مراقبة النظام - خطأ'
        }
        return render(request, 'Hr/monitoring/dashboard.html', context)


@staff_member_required
def system_logs_view(request):
    """عرض سجلات النظام"""
    try:
        # يمكن تحسين هذا لقراءة السجلات من ملفات السجل الفعلية
        from django.core.cache import cache
        
        # الحصول على السجلات من التخزين المؤقت
        error_logs = cache.get('error_statistics', [])
        slow_queries = cache.get('slow_queries_log', [])
        slow_requests = cache.get('slow_requests_log', [])
        
        context = {
            'error_logs': error_logs[-50:],  # آخر 50 خطأ
            'slow_queries': slow_queries[-20:],  # آخر 20 استعلام بطيء
            'slow_requests': slow_requests[-20:],  # آخر 20 طلب بطيء
            'page_title': 'سجلات النظام'
        }
        
        return render(request, 'Hr/monitoring/logs.html', context)
    
    except Exception as e:
        context = {
            'error': str(e),
            'page_title': 'سجلات النظام - خطأ'
        }
        return render(request, 'Hr/monitoring/logs.html', context)


@staff_member_required
def performance_report_view(request):
    """عرض تقرير الأداء"""
    try:
        # الحصول على تقرير الأداء
        from Hr.services.query_optimizer import query_optimizer
        
        performance_report = query_optimizer.get_query_performance_report()
        system_status = monitoring_service.get_system_status()
        
        context = {
            'performance_report': performance_report,
            'system_status': system_status,
            'page_title': 'تقرير الأداء'
        }
        
        return render(request, 'Hr/monitoring/performance_report.html', context)
    
    except Exception as e:
        context = {
            'error': str(e),
            'page_title': 'تقرير الأداء - خطأ'
        }
        return render(request, 'Hr/monitoring/performance_report.html', context)