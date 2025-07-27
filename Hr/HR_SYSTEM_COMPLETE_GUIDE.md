# دليل نظام الموارد البشرية الشامل

## نظرة عامة

نظام الموارد البشرية الشامل هو تطبيق متطور مبني على Django يوفر إدارة كاملة للموارد البشرية في المؤسسات. النظام يدعم اللغة العربية بالكامل ويتضمن ميزات متقدمة مثل إدارة الملفات، التأمينات، بيانات السيارات، والتقييمات الشاملة.

## الميزات الرئيسية

### 🧑‍💼 إدارة الموظفين الشاملة
- **البيانات الشخصية**: معلومات كاملة مع دعم الصور والوثائق
- **بيانات العمل**: الأقسام، الوظائف، الرواتب، والتاريخ الوظيفي
- **المؤهلات الدراسية**: إدارة الشهادات والمؤهلات مع التحقق
- **التأمينات**: إدارة جميع أنواع التأمينات (اجتماعي، صحي، حياة)
- **بيانات السيارات**: إدارة سيارات الشركة والبدلات

### 📁 إدارة الملفات والوثائق
- **رفع الملفات**: دعم جميع أنواع الملفات مع التحقق من الأمان
- **تصنيف الوثائق**: تنظيم تلقائي حسب النوع والموظف
- **تنبيهات الانتهاء**: تذكير قبل انتهاء صلاحية الوثائق
- **البحث المتقدم**: بحث في محتوى الملفات والبيانات الوصفية
- **الأمان**: تشفير الملفات الحساسة وإدارة الصلاحيات

### ⏰ إدارة الحضور والوقت
- **تسجيل الحضور**: دعم أجهزة الحضور المختلفة والتسجيل اليدوي
- **الورديات**: إدارة ورديات متعددة مع جدولة تلقائية
- **الوقت الإضافي**: حساب تلقائي وفقاً لقواعد الشركة
- **التقارير**: تقارير مفصلة للحضور والغياب والتأخير
- **التحليلات**: رسوم بيانية وإحصائيات متقدمة

### 💰 إدارة الرواتب المتقدمة
- **حساب الرواتب**: نظام شامل لحساب جميع مكونات الراتب
- **البدلات والحوافز**: إدارة مرنة للبدلات والمكافآت
- **الخصومات**: تأمينات، ضرائب، قروض، وجزاءات
- **كشوف الرواتب**: إنتاج كشوف احترافية قابلة للطباعة
- **التقارير المالية**: تحليلات التكاليف والميزانيات

### 🏖️ إدارة الإجازات
- **أنواع الإجازات**: إدارة مرنة لجميع أنواع الإجازات
- **سير العمل**: نظام موافقات متعدد المستويات
- **الأرصدة**: حساب تلقائي لأرصدة الإجازات
- **التقويم**: عرض بصري للإجازات والمناوبات
- **التقارير**: تحليلات استخدام الإجازات

### 📊 التقييمات والتحليلات
- **نماذج التقييم**: قوالب قابلة للتخصيص
- **تقييم الأداء**: نظام شامل لتقييم الموظفين
- **التحليلات**: مؤشرات أداء ورسوم بيانية
- **المقارنات**: مقارنة الأداء عبر الفترات والأقسام
- **التقارير**: تقارير مفصلة للإدارة العليا

### 🔒 الأمان والصلاحيات
- **نظام الصلاحيات**: إدارة دقيقة للوصول والعمليات
- **التدقيق**: تسجيل جميع العمليات الحساسة
- **التشفير**: حماية البيانات الحساسة
- **النسخ الاحتياطي**: نظام آمن للنسخ الاحتياطي
- **المراقبة**: مراقبة الأنشطة والتنبيهات

## التثبيت والإعداد

### المتطلبات الأساسية

```bash
# Python 3.8+
python --version

# Django 4.2+
pip install Django>=4.2

# SQL Server (أو قاعدة بيانات أخرى)
pip install mssql-django pyodbc
```

### التثبيت السريع

```bash
# 1. استنساخ المشروع
git clone <repository-url>
cd ElDawliya_sys

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. إعداد قاعدة البيانات
python manage.py migrate

# 4. إنشاء مستخدم إداري
python manage.py createsuperuser

# 5. جمع الملفات الثابتة
python manage.py collectstatic

# 6. تشغيل الخادم
python manage.py runserver
```

### الإعداد المتقدم

```bash
# 1. فحص النظام
python Hr/system_check.py

# 2. إعداد التخزين المؤقت
python Hr/setup_simple_cache.py

# 3. إنشاء بيانات تجريبية
python manage.py loaddata Hr/fixtures/sample_data.json

# 4. اختبار النظام
python manage.py test Hr
```

## الاستخدام

### الوصول للنظام

```
# الواجهة الرئيسية
http://localhost:8000/Hr/

# لوحة الإدارة
http://localhost:8000/admin/

# واجهة برمجة التطبيقات
http://localhost:8000/api/v1/hr/

# التوثيق التفاعلي
http://localhost:8000/api/docs/
```

### العمليات الأساسية

#### إضافة موظف جديد

```python
from Hr.services.employee_service import EmployeeService

service = EmployeeService()

employee_data = {
    'first_name': 'أحمد',
    'last_name': 'محمد',
    'employee_number': 'EMP001',
    'department_id': 1,
    'job_position_id': 1,
    'hire_date': '2024-01-01',
    'salary': 5000.00
}

employee = service.create_employee_complete(employee_data)
```

#### تسجيل حضور

```python
from Hr.services.attendance_service import AttendanceService

service = AttendanceService()
service.record_attendance(
    employee_id=1,
    attendance_type='check_in',
    timestamp='2024-01-15 08:00:00'
)
```

#### حساب راتب

```python
from Hr.services.payroll_service import PayrollService

service = PayrollService()
payroll = service.calculate_payroll(
    employee_id=1,
    period_start='2024-01-01',
    period_end='2024-01-31'
)
```

### واجهة برمجة التطبيقات

#### الموظفين

```bash
# قائمة الموظفين
GET /api/v1/hr/employees/

# إضافة موظف
POST /api/v1/hr/employees/
{
    "first_name": "أحمد",
    "last_name": "محمد",
    "employee_number": "EMP001"
}

# تفاصيل موظف
GET /api/v1/hr/employees/1/

# تحديث موظف
PUT /api/v1/hr/employees/1/

# حذف موظف
DELETE /api/v1/hr/employees/1/
```

#### الحضور

```bash
# تسجيل حضور
POST /api/v1/hr/attendance/
{
    "employee": 1,
    "attendance_type": "check_in",
    "timestamp": "2024-01-15T08:00:00Z"
}

# سجلات الحضور
GET /api/v1/hr/attendance/?employee=1&date=2024-01-15
```

#### الرواتب

```bash
# حساب راتب
POST /api/v1/hr/payroll/calculate/
{
    "employee": 1,
    "period_start": "2024-01-01",
    "period_end": "2024-01-31"
}

# كشوف الرواتب
GET /api/v1/hr/payroll/?period=2024-01
```

## التخصيص والتطوير

### إضافة حقول جديدة

```python
# في Hr/models.py
class Employee(models.Model):
    # الحقول الموجودة...
    
    # حقل جديد
    custom_field = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفون'
```

### إنشاء خدمة جديدة

```python
# في Hr/services/custom_service.py
class CustomService:
    """خدمة مخصصة"""
    
    def custom_operation(self, data):
        """عملية مخصصة"""
        # منطق العملية
        return result
```

### إضافة API جديد

```python
# في Hr/api/viewsets.py
class CustomViewSet(viewsets.ModelViewSet):
    """API مخصص"""
    
    queryset = CustomModel.objects.all()
    serializer_class = CustomSerializer
    permission_classes = [IsAuthenticated]
```

### إنشاء تقرير جديد

```python
# في Hr/services/report_service.py
class ReportService:
    
    def generate_custom_report(self, filters):
        """إنتاج تقرير مخصص"""
        # منطق التقرير
        return report_data
```

## الأداء والتحسين

### التخزين المؤقت

```python
# استخدام التخزين المؤقت
from Hr.decorators.cache_decorators import smart_cache

@smart_cache(timeout='long', tags=['employee'])
def get_employee_data(employee_id):
    return Employee.objects.get(id=employee_id)
```

### تحسين الاستعلامات

```python
# استخدام select_related و prefetch_related
employees = Employee.objects.select_related(
    'department', 'job_position'
).prefetch_related(
    'education_set', 'insurance_set'
)
```

### الفهرسة

```python
# في النماذج
class Employee(models.Model):
    employee_number = models.CharField(max_length=20, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['department', 'job_position']),
            models.Index(fields=['hire_date']),
        ]
```

## الأمان

### إدارة الصلاحيات

```python
# في العروض
from Hr.decorators import hr_permission_required

@hr_permission_required('view_employee')
def employee_list(request):
    # منطق العرض
    pass
```

### تشفير البيانات

```python
# في النماذج
from Hr.fields import EncryptedCharField

class Employee(models.Model):
    national_id = EncryptedCharField(max_length=20)
```

### التدقيق

```python
# تسجيل العمليات تلقائياً
from Hr.middleware import AuditMiddleware

# في settings.py
MIDDLEWARE = [
    # الوسطاء الأخرى...
    'Hr.middleware.AuditMiddleware',
]
```

## النشر

### الإعداد للإنتاج

```python
# في settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# قاعدة البيانات
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'hr_production',
        'HOST': 'your-db-server',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}

# التخزين المؤقت
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Docker

```dockerfile
# Dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "ElDawliya_sys.wsgi:application"]
```

### Nginx

```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /app/staticfiles/;
    }
    
    location /media/ {
        alias /app/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## الصيانة

### النسخ الاحتياطي

```bash
# نسخ احتياطي لقاعدة البيانات
python manage.py dbbackup

# نسخ احتياطي للملفات
python manage.py mediabackup

# نسخ احتياطي شامل
python Hr/backup_system.py
```

### المراقبة

```bash
# مراقبة الأداء
python manage.py monitor_performance

# فحص النظام
python Hr/system_check.py

# تنظيف التخزين المؤقت
python manage.py cache_management clear
```

### التحديثات

```bash
# تحديث المكتبات
pip install -r requirements.txt --upgrade

# تطبيق الهجرات
python manage.py migrate

# جمع الملفات الثابتة
python manage.py collectstatic --noinput
```

## استكشاف الأخطاء

### مشاكل شائعة

#### خطأ في الاتصال بقاعدة البيانات
```bash
# فحص الاتصال
python manage.py dbshell

# فحص الإعدادات
python manage.py check --database default
```

#### مشاكل في الملفات الثابتة
```bash
# جمع الملفات مرة أخرى
python manage.py collectstatic --clear

# فحص إعدادات الملفات الثابتة
python manage.py findstatic Hr/css/style.css
```

#### مشاكل في التخزين المؤقت
```bash
# مسح التخزين المؤقت
python manage.py cache_management clear

# فحص حالة التخزين المؤقت
python manage.py cache_management status
```

### السجلات

```python
# في settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'hr_system.log',
        },
    },
    'loggers': {
        'Hr': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## الدعم والمساعدة

### الوثائق
- [دليل المستخدم](Hr/USER_GUIDE.md)
- [دليل المطور](Hr/DEVELOPER_GUIDE.md)
- [دليل التخزين المؤقت](Hr/CACHE_README.md)
- [دليل الأمان](Hr/SECURITY_GUIDE.md)

### الأوامر المفيدة
```bash
# فحص شامل للنظام
python Hr/system_check.py

# إعداد التخزين المؤقت
python Hr/setup_simple_cache.py

# إنشاء بيانات تجريبية
python manage.py create_sample_data

# تشغيل الاختبارات
python manage.py test Hr

# إنتاج تقرير الأداء
python manage.py performance_report
```

### المساهمة
نرحب بالمساهمات! يرجى مراجعة [دليل المساهمة](CONTRIBUTING.md) للمزيد من المعلومات.

### الترخيص
هذا المشروع مرخص تحت [رخصة MIT](LICENSE).

---

**تم تطوير هذا النظام بعناية لتلبية احتياجات إدارة الموارد البشرية في المؤسسات العربية. نأمل أن يكون مفيداً لمؤسستكم!** 🚀