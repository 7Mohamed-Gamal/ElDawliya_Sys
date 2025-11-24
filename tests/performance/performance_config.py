"""
إعدادات اختبارات الأداء
Performance Testing Configuration
"""

# ================================================================
# معايير الأداء المستهدفة
# Performance Benchmarks
# ================================================================

# أوقات الاستجابة المستهدفة (بالميلي ثانية)
RESPONSE_TIME_TARGETS = {
    'homepage': 500,           # الصفحة الرئيسية
    'list_pages': 1000,        # صفحات القوائم
    'detail_pages': 800,       # صفحات التفاصيل
    'form_pages': 600,         # صفحات النماذج
    'api_endpoints': 300,      # نقاط API
    'search_pages': 1200,      # صفحات البحث
}

# معايير التحميل المتزامن
LOAD_TEST_TARGETS = {
    'light_load': {
        'users': 5,
        'success_rate': 95,    # نسبة النجاح المطلوبة
        'avg_response_time': 1000,
    },
    'medium_load': {
        'users': 10,
        'success_rate': 90,
        'avg_response_time': 2000,
    },
    'heavy_load': {
        'users': 20,
        'success_rate': 80,
        'avg_response_time': 5000,
    },
    'stress_test': {
        'users': 50,
        'success_rate': 70,
        'avg_response_time': 10000,
    }
}

# معايير استهلاك الذاكرة (بالميجابايت)
MEMORY_USAGE_TARGETS = {
    'page_load_increase': 50,      # الزيادة المسموحة لكل صفحة
    'total_session_increase': 100,  # الزيادة الإجمالية للجلسة
    'memory_leak_threshold': 20,    # حد تسريب الذاكرة
    'concurrent_requests_increase': 100,  # الزيادة مع الطلبات المتزامنة
}

# معايير قاعدة البيانات
DATABASE_PERFORMANCE_TARGETS = {
    'max_queries_per_page': 50,     # أقصى عدد استعلامات لكل صفحة
    'avg_query_time': 0.01,         # متوسط وقت الاستعلام (ثانية)
    'slow_query_threshold': 0.1,    # حد الاستعلام البطيء (ثانية)
    'max_slow_queries': 5,          # أقصى عدد استعلامات بطيئة
    'n_plus_one_threshold': 2,      # حد مشكلة N+1
}

# معايير التخزين المؤقت
CACHE_PERFORMANCE_TARGETS = {
    'hit_ratio': 80,               # نسبة إصابة التخزين المؤقت (%)
    'avg_get_time': 5,             # متوسط وقت القراءة (ميلي ثانية)
    'avg_set_time': 10,            # متوسط وقت الكتابة (ميلي ثانية)
    'operations_per_second': 1000, # العمليات في الثانية
}

# معايير استهلاك المعالج
CPU_USAGE_TARGETS = {
    'max_cpu_usage': 80,           # أقصى استهلاك للمعالج (%)
    'avg_cpu_usage': 50,           # متوسط استهلاك المعالج (%)
    'cpu_spike_threshold': 90,     # حد ارتفاع استهلاك المعالج
}

# ================================================================
# إعدادات الاختبارات
# Test Configuration
# ================================================================

# إعدادات عامة
GENERAL_TEST_CONFIG = {
    'default_iterations': 5,       # عدد التكرارات الافتراضي
    'warmup_requests': 2,          # طلبات الإحماء
    'timeout_seconds': 30,         # مهلة الاختبار
    'retry_attempts': 3,           # محاولات الإعادة
    'cleanup_after_test': True,    # تنظيف بعد الاختبار
}

# إعدادات اختبارات التحميل
LOAD_TEST_CONFIG = {
    'ramp_up_time': 10,           # وقت زيادة التحميل (ثانية)
    'test_duration': 60,          # مدة الاختبار (ثانية)
    'think_time': 1,              # وقت التفكير بين الطلبات (ثانية)
    'max_concurrent_users': 100,   # أقصى عدد مستخدمين متزامنين
}

# إعدادات مراقبة الذاكرة
MEMORY_MONITORING_CONFIG = {
    'sampling_interval': 1,        # فترة أخذ العينات (ثانية)
    'gc_before_measurement': True, # تنظيف الذاكرة قبل القياس
    'detailed_tracking': True,     # تتبع مفصل للذاكرة
}

# إعدادات قاعدة البيانات
DATABASE_TEST_CONFIG = {
    'enable_query_logging': True,  # تفعيل تسجيل الاستعلامات
    'analyze_query_patterns': True, # تحليل أنماط الاستعلامات
    'check_indexes': True,         # فحص الفهارس
    'connection_pooling': True,    # تجميع الاتصالات
}

# ================================================================
# URLs للاختبار
# Test URLs
# ================================================================

# URLs الأساسية للاختبار
TEST_URLS = {
    'homepage': [
        ('administrator:dashboard', 'الصفحة الرئيسية'),
    ],
    'hr_pages': [
        ('Hr:employee_list', 'قائمة الموظفين'),
        ('Hr:department_list', 'قائمة الأقسام'),
        ('Hr:job_list', 'قائمة الوظائف'),
        ('Hr:salary_list', 'قائمة الرواتب'),
    ],
    'inventory_pages': [
        ('inventory:product_list', 'قائمة المنتجات'),
        ('inventory:supplier_list', 'قائمة الموردين'),
        ('inventory:invoice_list', 'قائمة الفواتير'),
        ('inventory:category_list', 'قائمة التصنيفات'),
    ],
    'api_endpoints': [
        ('api:employee-list', 'API الموظفين'),
        ('api:department-list', 'API الأقسام'),
        ('api:product-list', 'API المنتجات'),
        ('api:supplier-list', 'API الموردين'),
    ],
    'reports_pages': [
        ('reports:employee_report', 'تقرير الموظفين'),
        ('reports:attendance_report', 'تقرير الحضور'),
        ('reports:inventory_report', 'تقرير المخزون'),
    ]
}

# URLs للاختبارات المتقدمة
ADVANCED_TEST_URLS = {
    'search_pages': [
        ('Hr:employee_search', 'البحث في الموظفين'),
        ('inventory:product_search', 'البحث في المنتجات'),
    ],
    'form_pages': [
        ('Hr:employee_add', 'إضافة موظف'),
        ('inventory:product_add', 'إضافة منتج'),
    ],
    'heavy_pages': [
        ('reports:detailed_report', 'التقرير المفصل'),
        ('analytics:dashboard', 'لوحة التحليلات'),
    ]
}

# ================================================================
# إعدادات التقارير
# Reporting Configuration
# ================================================================

REPORTING_CONFIG = {
    'generate_charts': True,       # إنتاج الرسوم البيانية
    'save_raw_data': True,         # حفظ البيانات الخام
    'export_formats': ['json', 'csv', 'html'],  # تنسيقات التصدير
    'include_recommendations': True, # تضمين التوصيات
    'detailed_analysis': True,     # التحليل المفصل
}

# مستويات التنبيهات
ALERT_LEVELS = {
    'info': {
        'color': 'green',
        'icon': '✅',
        'description': 'معلومات عامة'
    },
    'warning': {
        'color': 'yellow',
        'icon': '⚠️',
        'description': 'تحذير - يحتاج انتباه'
    },
    'error': {
        'color': 'red',
        'icon': '❌',
        'description': 'خطأ - يحتاج إصلاح فوري'
    },
    'critical': {
        'color': 'red',
        'icon': '🚨',
        'description': 'حرج - يحتاج تدخل عاجل'
    }
}

# ================================================================
# إعدادات البيئة
# Environment Configuration
# ================================================================

# إعدادات بيئة الاختبار
TEST_ENVIRONMENT = {
    'use_test_database': True,     # استخدام قاعدة بيانات الاختبار
    'disable_migrations': False,   # تعطيل الهجرات
    'use_in_memory_cache': False,  # استخدام تخزين مؤقت في الذاكرة
    'debug_mode': True,            # وضع التشخيص
    'log_level': 'INFO',           # مستوى السجلات
}

# إعدادات الأمان للاختبارات
SECURITY_CONFIG = {
    'create_test_users': True,     # إنشاء مستخدمين للاختبار
    'cleanup_test_data': True,     # تنظيف بيانات الاختبار
    'isolate_tests': True,         # عزل الاختبارات
    'use_transactions': True,      # استخدام المعاملات
}

# ================================================================
# دوال المساعدة
# Helper Functions
# ================================================================

def get_target_for_page_type(page_type):
    """الحصول على الهدف المحدد لنوع الصفحة"""
    return RESPONSE_TIME_TARGETS.get(page_type, RESPONSE_TIME_TARGETS['list_pages'])

def get_load_test_config(test_type):
    """الحصول على إعدادات اختبار التحميل"""
    return LOAD_TEST_CONFIG.get(test_type, LOAD_TEST_TARGETS['light_load'])

def is_performance_acceptable(metric_name, value, target_type='response_time'):
    """فحص ما إذا كان الأداء مقبولاً"""
    if target_type == 'response_time':
        target = RESPONSE_TIME_TARGETS.get(metric_name, 1000)
        return value <= target
    elif target_type == 'memory':
        target = MEMORY_USAGE_TARGETS.get(metric_name, 100)
        return value <= target
    elif target_type == 'database':
        target = DATABASE_PERFORMANCE_TARGETS.get(metric_name, 50)
        return value <= target

    return True

def get_alert_level(metric_name, value, target_type='response_time'):
    """تحديد مستوى التنبيه بناءً على القيمة"""
    if is_performance_acceptable(metric_name, value, target_type):
        return 'info'

    # تحديد مستوى التنبيه بناءً على مدى تجاوز الهدف
    if target_type == 'response_time':
        target = RESPONSE_TIME_TARGETS.get(metric_name, 1000)
        ratio = value / target

        if ratio <= 1.2:  # 20% زيادة
            return 'warning'
        elif ratio <= 2.0:  # 100% زيادة
            return 'error'
        else:
            return 'critical'

    return 'warning'
