# نظام الدولية (ElDawliya System)

## نظرة عامة
نظام الدولية هو منصة متكاملة لإدارة العمليات الداخلية للمؤسسة، يتضمن مجموعة من الوحدات المترابطة لتغطية مختلف احتياجات الإدارة والتشغيل.

## الوحدات الرئيسية

### 1. نظام الموارد البشرية (HR)
- إدارة بيانات الموظفين
- إدارة الإجازات والغياب
- متابعة العقود والوثائق
- إدارة الرواتب والمستحقات

### 2. نظام مهام الموظفين (Employee Tasks)
- إنشاء وتعديل وحذف المهام الشخصية
- تصنيف المهام حسب الأولوية والحالة
- تتبع نسبة إنجاز المهام
- إضافة خطوات تفصيلية لكل مهمة
- عرض المهام في تقويم وتحليلات أداء

### 3. نظام الاجتماعات (Meetings)
- جدولة وإدارة الاجتماعات
- دعوة المشاركين ومتابعة الحضور
- توثيق محاضر الاجتماعات
- متابعة القرارات والتوصيات

### 4. نظام المخزون (Inventory)
- إدارة المنتجات والأصناف
- متابعة حركة المخزون
- إنشاء طلبات الشراء التلقائية
- تنبيهات الحد الأدنى للمخزون

### 5. نظام المشتريات (Purchase Orders)
- إدارة طلبات الشراء
- متابعة حالة الطلبات
- إدارة الموافقات والمراجعات
- ربط الطلبات بالمخزون

### 6. نظام API والذكاء الاصطناعي (API & AI)
- **REST API شامل** لجميع وظائف النظام
- **دمج Google Gemini AI** للمحادثات الذكية وتحليل البيانات
- **مصادقة متعددة**: API Keys, JWT Tokens, Session Auth
- **وثائق تفاعلية** مع Swagger UI و ReDoc
- **تحليل البيانات بالذكاء الاصطناعي** واستخراج الرؤى
- **نظام صلاحيات متقدم** حسب المجموعات
- **مراقبة الاستخدام** وإحصائيات الأداء

## الأنظمة المساندة

### 1. نظام الأذونات (Permissions)
- نظام أذونات هرمي (قسم > وحدة > صلاحية)
- نظام RBAC للأدوار والصلاحيات
- تحكم دقيق بصلاحيات المستخدمين

### 2. نظام التنبيهات (Notifications)
- تنبيهات مخصصة لكل وحدة
- مستويات أولوية متعددة
- إشعارات فورية للمستخدمين

### 3. نظام تسجيل الأحداث (Audit)
- تسجيل تلقائي للأحداث
- تتبع عمليات المستخدمين
- سجلات تفصيلية للتغييرات

## المتطلبات التقنية
- Python 3.7+
- Django 3.2+
- قاعدة بيانات SQL Server أو SQLite
- JavaScript (jQuery, FullCalendar.js, Chart.js)
- Bootstrap 5

## التثبيت والإعداد
1. استنساخ المستودع:
```
git clone https://github.com/your-organization/ElDawliya_Sys.git
```

2. تثبيت المتطلبات:
```
pip install -r requirements.txt
```

3. إعداد قاعدة البيانات:
```
python manage.py migrate
```

4. إنشاء مستخدم مشرف:
```
python manage.py createsuperuser
```

5. إعداد API والذكاء الاصطناعي (تلقائي):
```
python setup_api.py
```

6. تشغيل الخادم مع API:
```
python run_api_server.py
```

## استخدام API

### الوصول للوثائق التفاعلية
- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/
- **حالة API**: http://localhost:8000/api/v1/status/

### المصادقة
```bash
# باستخدام API Key
curl -H "Authorization: ApiKey YOUR_API_KEY" http://localhost:8000/api/v1/employees/

# باستخدام JWT Token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/v1/products/
```

### أمثلة الاستخدام

#### محادثة مع الذكاء الاصطناعي
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "ما هو عدد الموظفين في النظام؟"}'
```

#### تحليل بيانات الموظفين
```bash
curl -X POST http://localhost:8000/api/v1/ai/analyze/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"data_type": "employees", "analysis_type": "summary"}'
```

#### البحث في المنتجات
```bash
curl "http://localhost:8000/api/v1/products/?search=كمبيوتر&low_stock=true" \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

### إدارة API

#### إنشاء مفتاح API
```bash
python manage.py create_api_key username --name "My API Key" --expires-days 30
```

#### إعداد مجموعات المستخدمين
```bash
python manage.py setup_api_groups
```

#### تشغيل اختبارات API
```bash
python manage.py test api
```

### أمثلة متقدمة
```bash
# تشغيل أمثلة شاملة للـ API
python api_examples.py
```

## الوثائق والمراجع

### 📚 دلائل مفصلة
- **[دليل API الكامل](api/README.md)** - شرح شامل لجميع endpoints والميزات
- **[إعداد قاعدة البيانات](README_DB_SETUP.md)** - دليل إعداد قاعدة البيانات
- **[الأمان والحماية](SECURITY.md)** - إرشادات الأمان

### 🔧 أدوات التطوير
- **[أمثلة API](api_examples.py)** - أمثلة عملية لاستخدام API
- **[إعداد تلقائي](setup_api.py)** - سكريبت إعداد API تلقائياً
- **[تشغيل الخادم](run_api_server.py)** - تشغيل خادم محسن للـ API

### 🤖 ميزات الذكاء الاصطناعي
- **محادثات ذكية**: استخدام Gemini AI للإجابة على الاستفسارات
- **تحليل البيانات**: تحليل ذكي لبيانات النظام واستخراج الرؤى
- **التوصيات**: توصيات ذكية لتحسين الأداء
- **المساعد الافتراضي**: مساعد ذكي لإدارة النظام

### 📊 نقاط النهاية الرئيسية
- `GET /api/v1/status/` - حالة النظام
- `GET /api/v1/employees/` - بيانات الموظفين
- `GET /api/v1/products/` - بيانات المنتجات
- `GET /api/v1/tasks/` - المهام
- `GET /api/v1/meetings/` - الاجتماعات
- `POST /api/v1/ai/chat/` - محادثة مع AI
- `POST /api/v1/ai/analyze/` - تحليل البيانات

## المساهمة في التطوير
- استخدم Git للتحكم في الإصدارات
- اتبع معايير كتابة الكود المعتمدة
- قم بإنشاء فرع جديد لكل ميزة أو إصلاح
- أرسل طلب سحب (Pull Request) للمراجعة قبل الدمج

## الترخيص
جميع الحقوق محفوظة © نظام الدولية
