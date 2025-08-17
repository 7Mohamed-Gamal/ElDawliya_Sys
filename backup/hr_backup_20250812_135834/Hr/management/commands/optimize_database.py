"""
أمر تحسين قاعدة البيانات
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.conf import settings
from django.apps import apps
from Hr.services.performance_service import performance_service
import time


class Command(BaseCommand):
    help = 'تحسين قاعدة البيانات وتنظيف البيانات القديمة'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze-tables',
            action='store_true',
            help='تحليل جميع الجداول'
        )
        parser.add_argument(
            '--optimize-indexes',
            action='store_true',
            help='تحسين الفهارس'
        )
        parser.add_argument(
            '--clean-old-data',
            action='store_true',
            help='تنظيف البيانات القديمة'
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='تنفيذ VACUUM (PostgreSQL/SQLite)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='تنفيذ جميع عمليات التحسين'
        )
        parser.add_argument(
            '--days-to-keep',
            type=int,
            default=90,
            help='عدد الأيام للاحتفاظ بالبيانات القديمة (افتراضي: 90)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== بدء تحسين قاعدة البيانات ===')
        )

        start_time = time.time()
        results = {}

        # تنفيذ جميع العمليات إذا تم تحديد --all
        if options['all']:
            options['analyze_tables'] = True
            options['optimize_indexes'] = True
            options['clean_old_data'] = True
            options['vacuum'] = True

        # تحليل الجداول
        if options['analyze_tables']:
            self.stdout.write('تحليل الجداول...')
            results['analyze_tables'] = self.analyze_tables()

        # تحسين الفهارس
        if options['optimize_indexes']:
            self.stdout.write('تحسين الفهارس...')
            results['optimize_indexes'] = self.optimize_indexes()

        # تنظيف البيانات القديمة
        if options['clean_old_data']:
            self.stdout.write('تنظيف البيانات القديمة...')
            results['clean_old_data'] = self.clean_old_data(options['days_to_keep'])

        # تنفيذ VACUUM
        if options['vacuum']:
            self.stdout.write('تنفيذ VACUUM...')
            results['vacuum'] = self.vacuum_database()

        # عرض النتائج
        total_time = time.time() - start_time
        self.display_results(results, total_time)

    def analyze_tables(self):
        """تحليل جميع الجداول"""
        try:
            analyzed_tables = []
            
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    # الحصول على جداول HR
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = DATABASE() 
                        AND table_name LIKE 'Hr_%'
                    """)
                    
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        try:
                            cursor.execute(f"ANALYZE TABLE {table_name}")
                            result = cursor.fetchone()
                            analyzed_tables.append({
                                'table': table_name,
                                'status': result[3] if result else 'completed'
                            })
                            self.stdout.write(f"  ✓ تم تحليل {table_name}")
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"  ✗ خطأ في تحليل {table_name}: {e}")
                            )

                elif connection.vendor == 'postgresql':
                    # تحديث إحصائيات PostgreSQL
                    cursor.execute("""
                        SELECT tablename 
                        FROM pg_tables 
                        WHERE schemaname = 'public' 
                        AND tablename LIKE 'Hr_%'
                    """)
                    
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        try:
                            cursor.execute(f"ANALYZE {table_name}")
                            analyzed_tables.append({
                                'table': table_name,
                                'status': 'completed'
                            })
                            self.stdout.write(f"  ✓ تم تحليل {table_name}")
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"  ✗ خطأ في تحليل {table_name}: {e}")
                            )

                elif connection.vendor == 'sqlite':
                    # SQLite ANALYZE
                    cursor.execute("ANALYZE")
                    analyzed_tables.append({
                        'table': 'all_tables',
                        'status': 'completed'
                    })
                    self.stdout.write("  ✓ تم تحليل جميع الجداول")

            return {
                'success': True,
                'analyzed_tables': analyzed_tables,
                'count': len(analyzed_tables)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def optimize_indexes(self):
        """تحسين الفهارس"""
        try:
            optimized_indexes = []
            
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    # تحسين الجداول
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = DATABASE() 
                        AND table_name LIKE 'Hr_%'
                    """)
                    
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        try:
                            cursor.execute(f"OPTIMIZE TABLE {table_name}")
                            result = cursor.fetchone()
                            optimized_indexes.append({
                                'table': table_name,
                                'status': result[3] if result else 'completed'
                            })
                            self.stdout.write(f"  ✓ تم تحسين {table_name}")
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"  ✗ خطأ في تحسين {table_name}: {e}")
                            )

                elif connection.vendor == 'postgresql':
                    # إعادة بناء الفهارس
                    cursor.execute("""
                        SELECT indexname, tablename 
                        FROM pg_indexes 
                        WHERE schemaname = 'public' 
                        AND tablename LIKE 'Hr_%'
                    """)
                    
                    indexes = cursor.fetchall()
                    
                    for index in indexes:
                        index_name, table_name = index
                        try:
                            cursor.execute(f"REINDEX INDEX {index_name}")
                            optimized_indexes.append({
                                'index': index_name,
                                'table': table_name,
                                'status': 'completed'
                            })
                            self.stdout.write(f"  ✓ تم تحسين فهرس {index_name}")
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"  ✗ خطأ في تحسين فهرس {index_name}: {e}")
                            )

                elif connection.vendor == 'sqlite':
                    # إعادة بناء الفهارس في SQLite
                    cursor.execute("REINDEX")
                    optimized_indexes.append({
                        'index': 'all_indexes',
                        'status': 'completed'
                    })
                    self.stdout.write("  ✓ تم تحسين جميع الفهارس")

            return {
                'success': True,
                'optimized_indexes': optimized_indexes,
                'count': len(optimized_indexes)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def clean_old_data(self, days_to_keep):
        """تنظيف البيانات القديمة"""
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            cutoff_date = timezone.now() - timedelta(days=days_to_keep)
            cleaned_data = []
            
            # تنظيف سجلات الحضور القديمة
            try:
                from Hr.models_enhanced import AttendanceRecord
                old_attendance = AttendanceRecord.objects.filter(
                    date__lt=cutoff_date.date()
                )
                count = old_attendance.count()
                if count > 0:
                    old_attendance.delete()
                    cleaned_data.append({
                        'model': 'AttendanceRecord',
                        'deleted_count': count
                    })
                    self.stdout.write(f"  ✓ تم حذف {count} سجل حضور قديم")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ! تعذر تنظيف سجلات الحضور: {e}")
                )

            # تنظيف سجلات الأداء القديمة
            try:
                from Hr.models_enhanced import PerformanceReview
                old_reviews = PerformanceReview.objects.filter(
                    created_at__lt=cutoff_date
                )
                count = old_reviews.count()
                if count > 0:
                    old_reviews.delete()
                    cleaned_data.append({
                        'model': 'PerformanceReview',
                        'deleted_count': count
                    })
                    self.stdout.write(f"  ✓ تم حذف {count} تقييم أداء قديم")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ! تعذر تنظيف تقييمات الأداء: {e}")
                )

            # تنظيف الإشعارات القديمة
            try:
                from notifications.models import Notification
                old_notifications = Notification.objects.filter(
                    created_at__lt=cutoff_date,
                    is_read=True
                )
                count = old_notifications.count()
                if count > 0:
                    old_notifications.delete()
                    cleaned_data.append({
                        'model': 'Notification',
                        'deleted_count': count
                    })
                    self.stdout.write(f"  ✓ تم حذف {count} إشعار قديم")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ! تعذر تنظيف الإشعارات: {e}")
                )

            # تنظيف سجلات التدقيق القديمة
            try:
                from audit.models import AuditLog
                old_audit_logs = AuditLog.objects.filter(
                    timestamp__lt=cutoff_date
                )
                count = old_audit_logs.count()
                if count > 0:
                    old_audit_logs.delete()
                    cleaned_data.append({
                        'model': 'AuditLog',
                        'deleted_count': count
                    })
                    self.stdout.write(f"  ✓ تم حذف {count} سجل تدقيق قديم")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ! تعذر تنظيف سجلات التدقيق: {e}")
                )

            return {
                'success': True,
                'cleaned_data': cleaned_data,
                'total_deleted': sum(item['deleted_count'] for item in cleaned_data)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def vacuum_database(self):
        """تنفيذ VACUUM لتحسين المساحة"""
        try:
            vacuum_results = []
            
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    # VACUUM ANALYZE لجميع الجداول
                    cursor.execute("""
                        SELECT tablename 
                        FROM pg_tables 
                        WHERE schemaname = 'public' 
                        AND tablename LIKE 'Hr_%'
                    """)
                    
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        try:
                            cursor.execute(f"VACUUM ANALYZE {table_name}")
                            vacuum_results.append({
                                'table': table_name,
                                'status': 'completed'
                            })
                            self.stdout.write(f"  ✓ تم تنفيذ VACUUM على {table_name}")
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"  ✗ خطأ في VACUUM {table_name}: {e}")
                            )

                elif connection.vendor == 'sqlite':
                    # VACUUM لـ SQLite
                    cursor.execute("VACUUM")
                    vacuum_results.append({
                        'database': 'sqlite',
                        'status': 'completed'
                    })
                    self.stdout.write("  ✓ تم تنفيذ VACUUM على قاعدة البيانات")

                else:
                    return {
                        'success': False,
                        'error': f'VACUUM غير مدعوم لـ {connection.vendor}'
                    }

            return {
                'success': True,
                'vacuum_results': vacuum_results,
                'count': len(vacuum_results)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def display_results(self, results, total_time):
        """عرض نتائج التحسين"""
        self.stdout.write('\n' + self.style.SUCCESS('=== نتائج التحسين ==='))
        
        success_count = 0
        error_count = 0
        
        for operation, result in results.items():
            if result.get('success'):
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {operation}: نجح")
                )
                
                # عرض تفاصيل إضافية
                if operation == 'analyze_tables':
                    self.stdout.write(f"  - تم تحليل {result['count']} جدول")
                elif operation == 'optimize_indexes':
                    self.stdout.write(f"  - تم تحسين {result['count']} فهرس")
                elif operation == 'clean_old_data':
                    self.stdout.write(f"  - تم حذف {result['total_deleted']} سجل قديم")
                elif operation == 'vacuum':
                    self.stdout.write(f"  - تم تنفيذ VACUUM على {result['count']} جدول")
                    
            else:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"✗ {operation}: فشل - {result.get('error', 'خطأ غير معروف')}")
                )
        
        # ملخص النتائج
        self.stdout.write('\n' + self.style.SUCCESS('=== الملخص ==='))
        self.stdout.write(f"العمليات الناجحة: {success_count}")
        self.stdout.write(f"العمليات الفاشلة: {error_count}")
        self.stdout.write(f"الوقت الإجمالي: {total_time:.2f} ثانية")
        
        if error_count == 0:
            self.stdout.write(
                self.style.SUCCESS('تم تحسين قاعدة البيانات بنجاح!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('تم التحسين مع بعض الأخطاء. راجع الرسائل أعلاه.')
            )