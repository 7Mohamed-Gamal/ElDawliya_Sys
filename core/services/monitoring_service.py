"""
Advanced Monitoring and Logging Service
======================================

This module provides comprehensive system monitoring including:
- Real-time performance monitoring
- Error tracking and alerting
- System health checks
- Automated alerts
- Usage analytics
"""

import logging
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db import connection
from django.core.cache import cache
from django.contrib.auth.models import User

from .cache_service import cache_service

logger = logging.getLogger(__name__)


class SystemMonitor:
    """مراقب النظام الشامل"""

    def __init__(self):
        """__init__ function"""
        self.alert_thresholds = {
            'cpu_usage': 80,        # CPU usage percentage
            'memory_usage': 85,     # Memory usage percentage
            'disk_usage': 90,       # Disk usage percentage
            'response_time': 2.0,   # Response time in seconds
            'error_rate': 5,        # Error rate percentage
            'query_count': 50,      # Max queries per request
        }

        self.monitoring_enabled = getattr(settings, 'MONITORING_ENABLED', True)
        self.alert_email = getattr(settings, 'ALERT_EMAIL', None)

    def get_system_metrics(self) -> Dict[str, Any]:
        """الحصول على مقاييس النظام"""

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB

            # Network metrics
            network = psutil.net_io_counters()

            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss / (1024**2)  # MB
            process_cpu = process.cpu_percent()

            metrics = {
                'timestamp': timezone.now().isoformat(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'process_usage': process_cpu,
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'available_gb': round(memory_available, 2),
                    'total_gb': round(memory_total, 2),
                    'process_mb': round(process_memory, 2),
                },
                'disk': {
                    'usage_percent': disk_percent,
                    'free_gb': round(disk_free, 2),
                    'total_gb': round(disk_total, 2),
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv,
                },
            }

            return metrics

        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }

    def get_database_metrics(self) -> Dict[str, Any]:
        """الحصول على مقاييس قاعدة البيانات"""

        try:
            with connection.cursor() as cursor:
                # Get database size and statistics
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_connections,
                        SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as active_connections
                    FROM sys.dm_exec_sessions
                    WHERE is_user_process = 1
                """)

                connection_stats = cursor.fetchone()

                # Get database size
                cursor.execute("""
                    SELECT
                        SUM(size * 8.0 / 1024) as size_mb
                    FROM sys.master_files
                    WHERE database_id = DB_ID()
                """)

                size_result = cursor.fetchone()
                db_size_mb = size_result[0] if size_result and size_result[0] else 0

                # Get query performance stats
                query_count = len(connection.queries)

                metrics = {
                    'timestamp': timezone.now().isoformat(),
                    'connections': {
                        'total': connection_stats[0] if connection_stats else 0,
                        'active': connection_stats[1] if connection_stats else 0,
                    },
                    'size_mb': round(db_size_mb, 2),
                    'query_count': query_count,
                }

                return metrics

        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }

    def get_application_metrics(self) -> Dict[str, Any]:
        """الحصول على مقاييس التطبيق"""

        try:
            # Get user statistics
            total_users = User.objects.count()
            active_users_today = User.objects.filter(
                last_login__gte=timezone.now() - timedelta(days=1)
            ).count()

            # Get cache statistics
            cache_stats = cache_service.get_stats()

            # Get error statistics from logs
            error_stats = self._get_error_statistics()

            metrics = {
                'timestamp': timezone.now().isoformat(),
                'users': {
                    'total': total_users,
                    'active_today': active_users_today,
                },
                'cache': cache_stats,
                'errors': error_stats,
            }

            return metrics

        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }

    def _get_error_statistics(self) -> Dict[str, int]:
        """الحصول على إحصائيات الأخطاء"""

        # This would typically read from log files or error tracking service
        # For now, return mock data
        return {
            'total_errors_today': 0,
            'critical_errors': 0,
            'warning_count': 0,
        }

    def check_system_health(self) -> Dict[str, Any]:
        """فحص صحة النظام"""

        health_status = {
            'overall_status': 'healthy',
            'checks': [],
            'timestamp': timezone.now().isoformat(),
        }

        # Get system metrics
        system_metrics = self.get_system_metrics()
        db_metrics = self.get_database_metrics()
        app_metrics = self.get_application_metrics()

        # Check CPU usage
        cpu_usage = system_metrics.get('cpu', {}).get('usage_percent', 0)
        if cpu_usage > self.alert_thresholds['cpu_usage']:
            health_status['checks'].append({
                'name': 'CPU Usage',
                'status': 'critical',
                'message': f'High CPU usage: {cpu_usage}%',
                'value': cpu_usage,
                'threshold': self.alert_thresholds['cpu_usage']
            })
            health_status['overall_status'] = 'critical'
        elif cpu_usage > self.alert_thresholds['cpu_usage'] * 0.8:
            health_status['checks'].append({
                'name': 'CPU Usage',
                'status': 'warning',
                'message': f'Elevated CPU usage: {cpu_usage}%',
                'value': cpu_usage,
                'threshold': self.alert_thresholds['cpu_usage']
            })
            if health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'
        else:
            health_status['checks'].append({
                'name': 'CPU Usage',
                'status': 'healthy',
                'message': f'CPU usage normal: {cpu_usage}%',
                'value': cpu_usage,
                'threshold': self.alert_thresholds['cpu_usage']
            })

        # Check Memory usage
        memory_usage = system_metrics.get('memory', {}).get('usage_percent', 0)
        if memory_usage > self.alert_thresholds['memory_usage']:
            health_status['checks'].append({
                'name': 'Memory Usage',
                'status': 'critical',
                'message': f'High memory usage: {memory_usage}%',
                'value': memory_usage,
                'threshold': self.alert_thresholds['memory_usage']
            })
            health_status['overall_status'] = 'critical'
        elif memory_usage > self.alert_thresholds['memory_usage'] * 0.8:
            health_status['checks'].append({
                'name': 'Memory Usage',
                'status': 'warning',
                'message': f'Elevated memory usage: {memory_usage}%',
                'value': memory_usage,
                'threshold': self.alert_thresholds['memory_usage']
            })
            if health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'
        else:
            health_status['checks'].append({
                'name': 'Memory Usage',
                'status': 'healthy',
                'message': f'Memory usage normal: {memory_usage}%',
                'value': memory_usage,
                'threshold': self.alert_thresholds['memory_usage']
            })

        # Check Disk usage
        disk_usage = system_metrics.get('disk', {}).get('usage_percent', 0)
        if disk_usage > self.alert_thresholds['disk_usage']:
            health_status['checks'].append({
                'name': 'Disk Usage',
                'status': 'critical',
                'message': f'High disk usage: {disk_usage}%',
                'value': disk_usage,
                'threshold': self.alert_thresholds['disk_usage']
            })
            health_status['overall_status'] = 'critical'
        elif disk_usage > self.alert_thresholds['disk_usage'] * 0.8:
            health_status['checks'].append({
                'name': 'Disk Usage',
                'status': 'warning',
                'message': f'Elevated disk usage: {disk_usage}%',
                'value': disk_usage,
                'threshold': self.alert_thresholds['disk_usage']
            })
            if health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'
        else:
            health_status['checks'].append({
                'name': 'Disk Usage',
                'status': 'healthy',
                'message': f'Disk usage normal: {disk_usage}%',
                'value': disk_usage,
                'threshold': self.alert_thresholds['disk_usage']
            })

        # Check Database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_status['checks'].append({
                    'name': 'Database Connection',
                    'status': 'healthy',
                    'message': 'Database connection is working'
                })
        except Exception as e:
            health_status['checks'].append({
                'name': 'Database Connection',
                'status': 'critical',
                'message': f'Database connection failed: {str(e)}'
            })
            health_status['overall_status'] = 'critical'

        # Check Cache connectivity
        try:
            cache.set('health_check', 'test', 60)
            cache.get('health_check')
            health_status['checks'].append({
                'name': 'Cache System',
                'status': 'healthy',
                'message': 'Cache system is working'
            })
        except Exception as e:
            health_status['checks'].append({
                'name': 'Cache System',
                'status': 'warning',
                'message': f'Cache system issue: {str(e)}'
            })
            if health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'

        return health_status

    def send_alert(self, alert_type: str, message: str, severity: str = 'warning'):
        """إرسال تنبيه"""

        if not self.monitoring_enabled or not self.alert_email:
            return

        try:
            subject = f"[ElDawliya System] {severity.upper()}: {alert_type}"

            email_body = f"""
            تنبيه من نظام الدولية
            ==================

            النوع: {alert_type}
            الخطورة: {severity}
            الوقت: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

            الرسالة:
            {message}

            ---
            نظام مراقبة الدولية
            """

            send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.alert_email],
                fail_silently=True
            )

            logger.info(f"Alert sent: {alert_type} - {severity}")

        except Exception as e:
            logger.error(f"Failed to send alert: {e}")


class PerformanceAnalyzer:
    """محلل الأداء"""

    def __init__(self):
        """__init__ function"""
        self.metrics_cache_key = 'performance_metrics'
        self.metrics_retention_hours = 24

    def record_request_metrics(self, request_path: str, response_time: float,
                             query_count: int, status_code: int):
        """
        record_request_metrics function
        تسجيل مقاييس الطلب
        """

        metrics = {
            'timestamp': timezone.now().isoformat(),
            'path': request_path,
            'response_time': response_time,
            'query_count': query_count,
            'status_code': status_code,
        }

        # Store in cache for real-time analysis
        cache_key = f"{self.metrics_cache_key}_{timezone.now().strftime('%Y%m%d%H')}"

        try:
            existing_metrics = cache.get(cache_key, [])
            existing_metrics.append(metrics)

            # Keep only last 1000 entries per hour
            if len(existing_metrics) > 1000:
                existing_metrics = existing_metrics[-1000:]

            cache.set(cache_key, existing_metrics, 3600)  # 1 hour

        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")

    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """الحصول على ملخص الأداء"""

        try:
            all_metrics = []

            # Collect metrics from last N hours
            for i in range(hours):
                hour_ago = timezone.now() - timedelta(hours=i)
                cache_key = f"{self.metrics_cache_key}_{hour_ago.strftime('%Y%m%d%H')}"
                hour_metrics = cache.get(cache_key, [])
                all_metrics.extend(hour_metrics)

            if not all_metrics:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'avg_query_count': 0,
                    'error_rate': 0,
                    'slowest_endpoints': [],
                    'most_queried_endpoints': [],
                }

            # Calculate summary statistics
            total_requests = len(all_metrics)
            avg_response_time = sum(m['response_time'] for m in all_metrics) / total_requests
            avg_query_count = sum(m['query_count'] for m in all_metrics) / total_requests

            error_requests = [m for m in all_metrics if m['status_code'] >= 400]
            error_rate = (len(error_requests) / total_requests) * 100

            # Group by endpoint
            endpoint_stats = {}
            for metric in all_metrics:
                path = metric['path']
                if path not in endpoint_stats:
                    endpoint_stats[path] = {
                        'count': 0,
                        'total_response_time': 0,
                        'total_query_count': 0,
                        'errors': 0,
                    }

                stats = endpoint_stats[path]
                stats['count'] += 1
                stats['total_response_time'] += metric['response_time']
                stats['total_query_count'] += metric['query_count']
                if metric['status_code'] >= 400:
                    stats['errors'] += 1

            # Calculate averages and sort
            for path, stats in endpoint_stats.items():
                stats['avg_response_time'] = stats['total_response_time'] / stats['count']
                stats['avg_query_count'] = stats['total_query_count'] / stats['count']
                stats['error_rate'] = (stats['errors'] / stats['count']) * 100

            # Get slowest endpoints
            slowest_endpoints = sorted(
                endpoint_stats.items(),
                key=lambda x: x[1]['avg_response_time'],
                reverse=True
            )[:10]

            # Get most queried endpoints
            most_queried_endpoints = sorted(
                endpoint_stats.items(),
                key=lambda x: x[1]['avg_query_count'],
                reverse=True
            )[:10]

            return {
                'total_requests': total_requests,
                'avg_response_time': round(avg_response_time, 3),
                'avg_query_count': round(avg_query_count, 1),
                'error_rate': round(error_rate, 2),
                'slowest_endpoints': [
                    {
                        'path': path,
                        'avg_response_time': round(stats['avg_response_time'], 3),
                        'count': stats['count']
                    }
                    for path, stats in slowest_endpoints
                ],
                'most_queried_endpoints': [
                    {
                        'path': path,
                        'avg_query_count': round(stats['avg_query_count'], 1),
                        'count': stats['count']
                    }
                    for path, stats in most_queried_endpoints
                ],
                'timestamp': timezone.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {
                'error': str(e),
                'timestamp': timezone.now().isoformat(),
            }


class AlertManager:
    """مدير التنبيهات"""

    def __init__(self):
        """__init__ function"""
        self.alert_rules = [
            {
                'name': 'High CPU Usage',
                'condition': lambda metrics: metrics.get('cpu', {}).get('usage_percent', 0) > 80,
                'severity': 'critical',
                'cooldown': 300,  # 5 minutes
            },
            {
                'name': 'High Memory Usage',
                'condition': lambda metrics: metrics.get('memory', {}).get('usage_percent', 0) > 85,
                'severity': 'critical',
                'cooldown': 300,
            },
            {
                'name': 'High Disk Usage',
                'condition': lambda metrics: metrics.get('disk', {}).get('usage_percent', 0) > 90,
                'severity': 'critical',
                'cooldown': 600,  # 10 minutes
            },
            {
                'name': 'High Error Rate',
                'condition': lambda metrics: metrics.get('error_rate', 0) > 5,
                'severity': 'warning',
                'cooldown': 300,
            },
        ]

        self.alert_history_key = 'alert_history'

    def check_alerts(self, system_metrics: Dict, performance_metrics: Dict):
        """فحص التنبيهات"""

        current_time = timezone.now()
        alert_history = cache.get(self.alert_history_key, {})

        for rule in self.alert_rules:
            rule_name = rule['name']

            # Check if alert is in cooldown
            last_alert_time = alert_history.get(rule_name)
            if last_alert_time:
                last_alert = datetime.fromisoformat(last_alert_time)
                if (current_time - last_alert).total_seconds() < rule['cooldown']:
                    continue

            # Check condition
            combined_metrics = {**system_metrics, **performance_metrics}

            try:
                if rule['condition'](combined_metrics):
                    self._trigger_alert(rule, combined_metrics)
                    alert_history[rule_name] = current_time.isoformat()
            except Exception as e:
                logger.error(f"Error checking alert rule {rule_name}: {e}")

        # Update alert history
        cache.set(self.alert_history_key, alert_history, 86400)  # 24 hours

    def _trigger_alert(self, rule: Dict, metrics: Dict):
        """تشغيل التنبيه"""

        message = f"Alert triggered: {rule['name']}\n"
        message += f"Severity: {rule['severity']}\n"
        message += f"Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"Metrics: {json.dumps(metrics, indent=2)}"

        logger.warning(f"ALERT: {rule['name']} - {rule['severity']}")

        # Send notification (email, Slack, etc.)
        system_monitor = SystemMonitor()
        system_monitor.send_alert(rule['name'], message, rule['severity'])


# Global instances
system_monitor = SystemMonitor()
performance_analyzer = PerformanceAnalyzer()
alert_manager = AlertManager()


# Monitoring middleware
class SystemMonitoringMiddleware:
    """وسطاء مراقبة النظام"""

    def __init__(self, get_response):
        """__init__ function"""
        self.get_response = get_response

    def __call__(self, request):
        """__call__ function"""
        start_time = time.time()
        initial_query_count = len(connection.queries)

        response = self.get_response(request)

        # Calculate metrics
        response_time = time.time() - start_time
        query_count = len(connection.queries) - initial_query_count

        # Record metrics
        performance_analyzer.record_request_metrics(
            request_path=request.path,
            response_time=response_time,
            query_count=query_count,
            status_code=response.status_code
        )

        return response
