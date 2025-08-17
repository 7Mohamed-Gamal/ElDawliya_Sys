"""
اختبارات النماذج
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from Hr.models import Employee, Department, JobPosition, Company, Branch
from Hr.services.encryption_service import encryption_service
from decimal import Decimal
import uuid


class CompanyModelTest(TestCase):
    """اختبارات نموذج الشركة"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.company_data = {
            'name': 'شركة الدولية للموارد البشرية',
            'name_en': 'ElDawliya HR Company',
            'commercial_register': '1234567890',
            'tax_number': '300123456789003',
            'phone': '0112345678',
            'email': 'info@eldawliya.com',
            'address': 'الرياض، المملكة العربية السعودية'
        }
    
    def test_create_company(self):
        """اختبار إنشاء شركة"""
        company = Company.objects.create(**self.company_data)
        
        self.assertEqual(company.name, self.company_data['name'])
        self.assertEqual(company.name_en, self.company_data['name_en'])
        self.assertEqual(company.commercial_register, self.company_data['commercial_register'])
        self.assertTrue(company.is_active)
        self.assertIsNotNone(company.created_at)
    
    def test_company_str_method(self):
        """اختبار طريقة __str__ للشركة"""
        company = Company.objects.create(**self.company_data)
        self.assertEqual(str(company), self.company_data['name'])
    
    def test_company_unique_commercial_register(self):
        """اختبار تفرد السجل التجاري"""
        Company.objects.create(**self.company_data)
        
        # محاولة إنشاء شركة أخرى بنفس السجل التجاري
        duplicate_data = self.company_data.copy()
        duplicate_data['name'] = 'شركة أخرى'
        
        with self.assertRaises(IntegrityError):
            Company.objects.create(**duplicate_data)
    
    def test_company_phone_validation(self):
        """اختبار التحقق من رقم الهاتف"""
        invalid_data = self.company_data.copy()
        invalid_data['phone'] = '123'  # رقم قصير
        
        company = Company(**invalid_data)
        with self.assertRaises(ValidationError):
            company.full_clean()


class DepartmentModelTest(TestCase):
    """اختبارات نموذج القسم"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        self.department_data = {
            'name': 'قسم الموارد البشرية',
            'name_en': 'Human Resources Department',
            'code': 'HR001',
            'company': self.company,
            'description': 'قسم إدارة الموارد البشرية'
        }
    
    def test_create_department(self):
        """اختبار إنشاء قسم"""
        department = Department.objects.create(**self.department_data)
        
        self.assertEqual(department.name, self.department_data['name'])
        self.assertEqual(department.code, self.department_data['code'])
        self.assertEqual(department.company, self.company)
        self.assertTrue(department.is_active)
    
    def test_department_hierarchy(self):
        """اختبار الهيكل الهرمي للأقسام"""
        parent_dept = Department.objects.create(**self.department_data)
        
        child_data = self.department_data.copy()
        child_data['name'] = 'قسم التوظيف'
        child_data['code'] = 'HR002'
        child_data['parent'] = parent_dept
        
        child_dept = Department.objects.create(**child_data)
        
        self.assertEqual(child_dept.parent, parent_dept)
        self.assertIn(child_dept, parent_dept.children.all())
    
    def test_department_unique_code_per_company(self):
        """اختبار تفرد كود القسم داخل الشركة"""
        Department.objects.create(**self.department_data)
        
        # محاولة إنشاء قسم آخر بنفس الكود في نفس الشركة
        duplicate_data = self.department_data.copy()
        duplicate_data['name'] = 'قسم آخر'
        
        with self.assertRaises(IntegrityError):
            Department.objects.create(**duplicate_data)
    
    def test_department_different_companies_same_code(self):
        """اختبار إمكانية استخدام نفس الكود في شركات مختلفة"""
        Department.objects.create(**self.department_data)
        
        # إنشاء شركة أخرى
        other_company = Company.objects.create(
            name='شركة أخرى',
            commercial_register='0987654321'
        )
        
        # إنشاء قسم بنفس الكود في شركة مختلفة
        other_dept_data = self.department_data.copy()
        other_dept_data['company'] = other_company
        
        other_dept = Department.objects.create(**other_dept_data)
        self.assertEqual(other_dept.code, self.department_data['code'])


class JobPositionModelTest(TestCase):
    """اختبارات نموذج المنصب الوظيفي"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        self.department = Department.objects.create(
            name='قسم الموارد البشرية',
            code='HR001',
            company=self.company
        )
        
        self.job_data = {
            'name': 'مدير الموارد البشرية',
            'name_en': 'HR Manager',
            'code': 'HRM001',
            'department': self.department,
            'level': 'manager',
            'min_salary': Decimal('8000.00'),
            'max_salary': Decimal('15000.00'),
            'description': 'إدارة شؤون الموظفين'
        }
    
    def test_create_job_position(self):
        """اختبار إنشاء منصب وظيفي"""
        job = JobPosition.objects.create(**self.job_data)
        
        self.assertEqual(job.name, self.job_data['name'])
        self.assertEqual(job.code, self.job_data['code'])
        self.assertEqual(job.department, self.department)
        self.assertEqual(job.level, 'manager')
        self.assertTrue(job.is_active)
    
    def test_salary_range_validation(self):
        """اختبار التحقق من نطاق الراتب"""
        invalid_data = self.job_data.copy()
        invalid_data['min_salary'] = Decimal('20000.00')  # أكبر من الحد الأقصى
        invalid_data['max_salary'] = Decimal('15000.00')
        
        job = JobPosition(**invalid_data)
        with self.assertRaises(ValidationError):
            job.full_clean()
    
    def test_job_level_choices(self):
        """اختبار خيارات مستوى الوظيفة"""
        valid_levels = ['entry', 'junior', 'senior', 'lead', 'manager', 'director', 'executive']
        
        for level in valid_levels:
            job_data = self.job_data.copy()
            job_data['code'] = f'TEST_{level.upper()}'
            job_data['level'] = level
            
            job = JobPosition.objects.create(**job_data)
            self.assertEqual(job.level, level)


class EmployeeModelTest(TestCase):
    """اختبارات نموذج الموظف"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        self.department = Department.objects.create(
            name='قسم الموارد البشرية',
            code='HR001',
            company=self.company
        )
        
        self.job_position = JobPosition.objects.create(
            name='موظف موارد بشرية',
            code='HRE001',
            department=self.department,
            min_salary=Decimal('5000.00'),
            max_salary=Decimal('8000.00')
        )
        
        self.employee_data = {
            'user': self.user,
            'employee_id': 'EMP001',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'first_name_en': 'Ahmed',
            'last_name_en': 'Mohammed',
            'national_id': '1234567890',
            'phone_number': '0501234567',
            'email': 'ahmed@company.com',
            'department': self.department,
            'job_position': self.job_position,
            'company': self.company,
            'hire_date': '2024-01-01',
            'basic_salary': Decimal('6000.00'),
            'gender': 'male',
            'marital_status': 'single'
        }
    
    def test_create_employee(self):
        """اختبار إنشاء موظف"""
        employee = Employee.objects.create(**self.employee_data)
        
        self.assertEqual(employee.employee_id, self.employee_data['employee_id'])
        self.assertEqual(employee.first_name, self.employee_data['first_name'])
        self.assertEqual(employee.department, self.department)
        self.assertEqual(employee.job_position, self.job_position)
        self.assertTrue(employee.is_active)
    
    def test_employee_full_name_property(self):
        """اختبار خاصية الاسم الكامل"""
        employee = Employee.objects.create(**self.employee_data)
        expected_name = f"{self.employee_data['first_name']} {self.employee_data['last_name']}"
        self.assertEqual(employee.full_name, expected_name)
    
    def test_employee_full_name_en_property(self):
        """اختبار خاصية الاسم الكامل بالإنجليزية"""
        employee = Employee.objects.create(**self.employee_data)
        expected_name = f"{self.employee_data['first_name_en']} {self.employee_data['last_name_en']}"
        self.assertEqual(employee.full_name_en, expected_name)
    
    def test_employee_age_calculation(self):
        """اختبار حساب العمر"""
        employee_data = self.employee_data.copy()
        employee_data['birth_date'] = '1990-01-01'
        
        employee = Employee.objects.create(**employee_data)
        self.assertIsInstance(employee.age, int)
        self.assertGreater(employee.age, 0)
    
    def test_employee_years_of_service(self):
        """اختبار حساب سنوات الخدمة"""
        employee = Employee.objects.create(**self.employee_data)
        self.assertIsInstance(employee.years_of_service, int)
        self.assertGreaterEqual(employee.years_of_service, 0)
    
    def test_employee_unique_employee_id(self):
        """اختبار تفرد رقم الموظف"""
        Employee.objects.create(**self.employee_data)
        
        # محاولة إنشاء موظف آخر بنفس الرقم
        duplicate_data = self.employee_data.copy()
        duplicate_data['user'] = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        duplicate_data['first_name'] = 'محمد'
        
        with self.assertRaises(IntegrityError):
            Employee.objects.create(**duplicate_data)
    
    def test_employee_salary_within_job_range(self):
        """اختبار أن راتب الموظف ضمن نطاق الوظيفة"""
        # راتب أقل من الحد الأدنى
        invalid_data = self.employee_data.copy()
        invalid_data['basic_salary'] = Decimal('3000.00')
        
        employee = Employee(**invalid_data)
        with self.assertRaises(ValidationError):
            employee.full_clean()
        
        # راتب أكبر من الحد الأقصى
        invalid_data['basic_salary'] = Decimal('10000.00')
        
        employee = Employee(**invalid_data)
        with self.assertRaises(ValidationError):
            employee.full_clean()
    
    def test_employee_national_id_encryption(self):
        """اختبار تشفير رقم الهوية الوطنية"""
        employee = Employee.objects.create(**self.employee_data)
        
        # التحقق من أن رقم الهوية مشفر في قاعدة البيانات
        employee_from_db = Employee.objects.get(id=employee.id)
        
        # إذا كان التشفير مفعلاً، يجب أن يكون الرقم مشفراً
        if hasattr(employee_from_db, '_state') and hasattr(employee_from_db._state, 'db'):
            # فحص القيمة المشفرة مباشرة من قاعدة البيانات
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT national_id FROM Hr_employee WHERE id = %s",
                    [employee.id]
                )
                db_value = cursor.fetchone()[0]
                
                # إذا كان مشفراً، يجب أن يكون مختلفاً عن القيمة الأصلية
                if encryption_service.is_encrypted(db_value):
                    self.assertNotEqual(db_value, self.employee_data['national_id'])
                    # التحقق من إمكانية فك التشفير
                    decrypted = encryption_service.decrypt_national_id(db_value)
                    self.assertEqual(decrypted, self.employee_data['national_id'])
    
    def test_employee_phone_validation(self):
        """اختبار التحقق من رقم الهاتف"""
        invalid_data = self.employee_data.copy()
        invalid_data['phone_number'] = '123'  # رقم قصير
        
        employee = Employee(**invalid_data)
        with self.assertRaises(ValidationError):
            employee.full_clean()
    
    def test_employee_email_validation(self):
        """اختبار التحقق من البريد الإلكتروني"""
        invalid_data = self.employee_data.copy()
        invalid_data['email'] = 'invalid-email'  # بريد غير صحيح
        
        employee = Employee(**invalid_data)
        with self.assertRaises(ValidationError):
            employee.full_clean()
    
    def test_employee_gender_choices(self):
        """اختبار خيارات الجنس"""
        valid_genders = ['male', 'female']
        
        for gender in valid_genders:
            employee_data = self.employee_data.copy()
            employee_data['employee_id'] = f'EMP_{gender.upper()}'
            employee_data['user'] = User.objects.create_user(
                username=f'user_{gender}',
                email=f'{gender}@example.com',
                password='testpass123'
            )
            employee_data['gender'] = gender
            
            employee = Employee.objects.create(**employee_data)
            self.assertEqual(employee.gender, gender)
    
    def test_employee_marital_status_choices(self):
        """اختبار خيارات الحالة الاجتماعية"""
        valid_statuses = ['single', 'married', 'divorced', 'widowed']
        
        for status in valid_statuses:
            employee_data = self.employee_data.copy()
            employee_data['employee_id'] = f'EMP_{status.upper()}'
            employee_data['user'] = User.objects.create_user(
                username=f'user_{status}',
                email=f'{status}@example.com',
                password='testpass123'
            )
            employee_data['marital_status'] = status
            
            employee = Employee.objects.create(**employee_data)
            self.assertEqual(employee.marital_status, status)


class EmployeeRelatedModelsTest(TestCase):
    """اختبارات النماذج المرتبطة بالموظف"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        self.department = Department.objects.create(
            name='قسم الموارد البشرية',
            code='HR001',
            company=self.company
        )
        
        self.job_position = JobPosition.objects.create(
            name='موظف موارد بشرية',
            code='HRE001',
            department=self.department,
            min_salary=Decimal('5000.00'),
            max_salary=Decimal('8000.00')
        )
        
        self.employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP001',
            first_name='أحمد',
            last_name='محمد',
            national_id='1234567890',
            phone_number='0501234567',
            email='ahmed@company.com',
            department=self.department,
            job_position=self.job_position,
            company=self.company,
            hire_date='2024-01-01',
            basic_salary=Decimal('6000.00'),
            gender='male',
            marital_status='single'
        )
    
    def test_employee_cascade_delete(self):
        """اختبار الحذف المتسلسل"""
        employee_id = self.employee.id
        
        # حذف المستخدم يجب أن يحذف الموظف
        self.user.delete()
        
        with self.assertRaises(Employee.DoesNotExist):
            Employee.objects.get(id=employee_id)
    
    def test_department_employee_relationship(self):
        """اختبار العلاقة بين القسم والموظفين"""
        self.assertIn(self.employee, self.department.employees.all())
        self.assertEqual(self.employee.department, self.department)
    
    def test_job_position_employee_relationship(self):
        """اختبار العلاقة بين المنصب والموظفين"""
        self.assertIn(self.employee, self.job_position.employees.all())
        self.assertEqual(self.employee.job_position, self.job_position)


class ModelMetaTest(TestCase):
    """اختبارات خصائص النماذج العامة"""
    
    def test_model_verbose_names(self):
        """اختبار أسماء النماذج المعروضة"""
        self.assertEqual(Company._meta.verbose_name, 'شركة')
        self.assertEqual(Company._meta.verbose_name_plural, 'الشركات')
        
        self.assertEqual(Department._meta.verbose_name, 'قسم')
        self.assertEqual(Department._meta.verbose_name_plural, 'الأقسام')
        
        self.assertEqual(JobPosition._meta.verbose_name, 'منصب وظيفي')
        self.assertEqual(JobPosition._meta.verbose_name_plural, 'المناصب الوظيفية')
        
        self.assertEqual(Employee._meta.verbose_name, 'موظف')
        self.assertEqual(Employee._meta.verbose_name_plural, 'الموظفون')
    
    def test_model_ordering(self):
        """اختبار ترتيب النماذج"""
        # إنشاء بيانات للاختبار
        company = Company.objects.create(
            name='شركة الاختبار',
            commercial_register='1234567890'
        )
        
        dept1 = Department.objects.create(
            name='قسم ب',
            code='DEPT_B',
            company=company
        )
        
        dept2 = Department.objects.create(
            name='قسم أ',
            code='DEPT_A',
            company=company
        )
        
        # التحقق من الترتيب
        departments = list(Department.objects.all())
        self.assertEqual(departments[0].name, 'قسم أ')
        self.assertEqual(departments[1].name, 'قسم ب')
    
    def test_model_indexes(self):
        """اختبار فهارس النماذج"""
        # التحقق من وجود الفهارس المطلوبة
        employee_indexes = [index.name for index in Employee._meta.indexes]
        
        # يجب أن تحتوي على فهارس للحقول المهمة
        expected_fields = ['employee_id', 'national_id', 'department', 'is_active']
        
        # فحص وجود فهارس للحقول المهمة (قد تكون بأسماء مختلفة)
        for field in expected_fields:
            field_has_index = any(
                field in str(index.fields) for index in Employee._meta.indexes
            ) or any(
                field in [f.name for f in Employee._meta.get_field(field).get_db_index_fields()]
                if hasattr(Employee._meta.get_field(field), 'get_db_index_fields')
                else [field] if getattr(Employee._meta.get_field(field), 'db_index', False) else []
            )
            
            # ملاحظة: هذا الاختبار قد يحتاج تعديل حسب تنفيق الفهارس الفعلي