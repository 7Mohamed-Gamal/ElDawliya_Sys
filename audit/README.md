# تطبيق سجلات التدقيق (Audit Application)

## نظرة عامة (Application Overview)

تطبيق سجلات التدقيق مسؤول عن تسجيل ومراقبة جميع العمليات والأنشطة في نظام الدولية. يوفر نظام تدقيق شامل لتتبع تغييرات البيانات، عمليات المستخدمين، والأنشطة الأمنية مع إمكانيات بحث وتحليل متقدمة.

**الغرض الرئيسي**: تسجيل شامل لجميع العمليات والأنشطة لضمان الأمان والمساءلة.

## الميزات الرئيسية (Key Features)

### 1. تسجيل العمليات (Operation Logging)
- تسجيل تلقائي لجميع عمليات CRUD
- تتبع تغييرات البيانات
- تسجيل عمليات تسجيل الدخول والخروج
- مراقبة الأنشطة الحساسة
- تسجيل محاولات الوصول المرفوضة

### 2. معلومات مفصلة (Detailed Information)
- معلومات المستخدم والجلسة
- عنوان IP ومعلومات المتصفح
- تفاصيل الكائن المتأثر
- بيانات التغييرات (قبل وبعد)
- الوقت الدقيق للعملية

### 3. البحث والفلترة (Search & Filtering)
- بحث متقدم في السجلات
- فلترة حسب المستخدم والتاريخ
- فلترة حسب نوع العملية
- فلترة حسب التطبيق والنموذج
- تصدير نتائج البحث

### 4. التقارير والتحليلات (Reports & Analytics)
- تقارير النشاط اليومي/الشهري
- إحصائيات المستخدمين
- تحليل الأنماط الأمنية
- تنبيهات الأنشطة المشبوهة
- رسوم بيانية للأنشطة

### 5. الأمان والامتثال (Security & Compliance)
- حماية سجلات التدقيق من التلاعب
- نسخ احتياطية آمنة
- الامتثال لمعايير التدقيق
- تشفير البيانات الحساسة
- سياسات الاحتفاظ بالسجلات

## هيكل النماذج (Models Documentation)

### AuditLog (سجل التدقيق)
```python
class AuditLog(models.Model):
    # أنواع العمليات
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    VIEW = 'VIEW'
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'
    OTHER = 'OTHER'

    ACTION_CHOICES = [
        (CREATE, 'إنشاء'),
        (UPDATE, 'تحديث'),
        (DELETE, 'حذف'),
        (VIEW, 'عرض'),
        (LOGIN, 'تسجيل دخول'),
        (LOGOUT, 'تسجيل خروج'),
        (OTHER, 'أخرى'),
    ]

    # معلومات المستخدم
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # المستخدم

    # تفاصيل العملية
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)    # الإجراء
    timestamp = models.DateTimeField(auto_now_add=True)                 # وقت الإجراء
    ip_address = models.GenericIPAddressField(null=True, blank=True)    # عنوان IP
    user_agent = models.TextField(null=True, blank=True)                # معلومات المتصفح
    app_name = models.CharField(max_length=100, null=True, blank=True)  # اسم التطبيق

    # معلومات الكائن المتأثر
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True) # نوع المحتوى
    object_id = models.CharField(max_length=255, null=True, blank=True) # معرف الكائن
    content_object = GenericForeignKey('content_type', 'object_id')     # الكائن المرتبط

    # تفاصيل إضافية
    object_repr = models.CharField(max_length=255, null=True, blank=True) # وصف الكائن
    action_details = models.TextField(null=True, blank=True)            # تفاصيل الإجراء
    change_data = models.JSONField(null=True, blank=True)               # بيانات التغييرات
```

### خصائص النموذج (Model Properties)
- **الفهرسة المحسنة**: فهارس على الحقول المستخدمة في البحث
- **العلاقات العامة**: استخدام GenericForeignKey لربط أي نموذج
- **البيانات المرنة**: حقل JSON لتخزين بيانات التغييرات
- **الأمان**: حماية من الحذف العرضي للسجلات

## العروض (Views Documentation)

### AuditLogListView
```python
class AuditLogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """عرض قائمة سجلات التدقيق"""
    model = AuditLog
    template_name = 'audit/log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    permission_required = 'audit.view_auditlog'

    def get_queryset(self):
        # فلترة حسب المستخدم والتاريخ ونوع العملية
        # البحث والترتيب
        # تطبيق الصلاحيات
```

### audit_dashboard
```python
@login_required
@permission_required('audit.view_auditlog')
def audit_dashboard(request):
    """لوحة تحكم سجلات التدقيق"""
    # إحصائيات اليوم والأسبوع
    # أكثر المستخدمين نشاطاً
    # أكثر العمليات تكراراً
    # السجلات الحديثة
```

## الإشارات (Signals)

### تسجيل تلقائي للعمليات
```python
@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """تسجيل عمليات الحفظ"""
    action = AuditLog.CREATE if created else AuditLog.UPDATE
    # إنشاء سجل التدقيق

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """تسجيل عمليات الحذف"""
    # إنشاء سجل الحذف

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """تسجيل عمليات تسجيل الدخول"""
    # تسجيل الدخول الناجح

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """تسجيل عمليات تسجيل الخروج"""
    # تسجيل الخروج
```

## الأدوات المساعدة (Utilities)

### دوال مساعدة
```python
def get_client_ip(request):
    """الحصول على عنوان IP الحقيقي للعميل"""

def get_change_data(instance, created):
    """الحصول على بيانات التغييرات"""

def log_custom_action(user, action, details, obj=None, app_name=None):
    """تسجيل عملية مخصصة"""
```

## كيفية الاستخدام (Usage)

### التسجيل التلقائي
تم تكوين middleware لتسجيل معظم العمليات تلقائياً

### التسجيل اليدوي
```python
from audit.utils import log_custom_action

# تسجيل عملية مخصصة
log_custom_action(
    user=request.user,
    action='CUSTOM_ACTION',
    details='تم تنفيذ عملية مخصصة',
    app_name='my_app'
)
```

### الوصول إلى السجلات
- واجهة المستخدم: `/audit/`
- لوحة الإدارة: قسم "سجلات التدقيق"

## الصلاحيات (Permissions)
- مدير (is_superuser)
- طاقم إداري (is_staff)
- صلاحية خاصة: 'audit.view_auditlog'

## التكامل مع التطبيقات الأخرى (Integration)

### تسجيل العمليات في التطبيقات الأخرى
```python
from audit.utils import log_custom_action

def my_view(request):
    # تنفيذ العملية
    result = perform_some_action()

    # تسجيل العملية
    log_custom_action(
        user=request.user,
        action='CUSTOM_ACTION',
        details='تم تنفيذ عملية مخصصة',
        app_name='my_app'
    )
```

### Middleware للتسجيل التلقائي
```python
class AuditMiddleware:
    """Middleware لتسجيل العمليات تلقائياً"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # حفظ المستخدم وتسجيل العمليات
        response = self.get_response(request)
        return response
```

---

**تم إنشاء هذا التوثيق في**: 2025-06-16
**الإصدار**: 1.0
**المطور**: فريق تطوير نظام الدولية
