"""
الخدمة الأساسية المشتركة
Base Service for all business logic services
"""
import logging
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from core.models.audit import AuditLog


class BaseService:
    """
    الخدمة الأساسية المشتركة لجميع خدمات الأعمال
    Base service class with common functionality for all business services
    """
    
    def __init__(self, user=None, request=None):
        self.user = user
        self.request = request
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def log_action(self, action, resource, content_object=None, 
                   old_values=None, new_values=None, details=None, 
                   result='success', message=None):
        """
        تسجيل عمل المستخدم
        Log user action for audit trail
        """
        return AuditLog.log_action(
            user=self.user,
            action=action,
            resource=resource,
            content_object=content_object,
            old_values=old_values,
            new_values=new_values,
            details=details,
            result=result,
            message=message,
            request=self.request
        )
    
    def check_permission(self, permission, obj=None):
        """
        فحص صلاحية المستخدم
        Check if user has required permission
        """
        if not self.user:
            raise PermissionDenied("المستخدم غير محدد")
            
        if not self.user.is_authenticated:
            raise PermissionDenied("المستخدم غير مسجل الدخول")
            
        if not self.user.has_perm(permission, obj):
            raise PermissionDenied(f"لا تملك صلاحية {permission}")
    
    def check_object_permission(self, permission, obj):
        """
        فحص صلاحية على كائن محدد
        Check object-level permission
        """
        self.check_permission(permission, obj)
    
    def get_user_context(self):
        """
        الحصول على سياق المستخدم
        Get user context information
        """
        if not self.user:
            return {}
            
        return {
            'user_id': self.user.id,
            'username': self.user.username,
            'full_name': self.user.get_full_name(),
            'email': self.user.email,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
    
    def validate_required_fields(self, data, required_fields):
        """
        التحقق من الحقول المطلوبة
        Validate required fields in data
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"الحقول التالية مطلوبة: {', '.join(missing_fields)}")
    
    def clean_data(self, data, allowed_fields=None):
        """
        تنظيف البيانات
        Clean and filter data based on allowed fields
        """
        if allowed_fields is None:
            return data
            
        cleaned_data = {}
        for field in allowed_fields:
            if field in data:
                cleaned_data[field] = data[field]
                
        return cleaned_data
    
    def handle_exception(self, exception, action, resource, details=None):
        """
        التعامل مع الاستثناءات
        Handle exceptions and log them
        """
        error_message = str(exception)
        self.logger.error(f"خطأ في {action} - {resource}: {error_message}")
        
        # Log the error
        self.log_action(
            action=action,
            resource=resource,
            details=details,
            result='failure',
            message=error_message
        )
        
        # Re-raise the exception
        raise exception
    
    @transaction.atomic
    def execute_with_transaction(self, func, *args, **kwargs):
        """
        تنفيذ دالة داخل معاملة قاعدة بيانات
        Execute function within database transaction
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"خطأ في المعاملة: {str(e)}")
            raise
    
    def paginate_queryset(self, queryset, page=1, page_size=20):
        """
        تقسيم النتائج إلى صفحات
        Paginate queryset results
        """
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            
        return {
            'results': page_obj.object_list,
            'page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    
    def format_response(self, data=None, message=None, success=True, errors=None):
        """
        تنسيق الاستجابة
        Format service response
        """
        response = {
            'success': success,
            'message': message,
            'data': data,
        }
        
        if errors:
            response['errors'] = errors
            
        return response
    
    def get_model_changes(self, instance, new_data):
        """
        الحصول على التغييرات في النموذج
        Get model changes for audit logging
        """
        old_values = {}
        new_values = {}
        
        for field, new_value in new_data.items():
            if hasattr(instance, field):
                old_value = getattr(instance, field)
                if old_value != new_value:
                    old_values[field] = old_value
                    new_values[field] = new_value
        
        return old_values, new_values
    
    def send_notification(self, recipient, template_name, context=None, channels=None):
        """
        إرسال إشعار
        Send notification using notification service
        """
        from .notifications import NotificationService
        
        notification_service = NotificationService()
        return notification_service.send_notification(
            recipient=recipient,
            template_name=template_name,
            context=context,
            channels=channels
        )
    
    def cache_key(self, *args):
        """
        إنشاء مفتاح التخزين المؤقت
        Generate cache key
        """
        service_name = self.__class__.__name__.lower()
        return f"{service_name}:{'_'.join(str(arg) for arg in args)}"
    
    def get_from_cache(self, key, default=None):
        """
        الحصول على قيمة من التخزين المؤقت
        Get value from cache
        """
        from django.core.cache import cache
        return cache.get(key, default)
    
    def set_cache(self, key, value, timeout=300):
        """
        تعيين قيمة في التخزين المؤقت
        Set value in cache
        """
        from django.core.cache import cache
        cache.set(key, value, timeout)
    
    def invalidate_cache(self, pattern):
        """
        إبطال التخزين المؤقت
        Invalidate cache by pattern
        """
        from .cache import CacheService
        CacheService.invalidate_pattern(pattern)