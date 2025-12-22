#!/usr/bin/env python
"""
نص نقل البيانات من النماذج القديمة إلى الجديدة
Data Migration Script from Old Models to New Models

هذا النص ينقل البيانات من النماذج القديمة إلى الهيكل الجديد المحسن
This script migrates data from old models to the new improved structure.
"""

import os
import sys
import django
from pathlib import Path
from django.db import transaction, connection
from django.core.management import execute_from_command_line

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings.migration')

# Initialize Django
django.setup()

class DataMigration:
    """مدير نقل البيانات"""

    def __init__(self):
        """__init__ function"""
        self.migrated_records = {}
        self.errors = []

    def log(self, message):
        """تسجيل رسالة"""
        print(f"[DATA_MIGRATION] {message}")

    def check_old_tables(self):
        """فحص الجداول القديمة الموجودة"""
        self.log("فحص الجداول القديمة...")

        old_tables = []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'django_%'
                AND name NOT LIKE 'core_%'
                AND name NOT LIKE 'sqlite_%'
            """)
            old_tables = [row[0] for row in cursor.fetchall()]

        self.log(f"تم العثور على {len(old_tables)} جدول قديم")
        return old_tables

    def migrate_employees_data(self):
        """نقل بيانات الموظفين"""
        self.log("نقل بيانات الموظفين...")

        try:
            with connection.cursor() as cursor:
                # Check if old employee table exists
                cursor.execute("""
                    SELECT COUNT(*) FROM sqlite_master
                    WHERE type='table' AND name='employees_employee'
                """)

                if cursor.fetchone()[0] > 0:
                    # Get old employee data
                    cursor.execute("""
                        SELECT id, first_name, last_name, email, phone, hire_date,
                               job_title, department, salary, is_active
                        FROM employees_employee
                    """)

                    old_employees = cursor.fetchall()
                    self.log(f"تم العثور على {len(old_employees)} موظف في النظام القديم")

                    # Insert into new core_employee table
                    migrated_count = 0
                    for emp in old_employees:
                        try:
                            cursor.execute("""
                                INSERT INTO core_employee
                                (id, first_name, last_name, email, phone, hire_date,
                                 job_title, department_name, basic_salary, is_active,
                                 created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                            """, emp)
                            migrated_count += 1
                        except Exception as e:
                            self.errors.append(f"خطأ في نقل الموظف {emp[1]} {emp[2]}: {e}")

                    self.migrated_records['employees'] = migrated_count
                    self.log(f"تم نقل {migrated_count} موظف بنجاح")
                else:
                    self.log("لا توجد بيانات موظفين قديمة")

        except Exception as e:
            self.log(f"خطأ في نقل بيانات الموظفين: {e}")

    def migrate_products_data(self):
        """نقل بيانات المنتجات"""
        self.log("نقل بيانات المنتجات...")

        try:
            with connection.cursor() as cursor:
                # Check if old product table exists
                cursor.execute("""
                    SELECT COUNT(*) FROM sqlite_master
                    WHERE type='table' AND name='inventory_product'
                """)

                if cursor.fetchone()[0] > 0:
                    # Get old product data
                    cursor.execute("""
                        SELECT id, name, description, price, quantity, category,
                               sku, is_active
                        FROM inventory_product
                    """)

                    old_products = cursor.fetchall()
                    self.log(f"تم العثور على {len(old_products)} منتج في النظام القديم")

                    # Insert into new core_product table
                    migrated_count = 0
                    for product in old_products:
                        try:
                            cursor.execute("""
                                INSERT INTO core_product
                                (id, name, description, unit_price, sku, is_active,
                                 created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                            """, (
                                product[0], product[1], product[2], product[3],
                                product[6], product[7]
                            ))
                            migrated_count += 1
                        except Exception as e:
                            self.errors.append(f"خطأ في نقل المنتج {product[1]}: {e}")

                    self.migrated_records['products'] = migrated_count
                    self.log(f"تم نقل {migrated_count} منتج بنجاح")
                else:
                    self.log("لا توجد بيانات منتجات قديمة")

        except Exception as e:
            self.log(f"خطأ في نقل بيانات المنتجات: {e}")

    def migrate_tasks_data(self):
        """نقل بيانات المهام"""
        self.log("نقل بيانات المهام...")

        try:
            with connection.cursor() as cursor:
                # Check if old task table exists
                cursor.execute("""
                    SELECT COUNT(*) FROM sqlite_master
                    WHERE type='table' AND name='tasks_task'
                """)

                if cursor.fetchone()[0] > 0:
                    # Get old task data
                    cursor.execute("""
                        SELECT id, title, description, status, priority,
                               due_date, assigned_to, created_at
                        FROM tasks_task
                    """)

                    old_tasks = cursor.fetchall()
                    self.log(f"تم العثور على {len(old_tasks)} مهمة في النظام القديم")

                    # Insert into new core_task table
                    migrated_count = 0
                    for task in old_tasks:
                        try:
                            cursor.execute("""
                                INSERT INTO core_task
                                (id, title, description, status, priority,
                                 due_date, assigned_to_id, created_at, updated_at,
                                 start_date, progress_percentage)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, 0)
                            """, (
                                task[0], task[1], task[2], task[3], task[4],
                                task[5], task[6], task[7], task[7]
                            ))
                            migrated_count += 1
                        except Exception as e:
                            self.errors.append(f"خطأ في نقل المهمة {task[1]}: {e}")

                    self.migrated_records['tasks'] = migrated_count
                    self.log(f"تم نقل {migrated_count} مهمة بنجاح")
                else:
                    self.log("لا توجد بيانات مهام قديمة")

        except Exception as e:
            self.log(f"خطأ في نقل بيانات المهام: {e}")

    def migrate_meetings_data(self):
        """نقل بيانات الاجتماعات"""
        self.log("نقل بيانات الاجتماعات...")

        try:
            with connection.cursor() as cursor:
                # Check if old meeting table exists
                cursor.execute("""
                    SELECT COUNT(*) FROM sqlite_master
                    WHERE type='table' AND name='meetings_meeting'
                """)

                if cursor.fetchone()[0] > 0:
                    # Get old meeting data
                    cursor.execute("""
                        SELECT id, title, description, start_datetime, end_datetime,
                               location, organizer_id, status
                        FROM meetings_meeting
                    """)

                    old_meetings = cursor.fetchall()
                    self.log(f"تم العثور على {len(old_meetings)} اجتماع في النظام القديم")

                    # Insert into new core_meeting table
                    migrated_count = 0
                    for meeting in old_meetings:
                        try:
                            cursor.execute("""
                                INSERT INTO core_meeting
                                (id, title, description, start_datetime, end_datetime,
                                 location, organizer_id, status, created_at, updated_at,
                                 meeting_type, version)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), 'team', 1)
                            """, meeting)
                            migrated_count += 1
                        except Exception as e:
                            self.errors.append(f"خطأ في نقل الاجتماع {meeting[1]}: {e}")

                    self.migrated_records['meetings'] = migrated_count
                    self.log(f"تم نقل {migrated_count} اجتماع بنجاح")
                else:
                    self.log("لا توجد بيانات اجتماعات قديمة")

        except Exception as e:
            self.log(f"خطأ في نقل بيانات الاجتماعات: {e}")

    def validate_migrated_data(self):
        """التحقق من صحة البيانات المنقولة"""
        self.log("التحقق من صحة البيانات المنقولة...")

        validation_errors = []

        with connection.cursor() as cursor:
            # Check for duplicate records
            tables_to_check = [
                ('core_employee', 'employees'),
                ('core_product', 'products'),
                ('core_task', 'tasks'),
                ('core_meeting', 'meetings')
            ]

            for table, entity in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]

                    expected_count = self.migrated_records.get(entity, 0)
                    if count != expected_count:
                        validation_errors.append(
                            f"عدد {entity} غير متطابق: متوقع {expected_count}, موجود {count}"
                        )
                    else:
                        self.log(f"✓ تم التحقق من {entity}: {count} سجل")

                except Exception as e:
                    validation_errors.append(f"خطأ في التحقق من {entity}: {e}")

        if validation_errors:
            self.log("أخطاء في التحقق:")
            for error in validation_errors:
                self.log(f"  - {error}")
        else:
            self.log("تم التحقق من جميع البيانات بنجاح")

        return len(validation_errors) == 0

    def cleanup_old_data(self):
        """تنظيف البيانات القديمة (اختياري)"""
        self.log("تنظيف البيانات القديمة...")

        # This is optional and should be done carefully
        # For now, we'll just log what could be cleaned up
        old_tables = self.check_old_tables()

        if old_tables:
            self.log("الجداول القديمة التي يمكن حذفها:")
            for table in old_tables:
                self.log(f"  - {table}")
            self.log("تحذير: لم يتم حذف الجداول القديمة تلقائياً للأمان")
        else:
            self.log("لا توجد جداول قديمة للحذف")

    def generate_migration_report(self):
        """إنشاء تقرير الهجرة"""
        self.log("إنشاء تقرير الهجرة...")

        report = []
        report.append("=" * 60)
        report.append("تقرير نقل البيانات - نظام الدولية")
        report.append("=" * 60)
        report.append("")

        # Migration summary
        report.append("ملخص النقل:")
        total_migrated = sum(self.migrated_records.values())
        report.append(f"إجمالي السجلات المنقولة: {total_migrated}")
        report.append("")

        # Details by entity
        report.append("تفاصيل النقل:")
        for entity, count in self.migrated_records.items():
            report.append(f"  - {entity}: {count} سجل")
        report.append("")

        # Errors
        if self.errors:
            report.append("الأخطاء:")
            for error in self.errors:
                report.append(f"  - {error}")
        else:
            report.append("لا توجد أخطاء")

        report.append("")
        report.append("=" * 60)

        # Write report to file
        report_path = project_root / 'logs' / 'data_migration_report.txt'
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        self.log(f"تم حفظ التقرير في: {report_path}")

        # Print summary
        for line in report:
            print(line)

    def run_data_migration(self):
        """تشغيل عملية نقل البيانات الكاملة"""
        self.log("بدء عملية نقل البيانات")
        self.log("=" * 50)

        try:
            with transaction.atomic():
                # Check old tables
                old_tables = self.check_old_tables()

                if not old_tables:
                    self.log("لا توجد بيانات قديمة للنقل")
                    return

                # Migrate different types of data
                self.migrate_employees_data()
                self.migrate_products_data()
                self.migrate_tasks_data()
                self.migrate_meetings_data()

                # Validate migrated data
                if self.validate_migrated_data():
                    self.log("تم نقل البيانات بنجاح")
                else:
                    self.log("تحذير: هناك مشاكل في البيانات المنقولة")

                # Cleanup (optional)
                self.cleanup_old_data()

        except Exception as e:
            self.log(f"خطأ في عملية نقل البيانات: {e}")
            raise
        finally:
            # Generate report
            self.generate_migration_report()


def main():
    """الدالة الرئيسية"""
    migration = DataMigration()
    migration.run_data_migration()


if __name__ == '__main__':
    main()
