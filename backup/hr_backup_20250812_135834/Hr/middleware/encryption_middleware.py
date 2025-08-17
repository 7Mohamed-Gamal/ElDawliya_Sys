"""
Middleware للتشفير والأمان
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse
from Hr.services.encryption_service import encryption_service
import json

logger = logging.getLogger(__name__)


class DataEncryptionMiddleware(MiddlewareMixin):
    """
    Middleware لتشفير البيانات الحساسة في الطلبات والاستجابات
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enable_encryption = getattr(settings, 'ENABLE_DATA_ENCRYPTION', True)
        self.sensitive_fields = getattr(settings, 'SENSITIVE_FIELDS', [
            'national_id', 'phone_number', 'mobile_number', 
            'personal_email', 'salary', 'bank_account'
        ])
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة الطلب الوارد"""
        if not self.enable_encryption:
            return None
        
        # تشفير البيانات الحساسة في POST data
        if request.method == 'POST' and request.content_type == 'application/json':
            try:
                if hasattr(request, 'body') and request.body:
                    data = json.loads(request.body.decode('utf-8'))
                    
                    # تشفير البيانات الحساسة
                    encrypted_data = self.encrypt_request_data(data)
                    
                    # تحديث body الطلب
                    request._body = json.dumps(encrypted_data).encode('utf-8')
            
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f'خطأ في معالجة بيانات الطلب: {e}')
        
        return None
    
    def process_response(self, request, response):
        """معالجة الاستجابة"""
        if not self.enable_encryption:
            return response
        
        # فك تشفير البيانات في الاستجابة للعرض
        if (response.get('Content-Type', '').startswith('application/json') and 
            hasattr(response, 'content')):
            try:
                data = json.loads(response.content.decode('utf-8'))
                
                # فك تشفير البيانات للعرض
                decrypted_data = self.decrypt_response_data(data)
                
                # تحديث محتوى الاستجابة
                response.content = json.dumps(decrypted_data, ensure_ascii=False).encode('utf-8')
                response['Content-Length'] = str(len(response.content))
            
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f'خطأ في معالجة بيانات الاستجابة: {e}')
        
        return response
    
    def encrypt_request_data(self, data):
        """تشفير البيانات الحساسة في الطلب"""
        if isinstance(data, dict):
            encrypted_data = {}
            for key, value in data.items():
                if key in self.sensitive_fields and value:
                    encrypted_data[key] = self.encrypt_field_value(key, value)
                elif isinstance(value, (dict, list)):
                    encrypted_data[key] = self.encrypt_request_data(value)
                else:
                    encrypted_data[key] = value
            return encrypted_data
        
        elif isinstance(data, list):
            return [self.encrypt_request_data(item) for item in data]
        
        return data
    
    def decrypt_response_data(self, data):
        """فك تشفير البيانات للعرض في الاستجابة"""
        if isinstance(data, dict):
            decrypted_data = {}
            for key, value in data.items():
                if key in self.sensitive_fields and value:
                    # فك التشفير وإخفاء البيانات الحساسة
                    decrypted_value = self.decrypt_field_value(key, value)
                    decrypted_data[key] = self.mask_sensitive_value(key, decrypted_value)
                elif isinstance(value, (dict, list)):
                    decrypted_data[key] = self.decrypt_response_data(value)
                else:
                    decrypted_data[key] = value
            return decrypted_data
        
        elif isinstance(data, list):
            return [self.decrypt_response_data(item) for item in data]
        
        return data
    
    def encrypt_field_value(self, field_name, value):
        """تشفير قيمة حقل محدد"""
        try:
            if field_name == 'national_id':
                return encryption_service.encrypt_national_id(value)
            elif field_name in ['phone_number', 'mobile_number']:
                return encryption_service.encrypt_phone_number(value)
            elif field_name == 'personal_email':
                return encryption_service.encrypt_email(value)
            elif field_name in ['salary', 'basic_salary']:
                return encryption_service.encrypt_salary(value)
            elif field_name == 'bank_account':
                return encryption_service.encrypt_bank_account(value)
            else:
                return encryption_service.encrypt_text(value)
        except Exception as e:
            logger.error(f'خطأ في تشفير الحقل {field_name}: {e}')
            return value
    
    def decrypt_field_value(self, field_name, value):
        """فك تشفير قيمة حقل محدد"""
        try:
            if not encryption_service.is_encrypted(str(value)):
                return value
            
            if field_name == 'national_id':
                return encryption_service.decrypt_national_id(value)
            elif field_name in ['phone_number', 'mobile_number']:
                return encryption_service.decrypt_phone_number(value)
            elif field_name == 'personal_email':
                return encryption_service.decrypt_email(value)
            elif field_name in ['salary', 'basic_salary']:
                return encryption_service.decrypt_salary(value)
            elif field_name == 'bank_account':
                return encryption_service.decrypt_bank_account(value)
            else:
                return encryption_service.decrypt_text(value)
        except Exception as e:
            logger.error(f'خطأ في فك تشفير الحقل {field_name}: {e}')
            return value
    
    def mask_sensitive_value(self, field_name, value):
        """إخفاء البيانات الحساسة للعرض"""
        if not value:
            return value
        
        try:
            if field_name == 'national_id':
                return encryption_service.mask_sensitive_data(str(value), visible_chars=2)
            elif field_name in ['phone_number', 'mobile_number']:
                return encryption_service.mask_sensitive_data(str(value), visible_chars=3)
            elif field_name == 'personal_email':
                # إخفاء جزء من البريد الإلكتروني
                if '@' in str(value):
                    local, domain = str(value).split('@', 1)
                    masked_local = encryption_service.mask_sensitive_data(local, visible_chars=2)
                    return f'{masked_local}@{domain}'
                return encryption_service.mask_sensitive_data(str(value))
            elif field_name in ['salary', 'basic_salary']:
                # إخفاء جزء من الراتب
                return '****'
            elif field_name == 'bank_account':
                return encryption_service.mask_sensitive_data(str(value), visible_chars=4)
            else:
                return encryption_service.mask_sensitive_data(str(value))
        except Exception as e:
            logger.error(f'خطأ في إخفاء البيانات للحقل {field_name}: {e}')
            return '****'


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware لإضافة headers الأمان المتقدمة
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_response(self, request, response):
        """إضافة headers الأمان"""
        
        # منع تضمين الصفحة في iframe
        response['X-Frame-Options'] = 'DENY'
        
        # منع تخمين نوع المحتوى
        response['X-Content-Type-Options'] = 'nosniff'
        
        # تفعيل حماية XSS
        response['X-XSS-Protection'] = '1; mode=block'
        
        # إجبار HTTPS في الإنتاج
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # سياسة المحتوى الأمنية المحسنة
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://code.jquery.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self'; "
            "media-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp_policy
        
        # منع تسريب المرجع
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # منع تحميل المحتوى المختلط
        if not settings.DEBUG:
            response['Content-Security-Policy'] += " upgrade-insecure-requests;"
        
        # إضافة header مخصص للتطبيق
        response['X-HR-System'] = 'ElDawliya-HR-v2.0'
        
        return response


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware لتسجيل العمليات الحساسة
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.sensitive_paths = [
            '/hr/employees/',
            '/hr/api/',
            '/admin/',
        ]
        self.sensitive_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        super().__init__(get_response)
    
    def process_request(self, request):
        """تسجيل الطلبات الحساسة"""
        if self.is_sensitive_request(request):
            self.log_sensitive_request(request)
        return None
    
    def process_response(self, request, response):
        """تسجيل الاستجابات للطلبات الحساسة"""
        if self.is_sensitive_request(request):
            self.log_sensitive_response(request, response)
        return response
    
    def is_sensitive_request(self, request):
        """التحقق من كون الطلب حساساً"""
        # فحص المسار
        for path in self.sensitive_paths:
            if request.path.startswith(path):
                return True
        
        # فحص الطريقة
        if request.method in self.sensitive_methods:
            return True
        
        return False
    
    def log_sensitive_request(self, request):
        """تسجيل الطلب الحساس"""
        try:
            log_data = {
                'action': 'sensitive_request',
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'timestamp': str(timezone.now())
            }
            
            # تسجيل معاملات GET
            if request.GET:
                log_data['get_params'] = dict(request.GET)
            
            # تسجيل معاملات POST (بدون البيانات الحساسة)
            if request.method == 'POST' and request.POST:
                safe_post_data = {}
                for key, value in request.POST.items():
                    if key not in self.sensitive_fields:
                        safe_post_data[key] = value
                    else:
                        safe_post_data[key] = '***ENCRYPTED***'
                log_data['post_params'] = safe_post_data
            
            logger.info(f'Sensitive request: {json.dumps(log_data, ensure_ascii=False)}')
        
        except Exception as e:
            logger.error(f'خطأ في تسجيل الطلب الحساس: {e}')
    
    def log_sensitive_response(self, request, response):
        """تسجيل الاستجابة للطلب الحساس"""
        try:
            log_data = {
                'action': 'sensitive_response',
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                'ip_address': self.get_client_ip(request),
                'response_size': len(response.content) if hasattr(response, 'content') else 0,
                'timestamp': str(timezone.now())
            }
            
            logger.info(f'Sensitive response: {json.dumps(log_data, ensure_ascii=False)}')
        
        except Exception as e:
            logger.error(f'خطأ في تسجيل الاستجابة الحساسة: {e}')
    
    def get_client_ip(self, request):
        """الحصول على عنوان IP الحقيقي للعميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Middleware لتحديد معدل الطلبات
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limits = getattr(settings, 'RATE_LIMITS', {
            'default': {'requests': 100, 'window': 3600},  # 100 طلب في الساعة
            'api': {'requests': 1000, 'window': 3600},      # 1000 طلب في الساعة للـ API
            'sensitive': {'requests': 50, 'window': 3600}   # 50 طلب في الساعة للعمليات الحساسة
        })
        super().__init__(get_response)
    
    def process_request(self, request):
        """فحص معدل الطلبات"""
        # تحديد نوع الطلب
        rate_limit_type = self.get_rate_limit_type(request)
        
        # فحص معدل الطلبات
        if not self.check_rate_limit(request, rate_limit_type):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'تم تجاوز الحد الأقصى للطلبات. يرجى المحاولة لاحقاً.',
                'retry_after': self.rate_limits[rate_limit_type]['window']
            }, status=429)
        
        return None
    
    def get_rate_limit_type(self, request):
        """تحديد نوع حد الطلبات"""
        if request.path.startswith('/hr/api/'):
            return 'api'
        elif any(request.path.startswith(path) for path in ['/admin/', '/hr/employees/']):
            return 'sensitive'
        else:
            return 'default'
    
    def check_rate_limit(self, request, rate_limit_type):
        """فحص معدل الطلبات"""
        try:
            from django.core.cache import cache
            
            # إنشاء مفتاح فريد للعميل
            client_ip = self.get_client_ip(request)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'
            cache_key = f'rate_limit:{rate_limit_type}:{client_ip}:{user_id}'
            
            # الحصول على العدد الحالي
            current_requests = cache.get(cache_key, 0)
            rate_limit = self.rate_limits[rate_limit_type]
            
            if current_requests >= rate_limit['requests']:
                return False
            
            # زيادة العداد
            cache.set(cache_key, current_requests + 1, rate_limit['window'])
            return True
        
        except Exception as e:
            logger.error(f'خطأ في فحص معدل الطلبات: {e}')
            return True  # السماح بالطلب في حالة الخطأ
    
    def get_client_ip(self, request):
        """الحصول على عنوان IP الحقيقي للعميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip