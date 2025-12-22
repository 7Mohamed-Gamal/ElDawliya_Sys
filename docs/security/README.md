# دليل الأمان - نظام الدولية

## نظرة عامة

هذا الدليل يوضح إعدادات الأمان والحماية في نظام الدولية، ويغطي جميع جوانب الأمان من المصادقة إلى حماية البيانات.

## 🔐 نظام المصادقة والتوثيق

### أنواع المصادقة المدعومة

#### 1. مصادقة كلمة المرور التقليدية
- كلمات مرور قوية ومعقدة
- انتهاء صلاحية دوري
- منع إعادة استخدام كلمات المرور السابقة

#### 2. مصادقة JWT للـ API
- رموز وصول قصيرة المدى (15 دقيقة)
- رموز تجديد طويلة المدى (7 أيام)
- إبطال الرموز عند تسجيل الخروج

#### 3. مفاتيح API للتكاملات
- مفاتيح فريدة لكل تطبيق خارجي
- صلاحيات محددة لكل مفتاح
- مراقبة الاستخدام والتنبيهات

### سياسات كلمات المرور

```python
# في settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# إعدادات إضافية للأمان
PASSWORD_RESET_TIMEOUT = 3600  # ساعة واحدة
LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_ATTEMPTS_TIMEOUT = 900  # 15 دقيقة
```

## 🛡️ نظام الصلاحيات الهرمي

### هيكل الصلاحيات

```
المؤسسة
├── الأقسام
│   ├── الموارد البشرية
│   │   ├── عرض الموظفين
│   │   ├── إضافة موظف
│   │   ├── تعديل الموظف
│   │   └── حذف الموظف
│   ├── المخزون
│   │   ├── عرض المنتجات
│   │   ├── إدارة المخزون
│   │   └── تقارير المخزون
│   └── المشاريع
│       ├── إدارة المشاريع
│       ├── إدارة المهام
│       └── تقارير المشاريع
```### 
الأدوار المحددة مسبقاً

| الدور | الوصف | الصلاحيات الأساسية |
|-------|--------|-------------------|
| **مدير النظام** | إدارة كاملة للنظام | جميع الصلاحيات |
| **مدير الموارد البشرية** | إدارة شؤون الموظفين | HR: إدارة كاملة |
| **مدير المخزون** | إدارة المخزون والمشتريات | المخزون والمشتريات: إدارة كاملة |
| **مدير المشاريع** | إدارة المشاريع والمهام | المشاريع: إدارة كاملة |
| **محاسب** | إدارة الشؤون المالية | المالية: عرض وتعديل |
| **موظف** | استخدام أساسي | عرض البيانات الشخصية |

### تطبيق الصلاحيات في الكود

```python
# في views.py
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

@permission_required('hr.view_employee', raise_exception=True)
def employee_list(request):
    # فحص الصلاحيات على مستوى الكائن
    if not request.user.has_perm('hr.view_all_employees'):
        # عرض موظفي نفس القسم فقط
        employees = Employee.objects.filter(
            department=request.user.employee.department
        )
    else:
        employees = Employee.objects.all()
    
    return render(request, 'employees/list.html', {'employees': employees})

# في API views
from rest_framework.permissions import BasePermission

class HRPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perm('hr.view_employee')
        elif request.method == 'POST':
            return request.user.has_perm('hr.add_employee')
        elif request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('hr.change_employee')
        elif request.method == 'DELETE':
            return request.user.has_perm('hr.delete_employee')
        return False
```

## 🔒 حماية البيانات والتشفير

### تشفير البيانات الحساسة

```python
# تشفير البيانات في قاعدة البيانات
from cryptography.fernet import Fernet
from django.conf import settings

class EncryptedField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.cipher.decrypt(value.encode()).decode()
    
    def to_python(self, value):
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return self.cipher.decrypt(value.encode()).decode()
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return self.cipher.encrypt(value.encode()).decode()

# استخدام الحقل المشفر
class Employee(models.Model):
    name = models.CharField(max_length=100)
    national_id = EncryptedField()  # رقم الهوية مشفر
    bank_account = EncryptedField()  # رقم الحساب البنكي مشفر
```

### حماية الجلسات

```python
# في settings.py
SESSION_COOKIE_SECURE = True  # HTTPS فقط
SESSION_COOKIE_HTTPONLY = True  # منع الوصول من JavaScript
SESSION_COOKIE_SAMESITE = 'Strict'  # حماية من CSRF
SESSION_COOKIE_AGE = 28800  # 8 ساعات

# إعدادات CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = ['https://your-domain.com']
```

## 🚨 مراقبة الأمان والتدقيق

### تسجيل العمليات الأمنية

```python
# نموذج سجل التدقيق
class AuditLog(models.Model):
    ACTIONS = [
        ('login', 'تسجيل دخول'),
        ('logout', 'تسجيل خروج'),
        ('create', 'إنشاء'),
        ('update', 'تحديث'),
        ('delete', 'حذف'),
        ('view', 'عرض'),
        ('export', 'تصدير'),
        ('permission_change', 'تغيير صلاحية'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTIONS)
    resource = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=50, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]

# Middleware للتسجيل التلقائي
class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # تسجيل العمليات المهمة
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            AuditLog.objects.create(
                user=request.user,
                action=self.get_action_from_request(request),
                resource=request.path,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={
                    'method': request.method,
                    'status_code': response.status_code,
                }
            )
        
        return response
```

### كشف التهديدات

```python
# كشف محاولات تسجيل الدخول المشبوهة
class SecurityMonitor:
    @staticmethod
    def check_suspicious_login(user, ip_address):
        # فحص محاولات تسجيل الدخول المتكررة
        recent_attempts = AuditLog.objects.filter(
            action='login',
            ip_address=ip_address,
            timestamp__gte=timezone.now() - timedelta(minutes=15)
        ).count()
        
        if recent_attempts > 10:
            SecurityAlert.objects.create(
                alert_type='suspicious_login',
                severity='high',
                details={
                    'ip_address': ip_address,
                    'attempts': recent_attempts,
                    'user': user.username if user else 'unknown'
                }
            )
            return True
        
        return False
    
    @staticmethod
    def check_unusual_access_pattern(user):
        # فحص أنماط الوصول غير المعتادة
        last_login_location = user.last_login_ip
        current_location = get_ip_location(request.META.get('REMOTE_ADDR'))
        
        if last_login_location and current_location:
            distance = calculate_distance(last_login_location, current_location)
            if distance > 1000:  # أكثر من 1000 كم
                SecurityAlert.objects.create(
                    alert_type='unusual_location',
                    severity='medium',
                    user=user,
                    details={
                        'last_location': last_login_location,
                        'current_location': current_location,
                        'distance_km': distance
                    }
                )
```

## 🛡️ حماية التطبيق من الهجمات

### حماية من SQL Injection

```python
# استخدام ORM بدلاً من SQL الخام
# ✅ آمن
employees = Employee.objects.filter(department=department_id)

# ❌ غير آمن
cursor.execute(f"SELECT * FROM employees WHERE department = {department_id}")

# إذا كان لابد من استخدام SQL خام، استخدم المعاملات
# ✅ آمن
cursor.execute("SELECT * FROM employees WHERE department = %s", [department_id])
```

### حماية من XSS

```python
# في القوالب، استخدم التصفية التلقائية
# ✅ آمن (Django يصفي تلقائياً)
{{ employee.name }}

# ❌ غير آمن (تعطيل التصفية)
{{ employee.name|safe }}

# للبيانات المعقدة، استخدم التصفية الصريحة
from django.utils.html import escape
safe_name = escape(employee.name)
```

### حماية من CSRF

```html
<!-- في جميع النماذج -->
<form method="post">
    {% csrf_token %}
    <!-- حقول النموذج -->
</form>
```

### Rate Limiting

```python
# حماية من الإفراط في الطلبات
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST')
def login_view(request):
    # منطق تسجيل الدخول
    pass

@ratelimit(key='user', rate='100/h', method='GET')
def api_endpoint(request):
    # منطق API
    pass
```

## 🔐 إعدادات الأمان في الإنتاج

### إعدادات Django الأمنية

```python
# في settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# إعدادات HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # سنة واحدة
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# إعدادات الأمان الإضافية
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# إعدادات الجلسات الآمنة
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
```

### إعدادات خادم الويب (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # إعدادات SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # إعدادات الأمان
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # إخفاء معلومات الخادم
    server_tokens off;
    
    # حماية من DDoS
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location /login/ {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://django_app;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://django_app;
    }
}
```

## 📊 مراقبة الأمان

### تقارير الأمان اليومية

```python
# سكريبت تقرير الأمان اليومي
def generate_security_report():
    today = timezone.now().date()
    
    report = {
        'date': today,
        'login_attempts': {
            'successful': AuditLog.objects.filter(
                action='login',
                timestamp__date=today,
                details__success=True
            ).count(),
            'failed': AuditLog.objects.filter(
                action='login',
                timestamp__date=today,
                details__success=False
            ).count()
        },
        'security_alerts': SecurityAlert.objects.filter(
            created_at__date=today
        ).count(),
        'suspicious_activities': AuditLog.objects.filter(
            timestamp__date=today,
            action__in=['permission_change', 'delete']
        ).count(),
        'unique_users': AuditLog.objects.filter(
            timestamp__date=today
        ).values('user').distinct().count(),
        'unique_ips': AuditLog.objects.filter(
            timestamp__date=today
        ).values('ip_address').distinct().count()
    }
    
    return report
```

### تنبيهات الأمان الفورية

```python
# إرسال تنبيهات الأمان
class SecurityAlertService:
    @staticmethod
    def send_alert(alert_type, severity, details):
        alert = SecurityAlert.objects.create(
            alert_type=alert_type,
            severity=severity,
            details=details
        )
        
        # إرسال تنبيه فوري للمديرين
        if severity in ['high', 'critical']:
            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                send_security_notification(admin, alert)
        
        # تسجيل في نظام المراقبة الخارجي
        log_to_security_system(alert)
    
    @staticmethod
    def handle_failed_login(username, ip_address):
        # عد محاولات تسجيل الدخول الفاشلة
        failed_attempts = cache.get(f'failed_login_{ip_address}', 0)
        failed_attempts += 1
        cache.set(f'failed_login_{ip_address}', failed_attempts, 3600)
        
        if failed_attempts >= 5:
            SecurityAlertService.send_alert(
                'brute_force_attempt',
                'high',
                {
                    'username': username,
                    'ip_address': ip_address,
                    'attempts': failed_attempts
                }
            )
            
            # حظر IP مؤقتاً
            cache.set(f'blocked_ip_{ip_address}', True, 3600)
```

## 🔧 أدوات الأمان والصيانة

### فحص الثغرات الأمنية

```bash
#!/bin/bash
# security_scan.sh - فحص الثغرات الأمنية

echo "=== فحص الأمان لنظام الدولية ==="

# فحص التبعيات للثغرات المعروفة
echo "1. فحص التبعيات..."
pip-audit

# فحص إعدادات Django
echo "2. فحص إعدادات Django..."
python manage.py check --deploy

# فحص كلمات المرور الضعيفة
echo "3. فحص كلمات المرور..."
python manage.py check_weak_passwords

# فحص الصلاحيات المفرطة
echo "4. فحص الصلاحيات..."
python manage.py audit_permissions

# فحص ملفات السجلات للأنشطة المشبوهة
echo "5. فحص السجلات..."
python manage.py analyze_security_logs

echo "=== انتهى فحص الأمان ==="
```

### نسخ احتياطية آمنة

```bash
#!/bin/bash
# secure_backup.sh - نسخ احتياطية مشفرة

BACKUP_DIR="/secure/backups"
DATE=$(date +%Y%m%d_%H%M%S)
GPG_RECIPIENT="admin@company.com"

# إنشاء النسخة الاحتياطية
mysqldump -u backup_user -p eldawliya_db > /tmp/db_backup_$DATE.sql

# تشفير النسخة الاحتياطية
gpg --trust-model always --encrypt -r $GPG_RECIPIENT /tmp/db_backup_$DATE.sql

# نقل النسخة المشفرة
mv /tmp/db_backup_$DATE.sql.gpg $BACKUP_DIR/

# حذف النسخة غير المشفرة
rm /tmp/db_backup_$DATE.sql

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "*.gpg" -mtime +30 -delete
```

## 📋 قائمة فحص الأمان

### قبل النشر
- [ ] تم تعطيل وضع DEBUG
- [ ] تم تحديد ALLOWED_HOSTS بشكل صحيح
- [ ] تم تفعيل HTTPS وإعدادات SSL
- [ ] تم تطبيق جميع إعدادات الأمان
- [ ] تم فحص التبعيات للثغرات
- [ ] تم اختبار نظام النسخ الاحتياطي
- [ ] تم إعداد مراقبة الأمان
- [ ] تم تدريب المستخدمين على الأمان

### مراجعة دورية (شهرياً)
- [ ] مراجعة سجلات الأمان
- [ ] تحديث كلمات المرور
- [ ] مراجعة صلاحيات المستخدمين
- [ ] فحص الثغرات الجديدة
- [ ] اختبار خطة الطوارئ
- [ ] تحديث التوثيق الأمني

## 📞 الاستجابة للحوادث الأمنية

### في حالة اكتشاف خرق أمني:

1. **العزل الفوري**
   - قطع الاتصال عن الشبكة
   - إيقاف الخدمات المتأثرة
   - حفظ الأدلة

2. **التقييم**
   - تحديد نطاق الخرق
   - تحديد البيانات المتأثرة
   - تقييم الأضرار

3. **الاحتواء**
   - إصلاح الثغرة
   - تغيير كلمات المرور
   - تحديث الأنظمة

4. **الاستعادة**
   - استعادة من النسخ الاحتياطية
   - اختبار سلامة النظام
   - إعادة تشغيل الخدمات

5. **التوثيق والتعلم**
   - توثيق الحادث
   - تحليل الأسباب
   - تحسين الإجراءات

### جهات الاتصال للطوارئ:
- **مدير الأمان**: security@company.com
- **فريق الاستجابة**: incident@company.com
- **الإدارة العليا**: management@company.com

---

**الأمان مسؤولية الجميع. ابلغ عن أي نشاط مشبوه فوراً! 🔒**