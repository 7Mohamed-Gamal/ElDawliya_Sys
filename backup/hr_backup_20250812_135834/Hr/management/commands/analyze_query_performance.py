"""
أمر تحليل أداء الاستعلامات
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from Hr.services.query_optimizer import query_optimizer
import time
import json


class Command(BaseCommand):
    help = 'تحليل أداء الاستعلامات وتحديد الاستعلامات البطيئة'

    def add_arguments(self, parser):
        parser.add_argument(
            '--duration',
            type=int,
            default=60,
            help='مدة المراقبة بالثواني (افتراضي: 60)'
        )
        
        parser.add_argument(
            '--threshold',
            type=float,
            default=1.0,
            help='عتبة الاستعلام البطيء بالثواني (افتراضي: 1.0)'
        )
        
        parser.add_argument(
            '--output',
            choices=['console', 'file', 'cache'],
            default='console',
            help='مكان إخراج النتائج'
        )
        
        parser.add_argument(
            '--analyze-existing',
            action='store_true',
            help='تحليل الاستعلامات المحفوظة مسبقاً'
        )

    def handle(self, *args, **options):
        duration = options['duration']
        threshold = options['threshold']
        output = options['output']
        analyze_existing = options['analyze_existing']
        
        if analyze_existing:
            self.analyze_existing_queries(threshold, output)
        else:
            self.monitor_queries(duration, threshold, output)

    def monitor_queries(self, duration, threshold, output):
        """مراقبة الاستعلامات لفترة محددة"""
        self.stdout.write(
            self.style.SUCCESS(f'بدء مراقبة الاستعلامات لمدة {duration} ثانية...')
        )
        
        start_time = time.time()
        initial_query_count = len(connection.queries)
        slow_queries = []
        
        # تفعيل تسجيل الاستعلامات
        original_debug = settings.DEBUG
        settings.DEBUG = True
        
        try:
            while time.time() - start_time < duration:
                current_queries = connection.queries[initial_query_count:]
                
                for query in current_queries:
                    query_time = float(query['time'])
                    if query_time > threshold:
                        slow_query = {
                            'sql': query['sql'],
                            'time': query_time,
                            'timestamp': timezone.now().isoformat()
                        }
                        slow_queries.append(slow_query)
                        
                        self.stdout.write(
                            self.style.WARNING(
                                f'استعلام بطيء: {query_time:.2f}s - {query["sql"][:100]}...'
                            )
                        )
                
                time.sleep(1)  # فحص كل ثانية
                
        finally:
            settings.DEBUG = original_debug
        
        # تحليل النتائج
        self.analyze_results(slow_queries, output)

    def analyze_existing_queries(self, threshold, output):
        """تحليل الاستعلامات المحفوظة مسبقاً"""
        self.stdout.write(
            self.style.SUCCESS('تحليل الاستعلامات المحفوظة...')
        )
        
        # الحصول على الاستعلامات البطيئة من التخزين المؤقت
        slow_queries = cache.get('slow_queries_log', [])
        
        if not slow_queries:
            self.stdout.write(
                self.style.WARNING('لا توجد استعلامات بطيئة محفوظة')
            )
            return
        
        # فلترة حسب العتبة
        filtered_queries = [
            q for q in slow_queries 
            if q.get('execution_time', 0) > threshold
        ]
        
        self.analyze_results(filtered_queries, output)

    def analyze_results(self, slow_queries, output):
        """تحليل نتائج الاستعلامات البطيئة"""
        if not slow_queries:
            self.stdout.write(
                self.style.SUCCESS('لا توجد استعلامات بطيئة!')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'تم العثور على {len(slow_queries)} استعلام بطيء')
        )
        
        # تحليل الأنماط
        analysis = self.perform_analysis(slow_queries)
        
        # إخراج النتائج
        if output == 'console':
            self.output_to_console(analysis)
        elif output == 'file':
            self.output_to_file(analysis)
        elif output == 'cache':
            self.output_to_cache(analysis)

    def perform_analysis(self, slow_queries):
        """تحليل الاستعلامات البطيئة"""
        analysis = {
            'total_slow_queries': len(slow_queries),
            'avg_time': sum(q.get('time', q.get('execution_time', 0)) for q in slow_queries) / len(slow_queries),
            'max_time': max(q.get('time', q.get('execution_time', 0)) for q in slow_queries),
            'min_time': min(q.get('time', q.get('execution_time', 0)) for q in slow_queries),
            'patterns': {},
            'tables': {},
            'operations': {},
            'recommendations': []
        }
        
        # تحليل الأنماط
        for query in slow_queries:
            sql = query.get('sql', '')
            query_time = query.get('time', query.get('execution_time', 0))
            
            # تحليل الجداول
            tables = self.extract_tables(sql)
            for table in tables:
                if table not in analysis['tables']:
                    analysis['tables'][table] = {'count': 0, 'total_time': 0}
                analysis['tables'][table]['count'] += 1
                analysis['tables'][table]['total_time'] += query_time
            
            # تحليل العمليات
            operation = self.extract_operation(sql)
            if operation not in analysis['operations']:
                analysis['operations'][operation] = {'count': 0, 'total_time': 0}
            analysis['operations'][operation]['count'] += 1
            analysis['operations'][operation]['total_time'] += query_time
            
            # تحليل الأنماط الشائعة
            pattern = self.extract_pattern(sql)
            if pattern not in analysis['patterns']:
                analysis['patterns'][pattern] = {'count': 0, 'total_time': 0}
            analysis['patterns'][pattern]['count'] += 1
            analysis['patterns'][pattern]['total_time'] += query_time
        
        # إنتاج التوصيات
        analysis['recommendations'] = self.generate_recommendations(analysis)
        
        return analysis

    def extract_tables(self, sql):
        """استخراج أسماء الجداول من الاستعلام"""
        import re
        
        # البحث عن أسماء الجداول بعد FROM و JOIN
        pattern = r'(?:FROM|JOIN)\s+["`]?(\w+)["`]?'
        matches = re.findall(pattern, sql.upper())
        
        # تنظيف أسماء الجداول
        tables = []
        for match in matches:
            if match and not match.upper() in ['SELECT', 'WHERE', 'ORDER', 'GROUP']:
                tables.append(match.lower())
        
        return list(set(tables))

    def extract_operation(self, sql):
        """استخراج نوع العملية من الاستعلام"""
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'

    def extract_pattern(self, sql):
        """استخراج نمط الاستعلام"""
        import re
        
        # إزالة القيم المحددة واستبدالها بـ placeholder
        pattern = re.sub(r"'[^']*'", "'?'", sql)
        pattern = re.sub(r'\b\d+\b', '?', pattern)
        pattern = re.sub(r'\s+', ' ', pattern)
        
        return pattern[:200]  # أول 200 حرف

    def generate_recommendations(self, analysis):
        """إنتاج توصيات التحسين"""
        recommendations = []
        
        # توصيات بناءً على الجداول الأكثر استخداماً
        if analysis['tables']:
            slowest_table = max(
                analysis['tables'].items(),
                key=lambda x: x[1]['total_time']
            )
            recommendations.append(
                f"الجدول '{slowest_table[0]}' يحتاج تحسين - "
                f"إجمالي الوقت: {slowest_table[1]['total_time']:.2f}s"
            )
        
        # توصيات بناءً على العمليات
        if analysis['operations']:
            slowest_operation = max(
                analysis['operations'].items(),
                key=lambda x: x[1]['total_time']
            )
            recommendations.append(
                f"عمليات {slowest_operation[0]} تحتاج تحسين - "
                f"متوسط الوقت: {slowest_operation[1]['total_time']/slowest_operation[1]['count']:.2f}s"
            )
        
        # توصيات عامة
        if analysis['avg_time'] > 2.0:
            recommendations.append(
                "متوسط وقت الاستعلامات مرتفع. يُنصح بمراجعة الفهارس وتحسين الاستعلامات"
            )
        
        if analysis['total_slow_queries'] > 50:
            recommendations.append(
                "عدد كبير من الاستعلامات البطيئة. يُنصح بتطبيق التخزين المؤقت"
            )
        
        return recommendations

    def output_to_console(self, analysis):
        """إخراج النتائج إلى وحدة التحكم"""
        self.stdout.write(self.style.SUCCESS('\n=== تحليل أداء الاستعلامات ==='))
        
        self.stdout.write(f'إجمالي الاستعلامات البطيئة: {analysis["total_slow_queries"]}')
        self.stdout.write(f'متوسط الوقت: {analysis["avg_time"]:.2f}s')
        self.stdout.write(f'أبطأ استعلام: {analysis["max_time"]:.2f}s')
        self.stdout.write(f'أسرع استعلام بطيء: {analysis["min_time"]:.2f}s')
        
        # الجداول الأكثر استخداماً
        if analysis['tables']:
            self.stdout.write('\nالجداول الأكثر استخداماً:')
            sorted_tables = sorted(
                analysis['tables'].items(),
                key=lambda x: x[1]['total_time'],
                reverse=True
            )
            for table, stats in sorted_tables[:5]:
                avg_time = stats['total_time'] / stats['count']
                self.stdout.write(
                    f'  - {table}: {stats["count"]} استعلام، '
                    f'متوسط الوقت: {avg_time:.2f}s'
                )
        
        # العمليات الأكثر استخداماً
        if analysis['operations']:
            self.stdout.write('\nالعمليات الأكثر استخداماً:')
            sorted_operations = sorted(
                analysis['operations'].items(),
                key=lambda x: x[1]['total_time'],
                reverse=True
            )
            for operation, stats in sorted_operations:
                avg_time = stats['total_time'] / stats['count']
                self.stdout.write(
                    f'  - {operation}: {stats["count"]} استعلام، '
                    f'متوسط الوقت: {avg_time:.2f}s'
                )
        
        # التوصيات
        if analysis['recommendations']:
            self.stdout.write('\nتوصيات التحسين:')
            for recommendation in analysis['recommendations']:
                self.stdout.write(f'  • {recommendation}')

    def output_to_file(self, analysis):
        """إخراج النتائج إلى ملف"""
        import os
        from django.conf import settings
        
        # إنشاء مجلد التقارير إذا لم يكن موجوداً
        reports_dir = os.path.join(settings.BASE_DIR, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # اسم الملف مع الطابع الزمني
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'query_performance_analysis_{timestamp}.json'
        filepath = os.path.join(reports_dir, filename)
        
        # حفظ التحليل
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
        
        self.stdout.write(
            self.style.SUCCESS(f'تم حفظ التحليل في: {filepath}')
        )

    def output_to_cache(self, analysis):
        """حفظ النتائج في التخزين المؤقت"""
        cache_key = f'query_analysis_{timezone.now().strftime("%Y%m%d")}'
        cache.set(cache_key, analysis, 86400)  # 24 ساعة
        
        self.stdout.write(
            self.style.SUCCESS(f'تم حفظ التحليل في التخزين المؤقت: {cache_key}')
        )