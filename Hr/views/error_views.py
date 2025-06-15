# =============================================================================
# ElDawliya HR Management System - Error Views
# =============================================================================
# Custom error handlers for the HR application
# =============================================================================

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.cache import never_cache

@requires_csrf_token
@never_cache
def handler400(request, exception=None):
    """معالج خطأ 400 - طلب غير صحيح"""
    context = {
        'error_code': 400,
        'error_title': 'طلب غير صحيح',
        'error_message': 'الطلب الذي أرسلته غير صحيح أو غير مكتمل.',
        'error_description': 'يرجى التحقق من البيانات المرسلة والمحاولة مرة أخرى.',
    }
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse(context, status=400)
    
    return render(request, 'Hr/errors/400.html', context, status=400)

@requires_csrf_token
@never_cache
def handler403(request, exception=None):
    """معالج خطأ 403 - ممنوع"""
    context = {
        'error_code': 403,
        'error_title': 'غير مسموح',
        'error_message': 'ليس لديك صلاحية للوصول إلى هذه الصفحة.',
        'error_description': 'يرجى التواصل مع مدير النظام للحصول على الصلاحيات المطلوبة.',
    }
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse(context, status=403)
    
    return render(request, 'Hr/errors/403.html', context, status=403)

@requires_csrf_token
@never_cache
def handler404(request, exception=None):
    """معالج خطأ 404 - الصفحة غير موجودة"""
    context = {
        'error_code': 404,
        'error_title': 'الصفحة غير موجودة',
        'error_message': 'الصفحة التي تبحث عنها غير موجودة.',
        'error_description': 'قد تكون الصفحة قد تم نقلها أو حذفها، أو أن الرابط غير صحيح.',
    }
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse(context, status=404)
    
    return render(request, 'Hr/errors/404.html', context, status=404)

@requires_csrf_token
@never_cache
def handler500(request):
    """معالج خطأ 500 - خطأ في الخادم"""
    context = {
        'error_code': 500,
        'error_title': 'خطأ في الخادم',
        'error_message': 'حدث خطأ غير متوقع في الخادم.',
        'error_description': 'نعتذر عن هذا الخطأ. يرجى المحاولة مرة أخرى لاحقاً أو التواصل مع الدعم الفني.',
    }
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse(context, status=500)
    
    return render(request, 'Hr/errors/500.html', context, status=500)
