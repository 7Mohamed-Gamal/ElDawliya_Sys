"""
Test Data Export/Import Utilities
=================================

This module provides utilities to export and import test data for:
- Backup and restore test scenarios
- Sharing test datasets between environments
- Creating reproducible test conditions
"""

import json
import csv
import os
import zipfile
from datetime import datetime, date
from decimal import Decimal
from django.core import serializers
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()


class TestDataExporter:
    """Export test data in various formats"""

    def __init__(self, output_dir='test_data_exports'):
        """__init__ function"""
        self.output_dir = output_dir
        self.ensure_output_dir()

    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export_all_data(self, format='json'):
        """Export all test data"""
        print(f"📤 تصدير جميع البيانات التجريبية بصيغة {format.upper()}...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format == 'json':
            return self.export_to_json(timestamp)
        elif format == 'csv':
            return self.export_to_csv(timestamp)
        elif format == 'excel':
            return self.export_to_excel(timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def export_to_json(self, timestamp):
        """Export data to JSON format"""
        export_file = os.path.join(self.output_dir, f'test_data_{timestamp}.json')

        # Define models to export in dependency order
        models_to_export = [
            'auth.User',
            'org.Branch',
            'org.Department',
            'org.Job',
            'employees.Employee',
            'inventory.TblCategories',
            'inventory.TblUnitsSpareparts',
            'inventory.TblSuppliers',
            'inventory.TblProducts',
            'tasks.TaskCategory',
            'tasks.Task',
            'meetings.Meeting',
            'meetings.Attendee',
            'Purchase_orders.Vendor',
            'Purchase_orders.PurchaseRequest',
            'Purchase_orders.PurchaseRequestItem',
        ]

        exported_data = []

        for model_name in models_to_export:
            try:
                app_label, model_class = model_name.split('.')
                model = apps.get_model(app_label, model_class)

                # Serialize model data
                model_data = serializers.serialize('json', model.objects.all())
                model_objects = json.loads(model_data)

                exported_data.extend(model_objects)
                print(f"  ✓ تم تصدير {len(model_objects)} من {model_name}")

            except Exception as e:
                print(f"  ⚠️  تعذر تصدير {model_name}: {e}")

        # Write to file
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(exported_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ تم تصدير البيانات إلى: {export_file}")
        return export_file

    def export_to_csv(self, timestamp):
        """Export data to CSV format"""
        export_dir = os.path.join(self.output_dir, f'csv_export_{timestamp}')
        os.makedirs(export_dir, exist_ok=True)

        # Define models and their key fields
        models_config = {
            'users': {
                'model': User,
                'fields': ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
            },
            'employees': {
                'model': 'employees.Employee',
                'fields': ['emp_code', 'first_name', 'last_name', 'email', 'mobile', 'hire_date', 'emp_status']
            },
            'products': {
                'model': 'inventory.TblProducts',
                'fields': ['product_id', 'product_name', 'qte_in_stock', 'unit_price', 'cat_name', 'unit_name']
            },
            'tasks': {
                'model': 'tasks.Task',
                'fields': ['title', 'status', 'priority', 'start_date', 'end_date', 'progress']
            }
        }

        exported_files = []

        for table_name, config in models_config.items():
            try:
                if isinstance(config['model'], str):
                    app_label, model_class = config['model'].split('.')
                    model = apps.get_model(app_label, model_class)
                else:
                    model = config['model']

                csv_file = os.path.join(export_dir, f'{table_name}.csv')

                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)

                    # Write header
                    writer.writerow(config['fields'])

                    # Write data
                    for obj in model.objects.all():
                        row = []
                        for field in config['fields']:
                            value = getattr(obj, field, '')
                            if isinstance(value, (datetime, date)):
                                value = value.isoformat()
                            elif isinstance(value, Decimal):
                                value = float(value)
                            row.append(value)
                        writer.writerow(row)

                exported_files.append(csv_file)
                print(f"  ✓ تم تصدير {table_name} إلى CSV")

            except Exception as e:
                print(f"  ⚠️  تعذر تصدير {table_name}: {e}")

        # Create zip file
        zip_file = os.path.join(self.output_dir, f'csv_export_{timestamp}.zip')
        with zipfile.ZipFile(zip_file, 'w') as zf:
            for file_path in exported_files:
                zf.write(file_path, os.path.basename(file_path))

        print(f"✅ تم تصدير البيانات إلى: {zip_file}")
        return zip_file

    def export_to_excel(self, timestamp):
        """Export data to Excel format"""
        try:
            import pandas as pd
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill

            excel_file = os.path.join(self.output_dir, f'test_data_{timestamp}.xlsx')

            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Export Users
                if User.objects.exists():
                    users_data = []
                    for user in User.objects.all():
                        users_data.append({
                            'اسم المستخدم': user.username,
                            'البريد الإلكتروني': user.email,
                            'الاسم الأول': user.first_name,
                            'الاسم الأخير': user.last_name,
                            'نشط': 'نعم' if user.is_active else 'لا',
                            'تاريخ التسجيل': user.date_joined.strftime('%Y-%m-%d') if user.date_joined else ''
                        })

                    df_users = pd.DataFrame(users_data)
                    df_users.to_excel(writer, sheet_name='المستخدمين', index=False)

                # Export Employees
                try:
                    from employees.models import Employee
                    if Employee.objects.exists():
                        employees_data = []
                        for emp in Employee.objects.all():
                            employees_data.append({
                                'رمز الموظف': emp.emp_code,
                                'الاسم الكامل': f"{emp.first_name} {emp.last_name}",
                                'البريد الإلكتروني': emp.email,
                                'الهاتف': emp.mobile,
                                'تاريخ التوظيف': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else '',
                                'الحالة': emp.emp_status,
                                'القسم': emp.dept.dept_name if emp.dept else '',
                                'الوظيفة': emp.job.job_title if emp.job else ''
                            })

                        df_employees = pd.DataFrame(employees_data)
                        df_employees.to_excel(writer, sheet_name='الموظفين', index=False)
                except ImportError:
                    pass

                # Export Products
                try:
                    from inventory.models import TblProducts
                    if TblProducts.objects.exists():
                        products_data = []
                        for product in TblProducts.objects.all():
                            products_data.append({
                                'رمز المنتج': product.product_id,
                                'اسم المنتج': product.product_name,
                                'الكمية المتاحة': float(product.qte_in_stock) if product.qte_in_stock else 0,
                                'سعر الوحدة': float(product.unit_price) if product.unit_price else 0,
                                'الفئة': product.cat_name,
                                'الوحدة': product.unit_name,
                                'الموقع': product.location
                            })

                        df_products = pd.DataFrame(products_data)
                        df_products.to_excel(writer, sheet_name='المنتجات', index=False)
                except ImportError:
                    pass

                # Export Tasks
                try:
                    from tasks.models import Task
                    if Task.objects.exists():
                        tasks_data = []
                        for task in Task.objects.all():
                            tasks_data.append({
                                'عنوان المهمة': task.title,
                                'الحالة': task.status,
                                'الأولوية': task.priority,
                                'تاريخ البداية': task.start_date.strftime('%Y-%m-%d') if task.start_date else '',
                                'تاريخ النهاية': task.end_date.strftime('%Y-%m-%d') if task.end_date else '',
                                'نسبة الإنجاز': task.progress,
                                'المُكلف': task.assigned_to.username if task.assigned_to else '',
                                'المُنشئ': task.created_by.username if task.created_by else ''
                            })

                        df_tasks = pd.DataFrame(tasks_data)
                        df_tasks.to_excel(writer, sheet_name='المهام', index=False)
                except ImportError:
                    pass

            print(f"✅ تم تصدير البيانات إلى Excel: {excel_file}")
            return excel_file

        except ImportError:
            print("⚠️  pandas و openpyxl غير متاحين - تعذر التصدير إلى Excel")
            return None


class TestDataImporter:
    """Import test data from various formats"""

    def __init__(self):
        """__init__ function"""
        self.imported_objects = {}

    def import_from_json(self, json_file):
        """Import data from JSON file"""
        print(f"📥 استيراد البيانات من: {json_file}")

        if not os.path.exists(json_file):
            raise FileNotFoundError(f"File not found: {json_file}")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with transaction.atomic():
            # Clear existing data first
            self.clear_existing_data()

            # Import data
            for obj_data in data:
                try:
                    # Deserialize and save
                    for deserialized_obj in serializers.deserialize('json', [obj_data]):
                        deserialized_obj.save()

                        model_name = deserialized_obj.object.__class__.__name__
                        if model_name not in self.imported_objects:
                            self.imported_objects[model_name] = 0
                        self.imported_objects[model_name] += 1

                except Exception as e:
                    print(f"  ⚠️  خطأ في استيراد كائن: {e}")

        print("✅ تم استيراد البيانات بنجاح!")
        self.print_import_summary()

        return self.imported_objects

    def clear_existing_data(self):
        """Clear existing test data"""
        print("🧹 مسح البيانات الموجودة...")

        # Define models to clear in reverse dependency order
        models_to_clear = [
            'Purchase_orders.PurchaseRequestItem',
            'Purchase_orders.PurchaseRequest',
            'Purchase_orders.Vendor',
            'meetings.Attendee',
            'meetings.Meeting',
            'tasks.Task',
            'tasks.TaskCategory',
            'inventory.TblProducts',
            'inventory.TblSuppliers',
            'inventory.TblUnitsSpareparts',
            'inventory.TblCategories',
            'employees.Employee',
            'org.Job',
            'org.Department',
            'org.Branch',
        ]

        for model_name in models_to_clear:
            try:
                app_label, model_class = model_name.split('.')
                model = apps.get_model(app_label, model_class)
                count = model.objects.count()
                if count > 0:
                    model.objects.all().delete()
                    print(f"  • تم مسح {count} من {model_name}")
            except Exception as e:
                print(f"  ⚠️  تعذر مسح {model_name}: {e}")

        # Clear non-admin users
        non_admin_users = User.objects.filter(is_superuser=False)
        user_count = non_admin_users.count()
        if user_count > 0:
            non_admin_users.delete()
            print(f"  • تم مسح {user_count} من المستخدمين العاديين")

    def print_import_summary(self):
        """Print summary of imported objects"""
        print("\n📊 ملخص البيانات المستوردة:")
        print("=" * 40)

        for model_name, count in self.imported_objects.items():
            print(f"  • {model_name}: {count}")

        print("=" * 40)


class TestScenarioExporter:
    """Export specific test scenarios"""

    def __init__(self, output_dir='test_scenarios'):
        """__init__ function"""
        self.output_dir = output_dir
        self.ensure_output_dir()

    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export_demo_scenario(self):
        """Export demo scenario data"""
        print("🎭 تصدير سيناريو العرض التوضيحي...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        scenario_file = os.path.join(self.output_dir, f'demo_scenario_{timestamp}.json')

        # Export specific demo data
        demo_data = {
            'scenario_name': 'العرض التوضيحي',
            'description': 'بيانات تجريبية للعرض التوضيحي والتدريب',
            'created_at': datetime.now().isoformat(),
            'data': {}
        }

        # Export key demo objects
        try:
            # Export sample users
            demo_users = User.objects.filter(username__startswith='user')[:5]
            demo_data['data']['users'] = json.loads(serializers.serialize('json', demo_users))

            # Export sample employees
            from employees.models import Employee
            demo_employees = Employee.objects.all()[:10]
            demo_data['data']['employees'] = json.loads(serializers.serialize('json', demo_employees))

            # Export sample products
            from inventory.models import TblProducts
            demo_products = TblProducts.objects.all()[:20]
            demo_data['data']['products'] = json.loads(serializers.serialize('json', demo_products))

            # Export sample tasks
            from tasks.models import Task
            demo_tasks = Task.objects.all()[:15]
            demo_data['data']['tasks'] = json.loads(serializers.serialize('json', demo_tasks))

        except ImportError as e:
            print(f"  ⚠️  بعض النماذج غير متاحة: {e}")

        # Write scenario file
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(demo_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ تم تصدير سيناريو العرض التوضيحي: {scenario_file}")
        return scenario_file

    def export_performance_scenario(self):
        """Export performance testing scenario"""
        print("⚡ تصدير سيناريو اختبار الأداء...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        scenario_file = os.path.join(self.output_dir, f'performance_scenario_{timestamp}.json')

        # Create performance test configuration
        performance_config = {
            'scenario_name': 'اختبار الأداء',
            'description': 'إعدادات اختبار الأداء والحمولة',
            'created_at': datetime.now().isoformat(),
            'config': {
                'concurrent_users': 100,
                'test_duration_minutes': 30,
                'ramp_up_time_seconds': 300,
                'data_volumes': {
                    'users': 1000,
                    'employees': 2000,
                    'products': 5000,
                    'tasks': 10000,
                    'meetings': 2000
                },
                'test_endpoints': [
                    '/api/v1/employees/',
                    '/api/v1/products/',
                    '/api/v1/tasks/',
                    '/api/v1/meetings/',
                    '/dashboard/',
                    '/reports/employees/',
                    '/reports/inventory/'
                ]
            }
        }

        # Write configuration file
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(performance_config, f, ensure_ascii=False, indent=2)

        print(f"✅ تم تصدير إعدادات اختبار الأداء: {scenario_file}")
        return scenario_file


def export_all_test_data(format='json'):
    """Main function to export all test data"""
    print("🚀 بدء تصدير جميع البيانات التجريبية...")

    exporter = TestDataExporter()
    exported_file = exporter.export_all_data(format)

    # Also export scenarios
    scenario_exporter = TestScenarioExporter()
    demo_file = scenario_exporter.export_demo_scenario()
    performance_file = scenario_exporter.export_performance_scenario()

    print("✅ تم تصدير جميع البيانات والسيناريوهات بنجاح!")

    return {
        'main_export': exported_file,
        'demo_scenario': demo_file,
        'performance_scenario': performance_file
    }


def import_test_data(json_file):
    """Main function to import test data"""
    print("🚀 بدء استيراد البيانات التجريبية...")

    importer = TestDataImporter()
    imported_objects = importer.import_from_json(json_file)

    print("✅ تم استيراد البيانات بنجاح!")
    return imported_objects


if __name__ == "__main__":
    # Export data when run directly
    export_all_test_data('json')
