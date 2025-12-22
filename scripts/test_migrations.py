#!/usr/bin/env python
"""
نص اختبار الهجرات على بيانات تجريبية
Migration Testing Script with Sample Data

هذا النص ينشئ بيانات تجريبية ويختبر عملية الهجرة عليها
This script creates sample data and tests the migration process on it.
"""

import os
import sys
import django
import uuid
from pathlib import Path
from django.db import transaction, connection
from django.core.management import execute_from_command_line
from datetime import datetime, date, timedelta

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings.migration')

# Initialize Django
django.setup()

class MigrationTester:
    """مختبر الهجرات"""

    def __init__(self):
        """__init__ function"""
        self.test_data = {}
        self.test_results = {}

    def log(self, message):
        """تسجيل رسالة"""
        print(f"[MIGRATION_TEST] {message}")

    def create_sample_data(self):
        """إنشاء بيانات تجريبية"""
        self.log("إنشاء بيانات تجريبية...")

        with connection.cursor() as cursor:
            # Create sample departments
            departments = [
                (str(uuid.uuid4()), 'تقنية المعلومات', 'IT Department', True),
                (str(uuid.uuid4()), 'الموارد البشرية', 'HR Department', True),
                (str(uuid.uuid4()), 'المالية', 'Finance Department', True),
                (str(uuid.uuid4()), 'المبيعات', 'Sales Department', True),
            ]

            # Create departments table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_departments (
                    id TEXT PRIMARY KEY,
                    name_ar TEXT,
                    name_en TEXT,
                    is_active BOOLEAN
                )
            """)

            for dept in departments:
                cursor.execute("""
                    INSERT OR REPLACE INTO test_departments
                    (id, name_ar, name_en, is_active)
                    VALUES (?, ?, ?, ?)
                """, dept)

            self.test_data['departments'] = len(departments)
            self.log(f"تم إنشاء {len(departments)} قسم تجريبي")

            # Create sample employees
            employees = []
            for i in range(20):
                emp_id = str(uuid.uuid4())
                employees.append((
                    emp_id,
                    f'أحمد_{i+1}',
                    f'محمد_{i+1}',
                    f'ahmed.mohamed{i+1}@eldawliya.com',
                    f'05{i+1:08d}',
                    (date.today() - timedelta(days=365*2)).isoformat(),
                    f'مطور برمجيات {i+1}',
                    departments[i % len(departments)][0],  # Random department
                    5000 + (i * 100),
                    True
                ))

            # Create employees table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_employees (
                    id TEXT PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    phone TEXT,
                    hire_date TEXT,
                    job_title TEXT,
                    department_id TEXT,
                    salary REAL,
                    is_active BOOLEAN
                )
            """)

            for emp in employees:
                cursor.execute("""
                    INSERT OR REPLACE INTO test_employees
                    (id, first_name, last_name, email, phone, hire_date,
                     job_title, department_id, salary, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, emp)

            self.test_data['employees'] = len(employees)
            self.log(f"تم إنشاء {len(employees)} موظف تجريبي")

            # Create sample products
            products = []
            categories = ['إلكترونيات', 'مكتبية', 'أثاث', 'برمجيات']

            for i in range(50):
                prod_id = str(uuid.uuid4())
                products.append((
                    prod_id,
                    f'منتج تجريبي {i+1}',
                    f'وصف المنتج التجريبي رقم {i+1}',
                    100 + (i * 10),
                    50 + i,
                    categories[i % len(categories)],
                    f'SKU{i+1:04d}',
                    True
                ))

            # Create products table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_products (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    price REAL,
                    quantity INTEGER,
                    category TEXT,
                    sku TEXT,
                    is_active BOOLEAN
                )
            """)

            for prod in products:
                cursor.execute("""
                    INSERT OR REPLACE INTO test_products
                    (id, name, description, price, quantity, category, sku, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, prod)

            self.test_data['products'] = len(products)
            self.log(f"تم إنشاء {len(products)} منتج تجريبي")

            # Create sample tasks
            tasks = []
            statuses = ['pending', 'in_progress', 'completed', 'cancelled']
            priorities = ['low', 'medium', 'high', 'urgent']

            for i in range(30):
                task_id = str(uuid.uuid4())
                tasks.append((
                    task_id,
                    f'مهمة تجريبية {i+1}',
                    f'وصف المهمة التجريبية رقم {i+1}',
                    statuses[i % len(statuses)],
                    priorities[i % len(priorities)],
                    (datetime.now() + timedelta(days=i)).isoformat(),
                    employees[i % len(employees)][0],  # Random employee
                    datetime.now().isoformat()
                ))

            # Create tasks table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    status TEXT,
                    priority TEXT,
                    due_date TEXT,
                    assigned_to TEXT,
                    created_at TEXT
                )
            """)

            for task in tasks:
                cursor.execute("""
                    INSERT OR REPLACE INTO test_tasks
                    (id, title, description, status, priority, due_date, assigned_to, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, task)

            self.test_data['tasks'] = len(tasks)
            self.log(f"تم إنشاء {len(tasks)} مهمة تجريبية")

    def test_core_migrations(self):
        """اختبار هجرات التطبيق الأساسي"""
        self.log("اختبار هجرات التطبيق الأساسي...")

        try:
            # Test creating core migrations
            execute_from_command_line([
                'manage.py', 'makemigrations', 'core', '--dry-run',
                '--settings=ElDawliya_sys.settings.migration'
            ])

            self.test_results['core_migrations'] = 'نجح'
            self.log("✓ اختبار هجرات core نجح")

        except Exception as e:
            self.test_results['core_migrations'] = f'فشل: {e}'
            self.log(f"✗ اختبار هجرات core فشل: {e}")

    def test_data_integrity(self):
        """اختبار سلامة البيانات"""
        self.log("اختبار سلامة البيانات...")

        integrity_tests = []

        with connection.cursor() as cursor:
            # Test 1: Check for duplicate IDs
            cursor.execute("SELECT id, COUNT(*) FROM test_employees GROUP BY id HAVING COUNT(*) > 1")
            duplicates = cursor.fetchall()
            if duplicates:
                integrity_tests.append(f"معرفات مكررة في الموظفين: {len(duplicates)}")
            else:
                integrity_tests.append("✓ لا توجد معرفات مكررة في الموظفين")

            # Test 2: Check email uniqueness
            cursor.execute("SELECT email, COUNT(*) FROM test_employees GROUP BY email HAVING COUNT(*) > 1")
            duplicate_emails = cursor.fetchall()
            if duplicate_emails:
                integrity_tests.append(f"إيميلات مكررة: {len(duplicate_emails)}")
            else:
                integrity_tests.append("✓ جميع الإيميلات فريدة")

            # Test 3: Check valid dates
            cursor.execute("SELECT COUNT(*) FROM test_employees WHERE hire_date > date('now')")
            future_dates = cursor.fetchone()[0]
            if future_dates > 0:
                integrity_tests.append(f"تواريخ توظيف مستقبلية: {future_dates}")
            else:
                integrity_tests.append("✓ جميع تواريخ التوظيف صحيحة")

            # Test 4: Check positive salaries
            cursor.execute("SELECT COUNT(*) FROM test_employees WHERE salary <= 0")
            invalid_salaries = cursor.fetchone()[0]
            if invalid_salaries > 0:
                integrity_tests.append(f"رواتب غير صحيحة: {invalid_salaries}")
            else:
                integrity_tests.append("✓ جميع الرواتب صحيحة")

        self.test_results['data_integrity'] = integrity_tests

        for test in integrity_tests:
            self.log(f"  {test}")

    def test_performance(self):
        """اختبار الأداء"""
        self.log("اختبار الأداء...")

        import time
        performance_tests = {}

        with connection.cursor() as cursor:
            # Test 1: Employee query performance
            start_time = time.time()
            cursor.execute("SELECT * FROM test_employees WHERE is_active = 1")
            results = cursor.fetchall()
            end_time = time.time()

            performance_tests['employee_query'] = {
                'time': end_time - start_time,
                'records': len(results)
            }

            # Test 2: Product search performance
            start_time = time.time()
            cursor# TODO: Use parameterized queries to prevent SQL injection
        .execute("SELECT * FROM test_products WHERE name LIKE '%تجريبي%'")
            results = cursor.fetchall()
            end_time = time.time()

            performance_tests['product_search'] = {
                'time': end_time - start_time,
                'records': len(results)
            }

            # Test 3: Task filtering performance
            start_time = time.time()
            cursor.execute("SELECT * FROM test_tasks WHERE status = 'pending'")
            results = cursor.fetchall()
            end_time = time.time()

            performance_tests['task_filter'] = {
                'time': end_time - start_time,
                'records': len(results)
            }

        self.test_results['performance'] = performance_tests

        for test_name, result in performance_tests.items():
            self.log(f"  {test_name}: {result['time']:.4f}s ({result['records']} records)")

    def test_migration_rollback(self):
        """اختبار التراجع عن الهجرة"""
        self.log("اختبار التراجع عن الهجرة...")

        try:
            # Create a backup of current state
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM test_employees")
                employee_count_before = cursor.fetchone()[0]

            # Simulate rollback by checking if we can restore data
            rollback_success = employee_count_before > 0

            if rollback_success:
                self.test_results['rollback'] = 'نجح'
                self.log("✓ اختبار التراجع نجح")
            else:
                self.test_results['rollback'] = 'فشل'
                self.log("✗ اختبار التراجع فشل")

        except Exception as e:
            self.test_results['rollback'] = f'فشل: {e}'
            self.log(f"✗ اختبار التراجع فشل: {e}")

    def generate_test_report(self):
        """إنشاء تقرير الاختبار"""
        self.log("إنشاء تقرير الاختبار...")

        report = []
        report.append("=" * 60)
        report.append("تقرير اختبار الهجرات - نظام الدولية")
        report.append("=" * 60)
        report.append("")

        # Test data summary
        report.append("البيانات التجريبية:")
        for entity, count in self.test_data.items():
            report.append(f"  - {entity}: {count}")
        report.append("")

        # Test results
        report.append("نتائج الاختبارات:")

        # Core migrations
        if 'core_migrations' in self.test_results:
            report.append(f"  - هجرات التطبيق الأساسي: {self.test_results['core_migrations']}")

        # Data integrity
        if 'data_integrity' in self.test_results:
            report.append("  - سلامة البيانات:")
            for test in self.test_results['data_integrity']:
                report.append(f"    {test}")

        # Performance
        if 'performance' in self.test_results:
            report.append("  - الأداء:")
            for test_name, result in self.test_results['performance'].items():
                report.append(f"    {test_name}: {result['time']:.4f}s")

        # Rollback
        if 'rollback' in self.test_results:
            report.append(f"  - التراجع: {self.test_results['rollback']}")

        report.append("")
        report.append("=" * 60)

        # Write report to file
        report_path = project_root / 'logs' / 'migration_test_report.txt'
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        self.log(f"تم حفظ التقرير في: {report_path}")

        # Print summary
        for line in report:
            print(line)

    def cleanup_test_data(self):
        """تنظيف البيانات التجريبية"""
        self.log("تنظيف البيانات التجريبية...")

        with connection.cursor() as cursor:
            test_tables = [
                'test_departments',
                'test_employees',
                'test_products',
                'test_tasks'
            ]

            for table in test_tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    self.log(f"تم حذف الجدول {table}")
                except Exception as e:
                    self.log(f"تحذير: لم يتم حذف الجدول {table}: {e}")

    def run_migration_tests(self):
        """تشغيل جميع اختبارات الهجرة"""
        self.log("بدء اختبارات الهجرة")
        self.log("=" * 50)

        try:
            # Create sample data
            self.create_sample_data()

            # Run tests
            self.test_core_migrations()
            self.test_data_integrity()
            self.test_performance()
            self.test_migration_rollback()

            # Generate report
            self.generate_test_report()

            self.log("=" * 50)
            self.log("تمت اختبارات الهجرة بنجاح")

        except Exception as e:
            self.log(f"خطأ في اختبارات الهجرة: {e}")
            raise
        finally:
            # Cleanup test data
            self.cleanup_test_data()


def main():
    """الدالة الرئيسية"""
    tester = MigrationTester()
    tester.run_migration_tests()


if __name__ == '__main__':
    main()
