"""
Specialized Test Scenarios Generator
===================================

This module creates specialized test scenarios for different use cases:
- Training scenarios with step-by-step workflows
- Demo scenarios for presentations
- Load testing scenarios with realistic data patterns
- Edge case scenarios for testing system limits
"""

import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from tests.fixtures.base_fixtures import BaseFixtureGenerator

User = get_user_model()


class TrainingScenarioGenerator(BaseFixtureGenerator):
    """Generate training scenarios with guided workflows"""
    
    def __init__(self):
        super().__init__()
        self.training_data = {}
    
    def create_hr_training_scenario(self):
        """Create HR training scenario with complete employee lifecycle"""
        print("👨‍🎓 إنشاء سيناريو تدريب الموارد البشرية...")
        
        # Create training users
        hr_manager = User.objects.create_user(
            username='hr_manager',
            email='hr.manager@training.com',
            password='training123',
            first_name='مدير',
            last_name='الموارد البشرية'
        )
        
        hr_specialist = User.objects.create_user(
            username='hr_specialist',
            email='hr.specialist@training.com',
            password='training123',
            first_name='أخصائي',
            last_name='موارد بشرية'
        )
        
        # Create organizational structure for training
        from org.models import Branch, Department, Job
        
        training_branch = Branch.objects.create(
            branch_name='فرع التدريب - الرياض',
            branch_code='TR001',
            address='شارع الملك فهد، الرياض',
            phone='0112345678',
            is_active=True
        )
        
        hr_department = Department.objects.create(
            dept_name='إدارة الموارد البشرية',
            dept_code='HR001',
            description='قسم إدارة الموارد البشرية والتدريب',
            is_active=True
        )
        
        manager_job = Job.objects.create(
            job_title='مدير موارد بشرية',
            job_code='MGR001',
            description='مسؤول عن إدارة جميع شؤون الموظفين',
            is_active=True
        )
        
        specialist_job = Job.objects.create(
            job_title='أخصائي موارد بشرية',
            job_code='SPE001',
            description='مسؤول عن تنفيذ سياسات الموارد البشرية',
            is_active=True
        )
        
        # Create sample employees for training
        from employees.models import Employee
        
        training_employees = []
        
        # New employee (for onboarding training)
        new_employee = Employee.objects.create(
            emp_code='TRN001',
            first_name='أحمد',
            second_name='محمد',
            third_name='علي',
            last_name='السعد',
            gender='M',
            birth_date=date(1990, 5, 15),
            nationality='سعودي',
            national_id='1234567890',
            mobile='0501234567',
            email='ahmed.alsaad@training.com',
            address='حي النخيل، الرياض',
            hire_date=date.today(),
            join_date=date.today(),
            job=specialist_job,
            dept=hr_department,
            branch=training_branch,
            emp_status='Active'
        )
        training_employees.append(new_employee)
        
        # Employee requesting leave (for leave management training)
        leave_employee = Employee.objects.create(
            emp_code='TRN002',
            first_name='فاطمة',
            second_name='عبدالله',
            third_name='أحمد',
            last_name='الحربي',
            gender='F',
            birth_date=date(1985, 8, 20),
            nationality='سعودي',
            national_id='2345678901',
            mobile='0507654321',
            email='fatima.alharbi@training.com',
            address='حي الملقا، الرياض',
            hire_date=date.today() - timedelta(days=365),
            join_date=date.today() - timedelta(days=365),
            job=specialist_job,
            dept=hr_department,
            branch=training_branch,
            emp_status='Active'
        )
        training_employees.append(leave_employee)
        
        # Employee with performance issues (for evaluation training)
        performance_employee = Employee.objects.create(
            emp_code='TRN003',
            first_name='خالد',
            second_name='سعد',
            third_name='محمد',
            last_name='العتيبي',
            gender='M',
            birth_date=date(1988, 12, 10),
            nationality='سعودي',
            national_id='3456789012',
            mobile='0509876543',
            email='khalid.alotaibi@training.com',
            address='حي العليا، الرياض',
            hire_date=date.today() - timedelta(days=730),
            join_date=date.today() - timedelta(days=730),
            job=specialist_job,
            dept=hr_department,
            branch=training_branch,
            emp_status='Active'
        )
        training_employees.append(performance_employee)
        
        # Create leave requests for training
        from leaves.models import LeaveType, LeaveRequest
        
        # Create leave types if they don't exist
        annual_leave, _ = LeaveType.objects.get_or_create(
            name='إجازة سنوية',
            defaults={
                'days_per_year': 30,
                'max_consecutive_days': 15,
                'requires_approval': True,
                'is_paid': True
            }
        )
        
        sick_leave, _ = LeaveType.objects.get_or_create(
            name='إجازة مرضية',
            defaults={
                'days_per_year': 120,
                'max_consecutive_days': 30,
                'requires_approval': True,
                'is_paid': True
            }
        )
        
        # Create sample leave request
        leave_request = LeaveRequest.objects.create(
            employee=leave_employee,
            leave_type=annual_leave,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=37),
            days_requested=7,
            reason='إجازة سنوية للراحة والاستجمام',
            status='pending',
            applied_date=date.today()
        )
        
        # Create attendance records for training
        from attendance.models import EmployeeAttendance
        
        # Create attendance for the last 30 days
        for days_back in range(30):
            att_date = date.today() - timedelta(days=days_back)
            
            # Skip weekends
            if att_date.weekday() in [4, 5]:
                continue
            
            for employee in training_employees:
                # Create varied attendance patterns for training
                if employee == performance_employee:
                    # Performance employee has attendance issues
                    if random.random() < 0.7:  # 70% attendance
                        status = random.choice(['Late', 'Very Late', 'Present'])
                        check_in_hour = random.randint(8, 10)
                    else:
                        continue  # Absent
                else:
                    # Good employees
                    status = 'Present'
                    check_in_hour = random.randint(7, 8)
                
                check_in_time = datetime.combine(
                    att_date,
                    datetime.min.time().replace(hour=check_in_hour, minute=random.randint(0, 59))
                )
                check_out_time = check_in_time + timedelta(hours=8, minutes=random.randint(0, 60))
                
                EmployeeAttendance.objects.create(
                    employee=employee,
                    att_date=att_date,
                    check_in=timezone.make_aware(check_in_time),
                    check_out=timezone.make_aware(check_out_time),
                    status=status,
                    working_hours=Decimal('8.0'),
                    overtime_hours=Decimal('0.0'),
                    notes=f'حضور {status}' if status != 'Present' else ''
                )
        
        self.training_data['hr_scenario'] = {
            'users': [hr_manager, hr_specialist],
            'branch': training_branch,
            'department': hr_department,
            'jobs': [manager_job, specialist_job],
            'employees': training_employees,
            'leave_request': leave_request,
            'description': 'سيناريو تدريب شامل لإدارة الموارد البشرية'
        }
        
        print("✅ تم إنشاء سيناريو تدريب الموارد البشرية")
        return self.training_data['hr_scenario']
    
    def create_inventory_training_scenario(self):
        """Create inventory training scenario with stock management workflows"""
        print("📦 إنشاء سيناريو تدريب إدارة المخزون...")
        
        # Create inventory training users
        inventory_manager = User.objects.create_user(
            username='inv_manager',
            email='inventory.manager@training.com',
            password='training123',
            first_name='مدير',
            last_name='المخزون'
        )
        
        warehouse_keeper = User.objects.create_user(
            username='warehouse_keeper',
            email='warehouse.keeper@training.com',
            password='training123',
            first_name='أمين',
            last_name='المخزن'
        )
        
        # Create inventory structure for training
        from inventory.models import TblCategories, TblUnitsSpareparts, TblSuppliers, TblProducts
        
        # Categories
        office_supplies = TblCategories.objects.create(
            cat_id=100,
            cat_name='مكتبيات'
        )
        
        computer_equipment = TblCategories.objects.create(
            cat_id=101,
            cat_name='معدات حاسوب'
        )
        
        # Units
        piece_unit = TblUnitsSpareparts.objects.create(
            unit_id=100,
            unit_name='قطعة'
        )
        
        box_unit = TblUnitsSpareparts.objects.create(
            unit_id=101,
            unit_name='علبة'
        )
        
        # Suppliers
        supplier1 = TblSuppliers.objects.create(
            supplier_id=100,
            supplier_name='شركة المكتبيات المتقدمة'
        )
        
        supplier2 = TblSuppliers.objects.create(
            supplier_id=101,
            supplier_name='مؤسسة التقنية الحديثة'
        )
        
        # Products with different stock levels for training scenarios
        training_products = []
        
        # Low stock product (for reorder training)
        low_stock_product = TblProducts.objects.create(
            product_id='TRN-LOW-001',
            product_name='ورق A4 أبيض',
            initial_balance=Decimal('100'),
            elwarad=Decimal('50'),
            mortagaaomalaa=Decimal('0'),
            elmonsarf=Decimal('45'),
            mortagaaelmawarden=Decimal('0'),
            qte_in_stock=Decimal('5'),  # Low stock
            cat=office_supplies,
            cat_name=office_supplies.cat_name,
            unit=box_unit,
            unit_name=box_unit.unit_name,
            minimum_threshold=Decimal('10'),
            maximum_threshold=Decimal('200'),
            unit_price=Decimal('25.50'),
            location='مخزن A-01',
            expiry_warning='لا'
        )
        training_products.append(low_stock_product)
        
        # Overstocked product (for optimization training)
        overstock_product = TblProducts.objects.create(
            product_id='TRN-HIGH-001',
            product_name='أقلام حبر جاف زرقاء',
            initial_balance=Decimal('200'),
            elwarad=Decimal('500'),
            mortagaaomalaa=Decimal('0'),
            elmonsarf=Decimal('50'),
            mortagaaelmawarden=Decimal('0'),
            qte_in_stock=Decimal('650'),  # Overstock
            cat=office_supplies,
            cat_name=office_supplies.cat_name,
            unit=piece_unit,
            unit_name=piece_unit.unit_name,
            minimum_threshold=Decimal('50'),
            maximum_threshold=Decimal('300'),
            unit_price=Decimal('2.75'),
            location='مخزن A-02',
            expiry_warning='لا'
        )
        training_products.append(overstock_product)
        
        # Normal stock product
        normal_product = TblProducts.objects.create(
            product_id='TRN-NOR-001',
            product_name='شاشة كمبيوتر 24 بوصة',
            initial_balance=Decimal('20'),
            elwarad=Decimal('15'),
            mortagaaomalaa=Decimal('0'),
            elmonsarf=Decimal('10'),
            mortagaaelmawarden=Decimal('0'),
            qte_in_stock=Decimal('25'),
            cat=computer_equipment,
            cat_name=computer_equipment.cat_name,
            unit=piece_unit,
            unit_name=piece_unit.unit_name,
            minimum_threshold=Decimal('5'),
            maximum_threshold=Decimal('50'),
            unit_price=Decimal('850.00'),
            location='مخزن B-01',
            expiry_warning='لا'
        )
        training_products.append(normal_product)
        
        # Create purchase requests for training
        from Purchase_orders.models import Vendor, PurchaseRequest, PurchaseRequestItem
        
        # Create vendor
        training_vendor = Vendor.objects.create(
            name='مورد التدريب المحدود',
            contact_person='مدير المبيعات',
            phone='0112345678',
            email='sales@training-vendor.com',
            address='شارع التجارة، الرياض'
        )
        
        # Create purchase request for low stock item
        purchase_request = PurchaseRequest.objects.create(
            request_number='PR-TRN-001',
            requested_by=inventory_manager,
            vendor=training_vendor,
            status='pending',
            notes='طلب شراء عاجل لتجديد المخزون المنخفض'
        )
        
        # Add items to purchase request
        PurchaseRequestItem.objects.create(
            purchase_request=purchase_request,
            product=low_stock_product,
            quantity_requested=Decimal('100'),
            status='pending',
            notes='مطلوب بشكل عاجل - المخزون منخفض'
        )
        
        self.training_data['inventory_scenario'] = {
            'users': [inventory_manager, warehouse_keeper],
            'categories': [office_supplies, computer_equipment],
            'units': [piece_unit, box_unit],
            'suppliers': [supplier1, supplier2],
            'products': training_products,
            'vendor': training_vendor,
            'purchase_request': purchase_request,
            'description': 'سيناريو تدريب شامل لإدارة المخزون والمشتريات'
        }
        
        print("✅ تم إنشاء سيناريو تدريب إدارة المخزون")
        return self.training_data['inventory_scenario']
    
    def create_project_management_training_scenario(self):
        """Create project management training scenario"""
        print("📋 إنشاء سيناريو تدريب إدارة المشاريع...")
        
        # Create project management users
        project_manager = User.objects.create_user(
            username='project_manager',
            email='project.manager@training.com',
            password='training123',
            first_name='مدير',
            last_name='المشاريع'
        )
        
        team_lead = User.objects.create_user(
            username='team_lead',
            email='team.lead@training.com',
            password='training123',
            first_name='قائد',
            last_name='الفريق'
        )
        
        developer1 = User.objects.create_user(
            username='developer1',
            email='dev1@training.com',
            password='training123',
            first_name='مطور',
            last_name='أول'
        )
        
        developer2 = User.objects.create_user(
            username='developer2',
            email='dev2@training.com',
            password='training123',
            first_name='مطور',
            last_name='ثاني'
        )
        
        # Create project meeting
        from meetings.models import Meeting, Attendee
        
        project_meeting = Meeting.objects.create(
            title='اجتماع بدء مشروع تطوير النظام الإلكتروني',
            date=timezone.now() + timedelta(days=2),
            topic='مناقشة متطلبات وخطة تطوير النظام الإلكتروني الجديد للشركة',
            status='pending',
            created_by=project_manager
        )
        
        # Add attendees
        attendees = [project_manager, team_lead, developer1, developer2]
        for attendee in attendees:
            Attendee.objects.create(meeting=project_meeting, user=attendee)
        
        # Create project tasks with different statuses and priorities
        from tasks.models import Task, TaskCategory, TaskStep
        
        # Create task category
        development_category = TaskCategory.objects.create(
            name='تطوير البرمجيات',
            description='مهام تطوير وبرمجة الأنظمة',
            color='#3498db',
            icon='fas fa-code',
            is_active=True
        )
        
        # Create training tasks
        training_tasks = []
        
        # Task 1: Requirements Analysis (High Priority, Pending)
        task1 = Task.objects.create(
            title='تحليل المتطلبات الوظيفية للنظام',
            description='تحليل وتوثيق جميع المتطلبات الوظيفية وغير الوظيفية للنظام الجديد',
            assigned_to=team_lead,
            created_by=project_manager,
            category=development_category,
            meeting=project_meeting,
            priority='high',
            status='pending',
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=8),
            progress=0,
            is_private=False
        )
        training_tasks.append(task1)
        
        # Add steps to task 1
        task1_steps = [
            'مراجعة النظام الحالي وتحديد نقاط القوة والضعف',
            'إجراء مقابلات مع أصحاب المصلحة',
            'توثيق المتطلبات الوظيفية',
            'مراجعة وتأكيد المتطلبات مع الإدارة'
        ]
        
        for step_desc in task1_steps:
            TaskStep.objects.create(
                task=task1,
                description=step_desc,
                created_by=team_lead,
                is_completed=False
            )
        
        # Task 2: Database Design (Medium Priority, In Progress)
        task2 = Task.objects.create(
            title='تصميم قاعدة البيانات',
            description='تصميم هيكل قاعدة البيانات وإنشاء المخططات اللازمة',
            assigned_to=developer1,
            created_by=project_manager,
            category=development_category,
            meeting=project_meeting,
            priority='medium',
            status='in_progress',
            start_date=timezone.now() + timedelta(days=5),
            end_date=timezone.now() + timedelta(days=15),
            progress=35,
            is_private=False
        )
        training_tasks.append(task2)
        
        # Task 3: UI Development (Low Priority, Completed)
        task3 = Task.objects.create(
            title='تطوير واجهة المستخدم الأساسية',
            description='تطوير الواجهات الأساسية للنظام مع دعم اللغة العربية',
            assigned_to=developer2,
            created_by=project_manager,
            category=development_category,
            priority='low',
            status='completed',
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=3),
            progress=100,
            is_private=False
        )
        training_tasks.append(task3)
        
        # Task 4: Testing (Urgent Priority, Pending)
        task4 = Task.objects.create(
            title='اختبار النظام الشامل',
            description='إجراء اختبارات شاملة للنظام قبل النشر',
            assigned_to=team_lead,
            created_by=project_manager,
            category=development_category,
            priority='urgent',
            status='pending',
            start_date=timezone.now() + timedelta(days=20),
            end_date=timezone.now() + timedelta(days=30),
            progress=0,
            is_private=False
        )
        training_tasks.append(task4)
        
        self.training_data['project_scenario'] = {
            'users': [project_manager, team_lead, developer1, developer2],
            'meeting': project_meeting,
            'category': development_category,
            'tasks': training_tasks,
            'description': 'سيناريو تدريب شامل لإدارة المشاريع والمهام'
        }
        
        print("✅ تم إنشاء سيناريو تدريب إدارة المشاريع")
        return self.training_data['project_scenario']
    
    def generate_complete_training_environment(self):
        """Generate complete training environment with all scenarios"""
        print("🎓 إنشاء بيئة التدريب الكاملة...")
        
        with transaction.atomic():
            hr_scenario = self.create_hr_training_scenario()
            inventory_scenario = self.create_inventory_training_scenario()
            project_scenario = self.create_project_management_training_scenario()
        
        complete_training = {
            'hr_scenario': hr_scenario,
            'inventory_scenario': inventory_scenario,
            'project_scenario': project_scenario,
            'description': 'بيئة تدريب شاملة لجميع وحدات النظام'
        }
        
        self.print_training_summary(complete_training)
        
        print("✅ تم إنشاء بيئة التدريب الكاملة بنجاح!")
        return complete_training
    
    def print_training_summary(self, training_data):
        """Print summary of training scenarios"""
        print("\n📚 ملخص بيئة التدريب:")
        print("=" * 60)
        
        print("👥 المستخدمين المُنشأين للتدريب:")
        all_users = []
        for scenario_name, scenario_data in training_data.items():
            if scenario_name != 'description' and 'users' in scenario_data:
                all_users.extend(scenario_data['users'])
        
        for user in all_users:
            print(f"  • {user.first_name} {user.last_name} ({user.username})")
        
        print(f"\n📊 إجمالي البيانات المُنشأة:")
        print(f"  • المستخدمين: {len(all_users)}")
        print(f"  • السيناريوهات: {len([k for k in training_data.keys() if k != 'description'])}")
        
        print("\n🔑 معلومات تسجيل الدخول:")
        print("  كلمة المرور لجميع المستخدمين: training123")
        
        print("=" * 60)
        print("🎉 بيئة التدريب جاهزة للاستخدام!")


class DemoScenarioGenerator(BaseFixtureGenerator):
    """Generate demo scenarios for presentations and showcases"""
    
    def __init__(self):
        super().__init__()
        self.demo_data = {}
    
    def create_executive_dashboard_demo(self):
        """Create demo data for executive dashboard presentation"""
        print("📊 إنشاء بيانات العرض التوضيحي للوحة التحكم التنفيذية...")
        
        # Create realistic data for the last 12 months
        from django.db import connection
        
        # Generate monthly statistics
        monthly_stats = []
        for month_back in range(12):
            month_date = date.today().replace(day=1) - timedelta(days=30 * month_back)
            
            # Simulate realistic business patterns
            base_employees = 150 + month_back * 2  # Growing company
            base_revenue = 500000 + random.randint(-50000, 100000)  # Fluctuating revenue
            
            monthly_stats.append({
                'month': month_date.strftime('%Y-%m'),
                'active_employees': base_employees,
                'new_hires': random.randint(2, 8),
                'resignations': random.randint(0, 3),
                'revenue': base_revenue,
                'expenses': int(base_revenue * 0.7),
                'projects_completed': random.randint(3, 12),
                'customer_satisfaction': random.uniform(4.2, 4.8)
            })
        
        # Store in temporary table for demo
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS demo_monthly_stats (
                    month TEXT PRIMARY KEY,
                    active_employees INTEGER,
                    new_hires INTEGER,
                    resignations INTEGER,
                    revenue INTEGER,
                    expenses INTEGER,
                    projects_completed INTEGER,
                    customer_satisfaction REAL
                )
            """)
            
            for stat in monthly_stats:
                cursor.execute("""
                    INSERT OR REPLACE INTO demo_monthly_stats 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    stat['month'], stat['active_employees'], stat['new_hires'],
                    stat['resignations'], stat['revenue'], stat['expenses'],
                    stat['projects_completed'], stat['customer_satisfaction']
                ])
        
        self.demo_data['executive_dashboard'] = {
            'monthly_stats': monthly_stats,
            'description': 'بيانات العرض التوضيحي للوحة التحكم التنفيذية'
        }
        
        print("✅ تم إنشاء بيانات العرض التوضيحي للوحة التحكم")
        return self.demo_data['executive_dashboard']
    
    def create_success_story_demo(self):
        """Create a success story demo with before/after scenarios"""
        print("🏆 إنشاء قصة نجاح توضيحية...")
        
        # Create "before" scenario - inefficient processes
        before_scenario = {
            'manual_processes': 15,
            'paper_forms': 25,
            'processing_time_hours': 48,
            'error_rate_percent': 12,
            'employee_satisfaction': 3.2,
            'cost_per_process': 150
        }
        
        # Create "after" scenario - with ElDawliya system
        after_scenario = {
            'automated_processes': 12,
            'digital_forms': 23,
            'processing_time_hours': 4,
            'error_rate_percent': 2,
            'employee_satisfaction': 4.6,
            'cost_per_process': 45
        }
        
        # Calculate improvements
        improvements = {
            'time_saved_percent': ((before_scenario['processing_time_hours'] - after_scenario['processing_time_hours']) / before_scenario['processing_time_hours']) * 100,
            'error_reduction_percent': ((before_scenario['error_rate_percent'] - after_scenario['error_rate_percent']) / before_scenario['error_rate_percent']) * 100,
            'cost_savings_percent': ((before_scenario['cost_per_process'] - after_scenario['cost_per_process']) / before_scenario['cost_per_process']) * 100,
            'satisfaction_improvement': after_scenario['employee_satisfaction'] - before_scenario['employee_satisfaction']
        }
        
        self.demo_data['success_story'] = {
            'before': before_scenario,
            'after': after_scenario,
            'improvements': improvements,
            'description': 'قصة نجاح توضيحية لتأثير نظام الدولية'
        }
        
        print("✅ تم إنشاء قصة النجاح التوضيحية")
        return self.demo_data['success_story']


class EdgeCaseScenarioGenerator(BaseFixtureGenerator):
    """Generate edge case scenarios for testing system limits"""
    
    def __init__(self):
        super().__init__()
        self.edge_cases = {}
    
    def create_data_limit_scenarios(self):
        """Create scenarios that test data limits and edge cases"""
        print("⚠️ إنشاء سيناريوهات الحالات الحدية...")
        
        # Create users with edge case data
        edge_users = []
        
        # User with very long names
        long_name_user = User.objects.create_user(
            username='very_long_username_that_tests_limits',
            email='very.long.email.address.that.tests.database.limits@company.com',
            password='edge123',
            first_name='اسم_طويل_جداً_يختبر_حدود_قاعدة_البيانات_والنظام',
            last_name='عائلة_طويلة_جداً_تختبر_حدود_النظام_والعرض'
        )
        edge_users.append(long_name_user)
        
        # User with special characters
        special_char_user = User.objects.create_user(
            username='special_chars_user',
            email='special@test.com',
            password='edge123',
            first_name='أحمد-محمد_علي',
            last_name='الأحمد&الثاني'
        )
        edge_users.append(special_char_user)
        
        # Create products with edge case values
        from inventory.models import TblCategories, TblUnitsSpareparts, TblProducts
        
        # Category for edge cases
        edge_category = TblCategories.objects.create(
            cat_id=999,
            cat_name='فئة اختبار الحالات الحدية'
        )
        
        edge_unit = TblUnitsSpareparts.objects.create(
            unit_id=999,
            unit_name='وحدة اختبار'
        )
        
        # Product with zero stock
        zero_stock_product = TblProducts.objects.create(
            product_id='EDGE-ZERO-001',
            product_name='منتج برصيد صفر',
            initial_balance=Decimal('0'),
            elwarad=Decimal('0'),
            mortagaaomalaa=Decimal('0'),
            elmonsarf=Decimal('0'),
            mortagaaelmawarden=Decimal('0'),
            qte_in_stock=Decimal('0'),
            cat=edge_category,
            cat_name=edge_category.cat_name,
            unit=edge_unit,
            unit_name=edge_unit.unit_name,
            minimum_threshold=Decimal('0'),
            maximum_threshold=Decimal('0'),
            unit_price=Decimal('0.01'),
            location='مخزن اختبار',
            expiry_warning='نعم'
        )
        
        # Product with very high values
        high_value_product = TblProducts.objects.create(
            product_id='EDGE-HIGH-001',
            product_name='منتج بقيم عالية جداً',
            initial_balance=Decimal('999999.99'),
            elwarad=Decimal('999999.99'),
            mortagaaomalaa=Decimal('0'),
            elmonsarf=Decimal('100000.00'),
            mortagaaelmawarden=Decimal('0'),
            qte_in_stock=Decimal('899999.99'),
            cat=edge_category,
            cat_name=edge_category.cat_name,
            unit=edge_unit,
            unit_name=edge_unit.unit_name,
            minimum_threshold=Decimal('50000.00'),
            maximum_threshold=Decimal('1000000.00'),
            unit_price=Decimal('99999.99'),
            location='مخزن القيم العالية',
            expiry_warning='لا'
        )
        
        # Create tasks with edge case dates
        from tasks.models import Task, TaskCategory
        
        edge_category_task = TaskCategory.objects.create(
            name='اختبار الحالات الحدية',
            description='فئة لاختبار الحالات الحدية في المهام',
            color='#ff0000',
            icon='fas fa-exclamation-triangle',
            is_active=True
        )
        
        # Task with very short duration
        short_task = Task.objects.create(
            title='مهمة قصيرة جداً',
            description='مهمة تستغرق دقيقة واحدة فقط',
            assigned_to=edge_users[0],
            created_by=edge_users[1],
            category=edge_category_task,
            priority='urgent',
            status='pending',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(minutes=1),
            progress=0
        )
        
        # Task with very long duration
        long_task = Task.objects.create(
            title='مهمة طويلة جداً',
            description='مهمة تستغرق سنة كاملة',
            assigned_to=edge_users[1],
            created_by=edge_users[0],
            category=edge_category_task,
            priority='low',
            status='pending',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=365),
            progress=0
        )
        
        # Task with past dates (overdue)
        overdue_task = Task.objects.create(
            title='مهمة متأخرة',
            description='مهمة انتهت منذ شهر ولم تكتمل',
            assigned_to=edge_users[0],
            created_by=edge_users[1],
            category=edge_category_task,
            priority='high',
            status='in_progress',
            start_date=timezone.now() - timedelta(days=45),
            end_date=timezone.now() - timedelta(days=30),
            progress=75
        )
        
        self.edge_cases['data_limits'] = {
            'users': edge_users,
            'products': [zero_stock_product, high_value_product],
            'tasks': [short_task, long_task, overdue_task],
            'description': 'سيناريوهات اختبار الحالات الحدية والقيم المتطرفة'
        }
        
        print("✅ تم إنشاء سيناريوهات الحالات الحدية")
        return self.edge_cases['data_limits']


def generate_all_specialized_scenarios():
    """Generate all specialized scenarios"""
    print("🚀 إنشاء جميع السيناريوهات المتخصصة...")
    
    results = {}
    
    with transaction.atomic():
        # Generate training scenarios
        training_generator = TrainingScenarioGenerator()
        results['training'] = training_generator.generate_complete_training_environment()
        
        # Generate demo scenarios
        demo_generator = DemoScenarioGenerator()
        results['demo_dashboard'] = demo_generator.create_executive_dashboard_demo()
        results['demo_success'] = demo_generator.create_success_story_demo()
        
        # Generate edge case scenarios
        edge_generator = EdgeCaseScenarioGenerator()
        results['edge_cases'] = edge_generator.create_data_limit_scenarios()
    
    print("✅ تم إنشاء جميع السيناريوهات المتخصصة بنجاح!")
    
    # Print overall summary
    print("\n🎯 ملخص السيناريوهات المُنشأة:")
    print("=" * 50)
    print("  • سيناريوهات التدريب: 3 سيناريوهات كاملة")
    print("  • سيناريوهات العرض التوضيحي: 2 سيناريو")
    print("  • سيناريوهات الحالات الحدية: 1 سيناريو")
    print("=" * 50)
    
    return results


if __name__ == "__main__":
    generate_all_specialized_scenarios()