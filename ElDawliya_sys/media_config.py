"""
إعدادات إدارة الملفات والوسائط المتقدمة
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ===== إعدادات الملفات الأساسية =====
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# إنشاء مجلدات الوسائط
MEDIA_SUBDIRS = {
    'employees': 'employees',
    'documents': 'documents',
    'photos': 'photos',
    'signatures': 'signatures',
    'certificates': 'certificates',
    'contracts': 'contracts',
    'reports': 'reports',
    'temp': 'temp',
    'backups': 'backups',
    'exports': 'exports',
}

# إنشاء المجلدات إذا لم تكن موجودة
for subdir in MEDIA_SUBDIRS.values():
    os.makedirs(os.path.join(MEDIA_ROOT, subdir), exist_ok=True)

# ===== إعدادات أنواع الملفات =====
ALLOWED_FILE_TYPES = {
    'documents': {
        'extensions': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'mime_types': [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'application/rtf',
        ],
        'max_size': 10 * 1024 * 1024,  # 10 MB
        'description': 'المستندات والوثائق',
    },
    'images': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'mime_types': [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/webp',
        ],
        'max_size': 5 * 1024 * 1024,  # 5 MB
        'description': 'الصور والرسوم',
    },
    'spreadsheets': {
        'extensions': ['.xls', '.xlsx', '.csv', '.ods'],
        'mime_types': [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/csv',
            'application/vnd.oasis.opendocument.spreadsheet',
        ],
        'max_size': 15 * 1024 * 1024,  # 15 MB
        'description': 'جداول البيانات',
    },
    'archives': {
        'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'mime_types': [
            'application/zip',
            'application/x-rar-compressed',
            'application/x-7z-compressed',
            'application/x-tar',
            'application/gzip',
        ],
        'max_size': 50 * 1024 * 1024,  # 50 MB
        'description': 'الملفات المضغوطة',
    },
    'presentations': {
        'extensions': ['.ppt', '.pptx', '.odp'],
        'mime_types': [
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.oasis.opendocument.presentation',
        ],
        'max_size': 20 * 1024 * 1024,  # 20 MB
        'description': 'العروض التقديمية',
    },
}

# ===== إعدادات الأمان =====
SECURITY_SETTINGS = {
    'scan_uploads': True,  # فحص الملفات المرفوعة
    'quarantine_suspicious': True,  # عزل الملفات المشبوهة
    'virus_scan_enabled': False,  # فحص الفيروسات (يحتاج مكتبة خارجية)
    'max_filename_length': 255,
    'sanitize_filenames': True,  # تنظيف أسماء الملفات
    'allowed_characters': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-أبتثجحخدذرزسشصضطظعغفقكلمنهوي',
    'block_executable_files': True,  # منع الملفات القابلة للتنفيذ
    'check_file_headers': True,  # فحص رؤوس الملفات
}

# الملفات المحظورة
BLOCKED_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
    '.jar', '.app', '.deb', '.pkg', '.dmg', '.iso', '.msi',
    '.php', '.asp', '.jsp', '.py', '.rb', '.pl', '.sh',
]

BLOCKED_MIME_TYPES = [
    'application/x-executable',
    'application/x-msdownload',
    'application/x-msdos-program',
    'application/x-msi',
    'application/x-bat',
    'text/x-php',
    'application/x-httpd-php',
]

# ===== إعدادات المعالجة =====
PROCESSING_SETTINGS = {
    'auto_resize_images': True,
    'max_image_width': 1920,
    'max_image_height': 1080,
    'image_quality': 85,
    'create_thumbnails': True,
    'thumbnail_sizes': [(150, 150), (300, 300), (600, 600)],
    'watermark_images': False,  # يمكن تفعيلها لاحقاً
    'extract_metadata': True,
    'generate_previews': True,
}

# ===== إعدادات التخزين =====
STORAGE_SETTINGS = {
    'use_subdirectories': True,  # تنظيم الملفات في مجلدات فرعية
    'directory_structure': 'year/month',  # هيكل المجلدات
    'duplicate_handling': 'rename',  # كيفية التعامل مع الملفات المكررة
    'cleanup_temp_files': True,
    'temp_file_lifetime': 3600,  # ساعة واحدة
    'backup_uploads': True,
    'compress_old_files': True,
    'archive_after_days': 365,
}

# ===== إعدادات الوصول =====
ACCESS_SETTINGS = {
    'require_authentication': True,
    'check_permissions': True,
    'log_access': True,
    'rate_limit_downloads': True,
    'max_downloads_per_hour': 100,
    'allow_direct_access': False,  # منع الوصول المباشر للملفات
    'use_secure_urls': True,
    'url_expiry_time': 3600,  # ساعة واحدة
}

# ===== إعدادات النسخ الاحتياطي =====
BACKUP_SETTINGS = {
    'auto_backup': True,
    'backup_schedule': '0 3 * * *',  # يومياً في الساعة 3 صباحاً
    'backup_retention': 30,  # 30 يوم
    'backup_location': os.path.join(BASE_DIR, 'backups', 'media'),
    'compress_backups': True,
    'encrypt_backups': True,
    'verify_backups': True,
}

# ===== إعدادات المراقبة =====
MONITORING_SETTINGS = {
    'track_usage': True,
    'log_uploads': True,
    'log_downloads': True,
    'log_deletions': True,
    'monitor_disk_space': True,
    'disk_space_threshold': 85,  # نسبة مئوية
    'alert_on_large_uploads': True,
    'large_file_threshold': 100 * 1024 * 1024,  # 100 MB
}

# ===== دوال المساعدة =====
def get_upload_path(instance, filename, category='documents'):
    """
    إنشاء مسار الرفع للملف
    """
    import datetime
    from django.utils.text import slugify

    # تنظيف اسم الملف
    filename = sanitize_filename(filename)

    # إنشاء مسار بناءً على التاريخ
    now = datetime.datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')

    # إنشاء المسار
    if hasattr(instance, 'employee'):
        employee_id = instance.employee.id
        path = f"{category}/{year}/{month}/employee_{employee_id}/{filename}"
    else:
        path = f"{category}/{year}/{month}/{filename}"

    return path

def sanitize_filename(filename):
    """
    تنظيف اسم الملف
    """
    import re
    from django.utils.text import slugify

    # فصل الاسم والامتداد
    name, ext = os.path.splitext(filename)

    # إزالة الأحرف غير المسموحة
    allowed_chars = SECURITY_SETTINGS['allowed_characters']
    name = ''.join(c for c in name if c in allowed_chars)

    # تحديد الطول
    max_length = SECURITY_SETTINGS['max_filename_length'] - len(ext)
    if len(name) > max_length:
        name = name[:max_length]

    # إضافة الامتداد
    return f"{name}{ext}"

def validate_file(file_obj, category='documents'):
    """
    التحقق من صحة الملف
    """
    errors = []

    if not file_obj:
        errors.append('لم يتم تحديد ملف')
        return errors

    # فحص نوع الملف
    if category not in ALLOWED_FILE_TYPES:
        errors.append(f'نوع الملف غير مدعوم: {category}')
        return errors

    file_config = ALLOWED_FILE_TYPES[category]

    # فحص الامتداد
    file_ext = os.path.splitext(file_obj.name)[1].lower()
    if file_ext not in file_config['extensions']:
        errors.append(f'امتداد الملف غير مسموح: {file_ext}')

    # فحص الحجم
    if file_obj.size > file_config['max_size']:
        max_size_mb = file_config['max_size'] / (1024 * 1024)
        errors.append(f'حجم الملف كبير جداً. الحد الأقصى: {max_size_mb:.1f} MB')

    # فحص نوع MIME
    if hasattr(file_obj, 'content_type'):
        if file_obj.content_type not in file_config['mime_types']:
            errors.append(f'نوع الملف غير مسموح: {file_obj.content_type}')

    # فحص الملفات المحظورة
    if file_ext in BLOCKED_EXTENSIONS:
        errors.append('نوع الملف محظور لأسباب أمنية')

    return errors

def get_file_info(file_path):
    """
    الحصول على معلومات الملف
    """
    import mimetypes
    from datetime import datetime

    if not os.path.exists(file_path):
        return None

    stat = os.stat(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)

    return {
        'name': os.path.basename(file_path),
        'size': stat.st_size,
        'size_human': format_file_size(stat.st_size),
        'mime_type': mime_type,
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'extension': os.path.splitext(file_path)[1].lower(),
    }

def format_file_size(size_bytes):
    """
    تنسيق حجم الملف
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def cleanup_temp_files():
    """
    تنظيف الملفات المؤقتة
    """
    import time

    temp_dir = os.path.join(MEDIA_ROOT, 'temp')
    if not os.path.exists(temp_dir):
        return

    current_time = time.time()
    lifetime = STORAGE_SETTINGS['temp_file_lifetime']

    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getctime(file_path)
            if file_age > lifetime:
                try:
                    os.remove(file_path)
                except OSError:
                    pass

# ===== إعدادات CDN (للمستقبل) =====
CDN_SETTINGS = {
    'enabled': False,
    'provider': 'cloudflare',  # أو 'aws', 'azure', 'gcp'
    'base_url': '',
    'api_key': '',
    'zone_id': '',
    'cache_ttl': 86400,  # 24 ساعة
    'auto_purge': True,
}

# ===== إعدادات الضغط =====
COMPRESSION_SETTINGS = {
    'enabled': True,
    'formats': ['gzip', 'brotli'],
    'level': 6,  # مستوى الضغط (1-9)
    'min_size': 1024,  # الحد الأدنى لحجم الملف للضغط
    'exclude_types': ['image/jpeg', 'image/png', 'image/gif'],  # أنواع مستثناة من الضغط
}
