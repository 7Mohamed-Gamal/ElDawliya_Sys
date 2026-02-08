# 📋 ملف المرجع الشامل - نظام الدولية ERP
**تاريخ الإنشاء:** 7 فبراير 2026  
**المسار:** F:\الدولية سيستم\07-02-2026\ElDawliya_Sys

---

## 🎯 نظرة عامة
**نوع المشروع:** نظام ERP متكامل للموارد البشرية والمخزون والمشاريع  
**الإطار:** Django 5.2.9 + Python 3.11  
**قاعدة البيانات:** Microsoft SQL Server  
**الواجهة:** Bootstrap 5 + HTML/CSS/JS

---

## 📁 هيكل المشروع

```
ElDawliya_Sys/
├── ElDawliya_sys/           # إعدادات المشروع
│   ├── settings/             # base, dev, prod, test
│   ├── urls.py              # المسارات الرئيسية
│   ├── wsgi.py, asgi.py     # خوادم التطبيق
│   └── celery.py            # المهام الخلفية
│
├── apps/                     # التطبيقات الرئيسية
│   ├── hr/                   # نظام الموارد البشرية
│   │   ├── employees/        # إدارة الموظفين
│   │   ├── attendance/       # الحضور والانصراف
│   │   ├── leaves/          # الإجازات
│   │   ├── payroll/         # الرواتب
│   │   ├── evaluations/     # التقييمات
│   │   ├── training/        # التدريب
│   │   ├── loans/           # القروض
│   │   ├── insurance/       # التأمينات
│   │   └── disciplinary/    # الإجراءات التأديبية
│   ├── inventory/           # نظام المخزون
│   ├── procurement/         # المشتريات
│   ├── projects/            # إدارة المشاريع
│   ├── finance/             # المالية
│   ├── administration/      # الإدارة العامة
│   ├── reports/             # التقارير
│   ├── rbac/                # الصلاحيات
│   ├── syssettings/         # إعدادات النظام
│   └── workflow/            # سير العمل
│
├── accounts/                # المصادقة والمستخدمين
├── api/v1/                  # واجهات البرمجة REST API
├── org/                     # الهيكل التنظيمي
├── notifications/           # الإشعارات
├── core/                    # وظائف مشتركة
├── frontend/                # الواجهة الأمامية
├── templates/               # قوالب HTML
├── static/                  # CSS, JS, Images
└── tests/                   # الاختبارات
```

---

## 🔧 التقنيات المستخدمة

### Backend
- **Django 5.2.9** - إطار العمل
- **Django REST Framework** - API
- **JWT Authentication** - المصادقة
- **Celery + Redis** - المهام الخلفية
- **Django Channels** - WebSocket
- **mssql-django** - SQL Server

### Frontend
- **Bootstrap 5.3** - إطار التصميم
- **Font Awesome 6** - الأيقونات
- **DataTables** - جداول متقدمة
- **Chart.js** - الرسوم البيانية
- **Select2** - حقول الاختيار

---

## 🗄️ قاعدة البيانات - الجداول الرئيسية

### نظام الموارد البشرية
| الجدول | الوصف | العلاقات |
|--------|-------|----------|
| `Employees` | بيانات الموظفين | Branches, Departments, Jobs |
| `EmployeeDocuments` | المستندات | Employees |
| `EmployeeBankAccounts` | الحسابات البنكية | Employees |
| `EmployeeAttendance` | الحضور والانصراف | Employees, AttendanceRules |
| `AttendanceRules` | قواعد الحضور | - |
| `ZKDevices` | أجهزة البصمة | Branches |
| `ZKAttendanceRaw` | بيانات البصمة الخام | Employees, ZKDevices |
| `EmployeeLeaves` | الإجازات | Employees, LeaveTypes |
| `LeaveTypes` | أنواع الإجازات | - |
| `PublicHolidays` | العطلات الرسمية | - |
| `EmployeeSalaries` | الرواتب | Employees |
| `PayrollRuns` | تشغيلات الرواتب | - |
| `PayrollDetails` | تفاصيل الرواتب | PayrollRuns, Employees |

### نظام المخزون
| الجدول | الوصف |
|--------|-------|
| `Tbl_Products` | المنتجات والأصناف |
| `Tbl_Categories` | الفئات |
| `Tbl_Suppliers` | الموردين |
| `Tbl_Customers` | العملاء |
| `Tbl_Invoices` | الفواتير |
| `Tbl_InvoiceItems` | عناصر الفواتير |
| `Tbl_Units_SpareParts` | وحدات القياس |

### الهيكل التنظيمي
| الجدول | الوصف |
|--------|-------|
| `Branches` | الفروع |
| `Departments` | الأقسام |
| `Jobs` | الوظائف |

---

## 📊 النماذج الرئيسية (Models)

### نموذج الموظف
```python
class Employee:
    - emp_id (PK)
    - emp_code (Unique)
    - first_name, second_name, third_name, last_name
    - gender, birth_date, nationality
    - national_id, passport_no
    - mobile, email, address
    - hire_date, join_date, probation_end
    - job (FK), dept (FK), branch (FK)
    - manager (Self FK)
    - emp_status, termination_date
```

### نموذج الحضور
```python
class EmployeeAttendance:
    - att_id (PK)
    - emp (FK)
    - att_date, check_in, check_out
    - status, rule (FK)
    - Methods: calculate_work_minutes(), calculate_late_minutes()
```

### نموذج الإجازة
```python
class EmployeeLeave:
    - leave_id (PK)
    - emp (FK), leave_type (FK)
    - start_date, end_date, duration_days
    - status, approved_by, approved_date
    - Methods: approve(), reject(), cancel()
```

### نموذج الراتب
```python
class EmployeeSalary:
    - salary_id (PK)
    - emp (FK)
    - basic_salary, housing_allow, transport_allow
    - gosi_deduction, tax_deduction
    - overtime_rate, weekend_rate, holiday_rate
    - Properties: gross_salary, net_salary, total_allowances
```

---

## 🔌 API Endpoints

### المصادقة
```
POST /api/v1/auth/login/          - تسجيل الدخول
POST /api/v1/auth/refresh/        - تحديث التوكن
POST /api/v1/auth/logout/         - تسجيل الخروج
```

### الموارد البشرية
```
GET    /api/v1/hr/employees/            - قائمة الموظفين
POST   /api/v1/hr/employees/            - إضافة موظف
GET    /api/v1/hr/employees/{id}/       - تفاصيل موظف
PUT    /api/v1/hr/employees/{id}/       - تحديث موظف
DELETE /api/v1/hr/employees/{id}/       - حذف موظف

GET    /api/v1/hr/attendance/           - سجلات الحضور
POST   /api/v1/hr/attendance/checkin/   - تسجيل دخول
POST   /api/v1/hr/attendance/checkout/  - تسجيل خروج

GET    /api/v1/hr/leaves/               - الإجازات
POST   /api/v1/hr/leaves/               - طلب إجازة
PUT    /api/v1/hr/leaves/{id}/approve/  - اعتماد إجازة

GET    /api/v1/hr/payroll/              - الرواتب
POST   /api/v1/hr/payroll/calculate/    - حساب الراتب
```

### المخزون
```
GET    /api/v1/inventory/products/      - المنتجات
POST   /api/v1/inventory/products/      - إضافة منتج
GET    /api/v1/inventory/categories/    - الفئات
GET    /api/v1/inventory/vouchers/      # الأذونات
POST   /api/v1/inventory/invoices/      - إنشاء فاتورة
```

---

## 🎨 الواجهة الأمامية

### القوالب الرئيسية
- `templates/base.html` - القالب الأساسي
- `templates/home_dashboard.html` - لوحة التحكم
- `templates/hr/hr_dashboard.html` - HR Dashboard
- `templates/org/departments.html` - الأقسام
- `templates/org/branches.html` - الفروع
- `templates/leaves/dashboard.html` - الإجازات

### الملفات الثابتة
**CSS:**
- `static/css/style.css` - الأنماط الرئيسية
- `static/css/rtl.css` - دعم العربية
- `static/css/style_inventory.css` - أنماط المخزون

**JS:**
- `static/js/main.js` - الوظائف الرئيسية
- `static/js/global-search.js` - البحث العام
- `static/js/theme-toggle.js` - تبديل السمة

---

## 🚨 الملفات غير المستخدمة (للحذف)

### ملفات تحتاج حذف
| الملف/المجلد | السبب |
|-------------|-------|
| `testsprite_tests/` | ملفات اختبار مؤقتة |
| `hr_core/` | تطبيق قديم مكرر |
| `core/migrations/` | ترحيلات قديمة |
| `staticfiles/` | ملفات مجمعة قديمة |
| `db_migration.sqlite3` | قاعدة بيانات مؤقتة |
| `__pycache__/` (في كل مكان) | ملفات مترجمة |
| `*.pyc` | ملفات بايثون مترجمة |
| `.pytest_cache/` | ذاكرة pytest |

---

## ⚙️ ملفات الإعدادات

### .env.example
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=mssql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

### settings/base.py
- الإعدادات الأساسية المشتركة
- التطبيقات المثبتة
- الميدلوير
- قاعدة البيانات
- المصادقة

---

## 🧪 الاختبارات

### أنواع الاختبارات
- `tests/unit/` - اختبارات الوحدة
- `tests/integration/` - اختبارات التكامل
- `tests/security/` - اختبارات الأمان
- `tests/performance/` - اختبارات الأداء

### تشغيل الاختبارات
```bash
python manage.py test
pytest
```

---

## 🐳 Docker

### docker-compose.yml
- **web:** تطبيق Django
- **db:** SQL Server
- **redis:** التخزين المؤقت
- **celery:** المهام الخلفية

### Dockerfile
- Python 3.11 slim
- تثبيت المتطلبات
- جمع الملفات الثابتة

---

## 📝 قائمة المهام - إعادة الهيكلة

### المرحلة 1: التنظيف
- [ ] حذف الملفات غير المستخدمة
- [ ] تنظيف __pycache__
- [ ] تنظيف الترحيلات القديمة
- [ ] إعادة بناء staticfiles

### المرحلة 2: التطوير
- [ ] تحديث Bootstrap إلى 5.3
- [ ] تحديث Font Awesome إلى 6
- [ ] إضافة Tailwind CSS
- [ ] تحسين التصميم العام
- [ ] جعل الواجهة متجاوبة 100%

### المرحلة 3: التحسينات
- [ ] تحسين أداء API
- [ ] إضافة التخزين المؤقت
- [ ] تحسين استعلامات قاعدة البيانات
- [ ] إضافة اختبارات جديدة

### المرحلة 4: الميزات الجديدة
- [ ] لوحة تحكم تفاعلية
- [ ] نظام إشعارات محسن
- [ ] تقارير متقدمة
- [ ] نظام سير عمل

---

## 📚 التوثيق

### ملفات التوثيق الموجودة
- `docs/` - مجلد التوثيق
- `README.md` - ملف القراءة
- `API_DOCUMENTATION.md` - توثيق API

### Swagger
- `/swagger/` - وثائق API تفاعلية
- `/redoc/` - وثائق ReDoc

---

## 👥 المستخدمون والصلاحيات

### نموذج المستخدم
```python
class User:
    - id (PK)
    - username, email
    - first_name, last_name
    - is_active, is_staff, is_superuser
    - groups, user_permissions
```

### المجموعات
- **Admin** - مدير النظام
- **HR Manager** - مدير الموارد البشرية
- **HR Officer** - موظف HR
- **Employee** - موظف
- **Inventory Manager** - مدير المخزون

---

## 🔐 الأمان

### التدابير الأمنية
- JWT Token Authentication
- CSRF Protection
- SQL Injection Protection
- XSS Protection
- Rate Limiting
- Password Hashing (PBKDF2)

---

## 📞 التواصل والدعم

### للأسئلة والاستفسارات
- مراجعة ملفات التوثيق في `docs/`
- التحقق من سجلات الأخطاء في `logs/`

### المسار الكامل
```
F:\الدولية سيستم\07-02-2026\ElDawliya_Sys
```

---

**آخر تحديث:** 7 فبراير 2026  
**الإصدار:** 1.0.0  
**المطور:** نظام الدولية
