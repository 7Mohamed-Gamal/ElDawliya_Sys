"""
خدمة مراقبة النظام المتقدمة
"""

import logging
import time
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.db import connection
from django.utils import timezone
from django.core.mail import send_mail
import os
import psutil

logger = logging.getLogger(__name__)


class SystemMonitoringService:
    """خدمة مراقبة النظام الشاملة"""
    
    def __init__(self):
        self.monitoring_enabled = getattr(settings, 'ENABLE_SYSTEM_MONITORING', True)
        self.alert_thresholds = getattr(settings, 'MONITORING_THRESHOLDS', {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90,
            'response_time': 2.0,
            'error_rate': 5.0,
            'database_connections': 80
        })
        self.alert_emails = getattr(settings, 'MONITORING_ALERT_EMAILS', [])
        self.check_interval = getattr(settings, 'MONITORING_CHECK_INTERVAL', 300)  # 5 دقائق
    
    def get_system_status(self):
        """الحصول على حالة النظام الشاملة"""
        if not self.monitoring_enabled:
            return {'status': 'monitoring_disabled'}
        
        try:
            status = {
                'timestamp': timezone.now().isoformat(),
                'overall_status': 'healthy',
                'system': self.get_system_metrics(),
                'database': self.get_database_metrics(),
                'application': self.get_application_metrics(),
                'performance': self.get_performance_metrics(),
                'alerts': self.get_active_alerts()
            }
            
            # تحديد الحالة العامة
            status['overall_status'] = self.determine_overall_status(status)
            
            return status
        
        except Exception as e:
            logger.error(f'خطأ في الحصول على حالة النظام: {e}')
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    def get_system_metrics(self):
        """الحصول على مقاييس النظام"""
        try:
            # معلومات المعالج
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # معلومات الذاكرة
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            # معلومات القرص
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            # معلومات الشبكة
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'status': 'warning' if cpu_percent > self.alert_thresholds['cpu_usage'] else 'normal'
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'available_gb': round(memory_available, 2),
                    'total_gb': round(memory_total, 2),
                    'status': 'warning' if memory_percent > self.alert_thresholds['memory_usage'] else 'normal'
                },
                'disk': {
                    'usage_percent': disk_percent,
                    'free_gb': round(disk_free, 2),
                    'total_gb': round(disk_total, 2),
                    'status': 'warning' if disk_percent > self.alert_thresholds['disk_usage'] else 'normal'
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
        
        except Exception as e:
            logger.error(f'خطأ في الحصول على مقاييس النظام: {e}')
            return {'error': str(e)}
    
    def get_database_metrics(self):
        """الحصول على مقاييس قاعدة البيانات"""
        try:
            # عدد الاستعلامات
            query_count = len(connection.queries)
            
            # حالة الاتصال
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_connected = True
            
            # معلومات قاعدة البيانات حسب النوع
            db_info = self.get_database_specific_info()
            
            return {
                'connected': db_connected,
                'query_count': query_count,
                'vendor': connection.vendor,
                'database_info': db_info,
                'status': 'normal' if db_connected else 'error'
            }
        
        except Exception as e:
            logger.error(f'خطأ في الحصول على مقاييس قاعدة البيانات: {e}')
            return {
                'connected': False,
                'error': str(e),
                'status': 'error'
            }
    
    def get_database_specific_info(self):
        """الحصول على معلومات قاعدة البيانات المحددة"""
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT 
                            count(*) as active_connections,
                            pg_size_pretty(pg_database_size(current_database())) as db_size
                        FROM pg_stat_activity 
                        WHERE state = 'active'
                    """)
                    result = cursor.fetchone()
                    return {
                        'active_connections': result[0],
                        'database_size': result[1]
                    }
                
                elif connection.vendor == 'mysql':
                    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                    connections = cursor.fetchone()
                    
                    cursor.execute("""
                        SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS 'DB Size in MB' 
                        FROM information_schema.tables 
                        WHERE table_schema=DATABASE()
                    """)
                    size = cursor.fetchone()
                    
                    return {
                        'active_connections': connections[1] if connections else 0,
                        'database_size': f"{size[0]} MB" if size else "Unknown"
                    }
                
                elif connection.vendor == 'sqlite':
                    cursor.execute("PRAGMA database_list")
                    db_info = cursor.fetchone()
                    
                    # حجم ملف قاعدة البيانات
                    if db_info and db_info[2]:
                        db_size = os.path.getsize(db_info[2]) / (1024**2)  # MB
                        return {
                            'database_file': db_info[2],
                            'database_size': f"{db_size:.1f} MB"
                        }
                
                return {'info': 'Database info not available for this vendor'}
        
        except Exception as e:
            logger.error(f'خطأ في الحصول على معلومات قاعدة البيانات: {e}')
            return {'error': str(e)}
    
    def get_application_metrics(self):
        """الحصول على مقاييس التطبيق"""
        try:
            # إحصائيات التخزين المؤقت
            cache_stats = self.get_cache_statistics()
            
            # إحصائيات الأخطاء
            error_stats = self.get_error_statistics()
            
            # إحصائيات المستخدمين
            user_stats = self.get_user_statistics()
            
            # إحصائيات الطلبات
            request_stats = self.get_request_statistics()
            
            return {
                'cache': cache_stats,
                'errors': error_stats,
                'users': user_stats,
                'requests': request_stats,
                'uptime': self.get_application_uptime()
            }
        
        except Exception as e:
            logger.error(f'خطأ في الحصول على مقاييس التطبيق: {e}')
            return {'error': str(e)}
    
    def get_cache_statistics(self):
        """إحصائيات التخزين المؤقت"""
        try:
            # محاولة الحصول على إحصائيات التخزين المؤقت
            cache_stats = cache.get('cache_statistics', {
                'hits': 0,
                'misses': 0,
                'total_keys': 0
            })
            
            total_operations = cache_stats['hits'] + cache_stats['misses']
            hit_rate = (cache_stats['hits'] / total_operations * 100) if total_operations > 0 else 0
            
            return {
                'hit_rate': round(hit_rate, 2),
                'total_operations': total_operations,
                'total_keys': cache_stats['total_keys'],
                'status': 'normal' if hit_rate > 70 else 'warning'
            }
        
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def get_error_statistics(self):
        """إحصائيات الأخطاء"""
        try:
            # الحصول على أخطاء آخر 24 ساعة
            error_log = cache.get('error_statistics', [])
            
            # فلترة الأخطاء حسب الوقت
            now = timezone.now()
            last_24h = now - timedelta(hours=24)
            
            recent_errors = [
                error for error in error_log 
                if datetime.fromisoformat(error.get('timestamp', '')) > last_24h
            ]
            
            error_count = len(recent_errors)
            error_rate = error_count / 24  # أخطاء في الساعة
            
            return {
                'total_errors_24h': error_count,
                'error_rate_per_hour': round(error_rate, 2),
                'status': 'warning' if error_rate > self.alert_thresholds['error_rate'] else 'normal'
            }
        
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def get_user_statistics(self):
        """إحصائيات المستخدمين"""
        try:
            from django.contrib.auth.models import User
            from django.contrib.sessions.models import Session
            
            # إجمالي المستخدمين
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            
            # الجلسات النشطة
            active_sessions = Session.objects.filter(
                expire_date__gte=timezone.now()
            ).count()
            
            # المستخدمين المتصلين حالياً (تقدير)
            online_users = cache.get('online_users_count', 0)
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'active_sessions': active_sessions,
                'online_users': online_users
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_request_statistics(self):
        """إحصائيات الطلبات"""
        try:
            # الحصول على إحصائيات الطلبات من التخزين المؤقت
            today = timezone.now().date().isoformat()
            request_stats = cache.get(f'request_statistics_{today}', {
                'total_requests': 0,
                'avg_response_time': 0,
                'slow_requests': 0
            })
            
            avg_response_time = request_stats.get('avg_response_time', 0)
            
            return {
                'total_requests_today': request_stats.get('total_requests', 0),
                'avg_response_time': round(avg_response_time, 3),
                'slow_requests': request_stats.get('slow_requests', 0),
                'status': 'warning' if avg_response_time > self.alert_thresholds['response_time'] else 'normal'
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_application_uptime(self):
        """وقت تشغيل التطبيق"""
        try:
            # محاولة الحصول على وقت بدء التطبيق
            start_time = cache.get('application_start_time')
            if not start_time:
                # إذا لم يكن محفوظاً، احفظه الآن
                start_time = timezone.now().isoformat()
                cache.set('application_start_time', start_time, None)  # بدون انتهاء صلاحية
            
            start_datetime = datetime.fromisoformat(start_time)
            uptime = timezone.now() - start_datetime
            
            return {
                'start_time': start_time,
                'uptime_seconds': int(uptime.total_seconds()),
                'uptime_formatted': str(uptime).split('.')[0]  # إزالة الميكروثواني
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_performance_metrics(self):
        """مقاييس الأداء"""
        try:
            # الاستعلامات البطيئة
            slow_queries = cache.get('slow_queries_log', [])
            slow_query_count = len(slow_queries)
            
            # الطلبات البطيئة
            slow_requests = cache.get('slow_requests_log', [])
            slow_request_count = len(slow_requests)
            
            # متوسط وقت الاستجابة
            today_stats = cache.get(f'performance_stats_{timezone.now().date().isoformat()}', {})
            avg_response_time = today_stats.get('total_time', 0) / max(today_stats.get('total_requests', 1), 1)
            
            return {
                'slow_queries': slow_query_count,
                'slow_requests': slow_request_count,
                'avg_response_time': round(avg_response_time, 3),
                'status': 'warning' if slow_query_count > 10 or slow_request_count > 5 else 'normal'
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_active_alerts(self):
        """الحصول على التنبيهات النشطة"""
        try:
            alerts = cache.get('active_alerts', [])
            
            # فلترة التنبيهات النشطة (آخر ساعة)
            now = timezone.now()
            one_hour_ago = now - timedelta(hours=1)
            
            active_alerts = [
                alert for alert in alerts
                if datetime.fromisoformat(alert.get('timestamp', '')) > one_hour_ago
            ]
            
            return active_alerts
        
        except Exception as e:
            logger.error(f'خطأ في الحصول على التنبيهات: {e}')
            return []
    
    def determine_overall_status(self, status):
        """تحديد الحالة العامة للنظام"""
        try:
            # فحص حالة المكونات الرئيسية
            system_status = status.get('system', {})
            database_status = status.get('database', {})
            performance_status = status.get('performance', {})
            
            # فحص التنبيهات النشطة
            active_alerts = status.get('alerts', [])
            critical_alerts = [alert for alert in active_alerts if alert.get('level') == 'critical']
            
            # تحديد الحالة
            if critical_alerts or database_status.get('status') == 'error':
                return 'critical'
            
            warning_conditions = [
                system_status.get('cpu', {}).get('status') == 'warning',
                system_status.get('memory', {}).get('status') == 'warning',
                system_status.get('disk', {}).get('status') == 'warning',
                performance_status.get('status') == 'warning',
                len(active_alerts) > 0
            ]
            
            if any(warning_conditions):
                return 'warning'
            
            return 'healthy'
        
        except Exception as e:
            logger.error(f'خطأ في تحديد الحالة العامة: {e}')
            return 'unknown'
    
    def check_and_alert(self):
        """فحص النظام وإرسال التنبيهات"""
        if not self.monitoring_enabled:
            return
        
        try:
            status = self.get_system_status()
            alerts = []
            
            # فحص استخدام المعالج
            cpu_usage = status.get('system', {}).get('cpu', {}).get('usage_percent', 0)
            if cpu_usage > self.alert_thresholds['cpu_usage']:
                alerts.append({
                    'type': 'cpu_high',
                    'level': 'warning',
                    'message': f'استخدام المعالج مرتفع: {cpu_usage}%',
                    'value': cpu_usage,
                    'threshold': self.alert_thresholds['cpu_usage'],
                    'timestamp': timezone.now().isoformat()
                })
            
            # فحص استخدام الذاكرة
            memory_usage = status.get('system', {}).get('memory', {}).get('usage_percent', 0)
            if memory_usage > self.alert_thresholds['memory_usage']:
                alerts.append({
                    'type': 'memory_high',
                    'level': 'warning',
                    'message': f'استخدام الذاكرة مرتفع: {memory_usage}%',
                    'value': memory_usage,
                    'threshold': self.alert_thresholds['memory_usage'],
                    'timestamp': timezone.now().isoformat()
                })
            
            # فحص استخدام القرص
            disk_usage = status.get('system', {}).get('disk', {}).get('usage_percent', 0)
            if disk_usage > self.alert_thresholds['disk_usage']:
                alerts.append({
                    'type': 'disk_high',
                    'level': 'critical' if disk_usage > 95 else 'warning',
                    'message': f'استخدام القرص مرتفع: {disk_usage}%',
                    'value': disk_usage,
                    'threshold': self.alert_thresholds['disk_usage'],
                    'timestamp': timezone.now().isoformat()
                })
            
            # فحص قاعدة البيانات
            if not status.get('database', {}).get('connected', True):
                alerts.append({
                    'type': 'database_disconnected',
                    'level': 'critical',
                    'message': 'فقدان الاتصال بقاعدة البيانات',
                    'timestamp': timezone.now().isoformat()
                })
            
            # حفظ التنبيهات
            if alerts:
                self.save_alerts(alerts)
                self.send_alert_notifications(alerts)
            
            return alerts
        
        except Exception as e:
            logger.error(f'خطأ في فحص النظام: {e}')
            return []
    
    def save_alerts(self, alerts):
        """حفظ التنبيهات"""
        try:
            # الحصول على التنبيهات الحالية
            current_alerts = cache.get('active_alerts', [])
            
            # إضافة التنبيهات الجديدة
            current_alerts.extend(alerts)
            
            # الاحتفاظ بآخر 100 تنبيه فقط
            if len(current_alerts) > 100:
                current_alerts = current_alerts[-100:]
            
            # حفظ في التخزين المؤقت
            cache.set('active_alerts', current_alerts, 86400)  # 24 ساعة
            
            # تسجيل في السجلات
            for alert in alerts:
                logger.warning(f"System Alert: {alert['message']}")
        
        except Exception as e:
            logger.error(f'خطأ في حفظ التنبيهات: {e}')
    
    def send_alert_notifications(self, alerts):
        """إرسال إشعارات التنبيهات"""
        if not self.alert_emails:
            return
        
        try:
            critical_alerts = [alert for alert in alerts if alert.get('level') == 'critical']
            warning_alerts = [alert for alert in alerts if alert.get('level') == 'warning']
            
            if critical_alerts or len(warning_alerts) > 3:
                subject = f'تنبيه نظام الموارد البشرية - {len(alerts)} تنبيه'
                
                message = 'تم اكتشاف المشاكل التالية في النظام:\\n\\n'
                
                for alert in alerts:
                    message += f"- {alert['message']} ({alert['level']})\\n"
                
                message += f'\\nالوقت: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\\n'
                message += 'يرجى مراجعة لوحة مراقبة النظام للمزيد من التفاصيل.'
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=self.alert_emails,
                    fail_silently=True
                )
        
        except Exception as e:
            logger.error(f'خطأ في إرسال إشعارات التنبيهات: {e}')
    
    def get_monitoring_history(self, hours=24):
        """الحصول على تاريخ المراقبة"""
        try:
            history = []
            now = timezone.now()
            
            for i in range(hours):
                timestamp = now - timedelta(hours=i)
                cache_key = f'monitoring_snapshot_{timestamp.strftime("%Y%m%d_%H")}'
                snapshot = cache.get(cache_key)
                
                if snapshot:
                    history.append(snapshot)
            
            return sorted(history, key=lambda x: x.get('timestamp', ''))
        
        except Exception as e:
            logger.error(f'خطأ في الحصول على تاريخ المراقبة: {e}')
            return []
    
    def save_monitoring_snapshot(self):
        """حفظ لقطة من حالة المراقبة"""
        try:
            status = self.get_system_status()
            timestamp = timezone.now()
            cache_key = f'monitoring_snapshot_{timestamp.strftime("%Y%m%d_%H")}'
            
            snapshot = {
                'timestamp': timestamp.isoformat(),
                'cpu_usage': status.get('system', {}).get('cpu', {}).get('usage_percent', 0),
                'memory_usage': status.get('system', {}).get('memory', {}).get('usage_percent', 0),
                'disk_usage': status.get('system', {}).get('disk', {}).get('usage_percent', 0),
                'response_time': status.get('performance', {}).get('avg_response_time', 0),
                'database_connected': status.get('database', {}).get('connected', False),
                'overall_status': status.get('overall_status', 'unknown')
            }
            
            cache.set(cache_key, snapshot, 86400 * 7)  # أسبوع واحد
            
        except Exception as e:
            logger.error(f'خطأ في حفظ لقطة المراقبة: {e}')


# إنشاء مثيل الخدمة
monitoring_service = SystemMonitoringService()