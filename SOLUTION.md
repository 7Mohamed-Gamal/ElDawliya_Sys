# 🔧 حل مشكلة تشغيل نظام الدولية

## المشكلة
```
ModuleNotFoundError: No module named 'dotenv'
```

## الحل المطبق

### 1. تعطيل مؤقت للـ API
قمت بتعطيل مكونات API مؤقتاً حتى يتم تثبيت المكتبات المطلوبة:

- ✅ تعطيل `api.apps.ApiConfig` من `INSTALLED_APPS`
- ✅ تعطيل `rest_framework` و مكتباته
- ✅ تعطيل `corsheaders.middleware.CorsMiddleware`
- ✅ تعطيل مسار `/api/v1/` من URLs

### 2. إصلاح ملف settings.py
- ✅ جعل `python-dotenv` اختياري
- ✅ إضافة try/except للمكتبات غير المثبتة

## طرق التشغيل المتاحة

### الطريقة الأولى: التشغيل الأساسي (بدون API)
```bash
# في Windows
start_basic.bat

# أو باستخدام Python
python run_basic.py

# أو يدوياً
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### الطريقة الثانية: تثبيت المكتبات وتفعيل API
```bash
# 1. تثبيت المكتبات الأساسية
pip install djangorestframework drf-yasg djangorestframework-simplejwt

# 2. تثبيت مكتبات الذكاء الاصطناعي
pip install google-generativeai python-dotenv django-cors-headers

# 3. تفعيل API في settings.py
# إلغاء التعليق عن السطور المعطلة

# 4. تفعيل مسار API في urls.py
# إلغاء التعليق عن path('api/v1/', include('api.urls'))

# 5. تشغيل النظام
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver
```

## الوصول للنظام

### النظام الأساسي (متاح الآن)
- **التطبيق الرئيسي**: http://localhost:8000/
- **لوحة الإدارة**: http://localhost:8000/admin/
- **الموارد البشرية**: http://localhost:8000/Hr/
- **المخزون**: http://localhost:8000/inventory/
- **المهام**: http://localhost:8000/tasks/
- **الاجتماعات**: http://localhost:8000/meetings/

### API (بعد تثبيت المكتبات)
- **وثائق API**: http://localhost:8000/api/v1/docs/
- **حالة API**: http://localhost:8000/api/v1/status/
- **ReDoc**: http://localhost:8000/api/v1/redoc/

## الخطوات التالية

### للاستخدام الفوري
```bash
start_basic.bat
```

### لتفعيل جميع الميزات
1. **تثبيت المكتبات**:
   ```bash
   pip install -r requirements.txt
   ```

2. **تفعيل API في settings.py**:
   ```python
   # إلغاء التعليق عن هذه السطور:
   'rest_framework',
   'rest_framework_simplejwt', 
   'corsheaders',
   'drf_yasg',
   'api.apps.ApiConfig',
   ```

3. **تفعيل CORS middleware**:
   ```python
   # إلغاء التعليق عن:
   'corsheaders.middleware.CorsMiddleware',
   ```

4. **تفعيل مسار API في urls.py**:
   ```python
   # إلغاء التعليق عن:
   path('api/v1/', include('api.urls')),
   ```

5. **تشغيل الترحيلات**:
   ```bash
   python manage.py makemigrations api
   python manage.py migrate
   ```

6. **إعداد API**:
   ```bash
   python setup_api.py
   ```

## الميزات المتاحة حالياً

### ✅ النظام الأساسي
- إدارة الموارد البشرية
- إدارة المخزون
- إدارة المهام
- إدارة الاجتماعات
- نظام التنبيهات
- نظام الصلاحيات
- تسجيل الأحداث

### ⏳ الميزات المعطلة مؤقتاً
- REST API
- وثائق Swagger
- الذكاء الاصطناعي (Gemini)
- مصادقة JWT
- CORS headers

## استكشاف الأخطاء

### خطأ: No module named 'X'
```bash
pip install [package-name]
```

### خطأ: Database connection
```bash
# تحقق من إعدادات قاعدة البيانات في settings.py
```

### خطأ: Port already in use
```bash
python manage.py runserver 8001
```

## الدعم

للحصول على المساعدة:
1. تأكد من تثبيت Python 3.7+
2. تأكد من تثبيت Django
3. راجع سجلات الأخطاء
4. استخدم `start_basic.bat` للتشغيل السريع

---

**ملاحظة**: هذا حل مؤقت لتشغيل النظام الأساسي. لتفعيل جميع الميزات، يرجى تثبيت المكتبات المطلوبة.
