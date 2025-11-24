"""
مدققات البيانات المخصصة
Custom data validators
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_saudi_id(value):
    """
    التحقق من صحة رقم الهوية السعودية
    Validate Saudi national ID number
    """
    if not value:
        return

    # Remove any non-digit characters
    id_number = ''.join(filter(str.isdigit, str(value)))

    # Check length
    if len(id_number) != 10:
        raise ValidationError(_('رقم الهوية يجب أن يكون 10 أرقام'))

    # Check if it starts with 1 or 2
    if not id_number.startswith(('1', '2')):
        raise ValidationError(_('رقم الهوية يجب أن يبدأ بـ 1 أو 2'))

    # Validate using Luhn algorithm (modified for Saudi ID)
    def luhn_checksum(card_num):
        """luhn_checksum function"""
        def digits_of(n):
            """digits_of function"""
            return [int(d) for d in str(n)]

        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10

    if luhn_checksum(id_number) != 0:
        raise ValidationError(_('رقم الهوية غير صحيح'))


def validate_phone_number(value):
    """
    التحقق من صحة رقم الهاتف السعودي
    Validate Saudi phone number
    """
    if not value:
        return

    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, str(value)))

    # Remove country code if present
    if phone.startswith('966'):
        phone = phone[3:]
    elif phone.startswith('0'):
        phone = phone[1:]

    # Check length (should be 9 digits)
    if len(phone) != 9:
        raise ValidationError(_('رقم الهاتف يجب أن يكون 9 أرقام'))

    # Check if it starts with valid mobile prefixes
    valid_prefixes = ['50', '51', '52', '53', '54', '55', '56', '57', '58', '59']
    if not any(phone.startswith(prefix) for prefix in valid_prefixes):
        raise ValidationError(_('رقم الهاتف غير صحيح'))


def validate_iban(value):
    """
    التحقق من صحة رقم الآيبان السعودي
    Validate Saudi IBAN number
    """
    if not value:
        return

    # Remove spaces and convert to uppercase
    iban = ''.join(value.split()).upper()

    # Check if it starts with SA
    if not iban.startswith('SA'):
        raise ValidationError(_('رقم الآيبان يجب أن يبدأ بـ SA'))

    # Check length (Saudi IBAN is 24 characters)
    if len(iban) != 24:
        raise ValidationError(_('رقم الآيبان يجب أن يكون 24 حرف'))

    # Check if the rest are digits
    if not iban[2:].isdigit():
        raise ValidationError(_('رقم الآيبان يحتوي على أحرف غير صحيحة'))

    # Validate using IBAN checksum algorithm
    def iban_checksum(iban):
        """iban_checksum function"""
        # Move first 4 characters to end
        rearranged = iban[4:] + iban[:4]

        # Replace letters with numbers (A=10, B=11, ..., Z=35)
        numeric = ''
        for char in rearranged:
            if char.isdigit():
                numeric += char
            else:
                numeric += str(ord(char) - ord('A') + 10)

        # Calculate mod 97
        return int(numeric) % 97

    if iban_checksum(iban) != 1:
        raise ValidationError(_('رقم الآيبان غير صحيح'))


def validate_email_domain(value, allowed_domains=None):
    """
    التحقق من نطاق البريد الإلكتروني
    Validate email domain
    """
    if not value or not allowed_domains:
        return

    domain = value.split('@')[-1].lower()
    if domain not in [d.lower() for d in allowed_domains]:
        raise ValidationError(
            _('البريد الإلكتروني يجب أن يكون من النطاقات المسموحة: %(domains)s') %
            {'domains': ', '.join(allowed_domains)}
        )


def validate_password_strength(value):
    """
    التحقق من قوة كلمة المرور
    Validate password strength
    """
    if not value:
        return

    errors = []

    # Check minimum length
    if len(value) < 8:
        errors.append(_('كلمة المرور يجب أن تكون 8 أحرف على الأقل'))

    # Check for uppercase letter
    if not re.search(r'[A-Z]', value):
        errors.append(_('كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل'))

    # Check for lowercase letter
    if not re.search(r'[a-z]', value):
        errors.append(_('كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل'))

    # Check for digit
    if not re.search(r'\d', value):
        errors.append(_('كلمة المرور يجب أن تحتوي على رقم واحد على الأقل'))

    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        errors.append(_('كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل'))

    if errors:
        raise ValidationError(errors)


def validate_file_size(value, max_size_mb=5):
    """
    التحقق من حجم الملف
    Validate file size
    """
    if not value:
        return

    max_size_bytes = max_size_mb * 1024 * 1024
    if value.size > max_size_bytes:
        raise ValidationError(
            _('حجم الملف يجب أن يكون أقل من %(max_size)s ميجابايت') %
            {'max_size': max_size_mb}
        )


def validate_file_extension(value, allowed_extensions=None):
    """
    التحقق من امتداد الملف
    Validate file extension
    """
    if not value or not allowed_extensions:
        return

    import os
    ext = os.path.splitext(value.name)[1].lower()

    if ext not in [e.lower() for e in allowed_extensions]:
        raise ValidationError(
            _('امتداد الملف غير مسموح. الامتدادات المسموحة: %(extensions)s') %
            {'extensions': ', '.join(allowed_extensions)}
        )


def validate_image_file(value):
    """
    التحقق من أن الملف صورة
    Validate that file is an image
    """
    if not value:
        return

    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    validate_file_extension(value, allowed_extensions)

    # Additional validation using PIL (if available)
    try:
        from PIL import Image
        img = Image.open(value)
        img.verify()
    except ImportError:
        # PIL not available, skip advanced validation
        pass
    except Exception:
        raise ValidationError(_('الملف ليس صورة صحيحة'))


def validate_date_range(start_date, end_date):
    """
    التحقق من صحة نطاق التاريخ
    Validate date range
    """
    if start_date and end_date and start_date > end_date:
        raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية'))


def validate_positive_number(value):
    """
    التحقق من أن الرقم موجب
    Validate that number is positive
    """
    if value is not None and value < 0:
        raise ValidationError(_('القيمة يجب أن تكون موجبة'))


def validate_percentage(value):
    """
    التحقق من صحة النسبة المئوية
    Validate percentage (0-100)
    """
    if value is not None and (value < 0 or value > 100):
        raise ValidationError(_('النسبة المئوية يجب أن تكون بين 0 و 100'))


def validate_working_hours(start_time, end_time):
    """
    التحقق من صحة ساعات العمل
    Validate working hours
    """
    if start_time and end_time and start_time >= end_time:
        raise ValidationError(_('وقت البداية يجب أن يكون قبل وقت النهاية'))


def validate_salary_range(basic_salary, min_salary=None, max_salary=None):
    """
    التحقق من نطاق الراتب
    Validate salary range
    """
    if basic_salary is None:
        return

    if min_salary and basic_salary < min_salary:
        raise ValidationError(
            _('الراتب الأساسي يجب أن يكون أكبر من %(min_salary)s') %
            {'min_salary': min_salary}
        )

    if max_salary and basic_salary > max_salary:
        raise ValidationError(
            _('الراتب الأساسي يجب أن يكون أقل من %(max_salary)s') %
            {'max_salary': max_salary}
        )


def validate_unique_in_queryset(value, queryset, field_name, exclude_id=None):
    """
    التحقق من عدم تكرار القيمة في مجموعة البيانات
    Validate uniqueness in queryset
    """
    if not value:
        return

    qs = queryset.filter(**{field_name: value})
    if exclude_id:
        qs = qs.exclude(id=exclude_id)

    if qs.exists():
        raise ValidationError(_('هذه القيمة موجودة بالفعل'))


def validate_business_email(value):
    """
    التحقق من البريد الإلكتروني التجاري
    Validate business email (exclude common personal email providers)
    """
    if not value:
        return

    personal_domains = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'live.com', 'msn.com', 'aol.com', 'icloud.com'
    ]

    domain = value.split('@')[-1].lower()
    if domain in personal_domains:
        raise ValidationError(_('يرجى استخدام بريد إلكتروني تجاري وليس شخصي'))


def validate_arabic_text(value):
    """
    التحقق من أن النص يحتوي على أحرف عربية
    Validate that text contains Arabic characters
    """
    if not value:
        return

    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    if not arabic_pattern.search(value):
        raise ValidationError(_('النص يجب أن يحتوي على أحرف عربية'))


def validate_english_text(value):
    """
    التحقق من أن النص يحتوي على أحرف إنجليزية فقط
    Validate that text contains only English characters
    """
    if not value:
        return

    english_pattern = re.compile(r'^[a-zA-Z0-9\s\-_.]+$')
    if not english_pattern.match(value):
        raise ValidationError(_('النص يجب أن يحتوي على أحرف إنجليزية فقط'))
