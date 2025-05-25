# 🎉 إعداد نظام الدولية مع API - مكتمل!

## ✅ ما تم إنجازه

### 1. تفعيل API بالكامل
- ✅ إلغاء التعليق عن جميع مكونات API في `settings.py`
- ✅ تفعيل مسار API في `urls.py`
- ✅ إصلاح جميع النماذج والـ Serializers
- ✅ تحديث ViewSets للعمل مع قاعدة البيانات الحالية
- ✅ إصلاح خدمات الذكاء الاصطناعي

### 2. إصلاح النماذج
- ✅ استخدام `TblProducts` بدلاً من `Product`
- ✅ استخدام `TblCategories` بدلاً من `Category`
- ✅ استخدام `TblSuppliers` بدلاً من `Supplier`
- ✅ تحديث جميع الحقول لتتوافق مع قاعدة البيانات

### 3. اختبار النظام
- ✅ `python manage.py check` يعمل بدون أخطاء
- ✅ جميع الـ imports تعمل بشكل صحيح
- ✅ النظام جاهز للتشغيل

## 🚀 طرق التشغيل

### الطريقة الأولى: التشغيل الكامل (موصى بها)
```bash
start_complete_system.bat
```

### الطريقة الثانية: التشغيل اليدوي
```bash
# 1. تثبيت المكتبات
pip install djangorestframework drf-yasg djangorestframework-simplejwt django-cors-headers google-generativeai python-dotenv

# 2. إنشاء الترحيلات
python manage.py makemigrations
python manage.py makemigrations api

# 3. تطبيق الترحيلات
python manage.py migrate

# 4. تشغيل الخادم
python manage.py runserver
```

### الطريقة الثالثة: التشغيل الأساسي (بدون API)
```bash
start_basic.bat
```

## 🌐 الوصول للنظام

بعد التشغيل، ستتمكن من الوصول إلى:

### التطبيق الأساسي
- **الصفحة الرئيسية**: http://localhost:8000/
- **لوحة الإدارة**: http://localhost:8000/admin/
- **الموارد البشرية**: http://localhost:8000/Hr/
- **المخزون**: http://localhost:8000/inventory/
- **المهام**: http://localhost:8000/tasks/
- **الاجتماعات**: http://localhost:8000/meetings/

### API والوثائق
- **وثائق API (Swagger)**: http://localhost:8000/api/v1/docs/
- **وثائق API (ReDoc)**: http://localhost:8000/api/v1/redoc/
- **حالة API**: http://localhost:8000/api/v1/status/
- **مخطط API**: http://localhost:8000/api/v1/schema/

## 🔑 المصادقة والوصول

### تسجيل الدخول الافتراضي
- **اسم المستخدم**: admin
- **كلمة المرور**: admin123

### إنشاء مفتاح API
```bash
python manage.py create_api_key admin --name "My API Key"
```

### إعداد مجموعات المستخدمين
```bash
python manage.py setup_api_groups
```

## 📊 نقاط النهاية المتاحة

### البيانات الأساسية
- `GET /api/v1/employees/` - قائمة الموظفين
- `GET /api/v1/departments/` - قائمة الأقسام
- `GET /api/v1/products/` - قائمة المنتجات
- `GET /api/v1/categories/` - قائمة الفئات
- `GET /api/v1/tasks/` - قائمة المهام
- `GET /api/v1/meetings/` - قائمة الاجتماعات

### المصادقة
- `POST /api/v1/auth/token/` - الحصول على JWT token
- `POST /api/v1/auth/token/refresh/` - تجديد JWT token
- `GET /api/v1/api-keys/` - إدارة مفاتيح API

### الذكاء الاصطناعي
- `POST /api/v1/ai/chat/` - محادثة مع Gemini AI
- `POST /api/v1/ai/analyze/` - تحليل البيانات

### المراقبة
- `GET /api/v1/status/` - حالة النظام
- `GET /api/v1/usage-stats/` - إحصائيات الاستخدام

## 🤖 إعداد الذكاء الاصطناعي

### 1. الحصول على مفتاح Gemini
1. اذهب إلى: https://makersuite.google.com/app/apikey
2. أنشئ مفتاح API جديد
3. انسخ المفتاح

### 2. إعداد متغيرات البيئة
أنشئ ملف `.env` أو حدث الموجود:
```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash
```

### 3. اختبار الذكاء الاصطناعي
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "مرحبا! ما هي إمكانيات النظام؟"}'
```

## 📝 أمثلة الاستخدام

### البحث في المنتجات
```bash
curl "http://localhost:8000/api/v1/products/?search=كمبيوتر" \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

### المنتجات منخفضة المخزون
```bash
curl "http://localhost:8000/api/v1/products/?low_stock=true" \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

### البحث في الموظفين
```bash
curl "http://localhost:8000/api/v1/employees/?department=تقنية" \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

### تحليل بيانات الموظفين
```bash
curl -X POST http://localhost:8000/api/v1/ai/analyze/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"data_type": "employees", "analysis_type": "summary"}'
```

## 🛠️ أوامر إدارية مفيدة

```bash
# إنشاء مستخدم مشرف
python manage.py createsuperuser

# إنشاء مفتاح API
python manage.py create_api_key username --name "API Key Name"

# إعداد مجموعات المستخدمين
python manage.py setup_api_groups

# تشغيل الاختبارات
python manage.py test api

# جمع الملفات الثابتة
python manage.py collectstatic

# فحص النظام
python manage.py check
```

## 🔧 استكشاف الأخطاء

### خطأ: ModuleNotFoundError
```bash
pip install [package-name]
```

### خطأ: Database connection
تحقق من إعدادات قاعدة البيانات في `settings.py`

### خطأ: Port already in use
```bash
python manage.py runserver 8001
```

### خطأ: API endpoints not working
تأكد من تثبيت جميع مكتبات API

## 🎯 الخطوات التالية

1. **تشغيل النظام**: `start_complete_system.bat`
2. **إنشاء مفتاح API**: `python manage.py create_api_key admin`
3. **اختبار API**: زيارة http://localhost:8000/api/v1/docs/
4. **إعداد Gemini AI**: إضافة `GEMINI_API_KEY` في `.env`
5. **تخصيص الصلاحيات**: إضافة المستخدمين للمجموعات المناسبة

## 🎉 تهانينا!

نظام الدولية مع API والذكاء الاصطناعي جاهز للاستخدام!

---

**ملاحظة**: للاستخدام في الإنتاج، يرجى مراجعة إعدادات الأمان وتغيير كلمات المرور الافتراضية.
