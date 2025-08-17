"""
أمر Django لإنشاء بيانات تجريبية شاملة لنظام الموارد البشرية
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
import random
from datetime import date, datetime, timedelta
import uuid


class Command(BaseCommand):
    help = 'إنشاء بيانات تجريبية شاملة لنظام الموارد البشرية'

    def add_arguments(self, parser):
        parser.add_argument(
            '--companies',
            type=int,
            default=3,
            help='عدد الشركات',
        )
        parser.add_argument(
            '--employees',
            type=int,
            default=50,
            help='عدد الموظفين',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='حذف البيانات الموجودة قبل إنشاء بيانات جديدة',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 بدء إنشاء البيانات التجريبية')
        )

        self.companies_count = options['companies']
        self.employees_count = options['employees']
        self.clear_existing = options['clear_existing']

        try:
            with transaction.atomic():
                if self.clear_existing:
                    self.clear_existing_data()

                # إنشاء البيانات التجريبية
                self.create_companies()
                self.create_branches()
                self.create_departments()
                self.create_job_positions()
                self.create_work_shifts()
                self.create_employees()
                self.create_employee_extended_data()
                self.create_attendance_machines()
                self.create_sample_attendance()

                self.stdout.write(
                    self.style.SUCCESS('✅ تم إنشاء البيانات التجريبية بنجاح!')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء البيانات التجريبية: {str(e)}')
            )
            raise

    def clear_existing_data(self):
        """حذف البيانات الموجودة"""
        self.stdout.write('🗑️ حذف البيانات الموجودة...')
        
        try:
            from Hr.models_enhanced import (
                Company, Branch, Department, JobPosition, Employee,
                WorkShift, AttendanceMachine, AttendanceRecord
            )
            
            # حذف البيانات بالترتيب الصحيح
            AttendanceRecord.objects.all().delete()
            AttendanceMachine.objects.all().delete()
            Employee.objects.all().delete()
            JobPosition.objects.all().delete()
            Department.objects.all().delete()
            Branch.objects.all().delete()
            WorkShift.objects.all().delete()
            Company.objects.all().delete()
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم حذف البيانات الموجودة')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ خطأ في حذف البيانات: {str(e)}')
            )

    def create_companies(self):
        """إنشاء الشركات"""
        self.stdout.write('🏢 إنشاء الشركات...')
        
        try:
            from Hr.models_enhanced import Company
            
            companies_data = [
                {
                    'name': 'شركة الدولية للتجارة',
                    'name_english': 'International Trading Company',
                    'code': 'ITC',
                    'tax_number': '1234567890',
                    'commercial_register': 'CR123456789',
                    'industry': 'التجارة',
                    'company_size': 'large',
                },
                {
                    'name': 'مؤسسة التقنية المتقدمة',
                    'name_english': 'Advanced Technology Corporation',
                    'code': 'ATC',
                    'tax_number': '2345678901',
                    'commercial_register': 'CR234567890',
                    'industry': 'التقنية',
                    'company_size': 'medium',
                },
                {
                    'name': 'شركة الخدمات الاستشارية',
                    'name_english': 'Consulting Services Company',
                    'code': 'CSC',
                    'tax_number': '3456789012',
                    'commercial_register': 'CR345678901',
                    'industry': 'الاستشارات',
                    'company_size': 'small',
                },
            ]
            
            self.companies = []
            for i, company_data in enumerate(companies_data[:self.companies_count]):
                company = Company.objects.create(
                    **company_data,
                    address=f'شارع الملك فهد، الرياض {i+1}',
                    city='الرياض',
                    country='Saudi Arabia',
                    phone=f'+966112345{i:03d}',
                    email=f'info@{company_data["code"].lower()}.com',
                    establishment_date=date(2010 + i, 1, 1),
                    is_headquarters=i == 0,
                )
                self.companies.append(company)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم إنشاء {len(self.companies)} شركة')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء الشركات: {str(e)}')
            )
            raise

    def create_branches(self):
        """إنشاء الفروع"""
        self.stdout.write('🏪 إنشاء الفروع...')
        
        try:
            from Hr.models_enhanced import Branch
            
            self.branches = []
            cities = ['الرياض', 'جدة', 'الدمام', 'مكة المكرمة', 'المدينة المنورة']
            
            for company in self.companies:
                # فرع رئيسي
                main_branch = Branch.objects.create(
                    company=company,
                    name=f'الفرع الرئيسي - {company.name}',
                    name_english=f'Main Branch - {company.name_english}',
                    code='MAIN',
                    branch_type='main',
                    address=company.address,
                    city=company.city,
                    phone=company.phone,
                    email=company.email,
                    opening_date=company.establishment_date,
                )
                self.branches.append(main_branch)
                
                # فروع إضافية
                for i, city in enumerate(cities[1:3]):  # فرعين إضافيين
                    branch = Branch.objects.create(
                        company=company,
                        name=f'فرع {city}',
                        name_english=f'{city} Branch',
                        code=f'BR{i+1:02d}',
                        branch_type='regional',
                        address=f'شارع الأمير محمد بن عبدالعزيز، {city}',
                        city=city,
                        phone=f'+966{random.randint(11, 17)}{random.randint(1000000, 9999999)}',
                        opening_date=company.establishment_date + timedelta(days=365 * (i+1)),
                    )
                    self.branches.append(branch)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم إنشاء {len(self.branches)} فرع')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء الفروع: {str(e)}')
            )
            raise

    def create_departments(self):
        """إنشاء الأقسام"""
        self.stdout.write('🏛️ إنشاء الأقسام...')
        
        try:
            from Hr.models_enhanced import Department
            
            departments_data = [
                {'name': 'الموارد البشرية', 'code': 'HR', 'type': 'hr'},
                {'name': 'المالية والمحاسبة', 'code': 'FIN', 'type': 'finance'},
                {'name': 'تقنية المعلومات', 'code': 'IT', 'type': 'technical'},
                {'name': 'المبيعات', 'code': 'SALES', 'type': 'sales'},
                {'name': 'التسويق', 'code': 'MKT', 'type': 'marketing'},
                {'name': 'العمليات', 'code': 'OPS', 'type': 'operational'},
                {'name': 'خدمة العملاء', 'code': 'CS', 'type': 'support'},
            ]
            
            self.departments = []
            for company in self.companies:
                for branch in company.branches.all():
                    for dept_data in departments_data:
                        department = Department.objects.create(
                            company=company,
                            branch=branch,
                            name=dept_data['name'],
                            code=dept_data['code'],
                            department_type=dept_data['type'],
                            description=f'قسم {dept_data["name"]} في {branch.name}',
                            budget=Decimal(random.randint(100000, 1000000)),
                        )
                        self.departments.append(department)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم إنشاء {len(self.departments)} قسم')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء الأقسام: {str(e)}')
            )
            raise

    def create_job_positions(self):
        """إنشاء المناصب الوظيفية"""
        self.stdout.write('💼 إنشاء المناصب الوظيفية...')
        
        try:
            from Hr.models_enhanced import JobPosition
            
            positions_by_dept = {
                'HR': [
                    {'title': 'مدير الموارد البشرية', 'level': 'manager', 'min_salary': 15000, 'max_salary': 25000},
                    {'title': 'أخصائي موارد بشرية', 'level': 'senior', 'min_salary': 8000, 'max_salary': 12000},
                    {'title': 'منسق موارد بشرية', 'level': 'mid', 'min_salary': 5000, 'max_salary': 8000},
                ],
                'FIN': [
                    {'title': 'مدير مالي', 'level': 'manager', 'min_salary': 18000, 'max_salary': 30000},
                    {'title': 'محاسب أول', 'level': 'senior', 'min_salary': 10000, 'max_salary': 15000},
                    {'title': 'محاسب', 'level': 'mid', 'min_salary': 6000, 'max_salary': 10000},
                ],
                'IT': [
                    {'title': 'مدير تقنية المعلومات', 'level': 'manager', 'min_salary': 20000, 'max_salary': 35000},
                    {'title': 'مطور أول', 'level': 'senior', 'min_salary': 12000, 'max_salary': 18000},
                    {'title': 'مطور', 'level': 'mid', 'min_salary': 7000, 'max_salary': 12000},
                    {'title': 'مطور مبتدئ', 'level': 'junior', 'min_salary': 4000, 'max_salary': 7000},
                ],
                'SALES': [
                    {'title': 'مدير المبيعات', 'level': 'manager', 'min_salary': 16000, 'max_salary': 28000},
                    {'title': 'مندوب مبيعات أول', 'level': 'senior', 'min_salary': 9000, 'max_salary': 14000},
                    {'title': 'مندوب مبيعات', 'level': 'mid', 'min_salary': 5500, 'max_salary': 9000},
                ],
            }
            
            self.job_positions = []
            for department in self.departments:
                dept_positions = positions_by_dept.get(department.code, [
                    {'title': f'موظف {department.name}', 'level': 'mid', 'min_salary': 5000, 'max_salary': 8000}
                ])
                
                for i, pos_data in enumerate(dept_positions):
                    position = JobPosition.objects.create(
                        company=department.company,
                        department=department,
                        title=pos_data['title'],
                        code=f'{department.code}_{i+1:02d}',
                        level=pos_data['level'],
                        category=department.department_type,
                        min_salary=Decimal(pos_data['min_salary']),
                        max_salary=Decimal(pos_data['max_salary']),
                        description=f'وصف وظيفي لمنصب {pos_data["title"]}',
                        requirements='متطلبات الوظيفة حسب المنصب',
                    )
                    self.job_positions.append(position)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم إنشاء {len(self.job_positions)} منصب وظيفي')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء المناصب الوظيفية: {str(e)}')
            )
            raise

    def create_work_shifts(self):
        """إنشاء ورديات العمل"""
        self.stdout.write('⏰ إنشاء ورديات العمل...')
        
        try:
            from Hr.models_enhanced import WorkShift
            from datetime import time
            
            shifts_data = [
                {
                    'name': 'الوردية الصباحية',
                    'code': 'MORNING',
                    'start_time': time(8, 0),
                    'end_time': time(17, 0),
                    'break_duration': timedelta(hours=1),
                },
                {
                    'name': 'الوردية المسائية',
                    'code': 'EVENING',
                    'start_time': time(14, 0),
                    'end_time': time(23, 0),
                    'break_duration': timedelta(hours=1),
                },
                {
                    'name': 'الوردية الليلية',
                    'code': 'NIGHT',
                    'start_time': time(22, 0),
                    'end_time': time(7, 0),
                    'break_duration': timedelta(hours=1),
                    'shift_type': 'night',
                },
            ]
            
            self.work_shifts = []
            for company in self.companies:
                for shift_data in shifts_data:
                    shift = WorkShift.objects.create(
                        company=company,
                        **shift_data
                    )
                    self.work_shifts.append(shift)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم إنشاء {len(self.work_shifts)} وردية عمل')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء ورديات العمل: {str(e)}')
            )
            raise

    def create_employees(self):
        """إنشاء الموظفين"""
        self.stdout.write('👥 إنشاء الموظفين...')
        
        try:
            from Hr.models_enhanced import Employee
            
            # أسماء عربية للموظفين
            first_names = [
                'أحمد', 'محمد', 'عبدالله', 'سعد', 'فهد', 'خالد', 'عبدالعزيز', 'سلطان',
                'فاطمة', 'عائشة', 'خديجة', 'مريم', 'نورا', 'سارة', 'هند', 'ريم'
            ]
            
            last_names = [
                'العتيبي', 'المطيري', 'الدوسري', 'القحطاني', 'الغامدي', 'الزهراني',
                'الشهري', 'العنزي', 'الحربي', 'الرشيد', 'آل سعود', 'الفيصل'
            ]
            
            cities = ['الرياض', 'جدة', 'الدمام', 'مكة المكرمة', 'المدينة المنورة', 'الطائف']
            
            self.employees = []
            employees_per_company = self.employees_count // len(self.companies)
            
            for company in self.companies:
                company_positions = [pos for pos in self.job_positions if pos.company == company]
                
                for i in range(employees_per_company):
                    position = random.choice(company_positions)
                    first_name = random.choice(first_names)
                    last_name = random.choice(last_names)
                    
                    # توليد رقم هوية وطنية عشوائي
                    national_id = f"{random.randint(1, 2)}{random.randint(100000000, 999999999)}"
                    
                    # توليد رقم موظف
                    employee_number = f"{company.code}{position.department.code}{i+1:04d}"
                    
                    employee = Employee.objects.create(
                        employee_number=employee_number,
                        company=company,
                        branch=position.department.branch,
                        department=position.department,
                        job_position=position,
                        first_name=first_name,
                        last_name=last_name,
                        date_of_birth=date(
                            random.randint(1980, 2000),
                            random.randint(1, 12),
                            random.randint(1, 28)
                        ),
                        gender=random.choice(['male', 'female']),
                        marital_status=random.choice(['single', 'married']),
                        nationality='Saudi',
                        national_id=national_id,
                        mobile_phone=f"+966{random.randint(500000000, 599999999)}",
                        personal_email=f"{first_name.lower()}.{last_name.lower()}@gmail.com",
                        work_email=f"{first_name.lower()}.{last_name.lower()}@{company.code.lower()}.com",
                        current_address=f"شارع {random.choice(['الملك فهد', 'الأمير محمد', 'العليا'])}",
                        current_city=random.choice(cities),
                        hire_date=date(
                            random.randint(2015, 2023),
                            random.randint(1, 12),
                            random.randint(1, 28)
                        ),
                        basic_salary=Decimal(random.randint(
                            int(position.min_salary),
                            int(position.max_salary)
                        )),
                        employment_type='full_time',
                        status='active',
                    )
                    self.employees.append(employee)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم إنشاء {len(self.employees)} موظف')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء الموظفين: {str(e)}')
            )
            raise

    def create_employee_extended_data(self):
        """إنشاء البيانات الموسعة للموظفين"""
        self.stdout.write('📚 إنشاء البيانات الموسعة للموظفين...')
        
        try:
            from Hr.models_enhanced import (
                EmployeeEducation, EmployeeInsurance, 
                EmployeeEmergencyContact, EmployeeShiftAssignment
            )
            
            # إنشاء بيانات التعليم
            degrees = ['bachelor', 'master', 'diploma', 'high_school']
            majors = ['إدارة الأعمال', 'المحاسبة', 'علوم الحاسب', 'الهندسة', 'الطب']
            institutions = ['جامعة الملك سعود', 'جامعة الملك عبدالعزيز', 'جامعة الإمام']
            
            for employee in self.employees[:20]:  # أول 20 موظف
                EmployeeEducation.objects.create(
                    employee=employee,
                    degree=random.choice(degrees),
                    major=random.choice(majors),
                    institution=random.choice(institutions),
                    graduation_year=random.randint(2000, 2020),
                    grade='very_good',
                    is_verified=True,
                )
            
            # إنشاء بيانات التأمين
            for employee in self.employees:
                EmployeeInsurance.objects.create(
                    employee=employee,
                    insurance_type='social',
                    insurance_number=f"SS{random.randint(100000000, 999999999)}",
                    provider='المؤسسة العامة للتأمينات الاجتماعية',
                    start_date=employee.hire_date,
                    subscription_date=employee.hire_date,
                    monthly_contribution=employee.basic_salary * Decimal('0.1'),
                    status='active',
                )
            
            # إنشاء جهات الاتصال الطارئة
            relationships = ['spouse', 'father', 'mother', 'brother', 'sister']
            for employee in self.employees[:30]:  # أول 30 موظف
                EmployeeEmergencyContact.objects.create(
                    employee=employee,
                    full_name=f"{random.choice(['أحمد', 'فاطمة', 'محمد', 'عائشة'])} {employee.last_name}",
                    relationship=random.choice(relationships),
                    primary_phone=f"+966{random.randint(500000000, 599999999)}",
                    is_primary=True,
                )
            
            # تعيين الورديات
            for employee in self.employees:
                company_shifts = [shift for shift in self.work_shifts if shift.company == employee.company]
                if company_shifts:
                    EmployeeShiftAssignment.objects.create(
                        employee=employee,
                        shift=random.choice(company_shifts),
                        assignment_type='permanent',
                        start_date=employee.hire_date,
                    )
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم إنشاء البيانات الموسعة للموظفين')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء البيانات الموسعة: {str(e)}')
            )

    def create_attendance_machines(self):
        """إنشاء أجهزة الحضور"""
        self.stdout.write('🖥️ إنشاء أجهزة الحضور...')
        
        try:
            from Hr.models_enhanced import AttendanceMachine
            
            machine_types = ['fingerprint', 'face_recognition', 'card_reader']
            
            for branch in self.branches:
                for i, machine_type in enumerate(machine_types):
                    AttendanceMachine.objects.create(
                        company=branch.company,
                        branch=branch,
                        name=f'جهاز الحضور {i+1}',
                        serial_number=f"{branch.code}_{machine_type.upper()}_{i+1:03d}",
                        machine_type=machine_type,
                        location=f'المدخل الرئيسي - الطابق {i+1}',
                        status='online',
                    )
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم إنشاء أجهزة الحضور')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء أجهزة الحضور: {str(e)}')
            )

    def create_sample_attendance(self):
        """إنشاء عينة من سجلات الحضور"""
        self.stdout.write('📊 إنشاء عينة من سجلات الحضور...')
        
        try:
            from Hr.models_enhanced import AttendanceRecord, AttendanceMachine
            
            machines = list(AttendanceMachine.objects.all())
            if not machines:
                return
            
            # إنشاء سجلات حضور للأسبوع الماضي
            for employee in self.employees[:10]:  # أول 10 موظفين
                machine = random.choice(machines)
                
                for days_ago in range(7):
                    record_date = date.today() - timedelta(days=days_ago)
                    
                    # سجل دخول
                    check_in_time = datetime.combine(
                        record_date,
                        datetime.strptime(f"08:{random.randint(0, 30):02d}", "%H:%M").time()
                    )
                    
                    AttendanceRecord.objects.create(
                        employee=employee,
                        machine=machine,
                        record_type='check_in',
                        timestamp=check_in_time,
                        source='machine',
                        status='valid',
                    )
                    
                    # سجل خروج
                    check_out_time = datetime.combine(
                        record_date,
                        datetime.strptime(f"17:{random.randint(0, 30):02d}", "%H:%M").time()
                    )
                    
                    AttendanceRecord.objects.create(
                        employee=employee,
                        machine=machine,
                        record_type='check_out',
                        timestamp=check_out_time,
                        source='machine',
                        status='valid',
                    )
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم إنشاء عينة من سجلات الحضور')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء سجلات الحضور: {str(e)}')
            )