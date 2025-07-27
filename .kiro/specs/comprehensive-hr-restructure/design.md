# تصميم إعادة هيكلة نظام الموارد البشرية الشامل

## نظرة عامة

هذا التصميم يهدف إلى إعادة هيكلة تطبيق الموارد البشرية بالكامل ليصبح نظاماً شاملاً ومتطوراً يدعم جميع جوانب إدارة الموارد البشرية. النظام سيكون مبنياً على Django 4.2+ وSQL Server مع دعم كامل للغة العربية ونظام RTL، ويتضمن ميزات متقدمة مثل إدارة الملفات، التأمينات، بيانات السيارات، والتقييمات الشاملة.

## الهيكل المعماري

### 1. هيكل النماذج المحسن والموسع

#### النماذج الأساسية (Core Models)
```python
# Company Structure - الهيكل التنظيمي
Company -> Branch -> Department -> JobPosition -> Employee

# Supporting Models - النماذج المساعدة
WorkShift, AttendanceMachine, LeaveType, SalaryComponent, EvaluationCriteria

# Extended Models - النماذج الموسعة
EmployeeEducation, EmployeeInsurance, EmployeeVehicle, EmployeeFiles
```

#### العلاقات الرئيسية المحسنة
- **Company (1:N) Branch**: شركة واحدة لها عدة فروع
- **Branch (1:N) Department**: فرع واحد له عدة أقسام  
- **Department (1:N) JobPosition**: قسم واحد له عدة وظائف
- **JobPosition (1:N) Employee**: وظيفة واحدة لها عدة موظفين
- **Employee (1:N) EmployeeEducation**: موظف واحد له عدة مؤهلات
- **Employee (1:N) EmployeeInsurance**: موظف واحد له عدة تأمينات
- **Employee (1:N) EmployeeVehicle**: موظف واحد له عدة سيارات
- **Employee (1:N) EmployeeFiles**: موظف واحد له عدة ملفات

### 2. النماذج الجديدة والموسعة

#### نموذج المؤهلات الدراسية
```python
class EmployeeEducation(models.Model):
    """نموذج المؤهلات الدراسية للموظف"""
    DEGREE_CHOICES = [
        ('high_school', 'ثانوية عامة'),
        ('diploma', 'دبلوم'),
        ('bachelor', 'بكالوريوس'),
        ('master', 'ماجستير'),
        ('phd', 'دكتوراه'),
        ('certificate', 'شهادة مهنية'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    degree_type = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    major = models.CharField(max_length=200)  # التخصص
    institution = models.CharField(max_length=200)  # الجامعة/المؤسسة
    graduation_year = models.PositiveIntegerField()
    grade = models.CharField(max_length=10, blank=True)  # المعدل
    country = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    certificate_file = models.FileField(upload_to='education/')
```

#### نموذج التأمينات
```python
class EmployeeInsurance(models.Model):
    """نموذج تأمينات الموظف"""
    INSURANCE_TYPE_CHOICES = [
        ('social', 'تأمين اجتماعي'),
        ('medical', 'تأمين صحي'),
        ('life', 'تأمين على الحياة'),
        ('disability', 'تأمين ضد العجز'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_TYPE_CHOICES)
    policy_number = models.CharField(max_length=100)
    provider = models.CharField(max_length=200)  # مقدم التأمين
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    employee_contribution = models.DecimalField(max_digits=10, decimal_places=2)
    employer_contribution = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
```

#### نموذج بيانات السيارات
```python
class EmployeeVehicle(models.Model):
    """نموذج سيارات الموظفين"""
    VEHICLE_TYPE_CHOICES = [
        ('company', 'سيارة الشركة'),
        ('personal', 'سيارة شخصية'),
        ('allowance', 'بدل سيارة'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    make = models.CharField(max_length=100)  # الماركة
    model = models.CharField(max_length=100)  # الموديل
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=20)
    assigned_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    monthly_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_expiry = models.DateField()
    registration_expiry = models.DateField()
    is_active = models.BooleanField(default=True)
```

### 3. طبقة الخدمات المحسنة (Enhanced Services Layer)

#### خدمات الموظفين الشاملة
```python
class EmployeeService:
    """خدمات إدارة الموظفين الشاملة"""
    
    def create_employee_complete(self, employee_data, education_data=None, 
                               insurance_data=None, vehicle_data=None):
        """إنشاء موظف مع جميع البيانات المرتبطة"""
        with transaction.atomic():
            employee = Employee.objects.create(**employee_data)
            
            if education_data:
                self._create_education_records(employee, education_data)
            
            if insurance_data:
                self._create_insurance_records(employee, insurance_data)
                
            if vehicle_data:
                self._create_vehicle_records(employee, vehicle_data)
                
            return employee
    
    def update_employee_comprehensive(self, employee_id, update_data):
        """تحديث شامل لبيانات الموظف"""
        pass
    
    def calculate_service_years_detailed(self, employee):
        """حساب تفصيلي لسنوات الخدمة"""
        pass
    
    def get_employee_complete_profile(self, employee_id):
        """الحصول على الملف الشخصي الكامل للموظف"""
        pass
    
    def export_employee_comprehensive_data(self, filters=None):
        """تصدير شامل لبيانات الموظفين"""
        pass
```

## تصميم قاعدة البيانات المحسن

### 1. الجداول الجديدة والموسعة

#### جدول المؤهلات الدراسية
```sql
CREATE TABLE hr_employee_education (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    employee_id UNIQUEIDENTIFIER NOT NULL REFERENCES hr_employee(id),
    degree_type NVARCHAR(20) NOT NULL,
    major NVARCHAR(200) NOT NULL,
    institution NVARCHAR(200) NOT NULL,
    graduation_year INT NOT NULL,
    grade NVARCHAR(10),
    country NVARCHAR(100) NOT NULL,
    is_verified BIT DEFAULT 0,
    certificate_file NVARCHAR(255),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
```

#### جدول التأمينات
```sql
CREATE TABLE hr_employee_insurance (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    employee_id UNIQUEIDENTIFIER NOT NULL REFERENCES hr_employee(id),
    insurance_type NVARCHAR(20) NOT NULL,
    policy_number NVARCHAR(100) NOT NULL,
    provider NVARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    premium_amount DECIMAL(10,2) NOT NULL,
    coverage_amount DECIMAL(12,2) NOT NULL,
    employee_contribution DECIMAL(10,2) DEFAULT 0,
    employer_contribution DECIMAL(10,2) DEFAULT 0,
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
```

### 2. واجهة برمجة التطبيقات المحسنة

#### REST API Endpoints الشاملة
```
/api/v1/hr/
├── employees/
│   ├── {id}/profile/          # الملف الشخصي الكامل
│   ├── {id}/education/        # المؤهلات الدراسية
│   ├── {id}/insurance/        # التأمينات
│   ├── {id}/vehicles/         # السيارات
│   ├── {id}/files/           # الملفات والوثائق
│   ├── {id}/evaluations/     # التقييمات
│   └── bulk-operations/      # العمليات المجمعة
├── attendance/
├── payroll/
├── leaves/
├── evaluations/
├── reports/
└── analytics/
```

## تصميم الأمان المتقدم

### 1. نظام الصلاحيات الهرمي

#### مستويات الصلاحيات المفصلة
```python
PERMISSION_LEVELS = [
    ('view', 'عرض'),
    ('add', 'إضافة'),
    ('change', 'تعديل'),
    ('delete', 'حذف'),
    ('approve', 'موافقة'),
    ('export', 'تصدير'),
    ('import', 'استيراد'),
    ('bulk_edit', 'تعديل مجمع'),
    ('view_sensitive', 'عرض البيانات الحساسة'),
    ('manage_files', 'إدارة الملفات'),
]

HR_MODULES = [
    ('employees', 'الموظفين'),
    ('employee_files', 'ملفات الموظفين'),
    ('attendance', 'الحضور'),
    ('payroll', 'الرواتب'),
    ('leaves', 'الإجازات'),
    ('evaluations', 'التقييمات'),
    ('reports', 'التقارير'),
    ('analytics', 'التحليلات'),
    ('settings', 'الإعدادات'),
]
```

هذا التصميم يوفر أساساً قوياً لإعادة هيكلة نظام الموارد البشرية ليصبح نظاماً متطوراً وشاملاً يلبي جميع المتطلبات المحددة.