# دليل استكشاف الأخطاء وإصلاحها - نظام الدولية

## 🚨 المشاكل الطارئة

### النظام لا يعمل نهائياً

#### الأعراض
- صفحة خطأ 500 أو 502
- عدم الاستجابة للطلبات
- رسالة "الخادم غير متاح"

#### التشخيص السريع
```bash
# فحص حالة الخدمات
sudo systemctl status eldawliya-web
sudo systemctl status eldawliya-worker
sudo systemctl status mysql
sudo systemctl status redis

# فحص استخدام الموارد
top
df -h
free -h

# فحص سجلات الأخطاء
tail -f /var/log/eldawliya/error.log
tail -f /var/log/mysql/error.log
```

#### الحلول السريعة
1. **إعادة تشغيل الخدمات**:
   ```bash
   sudo systemctl restart eldawliya-web
   sudo systemctl restart eldawliya-worker
   ```

2. **فحص مساحة القرص**:
   ```bash
   # إذا كانت المساحة ممتلئة
   sudo find /var/log -name "*.log" -mtime +7 -delete
   sudo find /tmp -type f -mtime +1 -delete
   ```

3. **إعادة تشغيل قاعدة البيانات**:
   ```bash
   sudo systemctl restart mysql
   # انتظار 30 ثانية ثم
   sudo systemctl restart eldawliya-web
   ```

### قاعدة البيانات لا تستجيب

#### الأعراض
- رسائل خطأ "Database connection failed"
- بطء شديد في تحميل الصفحات
- أخطاء timeout

#### التشخيص
```bash
# فحص حالة MySQL
sudo systemctl status mysql

# فحص العمليات النشطة
mysql -u root -p -e "SHOW PROCESSLIST;"

# فحص استخدام الذاكرة
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
```

#### الحلول
1. **قتل العمليات المعلقة**:
   ```sql
   -- عرض العمليات الطويلة
   SELECT * FROM information_schema.processlist 
   WHERE time > 300 AND command != 'Sleep';
   
   -- قتل عملية معينة
   KILL [process_id];
   ```

2. **تحسين إعدادات MySQL**:
   ```ini
   # في /etc/mysql/mysql.conf.d/mysqld.cnf
   max_connections = 200
   innodb_buffer_pool_size = 2G
   query_cache_size = 256M
   wait_timeout = 600
   ```

3. **إعادة بناء الفهارس**:
   ```sql
   OPTIMIZE TABLE employees;
   OPTIMIZE TABLE attendance;
   OPTIMIZE TABLE products;
   ```

## 🐛 مشاكل الأداء

### النظام بطيء جداً

#### تحديد مصدر البطء
```bash
# مراقبة استخدام المعالج
htop

# مراقبة استعلامات قاعدة البيانات البطيئة
mysql -u root -p -e "SHOW VARIABLES LIKE 'slow_query_log';"
mysql -u root -p -e "SET GLOBAL slow_query_log = 'ON';"
mysql -u root -p -e "SET GLOBAL long_query_time = 2;"

# عرض الاستعلامات البطيئة
tail -f /var/log/mysql/mysql-slow.log
```

#### تحسين الأداء
1. **تحسين استعلامات Django**:
   ```python
   # في views.py - استخدام select_related
   employees = Employee.objects.select_related('department', 'job_position').all()
   
   # استخدام prefetch_related للعلاقات المتعددة
   departments = Department.objects.prefetch_related('employees').all()
   
   # تحديد الحقول المطلوبة فقط
   employees = Employee.objects.only('first_name', 'last_name', 'email').all()
   ```

2. **تفعيل التخزين المؤقت**:
   ```python
   # في views.py
   from django.core.cache import cache
   
   def get_employee_stats():
       stats = cache.get('employee_stats')
       if not stats:
           stats = Employee.objects.aggregate(
               total=Count('id'),
               active=Count('id', filter=Q(is_active=True))
           )
           cache.set('employee_stats', stats, 300)  # 5 دقائق
       return stats
   ```

3. **تحسين قاعدة البيانات**:
   ```sql
   -- إضافة فهارس للاستعلامات الشائعة
   CREATE INDEX idx_employee_active ON employees(is_active);
   CREATE INDEX idx_attendance_date_emp ON attendance(attendance_date, employee_id);
   CREATE INDEX idx_product_category ON products(category_id, is_active);
   
   -- تحليل الجداول
   ANALYZE TABLE employees;
   ANALYZE TABLE attendance;
   ANALYZE TABLE products;
   ```

### استهلاك ذاكرة عالي

#### التشخيص
```bash
# مراقبة استهلاك الذاكرة
ps aux --sort=-%mem | head -10

# مراقبة عمليات Python
ps aux | grep python | awk '{print $2, $4, $11}' | sort -k2 -nr

# فحص ذاكرة MySQL
mysql -u root -p -e "SHOW STATUS LIKE 'Innodb_buffer_pool_pages_data';"
```

#### الحلول
1. **تحسين إعدادات Django**:
   ```python
   # في settings.py
   DEBUG = False  # تأكد من إيقاف وضع التطوير
   
   # تحديد حد أقصى لحجم الملفات المرفوعة
   FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
   
   # تحسين إعدادات قاعدة البيانات
   DATABASES = {
       'default': {
           'ENGINE': 'mssql',
           'OPTIONS': {
               'driver': 'ODBC Driver 17 for SQL Server',
               'extra_params': 'TrustServerCertificate=yes;Connection Timeout=30;'
           }
       }
   }
   ```

2. **تحسين إعدادات الخادم**:
   ```bash
   # في /etc/systemd/system/eldawliya-web.service
   [Service]
   Environment="DJANGO_SETTINGS_MODULE=ElDawliya_sys.settings.production"
   ExecStart=/path/to/venv/bin/gunicorn --workers 4 --max-requests 1000 --max-requests-jitter 100
   ```

## 🔐 مشاكل تسجيل الدخول

### المستخدمون لا يستطيعون تسجيل الدخول

#### الأسباب الشائعة
1. **كلمة مرور خاطئة**
2. **الحساب معطل**
3. **مشكلة في جلسات المستخدمين**
4. **مشكلة في قاعدة البيانات**

#### التشخيص
```python
# في Django shell
python manage.py shell

# فحص المستخدم
from django.contrib.auth.models import User
user = User.objects.get(username='ahmed')
print(f"نشط: {user.is_active}")
print(f"آخر تسجيل دخول: {user.last_login}")

# فحص كلمة المرور
from django.contrib.auth import authenticate
user = authenticate(username='ahmed', password='password123')
print(f"المصادقة: {'نجحت' if user else 'فشلت'}")
```

#### الحلول
1. **إعادة تعيين كلمة المرور**:
   ```python
   # في Django shell
   from django.contrib.auth.models import User
   user = User.objects.get(username='ahmed')
   user.set_password('new_password123')
   user.save()
   ```

2. **تفعيل الحساب**:
   ```python
   user = User.objects.get(username='ahmed')
   user.is_active = True
   user.save()
   ```

3. **مسح جلسات المستخدمين**:
   ```bash
   python manage.py clearsessions
   ```

### مشكلة "CSRF token missing"

#### الأعراض
- رسالة خطأ عند إرسال النماذج
- "CSRF verification failed"

#### الحلول
1. **التأكد من وجود CSRF token في النماذج**:
   ```html
   <form method="post">
       {% csrf_token %}
       <!-- باقي حقول النموذج -->
   </form>
   ```

2. **فحص إعدادات CSRF**:
   ```python
   # في settings.py
   CSRF_COOKIE_SECURE = False  # للتطوير المحلي
   CSRF_COOKIE_HTTPONLY = False
   CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://your-domain.com']
   ```

3. **مسح cookies المتصفح**:
   - اطلب من المستخدم مسح cookies الموقع
   - أو استخدام وضع التصفح الخاص

## 📊 مشاكل التقارير

### التقارير فارغة أو لا تظهر بيانات

#### التشخيص
```python
# في Django shell
from Hr.models import Employee
from datetime import datetime, timedelta

# فحص وجود البيانات
print(f"عدد الموظفين: {Employee.objects.count()}")
print(f"الموظفين النشطين: {Employee.objects.filter(is_active=True).count()}")

# فحص البيانات في فترة معينة
last_month = datetime.now() - timedelta(days=30)
recent_employees = Employee.objects.filter(created_at__gte=last_month)
print(f"الموظفين الجدد: {recent_employees.count()}")
```

#### الحلول
1. **فحص الفلاتر المطبقة**:
   ```python
   # تأكد من صحة الفلاتر في views.py
   def employee_report(request):
       employees = Employee.objects.all()
       
       # فلتر القسم
       department = request.GET.get('department')
       if department:
           employees = employees.filter(department_id=department)
       
       # فلتر التاريخ
       date_from = request.GET.get('date_from')
       if date_from:
           employees = employees.filter(hire_date__gte=date_from)
   ```

2. **فحص الصلاحيات**:
   ```python
   # تأكد من أن المستخدم لديه صلاحية عرض البيانات
   if not request.user.has_perm('Hr.view_employee'):
       return HttpResponseForbidden()
   ```

### مشكلة تصدير التقارير

#### الأعراض
- خطأ عند تصدير Excel أو PDF
- ملف فارغ أو تالف

#### الحلول
1. **فحص المكتبات المطلوبة**:
   ```bash
   pip install openpyxl xlsxwriter reportlab
   ```

2. **تحسين كود التصدير**:
   ```python
   import openpyxl
   from django.http import HttpResponse
   
   def export_employees_excel(request):
       response = HttpResponse(
           content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
       )
       response['Content-Disposition'] = 'attachment; filename="employees.xlsx"'
       
       workbook = openpyxl.Workbook()
       worksheet = workbook.active
       worksheet.title = 'الموظفين'
       
       # إضافة العناوين
       headers = ['الاسم', 'القسم', 'المنصب', 'تاريخ التوظيف']
       for col, header in enumerate(headers, 1):
           worksheet.cell(row=1, column=col, value=header)
       
       # إضافة البيانات
       employees = Employee.objects.select_related('department', 'job_position')
       for row, employee in enumerate(employees, 2):
           worksheet.cell(row=row, column=1, value=f"{employee.first_name} {employee.last_name}")
           worksheet.cell(row=row, column=2, value=employee.department.name if employee.department else '')
           worksheet.cell(row=row, column=3, value=employee.job_position.name if employee.job_position else '')
           worksheet.cell(row=row, column=4, value=employee.hire_date)
       
       workbook.save(response)
       return response
   ```

## 🔄 مشاكل المزامنة والتكامل

### مشكلة مزامنة أجهزة الحضور

#### الأعراض
- عدم ظهور بيانات الحضور الجديدة
- أخطاء في الاتصال بالجهاز

#### التشخيص
```python
# فحص اتصال الجهاز
from attendance.zk_service import ZKService

zk = ZKService('192.168.1.100', 4370)
if zk.connect():
    print("الاتصال ناجح")
    users = zk.get_users()
    print(f"عدد المستخدمين: {len(users)}")
    
    attendance = zk.get_attendance()
    print(f"عدد سجلات الحضور: {len(attendance)}")
else:
    print("فشل الاتصال")
```

#### الحلول
1. **فحص إعدادات الشبكة**:
   ```bash
   # فحص الاتصال بالجهاز
   ping 192.168.1.100
   
   # فحص المنفذ
   telnet 192.168.1.100 4370
   ```

2. **إعادة تشغيل خدمة المزامنة**:
   ```bash
   sudo systemctl restart eldawliya-sync
   ```

3. **مزامنة يدوية**:
   ```bash
   python manage.py sync_attendance_devices
   ```

### مشكلة إرسال الإشعارات

#### الأعراض
- الإشعارات لا تصل للمستخدمين
- أخطاء في إرسال البريد الإلكتروني

#### التشخيص
```python
# اختبار إعدادات البريد الإلكتروني
from django.core.mail import send_mail
from django.conf import settings

try:
    send_mail(
        'اختبار البريد الإلكتروني',
        'هذه رسالة اختبار من نظام الدولية',
        settings.DEFAULT_FROM_EMAIL,
        ['test@company.com'],
        fail_silently=False,
    )
    print("تم إرسال البريد بنجاح")
except Exception as e:
    print(f"خطأ في إرسال البريد: {e}")
```

#### الحلول
1. **فحص إعدادات البريد الإلكتروني**:
   ```python
   # في settings.py
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.company.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'noreply@company.com'
   EMAIL_HOST_PASSWORD = 'your_password'
   DEFAULT_FROM_EMAIL = 'نظام الدولية <noreply@company.com>'
   ```

2. **إعادة تشغيل خدمة الإشعارات**:
   ```bash
   sudo systemctl restart eldawliya-notifications
   ```

## 🗄️ مشاكل قاعدة البيانات

### خطأ "Table doesn't exist"

#### الأسباب
- الهجرات لم تطبق بشكل صحيح
- حذف جدول بالخطأ
- مشكلة في إعدادات قاعدة البيانات

#### الحلول
1. **تطبيق الهجرات**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **فحص حالة الهجرات**:
   ```bash
   python manage.py showmigrations
   ```

3. **إعادة إنشاء الجداول المفقودة**:
   ```bash
   python manage.py migrate --run-syncdb
   ```

### خطأ "Duplicate entry"

#### الأسباب
- محاولة إدخال قيمة مكررة في حقل فريد
- مشكلة في القيود المرجعية

#### الحلول
1. **فحص البيانات المكررة**:
   ```sql
   -- البحث عن الموظفين المكررين
   SELECT emp_code, COUNT(*) 
   FROM employees 
   GROUP BY emp_code 
   HAVING COUNT(*) > 1;
   ```

2. **حذف البيانات المكررة**:
   ```sql
   -- حذف الموظفين المكررين (احتفظ بالأحدث)
   DELETE e1 FROM employees e1
   INNER JOIN employees e2 
   WHERE e1.id < e2.id AND e1.emp_code = e2.emp_code;
   ```

### مشكلة في الترميز (Encoding)

#### الأعراض
- ظهور رموز غريبة بدلاً من النص العربي
- أخطاء في حفظ النصوص العربية

#### الحلول
1. **فحص ترميز قاعدة البيانات**:
   ```sql
   SHOW VARIABLES LIKE 'character_set%';
   SHOW VARIABLES LIKE 'collation%';
   ```

2. **تعديل ترميز قاعدة البيانات**:
   ```sql
   ALTER DATABASE eldawliya_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   -- تعديل ترميز الجداول
   ALTER TABLE employees CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **تحديث إعدادات Django**:
   ```python
   # في settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'OPTIONS': {
               'charset': 'utf8mb4',
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           },
       }
   }
   ```

## 📱 مشاكل واجهة المستخدم

### الصفحة لا تحمل بشكل صحيح

#### الأعراض
- صفحة بيضاء فارغة
- عناصر مفقودة أو غير منسقة
- أخطاء JavaScript

#### التشخيص
```bash
# فحص ملفات CSS و JavaScript
python manage.py collectstatic --noinput

# فحص سجلات الخادم
tail -f /var/log/nginx/error.log
tail -f /var/log/eldawliya/django.log
```

#### الحلول
1. **مسح ذاكرة التخزين المؤقت**:
   ```bash
   # مسح ذاكرة Django
   python manage.py clear_cache
   
   # إعادة جمع الملفات الثابتة
   python manage.py collectstatic --clear --noinput
   ```

2. **فحص إعدادات الملفات الثابتة**:
   ```python
   # في settings.py
   STATIC_URL = '/static/'
   STATIC_ROOT = '/var/www/eldawliya/static/'
   STATICFILES_DIRS = [
       BASE_DIR / 'static',
   ]
   ```

3. **إعادة تشغيل خادم الويب**:
   ```bash
   sudo systemctl restart nginx
   sudo systemctl restart eldawliya-web
   ```

### مشكلة في عرض النصوص العربية

#### الأعراض
- النص يظهر من اليسار لليمين
- الخطوط لا تظهر بشكل صحيح

#### الحلول
1. **التأكد من إعدادات RTL**:
   ```css
   /* في ملف CSS الرئيسي */
   body {
       direction: rtl;
       text-align: right;
       font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
   }
   
   .ltr {
       direction: ltr;
       text-align: left;
   }
   ```

2. **تحديث ملفات الخطوط**:
   ```html
   <!-- في base.html -->
   <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
   ```

## 🔧 أدوات التشخيص المفيدة

### سكريبت فحص صحة النظام

```bash
#!/bin/bash
# health_check.sh

echo "=== فحص صحة نظام الدولية ==="
echo "التاريخ: $(date)"
echo

# فحص الخدمات
echo "1. حالة الخدمات:"
services=("eldawliya-web" "eldawliya-worker" "mysql" "redis" "nginx")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "   ✅ $service: يعمل"
    else
        echo "   ❌ $service: متوقف"
    fi
done
echo

# فحص استخدام الموارد
echo "2. استخدام الموارد:"
echo "   المعالج: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "   الذاكرة: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "   القرص الصلب: $(df -h / | awk 'NR==2{print $5}')"
echo

# فحص قاعدة البيانات
echo "3. قاعدة البيانات:"
if mysql -u root -p"$DB_PASSWORD" -e "SELECT 1;" &>/dev/null; then
    echo "   ✅ الاتصال: ناجح"
    connections=$(mysql -u root -p"$DB_PASSWORD" -e "SHOW STATUS LIKE 'Threads_connected';" | awk 'NR==2{print $2}')
    echo "   الاتصالات النشطة: $connections"
else
    echo "   ❌ الاتصال: فاشل"
fi
echo

# فحص سجلات الأخطاء
echo "4. آخر الأخطاء:"
if [ -f /var/log/eldawliya/error.log ]; then
    echo "   آخر 3 أخطاء:"
    tail -n 3 /var/log/eldawliya/error.log | sed 's/^/   /'
else
    echo "   لا توجد أخطاء حديثة"
fi
```

### سكريبت إعادة التشغيل الآمن

```bash
#!/bin/bash
# safe_restart.sh

echo "بدء إعادة التشغيل الآمن لنظام الدولية..."

# إنشاء نسخة احتياطية سريعة
echo "إنشاء نسخة احتياطية..."
mysqldump -u backup_user -p eldawliya_db > /tmp/emergency_backup_$(date +%Y%m%d_%H%M%S).sql

# إيقاف الخدمات بالترتيب الصحيح
echo "إيقاف الخدمات..."
sudo systemctl stop eldawliya-web
sudo systemctl stop eldawliya-worker
sleep 5

# إعادة تشغيل قاعدة البيانات إذا لزم الأمر
if ! mysql -u root -p -e "SELECT 1;" &>/dev/null; then
    echo "إعادة تشغيل قاعدة البيانات..."
    sudo systemctl restart mysql
    sleep 10
fi

# إعادة تشغيل الخدمات
echo "إعادة تشغيل الخدمات..."
sudo systemctl start eldawliya-worker
sleep 5
sudo systemctl start eldawliya-web

# التحقق من الحالة
echo "التحقق من الحالة..."
sleep 10

if curl -f http://localhost:8000/health/ &>/dev/null; then
    echo "✅ النظام يعمل بشكل طبيعي"
else
    echo "❌ مشكلة في النظام - راجع السجلات"
    tail -n 10 /var/log/eldawliya/error.log
fi
```

## 📞 متى تطلب المساعدة

### اطلب المساعدة فوراً في هذه الحالات:
- **فقدان البيانات**: أي مؤشر على فقدان أو تلف البيانات
- **اختراق أمني**: أنشطة مشبوهة أو غير مصرح بها
- **انقطاع كامل**: النظام لا يعمل لأكثر من 30 دقيقة
- **أخطاء قاعدة البيانات الحرجة**: فساد في البيانات أو أخطاء لا يمكن إصلاحها

### معلومات مطلوبة عند طلب المساعدة:
1. **وصف المشكلة**: ما الذي حدث بالضبط؟
2. **وقت حدوث المشكلة**: متى بدأت المشكلة؟
3. **الخطوات المتخذة**: ما الذي جربته لحل المشكلة؟
4. **رسائل الخطأ**: أي رسائل خطأ ظهرت؟
5. **سجلات النظام**: آخر 50 سطر من سجلات الأخطاء
6. **معلومات البيئة**: إصدار النظام، نظام التشغيل، إعدادات الخادم

### جهات الاتصال للطوارئ:
- **الدعم الفني**: extension 123
- **مدير النظام**: extension 124
- **مطور النظام**: extension 125

---

**تذكر**: الوقاية خير من العلاج. راجع دليل الصيانة الدورية لتجنب معظم هذه المشاكل.