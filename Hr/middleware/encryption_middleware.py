"""
Middleware للتشفير التلقائي والأمان
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from Hr.services.encryption_service import encryption_service, secure_data_manager
import logging
import json
import hashlib
from datetime import timedelta

logger = logging.getLogger(__name__)


class EncryptionSecurityMiddleware(MiddlewareMixin):
    """Middleware للأمان والتشفير"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'HR_ENCRYPTION_SECURITY', True)
        self.max_requests_per_minute = getattr(settings, 'HR_MAX_REQUESTS_PER_MINUTE', 60)
        self.sensitive_paths = getattr(settings, 'HR_SENSITIVE_PATHS', [
            '/hr/employees/',
            '/hr/payroll/',
            '/hr/files/',
            '/api/v1/employees/',
            '/api/v1/payroll/'
        ])
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة الطلب الوارد"""
        if not self.enabled:
            return None
        
        # التحقق من معدل الطلبات
        if not self._check_rate_limit(request):
            logger.warning(f"تم تجاوز حد الطلبات من IP: {self._get_client_ip(request)}")
            return HttpResponseForbidden("تم تجاوز حد الطلبات المسموح")
        
        # التحقق من الوصول للمسارات الحساسة
        if self._is_sensitive_path(request.path):
            if not self._validate_sensitive_access(request):
                logger.warning(f"محاولة وصول غير مصرح بها للمسار الحساس: {request.path}")
                return HttpResponseForbidden("غير مصرح بالوصول")
        
        # إضافة معلومات الأمان للطلب
        request.security_context = {
            'client_ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'timestamp': timezone.now(),
            'is_sensitive_path': self._is_sensitive_path(request.path)
        }
        
        return None
    
    def process_response(self, request, response):
        """معالجة الاستجابة"""
        if not self.enabled:
            return response
        
        # إضافة headers الأمان
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # إضافة CSP للمسارات الحساسة
        if hasattr(request, 'security_context') and request.security_context.get('is_sensitive_path'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'"
            )
        
        # تسجيل الوصول للمسارات الحساسة
        if hasattr(request, 'security_context') and request.security_context.get('is_sensitive_path'):
            self._log_sensitive_access(request, response)
        
        return response
    
    def _check_rate_limit(self, request):
        """التحقق من معدل الطلبات"""
        try:
            client_ip = self._get_client_ip(request)
            cache_key = f'rate_limit_{client_ip}'
            
            # الحصول على عدد الطلبات الحالي
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= self.max_requests_per_minute:
                return False
            
            # زيادة العداد
            cache.set(cache_key, current_requests + 1, 60)  # 60 ثانية
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من معدل الطلبات: {e}")
            return True  # السماح بالطلب في حالة الخطأ
    
    def _is_sensitive_path(self, path):
        """التحقق من كون المسار حساساً"""
        return any(path.startswith(sensitive_path) for sensitive_path in self.sensitive_paths)
    
    def _validate_sensitive_access(self, request):
        """التحقق من صحة الوصول للمسارات الحساسة"""
        # التحقق من تسجيل الدخول
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        
        # التحقق من الصلاحيات الأساسية
        if not request.user.is_active:
            return False
        
        # التحقق من IP المسموح (إذا تم تكوينه)
        allowed_ips = getattr(settings, 'HR_ALLOWED_IPS', None)
        if allowed_ips:
            client_ip = self._get_client_ip(request)
            if client_ip not in allowed_ips:
                return False
        
        return True
    
    def _get_client_ip(self, request):
        """الحصول على IP العميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_sensitive_access(self, request, response):
        """تسجيل الوصول للمسارات الحساسة"""
        try:
            access_log = {
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
                'username': request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous',
                'path': request.path,
                'method': request.method,
                'client_ip': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'status_code': response.status_code,
                'timestamp': timezone.now().isoformat()
            }
            
            # حفظ في التخزين المؤقت
            today = timezone.now().date().isoformat()
            cache_key = f'sensitive_access_log_{today}'
            
            access_logs = cache.get(cache_key, [])
            access_logs.append(access_log)
            cache.set(cache_key, access_logs, 86400)  # 24 ساعة
            
            # تسجيل في السجل
            logger.info(f"وصول حساس: {access_log['username']} -> {access_log['path']}")
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الوصول الحساس: {e}")


class DataEncryptionMiddleware(MiddlewareMixin):
    """Middleware لتشفير البيانات تلقائياً"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'HR_AUTO_ENCRYPTION', True)
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة الطلب لتشفير البيانات الواردة"""
        if not self.enabled:
            return None
        
        # تشفير البيانات الحساسة في POST requests
        if request.method == 'POST' and request.content_type == 'application/json':
            try:
                if hasattr(request, 'body') and request.body:
                    data = json.loads(request.body.decode('utf-8'))
                    
                    # تشفير البيانات الحساسة
                    encrypted_data = encryption_service.encrypt_sensitive_data(data)
                    
                    # تحديث body الطلب
                    request._body = json.dumps(encrypted_data).encode('utf-8')
                    
            except Exception as e:
                logger.error(f"خطأ في تشفير بيانات الطلب: {e}")
        
        return None
    
    def process_response(self, request, response):
        """معالجة الاستجابة لفك تشفير البيانات"""
        if not self.enabled:
            return response
        
        # فك تشفير البيانات في JSON responses
        if (response.get('Content-Type', '').startswith('application/json') and 
            hasattr(response, 'content')):
            
            try:
                data = json.loads(response.content.decode('utf-8'))
                
                # فك تشفير البيانات الحساسة
                if isinstance(data, dict):
                    decrypted_data = encryption_service.decrypt_sensitive_data(data)
                    response.content = json.dumps(decrypted_data, ensure_ascii=False).encode('utf-8')
                elif isinstance(data, list):
                    decrypted_list = []
                    for item in data:
                        if isinstance(item, dict):
                            decrypted_list.append(encryption_service.decrypt_sensitive_data(item))
                        else:
                            decrypted_list.append(item)
                    response.content = json.dumps(decrypted_list, ensure_ascii=False).encode('utf-8')
                
            except Exception as e:
                logger.error(f"خطأ في فك تشفير بيانات الاستجابة: {e}")
        
        return response


class SecureSessionMiddleware(MiddlewareMixin):
    """Middleware للجلسات الآمنة"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'HR_SECURE_SESSIONS', True)
        self.session_timeout = getattr(settings, 'HR_SESSION_TIMEOUT', 3600)  # ساعة واحدة
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة الطلب للجلسات الآمنة"""
        if not self.enabled:
            return None
        
        # التحقق من انتهاء صلاحية الجلسة
        if hasattr(request, 'session') and request.session.session_key:
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                last_activity_time = timezone.datetime.fromisoformat(last_activity)
                if timezone.now() - last_activity_time > timedelta(seconds=self.session_timeout):
                    # انتهت صلاحية الجلسة
                    request.session.flush()
                    logger.info("تم إنهاء جلسة منتهية الصلاحية")
            
            # تحديث وقت النشاط الأخير
            request.session['last_activity'] = timezone.now().isoformat()
        
        # التحقق من تغيير IP
        if hasattr(request, 'session') and request.session.session_key:
            session_ip = request.session.get('client_ip')
            current_ip = self._get_client_ip(request)
            
            if session_ip and session_ip != current_ip:
                # تغير IP - إنهاء الجلسة للأمان
                request.session.flush()
                logger.warning(f"تم إنهاء جلسة بسبب تغيير IP: {session_ip} -> {current_ip}")
            else:
                request.session['client_ip'] = current_ip
        
        return None
    
    def process_response(self, request, response):
        """معالجة الاستجابة للجلسات الآمنة"""
        if not self.enabled:
            return response
        
        # إضافة headers الأمان للجلسات
        if hasattr(request, 'session') and request.session.session_key:
            response['X-Session-Timeout'] = str(self.session_timeout)
            
            # تشفير معرف الجلسة في cookie
            if 'sessionid' in response.cookies:
                response.cookies['sessionid']['secure'] = True
                response.cookies['sessionid']['httponly'] = True
                response.cookies['sessionid']['samesite'] = 'Strict'
        
        return response
    
    def _get_client_ip(self, request):
        """الحصول على IP العميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EncryptionAuditMiddleware(MiddlewareMixin):
    """Middleware لتدقيق عمليات التشفير"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'HR_ENCRYPTION_AUDIT', True)
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة الطلب لتدقيق التشفير"""
        if not self.enabled:
            return None
        
        # تسجيل الطلبات للمسارات الحساسة
        if self._is_sensitive_path(request.path):
            audit_data = {
                'action': 'access_sensitive_data',
                'path': request.path,
                'method': request.method,
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
                'client_ip': self._get_client_ip(request),
                'timestamp': timezone.now().isoformat()
            }
            
            self._save_audit_log(audit_data)
        
        return None
    
    def process_response(self, request, response):
        """معالجة الاستجابة لتدقيق التشفير"""
        if not self.enabled:
            return response
        
        # تسجيل الاستجابات للمسارات الحساسة
        if self._is_sensitive_path(request.path):
            audit_data = {
                'action': 'response_sensitive_data',
                'path': request.path,
                'method': request.method,
                'status_code': response.status_code,
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
                'client_ip': self._get_client_ip(request),
                'timestamp': timezone.now().isoformat()
            }
            
            self._save_audit_log(audit_data)
        
        return response
    
    def _is_sensitive_path(self, path):
        """التحقق من كون المسار حساساً"""
        sensitive_paths = [
            '/hr/employees/',
            '/hr/payroll/',
            '/hr/files/',
            '/api/v1/employees/',
            '/api/v1/payroll/'
        ]
        return any(path.startswith(sensitive_path) for sensitive_path in sensitive_paths)
    
    def _get_client_ip(self, request):
        """الحصول على IP العميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _save_audit_log(self, audit_data):
        """حفظ سجل التدقيق"""
        try:
            # حفظ في التخزين المؤقت
            today = timezone.now().date().isoformat()
            cache_key = f'encryption_audit_log_{today}'
            
            audit_logs = cache.get(cache_key, [])
            audit_logs.append(audit_data)
            cache.set(cache_key, audit_logs, 86400)  # 24 ساعة
            
            # تسجيل في السجل
            logger.info(f"تدقيق التشفير: {audit_data['action']} - {audit_data['path']}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ سجل تدقيق التشفير: {e}")