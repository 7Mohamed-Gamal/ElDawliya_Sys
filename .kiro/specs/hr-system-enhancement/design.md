# تصميم تحسين نظام الموارد البشرية

## نظرة عامة

هذا التصميم يهدف إلى تحويل نظام الموارد البشرية الحالي إلى نظام عصري وشامل يلبي احتياجات المؤسسات الحديثة مع الحفاظ على الدعم الكامل للغة العربية ونظام RTL.

## الهيكل المعماري

### 1. هيكل النماذج المحسن

#### النماذج الأساسية (Core Models)
```python
# Company Structure
Company -> Branch -> Department -> JobPosition -> Employee

# Supporting Models
WorkShift, AttendanceMachine, LeaveType, SalaryComponent
```

#### العلاقات الرئيسية
- **Company (1:N) Branch**: شركة واحدة لها عدة فروع
- **Branch (1:N) Department**: فرع واحد له عدة أقسام  
- **Department (1:N) JobPosition**: قسم واحد له عدة وظائف
- **JobPosition (1:N) Employee**: وظيفة واحدة لها عدة موظفين
- **Employee (1:N) AttendanceRecord**: موظف واحد له عدة سجلات حضور

### 2. طبقة الخدمات (Services Layer)

#### خدمات الموظفين
```python
class EmployeeService:
    - create_employee()
    - update_employee()
    - calculate_service_years()
    - get_employee_hierarchy()
    - export_employee_data()
```

#### خدمات الحضور
```python
class AttendanceService:
    - record_attendance()
    - calculate_work_hours()
    - generate_attendance_report()
    - sync_with_machines()
```

#### خدمات الرواتب
```python
class PayrollService:
    - calculate_salary()
    - generate_payslip()
    - process_bulk_payroll()
    - calculate_deductions()
```

### 3. واجهة برمجة التطبيقات (API Layer)

#### REST API Endpoints
```
/api/v1/hr/
├── employees/
├── departments/
├── attendance/
├── payroll/
├── leaves/
├── reports/
└── analytics/
```

## تصميم واجهة المستخدم

### 1. نظام التصميم

#### الألوان الأساسية
```css
:root {
  --primary: #2563eb;      /* أزرق أساسي */
  --secondary: #64748b;    /* رمادي ثانوي */
  --success: #10b981;      /* أخضر نجاح */
  --warning: #f59e0b;      /* أصفر تحذير */
  --danger: #ef4444;       /* أحمر خطر */
  --info: #06b6d4;         /* أزرق معلومات */
  --light: #f8fafc;        /* رمادي فاتح */
  --dark: #1e293b;         /* رمادي داكن */
}
```

#### الخطوط
- **الخط الأساسي**: Cairo (Google Fonts)
- **الخط الثانوي**: Tajawal
- **أحجام الخطوط**: 12px, 14px, 16px, 18px, 24px, 32px

#### المسافات
- **وحدة أساسية**: 8px
- **مسافات**: 8px, 16px, 24px, 32px, 48px, 64px

### 2. مكونات الواجهة

#### البطاقات (Cards)
```html
<div class="card">
  <div class="card-header">
    <h5 class="card-title">العنوان</h5>
    <div class="card-actions">أزرار العمل</div>
  </div>
  <div class="card-body">المحتوى</div>
  <div class="card-footer">التذييل</div>
</div>
```

#### الجداول التفاعلية
```html
<div class="table-container">
  <div class="table-toolbar">
    <div class="table-search">بحث</div>
    <div class="table-filters">فلاتر</div>
    <div class="table-actions">إجراءات</div>
  </div>
  <table class="table table-responsive">
    <!-- محتوى الجدول -->
  </table>
  <div class="table-pagination">ترقيم الصفحات</div>
</div>
```

#### النماذج المحسنة
```html
<form class="form-modern">
  <div class="form-section">
    <h6 class="form-section-title">البيانات الأساسية</h6>
    <div class="form-grid">
      <div class="form-group">
        <label class="form-label">الاسم</label>
        <input type="text" class="form-control">
        <div class="form-feedback">رسالة التحقق</div>
      </div>
    </div>
  </div>
</form>
```

### 3. التخطيط المتجاوب

#### نقاط الكسر (Breakpoints)
```css
/* Mobile First Approach */
@media (min-width: 576px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 992px) { /* lg */ }
@media (min-width: 1200px) { /* xl */ }
@media (min-width: 1400px) { /* xxl */ }
```

#### الشبكة المرنة
```html
<div class="container-fluid">
  <div class="row">
    <div class="col-12 col-md-8 col-lg-9">المحتوى الرئيسي</div>
    <div class="col-12 col-md-4 col-lg-3">الشريط الجانبي</div>
  </div>
</div>
```

## تصميم قاعدة البيانات

### 1. الجداول المحسنة

#### جدول الشركات
```sql
CREATE TABLE hr_company (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    name_english VARCHAR(200),
    code VARCHAR(20) UNIQUE NOT NULL,
    tax_id VARCHAR(50),
    commercial_register VARCHAR(50),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(254),
    website VARCHAR(200),
    logo VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### جدول الموظفين
```sql
CREATE TABLE hr_employee (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(300),
    full_name_english VARCHAR(300),
    email VARCHAR(254) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    mobile VARCHAR(20),
    address TEXT,
    national_id VARCHAR(20) UNIQUE NOT NULL,
    passport_number VARCHAR(20),
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    marital_status VARCHAR(20) NOT NULL,
    nationality VARCHAR(50) NOT NULL,
    company_id UUID REFERENCES hr_company(id),
    branch_id UUID REFERENCES hr_branch(id),
    department_id UUID REFERENCES hr_department(id),
    job_position_id UUID REFERENCES hr_job_position(id),
    manager_id UUID REFERENCES hr_employee(id),
    hire_date DATE NOT NULL,
    employment_type VARCHAR(20) NOT NULL,
    employment_status VARCHAR(20) DEFAULT 'active',
    basic_salary DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'SAR',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. الفهارس المحسنة

```sql
-- فهارس الأداء
CREATE INDEX idx_employee_number ON hr_employee(employee_number);
CREATE INDEX idx_employee_email ON hr_employee(email);
CREATE INDEX idx_employee_national_id ON hr_employee(national_id);
CREATE INDEX idx_employee_company_dept ON hr_employee(company_id, department_id);
CREATE INDEX idx_employee_status ON hr_employee(employment_status);
CREATE INDEX idx_employee_hire_date ON hr_employee(hire_date);

-- فهارس البحث النصي
CREATE INDEX idx_employee_search ON hr_employee USING gin(
    to_tsvector('arabic', full_name || ' ' || COALESCE(full_name_english, ''))
);
```

## تصميم الأمان

### 1. نظام الصلاحيات

#### مستويات الصلاحيات
```python
PERMISSION_LEVELS = [
    ('view', 'عرض'),
    ('add', 'إضافة'),
    ('change', 'تعديل'),
    ('delete', 'حذف'),
    ('approve', 'موافقة'),
    ('export', 'تصدير'),
]

MODULES = [
    ('employees', 'الموظفين'),
    ('attendance', 'الحضور'),
    ('payroll', 'الرواتب'),
    ('leaves', 'الإجازات'),
    ('reports', 'التقارير'),
]
```

#### مجموعات المستخدمين
```python
USER_GROUPS = [
    ('hr_admin', 'مدير الموارد البشرية'),
    ('hr_officer', 'موظف موارد بشرية'),
    ('department_manager', 'مدير قسم'),
    ('employee', 'موظف'),
    ('viewer', 'مستعرض'),
]
```

### 2. تشفير البيانات

#### البيانات الحساسة
```python
from cryptography.fernet import Fernet

class EncryptedField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.cipher.decrypt(value.encode()).decode()
    
    def to_python(self, value):
        return value
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return self.cipher.encrypt(value.encode()).decode()
```

## تصميم الأداء

### 1. التخزين المؤقت

#### استراتيجية التخزين المؤقت
```python
# Redis Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache Keys
CACHE_KEYS = {
    'employee_list': 'hr:employees:list:{page}:{filters}',
    'department_tree': 'hr:departments:tree:{company_id}',
    'attendance_summary': 'hr:attendance:summary:{employee_id}:{date}',
}
```

#### تخزين مؤقت للاستعلامات
```python
from django.core.cache import cache

def get_employees_cached(company_id, filters=None):
    cache_key = f"employees:{company_id}:{hash(str(filters))}"
    employees = cache.get(cache_key)
    
    if employees is None:
        employees = Employee.objects.filter(
            company_id=company_id,
            **filters or {}
        ).select_related('department', 'job_position')
        cache.set(cache_key, employees, 300)  # 5 minutes
    
    return employees
```

### 2. تحسين الاستعلامات

#### استخدام select_related و prefetch_related
```python
# تحسين استعلام الموظفين
employees = Employee.objects.select_related(
    'company',
    'branch', 
    'department',
    'job_position',
    'manager'
).prefetch_related(
    'attendance_records',
    'leave_requests',
    'documents'
)

# تحسين استعلام الحضور
attendance_records = AttendanceRecord.objects.select_related(
    'employee__department',
    'machine'
).filter(
    date__range=[start_date, end_date]
)
```

## تصميم التحليلات

### 1. مؤشرات الأداء الرئيسية

#### مؤشرات الموظفين
```python
class EmployeeKPIs:
    def get_total_employees(self, company_id=None):
        return Employee.objects.filter(
            company_id=company_id,
            is_active=True
        ).count()
    
    def get_turnover_rate(self, company_id=None, period='month'):
        # حساب معدل دوران الموظفين
        pass
    
    def get_average_tenure(self, company_id=None):
        # حساب متوسط سنوات الخدمة
        pass
```

#### مؤشرات الحضور
```python
class AttendanceKPIs:
    def get_attendance_rate(self, period='month'):
        # حساب معدل الحضور
        pass
    
    def get_late_arrivals(self, period='month'):
        # حساب التأخيرات
        pass
    
    def get_overtime_hours(self, period='month'):
        # حساب ساعات العمل الإضافي
        pass
```

### 2. الرسوم البيانية التفاعلية

#### Chart.js Integration
```javascript
// Employee Distribution Chart
const employeeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: departmentNames,
        datasets: [{
            data: employeeCounts,
            backgroundColor: colors
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom',
                rtl: true
            }
        }
    }
});

// Attendance Trend Chart
const attendanceChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: months,
        datasets: [{
            label: 'معدل الحضور',
            data: attendanceRates,
            borderColor: '#2563eb',
            tension: 0.4
        }]
    }
});
```

## تصميم التقارير

### 1. نظام التقارير المرن

#### قالب التقرير الأساسي
```python
class BaseReport:
    def __init__(self, filters=None):
        self.filters = filters or {}
    
    def get_data(self):
        raise NotImplementedError
    
    def generate_pdf(self):
        # إنتاج PDF باستخدام ReportLab
        pass
    
    def generate_excel(self):
        # إنتاج Excel باستخدام openpyxl
        pass
    
    def generate_csv(self):
        # إنتاج CSV
        pass
```

#### تقرير الموظفين
```python
class EmployeeReport(BaseReport):
    def get_data(self):
        return Employee.objects.filter(
            **self.filters
        ).select_related(
            'department', 'job_position'
        ).values(
            'employee_number',
            'full_name',
            'department__name',
            'job_position__title',
            'hire_date',
            'basic_salary'
        )
```

### 2. تصدير البيانات

#### تصدير Excel محسن
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

def export_employees_excel(employees):
    wb = Workbook()
    ws = wb.active
    ws.title = "قائمة الموظفين"
    
    # Headers
    headers = ['رقم الموظف', 'الاسم', 'القسم', 'الوظيفة', 'تاريخ التوظيف']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
    
    # Data
    for row, employee in enumerate(employees, 2):
        ws.cell(row=row, column=1, value=employee.employee_number)
        ws.cell(row=row, column=2, value=employee.full_name)
        ws.cell(row=row, column=3, value=employee.department.name)
        ws.cell(row=row, column=4, value=employee.job_position.title)
        ws.cell(row=row, column=5, value=employee.hire_date)
    
    return wb
```

## تصميم الإشعارات

### 1. نظام الإشعارات الذكية

#### أنواع الإشعارات
```python
NOTIFICATION_TYPES = [
    ('document_expiry', 'انتهاء صلاحية وثيقة'),
    ('leave_request', 'طلب إجازة'),
    ('attendance_late', 'تأخير في الحضور'),
    ('performance_review', 'تقييم الأداء'),
    ('birthday', 'عيد ميلاد'),
    ('work_anniversary', 'ذكرى التوظيف'),
]
```

#### خدمة الإشعارات
```python
class NotificationService:
    def send_notification(self, user, notification_type, context):
        # إرسال إشعار داخل النظام
        Notification.objects.create(
            user=user,
            type=notification_type,
            title=self.get_title(notification_type, context),
            message=self.get_message(notification_type, context),
            data=context
        )
        
        # إرسال بريد إلكتروني إذا لزم الأمر
        if self.should_send_email(notification_type):
            self.send_email_notification(user, notification_type, context)
    
    def check_document_expiry(self):
        # فحص الوثائق منتهية الصلاحية
        expiring_docs = EmployeeDocument.objects.filter(
            expiry_date__lte=timezone.now() + timedelta(days=30),
            status='active'
        )
        
        for doc in expiring_docs:
            self.send_notification(
                doc.employee.manager,
                'document_expiry',
                {'document': doc, 'employee': doc.employee}
            )
```

## تصميم التكامل

### 1. تكامل أجهزة الحضور

#### ZKTeco Integration
```python
from zk import ZK

class ZKTecoService:
    def __init__(self, ip, port=4370):
        self.ip = ip
        self.port = port
        self.conn = None
    
    def connect(self):
        zk = ZK(self.ip, port=self.port)
        self.conn = zk.connect()
        return self.conn is not None
    
    def get_attendance_records(self):
        if not self.conn:
            return []
        
        attendance = self.conn.get_attendance()
        records = []
        
        for record in attendance:
            records.append({
                'user_id': record.user_id,
                'timestamp': record.timestamp,
                'punch': record.punch,  # 0=check-in, 1=check-out
            })
        
        return records
    
    def sync_users(self, employees):
        if not self.conn:
            return False
        
        for employee in employees:
            self.conn.set_user(
                uid=employee.id,
                name=employee.full_name,
                privilege=0,
                password='',
                group_id='',
                user_id=employee.employee_number
            )
        
        return True
```

### 2. تكامل البريد الإلكتروني

#### Email Templates
```python
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

class EmailService:
    def send_leave_approval_email(self, leave_request):
        subject = f'طلب إجازة - {leave_request.employee.full_name}'
        
        html_content = render_to_string('emails/leave_approval.html', {
            'leave_request': leave_request,
            'employee': leave_request.employee,
        })
        
        text_content = render_to_string('emails/leave_approval.txt', {
            'leave_request': leave_request,
            'employee': leave_request.employee,
        })
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[leave_request.employee.manager.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
```

## استراتيجية النشر

### 1. البيئات

#### Development Environment
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://user:pass@db:5432/hrdb
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: hrdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
  
  redis:
    image: redis:6-alpine
```

#### Production Environment
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  web:
    image: hr-system:latest
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@db:5432/hrdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
```

### 2. CI/CD Pipeline

#### GitHub Actions
```yaml
name: HR System CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python manage.py test
    - name: Run linting
      run: |
        flake8 .
        black --check .

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        # Deployment script
```

هذا التصميم يوفر أساساً قوياً لتطوير نظام موارد بشرية عصري وشامل مع الحفاظ على الدعم الكامل للغة العربية والمتطلبات المحلية.