"""
Performance Test Data Generator
==============================

This module generates large datasets for performance and load testing.
It creates realistic data volumes that simulate real-world usage patterns.
"""

import random
import string
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from tests.fixtures.base_fixtures import BaseFixtureGenerator

User = get_user_model()


class PerformanceDataGenerator(BaseFixtureGenerator):
    """Generate large datasets for performance testing"""

    def __init__(self):
        """__init__ function"""
        super().__init__()
        self.batch_size = 1000  # Process in batches to avoid memory issues

    def generate_bulk_users(self, count=1000):
        """Generate large number of users efficiently"""
        print(f"📊 إنشاء {count} مستخدم للاختبار...")

        users_to_create = []

        for i in range(count):
            name_parts = self.generate_arabic_name()
            username = f"perfuser{i+1:06d}"

            user_data = {
                'username': username,
                'email': f"{username}@performance.test",
                'first_name': name_parts['first_name'],
                'last_name': name_parts['last_name'],
                'is_active': True,
                'is_staff': random.choice([True, False]),
                'date_joined': self.generate_random_datetime(
                    start_date=date.today() - timedelta(days=730),
                    end_date=date.today()
                )
            }

            users_to_create.append(User(**user_data))

            # Create in batches
            if len(users_to_create) >= self.batch_size:
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                users_to_create = []
                print(f"  ✓ تم إنشاء {i+1} مستخدم...")

        # Create remaining users
        if users_to_create:
            User.objects.bulk_create(users_to_create, ignore_conflicts=True)

        # Set passwords (can't be done in bulk_create)
        print("🔐 تعيين كلمات المرور...")
        users = User.objects.filter(username__startswith='perfuser').prefetch_related()  # TODO: Add appropriate prefetch_related fields
        for user in users.iterator(chunk_size=self.batch_size):
            user.set_password('performance123')
            user.save(update_fields=['password'])

        print(f"✅ تم إنشاء {count} مستخدم بنجاح")
        return users

    def generate_bulk_employees(self, count=2000):
        """Generate large number of employees"""
        print(f"👥 إنشاء {count} موظف للاختبار...")

        from employees.models import Employee
        from org.models import Branch, Department, Job

        # Get related objects
        branches = list(Branch.objects.all().select_related()  # TODO: Add appropriate select_related fields)
        departments = list(Department.objects.all().select_related()  # TODO: Add appropriate select_related fields)
        jobs = list(Job.objects.all().select_related()  # TODO: Add appropriate select_related fields)

        if not branches or not departments or not jobs:
            raise ValueError("Must create organization structure first")

        employees_to_create = []

        for i in range(count):
            name_parts = self.generate_arabic_name()

            hire_date = self.generate_random_date(
                start_date=date.today() - timedelta(days=3650),  # 10 years
                end_date=date.today()
            )

            birth_date = self.generate_random_date(
                start_date=date.today() - timedelta(days=65*365),
                end_date=date.today() - timedelta(days=18*365)
            )

            employee_data = {
                'emp_code': f"PERF{i+1:06d}",
                'first_name': name_parts['first_name'],
                'second_name': name_parts['second_name'],
                'third_name': name_parts['third_name'],
                'last_name': name_parts['last_name'],
                'gender': random.choice(['M', 'F']),
                'birth_date': birth_date,
                'nationality': random.choice(['سعودي', 'مصري', 'أردني', 'سوري', 'لبناني']),
                'national_id': self.generate_national_id(),
                'mobile': self.generate_phone_number(),
                'email': f"perf.emp{i+1:06d}@company.com",
                'address': self.generate_address(),
                'hire_date': hire_date,
                'join_date': hire_date + timedelta(days=random.randint(0, 30)),
                'job': random.choice(jobs),
                'dept': random.choice(departments),
                'branch': random.choice(branches),
                'emp_status': random.choices(
                    ['Active', 'Inactive', 'On Leave', 'Terminated'],
                    weights=[80, 10, 5, 5]
                )[0]
            }

            employees_to_create.append(Employee(**employee_data))

            # Create in batches
            if len(employees_to_create) >= self.batch_size:
                Employee.objects.bulk_create(employees_to_create, ignore_conflicts=True)
                employees_to_create = []
                print(f"  ✓ تم إنشاء {i+1} موظف...")

        # Create remaining employees
        if employees_to_create:
            Employee.objects.bulk_create(employees_to_create, ignore_conflicts=True)

        print(f"✅ تم إنشاء {count} موظف بنجاح")

    def generate_bulk_products(self, count=5000):
        """Generate large number of products"""
        print(f"📦 إنشاء {count} منتج للاختبار...")

        from inventory.models import TblProducts, TblCategories, TblUnitsSpareparts

        categories = list(TblCategories.objects.all().select_related()  # TODO: Add appropriate select_related fields)
        units = list(TblUnitsSpareparts.objects.all().select_related()  # TODO: Add appropriate select_related fields)

        if not categories or not units:
            raise ValueError("Must create categories and units first")

        products_to_create = []
        product_names = self.generate_product_names()

        for i in range(count):
            base_name = random.choice(product_names)
            product_name = f"{base_name} - موديل {i+1}"

            category = random.choice(categories)
            unit = random.choice(units)

            product_data = {
                'product_id': f"PERF{i+1:06d}",
                'product_name': product_name,
                'initial_balance': Decimal(str(random.randint(0, 10000))),
                'elwarad': Decimal(str(random.randint(0, 5000))),
                'mortagaaomalaa': Decimal(str(random.randint(0, 2000))),
                'elmonsarf': Decimal(str(random.randint(0, 3000))),
                'mortagaaelmawarden': Decimal(str(random.randint(0, 1000))),
                'qte_in_stock': Decimal(str(random.randint(0, 5000))),
                'cat': category,
                'cat_name': category.cat_name,
                'unit': unit,
                'unit_name': unit.unit_name,
                'minimum_threshold': Decimal(str(random.randint(1, 100))),
                'maximum_threshold': Decimal(str(random.randint(500, 10000))),
                'unit_price': Decimal(str(round(random.uniform(1.0, 5000.0), 2))),
                'location': f"مخزن {random.choice(['A', 'B', 'C', 'D', 'E'])}-{random.randint(1, 100)}",
                'expiry_warning': random.choice(['نعم', 'لا'])
            }

            products_to_create.append(TblProducts(**product_data))

            # Create in batches
            if len(products_to_create) >= self.batch_size:
                TblProducts.objects.bulk_create(products_to_create, ignore_conflicts=True)
                products_to_create = []
                print(f"  ✓ تم إنشاء {i+1} منتج...")

        # Create remaining products
        if products_to_create:
            TblProducts.objects.bulk_create(products_to_create, ignore_conflicts=True)

        print(f"✅ تم إنشاء {count} منتج بنجاح")

    def generate_bulk_tasks(self, count=10000):
        """Generate large number of tasks"""
        print(f"📋 إنشاء {count} مهمة للاختبار...")

        from tasks.models import Task, TaskCategory
        from meetings.models import Meeting

        users = list(User.objects.all().select_related()  # TODO: Add appropriate select_related fields)
        categories = list(TaskCategory.objects.all().select_related()  # TODO: Add appropriate select_related fields)
        meetings = list(Meeting.objects.all().select_related()  # TODO: Add appropriate select_related fields)

        if not users:
            raise ValueError("Must create users first")

        tasks_to_create = []
        descriptions = self.generate_task_descriptions()

        for i in range(count):
            start_date = self.generate_random_datetime(
                start_date=date.today() - timedelta(days=365),
                end_date=date.today() + timedelta(days=180)
            )

            end_date = start_date + timedelta(
                days=random.randint(1, 60),
                hours=random.randint(0, 23)
            )

            description = random.choice(descriptions)

            task_data = {
                'title': f"مهمة أداء {i+1}: {description[:30]}...",
                'description': f"{description} - مهمة اختبار الأداء رقم {i+1}",
                'assigned_to': random.choice(users),
                'created_by': random.choice(users),
                'category': random.choice(categories) if categories else None,
                'meeting': random.choice(meetings) if meetings and random.random() < 0.3 else None,
                'priority': random.choices(
                    ['low', 'medium', 'high', 'urgent'],
                    weights=[30, 40, 20, 10]
                )[0],
                'status': random.choices(
                    ['pending', 'in_progress', 'completed', 'canceled'],
                    weights=[30, 25, 40, 5]
                )[0],
                'start_date': start_date,
                'end_date': end_date,
                'is_private': random.choice([True, False]),
                'progress': random.randint(0, 100)
            }

            tasks_to_create.append(Task(**task_data))

            # Create in batches
            if len(tasks_to_create) >= self.batch_size:
                Task.objects.bulk_create(tasks_to_create, ignore_conflicts=True)
                tasks_to_create = []
                print(f"  ✓ تم إنشاء {i+1} مهمة...")

        # Create remaining tasks
        if tasks_to_create:
            Task.objects.bulk_create(tasks_to_create, ignore_conflicts=True)

        print(f"✅ تم إنشاء {count} مهمة بنجاح")

    def generate_bulk_meetings(self, count=2000):
        """Generate large number of meetings"""
        print(f"🤝 إنشاء {count} اجتماع للاختبار...")

        from meetings.models import Meeting, Attendee

        users = list(User.objects.all().select_related()  # TODO: Add appropriate select_related fields)
        if not users:
            raise ValueError("Must create users first")

        meetings_to_create = []
        topics = self.generate_meeting_topics()

        for i in range(count):
            meeting_date = self.generate_random_datetime(
                start_date=date.today() - timedelta(days=730),
                end_date=date.today() + timedelta(days=180)
            )

            topic = random.choice(topics)

            meeting_data = {
                'title': f"اجتماع أداء {i+1}: {topic}",
                'date': meeting_date,
                'topic': f"{topic} - اجتماع اختبار الأداء رقم {i+1}",
                'status': random.choices(
                    ['pending', 'completed', 'cancelled'],
                    weights=[20, 70, 10]
                )[0],
                'created_by': random.choice(users)
            }

            meetings_to_create.append(Meeting(**meeting_data))

            # Create in batches
            if len(meetings_to_create) >= self.batch_size:
                created_meetings = Meeting.objects.bulk_create(meetings_to_create, ignore_conflicts=True)

                # Add attendees for created meetings
                self.add_meeting_attendees(created_meetings, users)

                meetings_to_create = []
                print(f"  ✓ تم إنشاء {i+1} اجتماع...")

        # Create remaining meetings
        if meetings_to_create:
            created_meetings = Meeting.objects.bulk_create(meetings_to_create, ignore_conflicts=True)
            self.add_meeting_attendees(created_meetings, users)

        print(f"✅ تم إنشاء {count} اجتماع بنجاح")

    def add_meeting_attendees(self, meetings, users):
        """Add attendees to meetings"""
        from meetings.models import Attendee

        attendees_to_create = []

        for meeting in meetings:
            # Add 2-15 attendees per meeting
            attendee_count = random.randint(2, min(15, len(users)))
            selected_users = random.sample(users, attendee_count)

            for user in selected_users:
                attendees_to_create.append(Attendee(meeting=meeting, user=user))

        if attendees_to_create:
            Attendee.objects.bulk_create(attendees_to_create, ignore_conflicts=True)

    def generate_time_series_data(self, days_back=365):
        """Generate time-series data for analytics testing"""
        print(f"📈 إنشاء بيانات السلاسل الزمنية لـ {days_back} يوم...")

        from django.db import connection

        # Generate daily statistics
        start_date = date.today() - timedelta(days=days_back)

        daily_stats = []
        for i in range(days_back):
            current_date = start_date + timedelta(days=i)

            # Simulate realistic patterns (more activity on weekdays)
            is_weekend = current_date.weekday() >= 5
            base_activity = 0.3 if is_weekend else 1.0

            # Add seasonal variations
            month_factor = 1.0 + 0.2 * (current_date.month % 6 - 3) / 3

            daily_stats.append({
                'date': current_date,
                'tasks_created': int(random.randint(5, 50) * base_activity * month_factor),
                'meetings_held': int(random.randint(2, 20) * base_activity * month_factor),
                'products_moved': int(random.randint(10, 200) * base_activity * month_factor),
                'employees_active': int(random.randint(50, 500) * base_activity * month_factor)
            })

        # Store in a temporary table for analytics
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_activity_stats (
                    date DATE PRIMARY KEY,
                    tasks_created INTEGER,
                    meetings_held INTEGER,
                    products_moved INTEGER,
                    employees_active INTEGER
                )
            """)

            for stat in daily_stats:
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_activity_stats
                    (date, tasks_created, meetings_held, products_moved, employees_active)
                    VALUES (?, ?, ?, ?, ?)
                """, [
                    stat['date'],
                    stat['tasks_created'],
                    stat['meetings_held'],
                    stat['products_moved'],
                    stat['employees_active']
                ])

        print(f"✅ تم إنشاء بيانات السلاسل الزمنية بنجاح")

    def create_performance_indexes(self):
        """Create additional indexes for performance testing"""
        print("🚀 إنشاء فهارس الأداء...")

        with connection.cursor() as cursor:
            # Task performance indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_performance_1
                ON tasks (status, priority, end_date)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_performance_2
                ON tasks (assigned_to_id, status, created_at)
            """)

            # Employee performance indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_employees_performance_1
                ON Employees (emp_status, dept_id, hire_date)
            """)

            # Product performance indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_performance_1
                ON Tbl_Products (cat_id, qte_in_stock, unit_price)
            """)

            # Meeting performance indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_meetings_performance_1
                ON meetings_meeting (status, date, created_by_id)
            """)

        print("✅ تم إنشاء فهارس الأداء بنجاح")


class LoadTestScenarioGenerator:
    """Generate specific scenarios for load testing"""

    def __init__(self):
        """__init__ function"""
        self.scenarios = []

    def create_concurrent_user_scenario(self, user_count=100):
        """Create scenario for concurrent user testing"""
        print(f"👥 إنشاء سيناريو {user_count} مستخدم متزامن...")

        # Create users with specific patterns
        users = []
        for i in range(user_count):
            username = f"loadtest_user_{i+1:03d}"
            user = User.objects.create_user(
                username=username,
                email=f"{username}@loadtest.com",
                password='loadtest123',
                first_name=f"مستخدم {i+1}",
                last_name="اختبار الحمولة"
            )
            users.append(user)

        return users

    def create_heavy_query_scenario(self):
        """Create data patterns that will stress the database"""
        print("🔍 إنشاء سيناريو الاستعلامات الثقيلة...")

        from tasks.models import Task
        from employees.models import Employee

        # Create tasks with complex relationships
        employees = list(Employee.objects.all().select_related()  # TODO: Add appropriate select_related fields[:100])

        for i in range(1000):
            # Create tasks with overlapping date ranges
            start_date = timezone.now() - timedelta(days=random.randint(1, 365))
            end_date = start_date + timedelta(days=random.randint(1, 90))

            Task.objects.create(
                title=f"مهمة استعلام ثقيل {i+1}",
                description=f"مهمة لاختبار الاستعلامات المعقدة - {i+1}",
                assigned_to=random.choice(employees).user if hasattr(random.choice(employees), 'user') else User.objects.first(),
                created_by=User.objects.first(),
                start_date=start_date,
                end_date=end_date,
                status=random.choice(['pending', 'in_progress', 'completed']),
                priority=random.choice(['low', 'medium', 'high', 'urgent'])
            )

    def generate_report_data_scenario(self):
        """Generate data specifically for report generation testing"""
        print("📊 إنشاء بيانات اختبار التقارير...")

        # This would create data patterns that stress report generation
        # Implementation depends on specific report requirements
        pass


def run_performance_data_generation():
    """Main function to run performance data generation"""
    print("🚀 بدء إنشاء بيانات اختبار الأداء...")

    generator = PerformanceDataGenerator()

    with transaction.atomic():
        # Generate large datasets
        generator.generate_bulk_users(1000)
        generator.generate_bulk_employees(2000)
        generator.generate_bulk_products(5000)
        generator.generate_bulk_tasks(10000)
        generator.generate_bulk_meetings(2000)

        # Generate time series data
        generator.generate_time_series_data(365)

        # Create performance indexes
        generator.create_performance_indexes()

    print("✅ تم إنشاء جميع بيانات اختبار الأداء بنجاح!")


if __name__ == "__main__":
    run_performance_data_generation()
