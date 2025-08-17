"""
عروض إدارة التخزين المؤقت
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import json

from ..services.cache_service import cache_service
from ..services.cache_monitor import cache_monitor
from ..decorators import hr_permission_required


@login_required
@hr_permission_required('admin.cache_management')
def cache_dashboard(request):
    """لوحة تحكم التخزين المؤقت"""
    
    # الحصول على الإحصائيات
    stats = cache_service.get_stats()
    real_time_stats = cache_monitor.get_real_time_stats()
    alerts = cache_monitor.get_alerts(limit=10)
    
    context = {
        'stats': stats,
        'real_time_stats': real_time_stats,
        'alerts': alerts,
        'page_title': 'إدارة التخزين المؤقت'
    }
    
    return render(request, 'Hr/cache/dashboard.html', context)


@login_required
@hr_permission_required('admin.cache_management')
def cache_stats_api(request):
    """API إحصائيات التخزين المؤقت"""
    
    time_range_hours = int(request.GET.get('hours', 1))
    time_range = timedelta(hours=time_range_hours)
    
    stats = cache_monitor.get_stats(time_range)
    
    return JsonResponse({
        'success': True,
        'stats': stats,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@hr_permission_required('admin.cache_management')
@require_http_methods(["POST"])
def invalidate_cache(request):
    """إبطال التخزين المؤقت"""
    
    try:
        data = json.loads(request.body)
        tags = data.get('tags', [])
        
        if not tags:
            return JsonResponse({
                'success': False,
                'message': 'لا توجد علامات للإبطال'
            })
        
        count = cache_service.invalidate_by_tags(tags)
        
        return JsonResponse({
            'success': True,
            'message': f'تم إبطال {count} عنصر',
            'invalidated_count': count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في الإبطال: {str(e)}'
        })


@login_required
@hr_permission_required('admin.cache_management')
@require_http_methods(["POST"])
def warm_up_cache(request):
    """تسخين التخزين المؤقت"""
    
    try:
        from ..tasks.cache_tasks import warm_up_cache
        
        # تشغيل مهمة التسخين
        task = warm_up_cache.delay()
        
        return JsonResponse({
            'success': True,
            'message': 'تم بدء تسخين التخزين المؤقت',
            'task_id': task.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في التسخين: {str(e)}'
        })