"""
Base Test Fixtures for ElDawliya System
=====================================

This module provides comprehensive test fixtures for all system models.
It includes realistic Arabic data for testing purposes.
"""

import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

# Initialize Faker with Arabic locale
fake = Faker(['ar_SA', 'en_US'])
fake_ar = Faker('ar_SA')
fake_en = Faker('en_US')

User = get_user_model()


class BaseFixtureGenerator:
    """Base class for generating test fixtures"""
    
    def __init__(self):
        self.fake = fake
        self.fake_ar = fake_ar
        self.fake_en = fake_en
        self.created_objects = {}
    
    def generate_arabic_name(self):
        """Generate realistic Arabic names"""
        first_names = [
            'محمد', 'أحمد', 'علي', 'حسن', 'عبدالله', 'خالد', 'سعد', 'فهد', 'عبدالعزيز', 'ناصر',
            'فاطمة', 'عائشة', 'خديجة', 'مريم', 'زينب', 'نورا', 'سارة', 'هند', 'رقية', 'أسماء'
        ]
        
        second_names = [
            'عبدالرحمن', 'عبدالله', 'محمد', 'أحمد', 'علي', 'حسن', 'حسين', 'عمر', 'يوسف', 'إبراهيم'
        ]
        
        third_names = [
            'محمد', 'أحمد', 'علي', 'حسن', 'عبدالله', 'عبدالعزيز', 'عبدالرحمن', 'سعد', 'فهد', 'خالد'
        ]
        
        last_names = [
            'الأحمد', 'المحمد', 'العلي', 'الحسن', 'السعد', 'الفهد', 'الخالد', 'الناصر', 'العبدالله', 'الحربي',
            'العتيبي', 'القحطاني', 'الغامدي', 'الزهراني', 'الشهري', 'العمري', 'المطيري', 'الدوسري', 'الرشيد', 'السلمان'
        ]
        
        return {
            'first_name': random.choice(first_names),
            'second_name': random.choice(second_names),
            'third_name': random.choice(third_names),
            'last_name': random.choice(last_names)
        }
    
    def generate_department_names(self):
        """Generate Arabic department names"""
        return [
            'إدارة الموارد البشرية',
            'إدارة المالية والمحاسبة',
            'إدارة تقنية المعلومات',
            'إدارة المشاريع',
            'إدارة المخازن والمشتريات',
            'إدارة التسويق والمبيعات',
            'إدارة الجودة',
            'إدارة الصيانة',
            'الإدارة القانونية',
            'إدارة العلاقات العامة'
        ]
    
    def generate_job_titles(self):
        """Generate Arabic job titles"""
        return [
            'مدير عام',
            'مدير إدارة',
            'نائب مدير',
            'رئيس قسم',
            'مشرف',
            'موظف أول',
            'موظف',
            'محاسب',
            'مبرمج',
            'مهندس',
            'فني',
            'سكرتير',
            'مساعد إداري',
            'أخصائي',
            'مستشار'
        ]
    
    def generate_product_names(self):
        """Generate Arabic product names"""
        return [
            'ورق A4',
            'أقلام حبر جاف',
            'دباسة مكتبية',
            'مجلدات ملفات',
            'آلة حاسبة',
            'شاشة كمبيوتر',
            'لوحة مفاتيح',
            'فأرة كمبيوتر',
            'طابعة ليزر',
            'خرطوشة حبر',
            'كابل شبكة',
            'مفتاح كهربائي',
            'مصباح LED',
            'كرسي مكتب',
            'طاولة اجتماعات',
            'خزانة ملفات',
            'سبورة بيضاء',
            'جهاز عرض',
            'هاتف مكتبي',
            'آلة تصوير'
        ]
    
    def generate_supplier_names(self):
        """Generate Arabic supplier names"""
        return [
            'شركة الرياض للمكتبيات',
            'مؤسسة الخليج التجارية',
            'شركة النور للتقنية',
            'مكتبة الفهد التجارية',
            'شركة الأمل للمعدات',
            'مؤسسة الشرق للتوريدات',
            'شركة الوطن للخدمات',
            'مكتب الإبداع التجاري',
            'شركة المستقبل للتقنية',
            'مؤسسة الازدهار التجارية'
        ]
    
    def generate_meeting_topics(self):
        """Generate Arabic meeting topics"""
        return [
            'مراجعة الأداء الشهري',
            'مناقشة الميزانية السنوية',
            'تطوير النظام الإلكتروني',
            'تقييم المشاريع الجارية',
            'مراجعة السياسات الإدارية',
            'تخطيط التدريب السنوي',
            'مناقشة خطة التوسع',
            'مراجعة إجراءات الأمان',
            'تقييم الموردين',
            'مناقشة التحديثات التقنية'
        ]
    
    def generate_task_descriptions(self):
        """Generate Arabic task descriptions"""
        return [
            'إعداد التقرير الشهري للمبيعات',
            'مراجعة وتحديث قاعدة البيانات',
            'تنظيم ورشة عمل للموظفين الجدد',
            'إجراء جرد شامل للمخزون',
            'تطوير نظام إدارة المهام',
            'مراجعة عقود الموردين',
            'إعداد خطة التسويق الرقمي',
            'تحديث إجراءات الأمان والسلامة',
            'تدريب الموظفين على النظام الجديد',
            'إعداد دراسة جدوى للمشروع الجديد'
        ]
    
    def generate_random_date(self, start_date=None, end_date=None):
        """Generate random date within range"""
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today() + timedelta(days=365)
        
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        
        return start_date + timedelta(days=random_days)
    
    def generate_random_datetime(self, start_date=None, end_date=None):
        """Generate random datetime within range"""
        random_date = self.generate_random_date(start_date, end_date)
        random_time = self.fake.time()
        
        return timezone.make_aware(
            datetime.combine(random_date, random_time)
        )
    
    def generate_phone_number(self):
        """Generate Saudi phone number"""
        prefixes = ['050', '053', '054', '055', '056', '057', '058', '059']
        prefix = random.choice(prefixes)
        number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return f"{prefix}{number}"
    
    def generate_national_id(self):
        """Generate Saudi national ID"""
        # Saudi national ID starts with 1 or 2
        first_digit = random.choice(['1', '2'])
        remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        return f"{first_digit}{remaining_digits}"
    
    def generate_email(self, name_parts):
        """Generate email based on name"""
        domains = ['company.com', 'eldawliya.com', 'office.sa', 'work.sa']
        domain = random.choice(domains)
        
        # Use English transliteration for email
        username = f"{name_parts['first_name']}.{name_parts['last_name']}".lower()
        # Simple transliteration (in real scenario, use proper transliteration library)
        username = username.replace('محمد', 'mohammed').replace('أحمد', 'ahmed').replace('علي', 'ali')
        username = f"user{random.randint(1000, 9999)}"  # Simplified for testing
        
        return f"{username}@{domain}"
    
    def generate_address(self):
        """Generate Arabic address"""
        streets = [
            'شارع الملك فهد',
            'شارع الأمير محمد بن عبدالعزيز',
            'شارع العليا',
            'شارع التحلية',
            'شارع الورود',
            'شارع النخيل',
            'شارع الأندلس',
            'شارع الملقا',
            'شارع الصحافة',
            'شارع الرياض'
        ]
        
        districts = [
            'حي العليا',
            'حي الملقا',
            'حي الورود',
            'حي النخيل',
            'حي الصحافة',
            'حي السليمانية',
            'حي الملز',
            'حي الروضة',
            'حي المرسلات',
            'حي الندى'
        ]
        
        cities = [
            'الرياض',
            'جدة',
            'الدمام',
            'مكة المكرمة',
            'المدينة المنورة',
            'الطائف',
            'تبوك',
            'بريدة',
            'خميس مشيط',
            'حائل'
        ]
        
        street = random.choice(streets)
        district = random.choice(districts)
        city = random.choice(cities)
        building_no = random.randint(1, 999)
        
        return f"{street}، {district}، {city} {building_no}"


class UserFixtures(BaseFixtureGenerator):
    """Generate user fixtures"""
    
    def create_users(self, count=20):
        """Create test users"""
        users = []
        
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@eldawliya.com',
                password='admin123',
                first_name='مدير',
                last_name='النظام'
            )
            users.append(admin)
        
        # Create regular users
        for i in range(count):
            name_parts = self.generate_arabic_name()
            username = f"user{i+1:03d}"
            
            user = User.objects.create_user(
                username=username,
                email=self.generate_email(name_parts),
                password='password123',
                first_name=name_parts['first_name'],
                last_name=name_parts['last_name'],
                is_active=True,
                is_staff=random.choice([True, False])
            )
            users.append(user)
        
        self.created_objects['users'] = users
        return users


class OrganizationFixtures(BaseFixtureGenerator):
    """Generate organization structure fixtures"""
    
    def create_branches(self, count=5):
        """Create branch fixtures"""
        from org.models import Branch
        
        branches = []
        branch_names = [
            'الفرع الرئيسي - الرياض',
            'فرع جدة',
            'فرع الدمام',
            'فرع مكة المكرمة',
            'فرع المدينة المنورة'
        ]
        
        for i in range(min(count, len(branch_names))):
            branch = Branch.objects.create(
                branch_name=branch_names[i],
                branch_code=f"BR{i+1:03d}",
                address=self.generate_address(),
                phone=self.generate_phone_number(),
                is_active=True
            )
            branches.append(branch)
        
        self.created_objects['branches'] = branches
        return branches
    
    def create_departments(self, count=10):
        """Create department fixtures"""
        from org.models import Department
        
        departments = []
        dept_names = self.generate_department_names()
        
        for i in range(min(count, len(dept_names))):
            department = Department.objects.create(
                dept_name=dept_names[i],
                dept_code=f"DEPT{i+1:03d}",
                description=f"وصف {dept_names[i]}",
                is_active=True
            )
            departments.append(department)
        
        self.created_objects['departments'] = departments
        return departments
    
    def create_job_positions(self, count=15):
        """Create job position fixtures"""
        from org.models import Job
        
        jobs = []
        job_titles = self.generate_job_titles()
        
        for i in range(min(count, len(job_titles))):
            job = Job.objects.create(
                job_title=job_titles[i],
                job_code=f"JOB{i+1:03d}",
                description=f"وصف وظيفة {job_titles[i]}",
                is_active=True
            )
            jobs.append(job)
        
        self.created_objects['jobs'] = jobs
        return jobs


class EmployeeFixtures(BaseFixtureGenerator):
    """Generate employee fixtures"""
    
    def create_employees(self, count=50):
        """Create employee fixtures"""
        from employees.models import Employee
        from org.models import Branch, Department, Job
        
        # Ensure we have required related objects
        branches = list(Branch.objects.all())
        departments = list(Department.objects.all())
        jobs = list(Job.objects.all())
        
        if not branches or not departments or not jobs:
            raise ValueError("Must create branches, departments, and jobs before creating employees")
        
        employees = []
        
        for i in range(count):
            name_parts = self.generate_arabic_name()
            
            # Generate hire date (within last 5 years)
            hire_date = self.generate_random_date(
                start_date=date.today() - timedelta(days=1825),
                end_date=date.today()
            )
            
            # Generate birth date (between 22-60 years old)
            birth_date = self.generate_random_date(
                start_date=date.today() - timedelta(days=60*365),
                end_date=date.today() - timedelta(days=22*365)
            )
            
            employee = Employee.objects.create(
                emp_code=f"EMP{i+1:04d}",
                first_name=name_parts['first_name'],
                second_name=name_parts['second_name'],
                third_name=name_parts['third_name'],
                last_name=name_parts['last_name'],
                gender=random.choice(['M', 'F']),
                birth_date=birth_date,
                nationality='سعودي',
                national_id=self.generate_national_id(),
                mobile=self.generate_phone_number(),
                email=self.generate_email(name_parts),
                address=self.generate_address(),
                hire_date=hire_date,
                join_date=hire_date + timedelta(days=random.randint(0, 30)),
                job=random.choice(jobs),
                dept=random.choice(departments),
                branch=random.choice(branches),
                emp_status=random.choice(['Active', 'Active', 'Active', 'Inactive', 'On Leave']),  # Weighted towards Active
            )
            employees.append(employee)
        
        # Set some employees as managers
        managers = random.sample(employees[:20], 10)  # Select 10 managers from first 20 employees
        for manager in managers:
            # Assign 3-8 subordinates to each manager
            subordinates = random.sample(
                [emp for emp in employees if emp != manager and emp.manager is None],
                random.randint(3, min(8, len(employees) - 1))
            )
            for subordinate in subordinates:
                subordinate.manager = manager
                subordinate.save()
        
        self.created_objects['employees'] = employees
        return employees


class InventoryFixtures(BaseFixtureGenerator):
    """Generate inventory fixtures"""
    
    def create_categories(self, count=10):
        """Create product categories"""
        from inventory.models import TblCategories
        
        categories = []
        category_names = [
            'مكتبيات',
            'أجهزة كمبيوتر',
            'أثاث مكتبي',
            'مواد كهربائية',
            'مواد تنظيف',
            'قرطاسية',
            'معدات شبكات',
            'أجهزة طباعة',
            'مواد صيانة',
            'معدات أمان'
        ]
        
        for i in range(min(count, len(category_names))):
            category = TblCategories.objects.create(
                cat_id=i+1,
                cat_name=category_names[i]
            )
            categories.append(category)
        
        self.created_objects['categories'] = categories
        return categories
    
    def create_units(self, count=8):
        """Create product units"""
        from inventory.models import TblUnitsSpareparts
        
        units = []
        unit_names = ['قطعة', 'كيلو', 'متر', 'لتر', 'علبة', 'حزمة', 'صندوق', 'رول']
        
        for i in range(min(count, len(unit_names))):
            unit = TblUnitsSpareparts.objects.create(
                unit_id=i+1,
                unit_name=unit_names[i]
            )
            units.append(unit)
        
        self.created_objects['units'] = units
        return units
    
    def create_suppliers(self, count=10):
        """Create suppliers"""
        from inventory.models import TblSuppliers
        
        suppliers = []
        supplier_names = self.generate_supplier_names()
        
        for i in range(min(count, len(supplier_names))):
            supplier = TblSuppliers.objects.create(
                supplier_id=i+1,
                supplier_name=supplier_names[i]
            )
            suppliers.append(supplier)
        
        self.created_objects['suppliers'] = suppliers
        return suppliers
    
    def create_products(self, count=100):
        """Create products"""
        from inventory.models import TblProducts, TblCategories, TblUnitsSpareparts
        
        categories = list(TblCategories.objects.all())
        units = list(TblUnitsSpareparts.objects.all())
        
        if not categories or not units:
            raise ValueError("Must create categories and units before creating products")
        
        products = []
        product_names = self.generate_product_names()
        
        for i in range(count):
            product_name = random.choice(product_names)
            if i >= len(product_names):
                product_name = f"{product_name} - نوع {i+1}"
            
            category = random.choice(categories)
            unit = random.choice(units)
            
            product = TblProducts.objects.create(
                product_id=f"PRD{i+1:04d}",
                product_name=product_name,
                initial_balance=Decimal(str(random.randint(0, 1000))),
                elwarad=Decimal(str(random.randint(0, 500))),
                mortagaaomalaa=Decimal(str(random.randint(0, 200))),
                elmonsarf=Decimal(str(random.randint(0, 300))),
                mortagaaelmawarden=Decimal(str(random.randint(0, 100))),
                qte_in_stock=Decimal(str(random.randint(10, 500))),
                cat=category,
                cat_name=category.cat_name,
                unit=unit,
                unit_name=unit.unit_name,
                minimum_threshold=Decimal(str(random.randint(5, 50))),
                maximum_threshold=Decimal(str(random.randint(100, 1000))),
                unit_price=Decimal(str(random.uniform(10.0, 1000.0))),
                location=f"مخزن {random.choice(['A', 'B', 'C'])}-{random.randint(1, 20)}",
                expiry_warning=random.choice(['نعم', 'لا'])
            )
            products.append(product)
        
        self.created_objects['products'] = products
        return products


class MeetingFixtures(BaseFixtureGenerator):
    """Generate meeting fixtures"""
    
    def create_meetings(self, count=30):
        """Create meeting fixtures"""
        from meetings.models import Meeting, Attendee
        from accounts.models import Users_Login_New
        
        users = list(Users_Login_New.objects.all())
        if not users:
            raise ValueError("Must create users before creating meetings")
        
        meetings = []
        topics = self.generate_meeting_topics()
        
        for i in range(count):
            # Generate meeting date (within last 6 months to next 3 months)
            meeting_date = self.generate_random_datetime(
                start_date=date.today() - timedelta(days=180),
                end_date=date.today() + timedelta(days=90)
            )
            
            topic = random.choice(topics)
            if i >= len(topics):
                topic = f"{topic} - جلسة {i+1}"
            
            meeting = Meeting.objects.create(
                title=f"اجتماع {topic}",
                date=meeting_date,
                topic=topic,
                status=random.choice(['pending', 'completed', 'cancelled']),
                created_by=random.choice(users)
            )
            
            # Add attendees (3-10 people per meeting)
            attendee_count = random.randint(3, min(10, len(users)))
            attendees = random.sample(users, attendee_count)
            
            for attendee_user in attendees:
                Attendee.objects.create(
                    meeting=meeting,
                    user=attendee_user
                )
            
            meetings.append(meeting)
        
        self.created_objects['meetings'] = meetings
        return meetings


class TaskFixtures(BaseFixtureGenerator):
    """Generate task fixtures"""
    
    def create_task_categories(self, count=8):
        """Create task categories"""
        from tasks.models import TaskCategory
        
        categories = []
        category_data = [
            ('إدارية', '#3498db', 'fas fa-briefcase'),
            ('تقنية', '#e74c3c', 'fas fa-laptop-code'),
            ('مالية', '#f39c12', 'fas fa-dollar-sign'),
            ('موارد بشرية', '#9b59b6', 'fas fa-users'),
            ('مشاريع', '#1abc9c', 'fas fa-project-diagram'),
            ('صيانة', '#34495e', 'fas fa-tools'),
            ('تدريب', '#27ae60', 'fas fa-graduation-cap'),
            ('أخرى', '#95a5a6', 'fas fa-tasks')
        ]
        
        for i, (name, color, icon) in enumerate(category_data[:count]):
            category = TaskCategory.objects.create(
                name=name,
                description=f"تصنيف المهام الخاصة بـ {name}",
                color=color,
                icon=icon,
                is_active=True
            )
            categories.append(category)
        
        self.created_objects['task_categories'] = categories
        return categories
    
    def create_tasks(self, count=100):
        """Create task fixtures"""
        from tasks.models import Task, TaskCategory
        from meetings.models import Meeting
        from accounts.models import Users_Login_New
        
        users = list(Users_Login_New.objects.all())
        categories = list(TaskCategory.objects.all())
        meetings = list(Meeting.objects.all())
        
        if not users:
            raise ValueError("Must create users before creating tasks")
        
        tasks = []
        descriptions = self.generate_task_descriptions()
        
        for i in range(count):
            # Generate task dates
            start_date = self.generate_random_datetime(
                start_date=date.today() - timedelta(days=90),
                end_date=date.today() + timedelta(days=30)
            )
            
            end_date = start_date + timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23)
            )
            
            description = random.choice(descriptions)
            if i >= len(descriptions):
                description = f"{description} - مرحلة {i+1}"
            
            task = Task.objects.create(
                title=f"مهمة {i+1}: {description[:30]}...",
                description=description,
                assigned_to=random.choice(users),
                created_by=random.choice(users),
                category=random.choice(categories) if categories else None,
                meeting=random.choice(meetings) if meetings and random.choice([True, False]) else None,
                priority=random.choice(['low', 'medium', 'high', 'urgent']),
                status=random.choice(['pending', 'in_progress', 'completed', 'canceled']),
                start_date=start_date,
                end_date=end_date,
                is_private=random.choice([True, False]),
                progress=random.randint(0, 100)
            )
            tasks.append(task)
        
        self.created_objects['tasks'] = tasks
        return tasks


class PurchaseOrderFixtures(BaseFixtureGenerator):
    """Generate purchase order fixtures"""
    
    def create_vendors(self, count=15):
        """Create vendor fixtures"""
        from Purchase_orders.models import Vendor
        
        vendors = []
        vendor_names = self.generate_supplier_names()
        
        for i in range(min(count, len(vendor_names))):
            vendor = Vendor.objects.create(
                name=vendor_names[i],
                contact_person=f"مدير المبيعات - {vendor_names[i]}",
                phone=self.generate_phone_number(),
                email=f"sales{i+1}@vendor{i+1}.com",
                address=self.generate_address()
            )
            vendors.append(vendor)
        
        self.created_objects['vendors'] = vendors
        return vendors
    
    def create_purchase_requests(self, count=50):
        """Create purchase request fixtures"""
        from Purchase_orders.models import PurchaseRequest, PurchaseRequestItem, Vendor
        from inventory.models import TblProducts
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        users = list(User.objects.all())
        vendors = list(Vendor.objects.all())
        products = list(TblProducts.objects.all())
        
        if not users or not vendors or not products:
            raise ValueError("Must create users, vendors, and products before creating purchase requests")
        
        requests = []
        
        for i in range(count):
            request_date = self.generate_random_datetime(
                start_date=date.today() - timedelta(days=180),
                end_date=date.today()
            )
            
            request = PurchaseRequest.objects.create(
                request_number=f"PR{i+1:04d}",
                requested_by=random.choice(users),
                vendor=random.choice(vendors),
                status=random.choice(['pending', 'approved', 'rejected', 'completed']),
                notes=f"طلب شراء رقم {i+1} - ملاحظات إضافية"
            )
            
            # Add items to the request (1-10 items per request)
            item_count = random.randint(1, 10)
            request_products = random.sample(products, min(item_count, len(products)))
            
            for product in request_products:
                PurchaseRequestItem.objects.create(
                    purchase_request=request,
                    product=product,
                    quantity_requested=Decimal(str(random.randint(1, 100))),
                    status=random.choice(['pending', 'approved', 'rejected', 'transferred']),
                    notes=f"طلب {product.product_name}"
                )
            
            requests.append(request)
        
        self.created_objects['purchase_requests'] = requests
        return requests


class AttendanceFixtures(BaseFixtureGenerator):
    """Generate attendance fixtures"""
    
    def create_attendance_records(self, count=1000):
        """Create attendance records for employees"""
        from attendance.models import EmployeeAttendance
        from employees.models import Employee
        
        employees = list(Employee.objects.filter(emp_status='Active'))
        if not employees:
            raise ValueError("Must create active employees before creating attendance records")
        
        attendance_records = []
        
        # Generate attendance for the last 90 days
        for days_back in range(90):
            attendance_date = date.today() - timedelta(days=days_back)
            
            # Skip weekends (Friday and Saturday in Saudi Arabia)
            if attendance_date.weekday() in [4, 5]:  # Friday=4, Saturday=5
                continue
            
            # Each employee has 85% chance of attendance
            for employee in employees:
                if random.random() < 0.85:  # 85% attendance rate
                    # Generate realistic check-in/out times
                    check_in_hour = random.randint(7, 9)
                    check_in_minute = random.randint(0, 59)
                    check_out_hour = random.randint(15, 18)
                    check_out_minute = random.randint(0, 59)
                    
                    check_in_time = datetime.combine(
                        attendance_date,
                        datetime.min.time().replace(hour=check_in_hour, minute=check_in_minute)
                    )
                    check_out_time = datetime.combine(
                        attendance_date,
                        datetime.min.time().replace(hour=check_out_hour, minute=check_out_minute)
                    )
                    
                    # Determine status based on check-in time
                    if check_in_hour <= 8:
                        status = 'Present'
                    elif check_in_hour <= 9:
                        status = 'Late'
                    else:
                        status = 'Very Late'
                    
                    attendance = EmployeeAttendance.objects.create(
                        employee=employee,
                        att_date=attendance_date,
                        check_in=timezone.make_aware(check_in_time),
                        check_out=timezone.make_aware(check_out_time),
                        status=status,
                        working_hours=Decimal(str((check_out_hour - check_in_hour) + (check_out_minute - check_in_minute) / 60)),
                        overtime_hours=Decimal(str(max(0, (check_out_hour - 17) + (check_out_minute / 60)))),
                        notes=f"حضور {status.lower()}" if status != 'Present' else ''
                    )
                    attendance_records.append(attendance)
        
        self.created_objects['attendance_records'] = attendance_records
        return attendance_records


class PayrollFixtures(BaseFixtureGenerator):
    """Generate payroll fixtures"""
    
    def create_salary_structures(self):
        """Create salary structures for different job levels"""
        from payrolls.models import SalaryStructure, SalaryComponent
        
        structures = []
        
        # Define salary structures by job level
        salary_data = [
            {
                'name': 'هيكل راتب الإدارة العليا',
                'basic_salary': Decimal('15000.00'),
                'allowances': {
                    'housing_allowance': Decimal('5000.00'),
                    'transport_allowance': Decimal('1500.00'),
                    'communication_allowance': Decimal('500.00'),
                    'management_allowance': Decimal('3000.00')
                }
            },
            {
                'name': 'هيكل راتب الإدارة الوسطى',
                'basic_salary': Decimal('10000.00'),
                'allowances': {
                    'housing_allowance': Decimal('3000.00'),
                    'transport_allowance': Decimal('1000.00'),
                    'communication_allowance': Decimal('300.00'),
                    'supervision_allowance': Decimal('1500.00')
                }
            },
            {
                'name': 'هيكل راتب الموظفين',
                'basic_salary': Decimal('6000.00'),
                'allowances': {
                    'housing_allowance': Decimal('2000.00'),
                    'transport_allowance': Decimal('800.00'),
                    'communication_allowance': Decimal('200.00')
                }
            }
        ]
        
        for struct_data in salary_data:
            structure = SalaryStructure.objects.create(
                name=struct_data['name'],
                basic_salary=struct_data['basic_salary'],
                is_active=True
            )
            
            # Create salary components
            for component_name, amount in struct_data['allowances'].items():
                SalaryComponent.objects.create(
                    salary_structure=structure,
                    component_name=component_name.replace('_', ' ').title(),
                    component_type='allowance',
                    amount=amount,
                    is_taxable=True
                )
            
            structures.append(structure)
        
        self.created_objects['salary_structures'] = structures
        return structures
    
    def create_payroll_records(self, count=200):
        """Create payroll records for employees"""
        from payrolls.models import PayrollRecord, PayrollItem
        from employees.models import Employee
        
        employees = list(Employee.objects.filter(emp_status='Active'))
        if not employees:
            raise ValueError("Must create employees before creating payroll records")
        
        payroll_records = []
        
        # Generate payroll for the last 6 months
        for month_back in range(6):
            payroll_date = date.today().replace(day=1) - timedelta(days=30 * month_back)
            
            for employee in employees[:count]:
                # Calculate basic salary based on job level
                if 'مدير' in employee.job.job_title:
                    basic_salary = Decimal(str(random.randint(12000, 18000)))
                elif 'رئيس' in employee.job.job_title or 'مشرف' in employee.job.job_title:
                    basic_salary = Decimal(str(random.randint(8000, 12000)))
                else:
                    basic_salary = Decimal(str(random.randint(5000, 8000)))
                
                # Calculate allowances
                housing_allowance = basic_salary * Decimal('0.25')
                transport_allowance = Decimal(str(random.randint(800, 1500)))
                
                # Calculate deductions
                insurance_deduction = basic_salary * Decimal('0.09')  # 9% social insurance
                tax_deduction = max(Decimal('0'), (basic_salary - Decimal('3000')) * Decimal('0.05'))  # 5% tax on amount over 3000
                
                gross_salary = basic_salary + housing_allowance + transport_allowance
                total_deductions = insurance_deduction + tax_deduction
                net_salary = gross_salary - total_deductions
                
                payroll_record = PayrollRecord.objects.create(
                    employee=employee,
                    payroll_date=payroll_date,
                    basic_salary=basic_salary,
                    gross_salary=gross_salary,
                    total_deductions=total_deductions,
                    net_salary=net_salary,
                    status='processed'
                )
                
                # Create payroll items
                items_data = [
                    ('الراتب الأساسي', 'earning', basic_salary),
                    ('بدل السكن', 'earning', housing_allowance),
                    ('بدل المواصلات', 'earning', transport_allowance),
                    ('التأمينات الاجتماعية', 'deduction', insurance_deduction),
                    ('ضريبة الدخل', 'deduction', tax_deduction)
                ]
                
                for item_name, item_type, amount in items_data:
                    if amount > 0:
                        PayrollItem.objects.create(
                            payroll_record=payroll_record,
                            item_name=item_name,
                            item_type=item_type,
                            amount=amount
                        )
                
                payroll_records.append(payroll_record)
        
        self.created_objects['payroll_records'] = payroll_records
        return payroll_records


class LeaveFixtures(BaseFixtureGenerator):
    """Generate leave management fixtures"""
    
    def create_leave_types(self):
        """Create different types of leaves"""
        from leaves.models import LeaveType
        
        leave_types_data = [
            {
                'name': 'إجازة سنوية',
                'days_per_year': 30,
                'max_consecutive_days': 15,
                'requires_approval': True,
                'is_paid': True
            },
            {
                'name': 'إجازة مرضية',
                'days_per_year': 120,
                'max_consecutive_days': 30,
                'requires_approval': True,
                'is_paid': True
            },
            {
                'name': 'إجازة طارئة',
                'days_per_year': 5,
                'max_consecutive_days': 3,
                'requires_approval': True,
                'is_paid': False
            },
            {
                'name': 'إجازة أمومة',
                'days_per_year': 70,
                'max_consecutive_days': 70,
                'requires_approval': False,
                'is_paid': True
            },
            {
                'name': 'إجازة حج',
                'days_per_year': 15,
                'max_consecutive_days': 15,
                'requires_approval': True,
                'is_paid': True
            }
        ]
        
        leave_types = []
        for leave_data in leave_types_data:
            leave_type = LeaveType.objects.create(**leave_data)
            leave_types.append(leave_type)
        
        self.created_objects['leave_types'] = leave_types
        return leave_types
    
    def create_leave_requests(self, count=100):
        """Create leave requests for employees"""
        from leaves.models import LeaveRequest, LeaveType
        from employees.models import Employee
        
        employees = list(Employee.objects.filter(emp_status='Active'))
        leave_types = list(LeaveType.objects.all())
        
        if not employees or not leave_types:
            raise ValueError("Must create employees and leave types first")
        
        leave_requests = []
        
        for i in range(count):
            employee = random.choice(employees)
            leave_type = random.choice(leave_types)
            
            # Generate leave dates (within last 6 months to next 3 months)
            start_date = self.generate_random_date(
                start_date=date.today() - timedelta(days=180),
                end_date=date.today() + timedelta(days=90)
            )
            
            # Duration based on leave type
            if leave_type.name == 'إجازة أمومة':
                duration = 70
            elif leave_type.name == 'إجازة حج':
                duration = 15
            else:
                duration = random.randint(1, min(leave_type.max_consecutive_days, 10))
            
            end_date = start_date + timedelta(days=duration - 1)
            
            leave_request = LeaveRequest.objects.create(
                employee=employee,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                days_requested=duration,
                reason=f"طلب {leave_type.name} - {i+1}",
                status=random.choices(
                    ['pending', 'approved', 'rejected', 'cancelled'],
                    weights=[30, 50, 15, 5]
                )[0],
                applied_date=start_date - timedelta(days=random.randint(1, 30))
            )
            
            leave_requests.append(leave_request)
        
        self.created_objects['leave_requests'] = leave_requests
        return leave_requests


class ComprehensiveFixtureGenerator:
    """Main class to generate all fixtures in proper order"""
    
    def __init__(self):
        self.generators = {
            'users': UserFixtures(),
            'organization': OrganizationFixtures(),
            'employees': EmployeeFixtures(),
            'inventory': InventoryFixtures(),
            'meetings': MeetingFixtures(),
            'tasks': TaskFixtures(),
            'purchase_orders': PurchaseOrderFixtures(),
            'attendance': AttendanceFixtures(),
            'payroll': PayrollFixtures(),
            'leaves': LeaveFixtures(),
        }
        self.created_objects = {}
    
    def generate_all_fixtures(self, 
                            users_count=25,
                            employees_count=50,
                            products_count=100,
                            meetings_count=30,
                            tasks_count=100,
                            purchase_requests_count=50,
                            attendance_days=90,
                            payroll_months=6):
        """Generate all fixtures in proper dependency order"""
        
        print("🚀 بدء إنشاء البيانات التجريبية...")
        
        # 1. Create users first
        print("👥 إنشاء المستخدمين...")
        users = self.generators['users'].create_users(users_count)
        self.created_objects['users'] = users
        
        # 2. Create organization structure
        print("🏢 إنشاء الهيكل التنظيمي...")
        branches = self.generators['organization'].create_branches()
        departments = self.generators['organization'].create_departments()
        jobs = self.generators['organization'].create_job_positions()
        
        # 3. Create employees
        print("👨‍💼 إنشاء الموظفين...")
        employees = self.generators['employees'].create_employees(employees_count)
        
        # 4. Create inventory structure
        print("📦 إنشاء بيانات المخزون...")
        categories = self.generators['inventory'].create_categories()
        units = self.generators['inventory'].create_units()
        suppliers = self.generators['inventory'].create_suppliers()
        products = self.generators['inventory'].create_products(products_count)
        
        # 5. Create meetings
        print("🤝 إنشاء الاجتماعات...")
        meetings = self.generators['meetings'].create_meetings(meetings_count)
        
        # 6. Create tasks
        print("📋 إنشاء المهام...")
        task_categories = self.generators['tasks'].create_task_categories()
        tasks = self.generators['tasks'].create_tasks(tasks_count)
        
        # 7. Create purchase orders
        print("🛒 إنشاء طلبات الشراء...")
        vendors = self.generators['purchase_orders'].create_vendors()
        purchase_requests = self.generators['purchase_orders'].create_purchase_requests(purchase_requests_count)
        
        # 8. Create HR-related data
        print("💼 إنشاء بيانات الموارد البشرية...")
        
        # Create attendance records
        print("  📅 إنشاء سجلات الحضور...")
        attendance_records = self.generators['attendance'].create_attendance_records()
        
        # Create payroll data
        print("  💰 إنشاء بيانات الرواتب...")
        salary_structures = self.generators['payroll'].create_salary_structures()
        payroll_records = self.generators['payroll'].create_payroll_records()
        
        # Create leave management data
        print("  🏖️ إنشاء بيانات الإجازات...")
        leave_types = self.generators['leaves'].create_leave_types()
        leave_requests = self.generators['leaves'].create_leave_requests()
        
        # Collect all created objects
        self.created_objects.update({
            'branches': branches,
            'departments': departments,
            'jobs': jobs,
            'employees': employees,
            'categories': categories,
            'units': units,
            'suppliers': suppliers,
            'products': products,
            'meetings': meetings,
            'task_categories': task_categories,
            'tasks': tasks,
            'vendors': vendors,
            'purchase_requests': purchase_requests,
            'attendance_records': attendance_records,
            'salary_structures': salary_structures,
            'payroll_records': payroll_records,
            'leave_types': leave_types,
            'leave_requests': leave_requests,
        })
        
        print("✅ تم إنشاء جميع البيانات التجريبية بنجاح!")
        self.print_summary()
        
        return self.created_objects
    
    def print_summary(self):
        """Print summary of created objects"""
        print("\n📊 ملخص البيانات المُنشأة:")
        print("=" * 50)
        
        summary_items = [
            ('المستخدمين', 'users'),
            ('الفروع', 'branches'),
            ('الأقسام', 'departments'),
            ('الوظائف', 'jobs'),
            ('الموظفين', 'employees'),
            ('فئات المنتجات', 'categories'),
            ('وحدات القياس', 'units'),
            ('الموردين', 'suppliers'),
            ('المنتجات', 'products'),
            ('الاجتماعات', 'meetings'),
            ('فئات المهام', 'task_categories'),
            ('المهام', 'tasks'),
            ('موردي الشراء', 'vendors'),
            ('طلبات الشراء', 'purchase_requests'),
            ('سجلات الحضور', 'attendance_records'),
            ('هياكل الرواتب', 'salary_structures'),
            ('سجلات الرواتب', 'payroll_records'),
            ('أنواع الإجازات', 'leave_types'),
            ('طلبات الإجازات', 'leave_requests'),
        ]
        
        for arabic_name, key in summary_items:
            count = len(self.created_objects.get(key, []))
            if count > 0:
                print(f"  • {arabic_name}: {count}")
        
        print("=" * 50)
        print("🎉 جميع البيانات جاهزة للاختبار!")


def run_comprehensive_fixture_generation():
    """Main function to run comprehensive fixture generation"""
    print("🚀 بدء إنشاء البيانات التجريبية الشاملة...")
    
    generator = ComprehensiveFixtureGenerator()
    
    with transaction.atomic():
        created_objects = generator.generate_all_fixtures(
            users_count=30,
            employees_count=75,
            products_count=150,
            meetings_count=40,
            tasks_count=150,
            purchase_requests_count=75
        )
    
    print("✅ تم إنشاء جميع البيانات التجريبية بنجاح!")
    return created_objects


if __name__ == "__main__":
    run_comprehensive_fixture_generation()se_orders'].create_purchase_requests(purchase_requests_count)
        
        # Collect all created objects
        self.created_objects.update({
            'users': users,
            'branches': branches,
            'departments': departments,
            'jobs': jobs,
            'employees': employees,
            'categories': categories,
            'units': units,
            'suppliers': suppliers,
            'products': products,
            'meetings': meetings,
            'task_categories': task_categories,
            'tasks': tasks,
            'vendors': vendors,
            'purchase_requests': purchase_requests,
        })
        
        print("✅ تم إنشاء جميع البيانات التجريبية بنجاح!")
        self.print_summary()
        
        return self.created_objects
    
    def print_summary(self):
        """Print summary of created objects"""
        print("\n📊 ملخص البيانات المُنشأة:")
        print("=" * 50)
        
        summary_items = [
            ('المستخدمين', len(self.created_objects.get('users', []))),
            ('الفروع', len(self.created_objects.get('branches', []))),
            ('الأقسام', len(self.created_objects.get('departments', []))),
            ('الوظائف', len(self.created_objects.get('jobs', []))),
            ('الموظفين', len(self.created_objects.get('employees', []))),
            ('فئات المنتجات', len(self.created_objects.get('categories', []))),
            ('وحدات القياس', len(self.created_objects.get('units', []))),
            ('الموردين', len(self.created_objects.get('suppliers', []))),
            ('المنتجات', len(self.created_objects.get('products', []))),
            ('الاجتماعات', len(self.created_objects.get('meetings', []))),
            ('فئات المهام', len(self.created_objects.get('task_categories', []))),
            ('المهام', len(self.created_objects.get('tasks', []))),
            ('موردي الشراء', len(self.created_objects.get('vendors', []))),
            ('طلبات الشراء', len(self.created_objects.get('purchase_requests', []))),
        ]
        
        for item_name, count in summary_items:
            print(f"• {item_name}: {count}")
        
        print("=" * 50)
        print("🎉 البيانات جاهزة للاختبار والتدريب!")