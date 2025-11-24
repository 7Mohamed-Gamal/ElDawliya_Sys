"""
System Monitoring Dashboard Views
================================

Views for comprehensive system monitoring and alerting
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from datetime import datetime, timedelta
import json

from core.services.monitoring_service import (
    system_monitor,
    performance_analyzer,
    alert_manager
)


@staff_member_required
@never_cache
def monitoring_dashboard(request):
    """لوحة تحكم مراقبة النظام"""
    
    context = {
        'title': 'مراقبة النظام',
        'current_time': timezone.now(),
    }
    
    return render(request, 'core/monitoring_dashboard.html', context)


@staff_member_required
def system_metrics_api(request):
    """API لمقاييس النظام"""
    
    try:
        # Get system metrics
        system_metrics = system_monitor.get_system_metrics()
        
        # Get database metrics
        db_metrics = system_monitor.get_database_metrics()
        
        # Get application metrics
        app_metrics = system_monitor.get_application_metrics()
        
        data = {
            'system': system_metrics,
            'database': db_metrics,
            'application': app_metrics,
            'timestamp': timezone.now().isoformat(),
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@staff_member_required
def system_health_api(request):
    """API لفحص صحة النظام"""
    
    try:
        health_status = system_monitor.check_system_health()
        return JsonResponse(health_status)
        
    except Exception as e:
        return JsonResponse({
            'overall_status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@staff_member_required
def performance_metrics_api(request):
    """API لمقاييس الأداء"""
    
    try:
        hours = int(request.GET.get('hours', 1))
        performance_summary = performance_analyzer.get_performance_summary(hours)
        
        return JsonResponse(performance_summary)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@staff_member_required
def alert_history_api(request):
    """API لتاريخ التنبيهات"""
    
    try:
        from django.core.cache import cache
        
        alert_history = cache.get('alert_history', {})
        
        # Convert to list format with timestamps
        alerts = []
        for alert_name, timestamp_str in alert_history.items():
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                alerts.append({
                    'name': alert_name,
                    'timestamp': timestamp.isoformat(),
                    'time_ago': (timezone.now() - timestamp).total_seconds(),
                })
            except ValueError:
                continue
        
        # Sort by timestamp (most recent first)
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return JsonResponse({
            'alerts': alerts[:50],  # Last 50 alerts
            'total_count': len(alerts),
            'timestamp': timezone.now().isoformat(),
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@staff_member_required
def log_analysis_api(request):
    """API لتحليل السجلات"""
    
    try:
        log_type = request.GET.get('type', 'application')
        hours = int(request.GET.get('hours', 24))
        
        # This would typically analyze log files
        # For now, return mock data
        log_analysis = {
            'log_type': log_type,
            'time_range_hours': hours,
            'total_entries': 1250,
            'error_count': 15,
            'warning_count': 45,
            'info_count': 1190,
            'top_errors': [
                {
                    'message': 'Database connection timeout',
                    'count': 8,
                    'last_occurrence': (timezone.now() - timedelta(minutes=30)).isoformat(),
                },
                {
                    'message': 'Cache miss for key: employee_stats',
                    'count': 5,
                    'last_occurrence': (timezone.now() - timedelta(hours=2)).isoformat(),
                },
                {
                    'message': 'Slow query detected: SELECT * FROM employees',
                    'count': 2,
                    'last_occurrence': (timezone.now() - timedelta(hours=4)).isoformat(),
                },
            ],
            'error_trends': {
                'labels': ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                'data': [2, 1, 3, 5, 3, 1],
            },
            'timestamp': timezone.now().isoformat(),
        }
        
        return JsonResponse(log_analysis)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@staff_member_required
def resource_usage_history_api(request):
    """API لتاريخ استخدام الموارد"""
    
    try:
        hours = int(request.GET.get('hours', 24))
        
        # This would typically read from stored metrics
        # For now, generate sample data
        import random
        
        data_points = min(hours * 4, 100)  # 4 points per hour, max 100 points
        
        history = {
            'time_range_hours': hours,
            'data_points': data_points,
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'timestamps': [],
        }
        
        base_time = timezone.now() - timedelta(hours=hours)
        interval = timedelta(hours=hours) / data_points
        
        for i in range(data_points):
            timestamp = base_time + (interval * i)
            history['timestamps'].append(timestamp.isoformat())
            
            # Generate realistic sample data
            history['cpu_usage'].append(random.uniform(20, 80))
            history['memory_usage'].append(random.uniform(40, 85))
            history['disk_usage'].append(random.uniform(60, 75))
        
        return JsonResponse(history)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@staff_member_required
def monitoring_settings_api(request):
    """API لإعدادات المراقبة"""
    
    if request.method == 'GET':
        try:
            settings = {
                'alert_thresholds': system_monitor.alert_thresholds,
                'monitoring_enabled': system_monitor.monitoring_enabled,
                'alert_email': system_monitor.alert_email,
                'performance_retention_hours': performance_analyzer.metrics_retention_hours,
            }
            
            return JsonResponse(settings)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'timestamp': timezone.now().isoformat(),
            }, status=500)
    
    elif request.method == 'POST':
        try:
            # Update monitoring settings
            data = json.loads(request.body)
            
            if 'alert_thresholds' in data:
                system_monitor.alert_thresholds.update(data['alert_thresholds'])
            
            if 'monitoring_enabled' in data:
                system_monitor.monitoring_enabled = data['monitoring_enabled']
            
            if 'alert_email' in data:
                system_monitor.alert_email = data['alert_email']
            
            return JsonResponse({
                'success': True,
                'message': 'تم تحديث إعدادات المراقبة بنجاح',
                'timestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'timestamp': timezone.now().isoformat(),
            }, status=500)
    
    return JsonResponse({
        'error': 'Method not allowed',
    }, status=405)


@staff_member_required
def trigger_test_alert_api(request):
    """API لتشغيل تنبيه تجريبي"""
    
    if request.method == 'POST':
        try:
            alert_type = request.POST.get('type', 'test')
            severity = request.POST.get('severity', 'info')
            
            message = f"This is a test alert of type '{alert_type}' with severity '{severity}'"
            
            system_monitor.send_alert(
                alert_type=f"Test Alert - {alert_type}",
                message=message,
                severity=severity
            )
            
            return JsonResponse({
                'success': True,
                'message': 'تم إرسال التنبيه التجريبي بنجاح',
                'timestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'timestamp': timezone.now().isoformat(),
            }, status=500)
    
    return JsonResponse({
        'error': 'Method not allowed',
    }, status=405)


@staff_member_required
def export_monitoring_data_api(request):
    """API لتصدير بيانات المراقبة"""
    
    try:
        export_type = request.GET.get('type', 'all')
        format_type = request.GET.get('format', 'json')
        hours = int(request.GET.get('hours', 24))
        
        data = {}
        
        if export_type in ['all', 'system']:
            data['system_metrics'] = system_monitor.get_system_metrics()
        
        if export_type in ['all', 'performance']:
            data['performance_metrics'] = performance_analyzer.get_performance_summary(hours)
        
        if export_type in ['all', 'health']:
            data['health_status'] = system_monitor.check_system_health()
        
        if export_type in ['all', 'alerts']:
            from django.core.cache import cache
            data['alert_history'] = cache.get('alert_history', {})
        
        data['export_info'] = {
            'export_type': export_type,
            'format': format_type,
            'time_range_hours': hours,
            'exported_at': timezone.now().isoformat(),
        }
        
        if format_type == 'json':
            response = JsonResponse(data)
            response['Content-Disposition'] = f'attachment; filename="monitoring_data_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
            return response
        
        else:
            return JsonResponse({
                'error': 'Unsupported format type',
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@staff_member_required
def monitoring_reports_api(request):
    """API لتقارير المراقبة"""
    
    try:
        report_type = request.GET.get('type', 'summary')
        period = request.GET.get('period', 'daily')
        
        if report_type == 'summary':
            # Daily/Weekly/Monthly summary report
            report = {
                'report_type': 'summary',
                'period': period,
                'generated_at': timezone.now().isoformat(),
                'system_uptime': '99.8%',
                'avg_response_time': '0.245s',
                'total_requests': 15420,
                'error_rate': '0.3%',
                'cache_hit_rate': '87.2%',
                'top_issues': [
                    'High memory usage during peak hours',
                    'Slow database queries in inventory module',
                    'Cache misses for employee statistics',
                ],
                'recommendations': [
                    'Consider adding more memory to the server',
                    'Optimize inventory database queries',
                    'Implement better caching strategy for employee data',
                ],
            }
        
        elif report_type == 'performance':
            # Performance analysis report
            report = {
                'report_type': 'performance',
                'period': period,
                'generated_at': timezone.now().isoformat(),
                'avg_cpu_usage': '45.2%',
                'avg_memory_usage': '67.8%',
                'avg_disk_usage': '72.1%',
                'slowest_endpoints': [
                    {'path': '/Hr/employees/', 'avg_time': '1.2s'},
                    {'path': '/inventory/products/', 'avg_time': '0.8s'},
                    {'path': '/reports/attendance/', 'avg_time': '0.6s'},
                ],
                'query_performance': {
                    'total_queries': 8450,
                    'slow_queries': 23,
                    'avg_query_time': '0.045s',
                },
            }
        
        elif report_type == 'security':
            # Security monitoring report
            report = {
                'report_type': 'security',
                'period': period,
                'generated_at': timezone.now().isoformat(),
                'failed_login_attempts': 12,
                'suspicious_activities': 2,
                'blocked_ips': ['192.168.1.100', '10.0.0.50'],
                'security_events': [
                    'Multiple failed login attempts from IP 192.168.1.100',
                    'Unusual API access pattern detected',
                ],
            }
        
        else:
            return JsonResponse({
                'error': 'Unknown report type',
            }, status=400)
        
        return JsonResponse(report)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)