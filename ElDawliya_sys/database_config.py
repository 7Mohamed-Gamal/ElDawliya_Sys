"""
إعدادات قاعدة البيانات المحسنة لنظام الموارد البشرية
"""

import os
from django.core.exceptions import ImproperlyConfigured

def get_database_config():
    """
    إرجاع إعدادات قاعدة البيانات المحسنة
    """

    # إعدادات قاعدة البيانات الأساسية
    default_db_config = {
        'ENGINE': 'mssql',
        'NAME': os.environ.get('DB_NAME', 'ElDawliya_Sys'),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', '1433'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'no',
            'MARS_Connection': 'yes',  # تفعيل Multiple Active Result Sets
            'charset': 'utf8',
            'collation': 'Arabic_CI_AS',  # ترتيب عربي
            'init_command': "SET NAMES 'utf8' COLLATE 'utf8_unicode_ci'",
            'autocommit': True,
            'isolation_level': 'read committed',
            'timeout': 30,  # مهلة الاتصال
            'query_timeout': 60,  # مهلة الاستعلام
            'connection_timeout': 30,  # مهلة الاتصال
            'command_timeout': 60,  # مهلة الأمر
            'pool_size': 10,  # حجم مجموعة الاتصالات
            'max_overflow': 20,  # الحد الأقصى للاتصالات الإضافية
            'pool_recycle': 3600,  # إعادة تدوير الاتصالات كل ساعة
            'pool_pre_ping': True,  # فحص الاتصال قبل الاستخدام
        },
        'TEST': {
            'NAME': 'test_ElDawliya_Sys',
            'CHARSET': 'utf8',
            'COLLATION': 'Arabic_CI_AS',
        }
    }

    # إعدادات قاعدة البيانات الاحتياطية
    backup_db_config = {
        'ENGINE': 'mssql',
        'NAME': os.environ.get('BACKUP_DB_NAME', 'ElDawliya_Sys'),
        'HOST': os.environ.get('BACKUP_DB_HOST', ''),
        'PORT': os.environ.get('BACKUP_DB_PORT', '1433'),
        'USER': os.environ.get('BACKUP_DB_USER', ''),
        'PASSWORD': os.environ.get('BACKUP_DB_PASSWORD', '')
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Trusted_Connection': 'yes',
            'MARS_Connection': 'yes',
            'charset': 'utf8',
            'collation': 'Arabic_CI_AS',
            'init_command': "SET NAMES 'utf8' COLLATE 'utf8_unicode_ci'",
            'autocommit': True,
            'isolation_level': 'read committed',
            'timeout': 30,
            'query_timeout': 60,
            'connection_timeout': 30,
            'command_timeout': 60,
            'pool_size': 10,
            'max_overflow': 20,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
        },
        'TEST': {
            'NAME': 'test_ElDawliya_Sys_backup',
            'CHARSET': 'utf8',
            'COLLATION': 'Arabic_CI_AS',
        }
    }

    # إعدادات قاعدة بيانات للقراءة فقط (للتقارير)
    readonly_db_config = default_db_config.copy()
    readonly_db_config['OPTIONS']['readonly'] = True
    readonly_db_config['OPTIONS']['autocommit'] = False

    # إعدادات قاعدة بيانات للتحليلات
    analytics_db_config = default_db_config.copy()
    analytics_db_config['NAME'] = os.environ.get('ANALYTICS_DB_NAME', 'ElDawliya_Analytics')
    analytics_db_config['OPTIONS']['pool_size'] = 5  # حجم أصغر للتحليلات

    return {
        'default': default_db_config,
        'primary': backup_db_config,
        'readonly': readonly_db_config,
        'analytics': analytics_db_config,
    }

def get_database_router_config():
    """
    إعدادات توجيه قاعدة البيانات
    """
    return {
        'hr_models': ['Hr', 'employee_tasks', 'attendance'],
        'analytics_models': ['reports', 'analytics'],
        'readonly_operations': ['select', 'count', 'exists'],
        'write_operations': ['insert', 'update', 'delete'],
    }

# إعدادات الفهارس المحسنة
DATABASE_INDEXES = {
    'Hr_employee': [
        ['employee_number'],
        ['national_id'],
        ['email'],
        ['department_id', 'is_active'],
        ['hire_date'],
        ['created_at'],
    ],
    'Hr_attendance': [
        ['employee_id', 'date'],
        ['date', 'shift_id'],
        ['check_in_time'],
        ['check_out_time'],
    ],
    'Hr_payroll': [
        ['employee_id', 'pay_period'],
        ['pay_period'],
        ['created_at'],
    ],
    'Hr_leave_request': [
        ['employee_id', 'status'],
        ['start_date', 'end_date'],
        ['leave_type_id'],
        ['created_at'],
    ],
}

# إعدادات التحسين
DATABASE_OPTIMIZATION = {
    'connection_pooling': True,
    'query_caching': True,
    'prepared_statements': True,
    'bulk_operations': True,
    'lazy_loading': True,
    'select_related_depth': 2,
    'prefetch_related_lookups': 3,
}

# إعدادات المراقبة
DATABASE_MONITORING = {
    'slow_query_threshold': 1.0,  # ثانية
    'log_queries': True,
    'log_slow_queries': True,
    'monitor_connections': True,
    'alert_on_errors': True,
}

# إعدادات النسخ الاحتياطي
DATABASE_BACKUP = {
    'enabled': True,
    'schedule': '0 2 * * *',  # يومياً في الساعة 2 صباحاً
    'retention_days': 30,
    'compress': True,
    'encrypt': True,
    'verify_integrity': True,
    'backup_types': ['full', 'differential', 'transaction_log'],
}

def validate_database_config():
    """
    التحقق من صحة إعدادات قاعدة البيانات
    """
    required_env_vars = [
        'DB_NAME', 'DB_HOST', 'DB_USER', 'DB_PASSWORD'
    ]

    missing_vars = []
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        raise ImproperlyConfigured(
            f"المتغيرات البيئية التالية مطلوبة: {', '.join(missing_vars)}"
        )

    return True

def get_connection_string(db_name='default'):
    """
    إنشاء نص الاتصال بقاعدة البيانات
    """
    config = get_database_config()[db_name]

    connection_string = (
        f"DRIVER={{{config['OPTIONS']['driver']}}};"
        f"SERVER={config['HOST']},{config['PORT']};"
        f"DATABASE={config['NAME']};"
        f"UID={config['USER']};"
        f"PWD={config['PASSWORD']};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=yes;"
        f"Connection Timeout={config['OPTIONS']['connection_timeout']};"
        f"Command Timeout={config['OPTIONS']['command_timeout']};"
    )

    return connection_string

def test_database_connection(db_name='default'):
    """
    اختبار الاتصال بقاعدة البيانات
    """
    import pyodbc

    try:
        connection_string = get_connection_string(db_name)
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        connection.close()
        return True, "الاتصال ناجح"
    except Exception as e:
        return False, f"فشل الاتصال: {str(e)}"

# إعدادات الأداء المتقدمة
PERFORMANCE_SETTINGS = {
    'connection_pool_size': 20,
    'max_connections': 100,
    'query_timeout': 30,
    'connection_timeout': 10,
    'retry_attempts': 3,
    'retry_delay': 1,  # ثانية
    'health_check_interval': 60,  # ثانية
    'maintenance_window': '02:00-04:00',  # نافزة الصيانة
}

# إعدادات الأمان
SECURITY_SETTINGS = {
    'encrypt_connection': True,
    'trust_server_certificate': True,
    'use_ssl': True,
    'verify_ssl_cert': False,
    'connection_encryption': 'required',
    'audit_login_failures': True,
    'max_login_attempts': 5,
    'lockout_duration': 300,  # 5 دقائق
}
