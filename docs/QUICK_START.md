# 🚀 دليل البدء السريع - نظام الدولية مع API

## المشكلة الحالية وحلها

### المشكلة
```
ModuleNotFoundError: No module named 'dotenv'
```

### الحل السريع

#### الطريقة الأولى: تثبيت المكتبات المطلوبة
```bash
pip install python-dotenv google-generativeai drf-yasg djangorestframework-simplejwt django-cors-headers
```

#### الطريقة الثانية: استخدام ملف التشغيل المبسط
```bash
# في Windows
run_simple.bat

# في Linux/Mac
chmod +x run_simple.sh && ./run_simple.sh
```

#### الطريقة الثالثة: التثبيت التلقائي
```bash
python install_requirements.py
```

## خطوات التشغيل

### 1. تثبيت المتطلبات
```bash
# تثبيت المكتبات الأساسية
pip install Django djangorestframework python-dotenv

# تثبيت مكتبات API
pip install drf-yasg djangorestframework-simplejwt django-cors-headers

# تثبيت مكتبة Gemini AI
pip install google-generativeai
```

### 2. إعداد قاعدة البيانات
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. إنشاء مستخدم مشرف (اختياري)
```bash
python manage.py createsuperuser
```

### 4. تشغيل الخادم
```bash
python manage.py runserver
```

## الوصول للنظام

### الواجهات المتاحة
- **التطبيق الرئيسي**: http://localhost:8000/
- **لوحة الإدارة**: http://localhost:8000/admin/
- **وثائق API**: http://localhost:8000/api/v1/docs/
- **حالة API**: http://localhost:8000/api/v1/status/

### اختبار API

#### 1. فحص حالة النظام
```bash
curl http://localhost:8000/api/v1/status/
```

#### 2. الحصول على وثائق API
افتح في المتصفح: http://localhost:8000/api/v1/docs/

## إعداد الذكاء الاصطناعي (اختياري)

### 1. الحصول على مفتاح Gemini API
1. اذهب إلى: https://makersuite.google.com/app/apikey
2. أنشئ مفتاح API جديد
3. انسخ المفتاح

### 2. إعداد متغيرات البيئة
أنشئ ملف `.env` في جذر المشروع:
```env
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash
```

### 3. اختبار الذكاء الاصطناعي
```bash
# إنشاء مفتاح API
python manage.py create_api_key admin --name "Test Key"

# اختبار المحادثة
curl -X POST http://localhost:8000/api/v1/ai/chat/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "مرحبا"}'
```

## استكشاف الأخطاء

### خطأ: ModuleNotFoundError
```bash
# تثبيت المكتبة المفقودة
pip install [package-name]

# أو تثبيت جميع المتطلبات
pip install -r requirements.txt
```

### خطأ: Database connection
```bash
# تحقق من إعدادات قاعدة البيانات في settings.py
# أو استخدم SQLite للتطوير
```

### خطأ: Port already in use
```bash
# استخدم منفذ مختلف
python manage.py runserver 8001
```

## الميزات المتاحة

### ✅ API شامل
- مصادقة متعددة (API Key, JWT, Session)
- وثائق تفاعلية (Swagger)
- نظام صلاحيات متقدم
- مراقبة الاستخدام

### ✅ الذكاء الاصطناعي
- محادثات ذكية مع Gemini
- تحليل البيانات
- استخراج الرؤى والتوصيات

### ✅ إدارة البيانات
- الموارد البشرية
- المخزون والمنتجات
- المهام والاجتماعات
- نظام التنبيهات

## أوامر مفيدة

```bash
# إنشاء مفتاح API
python manage.py create_api_key username

# إعداد مجموعات المستخدمين
python manage.py setup_api_groups

# تشغيل الاختبارات
python manage.py test api

# جمع الملفات الثابتة
python manage.py collectstatic

# تشغيل shell Django
python manage.py shell
```

## الدعم والمساعدة

### 📚 الوثائق
- [دليل API الكامل](api/README.md)
- [أمثلة الاستخدام](api_examples.py)
- [إعداد قاعدة البيانات](README_DB_SETUP.md)

### 🛠️ أدوات التطوير
- [إعداد تلقائي](setup_api.py)
- [تشغيل محسن](run_api_server.py)
- [اختبارات شاملة](test_api.py)

### 🔧 استكشاف الأخطاء
1. تأكد من تثبيت Python 3.7+
2. تأكد من تثبيت جميع المتطلبات
3. تحقق من إعدادات قاعدة البيانات
4. راجع سجلات الأخطاء في وحدة التحكم

---

**ملاحظة**: هذا النظام في مرحلة التطوير. للاستخدام في الإنتاج، يرجى مراجعة إعدادات الأمان والأداء.
