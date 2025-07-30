"""
Middleware لمراقبة الأداء
"""

from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from Hr.services.performance_service import performance_service
import time
import logging
import json

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware لمراقبة أداء الطلبات"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'HR_PERFORMANCE_MONITORING', True)
        self.slow_request_threshold = getattr(settings, 'HR_SLOW_REQUEST_THRESHOLD', 2.0)
        self.log_slow_requests = getattr(settings, 'HR_LOG_SLOW_REQUESTS', True)
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة بداية الطلب"""
        if not self.enabled:
            return None
        
        # تسجيل بداية الطلب
        request._performance_start_time = time.time()
        request._performance_queries_before = len(connection.queries)
        
        return None
    
    def process_response(self, request, response):
        """معالجة نهاية الطلب"""
        if not self.enabled or not hasattr(request, '_performance_start_time'):
            return response
        
        # حساب الوقت المستغرق
        execution_time = time.time() - request._performance_start_time
        queries_count = len(connection.queries) - request._performance_queries_before
        
        # معلومات الطلب
        request_info = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            'execution_time': execution_time,
            'queries_count': queries_count,
            'status_code': response.status_code,
            'timestamp': timezone.now().isoformat()
        }
        
        # تسجيل الطلبات البطيئة
        if execution_time > self.slow_request_threshold and self.log_slow_requests:
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.path} | "
                f"Time: {execution_time:.3f}s | "
                f"Queries: {queries_count} | "
                f"User: {request_info['user']}"
            )
            
            # تسجيل تفاصيل الاستعلامات البطيئة
            if settings.DEBUG and queries_count > 0:
                slow_queries = connection.queries[request._performance_queries_before:]
                for i, query in enumerate(slow_queries):
                    if float(query.get('time', 0)) > 0.1:  # استعلامات أبطأ من 0.1 ثانية
                        logger.warning(
                            f"SLOW QUERY {i+1}: {query['sql'][:200]}... | "
                            f"Time: {query['time']}s"
                        )
        
        # حفظ إحصائيات الأداء
        self._save_performance_stats(request_info)
        
        # إضافة headers للأداء (في وضع التطوير فقط)
        if settings.DEBUG:
            response['X-Execution-Time'] = f"{execution_time:.3f}s"
            response['X-Query-Count'] = str(queries_count)
        
        return response
    
    def process_exception(self, request, exception):
        """معالجة الاستثناءات"""
        if not self.enabled or not hasattr(request, '_performance_start_time'):
            return None
        
        execution_time = time.time() - request._performance_start_time
        queries_count = len(connection.queries) - request._performance_queries_before
        
        # تسجيل الاستثناءات مع معلومات الأداء
        logger.error(
            f"EXCEPTION: {request.method} {request.path} | "
            f"Time: {execution_time:.3f}s | "
            f"Queries: {queries_count} | "
            f"Exception: {str(exception)}"
        )
        
        return None
    
    def _save_performance_stats(self, request_info):
        """حفظ إحصائيات الأداء"""
        try:
            # حفظ في خدمة الأداء
            performance_service.monitor_query_performance(
                func_name=f"{request_info['method']}_{request_info['path']}",
                execution_time=request_info['execution_time'],
                query_count=request_info['queries_count']
            )
            
            # حفظ إحصائيات يومية في التخزين المؤقت
            today = timezone.now().date().isoformat()
            daily_stats_key = f'daily_performance_stats_{today}'
            
            daily_stats = cache.get(daily_stats_key, {
                'total_requests': 0,
                'total_time': 0,
                'total_queries': 0,
                'slow_requests': 0,
                'error_requests': 0,
                'paths': {}
            })
            
            # تحديث الإحصائيات
            daily_stats['total_requests'] += 1
            daily_stats['total_time'] += request_info['execution_time']
            daily_stats['total_queries'] += request_info['queries_count']
            
            if request_info['execution_time'] > self.slow_request_threshold:
                daily_stats['slow_requests'] += 1
            
            if request_info['status_code'] >= 400:
                daily_stats['error_requests'] += 1
            
            # إحصائيات المسارات
            path = request_info['path']
            if path not in daily_stats['paths']:
                daily_stats['paths'][path] = {
                    'count': 0,
                    'total_time': 0,
                    'total_queries': 0,
                    'avg_time': 0
                }
            
            path_stats = daily_stats['paths'][path]
            path_stats['count'] += 1
            path_stats['total_time'] += request_info['execution_time']
            path_stats['total_queries'] += request_info['queries_count']
            path_stats['avg_time'] = path_stats['total_time'] / path_stats['count']
            
            # حفظ الإحصائيات المحدثة
            cache.set(daily_stats_key, daily_stats, 86400)  # 24 ساعة
            
        except Exception as e:
            logger.error(f"خطأ في حفظ إحصائيات الأداء: {e}")


class DatabaseQueryLoggingMiddleware(MiddlewareMixin):
    """Middleware لتسجيل استعلامات قاعدة البيانات"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'HR_LOG_DATABASE_QUERIES', False)
        self.log_all_queries = getattr(settings, 'HR_LOG_ALL_QUERIES', False)
        self.slow_query_threshold = getattr(settings, 'HR_SLOW_QUERY_THRESHOLD', 0.1)
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة بداية الطلب"""
        if not self.enabled:
            return None
        
        request._db_queries_before = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """معالجة نهاية الطلب"""
        if not self.enabled or not hasattr(request, '_db_queries_before'):
            return response
        
        # الحصول على الاستعلامات الجديدة
        new_queries = connection.queries[request._db_queries_before:]
        
        if not new_queries:
            return response
        
        # تحليل الاستعلامات
        query_analysis = self._analyze_queries(new_queries)
        
        # تسجيل الاستعلامات البطيئة أو جميع الاستعلامات
        if self.log_all_queries or query_analysis['slow_queries']:
            self._log_queries(request, query_analysis)
        
        # حفظ إحصائيات الاستعلامات
        self._save_query_stats(request, query_analysis)
        
        return response
    
    def _analyze_queries(self, queries):
        """تحليل الاستعلامات"""
        analysis = {
            'total_queries': len(queries),
            'total_time': 0,
            'slow_queries': [],
            'duplicate_queries': [],
            'query_types': {
                'SELECT': 0,
                'INSERT': 0,
                'UPDATE': 0,
                'DELETE': 0,
                'OTHER': 0
            }
        }
        
        query_signatures = {}
        
        for query in queries:
            query_time = float(query.get('time', 0))
            query_sql = query.get('sql', '')
            
            analysis['total_time'] += query_time
            
            # تصنيف نوع الاستعلام
            sql_upper = query_sql.upper().strip()
            if sql_upper.startswith('SELECT'):
                analysis['query_types']['SELECT'] += 1
            elif sql_upper.startswith('INSERT'):
                analysis['query_types']['INSERT'] += 1
            elif sql_upper.startswith('UPDATE'):
                analysis['query_types']['UPDATE'] += 1
            elif sql_upper.startswith('DELETE'):
                analysis['query_types']['DELETE'] += 1
            else:
                analysis['query_types']['OTHER'] += 1
            
            # تحديد الاستعلامات البطيئة
            if query_time > self.slow_query_threshold:
                analysis['slow_queries'].append({
                    'sql': query_sql[:500],  # أول 500 حرف
                    'time': query_time
                })
            
            # تحديد الاستعلامات المكررة
            # إنشاء توقيع للاستعلام (بدون القيم)
            import re
            signature = re.sub(r"'[^']*'", "'?'", query_sql)
            signature = re.sub(r'\d+', '?', signature)
            
            if signature in query_signatures:
                query_signatures[signature] += 1
            else:
                query_signatures[signature] = 1
        
        # العثور على الاستعلامات المكررة
        analysis['duplicate_queries'] = [
            {'signature': sig, 'count': count}
            for sig, count in query_signatures.items()
            if count > 1
        ]
        
        return analysis
    
    def _log_queries(self, request, analysis):
        """تسجيل الاستعلامات"""
        log_message = (
            f"DB QUERIES: {request.method} {request.path} | "
            f"Total: {analysis['total_queries']} | "
            f"Time: {analysis['total_time']:.3f}s | "
            f"Slow: {len(analysis['slow_queries'])} | "
            f"Duplicates: {len(analysis['duplicate_queries'])}"
        )
        
        if analysis['slow_queries'] or analysis['duplicate_queries']:
            logger.warning(log_message)
            
            # تسجيل تفاصيل الاستعلامات البطيئة
            for slow_query in analysis['slow_queries']:
                logger.warning(
                    f"SLOW QUERY ({slow_query['time']:.3f}s): {slow_query['sql']}"
                )
            
            # تسجيل الاستعلامات المكررة
            for dup_query in analysis['duplicate_queries']:
                logger.warning(
                    f"DUPLICATE QUERY ({dup_query['count']}x): {dup_query['signature'][:200]}..."
                )
        else:
            logger.debug(log_message)
    
    def _save_query_stats(self, request, analysis):
        """حفظ إحصائيات الاستعلامات"""
        try:
            # حفظ إحصائيات يومية
            today = timezone.now().date().isoformat()
            query_stats_key = f'daily_query_stats_{today}'
            
            query_stats = cache.get(query_stats_key, {
                'total_queries': 0,
                'total_time': 0,
                'slow_queries_count': 0,
                'duplicate_queries_count': 0,
                'query_types': {
                    'SELECT': 0,
                    'INSERT': 0,
                    'UPDATE': 0,
                    'DELETE': 0,
                    'OTHER': 0
                }
            })
            
            # تحديث الإحصائيات
            query_stats['total_queries'] += analysis['total_queries']
            query_stats['total_time'] += analysis['total_time']
            query_stats['slow_queries_count'] += len(analysis['slow_queries'])
            query_stats['duplicate_queries_count'] += len(analysis['duplicate_queries'])
            
            for query_type, count in analysis['query_types'].items():
                query_stats['query_types'][query_type] += count
            
            # حفظ الإحصائيات المحدثة
            cache.set(query_stats_key, query_stats, 86400)  # 24 ساعة
            
        except Exception as e:
            logger.error(f"خطأ في حفظ إحصائيات الاستعلامات: {e}")


class CachePerformanceMiddleware(MiddlewareMixin):
    """Middleware لمراقبة أداء التخزين المؤقت"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'HR_MONITOR_CACHE_PERFORMANCE', True)
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة بداية الطلب"""
        if not self.enabled:
            return None
        
        # تسجيل حالة التخزين المؤقت قبل الطلب
        request._cache_hits_before = getattr(cache, '_hits', 0)
        request._cache_misses_before = getattr(cache, '_misses', 0)
        
        return None
    
    def process_response(self, request, response):
        """معالجة نهاية الطلب"""
        if not self.enabled:
            return response
        
        if not hasattr(request, '_cache_hits_before'):
            return response
        
        # حساب إحصائيات التخزين المؤقت
        cache_hits = getattr(cache, '_hits', 0) - request._cache_hits_before
        cache_misses = getattr(cache, '_misses', 0) - request._cache_misses_before
        
        if cache_hits + cache_misses > 0:
            hit_rate = cache_hits / (cache_hits + cache_misses)
            
            # تسجيل معدل الإصابة المنخفض
            if hit_rate < 0.5:
                logger.warning(
                    f"LOW CACHE HIT RATE: {request.method} {request.path} | "
                    f"Hits: {cache_hits} | Misses: {cache_misses} | "
                    f"Rate: {hit_rate:.2%}"
                )
            
            # حفظ إحصائيات التخزين المؤقت
            self._save_cache_stats(request, cache_hits, cache_misses, hit_rate)
        
        return response
    
    def _save_cache_stats(self, request, hits, misses, hit_rate):
        """حفظ إحصائيات التخزين المؤقت"""
        try:
            today = timezone.now().date().isoformat()
            cache_stats_key = f'daily_cache_stats_{today}'
            
            cache_stats = cache.get(cache_stats_key, {
                'total_hits': 0,
                'total_misses': 0,
                'total_requests': 0,
                'hit_rate': 0
            })
            
            cache_stats['total_hits'] += hits
            cache_stats['total_misses'] += misses
            cache_stats['total_requests'] += 1
            
            if cache_stats['total_hits'] + cache_stats['total_misses'] > 0:
                cache_stats['hit_rate'] = cache_stats['total_hits'] / (
                    cache_stats['total_hits'] + cache_stats['total_misses']
                )
            
            cache.set(cache_stats_key, cache_stats, 86400)  # 24 ساعة
            
        except Exception as e:
            logger.error(f"خطأ في حفظ إحصائيات التخزين المؤقت: {e}")