# أمثلة عملية لاستخدام API - نظام الدولية

## 🚀 البدء السريع

### الحصول على رمز الوصول

```bash
# طلب رمز الوصول
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

**الاستجابة:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@company.com",
    "first_name": "مدير",
    "last_name": "النظام"
  }
}
```

### استخدام رمز الوصول

```bash
# استخدام الرمز في الطلبات
curl -X GET http://localhost:8000/api/v1/hr/employees/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## 👥 أمثلة الموارد البشرية

### إدارة الموظفين

#### قائمة الموظفين مع الفلترة
```bash
# جميع الموظفين
curl -X GET "http://localhost:8000/api/v1/hr/employees/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# البحث بالاسم
curl -X GET "http://localhost:8000/api/v1/hr/employees/?search=أحمد" \
  -H "Authorization: Bearer YOUR_TOKEN"

# فلترة حسب القسم
curl -X GET "http://localhost:8000/api/v1/hr/employees/?department=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# الموظفين النشطين فقط
curl -X GET "http://localhost:8000/api/v1/hr/employees/?is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### إضافة موظف جديد
```bash
curl -X POST http://localhost:8000/api/v1/hr/employees/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "emp_code": "EMP001",
    "first_name": "أحمد",
    "last_name": "محمد",
    "email": "ahmed@company.com",
    "phone": "01234567890",
    "department": 1,
    "job_position": 1,
    "hire_date": "2024-01-01"
  }'
```

#### تحديث بيانات موظف
```bash
# تحديث كامل (PUT)
curl -X PUT http://localhost:8000/api/v1/hr/employees/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "emp_code": "EMP001",
    "first_name": "أحمد",
    "last_name": "محمد علي",
    "email": "ahmed.ali@company.com",
    "phone": "01234567890",
    "department": 1,
    "job_position": 2,
    "hire_date": "2024-01-01"
  }'

# تحديث جزئي (PATCH)
curl -X PATCH http://localhost:8000/api/v1/hr/employees/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "01234567891",
    "job_position": 2
  }'
```

### إدارة الحضور والانصراف

#### تسجيل حضور
```bash
curl -X POST http://localhost:8000/api/v1/hr/attendance/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": 1,
    "check_in": "2024-01-01T08:00:00Z",
    "notes": "وصول في الموعد"
  }'
```

#### تسجيل انصراف
```bash
curl -X PATCH http://localhost:8000/api/v1/hr/attendance/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "check_out": "2024-01-01T17:00:00Z",
    "notes": "انصراف عادي"
  }'
```

#### تقرير الحضور الشهري
```bash
curl -X GET "http://localhost:8000/api/v1/hr/attendance/monthly_report/?employee=1&month=2024-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### إدارة الإجازات

#### طلب إجازة جديد
```bash
curl -X POST http://localhost:8000/api/v1/hr/leaves/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": 1,
    "leave_type": "annual",
    "start_date": "2024-02-01",
    "end_date": "2024-02-05",
    "reason": "إجازة سنوية",
    "emergency_contact": "01234567890"
  }'
```

#### الموافقة على طلب إجازة
```bash
curl -X POST http://localhost:8000/api/v1/hr/leaves/1/approve/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approved_by_notes": "تمت الموافقة على الطلب"
  }'
```

## 📦 أمثلة المخزون

### إدارة المنتجات

#### قائمة المنتجات
```bash
# جميع المنتجات
curl -X GET http://localhost:8000/api/v1/inventory/products/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# المنتجات منخفضة المخزون
curl -X GET "http://localhost:8000/api/v1/inventory/products/?low_stock=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# البحث في المنتجات
curl -X GET "http://localhost:8000/api/v1/inventory/products/?search=لابتوب" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### إضافة منتج جديد
```bash
curl -X POST http://localhost:8000/api/v1/inventory/products/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "PRD001",
    "product_name": "لابتوب ديل",
    "category": 1,
    "unit_price": 15000.00,
    "min_stock_level": 5,
    "max_stock_level": 50,
    "supplier": 1,
    "description": "لابتوب للاستخدام المكتبي"
  }'
```

### حركات المخزون

#### تسجيل حركة وارد
```bash
curl -X POST http://localhost:8000/api/v1/inventory/movements/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "movement_type": "in",
    "quantity": 10,
    "unit_price": 15000.00,
    "reference_number": "PO-2024-001",
    "notes": "استلام من المورد الرئيسي"
  }'
```

#### تسجيل حركة صادر
```bash
curl -X POST http://localhost:8000/api/v1/inventory/movements/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "movement_type": "out",
    "quantity": 2,
    "reference_number": "REQ-2024-001",
    "notes": "صرف لقسم تقنية المعلومات"
  }'
```

## 🎯 أمثلة المشاريع

### إدارة المشاريع

#### إنشاء مشروع جديد
```bash
curl -X POST http://localhost:8000/api/v1/projects/projects/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "تطوير موقع الشركة",
    "description": "تطوير موقع إلكتروني جديد للشركة",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "project_manager": 1,
    "budget": 100000.00,
    "priority": "high"
  }'
```

#### قائمة المشاريع النشطة
```bash
curl -X GET "http://localhost:8000/api/v1/projects/projects/?status=active" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### إدارة المهام

#### إضافة مهمة جديدة
```bash
curl -X POST http://localhost:8000/api/v1/projects/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "تصميم واجهة المستخدم",
    "description": "تصميم واجهة المستخدم الرئيسية للموقع",
    "project": 1,
    "assigned_to": 2,
    "due_date": "2024-02-15",
    "priority": "high",
    "estimated_hours": 40
  }'
```

#### تحديث حالة المهمة
```bash
curl -X PATCH http://localhost:8000/api/v1/projects/tasks/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "progress_percentage": 25,
    "notes": "تم البدء في التصميم الأولي"
  }'
```

## 🛒 أمثلة المشتريات

### أوامر الشراء

#### إنشاء أمر شراء
```bash
curl -X POST http://localhost:8000/api/v1/procurement/purchase-orders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
      },
      {
        "product": 2,
        "quantity": 5,
        "unit_price": 2000.00,
        "total_price": 10000.00
      }
    ],
    "notes": "طلب عاجل للمعدات الجديدة"
  }'
```

#### تحديث حالة أمر الشراء
```bash
curl -X PATCH http://localhost:8000/api/v1/procurement/purchase-orders/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "approved_by_notes": "تمت الموافقة على الطلب"
  }'
```

## 📊 أمثلة التقارير

### تقارير الموارد البشرية

#### تقرير ملخص الموظفين
```bash
curl -X GET http://localhost:8000/api/v1/reports/hr/employee-summary/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### تقرير الحضور الشهري
```bash
curl -X GET "http://localhost:8000/api/v1/reports/hr/attendance-monthly/?month=2024-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### تقارير المخزون

#### تقرير مستويات المخزون
```bash
curl -X GET http://localhost:8000/api/v1/reports/inventory/stock-levels/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### تقرير حركات المخزون
```bash
curl -X GET "http://localhost:8000/api/v1/reports/inventory/movements/?date_from=2024-01-01&date_to=2024-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔍 أمثلة البحث والفلترة

### البحث المتقدم
```bash
# البحث في الموظفين بمعايير متعددة
curl -X GET "http://localhost:8000/api/v1/hr/employees/?search=أحمد&department=1&is_active=true&ordering=hire_date" \
  -H "Authorization: Bearer YOUR_TOKEN"

# البحث في المنتجات بالفئة والمورد
curl -X GET "http://localhost:8000/api/v1/inventory/products/?category=1&supplier=1&min_price=1000&max_price=20000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### التصفح بالصفحات
```bash
# الصفحة الأولى (20 عنصر)
curl -X GET "http://localhost:8000/api/v1/hr/employees/?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# الصفحة الثانية
curl -X GET "http://localhost:8000/api/v1/hr/employees/?page=2&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📄 تصدير البيانات

### تصدير إلى Excel
```bash
curl -X GET "http://localhost:8000/api/v1/hr/employees/export/?format=excel" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o employees.xlsx
```

### تصدير إلى PDF
```bash
curl -X GET "http://localhost:8000/api/v1/hr/employees/export/?format=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o employees.pdf
```

### تصدير إلى CSV
```bash
curl -X GET "http://localhost:8000/api/v1/hr/employees/export/?format=csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o employees.csv
```

## 📤 استيراد البيانات

### استيراد موظفين من Excel
```bash
curl -X POST http://localhost:8000/api/v1/hr/employees/import/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@employees.xlsx" \
  -F "format=excel"
```

## 🔄 العمليات المجمعة

### تحديث مجموعة من الموظفين
```bash
curl -X POST http://localhost:8000/api/v1/hr/employees/bulk_update/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_ids": [1, 2, 3, 4, 5],
    "update_data": {
      "department": 2,
      "is_active": true
    }
  }'
```

### حذف مجموعة من السجلات
```bash
curl -X POST http://localhost:8000/api/v1/hr/employees/bulk_delete/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_ids": [10, 11, 12]
  }'
```

## 🧪 اختبار API

### سكريبت Python للاختبار
```python
import requests
import json

# إعدادات الاتصال
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "your_password"

# تسجيل الدخول والحصول على الرمز
def get_access_token():
    response = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        return response.json()["access"]
    else:
        raise Exception("فشل في تسجيل الدخول")

# اختبار قائمة الموظفين
def test_employees_list(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hr/employees/", headers=headers)
    
    print(f"حالة الاستجابة: {response.status_code}")
    print(f"عدد الموظفين: {response.json()['count']}")

# اختبار إضافة موظف
def test_create_employee(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    employee_data = {
        "emp_code": "TEST001",
        "first_name": "موظف",
        "last_name": "تجريبي",
        "email": "test@company.com",
        "phone": "01234567890",
        "department": 1,
        "job_position": 1,
        "hire_date": "2024-01-01"
    }
    
    response = requests.post(
        f"{BASE_URL}/hr/employees/", 
        headers=headers, 
        json=employee_data
    )
    
    if response.status_code == 201:
        print("تم إنشاء الموظف بنجاح")
        return response.json()["id"]
    else:
        print(f"فشل في إنشاء الموظف: {response.text}")
        return None

# تشغيل الاختبارات
if __name__ == "__main__":
    try:
        token = get_access_token()
        print("تم الحصول على رمز الوصول بنجاح")
        
        test_employees_list(token)
        employee_id = test_create_employee(token)
        
        if employee_id:
            print(f"تم إنشاء الموظف برقم: {employee_id}")
            
    except Exception as e:
        print(f"خطأ: {e}")
```

## 📱 استخدام API من JavaScript

### مثال React/JavaScript
```javascript
// خدمة API
class ElDawliyaAPI {
    constructor(baseURL = 'http://localhost:8000/api/v1') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('access_token');
    }
    
    // تسجيل الدخول
    async login(username, password) {
        const response = await fetch(`${this.baseURL}/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            this.token = data.access;
            localStorage.setItem('access_token', this.token);
            return data;
        } else {
            throw new Error('فشل في تسجيل الدخول');
        }
    }
    
    // الحصول على قائمة الموظفين
    async getEmployees(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = `${this.baseURL}/hr/employees/${queryString ? '?' + queryString : ''}`;
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
            }
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error('فشل في جلب بيانات الموظفين');
        }
    }
    
    // إضافة موظف جديد
    async createEmployee(employeeData) {
        const response = await fetch(`${this.baseURL}/hr/employees/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(employeeData)
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.message || 'فشل في إضافة الموظف');
        }
    }
}

// استخدام الخدمة
const api = new ElDawliyaAPI();

// مثال على الاستخدام
async function loadEmployees() {
    try {
        const employees = await api.getEmployees({ 
            search: 'أحمد', 
            department: 1 
        });
        console.log('الموظفين:', employees.results);
    } catch (error) {
        console.error('خطأ:', error.message);
    }
}
```

---

**هذه الأمثلة تغطي معظم حالات الاستخدام الشائعة. للمزيد من التفاصيل، راجع [التوثيق الكامل للـ API](README.md).**