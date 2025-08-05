"""
أمر توليد البيانات التجريبية
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Hr.models import Company, Branch, Department, JobPosition, Employee
from decimal import Decimal
import random
from faker import Faker
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'توليد بيانات تجريبية شاملة للنظام'

    def add_arguments(self, parser):
        parser.add_argument(
            '--employees',
            type=int,
            default=50,
            help='عدد الموظفين المراد إنشاؤهم (افتراضي: 50)'
        )
        
        parser.add_argument(
            '--companies',
            type=int,
            default=2,
            help='عدد الشركات المراد إنشاؤها (افتراضي: 2)'
        )
        
        parser.add_argument(
            '--departments',
            type=int,
            default=8,
            help='عدد الأقسام لكل شركة (افتراضي: 8)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='مسح البيانات الموجودة قبل إنشاء بيانات جديدة'
        )
        
        parser.add_argument(
            '--locale',
            default='ar_SA',
            help='اللغة المحلية لتوليد البيانات (افتراضي: ar_SA)'
        )

    def handle(self, *args, **options):
        self.fake = Faker(['ar_SA', 'en_US'])
        
        employees_count = options['employees']
        companies_count = options['companies']
        departments_count = options['departments']
        clear_data = options['clear']
        
        if clear_data:
            self.clear_existing_data()
        
        self.stdout.write(
            self.style.SUCCESS('بدء توليد البيانات التجريبية...')
        )
        
        # إنشاء الشركات
        companies = self.create_companies(companies_count)
        
        # إنشاء الفروع
        branches = self.create_branches(companies)
        
        # إنشاء الأقسام
        departments = self.create_departments(companies, departments_count)
        
        # إنشاء المناصب الوظيفية
        job_positions = self.create_job_positions(departments)
        
        # إنشاء الموظفين
        employees = self.create_employees(
            companies, departments, job_positions, employees_count
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'تم إنشاء البيانات التجريبية بنجاح:\n'
                f'  - {len(companies)} شركة\n'
                f'  - {len(branches)} فرع\n'
                f'  - {len(departments)} قسم\n'
                f'  - {len(job_positions)} منصب وظيفي\n'
                f'  - {len(employees)} موظف'
            )
        )

    def clear_existing_data(self):
        """مسح البيانات الموجودة"""
        self.stdout.write('مسح البيانات الموجودة...')
        
        Employee.objects.all().delete()
        JobPosition.objects.all().delete()
        Department.objects.all().delete()
        Branch.objects.all().delete()
        Company.objects.all().delete()
        
        # مسح المستخدمين المرتبطين بالموظفين
        User.objects.filter(username__startswith='emp_').delete()
        
        self.stdout.write(self.style.SUCCESS('تم مسح البيانات الموجودة'))

    def create_companies(self, count):
        """إنشاء الشركات"""
        self.stdout.write(f'إنشاء {count} شركة...')
        
        companies = []
        company_names = [
            'شركة الدولية للموارد البشرية',
            'شركة التقنية المتقدمة',
            'شركة الابتكار الرقمي',
            'شركة الحلول الذكية',
            'شركة التطوير المستدام'
        ]
        
        for i in range(count):
            company_name = company_names[i % len(company_names)]
            
            company = Company.objects.create(
                name=f'{company_name} {i+1}' if i > 0 else company_name,
                name_en=f'Company {i+1}',
                commercial_register=f'{1010000000 + i}',
                tax_number=f'{300000000000000 + i}',
                phone=f'011{random.randint(1000000, 9999999)}',
                email=f'info@company{i+1}.com',
                website=f'https://www.company{i+1}.com',
                address=self.fake.address(),
                city=random.choice(['الرياض', 'جدة', 'الدمام', 'مكة', 'المدينة']),
                country='المملكة العربية السعودية',
                postal_code=f'{random.randint(10000, 99999)}',
                is_active=True
            )
            companies.append(company)
        
        return companies

    def create_branches(self, companies):
        """إنشاء الفروع"""
        self.stdout.write('إنشاء الفروع...')
        
        branches = []
        cities = ['الرياض', 'جدة', 'الدمام', 'مكة', 'المدينة', 'الطائف', 'أبها', 'تبوك']
        
        for company in companies:
            # إنشاء 2-4 فروع لكل شركة
            branch_count = random.randint(2, 4)
            
            for i in range(branch_count):
                city = cities[i % len(cities)]
                
                branch = Branch.objects.create(
                    name=f'فرع {city}',
                    name_en=f'{city} Branch',
                    code=f'{city[:3].upper()}{i+1:03d}',
                    company=company,
                    address=self.fake.address(),
                    city=city,
                    phone=f'011{random.randint(1000000, 9999999)}',
                    manager_name=self.fake.name(),
                    is_active=True
                )
                branches.append(branch)
        
        return branches

    def create_departments(self, companies, departments_per_company):
        """إنشاء الأقسام"""
        self.stdout.write(f'إنشاء {departments_per_company} قسم لكل شركة...')
        
        departments = []
        department_templates = [
            {
                'name': 'قسم الموارد البشرية',
                'name_en': 'Human Resources Department',
                'code': 'HR',
                'description': 'قسم إدارة الموارد البشرية والتوظيف'
            },
            {
                'name': 'قسم تقنية المعلومات',
                'name_en': 'Information Technology Department',
                'code': 'IT',
                'description': 'قسم تطوير وصيانة الأنظمة التقنية'
            },
            {
                'name': 'قسم المالية والمحاسبة',
                'name_en': 'Finance and Accounting Department',
                'code': 'FIN',
                'description': 'قسم إدارة الشؤون المالية والمحاسبية'
            },
            {
                'name': 'قسم التسويق والمبيعات',
                'name_en': 'Marketing and Sales Department',
                'code': 'MKT',
                'description': 'قسم التسويق والمبيعات وخدمة العملاء'
            },
            {
                'name': 'قسم العمليات والإنتاج',
                'name_en': 'Operations and Production Department',
                'code': 'OPS',
                'description': 'قسم إدارة العمليات والإنتاج'
            },
            {
                'name': 'قسم الجودة والتطوير',
                'name_en': 'Quality and Development Department',
                'code': 'QD',
                'description': 'قسم ضمان الجودة والتطوير المستمر'
            },
            {
                'name': 'قسم الأمن والسلامة',
                'name_en': 'Security and Safety Department',
                'code': 'SEC',
                'description': 'قسم الأمن والسلامة المهنية'
            },
            {
                'name': 'قسم الشؤون القانونية',
                'name_en': 'Legal Affairs Department',
                'code': 'LEG',
                'description': 'قسم الشؤون القانونية والامتثال'
            }
        ]
        
        for company in companies:
            company_branches = list(company.branches.all())
            
            for i in range(min(departments_per_company, len(department_templates))):
                template = department_templates[i]
                branch = random.choice(company_branches) if company_branches else None
                
                department = Department.objects.create(
                    name=template['name'],
                    name_en=template['name_en'],
                    code=f"{template['code']}{i+1:03d}",
                    company=company,
                    branch=branch,
                    description=template['description'],
                    head_of_department=self.fake.name(),
                    budget=Decimal(random.randint(200000, 1000000)),
                    is_active=True
                )
                departments.append(department)
        
        return departments

    def create_job_positions(self, departments):
        """إنشاء المناصب الوظيفية"""
        self.stdout.write('إنشاء المناصب الوظيفية...')
        
        job_positions = []
        
        # قوالب المناصب حسب نوع القسم
        job_templates = {
            'HR': [
                {
                    'name': 'مدير الموارد البشرية',
                    'name_en': 'HR Manager',
                    'level': 'manager',
                    'min_salary': 12000, 'max_salary': 18000
                },
                {
                    'name': 'أخصائي موارد بشرية',
                    'name_en': 'HR Specialist',
                    'level': 'senior',
                    'min_salary': 8000, 'max_salary': 12000
                },
                {
                    'name': 'منسق التوظيف',
                    'name_en': 'Recruitment Coordinator',
                    'level': 'junior',
                    'min_salary': 5000, 'max_salary': 8000
                }
            ],
            'IT': [
                {
                    'name': 'مدير تقنية المعلومات',
                    'name_en': 'IT Manager',
                    'level': 'manager',
                    'min_salary': 15000, 'max_salary': 22000
                },
                {
                    'name': 'مطور برمجيات أول',
                    'name_en': 'Senior Software Developer',
                    'level': 'senior',
                    'min_salary': 10000, 'max_salary': 15000
                },
                {
                    'name': 'مطور برمجيات',
                    'name_en': 'Software Developer',
                    'level': 'junior',
                    'min_salary': 6000, 'max_salary': 10000
                },
                {
                    'name': 'أخصائي دعم تقني',
                    'name_en': 'Technical Support Specialist',
                    'level': 'junior',
                    'min_salary': 4000, 'max_salary': 7000
                }
            ],
            'FIN': [
                {
                    'name': 'مدير مالي',
                    'name_en': 'Finance Manager',
                    'level': 'manager',
                    'min_salary': 13000, 'max_salary': 20000
                },
                {
                    'name': 'محاسب أول',
                    'name_en': 'Senior Accountant',
                    'level': 'senior',
                    'min_salary': 9000, 'max_salary': 13000
                },
                {
                    'name': 'محاسب',
                    'name_en': 'Accountant',
                    'level': 'junior',
                    'min_salary': 5000, 'max_salary': 9000
                }
            ],
            'MKT': [
                {
                    'name': 'مدير التسويق',
                    'name_en': 'Marketing Manager',
                    'level': 'manager',
                    'min_salary': 11000, 'max_salary': 17000
                },
                {
                    'name': 'أخصائي تسويق',
                    'name_en': 'Marketing Specialist',
                    'level': 'senior',
                    'min_salary': 7000, 'max_salary': 11000
                },
                {
                    'name': 'منسق تسويق',
                    'name_en': 'Marketing Coordinator',
                    'level': 'junior',
                    'min_salary': 4500, 'max_salary': 7000
                }
            ]
        }
        
        # قالب افتراضي للأقسام الأخرى
        default_jobs = [
            {
                'name': 'مدير القسم',
                'name_en': 'Department Manager',
                'level': 'manager',
                'min_salary': 12000, 'max_salary': 18000
            },
            {
                'name': 'أخصائي أول',
                'name_en': 'Senior Specialist',
                'level': 'senior',
                'min_salary': 8000, 'max_salary': 12000
            },
            {
                'name': 'أخصائي',
                'name_en': 'Specialist',
                'level': 'junior',
                'min_salary': 5000, 'max_salary': 8000
            }
        ]
        
        for department in departments:
            # تحديد نوع القسم من الكود
            dept_type = department.code[:3] if len(department.code) >= 3 else 'DEFAULT'
            
            # اختيار القوالب المناسبة
            templates = job_templates.get(dept_type, default_jobs)
            
            for i, template in enumerate(templates):
                job_position = JobPosition.objects.create(
                    name=template['name'],
                    name_en=template['name_en'],
                    code=f"{department.code}_JOB{i+1:02d}",
                    department=department,
                    level=template['level'],
                    min_salary=Decimal(template['min_salary']),
                    max_salary=Decimal(template['max_salary']),
                    description=f"وصف {template['name']} في {department.name}",
                    requirements=self.generate_job_requirements(template['level']),
                    responsibilities=self.generate_job_responsibilities(template['name']),
                    is_active=True
                )
                job_positions.append(job_position)
        
        return job_positions

    def create_employees(self, companies, departments, job_positions, count):
        """إنشاء الموظفين"""
        self.stdout.write(f'إنشاء {count} موظف...')
        
        employees = []
        
        # أسماء عربية للموظفين
        arabic_first_names_male = [
            'أحمد', 'محمد', 'عبدالله', 'عبدالرحمن', 'خالد', 'سعد', 'فهد', 'عبدالعزيز',
            'ناصر', 'سلطان', 'عمر', 'يوسف', 'إبراهيم', 'عبدالمجيد', 'طلال', 'بندر'
        ]
        
        arabic_first_names_female = [
            'فاطمة', 'عائشة', 'خديجة', 'مريم', 'زينب', 'سارة', 'نورا', 'هند',
            'ريم', 'لجين', 'شهد', 'رغد', 'أمل', 'نوال', 'منى', 'سمر'
        ]
        
        arabic_last_names = [
            'الأحمد', 'المحمد', 'العبدالله', 'الخالد', 'السعد', 'الغامدي', 'العتيبي',
            'الشهري', 'القحطاني', 'الدوسري', 'المطيري', 'الحربي', 'الزهراني', 'العنزي'
        ]
        
        for i in range(count):
            # اختيار الجنس عشوائياً
            gender = random.choice(['male', 'female'])
            
            # اختيار الاسم حسب الجنس
            if gender == 'male':
                first_name = random.choice(arabic_first_names_male)
            else:
                first_name = random.choice(arabic_first_names_female)
            
            last_name = random.choice(arabic_last_names)
            
            # إنشاء مستخدم Django
            username = f'emp_{i+1:04d}'
            user = User.objects.create_user(
                username=username,
                email=f'{username}@company.com',
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            
            # اختيار شركة وقسم ومنصب عشوائياً
            company = random.choice(companies)
            company_departments = [d for d in departments if d.company == company]
            department = random.choice(company_departments)
            
            dept_job_positions = [j for j in job_positions if j.department == department]
            job_position = random.choice(dept_job_positions)
            
            # توليد راتب ضمن النطاق المحدد
            salary = Decimal(random.randint(
                int(job_position.min_salary),
                int(job_position.max_salary)
            ))
            
            # توليد تاريخ ميلاد وتوظيف
            birth_date = self.fake.date_of_birth(minimum_age=22, maximum_age=60)
            hire_date = self.fake.date_between(start_date='-5y', end_date='today')
            
            # إنشاء الموظف
            employee = Employee.objects.create(
                user=user,
                employee_id=f'EMP{i+1:04d}',
                first_name=first_name,
                last_name=last_name,
                first_name_en=self.fake.first_name(),
                last_name_en=self.fake.last_name(),
                national_id=f'{random.randint(1000000000, 2999999999)}',
                birth_date=birth_date,
                phone_number=f'05{random.randint(10000000, 99999999)}',
                personal_email=f'{first_name.lower()}.{last_name.lower().replace("ال", "")}@gmail.com',
                email=f'{username}@{company.name.replace(" ", "").lower()}.com',
                department=department,
                job_position=job_position,
                company=company,
                hire_date=hire_date,
                basic_salary=salary,
                gender=gender,
                marital_status=random.choice(['single', 'married', 'divorced', 'widowed']),
                nationality='سعودي',
                address=self.fake.address(),
                city=random.choice(['الرياض', 'جدة', 'الدمام', 'مكة', 'المدينة']),
                emergency_contact_name=self.fake.name(),
                emergency_contact_phone=f'05{random.randint(10000000, 99999999)}',
                emergency_contact_relationship=random.choice(['والد', 'والدة', 'زوج', 'زوجة', 'أخ', 'أخت']),
                is_active=random.choice([True, True, True, True, False]),  # 80% نشط
                notes=self.fake.text(max_nb_chars=200) if random.choice([True, False]) else ''
            )
            employees.append(employee)
        
        return employees

    def generate_job_requirements(self, level):
        """توليد متطلبات الوظيفة"""
        base_requirements = [
            'بكالوريوس في التخصص ذي العلاقة',
            'إجادة اللغة الإنجليزية',
            'مهارات التواصل الفعال',
            'القدرة على العمل ضمن فريق'
        ]
        
        if level == 'manager':
            base_requirements.extend([
                'خبرة لا تقل عن 7 سنوات',
                'مهارات قيادية متميزة',
                'خبرة في إدارة الفرق'
            ])
        elif level == 'senior':
            base_requirements.extend([
                'خبرة لا تقل عن 4 سنوات',
                'مهارات تحليلية قوية'
            ])
        else:  # junior
            base_requirements.extend([
                'خبرة لا تقل عن سنتين',
                'الرغبة في التعلم والتطوير'
            ])
        
        return ', '.join(base_requirements)

    def generate_job_responsibilities(self, job_name):
        """توليد مسؤوليات الوظيفة"""
        common_responsibilities = [
            'تنفيذ المهام المطلوبة بكفاءة عالية',
            'التعاون مع أعضاء الفريق',
            'إعداد التقارير الدورية',
            'المشاركة في اجتماعات القسم'
        ]
        
        if 'مدير' in job_name:
            common_responsibilities.extend([
                'قيادة وإدارة فريق العمل',
                'وضع الخطط الاستراتيجية',
                'متابعة تنفيذ المشاريع',
                'تقييم أداء الموظفين'
            ])
        
        return ', '.join(common_responsibilities)