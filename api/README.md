# تطبيق واجهة برمجة التطبيقات (API Application)

## نظرة عامة (Application Overview)

تطبيق واجهة برمجة التطبيقات يوفر REST API شامل لنظام الدولية مع تكامل الذكاء الاصطناعي. يتضمن إدارة مفاتيح API، محادثات الذكاء الاصطناعي، تسجيل الاستخدام، وواجهات برمجية لجميع وحدات النظام.

**الغرض الرئيسي**: توفير واجهات برمجية آمنة ومتكاملة مع دعم الذكاء الاصطناعي.

## الميزات الرئيسية (Key Features)

### 1. REST API شامل (Comprehensive REST API)
- واجهات برمجية لجميع وحدات النظام
- مصادقة آمنة بمفاتيح API
- تسلسل البيانات المتقدم
- فلترة وبحث متقدم
- ترقيم الصفحات

### 2. تكامل الذكاء الاصطناعي (AI Integration)
- دعم Google Gemini
- محادثات ذكية
- تحليل البيانات بالذكاء الاصطناعي
- معالجة اللغة الطبيعية
- إجابات ذكية على الاستفسارات

### 3. إدارة مفاتيح API (API Key Management)
- إنشاء وإدارة مفاتيح API
- تحكم في الصلاحيات
- تتبع الاستخدام
- انتهاء صلاحية المفاتيح
- إحصائيات الاستخدام

### 4. تسجيل الاستخدام (Usage Logging)
- تسجيل جميع طلبات API
- مراقبة الأداء
- إحصائيات مفصلة
- تحليل الاستخدام
- تنبيهات الحدود

### 5. واجهة ويب تفاعلية (Interactive Web Interface)
- واجهة ويب لاختبار API
- محرر طلبات تفاعلي
- عرض الاستجابات
- توثيق تفاعلي
- أمثلة عملية

## هيكل النماذج (Models Documentation)

### APIKey (مفتاح API)
```python
class APIKey(models.Model):
    name = models.CharField(max_length=100)                            # اسم المفتاح
    key = models.CharField(max_length=64, unique=True)                 # المفتاح
    user = models.ForeignKey(User, on_delete=models.CASCADE)           # المستخدم
    is_active = models.BooleanField(default=True)                      # نشط
    permissions = models.JSONField(default=list)                       # الصلاحيات
    rate_limit = models.IntegerField(default=1000)                     # حد المعدل (طلبات/ساعة)
    expires_at = models.DateTimeField(null=True, blank=True)           # تاريخ الانتهاء
    last_used = models.DateTimeField(null=True, blank=True)            # آخر استخدام
    created_at = models.DateTimeField(auto_now_add=True)               # تاريخ الإنشاء
```

### GeminiConversation (محادثة Gemini)
```python
class GeminiConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)           # المستخدم
    title = models.CharField(max_length=200)                           # عنوان المحادثة
    context = models.TextField(blank=True)                             # السياق
    is_active = models.BooleanField(default=True)                      # نشط
    created_at = models.DateTimeField(auto_now_add=True)               # تاريخ الإنشاء
    updated_at = models.DateTimeField(auto_now=True)                   # تاريخ التحديث
```

### GeminiMessage (رسالة Gemini)
```python
class GeminiMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'مستخدم'),
        ('assistant', 'مساعد'),
        ('system', 'نظام'),
    ]

    conversation = models.ForeignKey(GeminiConversation, related_name='messages') # المحادثة
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)       # الدور
    content = models.TextField()                                       # المحتوى
    timestamp = models.DateTimeField(auto_now_add=True)                # الوقت
    tokens_used = models.IntegerField(default=0)                       # الرموز المستخدمة
    response_time = models.FloatField(null=True, blank=True)           # وقت الاستجابة
```

### APIUsageLog (سجل استخدام API)
```python
class APIUsageLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)        # معرف فريد
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # المستخدم
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True) # مفتاح API
    endpoint = models.CharField(max_length=200)                        # نقطة النهاية
    method = models.CharField(max_length=10)                           # طريقة HTTP
    status_code = models.IntegerField()                                # رمز الاستجابة
    response_time = models.FloatField()                                # وقت الاستجابة (ثواني)
    timestamp = models.DateTimeField(auto_now_add=True)                # الوقت
    ip_address = models.GenericIPAddressField(null=True, blank=True)   # عنوان IP
    user_agent = models.TextField(blank=True)                          # معلومات المتصفح
```

### AIProvider (مقدم خدمة الذكاء الاصطناعي)
```python
class AIProvider(models.Model):
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI GPT'),
        ('claude', 'Anthropic Claude'),
        ('huggingface', 'Hugging Face'),
        ('ollama', 'Ollama (Local)'),
        ('custom', 'مخصص'),
    ]

    name = models.CharField(max_length=100)                            # اسم المقدم
    provider_type = models.CharField(max_length=20, choices=PROVIDER_CHOICES) # نوع المقدم
    api_endpoint = models.URLField()                                   # نقطة النهاية
    is_active = models.BooleanField(default=True)                      # نشط
    max_tokens = models.IntegerField(default=1000)                     # الحد الأقصى للرموز
    temperature = models.FloatField(default=0.7)                       # درجة الإبداع
    description = models.TextField(blank=True)                         # الوصف
```

### AIConfiguration (إعدادات الذكاء الاصطناعي)
```python
class AIConfiguration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_configurations') # المستخدم
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE) # مقدم الخدمة
    api_key = models.CharField(max_length=500)                         # مفتاح API
    model_name = models.CharField(max_length=200, default='gemini-1.5-flash') # اسم النموذج
    is_default = models.BooleanField(default=False)                    # الإعداد الافتراضي
    is_active = models.BooleanField(default=True)                      # نشط
    max_tokens = models.IntegerField(default=1000)                     # الحد الأقصى للرموز
    temperature = models.FloatField(default=0.7)                       # درجة الإبداع
    created_at = models.DateTimeField(auto_now_add=True)               # تاريخ الإنشاء
```

## التثبيت والإعداد (Installation & Setup)

### 1. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 2. إعداد متغيرات البيئة
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

### 4. إنشاء مفتاح API
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
