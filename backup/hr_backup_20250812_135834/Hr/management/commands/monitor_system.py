"""
أمر مراقبة النظام
"""

from django.core.management.base import BaseCommand
from Hr.services.monitoring_service import monitoring_service
import time
import signal
import sys


class Command(BaseCommand):
    help = 'مراقبة النظام وإرسال التنبيهات'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='فترة الفحص بالثواني (افتراضي: 300 = 5 دقائق)'
        )
        
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='تشغيل كخدمة في الخلفية'
        )
        
        parser.add_argument(
            '--once',
            action='store_true',
            help='تشغيل فحص واحد فقط'
        )
        
        parser.add_argument(
            '--status',
            action='store_true',
            help='عرض حالة النظام الحالية'
        )
        
        parser.add_argument(
            '--alerts',
            action='store_true',
            help='عرض التنبيهات النشطة'
        )
        
        parser.add_argument(
            '--history',
            type=int,
            help='عرض تاريخ المراقبة لعدد الساعات المحدد'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        daemon = options['daemon']
        once = options['once']
        status = options['status']
        alerts = options['alerts']
        history = options['history']
        
        if status:
            self.show_system_status()
        elif alerts:
            self.show_active_alerts()
        elif history:
            self.show_monitoring_history(history)
        elif once:
            self.run_single_check()
        else:
            self.run_monitoring_loop(interval, daemon)

    def show_system_status(self):
        """عرض حالة النظام الحالية"""
        self.stdout.write(self.style.SUCCESS('=== حالة النظام الحالية ==='))
        
        try:
            status = monitoring_service.get_system_status()
            
            # الحالة العامة
            overall_status = status.get('overall_status', 'unknown')
            status_style = self.get_status_style(overall_status)
            self.stdout.write(f'الحالة العامة: {status_style(overall_status.upper())}')
            self.stdout.write(f'الوقت: {status.get("timestamp", "غير معروف")}')
            
            # معلومات النظام
            system_info = status.get('system', {})
            if system_info:
                self.stdout.write('\\n--- معلومات النظام ---')
                
                cpu_info = system_info.get('cpu', {})
                self.stdout.write(f'المعالج: {cpu_info.get("usage_percent", 0)}% ({cpu_info.get("count", 0)} cores)')
                
                memory_info = system_info.get('memory', {})
                self.stdout.write(
                    f'الذاكرة: {memory_info.get("usage_percent", 0)}% '
                    f'({memory_info.get("available_gb", 0):.1f}GB متاحة من {memory_info.get("total_gb", 0):.1f}GB)'
                )
                
                disk_info = system_info.get('disk', {})
                self.stdout.write(
                    f'القرص: {disk_info.get("usage_percent", 0)}% '
                    f'({disk_info.get("free_gb", 0):.1f}GB متاحة من {disk_info.get("total_gb", 0):.1f}GB)'
                )
            
            # معلومات قاعدة البيانات
            db_info = status.get('database', {})
            if db_info:
                self.stdout.write('\\n--- قاعدة البيانات ---')
                db_status = 'متصلة' if db_info.get('connected', False) else 'غير متصلة'
                self.stdout.write(f'الحالة: {db_status}')
                self.stdout.write(f'النوع: {db_info.get("vendor", "غير معروف")}')
                self.stdout.write(f'عدد الاستعلامات: {db_info.get("query_count", 0)}')
            
            # معلومات التطبيق
            app_info = status.get('application', {})
            if app_info:
                self.stdout.write('\\n--- التطبيق ---')
                uptime = app_info.get('uptime', {})
                self.stdout.write(f'وقت التشغيل: {uptime.get("uptime_formatted", "غير معروف")}')
                
                user_stats = app_info.get('users', {})
                self.stdout.write(f'المستخدمون: {user_stats.get("online_users", 0)} متصل من {user_stats.get("total_users", 0)} إجمالي')
            
            # الأداء
            performance_info = status.get('performance', {})
            if performance_info:
                self.stdout.write('\\n--- الأداء ---')
                self.stdout.write(f'متوسط وقت الاستجابة: {performance_info.get("avg_response_time", 0):.3f}s')
                self.stdout.write(f'الاستعلامات البطيئة: {performance_info.get("slow_queries", 0)}')
                self.stdout.write(f'الطلبات البطيئة: {performance_info.get("slow_requests", 0)}')
            
            # التنبيهات النشطة
            alerts = status.get('alerts', [])
            if alerts:
                self.stdout.write('\\n--- التنبيهات النشطة ---')
                for alert in alerts:
                    level_style = self.get_alert_level_style(alert.get('level', 'info'))
                    self.stdout.write(f'  {level_style(alert.get("level", "").upper())}: {alert.get("message", "")}')
            else:
                self.stdout.write('\\n--- لا توجد تنبيهات نشطة ---')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ في عرض حالة النظام: {e}'))

    def show_active_alerts(self):
        """عرض التنبيهات النشطة"""
        self.stdout.write(self.style.SUCCESS('=== التنبيهات النشطة ==='))
        
        try:
            alerts = monitoring_service.get_active_alerts()
            
            if not alerts:
                self.stdout.write(self.style.SUCCESS('لا توجد تنبيهات نشطة'))
                return
            
            for i, alert in enumerate(alerts, 1):
                level_style = self.get_alert_level_style(alert.get('level', 'info'))
                self.stdout.write(f'\\n{i}. {level_style(alert.get("level", "").upper())}')
                self.stdout.write(f'   الرسالة: {alert.get("message", "")}')
                self.stdout.write(f'   النوع: {alert.get("type", "")}')
                self.stdout.write(f'   الوقت: {alert.get("timestamp", "")}')
                
                if 'value' in alert and 'threshold' in alert:
                    self.stdout.write(f'   القيمة: {alert["value"]} (العتبة: {alert["threshold"]})')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ في عرض التنبيهات: {e}'))

    def show_monitoring_history(self, hours):
        """عرض تاريخ المراقبة"""
        self.stdout.write(self.style.SUCCESS(f'=== تاريخ المراقبة لآخر {hours} ساعة ==='))
        
        try:
            history = monitoring_service.get_monitoring_history(hours)
            
            if not history:
                self.stdout.write('لا توجد بيانات تاريخية متاحة')
                return
            
            self.stdout.write(f'{"الوقت":<20} {"الحالة":<10} {"المعالج":<8} {"الذاكرة":<8} {"القرص":<8} {"الاستجابة":<10}')
            self.stdout.write('-' * 70)
            
            for snapshot in history:
                timestamp = snapshot.get('timestamp', '')[:16]  # YYYY-MM-DD HH:MM
                status = snapshot.get('overall_status', 'unknown')
                cpu = f"{snapshot.get('cpu_usage', 0):.1f}%"
                memory = f"{snapshot.get('memory_usage', 0):.1f}%"
                disk = f"{snapshot.get('disk_usage', 0):.1f}%"
                response = f"{snapshot.get('response_time', 0):.3f}s"
                
                self.stdout.write(f'{timestamp:<20} {status:<10} {cpu:<8} {memory:<8} {disk:<8} {response:<10}')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ في عرض التاريخ: {e}'))

    def run_single_check(self):
        """تشغيل فحص واحد"""
        self.stdout.write('تشغيل فحص النظام...')
        
        try:
            alerts = monitoring_service.check_and_alert()
            monitoring_service.save_monitoring_snapshot()
            
            if alerts:
                self.stdout.write(self.style.WARNING(f'تم اكتشاف {len(alerts)} تنبيه:'))
                for alert in alerts:
                    level_style = self.get_alert_level_style(alert.get('level', 'info'))
                    self.stdout.write(f'  {level_style(alert.get("level", "").upper())}: {alert.get("message", "")}')
            else:
                self.stdout.write(self.style.SUCCESS('النظام يعمل بشكل طبيعي'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ في فحص النظام: {e}'))

    def run_monitoring_loop(self, interval, daemon):
        """تشغيل حلقة المراقبة"""
        if daemon:
            self.stdout.write(f'بدء مراقبة النظام كخدمة (فحص كل {interval} ثانية)')
            self.stdout.write('اضغط Ctrl+C للإيقاف')
        else:
            self.stdout.write(f'بدء مراقبة النظام (فحص كل {interval} ثانية)')
            self.stdout.write('اضغط Ctrl+C للإيقاف')
        
        # إعداد معالج الإشارة للإيقاف الآمن
        def signal_handler(sig, frame):
            self.stdout.write('\\nإيقاف مراقبة النظام...')
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            while True:
                try:
                    # تشغيل الفحص
                    alerts = monitoring_service.check_and_alert()
                    monitoring_service.save_monitoring_snapshot()
                    
                    # عرض النتائج
                    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    if alerts:
                        self.stdout.write(
                            f'[{current_time}] تم اكتشاف {len(alerts)} تنبيه'
                        )
                        if not daemon:  # عرض التفاصيل فقط في الوضع التفاعلي
                            for alert in alerts:
                                level_style = self.get_alert_level_style(alert.get('level', 'info'))
                                self.stdout.write(f'  {level_style(alert.get("level", "").upper())}: {alert.get("message", "")}')
                    else:
                        if not daemon:
                            self.stdout.write(f'[{current_time}] النظام يعمل بشكل طبيعي')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'خطأ في فحص النظام: {e}'))
                
                # انتظار الفترة المحددة
                time.sleep(interval)
        
        except KeyboardInterrupt:
            self.stdout.write('\\nتم إيقاف مراقبة النظام')

    def get_status_style(self, status):
        """الحصول على نمط العرض حسب الحالة"""
        if status == 'healthy':
            return self.style.SUCCESS
        elif status == 'warning':
            return self.style.WARNING
        elif status == 'critical':
            return self.style.ERROR
        else:
            return self.style.NOTICE

    def get_alert_level_style(self, level):
        """الحصول على نمط العرض حسب مستوى التنبيه"""
        if level == 'critical':
            return self.style.ERROR
        elif level == 'warning':
            return self.style.WARNING
        elif level == 'info':
            return self.style.SUCCESS
        else:
            return self.style.NOTICE