"""
خدمة مراقبة النظام المتقدمة
"""

import os
import time
import logging
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from collections import defaultdict, deque
import threading

# محاولة استيراد psutil مع معالجة الخطأ
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)


class SystemMonitoringService:
    """خدمة مراقبة النظام المتقدمة"""
    
    def __init__(self):
        self.monitoring_enabled = getattr(settings, 'HR_SYSTEM_MONITORING', True)
        self.alert_thresholds = {
            'cpu_usage': getattr(settings, 'HR_CPU_THRESHOLD', 80),
            'memory_usage': getattr(settings, 'HR_MEMORY_THRESHOLD', 85),
            'disk_usage': getattr(settings, 'HR_DISK_THRESHOLD', 90),
            'response_time': getattr(settings, 'HR_RESPONSE_TIME_THRESHOLD', 2.0),
            'error_rate': getattr(settings, 'HR_ERROR_RATE_THRESHOLD', 5.0)
        }
        self.alert_emails = getattr(settings, 'HR_ALERT_EMAILS', [])
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
        
        # بدء مراقبة النظام في خيط منفصل
        if self.monitoring_enabled:
            self.start_monitoring()
    
    def start_monitoring(self):
        """بدء مراقبة النظام"""
        try:
            monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            monitoring_thread.start()
            logger.info("تم بدء مراقبة النظام")
        except Exception as e:
            logger.error(f"خطأ في بدء مراقبة النظام: {e}")
    
    def _monitoring_loop(self):
        """حلقة مراقبة النظام"""
        while self.monitoring_enabled:
            try:
                # جمع مقاييس النظام
                system_metrics = self.collect_system_metrics()
                
                # جمع مقاييس التطبيق
                app_metrics = self.collect_application_metrics()
                
                # جمع مقاييس قاعدة البيانات
                db_metrics = self.collect_database_metrics()
                
                # دمج جميع المقاييس
                all_metrics = {
                    'timestamp': timezone.now().isoformat(),
                    'system': system_metrics,
                    'application': app_metrics,
                    'database': db_metrics
                }
                
                # حفظ المقاييس
                self.save_metrics(all_metrics)
                
                # فحص التنبيهات
                self.check_alerts(all_metrics)
                
                # انتظار قبل الدورة التالية
                time.sleep(60)  # كل دقيقة
                
            except Exception as e:
                logger.error(f"خطأ في حلقة مراقبة النظام: {e}")
                time.sleep(60)
    
    def collect_system_metrics(self):
        """جمع مقاييس النظام"""
        if not PSUTIL_AVAILABLE:
            logger.warning("مكتبة psutil غير متاحة - سيتم استخدام قيم افتراضية")
            return {
                'cpu': {'usage_percent': 0, 'count': 1, 'frequency': None},
                'memory': {'total': 0, 'available': 0, 'used': 0, 'usage_percent': 0, 'swap_total': 0, 'swap_used': 0, 'swap_percent': 0},
                'disk': {'total': 0, 'used': 0, 'free': 0, 'usage_percent': 0, 'read_bytes': 0, 'write_bytes': 0},
                'network': {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0},
                'processes': {'count': 0},
                'temperatures': {}
            }
        
        try:
            # معلومات المعالج
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # معلومات الذاكرة
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # معلومات القرص
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # معلومات الشبكة
            network_io = psutil.net_io_counters()
            
            # معلومات العمليات
            process_count = len(psutil.pids())
            
            # درجة حرارة النظام (إذا كانت متاحة)
            temperatures = {}
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    temperatures = {name: [temp.current for temp in temp_list] 
                                  for name, temp_list in temps.items()}
            except:
                pass
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'usage_percent': memory.percent,
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percent': swap.percent
                },
                'disk': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'usage_percent': (disk_usage.used / disk_usage.total) * 100,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                },
                'processes': {
                    'count': process_count
                },
                'temperatures': temperatures
            }
            
        except Exception as e:
            logger.error(f"خطأ في جمع مقاييس النظام: {e}")
            return {}
    
    def collect_application_metrics(self):
        """جمع مقاييس التطبيق"""
        try:
            # إحصائيات Django
            django_stats = self._get_django_stats()
            
            if not PSUTIL_AVAILABLE:
                return {
                    'process': {
                        'pid': os.getpid(),
                        'memory_rss': 0,
                        'memory_vms': 0,
                        'memory_percent': 0,
                        'cpu_percent': 0,
                        'thread_count': 0,
                        'open_files': 0,
                        'connections': 0,
                        'create_time': 0
                    },
                    'django': django_stats
                }
            
            # معلومات العملية الحالية
            current_process = psutil.Process(os.getpid())
            
            # استخدام الذاكرة للتطبيق
            memory_info = current_process.memory_info()
            memory_percent = current_process.memory_percent()
            
            # استخدام المعالج للتطبيق
            cpu_percent = current_process.cpu_percent()
            
            # عدد الخيوط
            thread_count = current_process.num_threads()
            
            # الملفات المفتوحة
            try:
                open_files = len(current_process.open_files())
            except:
                open_files = 0
            
            # اتصالات الشبكة
            try:
                connections = len(current_process.connections())
            except:
                connections = 0
            
            return {
                'process': {
                    'pid': current_process.pid,
                    'memory_rss': memory_info.rss,
                    'memory_vms': memory_info.vms,
                    'memory_percent': memory_percent,
                    'cpu_percent': cpu_percent,
                    'thread_count': thread_count,
                    'open_files': open_files,
                    'connections': connections,
                    'create_time': current_process.create_time()
                },
                'django': django_stats
            }
            
        except Exception as e:
            logger.error(f"خطأ في جمع مقاييس التطبيق: {e}")
            return {}
    
    def collect_database_metrics(self):
        """جمع مقاييس قاعدة البيانات"""
        try:
            db_metrics = {
                'connection_info': {
                    'vendor': connection.vendor,
                    'database': connection.settings_dict.get('NAME', 'unknown'),
                    'host': connection.settings_dict.get('HOST', 'localhost'),
                    'port': connection.settings_dict.get('PORT', 'default')
                },
                'queries': {
                    'total_queries': len(connection.queries) if hasattr(connection, 'queries') else 0
                }
            }
            
            # إحصائيات خاصة بنوع قاعدة البيانات
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    # إحصائيات MySQL
                    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                    result = cursor.fetchone()
                    if result:
                        db_metrics['connections'] = {'active': int(result[1])}
                    
                    cursor.execute("SHOW STATUS LIKE 'Queries'")
                    result = cursor.fetchone()
                    if result:
                        db_metrics['queries']['total'] = int(result[1])
                    
                    cursor.execute("SHOW STATUS LIKE 'Slow_queries'")
                    result = cursor.fetchone()
                    if result:
                        db_metrics['queries']['slow'] = int(result[1])
                
                elif connection.vendor == 'postgresql':
                    # إحصائيات PostgreSQL
                    cursor.execute("SELECT count(*) FROM pg_stat_activity")
                    result = cursor.fetchone()
                    if result:
                        db_metrics['connections'] = {'active': result[0]}
                    
                    cursor.execute("""
                        SELECT sum(calls) as total_calls, 
                               sum(total_time) as total_time,
                               avg(mean_time) as avg_time
                        FROM pg_stat_statements 
                        WHERE query NOT LIKE '%pg_stat_statements%'
                    """)
                    result = cursor.fetchone()
                    if result and result[0]:
                        db_metrics['queries'].update({
                            'total': int(result[0]),
                            'total_time': float(result[1]) if result[1] else 0,
                            'avg_time': float(result[2]) if result[2] else 0
                        })
            
            return db_metrics
            
        except Exception as e:
            logger.error(f"خطأ في جمع مقاييس قاعدة البيانات: {e}")
            return {}
    
    def _get_django_stats(self):
        """الحصول على إحصائيات Django"""
        try:
            # إحصائيات التخزين المؤقت
            cache_stats = {
                'backend': cache.__class__.__name__
            }
            
            # محاولة الحصول على إحصائيات التخزين المؤقت
            try:
                cache_stats.update({
                    'hits': getattr(cache, '_hits', 0),
                    'misses': getattr(cache, '_misses', 0)
                })
            except:
                pass
            
            # إحصائيات الجلسات
            session_stats = {}
            try:
                from django.contrib.sessions.models import Session
                active_sessions = Session.objects.filter(
                    expire_date__gt=timezone.now()
                ).count()
                session_stats['active_sessions'] = active_sessions
            except:
                pass
            
            return {
                'cache': cache_stats,
                'sessions': session_stats,
                'debug': settings.DEBUG,
                'timezone': str(settings.TIME_ZONE)
            }
            
        except Exception as e:
            logger.error(f"خطأ في جمع إحصائيات Django: {e}")
            return {}
    
    def save_metrics(self, metrics):
        """حفظ المقاييس"""
        try:
            with self.lock:
                # حفظ في الذاكرة للوصول السريع
                timestamp = metrics['timestamp']
                
                for category, data in metrics.items():
                    if category != 'timestamp':
                        self.metrics_history[category].append({
                            'timestamp': timestamp,
                            'data': data
                        })
                
                # حفظ في التخزين المؤقت
                cache_key = f'system_metrics_{timezone.now().strftime("%Y%m%d_%H%M")}'
                cache.set(cache_key, metrics, 3600)  # ساعة واحدة
                
                # حفظ الملخص اليومي
                self._save_daily_summary(metrics)
                
        except Exception as e:
            logger.error(f"خطأ في حفظ المقاييس: {e}")
    
    def _save_daily_summary(self, metrics):
        """حفظ ملخص يومي للمقاييس"""
        try:
            today = timezone.now().date().isoformat()
            summary_key = f'daily_metrics_summary_{today}'
            
            # الحصول على الملخص الحالي
            daily_summary = cache.get(summary_key, {
                'date': today,
                'samples_count': 0,
                'system': {
                    'cpu_avg': 0,
                    'cpu_max': 0,
                    'memory_avg': 0,
                    'memory_max': 0,
                    'disk_avg': 0,
                    'disk_max': 0
                },
                'alerts_count': 0
            })
            
            # تحديث الملخص
            daily_summary['samples_count'] += 1
            
            if 'system' in metrics:
                system_data = metrics['system']
                
                # تحديث متوسطات المعالج
                if 'cpu' in system_data:
                    cpu_usage = system_data['cpu'].get('usage_percent', 0)
                    daily_summary['system']['cpu_avg'] = (
                        (daily_summary['system']['cpu_avg'] * (daily_summary['samples_count'] - 1) + cpu_usage) /
                        daily_summary['samples_count']
                    )
                    daily_summary['system']['cpu_max'] = max(
                        daily_summary['system']['cpu_max'], cpu_usage
                    )
                
                # تحديث متوسطات الذاكرة
                if 'memory' in system_data:
                    memory_usage = system_data['memory'].get('usage_percent', 0)
                    daily_summary['system']['memory_avg'] = (
                        (daily_summary['system']['memory_avg'] * (daily_summary['samples_count'] - 1) + memory_usage) /
                        daily_summary['samples_count']
                    )
                    daily_summary['system']['memory_max'] = max(
                        daily_summary['system']['memory_max'], memory_usage
                    )
                
                # تحديث متوسطات القرص
                if 'disk' in system_data:
                    disk_usage = system_data['disk'].get('usage_percent', 0)
                    daily_summary['system']['disk_avg'] = (
                        (daily_summary['system']['disk_avg'] * (daily_summary['samples_count'] - 1) + disk_usage) /
                        daily_summary['samples_count']
                    )
                    daily_summary['system']['disk_max'] = max(
                        daily_summary['system']['disk_max'], disk_usage
                    )
            
            # حفظ الملخص المحدث
            cache.set(summary_key, daily_summary, 86400)  # 24 ساعة
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الملخص اليومي: {e}")
    
    def check_alerts(self, metrics):
        """فحص التنبيهات"""
        try:
            alerts = []
            
            if 'system' in metrics:
                system_data = metrics['system']
                
                # فحص استخدام المعالج
                if 'cpu' in system_data:
                    cpu_usage = system_data['cpu'].get('usage_percent', 0)
                    if cpu_usage > self.alert_thresholds['cpu_usage']:
                        alerts.append({
                            'type': 'cpu_high',
                            'message': f'استخدام المعالج عالي: {cpu_usage:.1f}%',
                            'value': cpu_usage,
                            'threshold': self.alert_thresholds['cpu_usage'],
                            'severity': 'warning' if cpu_usage < 90 else 'critical'
                        })
                
                # فحص استخدام الذاكرة
                if 'memory' in system_data:
                    memory_usage = system_data['memory'].get('usage_percent', 0)
                    if memory_usage > self.alert_thresholds['memory_usage']:
                        alerts.append({
                            'type': 'memory_high',
                            'message': f'استخدام الذاكرة عالي: {memory_usage:.1f}%',
                            'value': memory_usage,
                            'threshold': self.alert_thresholds['memory_usage'],
                            'severity': 'warning' if memory_usage < 95 else 'critical'
                        })
                
                # فحص استخدام القرص
                if 'disk' in system_data:
                    disk_usage = system_data['disk'].get('usage_percent', 0)
                    if disk_usage > self.alert_thresholds['disk_usage']:
                        alerts.append({
                            'type': 'disk_high',
                            'message': f'استخدام القرص عالي: {disk_usage:.1f}%',
                            'value': disk_usage,
                            'threshold': self.alert_thresholds['disk_usage'],
                            'severity': 'warning' if disk_usage < 95 else 'critical'
                        })
            
            # إرسال التنبيهات
            if alerts:
                self.send_alerts(alerts)
                
        except Exception as e:
            logger.error(f"خطأ في فحص التنبيهات: {e}")
    
    def send_alerts(self, alerts):
        """إرسال التنبيهات"""
        try:
            for alert in alerts:
                # تسجيل التنبيه
                if alert['severity'] == 'critical':
                    logger.critical(alert['message'])
                else:
                    logger.warning(alert['message'])
                
                # حفظ التنبيه في التخزين المؤقت
                self._save_alert(alert)
                
                # إرسال بريد إلكتروني للتنبيهات الحرجة
                if alert['severity'] == 'critical' and self.alert_emails:
                    self._send_email_alert(alert)
                
        except Exception as e:
            logger.error(f"خطأ في إرسال التنبيهات: {e}")
    
    def _save_alert(self, alert):
        """حفظ التنبيه"""
        try:
            alert_data = {
                **alert,
                'timestamp': timezone.now().isoformat(),
                'acknowledged': False
            }
            
            # حفظ في قائمة التنبيهات
            today = timezone.now().date().isoformat()
            alerts_key = f'system_alerts_{today}'
            
            alerts_list = cache.get(alerts_key, [])
            alerts_list.append(alert_data)
            cache.set(alerts_key, alerts_list, 86400)  # 24 ساعة
            
            # تحديث عداد التنبيهات في الملخص اليومي
            summary_key = f'daily_metrics_summary_{today}'
            daily_summary = cache.get(summary_key, {})
            daily_summary['alerts_count'] = daily_summary.get('alerts_count', 0) + 1
            cache.set(summary_key, daily_summary, 86400)
            
        except Exception as e:
            logger.error(f"خطأ في حفظ التنبيه: {e}")
    
    def _send_email_alert(self, alert):
        """إرسال تنبيه عبر البريد الإلكتروني"""
        try:
            subject = f'تنبيه نظام الموارد البشرية - {alert["type"]}'
            message = f"""
            تم اكتشاف مشكلة في النظام:
            
            النوع: {alert['type']}
            الرسالة: {alert['message']}
            القيمة الحالية: {alert['value']}
            الحد المسموح: {alert['threshold']}
            مستوى الخطورة: {alert['severity']}
            الوقت: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            يرجى اتخاذ الإجراء المناسب.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                self.alert_emails,
                fail_silently=True
            )
            
        except Exception as e:
            logger.error(f"خطأ في إرسال تنبيه البريد الإلكتروني: {e}")
    
    def get_current_metrics(self):
        """الحصول على المقاييس الحالية"""
        try:
            return {
                'system': self.collect_system_metrics(),
                'application': self.collect_application_metrics(),
                'database': self.collect_database_metrics(),
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"خطأ في الحصول على المقاييس الحالية: {e}")
            return {}
    
    def get_metrics_history(self, category=None, hours=24):
        """الحصول على تاريخ المقاييس"""
        try:
            with self.lock:
                if category:
                    return list(self.metrics_history.get(category, []))
                else:
                    return {cat: list(data) for cat, data in self.metrics_history.items()}
        except Exception as e:
            logger.error(f"خطأ في الحصول على تاريخ المقاييس: {e}")
            return {}
    
    def get_daily_summary(self, date=None):
        """الحصول على الملخص اليومي"""
        try:
            if date is None:
                date = timezone.now().date().isoformat()
            
            summary_key = f'daily_metrics_summary_{date}'
            return cache.get(summary_key, {})
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الملخص اليومي: {e}")
            return {}
    
    def get_alerts(self, date=None, acknowledged=None):
        """الحصول على التنبيهات"""
        try:
            if date is None:
                date = timezone.now().date().isoformat()
            
            alerts_key = f'system_alerts_{date}'
            alerts = cache.get(alerts_key, [])
            
            if acknowledged is not None:
                alerts = [alert for alert in alerts if alert.get('acknowledged') == acknowledged]
            
            return alerts
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على التنبيهات: {e}")
            return []
    
    def acknowledge_alert(self, alert_id, user_id=None):
        """الإقرار بالتنبيه"""
        try:
            # البحث عن التنبيه وتحديثه
            # هذا مثال بسيط - يحتاج تنفيذ أكثر تفصيلاً
            today = timezone.now().date().isoformat()
            alerts_key = f'system_alerts_{today}'
            alerts = cache.get(alerts_key, [])
            
            for alert in alerts:
                if alert.get('id') == alert_id:
                    alert['acknowledged'] = True
                    alert['acknowledged_by'] = user_id
                    alert['acknowledged_at'] = timezone.now().isoformat()
                    break
            
            cache.set(alerts_key, alerts, 86400)
            return True
            
        except Exception as e:
            logger.error(f"خطأ في الإقرار بالتنبيه: {e}")
            return False
    
    def get_system_health_score(self):
        """حساب نقاط صحة النظام"""
        try:
            current_metrics = self.get_current_metrics()
            
            if not current_metrics:
                return 0
            
            score = 100
            
            # خصم نقاط بناءً على استخدام الموارد
            if 'system' in current_metrics:
                system_data = current_metrics['system']
                
                # المعالج
                if 'cpu' in system_data:
                    cpu_usage = system_data['cpu'].get('usage_percent', 0)
                    if cpu_usage > 80:
                        score -= (cpu_usage - 80) * 2
                
                # الذاكرة
                if 'memory' in system_data:
                    memory_usage = system_data['memory'].get('usage_percent', 0)
                    if memory_usage > 80:
                        score -= (memory_usage - 80) * 2
                
                # القرص
                if 'disk' in system_data:
                    disk_usage = system_data['disk'].get('usage_percent', 0)
                    if disk_usage > 80:
                        score -= (disk_usage - 80) * 1.5
            
            # خصم نقاط للتنبيهات النشطة
            active_alerts = self.get_alerts(acknowledged=False)
            critical_alerts = len([a for a in active_alerts if a.get('severity') == 'critical'])
            warning_alerts = len([a for a in active_alerts if a.get('severity') == 'warning'])
            
            score -= critical_alerts * 20
            score -= warning_alerts * 10
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"خطأ في حساب نقاط صحة النظام: {e}")
            return 0


# إنشاء مثيل الخدمة
monitoring_service = SystemMonitoringService()