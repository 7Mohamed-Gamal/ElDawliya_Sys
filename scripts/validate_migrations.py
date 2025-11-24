#!/usr/bin/env python
"""
نص التحقق من صحة الهجرات
Migration Validation Script

هذا النص يتحقق من صحة الهجرات والبنية الجديدة للنظام
This script validates the migrations and new system structure.
"""

import os
import sys
import django
from pathlib import Path
from django.db import connection
from django.core.management import execute_from_command_line
from django.apps import apps

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings.migration')

# Initialize Django
django.setup()

class MigrationValidator:
    """مدقق الهجرات"""

    def __init__(self):
        """__init__ function"""
        self.validation_results = {}
        self.errors = []
        self.warnings = []

    def log(self, message):
        """تسجيل رسالة"""
        print(f"[MIGRATION_VALIDATOR] {message}")

    def validate_database_structure(self):
        """التحقق من بنية قاعدة البيانات"""
        self.log("التحقق من بنية قاعدة البيانات...")

        expected_tables = [
            # Core tables
            'core_department',
            'core_jobposition',
            'core_employee',
            'core_product',
            'core_productcategory',
            'core_task',
            'core_project',
            'core_meeting',
            'core_auditlog',
            'core_systemsetting',

            # Django system tables
            'django_migrations',
            'django_content_type',
            'auth_permission',
            'auth_group',
        ]

        missing_tables = []
        existing_tables = []

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)

            db_tables = [row[0] for row in cursor.fetchall()]

            for table in expected_tables:
                if table in db_tables:
                    existing_tables.append(table)
                else:
                    missing_tables.append(table)

        self.validation_results['existing_tables'] = len(existing_tables)
        self.validation_results['missing_tables'] = len(missing_tables)

        if missing_tables:
            self.errors.extend([f"جدول مفقود: {table}" for table in missing_tables])

        self.log(f"الجداول الموجودة: {len(existing_tables)}")
        self.log(f"الجداول المفقودة: {len(missing_tables)}")

        return len(missing_tables) == 0

    def validate_table_structure(self):
        """التحقق من بنية الجداول"""
        self.log("التحقق من بنية الجداول...")

        table_validations = {}

        with connection.cursor() as cursor:
            # Validate core_employee table
            try:
                cursor.execute("PRAGMA table_info(core_employee)")
                columns = cursor.fetchall()

                expected_columns = [
                    'id', 'created_at', 'updated_at', 'is_active',
                    'first_name', 'last_name', 'email', 'phone',
                    'hire_date', 'emp_code', 'department_id'
                ]

                existing_columns = [col[1] for col in columns]
                missing_columns = [col for col in expected_columns if col not in existing_columns]

                table_validations['core_employee'] = {
                    'exists': True,
                    'columns': len(existing_columns),
                    'missing_columns': missing_columns
                }

                if missing_columns:
                    self.warnings.extend([f"core_employee: عمود مفقود {col}" for col in missing_columns])

            except Exception as e:
                table_validations['core_employee'] = {
                    'exists': False,
                    'error': str(e)
                }
                self.errors.append(f"خطأ في فحص core_employee: {e}")

            # Validate core_product table
            try:
                cursor.execute("PRAGMA table_info(core_product)")
                columns = cursor.fetchall()

                expected_columns = [
                    'id', 'created_at', 'updated_at', 'is_active',
                    'name', 'description', 'sku', 'unit_price',
                    'category_id'
                ]

                existing_columns = [col[1] for col in columns]
                missing_columns = [col for col in expected_columns if col not in existing_columns]

                table_validations['core_product'] = {
                    'exists': True,
                    'columns': len(existing_columns),
                    'missing_columns': missing_columns
                }

                if missing_columns:
                    self.warnings.extend([f"core_product: عمود مفقود {col}" for col in missing_columns])

            except Exception as e:
                table_validations['core_product'] = {
                    'exists': False,
                    'error': str(e)
                }
                self.errors.append(f"خطأ في فحص core_product: {e}")

        self.validation_results['table_structure'] = table_validations

        valid_tables = sum(1 for v in table_validations.values() if v.get('exists', False))
        self.log(f"الجداول الصحيحة: {valid_tables}/{len(table_validations)}")

        return valid_tables == len(table_validations)

    def validate_indexes(self):
        """التحقق من الفهارس"""
        self.log("التحقق من الفهارس...")

        expected_indexes = [
            'idx_employees_active',
            'idx_employees_department',
            'idx_products_category',
            'idx_tasks_status_assigned',
            'idx_audit_user_action'
        ]

        existing_indexes = []
        missing_indexes = []

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)

            db_indexes = [row[0] for row in cursor.fetchall()]

            for index in expected_indexes:
                if index in db_indexes:
                    existing_indexes.append(index)
                else:
                    missing_indexes.append(index)

        self.validation_results['existing_indexes'] = len(existing_indexes)
        self.validation_results['missing_indexes'] = len(missing_indexes)

        if missing_indexes:
            self.warnings.extend([f"فهرس مفقود: {index}" for index in missing_indexes])

        self.log(f"الفهارس الموجودة: {len(existing_indexes)}")
        self.log(f"الفهارس المفقودة: {len(missing_indexes)}")

        return len(missing_indexes) == 0

    def validate_migrations_applied(self):
        """التحقق من تطبيق الهجرات"""
        self.log("التحقق من تطبيق الهجرات...")

        migration_status = {}

        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT app, name FROM django_migrations
                    ORDER BY app, name
                """)

                applied_migrations = cursor.fetchall()

                # Group by app
                apps_migrations = {}
                for app, migration in applied_migrations:
                    if app not in apps_migrations:
                        apps_migrations[app] = []
                    apps_migrations[app].append(migration)

                migration_status = {
                    'total_migrations': len(applied_migrations),
                    'apps_with_migrations': len(apps_migrations),
                    'apps_migrations': apps_migrations
                }

                self.log(f"إجمالي الهجرات المطبقة: {len(applied_migrations)}")
                self.log(f"التطبيقات مع الهجرات: {len(apps_migrations)}")

                # Check for core app migrations
                if 'core' in apps_migrations:
                    self.log(f"هجرات core: {len(apps_migrations['core'])}")
                else:
                    self.errors.append("لا توجد هجرات مطبقة للتطبيق الأساسي core")

            except Exception as e:
                self.errors.append(f"خطأ في فحص الهجرات: {e}")
                migration_status = {'error': str(e)}

        self.validation_results['migrations'] = migration_status

        return 'error' not in migration_status

    def validate_data_consistency(self):
        """التحقق من تناسق البيانات"""
        self.log("التحقق من تناسق البيانات...")

        consistency_checks = {}

        with connection.cursor() as cursor:
            # Check for orphaned records
            try:
                # Check employees without departments (if department is required)
                cursor.execute("""
                    SELECT COUNT(*) FROM core_employee
                    WHERE department_id IS NOT NULL
                    AND department_id NOT IN (SELECT id FROM core_department)
                """)

                orphaned_employees = cursor.fetchone()[0] if cursor.fetchone() else 0
                consistency_checks['orphaned_employees'] = orphaned_employees

                if orphaned_employees > 0:
                    self.warnings.append(f"موظفون بدون أقسام صحيحة: {orphaned_employees}")

            except Exception as e:
                self.warnings.append(f"لم يتم فحص الموظفين المعزولين: {e}")

            # Check for duplicate emails
            try:
                cursor.execute("""
                    SELECT email, COUNT(*) FROM core_employee
                    WHERE email IS NOT NULL
                    GROUP BY email HAVING COUNT(*) > 1
                """)

                duplicate_emails = cursor.fetchall()
                consistency_checks['duplicate_emails'] = len(duplicate_emails)

                if duplicate_emails:
                    self.warnings.append(f"إيميلات مكررة: {len(duplicate_emails)}")

            except Exception as e:
                self.warnings.append(f"لم يتم فحص الإيميلات المكررة: {e}")

            # Check for invalid dates
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM core_employee
                    WHERE hire_date > date('now')
                """)

                future_dates = cursor.fetchone()[0] if cursor.fetchone() else 0
                consistency_checks['future_hire_dates'] = future_dates

                if future_dates > 0:
                    self.warnings.append(f"تواريخ توظيف مستقبلية: {future_dates}")

            except Exception as e:
                self.warnings.append(f"لم يتم فحص التواريخ: {e}")

        self.validation_results['data_consistency'] = consistency_checks

        # Consider validation successful if no critical errors
        return len([w for w in self.warnings if 'مكررة' in w or 'مستقبلية' in w]) == 0

    def validate_model_definitions(self):
        """التحقق من تعريفات النماذج"""
        self.log("التحقق من تعريفات النماذج...")

        model_validations = {}

        try:
            # Check if core models are properly loaded
            from core.models import Employee, Department, Product, Task, Project

            model_validations['core_models_loaded'] = True

            # Check model fields
            employee_fields = [f.name for f in Employee._meta.fields]
            required_employee_fields = ['first_name', 'last_name', 'email', 'hire_date']

            missing_fields = [f for f in required_employee_fields if f not in employee_fields]
            model_validations['employee_fields'] = {
                'total': len(employee_fields),
                'missing': missing_fields
            }

            if missing_fields:
                self.errors.extend([f"Employee model: حقل مفقود {field}" for field in missing_fields])

        except ImportError as e:
            model_validations['core_models_loaded'] = False
            self.errors.append(f"لم يتم تحميل النماذج الأساسية: {e}")

        except Exception as e:
            self.errors.append(f"خطأ في فحص النماذج: {e}")

        self.validation_results['model_definitions'] = model_validations

        return model_validations.get('core_models_loaded', False)

    def generate_validation_report(self):
        """إنشاء تقرير التحقق"""
        self.log("إنشاء تقرير التحقق...")

        report = []
        report.append("=" * 60)
        report.append("تقرير التحقق من الهجرات - نظام الدولية")
        report.append("=" * 60)
        report.append("")

        # Summary
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)

        report.append("الملخص:")
        report.append(f"الأخطاء: {total_errors}")
        report.append(f"التحذيرات: {total_warnings}")
        report.append("")

        # Validation results
        report.append("نتائج التحقق:")

        if 'existing_tables' in self.validation_results:
            report.append(f"الجداول الموجودة: {self.validation_results['existing_tables']}")
            report.append(f"الجداول المفقودة: {self.validation_results['missing_tables']}")

        if 'existing_indexes' in self.validation_results:
            report.append(f"الفهارس الموجودة: {self.validation_results['existing_indexes']}")
            report.append(f"الفهارس المفقودة: {self.validation_results['missing_indexes']}")

        if 'migrations' in self.validation_results:
            migrations = self.validation_results['migrations']
            if 'total_migrations' in migrations:
                report.append(f"الهجرات المطبقة: {migrations['total_migrations']}")

        report.append("")

        # Errors
        if self.errors:
            report.append("الأخطاء:")
            for error in self.errors:
                report.append(f"  ✗ {error}")
            report.append("")

        # Warnings
        if self.warnings:
            report.append("التحذيرات:")
            for warning in self.warnings:
                report.append(f"  ⚠ {warning}")
            report.append("")

        # Overall status
        if total_errors == 0:
            if total_warnings == 0:
                report.append("✅ التحقق مكتمل بنجاح - لا توجد مشاكل")
            else:
                report.append("⚠️ التحقق مكتمل مع تحذيرات")
        else:
            report.append("❌ التحقق فشل - يوجد أخطاء تحتاج إصلاح")

        report.append("")
        report.append("=" * 60)

        # Write report to file
        report_path = project_root / 'logs' / 'migration_validation_report.txt'
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        self.log(f"تم حفظ التقرير في: {report_path}")

        # Print summary
        for line in report:
            print(line)

        return total_errors == 0

    def run_validation(self):
        """تشغيل جميع عمليات التحقق"""
        self.log("بدء التحقق من الهجرات")
        self.log("=" * 50)

        validation_steps = [
            ("بنية قاعدة البيانات", self.validate_database_structure),
            ("بنية الجداول", self.validate_table_structure),
            ("الفهارس", self.validate_indexes),
            ("الهجرات المطبقة", self.validate_migrations_applied),
            ("تناسق البيانات", self.validate_data_consistency),
            ("تعريفات النماذج", self.validate_model_definitions),
        ]

        results = {}

        for step_name, step_function in validation_steps:
            self.log(f"تشغيل: {step_name}")
            try:
                result = step_function()
                results[step_name] = result
                status = "✓" if result else "✗"
                self.log(f"{status} {step_name}: {'نجح' if result else 'فشل'}")
            except Exception as e:
                results[step_name] = False
                self.errors.append(f"{step_name}: {e}")
                self.log(f"✗ {step_name}: خطأ - {e}")

        # Generate final report
        overall_success = self.generate_validation_report()

        self.log("=" * 50)
        if overall_success:
            self.log("✅ التحقق من الهجرات مكتمل بنجاح")
        else:
            self.log("❌ التحقق من الهجرات فشل - راجع التقرير للتفاصيل")

        return overall_success


def main():
    """الدالة الرئيسية"""
    validator = MigrationValidator()
    success = validator.run_validation()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
