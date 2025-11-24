"""
Cache Monitoring Views
====================

Views for monitoring cache performance and statistics
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import json

from core.services.cache_service import (
    cache_service,
    cache_performance_monitor,
    CacheService
)
from core.services.query_optimizer import (
    performance_monitor,
    index_analyzer
)


@staff_member_required
def cache_dashboard(request):
    """لوحة تحكم مراقبة التخزين المؤقت"""

    context = {
        'title': 'مراقبة التخزين المؤقت',
        'cache_backend': 'Redis' if hasattr(settings, 'REDIS_URL') else 'Database',
        'current_time': timezone.now(),
    }

    return render(request, 'core/cache_dashboard.html', context)


@staff_member_required
def cache_stats_api(request):
    """API لإحصائيات التخزين المؤقت"""

    try:
        # Get cache service stats
        cache_stats = cache_service.get_stats()

        # Get performance monitor stats
        performance_stats = cache_performance_monitor.get_performance_stats()

        # Get query performance stats
        query_stats = performance_monitor.get_query_stats()

        # Get index recommendations
        index_suggestions = index_analyzer.suggest_index_optimizations()

        data = {
            'cache_stats': cache_stats,
            'performance_stats': performance_stats,
            'query_stats': query_stats,
            'index_suggestions': index_suggestions[:5],  # Top 5 suggestions
            'timestamp': timezone.now().isoformat(),
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@staff_member_required
def slow_queries_api(request):
    """API للاستعلامات البطيئة"""

    try:
        slow_queries = performance_monitor.get_slow_queries(limit=20)

        data = {
            'slow_queries': slow_queries,
            'total_count': len(slow_queries),
            'timestamp': timezone.now().isoformat(),
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@staff_member_required
def cache_operations_api(request):
    """API لعمليات التخزين المؤقت"""

    if request.method == 'POST':
        operation = request.POST.get('operation')

        try:
            if operation == 'clear_all':
                cache_service.clear_all()
                return JsonResponse({
                    'success': True,
                    'message': 'تم مسح جميع البيانات المخزنة مؤقتاً'
                })

            elif operation == 'clear_pattern':
                pattern = request.POST.get('pattern', '')
                if pattern:
                    deleted_count = cache_service.delete_pattern(pattern)
                    return JsonResponse({
                        'success': True,
                        'message': f'تم مسح {deleted_count} مفتاح مطابق للنمط {pattern}'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'يجب تحديد النمط'
                    })

            elif operation == 'reset_stats':
                cache_performance_monitor.reset_stats()
                return JsonResponse({
                    'success': True,
                    'message': 'تم إعادة تعيين إحصائيات الأداء'
                })

            elif operation == 'warm_cache':
                # Warm up common cache entries
                warm_cache_entries()
                return JsonResponse({
                    'success': True,
                    'message': 'تم تسخين التخزين المؤقت'
                })

            else:
                return JsonResponse({
                    'success': False,
                    'message': 'عملية غير مدعومة'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطأ في تنفيذ العملية: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'طريقة غير مدعومة'
    })


@staff_member_required
def cache_key_browser(request):
    """متصفح مفاتيح التخزين المؤقت"""

    pattern = request.GET.get('pattern', '*')
    limit = int(request.GET.get('limit', 100))

    try:
        # This would work with Redis
        if hasattr(cache_service, 'redis_client') and cache_service.redis_client:
            keys = cache_service.redis_client.keys(f"*{pattern}*")[:limit]

            key_data = []
            for key in keys:
                try:
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                    ttl = cache_service.redis_client.ttl(key)
                    size = len(cache_service.redis_client.get(key) or b'')

                    key_data.append({
                        'key': key_str,
                        'ttl': ttl,
                        'size': size,
                        'expires_at': (timezone.now() + timedelta(seconds=ttl)).isoformat() if ttl > 0 else None
                    })
                except Exception:
                    continue

            return JsonResponse({
                'keys': key_data,
                'total_found': len(keys),
                'pattern': pattern,
                'timestamp': timezone.now().isoformat(),
            })
        else:
            return JsonResponse({
                'keys': [],
                'total_found': 0,
                'pattern': pattern,
                'message': 'Key browsing not available with current cache backend',
                'timestamp': timezone.now().isoformat(),
            })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


def warm_cache_entries():
    """تسخين مدخلات التخزين المؤقت الشائعة"""

    try:
        # Warm up dashboard stats
        from core.services.query_optimizer import get_dashboard_stats_cached
        get_dashboard_stats_cached()

        # Warm up common lookups
        try:
            from employees.models import Department, JobPosition

            # Cache departments
            departments = list(Department.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.values())
            cache_service.set('departments_list', departments, 'daily')

            # Cache job positions
            positions = list(JobPosition.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.values())
            cache_service.set('job_positions_list', positions, 'daily')

        except ImportError:
            pass

        # Warm up system settings
        try:
            from inventory.models import SystemSettings
            settings_obj = SystemSettings.get_settings()
            cache_service.set('system_settings', {
                'language': settings_obj.language,
                'font_family': settings_obj.font_family,
                'text_direction': settings_obj.text_direction,
            }, 'daily')
        except ImportError:
            pass

    except Exception as e:
        print(f"Error warming cache: {e}")


@staff_member_required
def cache_health_check(request):
    """فحص صحة التخزين المؤقت"""

    health_status = {
        'overall_status': 'healthy',
        'checks': [],
        'timestamp': timezone.now().isoformat(),
    }

    # Test basic cache operations
    try:
        test_key = 'health_check_test'
        test_value = 'test_value_' + str(timezone.now().timestamp())

        # Test set
        cache_service.set(test_key, test_value, 'short')

        # Test get
        retrieved_value = cache_service.get(test_key)

        if retrieved_value == test_value:
            health_status['checks'].append({
                'name': 'Basic Operations',
                'status': 'pass',
                'message': 'Cache read/write operations working correctly'
            })
        else:
            health_status['checks'].append({
                'name': 'Basic Operations',
                'status': 'fail',
                'message': 'Cache read/write test failed'
            })
            health_status['overall_status'] = 'unhealthy'

        # Clean up
        cache_service.delete(test_key)

    except Exception as e:
        health_status['checks'].append({
            'name': 'Basic Operations',
            'status': 'fail',
            'message': f'Cache operations failed: {str(e)}'
        })
        health_status['overall_status'] = 'unhealthy'

    # Test Redis connection if available
    if hasattr(cache_service, 'redis_client') and cache_service.redis_client:
        try:
            cache_service.redis_client.ping()
            health_status['checks'].append({
                'name': 'Redis Connection',
                'status': 'pass',
                'message': 'Redis connection is healthy'
            })
        except Exception as e:
            health_status['checks'].append({
                'name': 'Redis Connection',
                'status': 'fail',
                'message': f'Redis connection failed: {str(e)}'
            })
            health_status['overall_status'] = 'unhealthy'

    # Check cache performance
    try:
        perf_stats = cache_performance_monitor.get_performance_stats()
        hit_ratio = perf_stats.get('hit_ratio', 0)

        if hit_ratio >= 80:
            status = 'pass'
            message = f'Good cache hit ratio: {hit_ratio:.1f}%'
        elif hit_ratio >= 60:
            status = 'warning'
            message = f'Moderate cache hit ratio: {hit_ratio:.1f}%'
        else:
            status = 'fail'
            message = f'Low cache hit ratio: {hit_ratio:.1f}%'
            if health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'degraded'

        health_status['checks'].append({
            'name': 'Cache Performance',
            'status': status,
            'message': message
        })

    except Exception as e:
        health_status['checks'].append({
            'name': 'Cache Performance',
            'status': 'warning',
            'message': f'Could not check performance: {str(e)}'
        })

    return JsonResponse(health_status)
