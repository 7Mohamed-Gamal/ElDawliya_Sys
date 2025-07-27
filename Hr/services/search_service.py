"""
خدمة البحث المتقدم والذكي
"""

import re
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import Q, Count, F, Value, Case, When
from django.db.models.functions import Concat, Lower
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from ..models_search import (
    SearchIndex, SavedSearch, SearchSuggestion, SearchLog,
    SearchFilter, SmartSearchPattern
)

logger = logging.getLogger('hr_search')


class AdvancedSearchService:
    """خدمة البحث المتقدم"""
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'SEARCH_CACHE_TIMEOUT', 300)  # 5 دقائق
        self.max_results = getattr(settings, 'SEARCH_MAX_RESULTS', 1000)
        self.suggestion_limit = getattr(settings, 'SEARCH_SUGGESTION_LIMIT', 10)
        
        # أوزان أنواع المحتوى
        self.content_weights = {
            'employee': 1.0,
            'department': 0.8,
            'job': 0.7,
            'company': 0.9,
            'branch': 0.8,
            'leave_request': 0.6,
            'attendance_record': 0.5,
            'payroll_entry': 0.6,
            'employee_file': 0.7,
            'evaluation': 0.8,
            'notification': 0.4,
        }
    
    def search(
        self,
        query: str,
        user: User = None,
        content_types: List[str] = None,
        filters: Dict[str, Any] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = 'relevance',
        search_type: str = 'simple'
    ) -> Dict[str, Any]:
        """البحث الرئيسي"""
        
        start_time = time.time()
        
        try:
            # تنظيف وتحسين الاستعلام
            processed_query = self._process_query(query, search_type)
            
            # بناء الاستعلام الأساسي
            queryset = self._build_base_queryset(
                processed_query, content_types, filters, user
            )
            
            # تطبيق الترتيب
            queryset = self._apply_sorting(queryset, sort_by, processed_query)
            
            # حساب العدد الإجمالي
            total_count = queryset.count()
            
            # تطبيق التصفح
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            results = queryset[start_index:end_index]
            
            # تحويل النتائج
            formatted_results = self._format_results(results, processed_query)
            
            # حساب الوقت المستغرق
            execution_time = time.time() - start_time
            
            # تسجيل البحث
            self._log_search(
                user, query, search_type, filters, 
                total_count, execution_time
            )
            
            # إنشاء الاقتراحات
            suggestions = self._generate_suggestions(query, total_count == 0)
            
            return {
                'results': formatted_results,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'execution_time': execution_time,
                'query': processed_query,
                'suggestions': suggestions,
                'filters_applied': filters or {},
                'content_types': content_types or [],
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            self._log_search(
                user, query, search_type, filters, 
                0, time.time() - start_time, 'error'
            )
            raise e
    
    def smart_search(
        self,
        query: str,
        user: User = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """البحث الذكي مع معالجة متقدمة"""
        
        # تطبيق أنماط البحث الذكي
        enhanced_query = self._apply_smart_patterns(query, context)
        
        # البحث مع التوسع التلقائي
        results = self.search(
            enhanced_query, user, search_type='smart'
        )
        
        # إذا لم توجد نتائج، جرب البحث المرن
        if results['total_count'] == 0:
            flexible_results = self._flexible_search(query, user, context)
            if flexible_results['total_count'] > 0:
                results = flexible_results
                results['search_type'] = 'flexible'
        
        return results
    
    def advanced_search(
        self,
        criteria: Dict[str, Any],
        user: User = None
    ) -> Dict[str, Any]:
        """البحث المتقدم مع معايير متعددة"""
        
        # بناء استعلام معقد من المعايير
        query_parts = []
        filters = {}
        
        # معالجة معايير النص
        if criteria.get('text_query'):
            query_parts.append(criteria['text_query'])
        
        # معالجة الفلاتر
        for field, value in criteria.items():
            if field.startswith('filter_') and value:
                filter_name = field.replace('filter_', '')
                filters[filter_name] = value
        
        # دمج أجزاء الاستعلام
        combined_query = ' '.join(query_parts) if query_parts else '*'
        
        return self.search(
            combined_query,
            user=user,
            filters=filters,
            content_types=criteria.get('content_types'),
            sort_by=criteria.get('sort_by', 'relevance'),
            page=criteria.get('page', 1),
            page_size=criteria.get('page_size', 20),
            search_type='advanced'
        )
    
    def get_suggestions(
        self,
        partial_query: str,
        user: User = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """الحصول على اقتراحات البحث"""
        
        if not partial_query or len(partial_query) < 2:
            return []
        
        limit = limit or self.suggestion_limit
        
        # البحث في الاقتراحات المحفوظة
        suggestions = SearchSuggestion.objects.filter(
            text__icontains=partial_query,
            is_active=True
        ).order_by('-usage_count', '-success_rate')[:limit]
        
        results = []
        for suggestion in suggestions:
            results.append({
                'text': suggestion.text,
                'type': suggestion.suggestion_type,
                'usage_count': suggestion.usage_count,
                'success_rate': suggestion.success_rate,
            })
        
        # إضافة اقتراحات من الفهرس
        if len(results) < limit:
            index_suggestions = self._get_index_suggestions(
                partial_query, limit - len(results)
            )
            results.extend(index_suggestions)
        
        return results
    
    def save_search(
        self,
        user: User,
        name: str,
        query: str,
        filters: Dict[str, Any] = None,
        content_types: List[str] = None,
        search_type: str = 'simple',
        description: str = '',
        is_public: bool = False
    ) -> SavedSearch:
        """حفظ عملية البحث"""
        
        saved_search = SavedSearch.objects.create(
            user=user,
            name=name,
            description=description,
            search_type=search_type,
            query=query,
            filters=filters or {},
            content_types=content_types or [],
            is_public=is_public
        )
        
        return saved_search
    
    def get_saved_searches(
        self,
        user: User,
        include_public: bool = True
    ) -> List[SavedSearch]:
        """الحصول على عمليات البحث المحفوظة"""
        
        queryset = SavedSearch.objects.filter(user=user)
        
        if include_public:
            public_searches = SavedSearch.objects.filter(
                is_public=True
            ).exclude(user=user)
            queryset = queryset.union(public_searches)
        
        return queryset.order_by('-is_favorite', '-last_used_at', '-created_at')
    
    def execute_saved_search(
        self,
        saved_search: SavedSearch,
        user: User = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """تنفيذ بحث محفوظ"""
        
        # تحديث إحصائيات الاستخدام
        saved_search.increment_usage()
        
        # تنفيذ البحث
        if saved_search.search_type == 'advanced':
            criteria = {
                'text_query': saved_search.query,
                'content_types': saved_search.content_types,
                'page': page,
                'page_size': page_size,
            }
            criteria.update({f'filter_{k}': v for k, v in saved_search.filters.items()})
            
            return self.advanced_search(criteria, user)
        else:
            return self.search(
                saved_search.query,
                user=user,
                content_types=saved_search.content_types,
                filters=saved_search.filters,
                page=page,
                page_size=page_size,
                search_type=saved_search.search_type
            )
    
    def get_search_analytics(
        self,
        user: User = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """تحليلات البحث"""
        
        start_date = timezone.now() - timedelta(days=days)
        
        # استعلام أساسي
        logs_query = SearchLog.objects.filter(created_at__gte=start_date)
        if user:
            logs_query = logs_query.filter(user=user)
        
        # الإحصائيات العامة
        total_searches = logs_query.count()
        successful_searches = logs_query.filter(result_status='success').count()
        no_result_searches = logs_query.filter(result_status='no_results').count()
        
        # متوسط وقت التنفيذ
        avg_execution_time = logs_query.aggregate(
            avg_time=models.Avg('execution_time')
        )['avg_time'] or 0
        
        # أكثر الاستعلامات شيوعاً
        popular_queries = logs_query.values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # أنواع البحث
        search_types = logs_query.values('search_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # البحث اليومي
        daily_searches = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            count = logs_query.filter(created_at__date=date).count()
            daily_searches.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        daily_searches.reverse()
        
        return {
            'total_searches': total_searches,
            'successful_searches': successful_searches,
            'no_result_searches': no_result_searches,
            'success_rate': (successful_searches / total_searches * 100) if total_searches > 0 else 0,
            'avg_execution_time': round(avg_execution_time, 3),
            'popular_queries': list(popular_queries),
            'search_types': list(search_types),
            'daily_searches': daily_searches,
        }
    
    def _process_query(self, query: str, search_type: str = 'simple') -> str:
        """معالجة وتنظيف الاستعلام"""
        
        if not query:
            return ''
        
        # تنظيف أساسي
        processed = query.strip()
        
        # إزالة الأحرف الخاصة الضارة
        processed = re.sub(r'[<>\"\'%;()&+]', ' ', processed)
        
        # تطبيع المسافات
        processed = re.sub(r'\s+', ' ', processed)
        
        # معالجة خاصة للبحث المتقدم
        if search_type == 'advanced':
            processed = self._process_advanced_query(processed)
        elif search_type == 'smart':
            processed = self._apply_smart_patterns(processed)
        
        return processed.strip()
    
    def _process_advanced_query(self, query: str) -> str:
        """معالجة استعلام البحث المتقدم"""
        
        # دعم العمليات المنطقية
        query = re.sub(r'\bAND\b', ' & ', query, flags=re.IGNORECASE)
        query = re.sub(r'\bOR\b', ' | ', query, flags=re.IGNORECASE)
        query = re.sub(r'\bNOT\b', ' ! ', query, flags=re.IGNORECASE)
        
        # دعم البحث بالعبارات
        query = re.sub(r'\"([^\"]+)\"', r'\\1', query)
        
        return query
    
    def _apply_smart_patterns(self, query: str, context: Dict[str, Any] = None) -> str:
        """تطبيق أنماط البحث الذكي"""
        
        patterns = SmartSearchPattern.objects.filter(is_active=True).order_by('-priority')
        
        enhanced_query = query
        for pattern in patterns:
            # التحقق من السياق إذا كان مطلوباً
            if pattern.context_filters and context:
                if not self._match_context(pattern.context_filters, context):
                    continue
            
            # تطبيق النمط
            enhanced_query = pattern.apply_pattern(enhanced_query)
            
            # تحديث إحصائيات الاستخدام
            if enhanced_query != query:
                pattern.usage_count = F('usage_count') + 1
                pattern.save(update_fields=['usage_count'])
        
        return enhanced_query
    
    def _build_base_queryset(
        self,
        query: str,
        content_types: List[str] = None,
        filters: Dict[str, Any] = None,
        user: User = None
    ):
        """بناء الاستعلام الأساسي"""
        
        queryset = SearchIndex.objects.filter(is_active=True)
        
        # فلترة أنواع المحتوى
        if content_types:
            content_type_objects = ContentType.objects.filter(
                model__in=content_types
            )
            queryset = queryset.filter(content_type__in=content_type_objects)
        
        # تطبيق البحث النصي
        if query and query != '*':
            # بحث بسيط في الحقول النصية
            search_q = (
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(keywords__icontains=query) |
                Q(search_vector__icontains=query.lower())
            )
            
            # البحث في الكلمات المنفصلة
            words = query.split()
            if len(words) > 1:
                for word in words:
                    if len(word) > 2:  # تجاهل الكلمات القصيرة
                        search_q |= (
                            Q(title__icontains=word) |
                            Q(content__icontains=word) |
                            Q(keywords__icontains=word)
                        )
            
            queryset = queryset.filter(search_q)
        
        # تطبيق الفلاتر الإضافية
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # فلترة الصلاحيات (إذا كان المستخدم محدد)
        if user:
            queryset = self._apply_permissions(queryset, user)
        
        return queryset.distinct()
    
    def _apply_filters(self, queryset, filters: Dict[str, Any]):
        """تطبيق الفلاتر"""
        
        for filter_name, filter_value in filters.items():
            if not filter_value:
                continue
            
            try:
                # البحث عن تعريف الفلتر
                search_filter = SearchFilter.objects.get(
                    name=filter_name,
                    is_active=True
                )
                
                # تطبيق الفلتر حسب نوعه
                queryset = self._apply_single_filter(
                    queryset, search_filter, filter_value
                )
                
            except SearchFilter.DoesNotExist:
                # فلاتر افتراضية
                if filter_name == 'company_id':
                    queryset = queryset.filter(company_id=filter_value)
                elif filter_name == 'department_id':
                    queryset = queryset.filter(department_id=filter_value)
                elif filter_name == 'branch_id':
                    queryset = queryset.filter(branch_id=filter_value)
                elif filter_name == 'date_from':
                    queryset = queryset.filter(created_at__gte=filter_value)
                elif filter_name == 'date_to':
                    queryset = queryset.filter(created_at__lte=filter_value)
        
        return queryset
    
    def _apply_single_filter(self, queryset, search_filter: SearchFilter, value):
        """تطبيق فلتر واحد"""
        
        field_name = search_filter.field_name
        filter_type = search_filter.filter_type
        
        # بناء الفلتر حسب النوع
        if filter_type == 'text':
            if isinstance(value, dict) and 'operator' in value:
                operator = value['operator']
                search_value = value['value']
                
                if operator == 'contains':
                    return queryset.filter(**{f"{field_name}__icontains": search_value})
                elif operator == 'equals':
                    return queryset.filter(**{field_name: search_value})
                elif operator == 'starts_with':
                    return queryset.filter(**{f"{field_name}__istartswith": search_value})
                elif operator == 'ends_with':
                    return queryset.filter(**{f"{field_name}__iendswith": search_value})
            else:
                return queryset.filter(**{f"{field_name}__icontains": value})
        
        elif filter_type == 'number':
            if isinstance(value, dict) and 'operator' in value:
                operator = value['operator']
                search_value = value['value']
                
                if operator == 'equals':
                    return queryset.filter(**{field_name: search_value})
                elif operator == 'greater_than':
                    return queryset.filter(**{f"{field_name}__gt": search_value})
                elif operator == 'less_than':
                    return queryset.filter(**{f"{field_name}__lt": search_value})
                elif operator == 'between':
                    return queryset.filter(
                        **{f"{field_name}__gte": search_value[0]},
                        **{f"{field_name}__lte": search_value[1]}
                    )
            else:
                return queryset.filter(**{field_name: value})
        
        elif filter_type == 'date':
            if isinstance(value, dict) and 'operator' in value:
                operator = value['operator']
                search_value = value['value']
                
                if operator == 'equals':
                    return queryset.filter(**{f"{field_name}__date": search_value})
                elif operator == 'greater_than':
                    return queryset.filter(**{f"{field_name}__gt": search_value})
                elif operator == 'less_than':
                    return queryset.filter(**{f"{field_name}__lt": search_value})
                elif operator == 'between':
                    return queryset.filter(
                        **{f"{field_name}__gte": search_value[0]},
                        **{f"{field_name}__lte": search_value[1]}
                    )
            else:
                return queryset.filter(**{f"{field_name}__date": value})
        
        elif filter_type == 'choice':
            if isinstance(value, list):
                return queryset.filter(**{f"{field_name}__in": value})
            else:
                return queryset.filter(**{field_name: value})
        
        elif filter_type == 'boolean':
            return queryset.filter(**{field_name: bool(value)})
        
        return queryset
    
    def _apply_permissions(self, queryset, user: User):
        """تطبيق فلاتر الصلاحيات"""
        
        # هذا مثال بسيط - يمكن تطويره حسب نظام الصلاحيات
        if not user.is_superuser:
            # فلترة حسب الشركة/القسم إذا كان المستخدم محدود الصلاحيات
            if hasattr(user, 'employee_profile'):
                employee = user.employee_profile
                if employee.company_id:
                    queryset = queryset.filter(company_id=employee.company_id)
                if employee.department_id and not user.has_perm('Hr.view_all_departments'):
                    queryset = queryset.filter(department_id=employee.department_id)
        
        return queryset
    
    def _apply_sorting(self, queryset, sort_by: str, query: str = ''):
        """تطبيق الترتيب"""
        
        if sort_by == 'relevance' and query:
            # ترتيب حسب الصلة (مبسط)
            return queryset.extra(
                select={
                    'relevance': """
                        CASE 
                            WHEN title ILIKE %s THEN 3
                            WHEN content ILIKE %s THEN 2
                            WHEN keywords ILIKE %s THEN 1
                            ELSE 0
                        END
                    """
                },
                select_params=[f'%{query}%', f'%{query}%', f'%{query}%']
            ).order_by('-relevance', '-created_at')
        
        elif sort_by == 'date_desc':
            return queryset.order_by('-created_at')
        elif sort_by == 'date_asc':
            return queryset.order_by('created_at')
        elif sort_by == 'title':
            return queryset.order_by('title')
        elif sort_by == 'type':
            return queryset.order_by('content_type__model', 'title')
        else:
            return queryset.order_by('-created_at')
    
    def _format_results(self, results, query: str = '') -> List[Dict[str, Any]]:
        """تنسيق النتائج"""
        
        formatted = []
        
        for result in results:
            # تمييز النص المطابق
            highlighted_title = self._highlight_text(result.title, query)
            highlighted_content = self._highlight_text(result.content[:200], query)
            
            formatted.append({
                'id': str(result.id),
                'title': highlighted_title,
                'content': highlighted_content,
                'content_type': result.content_type.model,
                'content_type_name': result.content_type.name,
                'object_id': result.object_id,
                'metadata': result.metadata,
                'created_at': result.created_at.isoformat(),
                'url': self._get_object_url(result),
            })
        
        return formatted
    
    def _highlight_text(self, text: str, query: str) -> str:
        """تمييز النص المطابق"""
        
        if not query or not text:
            return text
        
        # تمييز بسيط
        words = query.split()
        highlighted = text
        
        for word in words:
            if len(word) > 2:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                highlighted = pattern.sub(f'<mark>{word}</mark>', highlighted)
        
        return highlighted
    
    def _get_object_url(self, search_result) -> str:
        """الحصول على رابط الكائن"""
        
        content_type = search_result.content_type.model
        object_id = search_result.object_id
        
        # روابط افتراضية - يمكن تخصيصها
        url_patterns = {
            'employee': f'/hr/employees/{object_id}/',
            'department': f'/hr/departments/{object_id}/',
            'job': f'/hr/jobs/{object_id}/',
            'company': f'/hr/companies/{object_id}/',
            'branch': f'/hr/branches/{object_id}/',
            'leave_request': f'/hr/leave-requests/{object_id}/',
            'attendance_record': f'/hr/attendance/records/{object_id}/',
            'payroll_entry': f'/hr/payroll-entries/{object_id}/',
            'employee_file': f'/hr/employee-documents/{object_id}/',
            'evaluation': f'/hr/evaluations/{object_id}/',
            'notification': f'/hr/notifications/{object_id}/',
        }
        
        return url_patterns.get(content_type, '#')
    
    def _flexible_search(self, query: str, user: User = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """البحث المرن عند عدم وجود نتائج"""
        
        # البحث بكلمات منفصلة
        words = query.split()
        if len(words) > 1:
            # جرب البحث بكل كلمة على حدة
            for word in words:
                if len(word) > 2:
                    results = self.search(word, user, search_type='flexible')
                    if results['total_count'] > 0:
                        results['original_query'] = query
                        results['flexible_query'] = word
                        return results
        
        # البحث الجزئي
        if len(query) > 4:
            partial_query = query[:len(query)//2]
            results = self.search(partial_query, user, search_type='flexible')
            if results['total_count'] > 0:
                results['original_query'] = query
                results['flexible_query'] = partial_query
                return results
        
        return {'results': [], 'total_count': 0}
    
    def _generate_suggestions(self, query: str, no_results: bool = False) -> List[str]:
        """إنتاج اقتراحات البحث"""
        
        suggestions = []
        
        if no_results:
            # اقتراحات للاستعلامات بدون نتائج
            similar_queries = SearchLog.objects.filter(
                query__icontains=query[:len(query)//2],
                result_count__gt=0
            ).values_list('query', flat=True).distinct()[:5]
            
            suggestions.extend(similar_queries)
        
        # اقتراحات عامة
        popular_suggestions = SearchSuggestion.objects.filter(
            is_active=True
        ).order_by('-usage_count')[:3]
        
        suggestions.extend([s.text for s in popular_suggestions])
        
        return list(set(suggestions))[:5]
    
    def _get_index_suggestions(self, partial_query: str, limit: int) -> List[Dict[str, Any]]:
        """الحصول على اقتراحات من الفهرس"""
        
        # البحث في العناوين
        titles = SearchIndex.objects.filter(
            title__icontains=partial_query,
            is_active=True
        ).values_list('title', flat=True).distinct()[:limit]
        
        suggestions = []
        for title in titles:
            suggestions.append({
                'text': title,
                'type': 'title',
                'usage_count': 0,
                'success_rate': 0.0,
            })
        
        return suggestions
    
    def _match_context(self, context_filters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """مطابقة السياق"""
        
        for key, expected_value in context_filters.items():
            if key not in context:
                return False
            
            actual_value = context[key]
            
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            elif actual_value != expected_value:
                return False
        
        return True
    
    def _log_search(
        self,
        user: User,
        query: str,
        search_type: str,
        filters: Dict[str, Any],
        result_count: int,
        execution_time: float,
        status: str = 'success'
    ):
        """تسجيل عملية البحث"""
        
        try:
            SearchLog.objects.create(
                user=user,
                query=query,
                search_type=search_type,
                filters_applied=filters or {},
                result_count=result_count,
                result_status=status if result_count > 0 else 'no_results',
                execution_time=execution_time
            )
        except Exception as e:
            logger.error(f"Error logging search: {e}")


class SearchIndexManager:
    """مدير فهرسة البحث"""
    
    def __init__(self):
        self.batch_size = 100
    
    def index_object(self, obj, content_type_name: str = None):
        """فهرسة كائن واحد"""
        
        try:
            content_type = ContentType.objects.get_for_model(obj)
            
            # استخراج البيانات للفهرسة
            index_data = self._extract_index_data(obj, content_type_name or content_type.model)
            
            if not index_data:
                return None
            
            # إنشاء أو تحديث الفهرس
            search_index, created = SearchIndex.objects.update_or_create(
                content_type=content_type,
                object_id=obj.pk,
                defaults=index_data
            )
            
            return search_index
            
        except Exception as e:
            logger.error(f"Error indexing object {obj}: {e}")
            return None
    
    def remove_from_index(self, obj):
        """إزالة كائن من الفهرس"""
        
        try:
            content_type = ContentType.objects.get_for_model(obj)
            SearchIndex.objects.filter(
                content_type=content_type,
                object_id=obj.pk
            ).delete()
        except Exception as e:
            logger.error(f"Error removing object from index {obj}: {e}")
    
    def rebuild_index(self, content_type_name: str = None):
        """إعادة بناء الفهرس"""
        
        if content_type_name:
            # إعادة بناء فهرس نوع محدد
            self._rebuild_content_type_index(content_type_name)
        else:
            # إعادة بناء جميع الفهارس
            content_types = [
                'employee', 'department', 'job', 'company', 'branch',
                'leave_request', 'attendance_record', 'payroll_entry',
                'employee_file', 'evaluation', 'notification'
            ]
            
            for ct in content_types:
                self._rebuild_content_type_index(ct)
    
    def _rebuild_content_type_index(self, content_type_name: str):
        """إعادة بناء فهرس نوع محدد"""
        
        try:
            # حذف الفهارس القديمة
            content_type = ContentType.objects.get(model=content_type_name)
            SearchIndex.objects.filter(content_type=content_type).delete()
            
            # الحصول على النموذج
            model_class = content_type.model_class()
            if not model_class:
                return
            
            # فهرسة جميع الكائنات
            objects = model_class.objects.all()
            
            for i in range(0, objects.count(), self.batch_size):
                batch = objects[i:i + self.batch_size]
                for obj in batch:
                    self.index_object(obj, content_type_name)
            
            logger.info(f"Rebuilt index for {content_type_name}")
            
        except Exception as e:
            logger.error(f"Error rebuilding index for {content_type_name}: {e}")
    
    def _extract_index_data(self, obj, content_type_name: str) -> Dict[str, Any]:
        """استخراج البيانات للفهرسة"""
        
        extractors = {
            'employee': self._extract_employee_data,
            'department': self._extract_department_data,
            'job': self._extract_job_data,
            'company': self._extract_company_data,
            'branch': self._extract_branch_data,
            'leave_request': self._extract_leave_request_data,
            'attendance_record': self._extract_attendance_record_data,
            'payroll_entry': self._extract_payroll_entry_data,
            'employee_file': self._extract_employee_file_data,
            'evaluation': self._extract_evaluation_data,
            'notification': self._extract_notification_data,
        }
        
        extractor = extractors.get(content_type_name)
        if extractor:
            return extractor(obj)
        
        return None
    
    def _extract_employee_data(self, employee) -> Dict[str, Any]:
        """استخراج بيانات الموظف"""
        
        title = f"{employee.full_name} - {employee.employee_number}"
        content = f"{employee.full_name} {employee.employee_number}"
        
        if hasattr(employee, 'job_title') and employee.job_title:
            content += f" {employee.job_title.title}"
        
        if hasattr(employee, 'department') and employee.department:
            content += f" {employee.department.name}"
        
        keywords = [
            employee.full_name,
            employee.employee_number,
            employee.email or '',
            employee.phone_number or '',
        ]
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': getattr(employee, 'company_id', None),
            'department_id': getattr(employee, 'department_id', None),
            'branch_id': getattr(employee, 'branch_id', None),
            'metadata': {
                'employee_number': employee.employee_number,
                'full_name': employee.full_name,
                'email': employee.email,
                'is_active': getattr(employee, 'is_active', True),
            }
        }
    
    def _extract_department_data(self, department) -> Dict[str, Any]:
        """استخراج بيانات القسم"""
        
        title = department.name
        content = f"{department.name} {department.description or ''}"
        
        keywords = [department.name, department.description or '']
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': getattr(department, 'company_id', None),
            'department_id': department.pk,
            'branch_id': getattr(department, 'branch_id', None),
            'metadata': {
                'name': department.name,
                'description': department.description,
                'is_active': getattr(department, 'is_active', True),
            }
        }
    
    def _extract_job_data(self, job) -> Dict[str, Any]:
        """استخراج بيانات الوظيفة"""
        
        title = job.title
        content = f"{job.title} {job.description or ''}"
        
        keywords = [job.title, job.description or '']
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': getattr(job, 'company_id', None),
            'department_id': getattr(job, 'department_id', None),
            'metadata': {
                'title': job.title,
                'description': job.description,
                'is_active': getattr(job, 'is_active', True),
            }
        }
    
    def _extract_company_data(self, company) -> Dict[str, Any]:
        """استخراج بيانات الشركة"""
        
        title = company.name
        content = f"{company.name} {company.description or ''}"
        
        keywords = [company.name, company.description or '']
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': company.pk,
            'metadata': {
                'name': company.name,
                'description': company.description,
                'is_active': getattr(company, 'is_active', True),
            }
        }
    
    def _extract_branch_data(self, branch) -> Dict[str, Any]:
        """استخراج بيانات الفرع"""
        
        title = branch.name
        content = f"{branch.name} {branch.address or ''}"
        
        keywords = [branch.name, branch.address or '']
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': getattr(branch, 'company_id', None),
            'branch_id': branch.pk,
            'metadata': {
                'name': branch.name,
                'address': branch.address,
                'is_active': getattr(branch, 'is_active', True),
            }
        }
    
    def _extract_leave_request_data(self, leave_request) -> Dict[str, Any]:
        """استخراج بيانات طلب الإجازة"""
        
        employee_name = leave_request.employee.full_name if leave_request.employee else ''
        leave_type = leave_request.leave_type.name if hasattr(leave_request, 'leave_type') else ''
        
        title = f"طلب إجازة - {employee_name}"
        content = f"{employee_name} {leave_type} {leave_request.reason or ''}"
        
        keywords = [employee_name, leave_type, leave_request.reason or '']
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': getattr(leave_request.employee, 'company_id', None) if leave_request.employee else None,
            'department_id': getattr(leave_request.employee, 'department_id', None) if leave_request.employee else None,
            'metadata': {
                'employee_name': employee_name,
                'leave_type': leave_type,
                'status': getattr(leave_request, 'status', ''),
                'start_date': leave_request.start_date.isoformat() if hasattr(leave_request, 'start_date') else None,
                'end_date': leave_request.end_date.isoformat() if hasattr(leave_request, 'end_date') else None,
            }
        }
    
    def _extract_attendance_record_data(self, record) -> Dict[str, Any]:
        """استخراج بيانات سجل الحضور"""
        
        employee_name = record.employee.full_name if record.employee else ''
        
        title = f"حضور - {employee_name}"
        content = f"{employee_name} {record.date}"
        
        keywords = [employee_name, str(record.date)]
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': getattr(record.employee, 'company_id', None) if record.employee else None,
            'department_id': getattr(record.employee, 'department_id', None) if record.employee else None,
            'metadata': {
                'employee_name': employee_name,
                'date': record.date.isoformat() if hasattr(record, 'date') else None,
                'check_in': record.check_in.isoformat() if hasattr(record, 'check_in') and record.check_in else None,
                'check_out': record.check_out.isoformat() if hasattr(record, 'check_out') and record.check_out else None,
            }
        }
    
    def _extract_payroll_entry_data(self, entry) -> Dict[str, Any]:
        """استخراج بيانات كشف الراتب"""
        
        employee_name = entry.employee.full_name if entry.employee else ''
        
        title = f"كشف راتب - {employee_name}"
        content = f"{employee_name} {entry.period}"
        
        keywords = [employee_name, str(entry.period)]
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': getattr(entry.employee, 'company_id', None) if entry.employee else None,
            'department_id': getattr(entry.employee, 'department_id', None) if entry.employee else None,
            'metadata': {
                'employee_name': employee_name,
                'period': str(entry.period) if hasattr(entry, 'period') else None,
                'basic_salary': float(entry.basic_salary) if hasattr(entry, 'basic_salary') else None,
                'total_salary': float(entry.total_salary) if hasattr(entry, 'total_salary') else None,
            }
        }
    
    def _extract_employee_file_data(self, file) -> Dict[str, Any]:
        """استخراج بيانات ملف الموظف"""
        
        employee_name = file.employee.full_name if file.employee else ''
        
        title = f"{file.title} - {employee_name}"
        content = f"{file.title} {employee_name} {file.description or ''}"
        
        keywords = [file.title, employee_name, file.description or '']
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': getattr(file.employee, 'company_id', None) if file.employee else None,
            'department_id': getattr(file.employee, 'department_id', None) if file.employee else None,
            'metadata': {
                'employee_name': employee_name,
                'file_title': file.title,
                'file_type': getattr(file, 'file_type', ''),
                'expiry_date': file.expiry_date.isoformat() if hasattr(file, 'expiry_date') and file.expiry_date else None,
            }
        }
    
    def _extract_evaluation_data(self, evaluation) -> Dict[str, Any]:
        """استخراج بيانات التقييم"""
        
        employee_name = evaluation.employee.full_name if evaluation.employee else ''
        
        title = f"تقييم - {employee_name}"
        content = f"{employee_name} {evaluation.comments or ''}"
        
        keywords = [employee_name, evaluation.comments or '']
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'company_id': getattr(evaluation.employee, 'company_id', None) if evaluation.employee else None,
            'department_id': getattr(evaluation.employee, 'department_id', None) if evaluation.employee else None,
            'metadata': {
                'employee_name': employee_name,
                'evaluation_date': evaluation.evaluation_date.isoformat() if hasattr(evaluation, 'evaluation_date') else None,
                'score': float(evaluation.score) if hasattr(evaluation, 'score') else None,
            }
        }
    
    def _extract_notification_data(self, notification) -> Dict[str, Any]:
        """استخراج بيانات الإشعار"""
        
        title = notification.title
        content = f"{notification.title} {notification.message}"
        
        keywords = [notification.title, notification.message]
        
        return {
            'title': title,
            'content': content,
            'keywords': ' '.join(filter(None, keywords)),
            'metadata': {
                'notification_type': notification.notification_type,
                'priority': getattr(notification, 'priority', ''),
                'status': getattr(notification, 'status', ''),
            }
        }