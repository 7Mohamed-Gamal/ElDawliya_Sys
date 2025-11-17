# 🚀 دليل النشر - نظام الدولية
## Deployment Guide - ElDawliya System

**الإصدار**: 1.0  
**تاريخ التحديث**: 2025-11-17  
**الحالة**: جاهز للنشر

---

## 📋 المتطلبات الأساسية (Prerequisites)

### البرمجيات المطلوبة

- **Python**: 3.7 أو أحدث (يُفضل 3.9+)
- **SQL Server**: 2016 أو أحدث
- **Redis**: 5.0 أو أحدث
- **Nginx**: 1.18 أو أحدث (للإنتاج)
- **Gunicorn**: 23.0.0 أو أحدث (للإنتاج)

### المتطلبات الإضافية

- **ODBC Driver 17 for SQL Server** أو أحدث
- **Git** لإدارة الإصدارات
- **SSL Certificate** للإنتاج (Let's Encrypt مجاني)

---

## 🔧 خطوات التثبيت (Installation Steps)

### 1. استنساخ المشروع (Clone Repository)

```bash
# استنساخ المشروع
git clone https://github.com/7Mohamed-Gamal7/ElDawliya_Sys.git
cd ElDawliya_Sys

# التبديل إلى الفرع المطلوب
git checkout main
```

### 2. إنشاء البيئة الافتراضية (Virtual Environment)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. تثبيت المتطلبات (Install Dependencies)

```bash
# تثبيت المتطلبات الأساسية
pip install --upgrade pip
pip install -r requirements.txt

# للتطوير فقط
pip install -r requirements-dev.txt

# للأمان المحسّن (اختياري)
pip install -r requirements-security.txt
```

### 4. إعداد المتغيرات البيئية (Environment Variables)

```bash
# نسخ ملف المثال
cp .env.example .env

# تحرير الملف وملء القيم الفعلية
# Windows: notepad .env
# Linux/Mac: nano .env
```

**القيم المطلوبة**:
- `DJANGO_SECRET_KEY`: مفتاح سري فريد (استخدم الأمر أدناه لتوليده)
- `DEBUG`: False للإنتاج
- `ALLOWED_HOSTS`: نطاقات الموقع
- `DB_*`: إعدادات قاعدة البيانات
- `EMAIL_*`: إعدادات البريد الإلكتروني

```bash
# توليد مفتاح سري جديد
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. إعداد قاعدة البيانات (Database Setup)

```bash
# إنشاء قاعدة البيانات في SQL Server
# استخدم SQL Server Management Studio أو:
sqlcmd -S localhost -U sa -P YourPassword -Q "CREATE DATABASE ElDawliya_Sys"

# تطبيق الهجرات
python manage.py migrate

# إنشاء مستخدم مدير
python manage.py createsuperuser
```

### 6. جمع الملفات الثابتة (Collect Static Files)

```bash
python manage.py collectstatic --noinput
```

### 7. اختبار التشغيل (Test Run)

```bash
# تشغيل خادم التطوير
python manage.py runserver

# زيارة: http://localhost:8000
# لوحة الإدارة: http://localhost:8000/admin
```

---

## 🔒 إعدادات الأمان (Security Configuration)

### 1. تأمين Django

تأكد من تطبيق الإعدادات التالية في `.env`:

```bash
DEBUG=False
DJANGO_SECRET_KEY=<مفتاح-سري-قوي-وفريد>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. تفعيل HTTPS

```bash
# في .env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 3. فحص الأمان

```bash
# فحص إعدادات النشر
python manage.py check --deploy

# فحص الثغرات الأمنية
bandit -r . -ll

# فحص التبعيات
safety check
```

---

## 🌐 إعداد Nginx (Production Web Server)

### 1. تثبيت Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 2. إنشاء ملف التكوين

```bash
sudo nano /etc/nginx/sites-available/eldawliya
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Static files
    location /static/ {
        alias /path/to/ElDawliya_Sys/staticfiles/;
        expires 30d;
    }
    
    # Media files
    location /media/ {
        alias /path/to/ElDawliya_Sys/media/;
        expires 30d;
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. تفعيل التكوين

```bash
# إنشاء رابط رمزي
sudo ln -s /etc/nginx/sites-available/eldawliya /etc/nginx/sites-enabled/

# اختبار التكوين
sudo nginx -t

# إعادة تشغيل Nginx
sudo systemctl restart nginx
```

---


