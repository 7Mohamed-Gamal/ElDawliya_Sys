# ElDawliya System API

API شامل لنظام الدولية الإداري مع دمج الذكاء الاصطناعي باستخدام Google Gemini.

## المميزات

### 🔐 المصادقة والأمان
- **API Key Authentication**: مفاتيح API آمنة للتطبيقات الخارجية
- **JWT Authentication**: رموز JWT للمصادقة المؤقتة
- **Session Authentication**: مصادقة الجلسة للواجهات الداخلية
- **صلاحيات متقدمة**: نظام صلاحيات مرن حسب المجموعات

### 📊 إدارة البيانات
- **الموارد البشرية**: الموظفين والأقسام
- **المخزون**: المنتجات والفئات والموردين
- **المهام**: إدارة المهام والتكليفات
- **الاجتماعات**: جدولة ومتابعة الاجتماعات

### 🤖 الذكاء الاصطناعي
- **Gemini AI Chat**: محادثات ذكية مع السياق
- **تحليل البيانات**: تحليل ذكي لبيانات النظام
- **الرؤى والتوصيات**: استخراج الرؤى والتوصيات

### 📈 المراقبة والتحليل
- **سجلات الاستخدام**: تتبع جميع طلبات API
- **إحصائيات الأداء**: مراقبة أداء API
- **معدل الطلبات**: حماية من الإفراط في الاستخدام

## التثبيت والإعداد

### 1. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 2. إعداد متغيرات البيئة

انسخ ملف `.env.example` إلى `.env` وقم بتعديل القيم:

```bash
cp .env.example .env
```

```env
# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash

# API Configuration
API_RATE_LIMIT=100
API_THROTTLE_ANON=10
API_THROTTLE_USER=60
```

### 3. تشغيل الترحيلات

```bash
python manage.py makemigrations api
python manage.py migrate
```

### 4. إعداد مجموعات المستخدمين

```bash
python manage.py setup_api_groups
```

### 5. إنشاء مفتاح API

```bash
python manage.py create_api_key username --name "My API Key" --expires-days 30
```

## الاستخدام

### Base URL
```
http://localhost:8000/api/v1/
```

### المصادقة

#### 1. API Key Authentication
```http
Authorization: ApiKey YOUR_API_KEY_HERE
```

#### 2. JWT Authentication
```http
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

### نقاط النهاية الرئيسية

#### 📚 الوثائق
- `GET /api/v1/docs/` - Swagger UI
- `GET /api/v1/redoc/` - ReDoc
- `GET /api/v1/schema/` - OpenAPI Schema

#### 🔐 المصادقة
- `POST /api/v1/auth/token/` - الحصول على JWT token
- `POST /api/v1/auth/token/refresh/` - تجديد JWT token
- `POST /api/v1/auth/token/verify/` - التحقق من JWT token

#### 📊 حالة النظام
- `GET /api/v1/status/` - حالة API
- `GET /api/v1/usage-stats/` - إحصائيات الاستخدام

#### 👥 الموارد البشرية
- `GET /api/v1/employees/` - قائمة الموظفين
- `GET /api/v1/employees/{id}/` - تفاصيل موظف
- `GET /api/v1/departments/` - قائمة الأقسام

#### 📦 المخزون
- `GET /api/v1/products/` - قائمة المنتجات
- `GET /api/v1/products/{id}/` - تفاصيل منتج
- `GET /api/v1/categories/` - قائمة الفئات

#### ✅ المهام
- `GET /api/v1/tasks/` - قائمة المهام
- `GET /api/v1/tasks/{id}/` - تفاصيل مهمة

#### 📅 الاجتماعات
- `GET /api/v1/meetings/` - قائمة الاجتماعات
- `GET /api/v1/meetings/{id}/` - تفاصيل اجتماع

#### 🤖 الذكاء الاصطناعي
- `POST /api/v1/ai/chat/` - محادثة مع Gemini
- `POST /api/v1/ai/analyze/` - تحليل البيانات

### أمثلة الاستخدام

#### محادثة مع Gemini AI
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ما هو عدد الموظفين في النظام؟",
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

#### تحليل بيانات الموظفين
```bash
curl -X POST http://localhost:8000/api/v1/ai/analyze/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "data_type": "employees",
    "analysis_type": "summary",
    "filters": {
      "department": "تقنية المعلومات"
    }
  }'
```

#### البحث في المنتجات
```bash
curl -X GET "http://localhost:8000/api/v1/products/?search=كمبيوتر&low_stock=true" \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

## المعاملات والفلاتر

### معاملات البحث العامة
- `search` - البحث في النصوص
- `page` - رقم الصفحة
- `page_size` - حجم الصفحة (الحد الأقصى: 100)

### فلاتر الموظفين
- `department` - اسم القسم
- `status` - حالة الموظف
- `search` - البحث في الاسم والبريد الإلكتروني

### فلاتر المنتجات
- `category` - اسم الفئة
- `low_stock` - المنتجات منخفضة المخزون (true/false)
- `search` - البحث في اسم المنتج

### فلاتر المهام
- `assigned_to` - اسم المستخدم المكلف
- `status` - حالة المهمة
- `priority` - أولوية المهمة

## معدل الطلبات

- **المستخدمين المسجلين**: 60 طلب/دقيقة
- **المستخدمين غير المسجلين**: 10 طلبات/دقيقة

## رموز الاستجابة

- `200` - نجح الطلب
- `201` - تم إنشاء المورد بنجاح
- `400` - خطأ في البيانات المرسلة
- `401` - غير مصرح بالوصول
- `403` - ممنوع الوصول
- `404` - المورد غير موجود
- `429` - تم تجاوز معدل الطلبات
- `500` - خطأ في الخادم

## الأمان

### أفضل الممارسات
1. احتفظ بمفاتيح API في مكان آمن
2. استخدم HTTPS في الإنتاج
3. قم بتجديد مفاتيح API بانتظام
4. راقب سجلات الاستخدام

### الصلاحيات
- `API_Users` - الوصول الأساسي للـ API
- `HR_Users` - الوصول لبيانات الموارد البشرية
- `Inventory_Users` - الوصول لبيانات المخزون
- `Meeting_Users` - الوصول لبيانات الاجتماعات
- `AI_Users` - استخدام ميزات الذكاء الاصطناعي

## الدعم والمساعدة

للحصول على المساعدة أو الإبلاغ عن مشاكل:
- البريد الإلكتروني: admin@eldawliya.com
- الوثائق التفاعلية: `/api/v1/docs/`
