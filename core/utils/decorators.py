"""
مزخرفات مخصصة
Custom decorators for common functionality
"""
import functools
import time
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.cache import cache
from core.models.audit import AuditLog


def require_permission(permission, obj_param=None):
    """
    مزخرف للتحقق من الصلاحيات
    Decorator to check user permissions
    """
    def decorator(view_func):
        """decorator function"""
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """wrapper function"""
            if not request.user.is_authenticated:
                raise PermissionDenied("المستخدم غير مسجل الدخول")

            # Get object if obj_param is specified
            obj = None
            if obj_param and obj_param in kwargs:
                # This would need to be implemented based on your models
                pass

            if not request.user.has_perm(permission, obj):
                raise PermissionDenied(f"لا تملك صلاحية {permission}")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_action(action, resource=None, get_object=None):
    """
    مزخرف لتسجيل أعمال المستخدم
    Decorator to log user actions
    """
    def decorator(view_func):
        """decorator function"""
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """wrapper function"""
            start_time = time.time()

            try:
                # Execute the view
                response = view_func(request, *args, **kwargs)

                # Calculate duration
                duration = time.time() - start_time

                # Get object if function provided
                obj = None
                if get_object and callable(get_object):
                    try:
                        obj = get_object(request, *args, **kwargs)
                    except:
                        pass

                # Determine resource name
                resource_name = resource or f"{view_func.__module__}.{view_func.__name__}"

                # Log successful action
                AuditLog.log_action(
                    user=request.user if request.user.is_authenticated else None,
                    action=action,
                    resource=resource_name,
                    content_object=obj,
                    result='success',
                    request=request
                )

                return response

            except Exception as e:
                # Calculate duration
                duration = time.time() - start_time

                # Log failed action
                AuditLog.log_action(
                    user=request.user if request.user.is_authenticated else None,
                    action=action,
                    resource=resource or f"{view_func.__module__}.{view_func.__name__}",
                    result='failure',
                    message=str(e),
                    request=request
                )

                # Re-raise the exception
                raise

        return wrapper
    return decorator


def cache_result(timeout=300, key_func=None, vary_on_user=False):
    """
    مزخرف للتخزين المؤقت للنتائج
    Decorator to cache function results
    """
    def decorator(view_func):
        """decorator function"""
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """wrapper function"""
            # Generate cache key
            if key_func and callable(key_func):
                cache_key = key_func(request, *args, **kwargs)
            else:
                cache_key = f"{view_func.__module__}.{view_func.__name__}"
                if args:
                    cache_key += f":{':'.join(str(arg) for arg in args)}"
                if kwargs:
                    cache_key += f":{':'.join(f'{k}={v}' for k, v in kwargs.items())}"

            # Add user to cache key if specified
            if vary_on_user and request.user.is_authenticated:
                cache_key += f":user_{request.user.id}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = view_func(request, *args, **kwargs)
            cache.set(cache_key, result, timeout)

            return result

        return wrapper
    return decorator


def ajax_required(view_func):
    """
    مزخرف للتأكد من أن الطلب AJAX
    Decorator to ensure request is AJAX
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        """wrapper function"""
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'هذا الطلب يتطلب AJAX'
            }, status=400)

        return view_func(request, *args, **kwargs)
    return wrapper


def json_response(view_func):
    """
    مزخرف لتحويل الاستجابة إلى JSON
    Decorator to convert response to JSON
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        """wrapper function"""
        try:
            result = view_func(request, *args, **kwargs)

            # If already a JsonResponse, return as is
            if isinstance(result, JsonResponse):
                return result

            # If it's a dict, convert to JsonResponse
            if isinstance(result, dict):
                return JsonResponse(result)

            # Otherwise, wrap in success response
            return JsonResponse({
                'success': True,
                'data': result
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    return wrapper


def rate_limit(max_requests=60, window=60):
    """
    مزخرف للحد من معدل الطلبات
    Decorator for rate limiting
    """
    def decorator(view_func):
        """decorator function"""
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """wrapper function"""
            # Get client IP
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or \
                 request.META.get('REMOTE_ADDR', '')

            # Create cache key
            cache_key = f"rate_limit:{ip}:{view_func.__name__}"

            # Get current count
            current_count = cache.get(cache_key, 0)

            if current_count >= max_requests:
                return JsonResponse({
                    'success': False,
                    'message': 'تم تجاوز الحد المسموح من الطلبات'
                }, status=429)

            # Increment count
            cache.set(cache_key, current_count + 1, window)

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def transaction_atomic(view_func):
    """
    مزخرف لتنفيذ العملية في معاملة قاعدة بيانات
    Decorator to execute view in database transaction
    """
    from django.db import transaction

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        """wrapper function"""
        with transaction.atomic():
            return view_func(request, *args, **kwargs)
    return wrapper


def measure_performance(view_func):
    """
    مزخرف لقياس أداء الدالة
    Decorator to measure function performance
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        """wrapper function"""
        start_time = time.time()

        result = view_func(request, *args, **kwargs)

        end_time = time.time()
        duration = end_time - start_time

        # Log performance if it's slow
        if duration > 1.0:  # More than 1 second
            import logging
            logger = logging.getLogger('performance')
            logger.warning(
                f"Slow view: {view_func.__name__} took {duration:.2f} seconds"
            )

        return result
    return wrapper


def staff_required(view_func):
    """
    مزخرف للتأكد من أن المستخدم موظف
    Decorator to ensure user is staff
    """
    @login_required
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        """wrapper function"""
        if not request.user.is_staff:
            raise PermissionDenied("هذه الصفحة مخصصة للموظفين فقط")

        return view_func(request, *args, **kwargs)
    return wrapper


def superuser_required(view_func):
    """
    مزخرف للتأكد من أن المستخدم مدير عام
    Decorator to ensure user is superuser
    """
    @login_required
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        """wrapper function"""
        if not request.user.is_superuser:
            raise PermissionDenied("هذه الصفحة مخصصة للمديرين العامين فقط")

        return view_func(request, *args, **kwargs)
    return wrapper


def handle_exceptions(default_response=None):
    """
    مزخرف للتعامل مع الاستثناءات
    Decorator to handle exceptions gracefully
    """
    def decorator(view_func):
        """decorator function"""
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """wrapper function"""
            try:
                return view_func(request, *args, **kwargs)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.exception(f"Error in {view_func.__name__}: {e}")

                if default_response:
                    return default_response

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'حدث خطأ غير متوقع'
                    }, status=500)

                from django.shortcuts import render
                return render(request, 'error.html', {
                    'error_message': 'حدث خطأ غير متوقع'
                }, status=500)

        return wrapper
    return decorator


def validate_request_data(required_fields=None, optional_fields=None):
    """
    مزخرف للتحقق من بيانات الطلب
    Decorator to validate request data
    """
    def decorator(view_func):
        """decorator function"""
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """wrapper function"""
            # Get data based on request method
            if request.method == 'POST':
                data = request.POST
            elif request.method in ['PUT', 'PATCH']:
                import json
                try:
                    data = json.loads(request.body)
                except:
                    data = request.POST
            else:
                data = request.GET

            # Check required fields
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or not data[field]:
                        missing_fields.append(field)

                if missing_fields:
                    return JsonResponse({
                        'success': False,
                        'message': f'الحقول التالية مطلوبة: {", ".join(missing_fields)}'
                    }, status=400)

            # Filter allowed fields
            if optional_fields or required_fields:
                allowed_fields = (required_fields or []) + (optional_fields or [])
                filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
                request.validated_data = filtered_data

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
