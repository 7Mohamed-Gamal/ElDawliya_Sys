# توثيق واجهات برمجة التطبيقات (API)

## نظرة عامة

يوفر نظام الدولية واجهات برمجة تطبيقات شاملة تدعم جميع العمليات الأساسية للنظام. تم تصميم هذه الواجهات لتكون آمنة وسهلة الاستخدام ومتوافقة مع معايير REST.

## 🔐 المصادقة والأمان

### أنواع المصادقة المدعومة

#### 1. JWT Token Authentication
```http
Authorization: Bearer <jwt_token>
```

#### 2. API Key Authentication
```http
X-API-Key: <api_key>
```

#### 3. Session Authentication
للاستخدام من خلال واجهة الويب

### الحصول على JWT Token

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**الاستجابة:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "أحمد",
        "last_name": "محمد"
    }
}
```

### تجديد JWT Token

```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 📊 هيكل الاستجابة المعياري

### الاستجابة الناجحة
```json
{
    "success": true,
    "data": {
        // البيانات المطلوبة
    },
    "message": "تم تنفيذ العملية بنجاح",
    "pagination": {
        "count": 100,
        "next": "http://api.example.com/api/v1/employees/?page=2",
        "previous": null,
        "page_size": 20
    }
}
```

### الاستجابة عند الخطأ
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "البيانات المدخلة غير صحيحة",
        "details": {
            "email": ["هذا الحقل مطلوب"],
            "phone": ["رقم الهاتف غير صحيح"]
        }
    }
}
```

## 🏢 واجهات الموارد البشرية

### الموظفين (Employees)

#### قائمة الموظفين
```http
GET /api/v1/hr/employees/
```

**المعاملات الاختيارية:**
- `department`: فلترة حسب القسم
- `job_position`: فلترة حسب المنصب
- `is_active`: فلترة حسب الحالة
- `search`: البحث في الاسم أو البريد الإلكتروني
- `ordering`: ترتيب النتائج (`created_at`, `-created_at`, `first_name`)

**مثال:**
```http
GET /api/v1/hr/employees/?department=1&is_active=true&search=أحمد
```

#### تفاصيل موظف
```http
GET /api/v1/hr/employees/{id}/
```

#### إضافة موظف جديد
```http
POST /api/v1/hr/employees/
Content-Type: application/json

{
    "emp_code": "EMP001",
    "first_name": "أحمد",
    "last_name": "محمد",
    "email": "ahmed@company.com",
    "phone": "01234567890",
    "department": 1,
    "job_position": 1,
    "hire_date": "2024-01-01",
    "salary": {
        "basic_salary": 5000.00,
        "allowances": 1000.00
    }
}
```

#### تحديث بيانات موظف
```http
PUT /api/v1/hr/employees/{id}/
PATCH /api/v1/hr/employees/{id}/
```

#### حذف موظف
```http
DELETE /api/v1/hr/employees/{id}/
```

### الحضور والانصراف (Attendance)

#### تسجيل الحضور
```http
POST /api/v1/hr/attendance/
Content-Type: application/json

{
    "employee": 1,
    "check_in": "2024-01-01T08:00:00Z",
    "check_out": "2024-01-01T17:00:00Z",
    "notes": "يوم عمل عادي"
}
```

#### قائمة سجلات الحضور
```http
GET /api/v1/hr/attendance/?employee=1&date_from=2024-01-01&date_to=2024-01-31
```

#### تقرير الحضور الشهري
```http
GET /api/v1/hr/attendance/monthly_report/?employee=1&month=2024-01
```

### الإجازات (Leaves)

#### طلب إجازة جديد
```http
POST /api/v1/hr/leaves/
Content-Type: application/json

{
    "employee": 1,
    "leave_type": "annual",
    "start_date": "2024-02-01",
    "end_date": "2024-02-05",
    "reason": "إجازة سنوية",
    "emergency_contact": "01234567890"
}
```

#### الموافقة على طلب إجازة
```http
POST /api/v1/hr/leaves/{id}/approve/
Content-Type: application/json

{
    "approved_by_notes": "تمت الموافقة"
}
```

## 📦 واجهات المخزون

### المنتجات (Products)

#### قائمة المنتجات
```http
GET /api/v1/inventory/products/
```

**المعاملات:**
- `category`: فلترة حسب الفئة
- `supplier`: فلترة حسب المورد
- `low_stock`: المنتجات منخفضة المخزون
- `search`: البحث في اسم المنتج أو الكود

#### إضافة منتج جديد
```http
POST /api/v1/inventory/products/
Content-Type: application/json

{
    "product_code": "PRD001",
    "product_name": "لابتوب ديل",
    "category": 1,
    "unit_price": 15000.00,
    "min_stock_level": 5,
    "max_stock_level": 50,
    "supplier": 1,
    "description": "لابتوب للاستخدام المكتبي"
}
```

### حركات المخزون (Stock Movements)

#### تسجيل حركة مخزون
```http
POST /api/v1/inventory/movements/
Content-Type: application/json

{
    "product": 1,
    "movement_type": "in",
    "quantity": 10,
    "unit_price": 15000.00,
    "reference_number": "PO-2024-001",
    "notes": "استلام من المورد"
}
```

#### تقرير حركات المخزون
```http
GET /api/v1/inventory/movements/report/?product=1&date_from=2024-01-01&date_to=2024-01-31
```

## 🎯 واجهات المشاريع

### المشاريع (Projects)

#### إنشاء مشروع جديد
```http
POST /api/v1/projects/projects/
Content-Type: application/json

{
    "name": "تطوير موقع الشركة",
    "description": "تطوير موقع إلكتروني جديد للشركة",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "project_manager": 1,
    "budget": 100000.00,
    "priority": "high"
}
```

### المهام (Tasks)

#### إضافة مهمة جديدة
```http
POST /api/v1/projects/tasks/
Content-Type: application/json

{
    "title": "تصميم واجهة المستخدم",
    "description": "تصميم واجهة المستخدم الرئيسية",
    "project": 1,
    "assigned_to": 2,
    "due_date": "2024-02-15",
    "priority": "high",
    "estimated_hours": 40
}
```

#### تحديث حالة المهمة
```http
PATCH /api/v1/projects/tasks/{id}/
Content-Type: application/json

{
    "status": "in_progress",
    "progress_percentage": 25,
    "notes": "تم البدء في التصميم"
}
```

## 🛒 واجهات المشتريات

### أوامر الشراء (Purchase Orders)

#### إنشاء أمر شراء
```http
POST /api/v1/procurement/purchase-orders/
Content-Type: application/json

{
    "po_number": "PO-2024-001",
    "supplier": 1,
    "order_date": "2024-01-01",
    "delivery_date": "2024-01-15",
    "items": [
        {
            "product": 1,
            "quantity": 10,
            "unit_price": 15000.00,
            "total_price": 150000.00
        }
    ],
    "notes": "طلب عاجل"
}
```

## 📈 واجهات التقارير

### تقارير الموارد البشرية

#### تقرير ملخص الموظفين
```http
GET /api/v1/reports/hr/employee-summary/
```

#### تقرير الحضور الشهري
```http
GET /api/v1/reports/hr/attendance-monthly/?month=2024-01
```

### تقارير المخزون

#### تقرير مستويات المخزون
```http
GET /api/v1/reports/inventory/stock-levels/
```

#### تقرير حركات المخزون
```http
GET /api/v1/reports/inventory/movements/?date_from=2024-01-01&date_to=2024-01-31
```

## 🔍 البحث والفلترة

### البحث العام
```http
GET /api/v1/search/?q=أحمد&type=employee
```

### الفلترة المتقدمة
```http
GET /api/v1/hr/employees/?department__name=المبيعات&job_position__level=senior&is_active=true
```

## 📄 التصدير والاستيراد

### تصدير البيانات
```http
GET /api/v1/hr/employees/export/?format=excel
GET /api/v1/hr/employees/export/?format=pdf
```

### استيراد البيانات
```http
POST /api/v1/hr/employees/import/
Content-Type: multipart/form-data

file: [Excel file]
```

## ⚠️ معالجة الأخطاء

### رموز الأخطاء الشائعة

| الرمز | الوصف |
|-------|--------|
| 400 | طلب غير صحيح |
| 401 | غير مصرح |
| 403 | ممنوع |
| 404 | غير موجود |
| 422 | خطأ في التحقق |
| 429 | تجاوز الحد المسموح |
| 500 | خطأ في الخادم |

### أمثلة على الأخطاء

```json
{
    "success": false,
    "error": {
        "code": "PERMISSION_DENIED",
        "message": "ليس لديك صلاحية للوصول لهذا المورد",
        "details": {
            "required_permission": "hr.view_employee",
            "user_permissions": ["hr.view_own_data"]
        }
    }
}
```

## 🚀 أمثلة عملية

### مثال شامل: إدارة موظف جديد

```javascript
// 1. تسجيل الدخول
const loginResponse = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'password123'
    })
});

const { access } = await loginResponse.json();

// 2. إضافة موظف جديد
const employeeResponse = await fetch('/api/v1/hr/employees/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${access}`
    },
    body: JSON.stringify({
        emp_code: 'EMP001',
        first_name: 'أحمد',
        last_name: 'محمد',
        email: 'ahmed@company.com',
        department: 1,
        job_position: 1,
        hire_date: '2024-01-01'
    })
});

const employee = await employeeResponse.json();

// 3. تسجيل حضور الموظف
const attendanceResponse = await fetch('/api/v1/hr/attendance/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${access}`
    },
    body: JSON.stringify({
        employee: employee.data.id,
        check_in: new Date().toISOString()
    })
});
```

## 📚 مراجع إضافية

- [دليل المطور](../developer_guide/README.md)
- [أمثلة التكامل](examples/)
- [SDK للغات المختلفة](sdk/)
- [Postman Collection](postman/)

---

**ملاحظة**: هذا التوثيق يتم تحديثه باستمرار. تأكد من مراجعة آخر إصدار.