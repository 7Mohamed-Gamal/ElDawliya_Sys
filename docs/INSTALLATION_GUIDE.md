# دليل التثبيت والنشر - نظام الموارد البشرية الشامل

## متطلبات النظام

### متطلبات الخادم

- **نظام التشغيل**: Windows Server 2019+ أو Linux (Ubuntu 20.04+)
- **المعالج**: Intel Core i5 أو أعلى
- **الذاكرة**: 8GB RAM كحد أدنى (16GB مُوصى به)
- **التخزين**: 100GB مساحة فارغة كحد أدنى
- **الشبكة**: اتصال إنترنت مستقر

### متطلبات البرمجيات

- **Python**: الإصدار 3.8 أو أحدث
- **قاعدة البيانات**: SQL Server 2017+ أو PostgreSQL 12+
- **خادم الويب**: IIS أو Nginx أو Apache
- **Redis**: للتخزين المؤقت (اختياري ولكن مُوصى به)

## التثبيت خطوة بخطوة

### 1. تحضير البيئة

#### تثبيت Python

```bash
# على Ubuntu/Debian
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev

# على Windows
# قم بتحميل Python من python.org وتثبيته
```

#### تثبيت قاعدة البيانات

```bash
# تثبيت PostgreSQL على Ubuntu
sudo apt install postgresql postgresql-contrib

# إنشاء قاعدة بيانات
sudo -u postgres createdb hr_system
sudo -u postgres createuser hr_user
sudo -u postgres psql -c "ALTER USER hr_user PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hr_system TO hr_user;"
```

### 2. تحميل وإعداد المشروع

```bash
# استنساخ المشروع
git clone https://github.com/your-repo/hr-system.git
cd hr-system

# إنشاء البيئة الافتراضية
python3 -m venv venv

# تفعيل البيئة الافتراضية
# على Linux/Mac
source venv/bin/activate
# على Windows
venv\Scripts\activate

# تثبيت المتطلبات
pip install -r requirements.txt
```

### 3. إعداد متغيرات البيئة

إنشاء ملف `.env` في جذر المشروع:

```env
# إعدادات Django
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1

# إعدادات قاعدة البيانات
DATABASE_URL=postgresql://hr_user:your_password@localhost:5432/hr_system

# إعدادات البريد الإلكتروني
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# إعدادات Redis (اختياري)
REDIS_URL=redis://localhost:6379/0

# إعدادات التشفير
HR_ENCRYPTION_KEY=your-encryption-key-here

# إعدادات المراقبة
ENABLE_PERFORMANCE_MONITORING=True
ENABLE_SYSTEM_MONITORING=True
```

### 4. إعداد قاعدة البيانات

```bash
# تطبيق الهجرات
python manage.py migrate

# إنشاء مستخدم إداري
python manage.py createsuperuser

# تحميل البيانات التجريبية (اختياري)
python manage.py loaddata Hr/fixtures/sample_data.json
```

### 5. جمع الملفات الثابتة

```bash
# جمع ملفات CSS و JavaScript
python manage.py collectstatic --noinput
```

### 6. اختبار التثبيت

```bash
# تشغيل الخادم التطويري للاختبار
python manage.py runserver 0.0.0.0:8000

# فتح المتصفح والانتقال إلى
# http://localhost:8000
```

## النشر في الإنتاج

### 1. إعداد Gunicorn

```bash
# تثبيت Gunicorn
pip install gunicorn

# إنشاء ملف إعداد Gunicorn
# gunicorn.conf.py
```

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### 2. إعداد Nginx

```nginx
# /etc/nginx/sites-available/hr-system
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /path/to/hr-system/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/hr-system/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. إعداد SSL

```bash
# تثبيت Certbot
sudo apt install certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com
```

### 4. إعداد خدمة النظام

```ini
# /etc/systemd/system/hr-system.service
[Unit]
Description=HR System Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/hr-system
ExecStart=/path/to/hr-system/venv/bin/gunicorn --config gunicorn.conf.py ElDawliya_sys.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# تفعيل وتشغيل الخدمة
sudo systemctl daemon-reload
sudo systemctl enable hr-system
sudo systemctl start hr-system
```

## إعداد النسخ الاحتياطي

### 1. نسخ احتياطي لقاعدة البيانات

```bash
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/hr_system"
DB_NAME="hr_system"
DB_USER="hr_user"

mkdir -p $BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# ضغط النسخة الاحتياطية
gzip $BACKUP_DIR/db_backup_$DATE.sql

# حذف النسخ الاحتياطية الأقدم من 30 يوم
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### 2. نسخ احتياطي للملفات

```bash
#!/bin/bash
# backup_files.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/hr_system"
PROJECT_DIR="/path/to/hr-system"

# نسخ احتياطي للملفات المرفوعة
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $PROJECT_DIR media/

# نسخ احتياطي لملفات الإعداد
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz -C $PROJECT_DIR .env gunicorn.conf.py
```

### 3. جدولة النسخ الاحتياطي

```bash
# إضافة إلى crontab
crontab -e

# نسخ احتياطي يومي في الساعة 2:00 صباحاً
0 2 * * * /path/to/backup_db.sh
30 2 * * * /path/to/backup_files.sh
```

## المراقبة والصيانة

### 1. مراقبة النظام

```bash
# مراقبة حالة الخدمة
sudo systemctl status hr-system

# مراقبة السجلات
sudo journalctl -u hr-system -f

# مراقبة استخدام الموارد
htop
```

### 2. تحديث النظام

```bash
#!/bin/bash
# update_system.sh

cd /path/to/hr-system

# إيقاف الخدمة
sudo systemctl stop hr-system

# تحديث الكود
git pull origin main

# تفعيل البيئة الافتراضية
source venv/bin/activate

# تحديث المتطلبات
pip install -r requirements.txt

# تطبيق الهجرات الجديدة
python manage.py migrate

# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# إعادة تشغيل الخدمة
sudo systemctl start hr-system
```

## استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. خطأ في الاتصال بقاعدة البيانات

```bash
# التحقق من حالة قاعدة البيانات
sudo systemctl status postgresql

# التحقق من إعدادات الاتصال
python manage.py dbshell
```

#### 2. مشاكل الصلاحيات

```bash
# إعطاء صلاحيات للملفات
sudo chown -R www-data:www-data /path/to/hr-system
sudo chmod -R 755 /path/to/hr-system
```

#### 3. مشاكل الذاكرة

```bash
# مراقبة استخدام الذاكرة
free -h

# إعادة تشغيل الخدمة لتحرير الذاكرة
sudo systemctl restart hr-system
```

## الأمان

### 1. تأمين قاعدة البيانات

- تغيير كلمات المرور الافتراضية
- تقييد الوصول للشبكة المحلية فقط
- تفعيل التشفير للاتصالات

### 2. تأمين الخادم

- تحديث النظام بانتظام
- تفعيل جدار الحماية
- استخدام مفاتيح SSH بدلاً من كلمات المرور

### 3. تأمين التطبيق

- استخدام HTTPS فقط
- تفعيل حماية CSRF
- تحديث Django والمكتبات بانتظام

---

*للحصول على مساعدة إضافية، يرجى التواصل مع فريق الدعم الفني*