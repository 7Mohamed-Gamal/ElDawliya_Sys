"""
Test Environment Setup
=====================

This module provides comprehensive test environment setup including:
- Database configuration for testing
- Test data scenarios
- Performance testing setup
- Demo environment configuration
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection
from django.test.utils import setup_test_environment, teardown_test_environment


class TestEnvironmentManager:
    """Manage test environment setup and teardown"""

    def __init__(self):
        """__init__ function"""
        self.test_db_name = None
        self.original_db_name = None

    def setup_test_database(self):
        """Setup isolated test database"""
        print("🗄️  إعداد قاعدة بيانات الاختبار...")

        # Store original database name
        self.original_db_name = settings.DATABASES['default']['NAME']

        # Create test database name
        self.test_db_name = f"test_{self.original_db_name}"

        # Update database settings for testing
        settings.DATABASES['default']['NAME'] = self.test_db_name

        # Create test database
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"CREATE DATABASE {self.test_db_name}")
                print(f"✅ تم إنشاء قاعدة بيانات الاختبار: {self.test_db_name}")
            except Exception as e:
                print(f"⚠️  قاعدة البيانات موجودة مسبقاً أو خطأ: {e}")

        # Run migrations
        print("🔄 تطبيق الهجرات...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=0'])

        print("✅ تم إعداد قاعدة بيانات الاختبار بنجاح")

    def teardown_test_database(self):
        """Clean up test database"""
        if self.test_db_name:
            print(f"🧹 تنظيف قاعدة بيانات الاختبار: {self.test_db_name}")

            # Restore original database name
            if self.original_db_name:
                settings.DATABASES['default']['NAME'] = self.original_db_name

            # Drop test database
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"DROP DATABASE IF EXISTS {self.test_db_name}")
                    print("✅ تم حذف قاعدة بيانات الاختبار")
                except Exception as e:
                    print(f"⚠️  خطأ في حذف قاعدة البيانات: {e}")

    def setup_test_environment(self):
        """Setup Django test environment"""
        print("🔧 إعداد بيئة الاختبار...")

        # Setup test environment
        setup_test_environment()

        # Configure test settings
        self.configure_test_settings()

        print("✅ تم إعداد بيئة الاختبار")

    def configure_test_settings(self):
        """Configure Django settings for testing"""
        # Disable migrations for faster testing
        settings.MIGRATION_MODULES = {
            app: None for app in [
                'auth', 'contenttypes', 'sessions', 'messages',
                'staticfiles', 'admin', 'hr', 'employees', 'inventory',
                'meetings', 'tasks', 'Purchase_orders', 'accounts',
                'administrator', 'api', 'audit', 'notifications'
            ]
        }

        # Use in-memory database for speed
        if 'test' in sys.argv:
            settings.DATABASES['default'] = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }

        # Disable logging during tests
        settings.LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'null': {
                    'class': 'logging.NullHandler',
                },
            },
            'root': {
                'handlers': ['null'],
            },
        }

        # Speed up password hashing
        settings.PASSWORD_HASHERS = [
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ]

        # Disable cache
        settings.CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }


class TestScenarioManager:
    """Manage different test scenarios"""

    def __init__(self):
        """__init__ function"""
        self.scenarios = {
            'minimal': self.setup_minimal_scenario,
            'standard': self.setup_standard_scenario,
            'comprehensive': self.setup_comprehensive_scenario,
            'performance': self.setup_performance_scenario,
            'demo': self.setup_demo_scenario
        }

    def setup_scenario(self, scenario_name='standard'):
        """Setup specific test scenario"""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        print(f"🎭 إعداد سيناريو الاختبار: {scenario_name}")
        return self.scenarios[scenario_name]()

    def setup_minimal_scenario(self):
        """Setup minimal test data for basic testing"""
        from tests.fixtures.base_fixtures import ComprehensiveFixtureGenerator

        generator = ComprehensiveFixtureGenerator()
        return generator.generate_all_fixtures(
            users_count=5,
            employees_count=10,
            products_count=20,
            meetings_count=5,
            tasks_count=15,
            purchase_requests_count=5
        )

    def setup_standard_scenario(self):
        """Setup standard test data for regular testing"""
        from tests.fixtures.base_fixtures import ComprehensiveFixtureGenerator

        generator = ComprehensiveFixtureGenerator()
        return generator.generate_all_fixtures(
            users_count=25,
            employees_count=50,
            products_count=100,
            meetings_count=30,
            tasks_count=100,
            purchase_requests_count=50
        )

    def setup_comprehensive_scenario(self):
        """Setup comprehensive test data for full testing"""
        from tests.fixtures.base_fixtures import ComprehensiveFixtureGenerator

        generator = ComprehensiveFixtureGenerator()
        return generator.generate_all_fixtures(
            users_count=100,
            employees_count=200,
            products_count=500,
            meetings_count=100,
            tasks_count=500,
            purchase_requests_count=200
        )

    def setup_performance_scenario(self):
        """Setup large dataset for performance testing"""
        from tests.fixtures.performance_data_generator import PerformanceDataGenerator

        generator = PerformanceDataGenerator()

        # Generate large datasets
        generator.generate_bulk_users(1000)
        generator.generate_bulk_employees(2000)
        generator.generate_bulk_products(5000)
        generator.generate_bulk_tasks(10000)
        generator.generate_bulk_meetings(2000)
        generator.generate_time_series_data(365)
        generator.create_performance_indexes()

        return "Performance data generated successfully"

    def setup_demo_scenario(self):
        """Setup demo data for presentations"""
        from tests.fixtures.base_fixtures import ComprehensiveFixtureGenerator

        generator = ComprehensiveFixtureGenerator()
        created_objects = generator.generate_all_fixtures(
            users_count=15,
            employees_count=30,
            products_count=50,
            meetings_count=20,
            tasks_count=50,
            purchase_requests_count=25
        )

        # Add demo-specific scenarios
        self.create_demo_scenarios(created_objects)

        return created_objects

    def create_demo_scenarios(self, created_objects):
        """Create specific demo scenarios"""
        from tasks.models import Task, TaskStep
        from meetings.models import Meeting
        from datetime import timedelta
        from django.utils import timezone

        users = created_objects.get('users', [])
        if len(users) >= 4:
            # Create a realistic project scenario
            project_manager = users[1]
            developer1 = users[2]
            developer2 = users[3]

            # Create project meeting
            meeting = Meeting.objects.create(
                title='اجتماع مشروع تطوير النظام الإلكتروني',
                date=timezone.now() + timedelta(days=3),
                topic='مناقشة تطوير وتحسين النظام الإلكتروني للشركة',
                status='pending',
                created_by=project_manager
            )

            # Create related tasks
            tasks_data = [
                {
                    'title': 'تحليل المتطلبات الوظيفية',
                    'description': 'تحليل وتوثيق جميع المتطلبات الوظيفية للنظام الجديد بما يشمل احتياجات جميع الأقسام',
                    'assigned_to': developer1,
                    'priority': 'high',
                    'days_to_complete': 7
                },
                {
                    'title': 'تصميم واجهة المستخدم',
                    'description': 'تصميم واجهة مستخدم حديثة ومتجاوبة تدعم اللغة العربية بشكل كامل',
                    'assigned_to': developer2,
                    'priority': 'medium',
                    'days_to_complete': 14
                },
                {
                    'title': 'تطوير قاعدة البيانات',
                    'description': 'تطوير وتحسين هيكل قاعدة البيانات لضمان الأداء الأمثل',
                    'assigned_to': developer1,
                    'priority': 'high',
                    'days_to_complete': 10
                }
            ]

            for task_data in tasks_data:
                start_date = timezone.now() + timedelta(days=1)
                end_date = start_date + timedelta(days=task_data['days_to_complete'])

                task = Task.objects.create(
                    title=task_data['title'],
                    description=task_data['description'],
                    assigned_to=task_data['assigned_to'],
                    created_by=project_manager,
                    meeting=meeting,
                    priority=task_data['priority'],
                    status='pending',
                    start_date=start_date,
                    end_date=end_date,
                    progress=0
                )

                # Add steps to first task
                if task_data['title'] == 'تحليل المتطلبات الوظيفية':
                    steps = [
                        'مراجعة النظام الحالي وتحديد نقاط القوة والضعف',
                        'إجراء مقابلات مع أصحاب المصلحة في جميع الأقسام',
                        'توثيق المتطلبات الوظيفية بشكل مفصل',
                        'مراجعة وتأكيد المتطلبات مع الإدارة العليا'
                    ]

                    for step_desc in steps:
                        TaskStep.objects.create(
                            task=task,
                            description=step_desc,
                            created_by=task_data['assigned_to']
                        )


class TestDataValidator:
    """Validate test data integrity and consistency"""

    def __init__(self):
        """__init__ function"""
        self.validation_results = {}

    def validate_all_data(self):
        """Run all validation checks"""
        print("🔍 التحقق من سلامة البيانات التجريبية...")

        validations = [
            ('المستخدمين', self.validate_users),
            ('الموظفين', self.validate_employees),
            ('المنتجات', self.validate_products),
            ('المهام', self.validate_tasks),
            ('الاجتماعات', self.validate_meetings),
            ('طلبات الشراء', self.validate_purchase_requests)
        ]

        all_valid = True

        for name, validation_func in validations:
            try:
                is_valid = validation_func()
                self.validation_results[name] = is_valid

                if is_valid:
                    print(f"  ✅ {name}: صحيح")
                else:
                    print(f"  ❌ {name}: يحتوي على أخطاء")
                    all_valid = False

            except Exception as e:
                print(f"  ⚠️  {name}: خطأ في التحقق - {e}")
                self.validation_results[name] = False
                all_valid = False

        if all_valid:
            print("✅ جميع البيانات صحيحة ومتسقة")
        else:
            print("❌ توجد أخطاء في البيانات - يرجى المراجعة")

        return all_valid

    def validate_users(self):
        """Validate user data"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Check for duplicate usernames
        total_users = User.objects.count()
        unique_usernames = User.objects.values('username').distinct().count()

        if total_users != unique_usernames:
            print(f"    ⚠️  أسماء مستخدمين مكررة: {total_users - unique_usernames}")
            return False

        # Check for users without email
        users_without_email = User.objects.filter(email='').count()
        if users_without_email > 0:
            print(f"    ⚠️  مستخدمين بدون بريد إلكتروني: {users_without_email}")
            return False

        return True

    def validate_employees(self):
        """Validate employee data"""
        try:
            from employees.models import Employee

            # Check for employees without required fields
            employees_without_code = Employee.objects.filter(emp_code='').count()
            if employees_without_code > 0:
                print(f"    ⚠️  موظفين بدون رمز: {employees_without_code}")
                return False

            # Check for duplicate employee codes
            total_employees = Employee.objects.count()
            unique_codes = Employee.objects.values('emp_code').distinct().count()

            if total_employees != unique_codes:
                print(f"    ⚠️  رموز موظفين مكررة: {total_employees - unique_codes}")
                return False

            return True

        except ImportError:
            print("    ⚠️  نموذج الموظفين غير متاح")
            return True

    def validate_products(self):
        """Validate product data"""
        try:
            from inventory.models import TblProducts

            # Check for products with negative stock
            negative_stock = TblProducts.objects.filter(qte_in_stock__lt=0).count()
            if negative_stock > 0:
                print(f"    ⚠️  منتجات برصيد سالب: {negative_stock}")
                return False

            # Check for products without categories
            no_category = TblProducts.objects.filter(cat__isnull=True).count()
            if no_category > 0:
                print(f"    ⚠️  منتجات بدون فئة: {no_category}")
                return False

            return True

        except ImportError:
            print("    ⚠️  نموذج المنتجات غير متاح")
            return True

    def validate_tasks(self):
        """Validate task data"""
        try:
            from tasks.models import Task

            # Check for tasks with end date before start date
            invalid_dates = Task.objects.filter(end_date__lt=models.F('start_date').count()
            if invalid_dates > 0:
                print(f"    ⚠️  مهام بتواريخ غير صحيحة: {invalid_dates}")
                return False

            # Check for tasks without assigned users
            no_assignee = Task.objects.filter(assigned_to__isnull=True).count()
            if no_assignee > 0:
                print(f"    ⚠️  مهام غير مُعيَّنة: {no_assignee}")
                return False

            return True

        except ImportError:
            print("    ⚠️  نموذج المهام غير متاح")
            return True

    def validate_meetings(self):
        """Validate meeting data"""
        try:
            from meetings.models import Meeting, Attendee

            # Check for meetings without attendees
            meetings_without_attendees = Meeting.objects.filter(attendees__isnull=True).count()
            if meetings_without_attendees > 0:
                print(f"    ⚠️  اجتماعات بدون حضور: {meetings_without_attendees}")
                return False

            return True

        except ImportError:
            print("    ⚠️  نموذج الاجتماعات غير متاح")
            return True

    def validate_purchase_requests(self):
        """Validate purchase request data"""
        try:
            from Purchase_orders.models import PurchaseRequest, PurchaseRequestItem

            # Check for requests without items
            requests_without_items = PurchaseRequest.objects.filter(items__isnull=True).count()
            if requests_without_items > 0:
                print(f"    ⚠️  طلبات شراء بدون عناصر: {requests_without_items}")
                return False

            return True

        except ImportError:
            print("    ⚠️  نموذج طلبات الشراء غير متاح")
            return True


def setup_complete_test_environment(scenario='standard'):
    """Setup complete test environment with data"""
    print("🚀 إعداد بيئة الاختبار الكاملة...")

    # Setup environment
    env_manager = TestEnvironmentManager()
    env_manager.setup_test_environment()
    env_manager.setup_test_database()

    # Generate test data
    scenario_manager = TestScenarioManager()
    created_objects = scenario_manager.setup_scenario(scenario)

    # Validate data
    validator = TestDataValidator()
    is_valid = validator.validate_all_data()

    if is_valid:
        print("🎉 تم إعداد بيئة الاختبار بنجاح!")
    else:
        print("⚠️  تم إعداد بيئة الاختبار مع بعض التحذيرات")

    return {
        'environment_manager': env_manager,
        'scenario_manager': scenario_manager,
        'validator': validator,
        'created_objects': created_objects,
        'is_valid': is_valid
    }


if __name__ == "__main__":
    # Setup test environment when run directly
    setup_complete_test_environment('demo')
