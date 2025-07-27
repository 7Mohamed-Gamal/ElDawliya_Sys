"""
Views للبحث المتقدم والذكي
"""

import json
import time
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib import messages

from ..models_search import (
    SearchIndex, SavedSearch, SearchSuggestion, SearchLog,
    SearchFilter, SmartSearchPattern
)
from ..services.search_service import AdvancedSearchService, SearchIndexManager
from ..models_enhanced import Company, Department


@login_required
def advanced_search_view(request):
    """صفحة البحث المتقدم"""
    
    # الحصول على الشركات والأقسام للفلاتر
    companies = Company.objects.filter(is_active=True).order_by('name')
    departments = Department.objects.filter(is_active=True).order_by('name')
    
    # الحصول على عمليات البحث المحفوظة
    saved_searches = []
    if request.user.is_authenticated:
        saved_searches = SavedSearch.objects.filter(
            Q(user=request.user) | Q(is_public=True)
        ).order_by('-is_favorite', '-last_used_at')[:10]
    
    # تنفيذ البحث إذا كانت هناك معايير
    results = None
    if request.GET.get('q'):
        search_service = AdvancedSearchService()
        
        # جمع معايير البحث
        query = request.GET.get('q', '')
        content_types = request.GET.getlist('content_types')
        filters = {}
        
        # جمع الفلاتر
        for key, value in request.GET.items():
            if key not in ['q', 'content_types', 'page', 'sort_by'] and value:
                filters[key] = value
        
        # تنفيذ البحث
        try:
            results = search_service.search(
                query=query,
                user=request.user,
                content_types=content_types,
                filters=filters,
                page=int(request.GET.get('page', 1)),
                page_size=20,
                sort_by=request.GET.get('sort_by', 'relevance'),
                search_type='advanced'
            )
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء البحث: {str(e)}')
    
    context = {
        'companies': companies,
        'departments': departments,
        'saved_searches': saved_searches,
        'results': results,
    }
    
    return render(request, 'Hr/search/advanced_search.html', context)


@login_required
@require_http_methods(["GET"])
def search_api(request):
    """API البحث"""
    
    try:
        search_service = AdvancedSearchService()
        
        # جمع معايير البحث
        query = request.GET.get('q', '')
        content_types = request.GET.getlist('content_types')
        filters = {}
        
        # جمع الفلاتر
        for key, value in request.GET.items():
            if key not in ['q', 'content_types', 'page', 'sort_by'] and value:
                filters[key] = value
        
        # تنفيذ البحث
        results = search_service.search(
            query=query,
            user=request.user,
            content_types=content_types,
            filters=filters,
            page=int(request.GET.get('page', 1)),
            page_size=20,
            sort_by=request.GET.get('sort_by', 'relevance'),
            search_type='api'
        )
        
        return JsonResponse(results)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'results': [],
            'total_count': 0
        }, status=500)


@login_required
@require_http_methods(["GET"])
def search_suggestions_api(request):
    """API اقتراحات البحث"""
    
    try:
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 10))
        
        if not query or len(query) < 2:
            return JsonResponse([])
        
        search_service = AdvancedSearchService()
        suggestions = search_service.get_suggestions(
            partial_query=query,
            user=request.user,
            limit=limit
        )
        
        return JsonResponse(suggestions, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def smart_search_api(request):
    """API البحث الذكي"""
    
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        context = data.get('context', {})
        
        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)
        
        search_service = AdvancedSearchService()
        results = search_service.smart_search(
            query=query,
            user=request.user,
            context=context
        )
        
        return JsonResponse(results)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def save_search_api(request):
    """API حفظ البحث"""
    
    try:
        data = json.loads(request.body)
        
        # التحقق من البيانات المطلوبة
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'error': 'اسم البحث مطلوب'}, status=400)
        
        # التحقق من عدم تكرار الاسم
        if SavedSearch.objects.filter(user=request.user, name=name).exists():
            return JsonResponse({'error': 'يوجد بحث محفوظ بنفس الاسم'}, status=400)
        
        search_service = AdvancedSearchService()
        saved_search = search_service.save_search(
            user=request.user,
            name=name,
            query=data.get('query', ''),
            filters=data.get('filters', {}),
            content_types=data.get('content_types', []),
            search_type=data.get('search_type', 'advanced'),
            description=data.get('description', ''),
            is_public=data.get('is_public', False)
        )
        
        return JsonResponse({
            'success': True,
            'search_id': str(saved_search.id),
            'message': 'تم حفظ البحث بنجاح'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def saved_searches_api(request):
    """API عمليات البحث المحفوظة"""
    
    try:
        search_service = AdvancedSearchService()
        saved_searches = search_service.get_saved_searches(
            user=request.user,
            include_public=True
        )
        
        # تحويل إلى JSON
        searches_data = []
        for search in saved_searches:
            searches_data.append({
                'id': str(search.id),
                'name': search.name,
                'description': search.description,
                'search_type': search.search_type,
                'usage_count': search.usage_count,
                'last_used_at': search.last_used_at.isoformat() if search.last_used_at else None,
                'is_favorite': search.is_favorite,
                'is_public': search.is_public,
                'can_delete': search.user == request.user,
                'created_at': search.created_at.isoformat(),
            })
        
        return JsonResponse(searches_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def execute_saved_search_api(request, search_id):
    """API تنفيذ بحث محفوظ"""
    
    try:
        saved_search = get_object_or_404(SavedSearch, id=search_id)
        
        # التحقق من الصلاحيات
        if saved_search.user != request.user and not saved_search.is_public:
            return JsonResponse({'error': 'ليس لديك صلاحية لتنفيذ هذا البحث'}, status=403)
        
        search_service = AdvancedSearchService()
        results = search_service.execute_saved_search(
            saved_search=saved_search,
            user=request.user,
            page=int(request.GET.get('page', 1)),
            page_size=20
        )
        
        # إضافة معايير البحث للاستجابة
        results['search_criteria'] = {
            'query': saved_search.query,
            'filters': saved_search.filters,
            'content_types': saved_search.content_types,
        }
        
        return JsonResponse(results)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["DELETE"])
def delete_saved_search_api(request, search_id):
    """API حذف بحث محفوظ"""
    
    try:
        saved_search = get_object_or_404(SavedSearch, id=search_id, user=request.user)
        saved_search.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'تم حذف البحث المحفوظ بنجاح'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def toggle_favorite_search(request, search_id):
    """تبديل حالة المفضلة للبحث المحفوظ"""
    
    try:
        saved_search = get_object_or_404(SavedSearch, id=search_id, user=request.user)
        saved_search.is_favorite = not saved_search.is_favorite
        saved_search.save(update_fields=['is_favorite'])
        
        return JsonResponse({
            'success': True,
            'is_favorite': saved_search.is_favorite,
            'message': 'تم تحديث حالة المفضلة'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def search_analytics_view(request):
    """صفحة تحليلات البحث"""
    
    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.view_searchlog'):
        messages.error(request, 'ليس لديك صلاحية لعرض تحليلات البحث')
        return redirect('hr:dashboard')
    
    days = int(request.GET.get('days', 30))
    
    search_service = AdvancedSearchService()
    analytics = search_service.get_search_analytics(
        user=request.user if not request.user.is_superuser else None,
        days=days
    )
    
    context = {
        'analytics': analytics,
        'days': days,
    }
    
    return render(request, 'Hr/search/analytics.html', context)


@login_required
def search_management_view(request):
    """صفحة إدارة البحث"""
    
    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.change_searchfilter'):
        messages.error(request, 'ليس لديك صلاحية لإدارة البحث')
        return redirect('hr:dashboard')
    
    # الحصول على الفلاتر والأنماط
    search_filters = SearchFilter.objects.all().order_by('order', 'name')
    smart_patterns = SmartSearchPattern.objects.all().order_by('-priority', 'pattern')
    suggestions = SearchSuggestion.objects.filter(is_active=True).order_by('-usage_count')[:20]
    
    context = {
        'search_filters': search_filters,
        'smart_patterns': smart_patterns,
        'suggestions': suggestions,
    }
    
    return render(request, 'Hr/search/management.html', context)


@login_required
@require_http_methods(["POST"])
def rebuild_search_index(request):
    """إعادة بناء فهرس البحث"""
    
    # التحقق من الصلاحيات
    if not request.user.is_superuser:
        return JsonResponse({'error': 'ليس لديك صلاحية لإعادة بناء الفهرس'}, status=403)
    
    try:
        content_type = request.POST.get('content_type')
        
        index_manager = SearchIndexManager()
        index_manager.rebuild_index(content_type)
        
        return JsonResponse({
            'success': True,
            'message': f'تم إعادة بناء فهرس البحث {"لـ " + content_type if content_type else "بالكامل"}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_search_filter(request):
    """إنشاء فلتر بحث جديد"""
    
    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.add_searchfilter'):
        return JsonResponse({'error': 'ليس لديك صلاحية لإنشاء فلاتر البحث'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        search_filter = SearchFilter.objects.create(
            name=data['name'],
            field_name=data['field_name'],
            display_name=data['display_name'],
            filter_type=data['filter_type'],
            supported_operators=data.get('supported_operators', []),
            choices=data.get('choices', []),
            content_types=data.get('content_types', []),
            description=data.get('description', ''),
            help_text=data.get('help_text', ''),
            order=data.get('order', 0)
        )
        
        return JsonResponse({
            'success': True,
            'filter_id': str(search_filter.id),
            'message': 'تم إنشاء الفلتر بنجاح'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_smart_pattern(request):
    """إنشاء نمط بحث ذكي جديد"""
    
    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.add_smartsearchpattern'):
        return JsonResponse({'error': 'ليس لديك صلاحية لإنشاء أنماط البحث الذكي'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        pattern = SmartSearchPattern.objects.create(
            pattern=data['pattern'],
            replacement=data['replacement'],
            pattern_type=data['pattern_type'],
            weight=data.get('weight', 1.0),
            priority=data.get('priority', 0),
            context_filters=data.get('context_filters', {}),
            is_case_sensitive=data.get('is_case_sensitive', False)
        )
        
        return JsonResponse({
            'success': True,
            'pattern_id': str(pattern.id),
            'message': 'تم إنشاء النمط بنجاح'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def export_search_data(request):
    """تصدير بيانات البحث"""
    
    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.view_searchlog'):
        return JsonResponse({'error': 'ليس لديك صلاحية لتصدير بيانات البحث'}, status=403)
    
    try:
        export_type = request.GET.get('type', 'logs')
        days = int(request.GET.get('days', 30))
        
        if export_type == 'logs':
            # تصدير سجلات البحث
            start_date = timezone.now() - timezone.timedelta(days=days)
            logs = SearchLog.objects.filter(
                created_at__gte=start_date
            ).order_by('-created_at')
            
            if not request.user.is_superuser:
                logs = logs.filter(user=request.user)
            
            # تحويل إلى CSV
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="search_logs_{days}days.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'التاريخ', 'المستخدم', 'الاستعلام', 'نوع البحث', 
                'عدد النتائج', 'وقت التنفيذ', 'الحالة'
            ])
            
            for log in logs:
                writer.writerow([
                    log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    log.user.get_full_name() if log.user else 'مجهول',
                    log.query,
                    log.get_search_type_display(),
                    log.result_count,
                    f'{log.execution_time:.3f}s',
                    log.get_result_status_display()
                ])
            
            return response
            
        elif export_type == 'analytics':
            # تصدير التحليلات
            search_service = AdvancedSearchService()
            analytics = search_service.get_search_analytics(
                user=request.user if not request.user.is_superuser else None,
                days=days
            )
            
            return JsonResponse(analytics)
        
        else:
            return JsonResponse({'error': 'نوع التصدير غير مدعوم'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def simple_search_view(request):
    """البحث البسيط (للمستخدمين غير المسجلين)"""
    
    results = None
    if request.GET.get('q'):
        search_service = AdvancedSearchService()
        
        try:
            results = search_service.search(
                query=request.GET.get('q', ''),
                user=request.user if request.user.is_authenticated else None,
                page=int(request.GET.get('page', 1)),
                page_size=20,
                search_type='simple'
            )
        except Exception as e:
            if request.user.is_authenticated:
                messages.error(request, f'حدث خطأ أثناء البحث: {str(e)}')
    
    context = {
        'results': results,
        'is_simple_search': True,
    }
    
    return render(request, 'Hr/search/simple_search.html', context)