"""
Middleware لتسجيل العمليات الحساسة في نظام الموارد البشرية
"""

import json
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.urls import resolve
from django.utils import timezone
from django.conf import settings
import uuid

logger = logging.getLogger('hr_audit')


class HRAuditMiddleware(MiddlewareMixin):
    """
    Middleware لتسجيل جميع العمليات الحساسة في نظام الموارد البشرية
    """
    
    # العمليات التي يجب تسجيلها
    SENSITIVE_OPERATIONS = {
        'POST': ['create', 'add', 'save', 'submit', 'approve', 'reject'],
        'PUT': ['update', 'edit', 'modify', 'change'],
        'PATCH': ['update', 'edit', 'modify', 'change'],
        'DELETE': ['delete', 'remove', 'destroy'],
    }
    
    # المسارات الحساسة
    SENSITIVE_PATHS = [
        '/Hr/employees/',
        '/Hr/payroll/',
        '/Hr/evaluations/',
        '/Hr/permissions/',
        '/Hr/attendance/',
        '/Hr/leaves/',
        '/api/hr/',
    ]
    
    # البيانات الحساسة التي يجب إخفاؤها
    SENSITIVE_FIELDS = [
        'password', 'token', 'secret', 'key', 'ssn', 'national_id',
        'bank_account', 'salary', 'credit_card', 'phone', 'email'
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """معالجة الطلب قبل الوصول للعرض"""
        
        # إضافة معرف فريد للطلب
        request.audit_id = str(uuid.uuid4())
        request.start_time = time.time()
        
        # التحقق من ضرورة تسجيل هذا الطلب
        if self._should_audit_request(request):
            request.should_audit = True
            
            # تسجيل بداية الطلب
            self._log_request_start(request)
        else:
            request.should_audit = False
        
        return None

    def process_response(self, request, response):
        """معالجة الاستجابة بعد العرض"""
        
        if getattr(request, 'should_audit', False):
            # حساب وقت الاستجابة
            response_time = time.time() - getattr(request, 'start_time', time.time())
            
            # تسجيل الاستجابة
            self._log_response(request, response, response_time)
        
        return response

    def process_exception(self, request, exception):
        """معالجة الاستثناءات"""
        
        if getattr(request, 'should_audit', False):
            self._log_exception(request, exception)
        
        return None

    def _should_audit_request(self, request):
        """تحديد ما إذا كان يجب تسجيل هذا الطلب"""
        
        # تجاهل الطلبات الثابتة
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return False
        
        # تجاهل طلبات الصحة
        if request.path in ['/health/', '/ping/', '/status/']:
            return False
        
        # تسجيل جميع العمليات الحساسة
        if request.method in self.SENSITIVE_OPERATIONS:
            return True
        
        # تسجيل المسارات الحساسة
        for sensitive_path in self.SENSITIVE_PATHS:
            if request.path.startswith(sensitive_path):
                return True
        
        # تسجيل طلبات المستخدمين المسجلين فقط للمسارات المهمة
        if not isinstance(request.user, AnonymousUser):
            if request.path.startswith('/Hr/') or request.path.startswith('/api/'):
                return True
        
        return False

    def _log_request_start(self, request):
        """تسجيل بداية الطلب"""
        
        try:
            # جمع معلومات الطلب
            request_data = {
                'audit_id': request.audit_id,
                'timestamp': timezone.now().isoformat(),
                'event_type': 'request_start',
                'user_id': request.user.id if not isinstance(request.user, AnonymousUser) else None,
                'username': request.user.username if not isinstance(request.user, AnonymousUser) else 'anonymous',
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.GET),
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', ''),
                'session_key': request.session.session_key if hasattr(request, 'session') else None,
            }
            
            # إضافة بيانات POST إذا كانت موجودة (مع إخفاء البيانات الحساسة)
            if request.method in ['POST', 'PUT', 'PATCH']:
                request_data['post_data'] = self._sanitize_data(dict(request.POST))
                
                # إضافة بيانات JSON إذا كانت موجودة
                if request.content_type == 'application/json':
                    try:
                        json_data = json.loads(request.body.decode('utf-8'))
                        request_data['json_data'] = self._sanitize_data(json_data)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
            
            # تسجيل في قاعدة البيانات
            self._save_audit_log(request_data)
            
            # تسجيل في ملف السجل
            logger.info(f"Request started: {json.dumps(request_data, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Error logging request start: {e}")

    def _log_response(self, request, response, response_time):
        """تسجيل الاستجابة"""
        
        try:
            response_data = {
                'audit_id': request.audit_id,
                'timestamp': timezone.now().isoformat(),
                'event_type': 'request_complete',
                'status_code': response.status_code,
                'response_time': round(response_time * 1000, 2),  # بالميلي ثانية
                'content_type': response.get('Content-Type', ''),
                'content_length': len(response.content) if hasattr(response, 'content') else 0,
            }
            
            # إضافة بيانات الاستجابة للعمليات المهمة
            if response.status_code >= 400 or request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                if hasattr(response, 'content') and response.get('Content-Type', '').startswith('application/json'):
                    try:
                        json_response = json.loads(response.content.decode('utf-8'))
                        response_data['response_data'] = self._sanitize_data(json_response)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
            
            # تحديد مستوى الخطورة
            if response.status_code >= 500:
                severity = 'critical'
            elif response.status_code >= 400:
                severity = 'warning'
            elif request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                severity = 'high'
            else:
                severity = 'normal'
            
            response_data['severity'] = severity
            
            # تسجيل في قاعدة البيانات
            self._save_audit_log(response_data)
            
            # تسجيل في ملف السجل
            log_level = getattr(logger, severity.upper() if severity != 'normal' else 'INFO')
            log_level(f"Request completed: {json.dumps(response_data, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Error logging response: {e}")

    def _log_exception(self, request, exception):
        """تسجيل الاستثناءات"""
        
        try:
            exception_data = {
                'audit_id': request.audit_id,
                'timestamp': timezone.now().isoformat(),
                'event_type': 'exception',
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'severity': 'critical',
            }
            
            # تسجيل في قاعدة البيانات
            self._save_audit_log(exception_data)
            
            # تسجيل في ملف السجل
            logger.critical(f"Request exception: {json.dumps(exception_data, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Error logging exception: {e}")

    def _sanitize_data(self, data):
        """إخفاء البيانات الحساسة"""
        
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                    sanitized[key] = '***HIDDEN***'
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_data(value)
                else:
                    sanitized[key] = value
            return sanitized
        
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        
        else:
            return data

    def _get_client_ip(self, request):
        """الحصول على عنوان IP الخاص بالعميل"""
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _save_audit_log(self, log_data):
        """حفظ سجل التدقيق في قاعدة البيانات"""
        
        try:
            from .models import AuditLog
            
            AuditLog.objects.create(
                audit_id=log_data.get('audit_id'),
                event_type=log_data.get('event_type'),
                user_id=log_data.get('user_id'),
                username=log_data.get('username', 'anonymous'),
                method=log_data.get('method'),
                path=log_data.get('path'),
                ip_address=log_data.get('ip_address'),
                user_agent=log_data.get('user_agent', ''),
                status_code=log_data.get('status_code'),
                response_time=log_data.get('response_time'),
                severity=log_data.get('severity', 'normal'),
                details=log_data,
                timestamp=timezone.now()
            )
            
        except Exception as e:
            logger.error(f"Error saving audit log to database: {e}")


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware للأمان المتقدم
    """
    
    # محاولات تسجيل الدخول المشبوهة
    SUSPICIOUS_PATTERNS = [
        'admin', 'root', 'test', 'guest', 'demo',
        'sql', 'script', 'alert', 'javascript',
        '../', '..\\', '<script', 'union select',
        'drop table', 'delete from'
    ]
    
    # الحد الأقصى لحجم الطلب (بالبايت)
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB

    def process_request(self, request):
        """فحص الطلب للأنشطة المشبوهة"""
        
        # فحص حجم الطلب
        if hasattr(request, 'META') and 'CONTENT_LENGTH' in request.META:
            try:
                content_length = int(request.META['CONTENT_LENGTH'])
                if content_length > self.MAX_REQUEST_SIZE:
                    logger.warning(f"Large request detected: {content_length} bytes from {self._get_client_ip(request)}")
                    return JsonResponse({'error': 'Request too large'}, status=413)
            except (ValueError, TypeError):
                pass
        
        # فحص الأنماط المشبوهة
        suspicious_found = self._check_suspicious_patterns(request)
        if suspicious_found:
            logger.warning(f"Suspicious request detected from {self._get_client_ip(request)}: {suspicious_found}")
            
            # تسجيل النشاط المشبوه
            self._log_suspicious_activity(request, suspicious_found)
            
            # يمكن إرجاع خطأ أو السماح بالمتابعة حسب السياسة
            # return JsonResponse({'error': 'Suspicious activity detected'}, status=403)
        
        return None

    def _check_suspicious_patterns(self, request):
        """فحص الأنماط المشبوهة في الطلب"""
        
        # فحص المسار
        path_lower = request.path.lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern in path_lower:
                return f"Suspicious pattern in path: {pattern}"
        
        # فحص معاملات GET
        for key, value in request.GET.items():
            value_lower = str(value).lower()
            for pattern in self.SUSPICIOUS_PATTERNS:
                if pattern in value_lower:
                    return f"Suspicious pattern in GET parameter {key}: {pattern}"
        
        # فحص معاملات POST
        if request.method == 'POST':
            for key, value in request.POST.items():
                value_lower = str(value).lower()
                for pattern in self.SUSPICIOUS_PATTERNS:
                    if pattern in value_lower:
                        return f"Suspicious pattern in POST parameter {key}: {pattern}"
        
        # فحص User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['bot', 'crawler', 'scanner', 'hack', 'exploit']
        for agent in suspicious_agents:
            if agent in user_agent:
                return f"Suspicious user agent: {agent}"
        
        return None

    def _log_suspicious_activity(self, request, activity_type):
        """تسجيل النشاط المشبوه"""
        
        try:
            from .models import SecurityLog
            
            SecurityLog.objects.create(
                event_type='suspicious_activity',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                path=request.path,
                method=request.method,
                user_id=request.user.id if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser) else None,
                details={
                    'activity_type': activity_type,
                    'get_params': dict(request.GET),
                    'post_params': dict(request.POST) if request.method == 'POST' else {},
                    'referer': request.META.get('HTTP_REFERER', ''),
                },
                severity='high',
                timestamp=timezone.now()
            )
            
        except Exception as e:
            logger.error(f"Error logging suspicious activity: {e}")

    def _get_client_ip(self, request):
        """الحصول على عنوان IP الخاص بالعميل"""
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware لمراقبة الأداء
    """
    
    # الحد الأقصى لوقت الاستجابة (بالثواني)
    SLOW_REQUEST_THRESHOLD = 2.0
    
    # الحد الأقصى لاستهلاك الذاكرة (بالميجابايت)
    MEMORY_THRESHOLD = 100

    def process_request(self, request):
        """بداية مراقبة الأداء"""
        
        request.performance_start = time.time()
        
        # قياس استهلاك الذاكرة (إذا كان متاحاً)
        try:
            import psutil
            process = psutil.Process()
            request.memory_start = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            request.memory_start = None
        
        return None

    def process_response(self, request, response):
        """تحليل أداء الطلب"""
        
        if hasattr(request, 'performance_start'):
            response_time = time.time() - request.performance_start
            
            # قياس استهلاك الذاكرة النهائي
            memory_used = None
            if hasattr(request, 'memory_start') and request.memory_start:
                try:
                    import psutil
                    process = psutil.Process()
                    memory_end = process.memory_info().rss / 1024 / 1024  # MB
                    memory_used = memory_end - request.memory_start
                except ImportError:
                    pass
            
            # تسجيل الطلبات البطيئة
            if response_time > self.SLOW_REQUEST_THRESHOLD:
                self._log_slow_request(request, response_time, memory_used)
            
            # تسجيل استهلاك الذاكرة العالي
            if memory_used and memory_used > self.MEMORY_THRESHOLD:
                self._log_high_memory_usage(request, memory_used, response_time)
        
        return response

    def _log_slow_request(self, request, response_time, memory_used):
        """تسجيل الطلبات البطيئة"""
        
        try:
            from .models import PerformanceLog
            
            PerformanceLog.objects.create(
                event_type='slow_request',
                path=request.path,
                method=request.method,
                response_time=response_time,
                memory_usage=memory_used,
                user_id=request.user.id if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser) else None,
                ip_address=self._get_client_ip(request),
                details={
                    'query_params': dict(request.GET),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                },
                severity='warning',
                timestamp=timezone.now()
            )
            
            logger.warning(f"Slow request: {request.path} took {response_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error logging slow request: {e}")

    def _log_high_memory_usage(self, request, memory_used, response_time):
        """تسجيل استهلاك الذاكرة العالي"""
        
        try:
            from .models import PerformanceLog
            
            PerformanceLog.objects.create(
                event_type='high_memory_usage',
                path=request.path,
                method=request.method,
                response_time=response_time,
                memory_usage=memory_used,
                user_id=request.user.id if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser) else None,
                ip_address=self._get_client_ip(request),
                details={
                    'query_params': dict(request.GET),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                },
                severity='warning',
                timestamp=timezone.now()
            )
            
            logger.warning(f"High memory usage: {request.path} used {memory_used:.2f}MB")
            
        except Exception as e:
            logger.error(f"Error logging high memory usage: {e}")

    def _get_client_ip(self, request):
        """الحصول على عنوان IP الخاص بالعميل"""
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip