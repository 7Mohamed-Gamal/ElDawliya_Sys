"""
أمر إنشاء بيانات اختبار الأداء
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from Hr.models import Company, Branch, Department, JobPosition, Employee
from decimal import Decimal
import random
from faker import Faker
from datetime import date, timedelta
import time


class Command(BaseCommand):
    help = 'إنشاء بيانات كبيرة لاختبار الأداء والحمولة'

    def add_arguments(self, parser):
        parser.add_argument(
            '--employees',
            type=int,
            default=1000,
            help='عدد الموظفين المراد إنشاؤهم (افتراضي: 1000)'
        )
        
        parser.add_argument(
            '--companies',
            type=int,
            default=5,
            help='عدد الشركات المراد إنشاؤها (افتراضي: 5)'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='حجم الدفعة للإنشاء المجمع (افتراضي: 100)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='مسح البيانات الموجودة قبل إنشاء بيانات جديدة'
        )

    def handle(self, *args, **options):
        self.fake = Faker(['ar_SA', 'en_US'])
        
        employees_count = options['employees']
        companies_count = options['companies']
        batch_size = options['batch_size']
        clear_data = options['clear']
        
        if clear_data:
            self.clear_existing_data()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'بدء إنشاء بيانات اختبار الأداء:\n'
                f'  - {companies_count} شركة\n'
                f'  - {employees_count} موظف\n'
                f'  - حجم الدفعة: {batch_size}'
            )
        )
        
        start_time = time.time()
        
        # إنشاء البيانات الأساسية
        companies = self.create_companies_bulk(companies_count)
        branches = self.create_branches_bulk(companies)
        departments = self.create_departments_bulk(companies)
        job_positions = self.create_job_positions_bulk(departments)
        
        # إنشاء الموظفين على دفعات
        employees = self.create_employees_bulk(
            companies, departments, job_positions, employees_count, batch_size
        )
        
        total_time = time.time() - start_time
        
        self.stdout.write(
            self.style.SUCCESS(
                f'تم إنشاء بيانات اختبار الأداء بنجاح في {total_time:.2f} ثانية:\n'
                f'  - {len(companies)} شركة\n'
                f'  - {len(branches)} فرع\n'
                f'  - {len(departments)} قسم\n'
                f'  - {len(job_positions)} منصب وظيفي\n'
                f'  - {len(employees)} موظف\n'
                f'  - معدل الإنشاء: {len(employees)/total_time:.1f} موظف/ثانية'
            )
        )

    def clear_existing_data(self):
        """مسح البيانات الموجودة"""
        self.stdout.write('مسح البيانات الموجودة...')
        
        start_time = time.time()
        
        # مسح بالترتيب الصحيح لتجنب مشاكل المفاتيح الخارجية
        Employee.objects.all().delete()
        JobPosition.objects.all().delete()
        Department.objects.all().delete()
        Branch.objects.all().delete()
        Company.objects.all().delete()
        
        # مسح المستخدمين المرتبطين
        User.objects.filter(username__startswith='perf_').delete()
        
        clear_time = time.time() - start_time
        
        self.stdout.write(
            self.style.SUCCESS(f'تم مسح البيانات في {clear_time:.2f} ثانية')
        )

    def create_companies_bulk(self, count):
        """إنشاء الشركات بشكل مجمع"""
        self.stdout.write(f'إنشاء {count} شركة...')
        
        companies_data = []
        
        for i in range(count):
            companies_data.append(Company(
                name=f'شركة الأداء {i+1}',
                name_en=f'Performance Company {i+1}',
                commercial_register=f'{2010000000 + i}',
                tax_number=f'{400000000000000 + i}',
                phone=f'011{random.randint(1000000, 9999999)}',
                email=f'info@perfcompany{i+1}.com',
                website=f'https://www.perfcompany{i+1}.com',
                address=self.fake.address(),
                city=random.choice(['الرياض', 'جدة', 'الدمام']),
                country='المملكة العربية السعودية',
                postal_code=f'{random.randint(10000, 99999)}',
                is_active=True
            ))
        
        companies = Company.objects.bulk_create(companies_data)
        return companies

    def create_branches_bulk(self, companies):
        """إنشاء الفروع بشكل مجمع"""
        self.stdout.write('إنشاء الفروع...')
        
        branches_data = []
        cities = ['الرياض', 'جدة', 'الدمام', 'مكة', 'المدينة']
        
        for company in companies:
            # 3 فروع لكل شركة
            for i in range(3):
                city = cities[i % len(cities)]
                
                branches_data.append(Branch(
                    name=f'فرع {city} - {company.name}',
                    name_en=f'{city} Branch - {company.name_en}',
                    code=f'{company.id}_{city[:3].upper()}{i+1:02d}',
                    company=company,
                    address=self.fake.address(),
                    city=city,
                    phone=f'011{random.randint(1000000, 9999999)}',
                    manager_name=self.fake.name(),
                    is_active=True
                ))
        
        branches = Branch.objects.bulk_create(branches_data)
        return branches

    def create_departments_bulk(self, companies):
        """إنشاء الأقسام بشكل مجمع"""
        self.stdout.write('إنشاء الأقسام...')
        
        departments_data = []
        
        department_templates = [
            ('قسم الموارد البشرية', 'HR Department', 'HR'),
            ('قسم تقنية المعلومات', 'IT Department', 'IT'),
            ('قسم المالية', 'Finance Department', 'FIN'),
            ('قسم التسويق', 'Marketing Department', 'MKT'),
            ('قسم العمليات', 'Operations Department', 'OPS'),
            ('قسم الجودة', 'Quality Department', 'QA'),
            ('قسم المبيعات', 'Sales Department', 'SAL'),
            ('قسم الأمن', 'Security Department', 'SEC')
        ]
        
        for company in companies:
            for i, (name_ar, name_en, code) in enumerate(department_templates):
                departments_data.append(Department(
                    name=name_ar,
                    name_en=name_en,
                    code=f'{company.id}_{code}{i+1:02d}',
                    company=company,
                    description=f'وصف {name_ar}',
                    head_of_department=self.fake.name(),
                    budget=Decimal(random.randint(200000, 1000000)),
                    is_active=True
                ))
        
        departments = Department.objects.bulk_create(departments_data)
        return departments

    def create_job_positions_bulk(self, departments):
        """إنشاء المناصب الوظيفية بشكل مجمع"""
        self.stdout.write('إنشاء المناصب الوظيفية...')
        
        job_positions_data = []
        
        job_templates = [
            ('مدير', 'Manager', 'manager', 12000, 20000),
            ('نائب مدير', 'Deputy Manager', 'senior', 10000, 15000),
            ('رئيس قسم', 'Section Head', 'senior', 8000, 12000),
            ('أخصائي أول', 'Senior Specialist', 'senior', 7000, 10000),
            ('أخصائي', 'Specialist', 'junior', 5000, 8000),
            ('مساعد إداري', 'Administrative Assistant', 'entry', 3000, 5000)
        ]
        
        for department in departments:
            for i, (name_ar, name_en, level, min_sal, max_sal) in enumerate(job_templates):
                job_positions_data.append(JobPosition(
                    name=f'{name_ar} - {department.name}',
                    name_en=f'{name_en} - {department.name_en}',
                    code=f'{department.code}_JOB{i+1:02d}',
                    department=department,
                    level=level,
                    min_salary=Decimal(min_sal),
                    max_salary=Decimal(max_sal),
                    description=f'وصف {name_ar} في {department.name}',
                    requirements='متطلبات الوظيفة',
                    responsibilities='مسؤوليات الوظيفة',
                    is_active=True
                ))
        
        job_positions = JobPosition.objects.bulk_create(job_positions_data)
        return job_positions

    def create_employees_bulk(self, companies, departments, job_positions, total_count, batch_size):
        """إنشاء الموظفين بشكل مجمع على دفعات"""
        self.stdout.write(f'إنشاء {total_count} موظف على دفعات بحجم {batch_size}...')
        
        all_employees = []
        
        # أسماء للاختبار
        first_names_male = ['أحمد', 'محمد', 'عبدالله', 'خالد', 'سعد', 'فهد', 'عمر', 'يوسف']
        first_names_female = ['فاطمة', 'عائشة', 'مريم', 'سارة', 'نورا', 'هند', 'ريم', 'أمل']
        last_names = ['الأحمد', 'المحمد', 'الخالد', 'السعد', 'الغامدي', 'العتيبي', 'الشهري', 'القحطاني']
        
        for batch_start in range(0, total_count, batch_size):
            batch_end = min(batch_start + batch_size, total_count)
            current_batch_size = batch_end - batch_start
            
            self.stdout.write(f'  معالجة الدفعة {batch_start//batch_size + 1}: الموظفين {batch_start + 1} إلى {batch_end}')
            
            batch_start_time = time.time()
            
            # إنشاء المستخدمين للدفعة
            users_data = []
            for i in range(batch_start, batch_end):
                gender = random.choice(['male', 'female'])
                first_name = random.choice(first_names_male if gender == 'male' else first_names_female)
                last_name = random.choice(last_names)
                
                users_data.append(User(
                    username=f'perf_emp_{i+1:06d}',
                    email=f'perf_emp_{i+1:06d}@company.com',
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True
                ))
            
            # إنشاء المستخدمين بشكل مجمع
            with transaction.atomic():
                created_users = User.objects.bulk_create(users_data)
                
                # تعيين كلمات المرور (يجب أن يكون بعد الإنشاء)
                for user in created_users:
                    user.set_password('password123')
                
                User.objects.bulk_update(created_users, ['password'])
            
            # إنشاء الموظفين للدفعة
            employees_data = []
            for i, user in enumerate(created_users):
                actual_index = batch_start + i
                
                # اختيار بيانات عشوائية
                company = random.choice(companies)
                company_departments = [d for d in departments if d.company == company]
                department = random.choice(company_departments)
                dept_jobs = [j for j in job_positions if j.department == department]
                job_position = random.choice(dept_jobs)
                
                gender = 'male' if user.first_name in first_names_male else 'female'
                
                salary = Decimal(random.randint(
                    int(job_position.min_salary),
                    int(job_position.max_salary)
                ))
                
                birth_date = self.fake.date_of_birth(minimum_age=22, maximum_age=60)
                hire_date = self.fake.date_between(start_date='-5y', end_date='today')
                
                employees_data.append(Employee(
                    user=user,
                    employee_id=f'PERF{actual_index+1:06d}',
                    first_name=user.first_name,
                    last_name=user.last_name,
                    first_name_en=self.fake.first_name(),
                    last_name_en=self.fake.last_name(),
                    national_id=f'{random.randint(1000000000, 2999999999)}',
                    birth_date=birth_date,
                    phone_number=f'05{random.randint(10000000, 99999999)}',
                    personal_email=f'personal{actual_index+1}@gmail.com',
                    email=f'perf_emp_{actual_index+1:06d}@{company.name.replace(" ", "").lower()}.com',
                    department=department,
                    job_position=job_position,
                    company=company,
                    hire_date=hire_date,
                    basic_salary=salary,
                    gender=gender,
                    marital_status=random.choice(['single', 'married', 'divorced']),
                    nationality='سعودي',
                    address=f'عنوان تجريبي {actual_index+1}',
                    city=random.choice(['الرياض', 'جدة', 'الدمام']),
                    emergency_contact_name=f'جهة اتصال {actual_index+1}',
                    emergency_contact_phone=f'05{random.randint(10000000, 99999999)}',
                    emergency_contact_relationship=random.choice(['والد', 'والدة', 'زوج', 'زوجة']),
                    is_active=random.choice([True, True, True, False]),  # 75% نشط
                    notes=f'ملاحظات تجريبية للموظف {actual_index+1}' if random.choice([True, False]) else ''
                ))
            
            # إنشاء الموظفين بشكل مجمع
            with transaction.atomic():
                batch_employees = Employee.objects.bulk_create(employees_data)
                all_employees.extend(batch_employees)
            
            batch_time = time.time() - batch_start_time
            
            self.stdout.write(
                f'    تم إنشاء {current_batch_size} موظف في {batch_time:.2f} ثانية '
                f'({current_batch_size/batch_time:.1f} موظف/ثانية)'
            )
        
        return all_employees

    def create_sample_attendance_data(self, employees, days=30):
        """إنشاء بيانات حضور تجريبية"""
        self.stdout.write(f'إنشاء بيانات حضور لآخر {days} يوم...')
        
        # هذا يتطلب وجود نموذج الحضور
        # يمكن إضافته لاحقاً عند توفر النموذج
        pass

    def create_sample_payroll_data(self, employees):
        """إنشاء بيانات رواتب تجريبية"""
        self.stdout.write('إنشاء بيانات رواتب تجريبية...')
        
        # هذا يتطلب وجود نموذج الرواتب
        # يمكن إضافته لاحقاً عند توفر النموذج
        pass