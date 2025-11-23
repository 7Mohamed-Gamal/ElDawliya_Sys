"""
Custom exception handlers for API
معالجات الاستثناءات المخصصة لـ API
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import Http404

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides Arabic error messages
    معالج استثناءات مخصص يوفر رسائل خطأ باللغة العربية
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Log the exception
    request = context.get('request')
    if request:
        logger.error(
            f"API Exception: {exc.__class__.__name__} - {str(exc)} - "
            f"Path: {request.path} - Method: {request.method} - "
            f"User: {getattr(request.user, 'username', 'Anonymous')}"
        )

    if response is not None:
        # Customize the response data
        custom_response_data = {
            'error': True,
            'message': get_arabic_error_message(exc, response.data),
            'details': response.data,
            'status_code': response.status_code,
            'timestamp': context.get('request').META.get('HTTP_X_TIMESTAMP') if context.get('request') else None
        }
        
        # Add request ID if available
        if hasattr(context.get('request'), 'id'):
            custom_response_data['request_id'] = context['request'].id

        response.data = custom_response_data

    else:
        # Handle Django exceptions that DRF doesn't handle
        if isinstance(exc, ValidationError):
            response = Response({
                'error': True,
                'message': 'خطأ في التحقق من صحة البيانات',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(exc, IntegrityError):
            response = Response({
                'error': True,
                'message': 'خطأ في سلامة البيانات - قد تكون البيانات مكررة أو غير صحيحة',
                'details': str(exc),
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(exc, Http404):
            response = Response({
                'error': True,
                'message': 'المورد المطلوب غير موجود',
                'details': str(exc),
                'status_code': status.HTTP_404_NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND)

        else:
            # Generic server error
            response = Response({
                'error': True,
                'message': 'حدث خطأ داخلي في الخادم',
                'details': str(exc) if settings.DEBUG else 'خطأ داخلي',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def get_arabic_error_message(exc, response_data):
    """
    Convert English error messages to Arabic
    تحويل رسائل الخطأ الإنجليزية إلى العربية
    """
    error_messages = {
        'ValidationError': 'خطأ في التحقق من صحة البيانات',
        'PermissionDenied': 'ليس لديك صلاحية للوصول لهذا المورد',
        'NotAuthenticated': 'يجب تسجيل الدخول للوصول لهذا المورد',
        'AuthenticationFailed': 'فشل في المصادقة - تحقق من بيانات الدخول',
        'NotFound': 'المورد المطلوب غير موجود',
        'MethodNotAllowed': 'الطريقة المستخدمة غير مسموحة لهذا المورد',
        'NotAcceptable': 'تنسيق الاستجابة المطلوب غير مدعوم',
        'UnsupportedMediaType': 'نوع الوسائط غير مدعوم',
        'Throttled': 'تم تجاوز الحد المسموح من الطلبات - حاول مرة أخرى لاحقاً',
        'ParseError': 'خطأ في تحليل البيانات المرسلة',
        'APIException': 'حدث خطأ في API',
    }

    exc_name = exc.__class__.__name__
    
    # Check for specific field errors
    if isinstance(response_data, dict):
        if 'detail' in response_data:
            detail = response_data['detail']
            if 'Invalid API key' in str(detail):
                return 'مفتاح API غير صحيح'
            elif 'API key has expired' in str(detail):
                return 'انتهت صلاحية مفتاح API'
            elif 'User account is disabled' in str(detail):
                return 'حساب المستخدم معطل'
            elif 'Invalid token' in str(detail):
                return 'رمز المصادقة غير صحيح'
            elif 'Token has expired' in str(detail):
                return 'انتهت صلاحية رمز المصادقة'
        
        # Check for field-specific errors
        field_errors = []
        for field, errors in response_data.items():
            if field not in ['detail', 'non_field_errors']:
                arabic_field = get_arabic_field_name(field)
                if isinstance(errors, list):
                    for error in errors:
                        field_errors.append(f"{arabic_field}: {get_arabic_validation_message(error)}")
                else:
                    field_errors.append(f"{arabic_field}: {get_arabic_validation_message(errors)}")
        
        if field_errors:
            return "أخطاء في الحقول: " + "، ".join(field_errors)

    return error_messages.get(exc_name, f'حدث خطأ: {str(exc)}')


def get_arabic_field_name(field_name):
    """
    Convert English field names to Arabic
    تحويل أسماء الحقول الإنجليزية إلى العربية
    """
    field_names = {
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'email': 'البريد الإلكتروني',
        'first_name': 'الاسم الأول',
        'last_name': 'اسم العائلة',
        'phone': 'رقم الهاتف',
        'name': 'الاسم',
        'title': 'العنوان',
        'description': 'الوصف',
        'date': 'التاريخ',
        'time': 'الوقت',
        'status': 'الحالة',
        'priority': 'الأولوية',
        'category': 'الفئة',
        'department': 'القسم',
        'position': 'المنصب',
        'salary': 'الراتب',
        'hire_date': 'تاريخ التوظيف',
        'birth_date': 'تاريخ الميلاد',
        'address': 'العنوان',
        'city': 'المدينة',
        'country': 'البلد',
        'product_name': 'اسم المنتج',
        'price': 'السعر',
        'quantity': 'الكمية',
        'supplier': 'المورد',
        'warehouse': 'المخزن',
    }
    
    return field_names.get(field_name, field_name)


def get_arabic_validation_message(error_message):
    """
    Convert English validation messages to Arabic
    تحويل رسائل التحقق الإنجليزية إلى العربية
    """
    validation_messages = {
        'This field is required.': 'هذا الحقل مطلوب',
        'This field may not be blank.': 'هذا الحقل لا يمكن أن يكون فارغاً',
        'This field may not be null.': 'هذا الحقل لا يمكن أن يكون فارغاً',
        'Enter a valid email address.': 'أدخل عنوان بريد إلكتروني صحيح',
        'Enter a valid URL.': 'أدخل رابط صحيح',
        'Enter a valid date.': 'أدخل تاريخ صحيح',
        'Enter a valid time.': 'أدخل وقت صحيح',
        'Enter a valid number.': 'أدخل رقم صحيح',
        'Ensure this value is greater than or equal to': 'تأكد أن هذه القيمة أكبر من أو تساوي',
        'Ensure this value is less than or equal to': 'تأكد أن هذه القيمة أقل من أو تساوي',
        'Ensure this field has no more than': 'تأكد أن هذا الحقل لا يحتوي على أكثر من',
        'Ensure this field has at least': 'تأكد أن هذا الحقل يحتوي على الأقل على',
        'Invalid choice.': 'اختيار غير صحيح',
        'A user with that username already exists.': 'يوجد مستخدم بهذا الاسم مسبقاً',
        'The password is too similar to the username.': 'كلمة المرور مشابهة جداً لاسم المستخدم',
        'This password is too short.': 'كلمة المرور قصيرة جداً',
        'This password is too common.': 'كلمة المرور شائعة جداً',
        'This password is entirely numeric.': 'كلمة المرور تحتوي على أرقام فقط',
    }
    
    error_str = str(error_message)
    
    # Check for exact matches first
    if error_str in validation_messages:
        return validation_messages[error_str]
    
    # Check for partial matches
    for english_msg, arabic_msg in validation_messages.items():
        if english_msg in error_str:
            return arabic_msg
    
    return error_str


class APIException(Exception):
    """
    Custom API exception with Arabic support
    استثناء API مخصص مع دعم العربية
    """
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(APIException):
    """
    Custom validation exception
    استثناء التحقق المخصص
    """
    def __init__(self, message, field_errors=None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, field_errors)


class PermissionException(APIException):
    """
    Custom permission exception
    استثناء الصلاحيات المخصص
    """
    def __init__(self, message="ليس لديك صلاحية للوصول لهذا المورد"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class AuthenticationException(APIException):
    """
    Custom authentication exception
    استثناء المصادقة المخصص
    """
    def __init__(self, message="فشل في المصادقة"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ResourceNotFoundException(APIException):
    """
    Custom not found exception
    استثناء عدم وجود المورد المخصص
    """
    def __init__(self, message="المورد المطلوب غير موجود"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class RateLimitException(APIException):
    """
    Custom rate limit exception
    استثناء تجاوز الحد المسموح المخصص
    """
    def __init__(self, message="تم تجاوز الحد المسموح من الطلبات"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)