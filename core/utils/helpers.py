"""
دوال مساعدة عامة
General helper functions
"""
import uuid
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


def generate_unique_code(prefix='', length=8, include_letters=True, include_numbers=True):
    """
    توليد رمز فريد
    Generate unique code with optional prefix
    """
    characters = ''
    if include_letters:
        characters += string.ascii_uppercase
    if include_numbers:
        characters += string.digits
    
    if not characters:
        characters = string.digits
    
    code = ''.join(random.choices(characters, k=length))
    return f"{prefix}{code}" if prefix else code


def generate_employee_code(department_code='', sequence_number=None):
    """
    توليد رقم موظف
    Generate employee code
    """
    if sequence_number is None:
        sequence_number = random.randint(1000, 9999)
    
    year = datetime.now().year
    return f"{department_code}{year}{sequence_number:04d}"


def format_currency(amount, currency='ريال', show_currency=True):
    """
    تنسيق المبلغ المالي
    Format currency amount
    """
    if amount is None:
        return '0'
    
    # Format with thousands separator
    formatted = f"{amount:,.2f}"
    
    if show_currency:
        return f"{formatted} {currency}"
    return formatted


def format_phone_number(phone, country_code='+966'):
    """
    تنسيق رقم الهاتف
    Format phone number with country code
    """
    if not phone:
        return ''
    
    # Remove any non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # Handle Saudi phone numbers
    if country_code == '+966':
        if digits_only.startswith('966'):
            digits_only = digits_only[3:]
        elif digits_only.startswith('0'):
            digits_only = digits_only[1:]
        
        if len(digits_only) == 9:
            return f"+966 {digits_only[:2]} {digits_only[2:5]} {digits_only[5:]}"
    
    return phone


def get_client_ip(request):
    """
    الحصول على عنوان IP للعميل
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    الحصول على معلومات المتصفح
    Get user agent from request
    """
    return request.META.get('HTTP_USER_AGENT', '')


def calculate_age(birth_date):
    """
    حساب العمر
    Calculate age from birth date
    """
    if not birth_date:
        return None
    
    today = timezone.now().date()
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age


def calculate_service_years(hire_date, end_date=None):
    """
    حساب سنوات الخدمة
    Calculate years of service
    """
    if not hire_date:
        return 0
    
    end_date = end_date or timezone.now().date()
    service_period = end_date - hire_date
    return round(service_period.days / 365.25, 2)


def get_hijri_date(gregorian_date=None):
    """
    تحويل التاريخ الميلادي إلى هجري
    Convert Gregorian date to Hijri (basic approximation)
    """
    if gregorian_date is None:
        gregorian_date = timezone.now().date()
    
    # This is a basic approximation
    # For accurate conversion, use a proper Hijri calendar library
    hijri_year = gregorian_date.year - 579
    return f"{gregorian_date.day}/{gregorian_date.month}/{hijri_year}هـ"


def send_email_notification(to_email, subject, message, from_email=None):
    """
    إرسال إشعار بالبريد الإلكتروني
    Send email notification
    """
    try:
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email] if isinstance(to_email, str) else to_email,
            fail_silently=False,
        )
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send email: {e}")
        return False


def generate_password(length=12, include_special=True):
    """
    توليد كلمة مرور عشوائية
    Generate random password
    """
    characters = string.ascii_letters + string.digits
    if include_special:
        characters += "!@#$%^&*"
    
    password = ''.join(random.choices(characters, k=length))
    return password


def slugify_arabic(text):
    """
    تحويل النص العربي إلى slug
    Convert Arabic text to URL-friendly slug
    """
    import re
    from django.utils.text import slugify
    
    # Replace Arabic characters with transliteration
    arabic_to_latin = {
        'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h',
        'خ': 'kh', 'د': 'd', 'ذ': 'th', 'ر': 'r', 'ز': 'z', 'س': 's',
        'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': 'a',
        'غ': 'gh', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm',
        'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a', 'ة': 'h',
        'أ': 'a', 'إ': 'i', 'آ': 'a', 'ؤ': 'o', 'ئ': 'e'
    }
    
    # Replace Arabic characters
    for arabic, latin in arabic_to_latin.items():
        text = text.replace(arabic, latin)
    
    # Use Django's slugify for the rest
    return slugify(text)


def format_file_size(size_bytes):
    """
    تنسيق حجم الملف
    Format file size in human readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def get_file_extension(filename):
    """
    الحصول على امتداد الملف
    Get file extension
    """
    import os
    return os.path.splitext(filename)[1].lower()


def is_image_file(filename):
    """
    فحص ما إذا كان الملف صورة
    Check if file is an image
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return get_file_extension(filename) in image_extensions


def is_document_file(filename):
    """
    فحص ما إذا كان الملف وثيقة
    Check if file is a document
    """
    document_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
    return get_file_extension(filename) in document_extensions


def truncate_text(text, max_length=100, suffix='...'):
    """
    اقتطاع النص
    Truncate text to specified length
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def clean_phone_number(phone):
    """
    تنظيف رقم الهاتف
    Clean phone number (remove non-digits)
    """
    if not phone:
        return ''
    
    return ''.join(filter(str.isdigit, phone))


def mask_sensitive_data(data, mask_char='*', visible_chars=4):
    """
    إخفاء البيانات الحساسة
    Mask sensitive data (like credit card numbers)
    """
    if not data or len(data) <= visible_chars:
        return data
    
    visible_part = data[-visible_chars:]
    masked_part = mask_char * (len(data) - visible_chars)
    return masked_part + visible_part


def get_quarter_from_date(date_obj):
    """
    الحصول على الربع من التاريخ
    Get quarter from date
    """
    month = date_obj.month
    if month <= 3:
        return 1
    elif month <= 6:
        return 2
    elif month <= 9:
        return 3
    else:
        return 4


def get_week_number(date_obj):
    """
    الحصول على رقم الأسبوع
    Get week number from date
    """
    return date_obj.isocalendar()[1]


def business_days_between(start_date, end_date):
    """
    حساب أيام العمل بين تاريخين
    Calculate business days between two dates
    """
    from datetime import timedelta
    
    current_date = start_date
    business_days = 0
    
    while current_date <= end_date:
        # Monday = 0, Sunday = 6
        # In Saudi Arabia, weekend is Friday (4) and Saturday (5)
        if current_date.weekday() not in [4, 5]:  # Not Friday or Saturday
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days


def add_business_days(start_date, days_to_add):
    """
    إضافة أيام عمل إلى تاريخ
    Add business days to a date
    """
    from datetime import timedelta
    
    current_date = start_date
    days_added = 0
    
    while days_added < days_to_add:
        current_date += timedelta(days=1)
        # Skip weekends (Friday and Saturday in Saudi Arabia)
        if current_date.weekday() not in [4, 5]:
            days_added += 1
    
    return current_date


def generate_qr_code(data, size=10):
    """
    توليد رمز QR
    Generate QR code (requires qrcode library)
    """
    try:
        import qrcode
        from io import BytesIO
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
        
    except ImportError:
        # qrcode library not installed
        return None