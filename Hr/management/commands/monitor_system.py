"""
أمر مراقبة النظام
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from Hr.services.monitoring_service import monitoring_service
import time
import json


class Command(BaseCommand):
    help = 'مراقبة النظام وعرض المقاييس والتنبيهات'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['current', 'history', 'alerts', 'summary', 'health', 'watch'],
            default='current',
            help='نوع المراقبة'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='فترة التحديث بالثواني (للوضع watch)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='عدد الساعات للتاريخ'
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='عرض النتائج بصيغة JSON'
        )
        parser.add_argument(
            '--category',
            type=str,
            choices=['system', 'application', 'database'],
            help='فئة المقاييس'
        )

    def handle(self, *args, **options):
        mode = options['mode']
        
        if mode == 'current':
            self.show_current_metrics(options)
        elif mode == 'history':
            self.show_metrics_history(options)
        elif mode == 'alerts':
            self.show_alerts(options)
        elif mode == 'summary':
            self.show_daily_summary(options)
        elif mode == 'health':
            self.show_health_score(options)
        elif mode == 'watch':
            self.watch_metrics(options)

    def show_current_metrics(self, options):
        """عرض المقاييس الحالية"""
        self.stdout.write(
            self.style.SUCCESS('=== المقاييس الحالية ===')
        )
        
        try:
            metrics = monitoring_service.get_current_metrics()
            
            if options['json']:
                self.stdout.write(json.dumps(metrics, indent=2, ensure_ascii=False))
                return
            
            if not metrics:
                self.stdout.write(self.style.ERROR('لا توجد مقاييس متاحة'))
                return
            
            # عرض مقاييس النظام
            if 'system' in metrics and (not options['category'] or options['category'] == 'system'):
                self.display_system_metrics(metrics['system'])
            
            # عرض مقاييس التطبيق
            if 'application' in metrics and (not options['category'] or options['category'] == 'application'):
                self.display_application_metrics(metrics['application'])
            
            # عرض مقاييس قاعدة البيانات
            if 'database' in metrics and (not options['category'] or options['category'] == 'database'):
                self.display_database_metrics(metrics['database'])
            
            self.stdout.write(f"\nآخر تحديث: {metrics.get('timestamp', 'غير معروف')}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ في عرض المقاييس: {e}'))

    def display_system_metrics(self, system_data):
        """عرض مقاييس النظام"""
        self.stdout.write('\n' + self.style.SUCCESS('--- مقاييس النظام ---'))
        
        # المعالج
        if 'cpu' in system_data:
            cpu = system_data['cpu']
            cpu_usage = cpu.get('usage_percent', 0)
            cpu_color = self.get_usage_color(cpu_usage, 80, 90)
            
            self.stdout.write(f"المعالج:")
            self.stdout.write(f"  الاستخدام: {cpu_color(f'{cpu_usage:.1f}%')}")
            self.stdout.write(f"  عدد النوى: {cpu.get('count', 'غير معروف')}")
            if cpu.get('frequency'):
                self.stdout.write(f"  التردد: {cpu['frequency']:.0f} MHz")
        
        # الذاكرة
        if 'memory' in system_data:
            memory = system_data['memory']
            memory_usage = memory.get('usage_percent', 0)
            memory_color = self.get_usage_color(memory_usage, 85, 95)
            
            self.stdout.write(f"\nالذاكرة:")
            self.stdout.write(f"  الاستخدام: {memory_color(f'{memory_usage:.1f}%')}")
            self.stdout.write(f"  المستخدم: {self.format_bytes(memory.get('used', 0))}")
            self.stdout.write(f"  المتاح: {self.format_bytes(memory.get('available', 0))}")
            self.stdout.write(f"  الإجمالي: {self.format_bytes(memory.get('total', 0))}")
            
            if memory.get('swap_total', 0) > 0:
                swap_usage = memory.get('swap_percent', 0)
                swap_color = self.get_usage_color(swap_usage, 50, 80)
                self.stdout.write(f"  Swap: {swap_color(f'{swap_usage:.1f}%')}")
        
        # القرص
        if 'disk' in system_data:
            disk = system_data['disk']
            disk_usage = disk.get('usage_percent', 0)
            disk_color = self.get_usage_color(disk_usage, 90, 95)
            
            self.stdout.write(f"\nالقرص:")
            self.stdout.write(f"  الاستخدام: {disk_color(f'{disk_usage:.1f}%')}")
            self.stdout.write(f"  المستخدم: {self.format_bytes(disk.get('used', 0))}")
            self.stdout.write(f"  المتاح: {self.format_bytes(disk.get('free', 0))}")
            self.stdout.write(f"  الإجمالي: {self.format_bytes(disk.get('total', 0))}")
        
        # الشبكة
        if 'network' in system_data:
            network = system_data['network']
            self.stdout.write(f"\nالشبكة:")
            self.stdout.write(f"  البيانات المرسلة: {self.format_bytes(network.get('bytes_sent', 0))}")
            self.stdout.write(f"  البيانات المستقبلة: {self.format_bytes(network.get('bytes_recv', 0))}")
            self.stdout.write(f"  الحزم المرسلة: {network.get('packets_sent', 0):,}")
            self.stdout.write(f"  الحزم المستقبلة: {network.get('packets_recv', 0):,}")
        
        # العمليات
        if 'processes' in system_data:
            processes = system_data['processes']
            self.stdout.write(f"\nالعمليات:")
            self.stdout.write(f"  عدد العمليات: {processes.get('count', 0)}")

    def display_application_metrics(self, app_data):
        """عرض مقاييس التطبيق"""
        self.stdout.write('\n' + self.style.SUCCESS('--- مقاييس التطبيق ---'))
        
        # معلومات العملية
        if 'process' in app_data:
            process = app_data['process']
            memory_percent = process.get('memory_percent', 0)
            cpu_percent = process.get('cpu_percent', 0)
            
            memory_color = self.get_usage_color(memory_percent, 10, 20)
            cpu_color = self.get_usage_color(cpu_percent, 50, 80)
            
            self.stdout.write(f"العملية (PID: {process.get('pid', 'غير معروف')}):")
            self.stdout.write(f"  استخدام الذاكرة: {memory_color(f'{memory_percent:.1f}%')}")
            self.stdout.write(f"  استخدام المعالج: {cpu_color(f'{cpu_percent:.1f}%')}")
            self.stdout.write(f"  الذاكرة المستخدمة: {self.format_bytes(process.get('memory_rss', 0))}")
            self.stdout.write(f"  عدد الخيوط: {process.get('thread_count', 0)}")
            self.stdout.write(f"  الملفات المفتوحة: {process.get('open_files', 0)}")
            self.stdout.write(f"  الاتصالات: {process.get('connections', 0)}")
        
        # معلومات Django
        if 'django' in app_data:
            django = app_data['django']
            self.stdout.write(f"\nDjango:")
            self.stdout.write(f"  وضع التطوير: {'نعم' if django.get('debug') else 'لا'}")
            self.stdout.write(f"  المنطقة الزمنية: {django.get('timezone', 'غير معروف')}")
            
            if 'cache' in django:
                cache_info = django['cache']
                self.stdout.write(f"  التخزين المؤقت: {cache_info.get('backend', 'غير معروف')}")
                
                hits = cache_info.get('hits', 0)
                misses = cache_info.get('misses', 0)
                if hits + misses > 0:
                    hit_rate = (hits / (hits + misses)) * 100
                    hit_color = self.get_usage_color(100 - hit_rate, 20, 50)  # عكسي للمعدل
                    self.stdout.write(f"  معدل الإصابة: {hit_color(f'{hit_rate:.1f}%')}")
            
            if 'sessions' in django:
                sessions = django['sessions']
                self.stdout.write(f"  الجلسات النشطة: {sessions.get('active_sessions', 0)}")

    def display_database_metrics(self, db_data):
        """عرض مقاييس قاعدة البيانات"""
        self.stdout.write('\n' + self.style.SUCCESS('--- مقاييس قاعدة البيانات ---'))
        
        # معلومات الاتصال
        if 'connection_info' in db_data:
            conn = db_data['connection_info']
            self.stdout.write(f"نوع قاعدة البيانات: {conn.get('vendor', 'غير معروف')}")
            self.stdout.write(f"اسم قاعدة البيانات: {conn.get('database', 'غير معروف')}")
            self.stdout.write(f"الخادم: {conn.get('host', 'localhost')}:{conn.get('port', 'default')}")
        
        # الاتصالات
        if 'connections' in db_data:
            connections = db_data['connections']
            self.stdout.write(f"الاتصالات النشطة: {connections.get('active', 0)}")
        
        # الاستعلامات
        if 'queries' in db_data:
            queries = db_data['queries']
            self.stdout.write(f"إجمالي الاستعلامات: {queries.get('total', 0):,}")
            
            if 'slow' in queries:
                slow_queries = queries['slow']
                slow_color = self.style.ERROR if slow_queries > 10 else self.style.WARNING if slow_queries > 0 else self.style.SUCCESS
                self.stdout.write(f"الاستعلامات البطيئة: {slow_color(str(slow_queries))}")
            
            if 'avg_time' in queries:
                avg_time = queries['avg_time']
                time_color = self.style.ERROR if avg_time > 1000 else self.style.WARNING if avg_time > 100 else self.style.SUCCESS
                self.stdout.write(f"متوسط وقت الاستعلام: {time_color(f'{avg_time:.2f}ms')}")

    def show_alerts(self, options):
        """عرض التنبيهات"""
        self.stdout.write(
            self.style.SUCCESS('=== التنبيهات ===')
        )
        
        try:
            alerts = monitoring_service.get_alerts()
            
            if options['json']:
                self.stdout.write(json.dumps(alerts, indent=2, ensure_ascii=False))
                return
            
            if not alerts:
                self.stdout.write(self.style.SUCCESS('لا توجد تنبيهات'))
                return
            
            # تصنيف التنبيهات
            critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
            warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
            
            # عرض التنبيهات الحرجة
            if critical_alerts:
                self.stdout.write('\n' + self.style.ERROR('--- تنبيهات حرجة ---'))
                for alert in critical_alerts:
                    self.display_alert(alert, self.style.ERROR)
            
            # عرض التنبيهات التحذيرية
            if warning_alerts:
                self.stdout.write('\n' + self.style.WARNING('--- تنبيهات تحذيرية ---'))
                for alert in warning_alerts:
                    self.display_alert(alert, self.style.WARNING)
            
            self.stdout.write(f'\nإجمالي التنبيهات: {len(alerts)}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ في عرض التنبيهات: {e}'))

    def display_alert(self, alert, style_func):
        """عرض تنبيه واحد"""
        acknowledged = '✓' if alert.get('acknowledged') else '✗'
        self.stdout.write(
            f"{style_func(alert.get('type', 'unknown'))}: {alert.get('message', 'لا توجد رسالة')} "
            f"[{acknowledged}] ({alert.get('timestamp', 'غير معروف')})"
        )

    def show_health_score(self, options):
        """عرض نقاط صحة النظام"""
        self.stdout.write(
            self.style.SUCCESS('=== نقاط صحة النظام ===')
        )
        
        try:
            health_score = monitoring_service.get_system_health_score()
            
            if options['json']:
                self.stdout.write(json.dumps({'health_score': health_score}, indent=2))
                return
            
            # تحديد لون النقاط
            if health_score >= 90:
                score_color = self.style.SUCCESS
                status = 'ممتاز'
            elif health_score >= 70:
                score_color = self.style.WARNING
                status = 'جيد'
            elif health_score >= 50:
                score_color = self.style.ERROR
                status = 'متوسط'
            else:
                score_color = self.style.ERROR
                status = 'ضعيف'
            
            self.stdout.write(f"نقاط الصحة: {score_color(f'{health_score:.1f}/100')}")
            self.stdout.write(f"الحالة: {score_color(status)}")
            
            # عرض شريط تقدم بسيط
            bar_length = 50
            filled_length = int(bar_length * health_score / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            self.stdout.write(f"[{score_color(bar)}]")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ في عرض نقاط الصحة: {e}'))

    def show_daily_summary(self, options):
        """عرض الملخص اليومي"""
        self.stdout.write(
            self.style.SUCCESS('=== الملخص اليومي ===')
        )
        
        try:
            summary = monitoring_service.get_daily_summary()
            
            if options['json']:
                self.stdout.write(json.dumps(summary, indent=2, ensure_ascii=False))
                return
            
            if not summary:
                self.stdout.write('لا يوجد ملخص متاح')
                return
            
            self.stdout.write(f"التاريخ: {summary.get('date', 'غير معروف')}")
            self.stdout.write(f"عدد العينات: {summary.get('samples_count', 0)}")
            
            if 'system' in summary:
                system = summary['system']
                self.stdout.write('\nمتوسطات النظام:')
                self.stdout.write(f"  المعالج: {system.get('cpu_avg', 0):.1f}% (الحد الأقصى: {system.get('cpu_max', 0):.1f}%)")
                self.stdout.write(f"  الذاكرة: {system.get('memory_avg', 0):.1f}% (الحد الأقصى: {system.get('memory_max', 0):.1f}%)")
                self.stdout.write(f"  القرص: {system.get('disk_avg', 0):.1f}% (الحد الأقصى: {system.get('disk_max', 0):.1f}%)")
            
            alerts_count = summary.get('alerts_count', 0)
            alerts_color = self.style.ERROR if alerts_count > 10 else self.style.WARNING if alerts_count > 0 else self.style.SUCCESS
            self.stdout.write(f"\nعدد التنبيهات: {alerts_color(str(alerts_count))}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ في عرض الملخص اليومي: {e}'))

    def watch_metrics(self, options):
        """مراقبة المقاييس المباشرة"""
        self.stdout.write(
            self.style.SUCCESS('=== مراقبة مباشرة ===')
        )
        self.stdout.write('اضغط Ctrl+C للإيقاف\n')
        
        try:
            while True:
                # مسح الشاشة (يعمل في معظم الأنظمة)
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                
                self.stdout.write(
                    self.style.SUCCESS(f'=== مراقبة مباشرة - {timezone.now().strftime("%H:%M:%S")} ===')
                )
                
                # عرض المقاييس الحالية
                self.show_current_metrics(options)
                
                # عرض نقاط الصحة
                health_score = monitoring_service.get_system_health_score()
                if health_score >= 90:
                    health_color = self.style.SUCCESS
                elif health_score >= 70:
                    health_color = self.style.WARNING
                else:
                    health_color = self.style.ERROR
                
                self.stdout.write(f'\nصحة النظام: {health_color(f"{health_score:.1f}/100")}')
                
                # انتظار
                time.sleep(options['interval'])
                
        except KeyboardInterrupt:
            self.stdout.write('\n' + self.style.SUCCESS('تم إيقاف المراقبة'))

    def get_usage_color(self, usage, warning_threshold, critical_threshold):
        """الحصول على لون الاستخدام"""
        if usage >= critical_threshold:
            return self.style.ERROR
        elif usage >= warning_threshold:
            return self.style.WARNING
        else:
            return self.style.SUCCESS

    def format_bytes(self, bytes_value):
        """تنسيق البايتات"""
        if bytes_value == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while bytes_value >= 1024 and unit_index < len(units) - 1:
            bytes_value /= 1024
            unit_index += 1
        
        return f"{bytes_value:.1f} {units[unit_index]}"