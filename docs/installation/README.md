# دليل التثبيت والنشر - نظام الدولية

## نظرة عامة

هذا الدليل يوضح كيفية تثبيت ونشر نظام الدولية على خادم إنتاج. يغطي جميع الخطوات من إعداد البيئة إلى تشغيل النظام بالكامل.

## 📋 متطلبات النظام

### الحد الأدنى للمتطلبات
- **نظام التشغيل**: Ubuntu 20.04 LTS أو CentOS 8+
- **المعالج**: 2 CPU cores
- **الذاكرة**: 4 GB RAM
- **التخزين**: 50 GB مساحة حرة
- **الشبكة**: اتصال إنترنت مستقر

### المتطلبات الموصى بها
- **نظام التشغيل**: Ubuntu 22.04 LTS
- **المعالج**: 4+ CPU cores
- **الذاكرة**: 8+ GB RAM
- **التخزين**: 100+ GB SSD
- **الشبكة**: 100 Mbps أو أسرع

### المتطلبات البرمجية
- **Python**: 3.9+
- **قاعدة البيانات**: SQL Server 2019+ أو MySQL 8.0+
- **خادم الويب**: Nginx 1.18+
- **Redis**: 6.0+ (للتخزين المؤقت)
- **Git**: لإدارة الكود المصدري

## 🚀 التثبيت السريع (Ubuntu)

### الخطوة 1: تحديث النظام
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim htop
```

### الخطوة 2: تثبيت Python والأدوات المطلوبة
```bash
# تثبيت Python 3.9+
sudo apt install -y python3.9 python3.9-venv python3.9-dev python3-pip

# تثبيت أدوات التطوير
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y pkg-config default-libmysqlclient-dev

# إنشاء رابط symbolic لـ Python
sudo ln -sf /usr/bin/python3.9 /usr/bin/python3
```

### الخطوة 3: تثبيت قاعدة البيانات

#### خيار أ: MySQL
```bash
# تثبيت MySQL
sudo apt install -y mysql-server mysql-client

# تأمين MySQL
sudo mysql_secure_installation

# إنشاء قاعدة البيانات والمستخدم
sudo mysql -u root -p
```

```sql
-- في MySQL shell
CREATE DATABASE eldawliya_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'eldawliya_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON eldawliya_db.* TO 'eldawliya_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### خيار ب: SQL Server (إذا كان متاحاً)
```bash
# تثبيت Microsoft ODBC Driver
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list

sudo apt update
sudo apt install -y msodbcsql17 unixodbc-dev
```

### الخطوة 4: تثبيت Redis
```bash
sudo apt install -y redis-server

# تفعيل Redis للبدء التلقائي
sudo systemctl enable redis-server
sudo systemctl start redis-server

# اختبار Redis
redis-cli ping
```

### الخطوة 5: تثبيت Nginx
```bash
sudo apt install -y nginx

# تفعيل Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

## 📦 تثبيت التطبيق

### الخطوة 1: إنشاء مستخدم النظام
```bash
# إنشاء مستخدم مخصص للتطبيق
sudo adduser --system --group --home /opt/eldawliya eldawliya
sudo usermod -aG www-data eldawliya
```

### الخطوة 2: تحميل الكود المصدري
```bash
# التبديل للمستخدم الجديد
sudo su - eldawliya

# تحميل الكود (استبدل بالرابط الصحيح)
git clone https://github.com/your-company/eldawliya-system.git /opt/eldawliya/app
cd /opt/eldawliya/app
```

### الخطوة 3: إعداد البيئة الافتراضية
```bash
# إنشاء البيئة الافتراضية
python3 -m venv /opt/eldawliya/venv

# تفعيل البيئة الافتراضية
source /opt/eldawliya/venv/bin/activate

# تحديث pip
pip install --upgrade pip setuptools wheel
```

### الخطوة 4: تثبيت المتطلبات
```bash
# تثبيت المتطلبات الأساسية
pip install -r requirements/production.txt

# إذا كنت تستخدم SQL Server
pip install mssql-django pyodbc

# إذا كنت تستخدم MySQL
pip install mysqlclient
```

## ⚙️ إعداد التكوين

### الخطوة 1: إنشاء ملف البيئة
```bash
# إنشاء ملف .env
cp .env.example .env
vim .env
```

```bash
# محتوى ملف .env
DEBUG=False
SECRET_KEY=your-very-long-and-random-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost

# إعدادات قاعدة البيانات - MySQL
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=eldawliya_db
DATABASE_USER=eldawliya_user
DATABASE_PASSWORD=strong_password_here
DATABASE_HOST=localhost
DATABASE_PORT=3306

# إعدادات قاعدة البيانات - SQL Server
# DATABASE_ENGINE=mssql
# DATABASE_NAME=eldawliya_db
# DATABASE_USER=sa
# DATABASE_PASSWORD=your_password
# DATABASE_HOST=localhost
# DATABASE_PORT=1433

# إعدادات Redis
REDIS_URL=redis://localhost:6379/0

# إعدادات البريد الإلكتروني
EMAIL_HOST=smtp.your-company.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@your-company.com
EMAIL_HOST_PASSWORD=email_password
DEFAULT_FROM_EMAIL=نظام الدولية <noreply@your-company.com>

# إعدادات الأمان
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# مسارات الملفات
STATIC_ROOT=/opt/eldawliya/static
MEDIA_ROOT=/opt/eldawliya/media
```

### الخطوة 2: إنشاء إعدادات الإنتاج
```bash
# إنشاء ملف إعدادات الإنتاج
mkdir -p ElDawliya_sys/settings
vim ElDawliya_sys/settings/production.py
```

```python
# محتوى production.py
from .base import *
import os
from decouple import config

# إعدادات الأمان
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# قاعدة البيانات
DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE'),
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        } if 'mysql' in config('DATABASE_ENGINE') else {}
    }
}

# التخزين المؤقت
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# الجلسات
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# الملفات الثابتة
STATIC_ROOT = config('STATIC_ROOT')
MEDIA_ROOT = config('MEDIA_ROOT')

# الأمان
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)

# السجلات
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/eldawliya/logs/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/eldawliya/logs/error.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## 🗄️ إعداد قاعدة البيانات

### الخطوة 1: تطبيق الهجرات
```bash
# التأكد من تفعيل البيئة الافتراضية
source /opt/eldawliya/venv/bin/activate
cd /opt/eldawliya/app

# تعيين متغير البيئة
export DJANGO_SETTINGS_MODULE=ElDawliya_sys.settings.production

# إنشاء الهجرات
python manage.py makemigrations

# تطبيق الهجرات
python manage.py migrate

# إنشاء مستخدم مدير
python manage.py createsuperuser
```

### الخطوة 2: جمع الملفات الثابتة
```bash
# إنشاء المجلدات المطلوبة
sudo mkdir -p /opt/eldawliya/static /opt/eldawliya/media /opt/eldawliya/logs
sudo chown -R eldawliya:eldawliya /opt/eldawliya/

# جمع الملفات الثابتة
python manage.py collectstatic --noinput
```

### الخطوة 3: تحميل البيانات الأولية
```bash
# تحميل البيانات الأساسية (إذا كانت متوفرة)
python manage.py loaddata initial_data.json

# إنشاء الأقسام والمناصب الأساسية
python manage.py setup_initial_data
```

## 🔧 إعداد خدمات النظام

### الخطوة 1: إعداد Gunicorn
```bash
# إنشاء ملف إعداد Gunicorn
sudo vim /etc/systemd/system/eldawliya-web.service
```

```ini
[Unit]
Description=ElDawliya Web Application
After=network.target mysql.service redis.service

[Service]
Type=notify
User=eldawliya
Group=eldawliya
RuntimeDirectory=eldawliya
WorkingDirectory=/opt/eldawliya/app
Environment=DJANGO_SETTINGS_MODULE=ElDawliya_sys.settings.production
Environment=PYTHONPATH=/opt/eldawliya/app
ExecStart=/opt/eldawliya/venv/bin/gunicorn \
    --bind unix:/run/eldawliya/eldawliya.sock \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --log-level info \
    --log-file /opt/eldawliya/logs/gunicorn.log \
    --access-logfile /opt/eldawliya/logs/access.log \
    ElDawliya_sys.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### الخطوة 2: إعداد Celery (للمهام الخلفية)
```bash
# إنشاء خدمة Celery Worker
sudo vim /etc/systemd/system/eldawliya-worker.service
```

```ini
[Unit]
Description=ElDawliya Celery Worker
After=network.target redis.service mysql.service

[Service]
Type=forking
User=eldawliya
Group=eldawliya
WorkingDirectory=/opt/eldawliya/app
Environment=DJANGO_SETTINGS_MODULE=ElDawliya_sys.settings.production
Environment=PYTHONPATH=/opt/eldawliya/app
ExecStart=/opt/eldawliya/venv/bin/celery multi start worker1 \
    -A ElDawliya_sys \
    --pidfile=/opt/eldawliya/logs/celery_%n.pid \
    --logfile=/opt/eldawliya/logs/celery_%n.log \
    --loglevel=info \
    --concurrency=4
ExecStop=/opt/eldawliya/venv/bin/celery multi stopwait worker1 \
    --pidfile=/opt/eldawliya/logs/celery_%n.pid
ExecReload=/opt/eldawliya/venv/bin/celery multi restart worker1 \
    -A ElDawliya_sys \
    --pidfile=/opt/eldawliya/logs/celery_%n.pid \
    --logfile=/opt/eldawliya/logs/celery_%n.log \
    --loglevel=info \
    --concurrency=4

[Install]
WantedBy=multi-user.target
```

### الخطوة 3: إعداد Nginx
```bash
# إنشاء ملف إعداد Nginx
sudo vim /etc/nginx/sites-available/eldawliya
```

```nginx
upstream eldawliya_app {
    server unix:/run/eldawliya/eldawliya.sock;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # إعادة توجيه HTTP إلى HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # شهادات SSL (ستحتاج لإعدادها)
    ssl_certificate /etc/ssl/certs/eldawliya.crt;
    ssl_certificate_key /etc/ssl/private/eldawliya.key;
    
    # إعدادات SSL الأمنية
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # إعدادات الأمان
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # إعدادات عامة
    client_max_body_size 100M;
    keepalive_timeout 65;
    
    # الملفات الثابتة
    location /static/ {
        alias /opt/eldawliya/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # ملفات الوسائط
    location /media/ {
        alias /opt/eldawliya/media/;
        expires 1M;
        add_header Cache-Control "public";
    }
    
    # التطبيق الرئيسي
    location / {
        proxy_pass http://eldawliya_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # إعدادات timeout
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # صفحة الصحة
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

```bash
# تفعيل الموقع
sudo ln -s /etc/nginx/sites-available/eldawliya /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# اختبار إعدادات Nginx
sudo nginx -t

# إعادة تحميل Nginx
sudo systemctl reload nginx
```

## 🔐 إعداد شهادات SSL

### استخدام Let's Encrypt (مجاني)
```bash
# تثبيت Certbot
sudo apt install -y certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# إعداد التجديد التلقائي
sudo crontab -e
# أضف هذا السطر:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### استخدام شهادة مخصصة
```bash
# نسخ ملفات الشهادة
sudo cp your-certificate.crt /etc/ssl/certs/eldawliya.crt
sudo cp your-private-key.key /etc/ssl/private/eldawliya.key

# تعيين الصلاحيات الصحيحة
sudo chmod 644 /etc/ssl/certs/eldawliya.crt
sudo chmod 600 /etc/ssl/private/eldawliya.key
```

## 🚀 تشغيل النظام

### الخطوة 1: تفعيل وتشغيل الخدمات
```bash
# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل الخدمات للبدء التلقائي
sudo systemctl enable eldawliya-web
sudo systemctl enable eldawliya-worker

# تشغيل الخدمات
sudo systemctl start eldawliya-web
sudo systemctl start eldawliya-worker

# فحص حالة الخدمات
sudo systemctl status eldawliya-web
sudo systemctl status eldawliya-worker
```

### الخطوة 2: اختبار النظام
```bash
# اختبار الاتصال المحلي
curl -I http://localhost/health/

# اختبار الاتصال الخارجي
curl -I https://your-domain.com/health/

# فحص السجلات
sudo journalctl -u eldawliya-web -f
sudo journalctl -u eldawliya-worker -f
```

## 📊 إعداد المراقبة

### إعداد سجلات النظام
```bash
# إنشاء ملف إعداد logrotate
sudo vim /etc/logrotate.d/eldawliya
```

```
/opt/eldawliya/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 eldawliya eldawliya
    postrotate
        systemctl reload eldawliya-web
    endscript
}
```

### إعداد مراقبة الأداء
```bash
# تثبيت htop للمراقبة
sudo apt install -y htop iotop nethogs

# إعداد مراقبة تلقائية
sudo vim /opt/eldawliya/scripts/monitor.sh
```

```bash
#!/bin/bash
# monitor.sh - سكريبت مراقبة النظام

LOG_FILE="/opt/eldawliya/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# فحص استخدام الذاكرة
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')

# فحص استخدام المعالج
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

# فحص مساحة القرص
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)

# كتابة السجل
echo "$DATE - CPU: ${CPU_USAGE}%, Memory: ${MEMORY_USAGE}%, Disk: ${DISK_USAGE}%" >> $LOG_FILE

# إرسال تنبيه إذا تجاوز الاستخدام 80%
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )) || (( $(echo "$CPU_USAGE > 80" | bc -l) )) || (( DISK_USAGE > 80 )); then
    echo "تحذير: استخدام عالي للموارد - CPU: ${CPU_USAGE}%, Memory: ${MEMORY_USAGE}%, Disk: ${DISK_USAGE}%" | \
    mail -s "تنبيه نظام الدولية" admin@your-company.com
fi
```

```bash
# جعل السكريبت قابل للتنفيذ
chmod +x /opt/eldawliya/scripts/monitor.sh

# إضافة للـ crontab للتشغيل كل 5 دقائق
sudo crontab -e
# أضف هذا السطر:
# */5 * * * * /opt/eldawliya/scripts/monitor.sh
```

## 💾 إعداد النسخ الاحتياطية

### سكريبت النسخ الاحتياطي التلقائي
```bash
sudo vim /opt/eldawliya/scripts/backup.sh
```

```bash
#!/bin/bash
# backup.sh - سكريبت النسخ الاحتياطي

BACKUP_DIR="/opt/eldawliya/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="eldawliya_db"
DB_USER="eldawliya_user"
DB_PASS="your_password"

# إنشاء مجلد النسخة الاحتياطية
mkdir -p $BACKUP_DIR/$DATE

# نسخ قاعدة البيانات
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/$DATE/database.sql

# نسخ ملفات الوسائط
tar -czf $BACKUP_DIR/$DATE/media.tar.gz /opt/eldawliya/media/

# نسخ ملفات التكوين
cp /opt/eldawliya/app/.env $BACKUP_DIR/$DATE/
cp -r /opt/eldawliya/app/ElDawliya_sys/settings/ $BACKUP_DIR/$DATE/settings/

# ضغط النسخة الاحتياطية
cd $BACKUP_DIR
tar -czf eldawliya_backup_$DATE.tar.gz $DATE/
rm -rf $DATE/

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "eldawliya_backup_*.tar.gz" -mtime +30 -delete

# إرسال تقرير
echo "تم إنشاء النسخة الاحتياطية: eldawliya_backup_$DATE.tar.gz" | \
mail -s "تقرير النسخ الاحتياطي" admin@your-company.com
```

```bash
# جعل السكريبت قابل للتنفيذ
chmod +x /opt/eldawliya/scripts/backup.sh

# إضافة للـ crontab للتشغيل يومياً في 2:00 ص
sudo crontab -e
# أضف هذا السطر:
# 0 2 * * * /opt/eldawliya/scripts/backup.sh
```

## 🔧 الصيانة والتحديثات

### سكريبت التحديث الآمن
```bash
sudo vim /opt/eldawliya/scripts/update.sh
```

```bash
#!/bin/bash
# update.sh - سكريبت التحديث الآمن

APP_DIR="/opt/eldawliya/app"
BACKUP_DIR="/opt/eldawliya/backups/pre_update_$(date +%Y%m%d_%H%M%S)"

echo "بدء عملية التحديث..."

# إنشاء نسخة احتياطية
echo "إنشاء نسخة احتياطية..."
mkdir -p $BACKUP_DIR
mysqldump -u eldawliya_user -p eldawliya_db > $BACKUP_DIR/database.sql
cp -r $APP_DIR $BACKUP_DIR/app_backup

# إيقاف الخدمات
echo "إيقاف الخدمات..."
sudo systemctl stop eldawliya-web
sudo systemctl stop eldawliya-worker

# تحديث الكود
echo "تحديث الكود..."
cd $APP_DIR
git pull origin main

# تفعيل البيئة الافتراضية وتحديث المتطلبات
source /opt/eldawliya/venv/bin/activate
pip install -r requirements/production.txt

# تطبيق الهجرات
echo "تطبيق هجرات قاعدة البيانات..."
python manage.py migrate

# جمع الملفات الثابتة
echo "جمع الملفات الثابتة..."
python manage.py collectstatic --noinput

# إعادة تشغيل الخدمات
echo "إعادة تشغيل الخدمات..."
sudo systemctl start eldawliya-worker
sleep 5
sudo systemctl start eldawliya-web

# اختبار النظام
echo "اختبار النظام..."
sleep 10
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ التحديث تم بنجاح"
    # حذف النسخة الاحتياطية المؤقتة بعد أسبوع
    echo "rm -rf $BACKUP_DIR" | at now + 7 days
else
    echo "❌ فشل التحديث - استعادة النسخة الاحتياطية"
    # استعادة النسخة الاحتياطية
    sudo systemctl stop eldawliya-web eldawliya-worker
    mysql -u eldawliya_user -p eldawliya_db < $BACKUP_DIR/database.sql
    rm -rf $APP_DIR
    mv $BACKUP_DIR/app_backup $APP_DIR
    sudo systemctl start eldawliya-worker eldawliya-web
fi
```

## ✅ قائمة التحقق النهائية

### قبل الإطلاق
- [ ] جميع الخدمات تعمل بشكل صحيح
- [ ] قاعدة البيانات تستجيب
- [ ] الملفات الثابتة تحمل بشكل صحيح
- [ ] شهادات SSL مثبتة وتعمل
- [ ] النسخ الاحتياطية تعمل تلقائياً
- [ ] المراقبة والسجلات تعمل
- [ ] اختبار جميع الوظائف الأساسية
- [ ] إعداد حسابات المستخدمين الأولية
- [ ] تدريب المستخدمين الأساسيين

### بعد الإطلاق
- [ ] مراقبة الأداء لمدة 24 ساعة
- [ ] فحص السجلات للأخطاء
- [ ] اختبار النسخ الاحتياطية
- [ ] جمع ملاحظات المستخدمين
- [ ] توثيق أي مشاكل وحلولها

## 📞 الدعم والمساعدة

### في حالة المشاكل أثناء التثبيت:
1. **راجع السجلات**: `sudo journalctl -u eldawliya-web -f`
2. **تحقق من الخدمات**: `sudo systemctl status eldawliya-web`
3. **اختبر قاعدة البيانات**: `python manage.py dbshell`
4. **راجع ملف .env**: تأكد من صحة جميع المتغيرات

### جهات الاتصال:
- **الدعم الفني**: support@your-company.com
- **مطور النظام**: developer@your-company.com
- **مدير النظام**: admin@your-company.com

---

**تهانينا! 🎉 تم تثبيت نظام الدولية بنجاح**

للمزيد من المساعدة، راجع:
- [دليل المدير](../admin_guide/README.md)
- [دليل استكشاف الأخطاء](../admin_guide/troubleshooting.md)
- [دليل المستخدم](../user_guide/README.md)