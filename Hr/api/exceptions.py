"""
HR API Exception Handlers - معالجات الاستثناءات لواجهات برمجة التطبيقات
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger('hr_api')

def custom_exception_handler(exc, context):
    """معالج الاستثناءات المخصص"""
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception
    logger.error(f"API Exception: {exc}", exc_info=True)
    
    if response is not None:
        # Customize the response format
        custom_response_data = {
            'error': True,
            'message': 'حدث خطأ في معالجة الطلب',
            'details': response.data,
            'status_code': response.status_code
        }
        
        # Handle specific error types
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['message'] = 'بيانات غير صحيحة'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['message'] = 'غير مصرح لك بالوصول'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['message'] = 'ليس لديك صلاحية للقيام بهذا الإجراء'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['message'] = 'العنصر المطلوب غير موجود'
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_response_data['message'] = 'الطريقة غير مسموحة'
        elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            custom_response_data['message'] = 'تم تجاوز الحد المسموح من الطلبات'
        elif response.status_code >= 500:
            custom_response_data['message'] = 'خطأ داخلي في الخادم'
        
        response.data = custom_response_data
        
    else:
        # Handle non-DRF exceptions
        if isinstance(exc, DjangoValidationError):
            custom_response_data = {
                'error': True,
                'message': 'خطأ في التحقق من البيانات',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                'status_code': status.HTTP_400_BAD_REQUEST
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
            
        elif isinstance(exc, IntegrityError):
            custom_response_data = {
                'error': True,
                'message': 'خطأ في سلامة البيانات',
                'details': 'البيانات المدخلة تتعارض مع قيود قاعدة البيانات',
                'status_code': status.HTTP_400_BAD_REQUEST
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
            
        elif isinstance(exc, PermissionError):
            custom_response_data = {
                'error': True,
                'message': 'ليس لديك صلاحية للقيام بهذا الإجراء',
                'details': str(exc),
                'status_code': status.HTTP_403_FORBIDDEN
            }
            response = Response(custom_response_data, status=status.HTTP_403_FORBIDDEN)
            
        else:
            # Generic server error
            custom_response_data = {
                'error': True,
                'message': 'خطأ داخلي في الخادم',
                'details': str(exc) if settings.DEBUG else 'حدث خطأ غير متوقع',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response

class HRAPIException(Exception):
    """استثناء مخصص لواجهات برمجة التطبيقات"""
    
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class EmployeeNotFoundException(HRAPIException):
    """استثناء عدم وجود الموظف"""
    
    def __init__(self, employee_id=None):
        message = f"الموظف غير موجود"
        if employee_id:
            message += f" (ID: {employee_id})"
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class AttendanceRecordException(HRAPIException):
    """استثناء سجل الحضور"""
    
    def __init__(self, message, details=None):
        super().__init__(f"خطأ في سجل الحضور: {message}", status.HTTP_400_BAD_REQUEST, details)

class LeaveRequestException(HRAPIException):
    """استثناء طلب الإجازة"""
    
    def __init__(self, message, details=None):
        super().__init__(f"خطأ في طلب الإجازة: {message}", status.HTTP_400_BAD_REQUEST, details)

class PayrollException(HRAPIException):
    """استثناء الرواتب"""
    
    def __init__(self, message, details=None):
        super().__init__(f"خطأ في الرواتب: {message}", status.HTTP_400_BAD_REQUEST, details)

class FileUploadException(HRAPIException):
    """استثناء رفع الملفات"""
    
    def __init__(self, message, details=None):
        super().__init__(f"خطأ في رفع الملف: {message}", status.HTTP_400_BAD_REQUEST, details)

class PermissionDeniedException(HRAPIException):
    """استثناء رفض الصلاحية"""
    
    def __init__(self, action=None):
        message = "ليس لديك صلاحية للقيام بهذا الإجراء"
        if action:
            message += f": {action}"
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class ValidationException(HRAPIException):
    """استثناء التحقق من البيانات"""
    
    def __init__(self, field, message):
        super().__init__(f"خطأ في التحقق من {field}: {message}", status.HTTP_400_BAD_REQUEST)

class BusinessLogicException(HRAPIException):
    """استثناء منطق العمل"""
    
    def __init__(self, message, details=None):
        super().__init__(f"خطأ في منطق العمل: {message}", status.HTTP_422_UNPROCESSABLE_ENTITY, details)