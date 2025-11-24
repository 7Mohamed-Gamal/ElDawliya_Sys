#!/usr/bin/env python
"""
نص شامل لهجرة نظام الدولية
Comprehensive Migration Script for ElDawliya System

هذا النص يقوم بإنشاء وتطبيق الهجرات الشاملة للنظام الجديد
This script creates and applies comprehensive migrations for the new system structure.
"""

import os
import sys
import django
from pathlib import Path
from django.core.management import execute_from_command_line
from django.db import connection, transaction
from django.apps import apps

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings.migration')

# Initialize Django
django.setup()

class ComprehensiveMigration:
    """مدير الهجرة الشاملة"""

    def __init__(self):
        """__init__ function"""
        self.backup_created = False
        self.migration_steps = []

    def log(self, message):
        """تسجيل رسالة"""
        print(f"[MIGRATION] {message}")

    def create_backup(self):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        self.log("إنشاء نسخة احتياطية من قاعدة البيانات...")

        # For SQLite (development), copy the database file
        if 'sqlite' in connection.settings_dict['ENGINE']:
            import shutil
            db_path = connection.settings_dict['NAME']
            backup_path = f"{db_path}.backup"

            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_path)
                self.log(f"تم إنشاء نسخة احتياطية: {backup_path}")
                self.backup_created = True
            else:
                self.log("لا توجد قاعدة بيانات للنسخ الاحتياطي")
        else:
            self.log("نسخ احتياطي لقاعدة البيانات غير مدعوم في هذا الإعداد")

    def check_existing_data(self):
        """فحص البيانات الموجودة"""
        self.log("فحص البيانات الموجودة...")

        with connection.cursor() as cursor:
            # Check if any tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = cursor.fetchall()

            if tables:
                self.log(f"تم العثور على {len(tables)} جدول موجود")
                for table in tables[:5]:  # Show first 5 tables
                    self.log(f"  - {table[0]}")
                if len(tables) > 5:
                    self.log(f"  ... و {len(tables) - 5} جدول آخر")
            else:
                self.log("لا توجد جداول موجودة")

        return len(tables) > 0

    def create_core_migrations(self):
        """إنشاء هجرات التطبيق الأساسي"""
        self.log("إنشاء هجرات التطبيق الأساسي...")

        # Create initial migration for core app
        try:
            execute_from_command_line([
                'manage.py', 'makemigrations', 'core',
                '--settings=ElDawliya_sys.settings.migration'
            ])
            self.log("تم إنشاء هجرات core بنجاح")
        except Exception as e:
            self.log(f"خطأ في إنشاء هجرات core: {e}")

    def create_app_migrations(self):
        """إنشاء هجرات التطبيقات الأخرى"""
        self.log("إنشاء هجرات التطبيقات الأخرى...")

        apps_to_migrate = [
            'accounts', 'hr', 'api', 'meetings', 'tasks', 'inventory',
            'administrator', 'Purchase_orders', 'notifications', 'audit',
            'cars', 'attendance', 'org', 'employees', 'companies',
            'leaves', 'evaluations', 'payrolls', 'banks', 'insurance',
            'training', 'loans', 'disciplinary', 'tickets', 'workflow',
            'assets', 'rbac', 'reports', 'syssettings'
        ]

        for app_name in apps_to_migrate:
            try:
                execute_from_command_line([
                    'manage.py', 'makemigrations', app_name,
                    '--settings=ElDawliya_sys.settings.migration'
                ])
                self.log(f"تم إنشاء هجرات {app_name} بنجاح")
            except Exception as e:
                self.log(f"تحذير: لم يتم إنشاء هجرات {app_name}: {e}")

    def apply_migrations(self):
        """تطبيق الهجرات"""
        self.log("تطبيق الهجرات...")

        try:
            # Apply core migrations first
            execute_from_command_line([
                'manage.py', 'migrate', 'core',
                '--settings=ElDawliya_sys.settings.migration'
            ])
            self.log("تم تطبيق هجرات core بنجاح")

            # Apply other migrations
            execute_from_command_line([
                'manage.py', 'migrate',
                '--settings=ElDawliya_sys.settings.migration'
            ])
            self.log("تم تطبيق جميع الهجرات بنجاح")

        except Exception as e:
            self.log(f"خطأ في تطبيق الهجرات: {e}")
            raise

    def create_indexes(self):
        """إنشاء الفهارس المحسنة"""
        self.log("إنشاء الفهارس المحسنة...")

        indexes_sql = [
            # Employee indexes
            "CREATE INDEX IF NOT EXISTS idx_employees_active ON core_employee(is_active, emp_status);",
            "CREATE INDEX IF NOT EXISTS idx_employees_department ON core_employee(department_id);",
            "CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON core_employee(hire_date);",

            # Attendance indexes
            "CREATE INDEX IF NOT EXISTS idx_attendance_date_emp ON core_attendancerecord(date, employee_id);",
            "CREATE INDEX IF NOT EXISTS idx_attendance_status ON core_attendancerecord(status);",

            # Product indexes
            "CREATE INDEX IF NOT EXISTS idx_products_category ON core_product(category_id, is_active);",
            "CREATE INDEX IF NOT EXISTS idx_products_sku ON core_product(sku);",

            # Task indexes
            "CREATE INDEX IF NOT EXISTS idx_tasks_status_assigned ON core_task(status, assigned_to_id);",
            "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON core_task(due_date);",
            "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON core_task(priority);",

            # Project indexes
            "CREATE INDEX IF NOT EXISTS idx_projects_status ON core_project(status);",
            "CREATE INDEX IF NOT EXISTS idx_projects_manager ON core_project(manager_id);",

            # Audit indexes
            "CREATE INDEX IF NOT EXISTS idx_audit_user_action ON core_auditlog(user_id, action);",
            "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON core_auditlog(timestamp);",
        ]

        with connection.cursor() as cursor:
            for sql in indexes_sql:
                try:
                    cursor.execute(sql)
                    self.log(f"تم إنشاء فهرس: {sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    self.log(f"تحذير: لم يتم إنشاء فهرس: {e}")

    def create_constraints(self):
        """إنشاء القيود الجديدة"""
        self.log("إنشاء القيود الجديدة...")

        # Note: SQLite has limited constraint support, so we'll focus on what's possible
        constraints_sql = [
            # Check constraints for valid data
            "-- Employee hire date constraint would go here if supported",
            "-- Product price constraint would go here if supported",
        ]

        self.log("تم تخطي القيود (غير مدعومة في SQLite)")

    def verify_migration(self):
        """التحقق من نجاح الهجرة"""
        self.log("التحقق من نجاح الهجرة...")

        with connection.cursor() as cursor:
            # Check core tables exist
            core_tables = [
                'core_employee', 'core_department', 'core_product',
                'core_task', 'core_project', 'core_auditlog'
            ]

            for table in core_tables:
                cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone()[0] == 0:
                    self.log(f"تحذير: الجدول {table} غير موجود")
                else:
                    self.log(f"✓ الجدول {table} موجود")

    def run_migration(self):
        """تشغيل عملية الهجرة الكاملة"""
        self.log("بدء عملية الهجرة الشاملة لنظام الدولية")
        self.log("=" * 50)

        try:
            # Step 1: Create backup
            self.create_backup()

            # Step 2: Check existing data
            has_data = self.check_existing_data()

            # Step 3: Create migrations
            self.create_core_migrations()
            self.create_app_migrations()

            # Step 4: Apply migrations
            self.apply_migrations()

            # Step 5: Create indexes and constraints
            self.create_indexes()
            self.create_constraints()

            # Step 6: Verify migration
            self.verify_migration()

            self.log("=" * 50)
            self.log("تمت عملية الهجرة بنجاح!")
            self.log("يمكنك الآن استخدام النظام الجديد")

            if self.backup_created:
                self.log("تم الاحتفاظ بنسخة احتياطية من قاعدة البيانات")

        except Exception as e:
            self.log(f"خطأ في عملية الهجرة: {e}")
            if self.backup_created:
                self.log("يمكنك استعادة النسخة الاحتياطية في حالة الحاجة")
            raise


def main():
    """الدالة الرئيسية"""
    migration = ComprehensiveMigration()
    migration.run_migration()


if __name__ == '__main__':
    main()
