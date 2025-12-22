# تصميم تنظيف وإكمال نظام الدولية الشامل

## نظرة عامة

هذا التصميم يهدف إلى تنظيف وإعادة هيكلة نظام الدولية بالكامل ليصبح نظاماً احترافياً جاهزاً للعمل على سيرفر داخلي للشركة. النظام سيكون مبنياً على Django 4.2+ وSQL Server مع دعم كامل للغة العربية ونظام RTL، ويتضمن إدارة الموارد البشرية، المخزون، المهام، الاجتماعات، وأوامر الشراء.

## الهيكل المعماري المحسن

### 1. هيكل المشروع المنظم

```
ElDawliya_sys/
├── core/                          # الوحدة الأساسية المشتركة
│   ├── models/                    # النماذج الأساسية المشتركة
│   ├── services/                  # الخدمات المشتركة
│   ├── utils/                     # الأدوات المساعدة
│   ├── permissions/               # نظام الصلاحيات
│   ├── middleware/                # الوسطاء المخصصة
│   └── validators/                # المدققات المخصصة
├── apps/                          # تطبيقات النظام
│   ├── hr/                        # إدارة الموارد البشرية
│   │   ├── employees/             # إدارة الموظفين
│   │   ├── attendance/            # الحضور والانصراف
│   │   ├── payroll/               # الرواتب
│   │   ├── leaves/                # الإجازات
│   │   ├── evaluations/           # التقييمات
│   │   └── training/              # التدريب
│   ├── inventory/                 # إدارة المخزون
│   │   ├── products/              # المنتجات
│   │   ├── suppliers/             # الموردين
│   │   ├── warehouses/            # المخازن
│   │   └── movements/             # حركات المخزون
│   ├── procurement/               # المشتريات
│   │   ├── purchase_orders/       # أوامر الشراء
│   │   ├── quotations/            # عروض الأسعار
│   │   └── contracts/             # العقود
│   ├── projects/                  # إدارة المشاريع
│   │   ├── tasks/                 # المهام
│   │   ├── meetings/              # الاجتماعات
│   │   └── documents/             # الوثائق
│   ├── finance/                   # المالية
│   │   ├── accounts/              # الحسابات
│   │   ├── budgets/               # الميزانيات
│   │   └── reports/               # التقارير المالية
│   └── administration/            # الإدارة العامة
│       ├── users/                 # المستخدمين
│       ├── roles/                 # الأدوار
│       ├── settings/              # الإعدادات
│       └── audit/                 # المراجعة والتدقيق
├── api/                           # واجهات برمجة التطبيقات
│   ├── v1/                        # الإصدار الأول من API
│   ├── authentication/            # المصادقة
│   ├── permissions/               # الصلاحيات
│   └── serializers/               # المسلسلات
├── frontend/                      # الواجهة الأمامية
│   ├── static/                    # الملفات الثابتة
│   │   ├── css/                   # ملفات التنسيق
│   │   ├── js/                    # ملفات JavaScript
│   │   ├── images/                # الصور
│   │   └── fonts/                 # الخطوط
│   ├── templates/                 # القوالب
│   │   ├── base/                  # القوالب الأساسية
│   │   ├── components/            # المكونات القابلة لإعادة الاستخدام
│   │   └── pages/                 # صفحات التطبيق
│   └── assets/                    # الأصول المصدرية
├── config/                        # إعدادات التكوين
│   ├── settings/                  # إعدادات Django
│   ├── urls/                      # توجيه URLs
│   ├── wsgi.py                    # WSGI configuration
│   └── asgi.py                    # ASGI configuration
├── deployment/                    # ملفات النشر
│   ├── docker/                    # Docker configurations
│   ├── nginx/                     # Nginx configurations
│   ├── scripts/                   # سكريبتات النشر
│   └── systemd/                   # خدمات النظام
├── docs/                          # التوثيق
│   ├── api/                       # توثيق API
│   ├── user_guide/                # دليل المستخدم
│   ├── admin_guide/               # دليل المدير
│   └── developer_guide/           # دليل المطور
├── tests/                         # الاختبارات
│   ├── unit/                      # اختبارات الوحدة
│   ├── integration/               # اختبارات التكامل
│   ├── performance/               # اختبارات الأداء
│   └── fixtures/                  # بيانات الاختبار
└── requirements/                  # متطلبات المشروع
    ├── base.txt                   # المتطلبات الأساسية
    ├── development.txt            # متطلبات التطوير
    ├── production.txt             # متطلبات الإنتاج
    └── testing.txt                # متطلبات الاختبار
```

### 2. معمارية قاعدة البيانات المحسنة

#### النماذج الأساسية المشتركة
```python
# core/models/base.py
class BaseModel(models.Model):
    """النموذج الأساسي المشترك"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    class Meta:
        abstract = True

class AuditableModel(BaseModel):
    """نموذج قابل للمراجعة"""
    version = models.PositiveIntegerField(default=1, verbose_name='الإصدار')
    
    class Meta:
        abstract = True
```

#### هيكل قاعدة البيانات المحسن
```sql
-- الجداول الأساسية
CREATE SCHEMA hr;
CREATE SCHEMA inventory;
CREATE SCHEMA procurement;
CREATE SCHEMA projects;
CREATE SCHEMA finance;
CREATE SCHEMA administration;

-- فهارس الأداء
CREATE INDEX idx_employees_active ON hr.employees(is_active, emp_status);
CREATE INDEX idx_attendance_date_emp ON hr.attendance(att_date, employee_id);
CREATE INDEX idx_products_category ON inventory.products(category_id, is_active);
CREATE INDEX idx_tasks_status_assigned ON projects.tasks(status, assigned_to_id);

-- قيود سلامة البيانات
ALTER TABLE hr.employees ADD CONSTRAINT chk_emp_hire_date 
    CHECK (hire_date <= GETDATE());
ALTER TABLE inventory.products ADD CONSTRAINT chk_product_price 
    CHECK (unit_price >= 0);
```

### 3. طبقة الخدمات المحسنة

#### خدمات الأعمال المركزية
```python
# core/services/base.py
class BaseService:
    """الخدمة الأساسية المشتركة"""
    
    def __init__(self, user=None):
        self.user = user
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_action(self, action, obj=None, details=None):
        """تسجيل العمليات"""
        AuditLog.objects.create(
            user=self.user,
            action=action,
            content_object=obj,
            details=details
        )
    
    def check_permission(self, permission, obj=None):
        """فحص الصلاحيات"""
        if not self.user.has_perm(permission, obj):
            raise PermissionDenied(f"لا تملك صلاحية {permission}")

# apps/hr/services/employee_service.py
class EmployeeService(BaseService):
    """خدمة إدارة الموظفين"""
    
    def create_employee(self, data):
        """إنشاء موظف جديد"""
        self.check_permission('hr.add_employee')
        
        with transaction.atomic():
            employee = Employee.objects.create(**data)
            self.log_action('create_employee', employee)
            
            # إنشاء حساب مستخدم
            if data.get('create_user_account'):
                self._create_user_account(employee)
            
            # إرسال إشعار الترحيب
            self._send_welcome_notification(employee)
            
            return employee
    
    def calculate_service_years(self, employee):
        """حساب سنوات الخدمة"""
        if not employee.hire_date:
            return 0
        
        today = date.today()
        service_period = today - employee.hire_date
        return service_period.days / 365.25
```

### 4. واجهات برمجة التطبيقات المحسنة

#### هيكل API المنظم
```python
# api/v1/urls.py
urlpatterns = [
    path('auth/', include('api.v1.authentication.urls')),
    path('hr/', include('api.v1.hr.urls')),
    path('inventory/', include('api.v1.inventory.urls')),
    path('procurement/', include('api.v1.procurement.urls')),
    path('projects/', include('api.v1.projects.urls')),
    path('finance/', include('api.v1.finance.urls')),
    path('admin/', include('api.v1.administration.urls')),
]

# api/v1/hr/views.py
class EmployeeViewSet(viewsets.ModelViewSet):
    """API لإدارة الموظفين"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'job_position', 'emp_status']
    search_fields = ['first_name', 'last_name', 'emp_code', 'email']
    ordering_fields = ['created_at', 'hire_date', 'first_name']
    
    def get_queryset(self):
        """تخصيص الاستعلام حسب الصلاحيات"""
        queryset = super().get_queryset()
        
        if not self.request.user.has_perm('hr.view_all_employees'):
            # عرض موظفي نفس القسم فقط
            queryset = queryset.filter(
                department=self.request.user.employee.department
            )
        
        return queryset.select_related('department', 'job_position', 'manager')
    
    @action(detail=True, methods=['post'])
    def calculate_salary(self, request, pk=None):
        """حساب راتب الموظف"""
        employee = self.get_object()
        service = PayrollService(user=request.user)
        salary_data = service.calculate_employee_salary(employee)
        return Response(salary_data)
```

### 5. نظام الأمان والصلاحيات المتقدم

#### نموذج الصلاحيات الهرمي
```python
# core/models/permissions.py
class Module(models.Model):
    """وحدات النظام"""
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

class Permission(models.Model):
    """الصلاحيات المفصلة"""
    PERMISSION_TYPES = [
        ('view', 'عرض'),
        ('add', 'إضافة'),
        ('change', 'تعديل'),
        ('delete', 'حذف'),
        ('approve', 'موافقة'),
        ('export', 'تصدير'),
        ('import', 'استيراد'),
        ('manage', 'إدارة كاملة'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

class Role(models.Model):
    """الأدوار"""
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission)
    is_system_role = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

class UserRole(models.Model):
    """أدوار المستخدمين"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
```

### 6. واجهة المستخدم المتجاوبة والحديثة

#### نظام التصميم الموحد
```css
/* frontend/static/css/design-system.css */
:root {
    /* الألوان الأساسية */
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --info-color: #06b6d4;
    
    /* الألوان المحايدة */
    --gray-50: #f8fafc;
    --gray-100: #f1f5f9;
    --gray-200: #e2e8f0;
    --gray-300: #cbd5e1;
    --gray-400: #94a3b8;
    --gray-500: #64748b;
    --gray-600: #475569;
    --gray-700: #334155;
    --gray-800: #1e293b;
    --gray-900: #0f172a;
    
    /* الخطوط */
    --font-family-arabic: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    --font-size-xs: 0.75rem;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;
    --font-size-2xl: 1.5rem;
    --font-size-3xl: 1.875rem;
    
    /* المسافات */
    --spacing-1: 0.25rem;
    --spacing-2: 0.5rem;
    --spacing-3: 0.75rem;
    --spacing-4: 1rem;
    --spacing-5: 1.25rem;
    --spacing-6: 1.5rem;
    --spacing-8: 2rem;
    --spacing-10: 2.5rem;
    --spacing-12: 3rem;
    
    /* الظلال */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
    
    /* الانتقالات */
    --transition-fast: 150ms ease-in-out;
    --transition-normal: 300ms ease-in-out;
    --transition-slow: 500ms ease-in-out;
}

/* المكونات الأساسية */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-2) var(--spacing-4);
    border: 1px solid transparent;
    border-radius: 0.375rem;
    font-size: var(--font-size-sm);
    font-weight: 500;
    text-decoration: none;
    transition: all var(--transition-fast);
    cursor: pointer;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

.btn-primary:hover {
    background-color: #1d4ed8;
    border-color: #1d4ed8;
}

.card {
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--gray-200);
    overflow: hidden;
}

.card-header {
    padding: var(--spacing-4) var(--spacing-6);
    border-bottom: 1px solid var(--gray-200);
    background-color: var(--gray-50);
}

.card-body {
    padding: var(--spacing-6);
}

/* الجداول المتجاوبة */
.table-responsive {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--font-size-sm);
}

.table th,
.table td {
    padding: var(--spacing-3) var(--spacing-4);
    text-align: right;
    border-bottom: 1px solid var(--gray-200);
}

.table th {
    background-color: var(--gray-50);
    font-weight: 600;
    color: var(--gray-700);
}

/* النماذج */
.form-group {
    margin-bottom: var(--spacing-4);
}

.form-label {
    display: block;
    margin-bottom: var(--spacing-2);
    font-weight: 500;
    color: var(--gray-700);
}

.form-control {
    display: block;
    width: 100%;
    padding: var(--spacing-2) var(--spacing-3);
    border: 1px solid var(--gray-300);
    border-radius: 0.375rem;
    font-size: var(--font-size-base);
    transition: border-color var(--transition-fast);
}

.form-control:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgb(37 99 235 / 0.1);
}

/* الاستجابة للأجهزة المحمولة */
@media (max-width: 768px) {
    .container {
        padding-left: var(--spacing-4);
        padding-right: var(--spacing-4);
    }
    
    .table-responsive {
        font-size: var(--font-size-xs);
    }
    
    .btn {
        padding: var(--spacing-2) var(--spacing-3);
        font-size: var(--font-size-xs);
    }
}
```

### 7. نظام التقارير والتحليلات المتقدم

#### محرك التقارير المرن
```python
# core/services/reporting.py
class ReportEngine:
    """محرك التقارير المتقدم"""
    
    def __init__(self, user):
        self.user = user
        self.filters = {}
        self.aggregations = {}
        self.groupings = []
    
    def add_filter(self, field, operator, value):
        """إضافة فلتر للتقرير"""
        self.filters[field] = {'operator': operator, 'value': value}
        return self
    
    def add_aggregation(self, field, function):
        """إضافة تجميع للتقرير"""
        self.aggregations[field] = function
        return self
    
    def group_by(self, *fields):
        """تجميع البيانات حسب الحقول"""
        self.groupings.extend(fields)
        return self
    
    def generate(self, model_class, format='json'):
        """توليد التقرير"""
        queryset = model_class.objects.all()
        
        # تطبيق الفلاتر
        for field, filter_data in self.filters.items():
            operator = filter_data['operator']
            value = filter_data['value']
            
            if operator == 'equals':
                queryset = queryset.filter(**{field: value})
            elif operator == 'contains':
                queryset = queryset.filter(**{f"{field}__icontains": value})
            elif operator == 'gte':
                queryset = queryset.filter(**{f"{field}__gte": value})
            elif operator == 'lte':
                queryset = queryset.filter(**{f"{field}__lte": value})
        
        # تطبيق التجميعات
        if self.aggregations:
            queryset = queryset.aggregate(**self.aggregations)
        
        # تطبيق التجميع
        if self.groupings:
            queryset = queryset.values(*self.groupings).annotate(
                count=Count('id')
            )
        
        # تحويل النتائج حسب التنسيق المطلوب
        if format == 'json':
            return list(queryset)
        elif format == 'excel':
            return self._export_to_excel(queryset)
        elif format == 'pdf':
            return self._export_to_pdf(queryset)
    
    def _export_to_excel(self, data):
        """تصدير إلى Excel"""
        # تنفيذ تصدير Excel
        pass
    
    def _export_to_pdf(self, data):
        """تصدير إلى PDF"""
        # تنفيذ تصدير PDF
        pass

# تقارير الموارد البشرية
class HRReports:
    """تقارير الموارد البشرية"""
    
    @staticmethod
    def employee_summary_report(user, filters=None):
        """تقرير ملخص الموظفين"""
        engine = ReportEngine(user)
        
        if filters:
            for field, value in filters.items():
                engine.add_filter(field, 'equals', value)
        
        return engine.group_by('department__name', 'job_position__name')\
                    .add_aggregation('total_employees', Count('id'))\
                    .add_aggregation('avg_salary', Avg('salary__basic_salary'))\
                    .generate(Employee)
    
    @staticmethod
    def attendance_report(user, start_date, end_date):
        """تقرير الحضور"""
        engine = ReportEngine(user)
        
        return engine.add_filter('att_date', 'gte', start_date)\
                    .add_filter('att_date', 'lte', end_date)\
                    .group_by('employee__department__name')\
                    .add_aggregation('present_days', Count('id', filter=Q(status='Present')))\
                    .add_aggregation('absent_days', Count('id', filter=Q(status='Absent')))\
                    .add_aggregation('late_days', Count('id', filter=Q(status='Late')))\
                    .generate(EmployeeAttendance)
```

### 8. نظام الإشعارات الذكية

#### محرك الإشعارات المتقدم
```python
# core/services/notifications.py
class NotificationService:
    """خدمة الإشعارات الذكية"""
    
    CHANNELS = {
        'in_app': 'داخل التطبيق',
        'email': 'البريد الإلكتروني',
        'sms': 'رسائل نصية',
        'push': 'إشعارات فورية',
    }
    
    def __init__(self):
        self.templates = {}
        self.channels = []
    
    def send_notification(self, recipient, template_name, context=None, channels=None):
        """إرسال إشعار"""
        template = self.get_template(template_name)
        channels = channels or ['in_app']
        
        notification = Notification.objects.create(
            recipient=recipient,
            title=template.render_title(context),
            message=template.render_message(context),
            notification_type=template.notification_type,
            priority=template.priority
        )
        
        for channel in channels:
            self._send_via_channel(notification, channel, context)
        
        return notification
    
    def _send_via_channel(self, notification, channel, context):
        """إرسال عبر قناة محددة"""
        if channel == 'email':
            self._send_email(notification, context)
        elif channel == 'sms':
            self._send_sms(notification, context)
        elif channel == 'push':
            self._send_push(notification, context)
    
    def schedule_notification(self, recipient, template_name, send_at, context=None):
        """جدولة إشعار"""
        ScheduledNotification.objects.create(
            recipient=recipient,
            template_name=template_name,
            context=context,
            send_at=send_at
        )

# إشعارات الموارد البشرية
class HRNotifications:
    """إشعارات الموارد البشرية"""
    
    @staticmethod
    def employee_birthday_reminder(employee):
        """تذكير عيد ميلاد الموظف"""
        NotificationService().send_notification(
            recipient=employee.manager,
            template_name='employee_birthday',
            context={'employee': employee},
            channels=['in_app', 'email']
        )
    
    @staticmethod
    def leave_request_notification(leave_request):
        """إشعار طلب إجازة"""
        NotificationService().send_notification(
            recipient=leave_request.employee.manager,
            template_name='leave_request_submitted',
            context={'leave_request': leave_request},
            channels=['in_app', 'email']
        )
    
    @staticmethod
    def document_expiry_warning(employee, document):
        """تحذير انتهاء صلاحية وثيقة"""
        NotificationService().send_notification(
            recipient=employee,
            template_name='document_expiry_warning',
            context={'employee': employee, 'document': document},
            channels=['in_app', 'email']
        )
```

### 9. نظام التخزين المؤقت والأداء

#### استراتيجية التخزين المؤقت
```python
# core/services/cache.py
class CacheService:
    """خدمة التخزين المؤقت المتقدمة"""
    
    CACHE_TIMEOUTS = {
        'short': 300,      # 5 دقائق
        'medium': 1800,    # 30 دقيقة
        'long': 3600,      # ساعة واحدة
        'daily': 86400,    # يوم واحد
    }
    
    @staticmethod
    def get_or_set(key, callable_func, timeout='medium'):
        """الحصول على قيمة من التخزين المؤقت أو تعيينها"""
        cached_value = cache.get(key)
        if cached_value is not None:
            return cached_value
        
        value = callable_func()
        cache.set(key, value, CacheService.CACHE_TIMEOUTS[timeout])
        return value
    
    @staticmethod
    def invalidate_pattern(pattern):
        """إبطال التخزين المؤقت بنمط معين"""
        keys = cache.keys(pattern)
        if keys:
            cache.delete_many(keys)
    
    @staticmethod
    def warm_up_cache():
        """تسخين التخزين المؤقت"""
        # تحميل البيانات الأساسية مسبقاً
        CacheService.get_or_set(
            'departments_list',
            lambda: list(Department.objects.filter(is_active=True).values()),
            'daily'
        )
        
        CacheService.get_or_set(
            'job_positions_list',
            lambda: list(JobPosition.objects.filter(is_active=True).values()),
            'daily'
        )

# تطبيق التخزين المؤقت في الخدمات
class EmployeeService(BaseService):
    """خدمة الموظفين مع التخزين المؤقت"""
    
    def get_department_employees(self, department_id):
        """الحصول على موظفي القسم مع التخزين المؤقت"""
        cache_key = f"department_employees_{department_id}"
        
        return CacheService.get_or_set(
            cache_key,
            lambda: Employee.objects.filter(
                department_id=department_id,
                is_active=True
            ).select_related('job_position', 'manager'),
            'medium'
        )
    
    def invalidate_employee_cache(self, employee):
        """إبطال التخزين المؤقت للموظف"""
        patterns = [
            f"employee_{employee.id}_*",
            f"department_employees_{employee.department_id}",
            "employees_summary_*"
        ]
        
        for pattern in patterns:
            CacheService.invalidate_pattern(pattern)
```

### 10. نظام المراقبة والتسجيل

#### نظام التسجيل المتقدم
```python
# core/services/logging.py
import logging
import json
from datetime import datetime

class StructuredLogger:
    """مسجل منظم للأحداث"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # إعداد معالج الملفات
        file_handler = logging.FileHandler('logs/application.log')
        file_handler.setLevel(logging.INFO)
        
        # إعداد التنسيق
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def log_user_action(self, user, action, resource, details=None):
        """تسجيل عمل المستخدم"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user.id if user else None,
            'username': user.username if user else 'anonymous',
            'action': action,
            'resource': resource,
            'details': details or {},
            'ip_address': getattr(user, 'ip_address', None)
        }
        
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_system_event(self, event_type, message, level='info', extra_data=None):
        """تسجيل حدث النظام"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'message': message,
            'extra_data': extra_data or {}
        }
        
        log_message = json.dumps(log_data, ensure_ascii=False)
        
        if level == 'error':
            self.logger.error(log_message)
        elif level == 'warning':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

# middleware للتسجيل التلقائي
class AuditMiddleware:
    """وسطاء المراجعة والتدقيق"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = StructuredLogger('audit')
    
    def __call__(self, request):
        # تسجيل الطلب
        start_time = datetime.now()
        
        response = self.get_response(request)
        
        # تسجيل الاستجابة
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if request.user.is_authenticated:
            self.logger.log_user_action(
                user=request.user,
                action=f"{request.method} {request.path}",
                resource=request.path,
                details={
                    'status_code': response.status_code,
                    'duration': duration,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )
        
        return response
```

هذا التصميم يوفر أساساً قوياً ومنظماً لتنظيف وإكمال نظام الدولية ليصبح نظاماً احترافياً جاهزاً للعمل على سيرفر داخلي للشركة مع جميع الميزات المطلوبة والأداء المحسن.