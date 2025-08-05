# دليل استكشاف الأخطاء وإصلاحها

## مقدمة

هذا الدليل يساعدك على تشخيص وحل المشاكل الشائعة في نظام الموارد البشرية الشامل.

## المشاكل الشائعة وحلولها

### 1. مشاكل تسجيل الدخول

#### المشكلة: "اسم المستخدم أو كلمة المرور غير صحيحة"

**الأسباب المحتملة:**
- كلمة مرور خاطئة
- اسم مستخدم غير صحيح
- الحساب معطل
- مشكلة في قاعدة البيانات

**الحلول:**
1. تأكد من صحة بيانات تسجيل الدخول
2. استخدم خاصية "نسيت كلمة المرور"
3. تواصل مع مدير النظام للتحقق من حالة الحساب

```bash
# للمطورين: التحقق من حالة المستخدم
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='username')
>>> print(f"نشط: {user.is_active}, موظف: {user.is_staff}")
```

#### المشكلة: "انتهت صلاحية الجلسة"

**الحل:**
- قم بتسجيل الدخول مرة أخرى
- تحقق من إعدادات انتهاء الجلسة في النظام

### 2. مشاكل الأداء

#### المشكلة: النظام بطيء في التحميل

**التشخيص:**
```bash
# فحص استخدام الموارد
htop
free -h
df -h

# فحص حالة قاعدة البيانات
python manage.py dbshell
```

**الحلول:**
1. **تحسين قاعدة البيانات:**
```bash
python manage.py optimize_database --action=optimize
```

2. **مسح التخزين المؤقت:**
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

3. **إعادة تشغيل الخدمات:**
```bash
sudo systemctl restart hr-system
sudo systemctl restart nginx
sudo systemctl restart postgresql
```

#### المشكلة: استهلاك عالي للذاكرة

**التشخيص:**
```bash
# مراقبة استخدام الذاكرة
python manage.py monitor_system --action=report
```

**الحلول:**
1. زيادة ذاكرة الخادم
2. تحسين استعلامات قاعدة البيانات
3. تقليل عدد العمليات المتزامنة

### 3. مشاكل قاعدة البيانات

#### المشكلة: "خطأ في الاتصال بقاعدة البيانات"

**التشخيص:**
```bash
# فحص حالة قاعدة البيانات
sudo systemctl status postgresql

# اختبار الاتصال
python manage.py dbshell
```

**الحلول:**
1. **إعادة تشغيل قاعدة البيانات:**
```bash
sudo systemctl restart postgresql
```

2. **التحقق من إعدادات الاتصال:**
```python
# في settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hr_system',
        'USER': 'hr_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### المشكلة: "خطأ في الهجرات"

**التشخيص:**
```bash
python manage.py showmigrations
```

**الحلول:**
1. **تطبيق الهجرات المعلقة:**
```bash
python manage.py migrate
```

2. **إصلاح تضارب الهجرات:**
```bash
python manage.py migrate --fake-initial
```

3. **إعادة إنشاء الهجرات:**
```bash
python manage.py makemigrations --empty Hr
```

### 4. مشاكل الملفات والوسائط

#### المشكلة: "لا يمكن رفع الملفات"

**التشخيص:**
```bash
# فحص صلاحيات المجلدات
ls -la media/
ls -la staticfiles/
```

**الحلول:**
1. **إصلاح الصلاحيات:**
```bash
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/
```

2. **التحقق من إعدادات Django:**
```python
# في settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
```

#### المشكلة: "الملفات الثابتة لا تظهر"

**الحلول:**
```bash
# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# التحقق من إعدادات Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 5. مشاكل API

#### المشكلة: "خطأ 401 - غير مصرح"

**الحلول:**
1. **التحقق من Token:**
```bash
python manage.py shell
>>> from rest_framework.authtoken.models import Token
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='your_username')
>>> token, created = Token.objects.get_or_create(user=user)
>>> print(f"Token: {token.key}")
```

2. **إنشاء Token جديد:**
```bash
python manage.py drf_create_token username
```

#### المشكلة: "خطأ 500 - خطأ في الخادم"

**التشخيص:**
```bash
# فحص سجلات الأخطاء
tail -f /var/log/nginx/error.log
sudo journalctl -u hr-system -f
```

### 6. مشاكل التشفير

#### المشكلة: "لا يمكن فك تشفير البيانات"

**التشخيص:**
```bash
python manage.py shell
>>> from Hr.services.encryption_service import encryption_service
>>> status = encryption_service.get_encryption_status()
>>> print(status)
```

**الحلول:**
1. **التحقق من مفتاح التشفير:**
```bash
# في .env
HR_ENCRYPTION_KEY=your-encryption-key-here
```

2. **إعادة تشفير البيانات:**
```bash
python manage.py encrypt_existing_data --dry-run
```

### 7. مشاكل المراقبة

#### المشكلة: "لا تظهر بيانات المراقبة"

**التشخيص:**
```bash
python manage.py monitor_system --action=analyze
```

**الحلول:**
1. **تفعيل المراقبة:**
```python
# في settings.py
ENABLE_SYSTEM_MONITORING = True
ENABLE_PERFORMANCE_MONITORING = True
```

2. **تشغيل خدمة المراقبة:**
```bash
python manage.py monitor_system --daemon
```

## أدوات التشخيص

### 1. فحص حالة النظام

```bash
# سكريبت شامل لفحص النظام
#!/bin/bash

echo "=== فحص حالة النظام ==="

# فحص الخدمات
echo "1. حالة الخدمات:"
systemctl is-active hr-system
systemctl is-active nginx
systemctl is-active postgresql

# فحص الموارد
echo "2. استخدام الموارد:"
free -h
df -h

# فحص قاعدة البيانات
echo "3. قاعدة البيانات:"
python manage.py dbshell -c "SELECT version();"

# فحص السجلات
echo "4. آخر الأخطاء:"
tail -n 10 /var/log/nginx/error.log
```

### 2. اختبار الاتصال

```python
# test_connections.py
import os
import django
from django.db import connection
from django.core.cache import cache

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

def test_database():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ قاعدة البيانات: متصلة")
    except Exception as e:
        print(f"✗ قاعدة البيانات: {e}")

def test_cache():
    try:
        cache.set('test', 'value', 30)
        result = cache.get('test')
        if result == 'value':
            print("✓ التخزين المؤقت: يعمل")
        else:
            print("✗ التخزين المؤقت: لا يعمل")
    except Exception as e:
        print(f"✗ التخزين المؤقت: {e}")

if __name__ == "__main__":
    test_database()
    test_cache()
```

### 3. مراقبة الأداء

```bash
# performance_check.sh
#!/bin/bash

echo "=== مراقبة الأداء ==="

# استخدام المعالج
echo "استخدام المعالج:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1

# استخدام الذاكرة
echo "استخدام الذاكرة:"
free | grep Mem | awk '{printf "%.2f%%\n", $3/$2 * 100.0}'

# استخدام القرص
echo "استخدام القرص:"
df -h | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{print $5 " " $1}'

# عدد الاتصالات النشطة
echo "الاتصالات النشطة:"
netstat -an | grep :8000 | wc -l
```

## السجلات والتتبع

### 1. مواقع ملفات السجلات

```bash
# سجلات التطبيق
/var/log/hr-system/
/var/log/gunicorn/

# سجلات الخادم
/var/log/nginx/access.log
/var/log/nginx/error.log

# سجلات قاعدة البيانات
/var/log/postgresql/

# سجلات النظام
/var/log/syslog
journalctl -u hr-system
```

### 2. تحليل السجلات

```bash
# البحث عن الأخطاء
grep -i error /var/log/nginx/error.log | tail -20

# مراقبة السجلات المباشرة
tail -f /var/log/nginx/access.log

# تحليل أداء الاستعلامات
python manage.py analyze_query_performance --duration=300
```

## الاتصال بالدعم الفني

عند التواصل مع الدعم الفني، يرجى تقديم المعلومات التالية:

### معلومات النظام
```bash
# جمع معلومات النظام
python manage.py system_info > system_info.txt
```

### معلومات الخطأ
- رسالة الخطأ الكاملة
- الخطوات التي أدت للخطأ
- وقت حدوث الخطأ
- لقطة شاشة (إن أمكن)

### معلومات البيئة
- إصدار النظام
- إصدار Python
- إصدار قاعدة البيانات
- نظام التشغيل

## الصيانة الوقائية

### 1. المهام اليومية
```bash
# فحص حالة الخدمات
systemctl status hr-system nginx postgresql

# مراقبة استخدام الموارد
df -h
free -h

# فحص السجلات
tail -n 50 /var/log/nginx/error.log
```

### 2. المهام الأسبوعية
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade

# تنظيف السجلات القديمة
sudo journalctl --vacuum-time=7d

# فحص النسخ الاحتياطية
ls -la /backups/hr_system/
```

### 3. المهام الشهرية
```bash
# تحليل أداء قاعدة البيانات
python manage.py optimize_database --action=analyze

# مراجعة أمان النظام
python manage.py check --deploy

# تحديث المكتبات
pip list --outdated
```

---

*للحصول على مساعدة إضافية، يرجى التواصل مع فريق الدعم الفني*
*البريد الإلكتروني: support@eldawliya-hr.com*
*الهاتف: 0112345678*