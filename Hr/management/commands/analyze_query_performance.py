"""
أمر تحليل أداء الاستعلامات
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from django.apps import apps
from django.db.models import Count
from Hr.services.query_optimizer import query_optimizer
import time
import json


class Command(BaseCommand):
    help = 'تحليل أداء الاستعلامات وتقديم توصيات للتحسين'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='تحليل نموذج محدد (مثل: Employee, Department)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='عرض تفاصيل إضافية'
        )
        parser.add_argument(
            '--export',
            type=str,
            help='تصدير النتائج إلى ملف JSON'
        )
        parser.add_argument(
            '--test-queries',
            action='store_true',
            help='تشغيل اختبارات الأداء'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== تحليل أداء الاستعلامات ===')
        )

        analysis_results = {
            'database_info': self.get_database_info(),
            'performance_stats': self.get_performance_stats(),
            'model_analysis': {},
            'recommendations': []
        }

        # تحليل نموذج محدد أو جميع النماذج
        if options['model']:
            model_name = options['model']
            analysis_results['model_analysis'][model_name] = self.analyze_model(model_name, options['verbose'])
        else:
            hr_models = ['Employee', 'Department', 'JobPosition', 'Company', 'Branch']
            for model_name in hr_models:
                analysis_results['model_analysis'][model_name] = self.analyze_model(model_name, options['verbose'])

        # تشغيل اختبارات الأداء
        if options['test_queries']:
            analysis_results['performance_tests'] = self.run_performance_tests()

        # إنتاج التوصيات
        analysis_results['recommendations'] = self.generate_recommendations(analysis_results)

        # عرض النتائج
        self.display_results(analysis_results, options['verbose'])

        # تصدير النتائج
        if options['export']:
            self.export_results(analysis_results, options['export'])

    def get_database_info(self):
        """الحصول على معلومات قاعدة البيانات"""
        try:
            db_info = {
                'vendor': connection.vendor,
                'database_name': connection.settings_dict.get('NAME', 'Unknown'),
                'host': connection.settings_dict.get('HOST', 'localhost'),
                'port': connection.settings_dict.get('PORT', 'default'),
                'engine': connection.settings_dict.get('ENGINE', 'Unknown')
            }
            
            # معلومات إضافية حسب نوع قاعدة البيانات
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    cursor.execute("SELECT VERSION()")
                    db_info['version'] = cursor.fetchone()[0]
                    
                    cursor.execute("SHOW VARIABLES LIKE 'innodb_buffer_pool_size'")
                    result = cursor.fetchone()
                    if result:
                        db_info['buffer_pool_size'] = result[1]
                        
                elif connection.vendor == 'postgresql':
                    cursor.execute("SELECT version()")
                    db_info['version'] = cursor.fetchone()[0]
                    
                    cursor.execute("SHOW shared_buffers")
                    result = cursor.fetchone()
                    if result:
                        db_info['shared_buffers'] = result[0]
                        
                elif connection.vendor == 'sqlite':
                    cursor.execute("SELECT sqlite_version()")
                    db_info['version'] = cursor.fetchone()[0]
            
            return db_info
            
        except Exception as e:
            return {'error': f'خطأ في الحصول على معلومات قاعدة البيانات: {e}'}

    def get_performance_stats(self):
        """الحصول على إحصائيات الأداء"""
        try:
            return query_optimizer.get_query_performance_stats()
        except Exception as e:
            return {'error': f'خطأ في الحصول على إحصائيات الأداء: {e}'}

    def analyze_model(self, model_name, verbose=False):
        """تحليل أداء نموذج محدد"""
        try:
            # الحصول على النموذج
            model_class = apps.get_model('Hr', model_name)
            
            analysis = {
                'model_name': model_name,
                'table_name': model_class._meta.db_table,
                'total_records': 0,
                'fields_analysis': {},
                'indexes_analysis': {},
                'query_patterns': {},
                'recommendations': []
            }
            
            # عدد السجلات
            start_time = time.time()
            analysis['total_records'] = model_class.objects.count()
            count_time = time.time() - start_time
            
            if count_time > 1.0:
                analysis['recommendations'].append(
                    f'استعلام العد بطيء ({count_time:.2f}s) - قد تحتاج لفهرسة إضافية'
                )
            
            # تحليل الحقول
            for field in model_class._meta.fields:
                field_analysis = {
                    'name': field.name,
                    'type': field.__class__.__name__,
                    'db_column': field.db_column or field.name,
                    'indexed': field.db_index,
                    'unique': field.unique,
                    'null': field.null
                }
                
                # تحليل إضافي للحقول المهمة
                if field.name in ['id', 'created_at', 'updated_at']:
                    field_analysis['importance'] = 'high'
                elif field.db_index or field.unique:
                    field_analysis['importance'] = 'medium'
                else:
                    field_analysis['importance'] = 'low'
                
                analysis['fields_analysis'][field.name] = field_analysis
            
            # تحليل العلاقات
            relations_analysis = {}
            for field in model_class._meta.fields:
                if field.related_model:
                    relations_analysis[field.name] = {
                        'related_model': field.related_model.__name__,
                        'relation_type': field.__class__.__name__,
                        'on_delete': getattr(field, 'on_delete', None).__name__ if hasattr(field, 'on_delete') else None
                    }
            
            analysis['relations_analysis'] = relations_analysis
            
            # اختبار استعلامات شائعة
            if verbose:
                analysis['common_queries_performance'] = self.test_common_queries(model_class)
            
            return analysis
            
        except Exception as e:
            return {'error': f'خطأ في تحليل النموذج {model_name}: {e}'}

    def test_common_queries(self, model_class):
        """اختبار أداء الاستعلامات الشائعة"""
        queries_performance = {}
        
        try:
            # اختبار الاستعلامات الأساسية
            test_queries = [
                ('all_records', lambda: list(model_class.objects.all())),
                ('first_10', lambda: list(model_class.objects.all()[:10])),
                ('count', lambda: model_class.objects.count()),
                ('exists', lambda: model_class.objects.exists()),
            ]
            
            # إضافة اختبارات خاصة بالنموذج
            if hasattr(model_class, 'is_active'):
                test_queries.append(
                    ('active_only', lambda: list(model_class.objects.filter(is_active=True)))
                )
            
            if hasattr(model_class, 'created_at'):
                from django.utils import timezone
                from datetime import timedelta
                
                test_queries.append(
                    ('recent_records', lambda: list(
                        model_class.objects.filter(
                            created_at__gte=timezone.now() - timedelta(days=30)
                        )
                    ))
                )
            
            # تشغيل الاختبارات
            for query_name, query_func in test_queries:
                try:
                    queries_before = len(connection.queries)
                    start_time = time.time()
                    
                    result = query_func()
                    
                    execution_time = time.time() - start_time
                    queries_after = len(connection.queries)
                    query_count = queries_after - queries_before
                    
                    queries_performance[query_name] = {
                        'execution_time': execution_time,
                        'query_count': query_count,
                        'result_count': len(result) if hasattr(result, '__len__') else 1,
                        'status': 'slow' if execution_time > 1.0 else 'normal'
                    }
                    
                except Exception as e:
                    queries_performance[query_name] = {
                        'error': str(e),
                        'status': 'error'
                    }
            
            return queries_performance
            
        except Exception as e:
            return {'error': f'خطأ في اختبار الاستعلامات: {e}'}

    def run_performance_tests(self):
        """تشغيل اختبارات الأداء الشاملة"""
        self.stdout.write('تشغيل اختبارات الأداء...')
        
        performance_tests = {}
        
        try:
            # اختبار خدمة تحسين الاستعلامات
            start_time = time.time()
            dashboard_stats = query_optimizer.get_dashboard_stats()
            dashboard_time = time.time() - start_time
            
            performance_tests['dashboard_stats'] = {
                'execution_time': dashboard_time,
                'status': 'slow' if dashboard_time > 2.0 else 'normal',
                'data_points': len(dashboard_stats) if dashboard_stats else 0
            }
            
            # اختبار استعلامات الموظفين المحسنة
            start_time = time.time()
            optimized_employees = query_optimizer.optimize_employee_queries()[:10]
            list(optimized_employees)  # تنفيذ الاستعلام
            employees_time = time.time() - start_time
            
            performance_tests['optimized_employees'] = {
                'execution_time': employees_time,
                'status': 'slow' if employees_time > 1.0 else 'normal'
            }
            
            # اختبار ملخص الحضور
            start_time = time.time()
            attendance_summary = query_optimizer.get_attendance_summary()
            attendance_time = time.time() - start_time
            
            performance_tests['attendance_summary'] = {
                'execution_time': attendance_time,
                'status': 'slow' if attendance_time > 1.5 else 'normal',
                'data_points': len(attendance_summary) if attendance_summary else 0
            }
            
            return performance_tests
            
        except Exception as e:
            return {'error': f'خطأ في اختبارات الأداء: {e}'}

    def generate_recommendations(self, analysis_results):
        """إنتاج توصيات التحسين"""
        recommendations = []
        
        try:
            # توصيات عامة لقاعدة البيانات
            db_info = analysis_results.get('database_info', {})
            if db_info.get('vendor') == 'sqlite':
                recommendations.append({
                    'type': 'database',
                    'priority': 'high',
                    'message': 'يُنصح بالترقية من SQLite إلى PostgreSQL أو MySQL للإنتاج'
                })
            
            # توصيات الأداء
            perf_stats = analysis_results.get('performance_stats', {})
            if 'slow_queries' in perf_stats and perf_stats['slow_queries'] > 10:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'message': f'يوجد {perf_stats["slow_queries"]} استعلام بطيء - يحتاج تحسين'
                })
            
            # توصيات النماذج
            for model_name, model_analysis in analysis_results.get('model_analysis', {}).items():
                if isinstance(model_analysis, dict) and 'total_records' in model_analysis:
                    # توصيات للجداول الكبيرة
                    if model_analysis['total_records'] > 10000:
                        recommendations.append({
                            'type': 'indexing',
                            'priority': 'medium',
                            'message': f'جدول {model_name} كبير ({model_analysis["total_records"]} سجل) - يحتاج فهرسة إضافية'
                        })
                    
                    # توصيات الحقول
                    fields_analysis = model_analysis.get('fields_analysis', {})
                    for field_name, field_info in fields_analysis.items():
                        if field_name.endswith('_id') and not field_info.get('indexed'):
                            recommendations.append({
                                'type': 'indexing',
                                'priority': 'medium',
                                'message': f'حقل المفتاح الخارجي {model_name}.{field_name} غير مفهرس'
                            })
            
            # توصيات اختبارات الأداء
            perf_tests = analysis_results.get('performance_tests', {})
            for test_name, test_result in perf_tests.items():
                if isinstance(test_result, dict) and test_result.get('status') == 'slow':
                    recommendations.append({
                        'type': 'optimization',
                        'priority': 'high',
                        'message': f'اختبار {test_name} بطيء ({test_result.get("execution_time", 0):.2f}s)'
                    })
            
            return recommendations
            
        except Exception as e:
            return [{'type': 'error', 'message': f'خطأ في إنتاج التوصيات: {e}'}]

    def display_results(self, analysis_results, verbose=False):
        """عرض نتائج التحليل"""
        
        # معلومات قاعدة البيانات
        self.stdout.write('\n' + self.style.SUCCESS('=== معلومات قاعدة البيانات ==='))
        db_info = analysis_results.get('database_info', {})
        if 'error' not in db_info:
            self.stdout.write(f"نوع قاعدة البيانات: {db_info.get('vendor', 'غير معروف')}")
            self.stdout.write(f"اسم قاعدة البيانات: {db_info.get('database_name', 'غير معروف')}")
            if 'version' in db_info:
                self.stdout.write(f"الإصدار: {db_info['version']}")
        else:
            self.stdout.write(self.style.ERROR(db_info['error']))
        
        # إحصائيات الأداء
        self.stdout.write('\n' + self.style.SUCCESS('=== إحصائيات الأداء ==='))
        perf_stats = analysis_results.get('performance_stats', {})
        if 'error' not in perf_stats:
            for key, value in perf_stats.items():
                self.stdout.write(f"{key}: {value}")
        else:
            self.stdout.write(self.style.ERROR(perf_stats['error']))
        
        # تحليل النماذج
        self.stdout.write('\n' + self.style.SUCCESS('=== تحليل النماذج ==='))
        for model_name, model_analysis in analysis_results.get('model_analysis', {}).items():
            if isinstance(model_analysis, dict) and 'error' not in model_analysis:
                self.stdout.write(f"\n{model_name}:")
                self.stdout.write(f"  عدد السجلات: {model_analysis.get('total_records', 0)}")
                self.stdout.write(f"  عدد الحقول: {len(model_analysis.get('fields_analysis', {}))}")
                self.stdout.write(f"  عدد العلاقات: {len(model_analysis.get('relations_analysis', {}))}")
                
                if verbose and 'common_queries_performance' in model_analysis:
                    self.stdout.write("  أداء الاستعلامات الشائعة:")
                    for query_name, query_perf in model_analysis['common_queries_performance'].items():
                        if 'error' not in query_perf:
                            status_color = self.style.ERROR if query_perf.get('status') == 'slow' else self.style.SUCCESS
                            self.stdout.write(
                                f"    {query_name}: {query_perf.get('execution_time', 0):.3f}s " +
                                status_color(f"({query_perf.get('status', 'unknown')})")
                            )
            elif isinstance(model_analysis, dict):
                self.stdout.write(self.style.ERROR(f"{model_name}: {model_analysis['error']}"))
        
        # اختبارات الأداء
        if 'performance_tests' in analysis_results:
            self.stdout.write('\n' + self.style.SUCCESS('=== اختبارات الأداء ==='))
            for test_name, test_result in analysis_results['performance_tests'].items():
                if isinstance(test_result, dict) and 'error' not in test_result:
                    status_color = self.style.ERROR if test_result.get('status') == 'slow' else self.style.SUCCESS
                    self.stdout.write(
                        f"{test_name}: {test_result.get('execution_time', 0):.3f}s " +
                        status_color(f"({test_result.get('status', 'unknown')})")
                    )
        
        # التوصيات
        self.stdout.write('\n' + self.style.SUCCESS('=== توصيات التحسين ==='))
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_color = {
                    'high': self.style.ERROR,
                    'medium': self.style.WARNING,
                    'low': self.style.SUCCESS
                }.get(rec.get('priority', 'low'), self.style.SUCCESS)
                
                self.stdout.write(
                    f"{i}. [{rec.get('type', 'عام')}] " +
                    priority_color(f"[{rec.get('priority', 'منخفض')}]") +
                    f" {rec.get('message', 'لا توجد رسالة')}"
                )
        else:
            self.stdout.write(self.style.SUCCESS('لا توجد توصيات - الأداء جيد!'))

    def export_results(self, analysis_results, export_path):
        """تصدير النتائج إلى ملف JSON"""
        try:
            # تحويل النتائج لتكون قابلة للتسلسل
            serializable_results = self.make_serializable(analysis_results)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(f'تم تصدير النتائج إلى: {export_path}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطأ في تصدير النتائج: {e}')
            )

    def make_serializable(self, obj):
        """تحويل الكائن ليكون قابلاً للتسلسل في JSON"""
        if isinstance(obj, dict):
            return {key: self.make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return str(obj)
        else:
            return obj