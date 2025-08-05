# توثيق API - نظام الموارد البشرية الشامل

## مقدمة

يوفر نظام الموارد البشرية الشامل واجهة برمجة تطبيقات (API) قوية ومرنة تتيح للمطورين التكامل مع النظام بسهولة. تستخدم الواجهة معايير REST وتدعم تنسيقات JSON للبيانات.

## المصادقة

### Token Authentication

يستخدم النظام مصادقة Token للوصول إلى API:

```http
Authorization: Token your-api-token-here
```

### الحصول على Token

```http
POST /api/auth/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**الاستجابة:**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

## نقاط النهاية الرئيسية

### الموظفون (Employees)

#### قائمة الموظفين

```http
GET /api/v1/employees/
Authorization: Token your-token
```

**المعاملات:**
- `page`: رقم الصفحة (افتراضي: 1)
- `page_size`: عدد العناصر في الصفحة (افتراضي: 20)
- `search`: البحث في الاسم أو رقم الموظف
- `department`: فلترة حسب القسم
- `is_active`: فلترة حسب الحالة (true/false)

**مثال على الاستجابة:**
```json
{
    "count": 150,
    "next": "http://api.example.com/api/v1/employees/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "employee_id": "EMP001",
            "first_name": "أحمد",
            "last_name": "محمد",
            "first_name_en": "Ahmed",
            "last_name_en": "Mohammed",
            "email": "ahmed@company.com",
            "phone_number": "0501234567",
            "department": {
                "id": 1,
                "name": "قسم الموارد البشرية",
                "code": "HR001"
            },
            "job_position": {
                "id": 1,
                "name": "مدير الموارد البشرية",
                "level": "manager"
            },
            "hire_date": "2024-01-01",
            "basic_salary": "15000.00",
            "is_active": true,
            "created_at": "2024-01-01T08:00:00Z"
        }
    ]
}
```

#### تفاصيل الموظف

```http
GET /api/v1/employees/{id}/
Authorization: Token your-token
```

#### إنشاء موظف جديد

```http
POST /api/v1/employees/
Authorization: Token your-token
Content-Type: application/json

{
    "employee_id": "EMP002",
    "first_name": "فاطمة",
    "last_name": "علي",
    "first_name_en": "Fatima",
    "last_name_en": "Ali",
    "national_id": "1234567890",
    "phone_number": "0501234568",
    "email": "fatima@company.com",
    "department": 1,
    "job_position": 2,
    "company": 1,
    "hire_date": "2024-01-15",
    "basic_salary": "8000.00",
    "gender": "female",
    "marital_status": "single"
}
```

#### تحديث بيانات الموظف

```http
PUT /api/v1/employees/{id}/
Authorization: Token your-token
Content-Type: application/json

{
    "first_name": "فاطمة المحدثة",
    "basic_salary": "9000.00"
}
```

#### حذف الموظف

```http
DELETE /api/v1/employees/{id}/
Authorization: Token your-token
```

### الأقسام (Departments)

#### قائمة الأقسام

```http
GET /api/v1/departments/
Authorization: Token your-token
```

**مثال على الاستجابة:**
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "name": "قسم الموارد البشرية",
            "name_en": "Human Resources Department",
            "code": "HR001",
            "company": {
                "id": 1,
                "name": "شركة الدولية"
            },
            "head_of_department": "سارة أحمد",
            "employee_count": 15,
            "is_active": true
        }
    ]
}
```

#### إنشاء قسم جديد

```http
POST /api/v1/departments/
Authorization: Token your-token
Content-Type: application/json

{
    "name": "قسم التسويق",
    "name_en": "Marketing Department",
    "code": "MKT001",
    "company": 1,
    "description": "قسم التسويق والإعلان",
    "head_of_department": "خالد أحمد",
    "budget": "500000.00"
}
```

### المناصب الوظيفية (Job Positions)

#### قائمة المناصب

```http
GET /api/v1/job-positions/
Authorization: Token your-token
```

#### إنشاء منصب جديد

```http
POST /api/v1/job-positions/
Authorization: Token your-token
Content-Type: application/json

{
    "name": "مطور برمجيات",
    "name_en": "Software Developer",
    "code": "DEV001",
    "department": 2,
    "level": "senior",
    "min_salary": "8000.00",
    "max_salary": "12000.00",
    "description": "تطوير التطبيقات البرمجية",
    "requirements": "بكالوريوس في علوم الحاسب، خبرة 3 سنوات"
}
```

### الحضور (Attendance)

#### تسجيل الحضور

```http
POST /api/v1/attendance/check-in/
Authorization: Token your-token
Content-Type: application/json

{
    "employee_id": "EMP001",
    "timestamp": "2024-01-15T08:00:00Z",
    "location": {
        "latitude": 24.7136,
        "longitude": 46.6753
    }
}
```

#### تسجيل الانصراف

```http
POST /api/v1/attendance/check-out/
Authorization: Token your-token
Content-Type: application/json

{
    "employee_id": "EMP001",
    "timestamp": "2024-01-15T17:00:00Z"
}
```

#### سجلات الحضور

```http
GET /api/v1/attendance/records/
Authorization: Token your-token
```

**المعاملات:**
- `employee`: معرف الموظف
- `date_from`: تاريخ البداية (YYYY-MM-DD)
- `date_to`: تاريخ النهاية (YYYY-MM-DD)
- `status`: حالة الحضور (present, absent, late)

### الرواتب (Payroll)

#### حساب الراتب

```http
POST /api/v1/payroll/calculate/
Authorization: Token your-token
Content-Type: application/json

{
    "employee_id": "EMP001",
    "month": 1,
    "year": 2024,
    "allowances": [
        {
            "type": "housing",
            "amount": "2000.00"
        }
    ],
    "deductions": [
        {
            "type": "insurance",
            "amount": "500.00"
        }
    ]
}
```

#### سجلات الرواتب

```http
GET /api/v1/payroll/records/
Authorization: Token your-token
```

### التقارير (Reports)

#### إنتاج تقرير

```http
POST /api/v1/reports/generate/
Authorization: Token your-token
Content-Type: application/json

{
    "report_type": "employee_summary",
    "filters": {
        "department": 1,
        "date_from": "2024-01-01",
        "date_to": "2024-01-31"
    },
    "format": "pdf"
}
```

#### قائمة التقارير

```http
GET /api/v1/reports/
Authorization: Token your-token
```

## رموز الحالة

| الرمز | الوصف |
|-------|--------|
| 200 | نجح الطلب |
| 201 | تم الإنشاء بنجاح |
| 400 | خطأ في البيانات المرسلة |
| 401 | غير مصرح بالوصول |
| 403 | ممنوع الوصول |
| 404 | العنصر غير موجود |
| 500 | خطأ في الخادم |

## معالجة الأخطاء

### تنسيق رسائل الخطأ

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "البيانات المرسلة غير صحيحة",
        "details": {
            "email": ["هذا الحقل مطلوب"],
            "phone_number": ["رقم الهاتف غير صحيح"]
        }
    }
}
```

### أنواع الأخطاء الشائعة

- `VALIDATION_ERROR`: خطأ في التحقق من البيانات
- `AUTHENTICATION_ERROR`: خطأ في المصادقة
- `PERMISSION_ERROR`: عدم وجود صلاحيات
- `NOT_FOUND`: العنصر غير موجود
- `DUPLICATE_ERROR`: البيانات مكررة

## التصفية والبحث

### البحث النصي

```http
GET /api/v1/employees/?search=أحمد
```

### التصفية المتقدمة

```http
GET /api/v1/employees/?department=1&is_active=true&hire_date__gte=2024-01-01
```

### الترتيب

```http
GET /api/v1/employees/?ordering=-hire_date,first_name
```

## التصدير

### تصدير البيانات

```http
GET /api/v1/employees/export/?format=csv
Authorization: Token your-token
```

**التنسيقات المدعومة:**
- `csv`: ملف CSV
- `excel`: ملف Excel
- `pdf`: ملف PDF

## الحدود والقيود

- **معدل الطلبات**: 1000 طلب في الساعة لكل مستخدم
- **حجم البيانات**: حد أقصى 10MB لكل طلب
- **التصفح**: حد أقصى 100 عنصر في الصفحة الواحدة

## أمثلة عملية

### مثال بـ Python

```python
import requests

# إعداد المصادقة
headers = {
    'Authorization': 'Token your-api-token',
    'Content-Type': 'application/json'
}

# الحصول على قائمة الموظفين
response = requests.get(
    'http://api.example.com/api/v1/employees/',
    headers=headers
)

employees = response.json()
print(f"عدد الموظفين: {employees['count']}")

# إنشاء موظف جديد
new_employee = {
    'employee_id': 'EMP003',
    'first_name': 'سارة',
    'last_name': 'أحمد',
    'email': 'sara@company.com',
    'department': 1,
    'job_position': 2
}

response = requests.post(
    'http://api.example.com/api/v1/employees/',
    headers=headers,
    json=new_employee
)

if response.status_code == 201:
    print("تم إنشاء الموظف بنجاح")
```

### مثال بـ JavaScript

```javascript
// إعداد المصادقة
const headers = {
    'Authorization': 'Token your-api-token',
    'Content-Type': 'application/json'
};

// الحصول على قائمة الموظفين
fetch('http://api.example.com/api/v1/employees/', {
    headers: headers
})
.then(response => response.json())
.then(data => {
    console.log(`عدد الموظفين: ${data.count}`);
    data.results.forEach(employee => {
        console.log(`${employee.first_name} ${employee.last_name}`);
    });
});

// إنشاء موظف جديد
const newEmployee = {
    employee_id: 'EMP004',
    first_name: 'محمد',
    last_name: 'علي',
    email: 'mohammed@company.com',
    department: 1,
    job_position: 3
};

fetch('http://api.example.com/api/v1/employees/', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(newEmployee)
})
.then(response => {
    if (response.status === 201) {
        console.log('تم إنشاء الموظف بنجاح');
    }
});
```

## الدعم والمساعدة

للحصول على مساعدة إضافية أو الإبلاغ عن مشاكل في API:

- **البريد الإلكتروني**: api-support@eldawliya-hr.com
- **التوثيق التفاعلي**: http://api.example.com/docs/
- **حالة الخدمة**: http://status.example.com/

---

*آخر تحديث: يناير 2024*
*إصدار API: v1.0*