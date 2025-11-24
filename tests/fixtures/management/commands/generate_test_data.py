"""
Django Management Command to Generate Test Data
==============================================

This command generates comprehensive test data for the ElDawliya system.
It creates realistic Arabic data for all modules including HR, inventory,
meetings, tasks, and purchase orders.

Usage:
    python manage.py generate_test_data
    python manage.py generate_test_data --users 50 --employees 100
    python manage.py generate_test_data --clear-existing
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model
from tests.fixtures.base_fixtures import ComprehensiveFixtureGenerator

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate comprehensive test data for ElDawliya system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=25,
            help='Number of users to create (default: 25)'
        )
        
        parser.add_argument(
            '--employees',
            type=int,
            default=50,
            help='Number of employees to create (default: 50)'
        )
        
        parser.add_argument(
            '--products',
            type=int,
            default=100,
            help='Number of products to create (default: 100)'
        )
        
        parser.add_argument(
            '--meetings',
            type=int,
            default=30,
            help='Number of meetings to create (default: 30)'
        )
        
        parser.add_argument(
            '--tasks',
            type=int,
            default=100,
            help='Number of tasks to create (default: 100)'
        )
        
        parser.add_argument(
            '--purchase-requests',
            type=int,
            default=50,
            help='Number of purchase requests to create (default: 50)'
        )
        
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing test data before generating new data'
        )
        
        parser.add_argument(
            '--demo-mode',
            action='store_true',
            help='Generate demo data with predefined scenarios'
        )
        
        parser.add_argument(
            '--performance-test',
            action='store_true',
            help='Generate large dataset for performance testing'
        )
        
        parser.add_argument(
            '--training-scenarios',
            action='store_true',
            help='Generate specialized training scenarios'
        )
        
        parser.add_argument(
            '--edge-cases',
            action='store_true',
            help='Generate edge case scenarios for testing limits'
        )
        
        parser.add_argument(
            '--export-data',
            choices=['json', 'csv', 'excel'],
            help='Export generated data in specified format'
        )
        
        parser.add_argument(
            '--scenario-type',
            choices=['minimal', 'standard', 'comprehensive', 'training', 'demo'],
            default='standard',
            help='Type of scenario to generate (default: standard)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 بدء إنشاء البيانات التجريبية لنظام الدولية...')
        )
        
        try:
            with transaction.atomic():
                # Clear existing data if requested
                if options['clear_existing']:
                    self.clear_existing_data()
                
                # Handle specialized scenarios
                if options['training_scenarios']:
                    self.generate_training_scenarios()
                    return
                
                if options['edge_cases']:
                    self.generate_edge_case_scenarios()
                    return
                
                # Determine scenario type and counts
                scenario_type = options['scenario_type']
                created_objects = self.generate_scenario_data(scenario_type, options)
                
                # Export data if requested
                if options['export_data']:
                    self.export_generated_data(options['export_data'])
                
                self.stdout.write(
                    self.style.SUCCESS('✅ تم إنشاء جميع البيانات التجريبية بنجاح!')
                )
                
                # Print login information
                self.print_login_info()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء البيانات: {str(e)}')
            )
            raise CommandError(f'Failed to generate test data: {str(e)}')
    
    def generate_scenario_data(self, scenario_type, options):
        """Generate data based on scenario type"""
        
        if scenario_type == 'minimal':
            counts = {
                'users_count': 5,
                'employees_count': 10,
                'products_count': 20,
                'meetings_count': 5,
                'tasks_count': 15,
                'purchase_requests_count': 5
            }
            self.stdout.write(
                self.style.WARNING('🔹 السيناريو المبسط: بيانات أساسية للاختبار السريع...')
            )
        
        elif scenario_type == 'comprehensive':
            counts = {
                'users_count': 100,
                'employees_count': 200,
                'products_count': 500,
                'meetings_count': 100,
                'tasks_count': 500,
                'purchase_requests_count': 200
            }
            self.stdout.write(
                self.style.WARNING('🔸 السيناريو الشامل: بيانات كاملة للاختبار المتقدم...')
            )
        
        elif scenario_type == 'training':
            counts = {
                'users_count': 20,
                'employees_count': 40,
                'products_count': 80,
                'meetings_count': 25,
                'tasks_count': 60,
                'purchase_requests_count': 30
            }
            self.stdout.write(
                self.style.WARNING('🎓 سيناريو التدريب: بيانات مُحسنة للتدريب والتعلم...')
            )
        
        elif scenario_type == 'demo':
            counts = {
                'users_count': 15,
                'employees_count': 30,
                'products_count': 50,
                'meetings_count': 20,
                'tasks_count': 50,
                'purchase_requests_count': 25
            }
            self.stdout.write(
                self.style.WARNING('🎭 سيناريو العرض التوضيحي: بيانات للعروض والتقديمات...')
            )
        
        elif options['performance_test']:
            counts = {
                'users_count': 200,
                'employees_count': 500,
                'products_count': 1000,
                'meetings_count': 200,
                'tasks_count': 1000,
                'purchase_requests_count': 300
            }
            self.stdout.write(
                self.style.WARNING('⚡ وضع اختبار الأداء: إنشاء بيانات كبيرة...')
            )
        
        else:  # standard
            counts = {
                'users_count': options['users'],
                'employees_count': options['employees'],
                'products_count': options['products'],
                'meetings_count': options['meetings'],
                'tasks_count': options['tasks'],
                'purchase_requests_count': options['purchase_requests']
            }
            self.stdout.write(
                self.style.WARNING('📊 السيناريو القياسي: بيانات متوازنة للاختبار العام...')
            )
        
        # Generate fixtures
        generator = ComprehensiveFixtureGenerator()
        created_objects = generator.generate_all_fixtures(**counts)
        
        # Generate additional scenarios based on type
        if scenario_type == 'demo' or options.get('demo_mode'):
            self.generate_demo_scenarios(created_objects)
        
        if scenario_type == 'training':
            self.generate_additional_training_data(created_objects)
        
        return created_objects
    
    def generate_training_scenarios(self):
        """Generate specialized training scenarios"""
        self.stdout.write(
            self.style.WARNING('🎓 إنشاء السيناريوهات التدريبية المتخصصة...')
        )
        
        try:
            from tests.fixtures.specialized_scenarios import TrainingScenarioGenerator
            
            training_generator = TrainingScenarioGenerator()
            training_data = training_generator.generate_complete_training_environment()
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم إنشاء جميع السيناريوهات التدريبية بنجاح!')
            )
            
            # Print training-specific login info
            self.print_training_login_info()
            
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ تعذر استيراد مولد السيناريوهات التدريبية: {str(e)}')
            )
    
    def generate_edge_case_scenarios(self):
        """Generate edge case scenarios for testing limits"""
        self.stdout.write(
            self.style.WARNING('⚠️ إنشاء سيناريوهات الحالات الحدية...')
        )
        
        try:
            from tests.fixtures.specialized_scenarios import EdgeCaseScenarioGenerator
            
            edge_generator = EdgeCaseScenarioGenerator()
            edge_data = edge_generator.create_data_limit_scenarios()
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم إنشاء سيناريوهات الحالات الحدية بنجاح!')
            )
            
            self.stdout.write(
                self.style.WARNING('⚠️ تحذير: هذه البيانات تحتوي على قيم متطرفة لاختبار حدود النظام')
            )
            
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ تعذر استيراد مولد الحالات الحدية: {str(e)}')
            )
    
    def generate_additional_training_data(self, created_objects):
        """Generate additional training-specific data"""
        self.stdout.write('📚 إضافة بيانات تدريبية متخصصة...')
        
        try:
            from tests.fixtures.specialized_scenarios import DemoScenarioGenerator
            
            demo_generator = DemoScenarioGenerator()
            demo_generator.create_executive_dashboard_demo()
            demo_generator.create_success_story_demo()
            
            self.stdout.write('  • تم إنشاء بيانات لوحة التحكم التنفيذية')
            self.stdout.write('  • تم إنشاء قصة نجاح توضيحية')
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ تعذر إنشاء بعض البيانات التدريبية: {str(e)}')
            )
    
    def export_generated_data(self, export_format):
        """Export generated data in specified format"""
        self.stdout.write(f'📤 تصدير البيانات بصيغة {export_format.upper()}...')
        
        try:
            from tests.fixtures.data_export_import import TestDataExporter
            
            exporter = TestDataExporter()
            exported_file = exporter.export_all_data(export_format)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم تصدير البيانات إلى: {exported_file}')
            )
            
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ تعذر استيراد مُصدر البيانات: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في تصدير البيانات: {str(e)}')
            )
    
    def print_training_login_info(self):
        """Print login information for training scenarios"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎓 معلومات تسجيل الدخول للتدريب:'))
        self.stdout.write('='*60)
        
        # Training users
        training_accounts = [
            ('hr_manager', 'مدير الموارد البشرية'),
            ('hr_specialist', 'أخصائي موارد بشرية'),
            ('inv_manager', 'مدير المخزون'),
            ('warehouse_keeper', 'أمين المخزن'),
            ('project_manager', 'مدير المشاريع'),
            ('team_lead', 'قائد الفريق'),
            ('developer1', 'مطور أول'),
            ('developer2', 'مطور ثاني')
        ]
        
        self.stdout.write(self.style.HTTP_INFO('👥 حسابات التدريب المتخصصة:'))
        for username, description in training_accounts:
            self.stdout.write(f'   {description}: {username}')
        
        self.stdout.write('\n   كلمة المرور لجميع حسابات التدريب: training123')
        
        # Admin user
        self.stdout.write(f'\n{self.style.HTTP_INFO("👑 المدير العام:")}')
        self.stdout.write('   اسم المستخدم: admin')
        self.stdout.write('   كلمة المرور: admin123')
        
        # URLs
        self.stdout.write(f'\n{self.style.HTTP_INFO("🌐 الروابط المهمة:")}')
        self.stdout.write('   الصفحة الرئيسية: http://localhost:8000/')
        self.stdout.write('   لوحة الإدارة: http://localhost:8000/admin/')
        self.stdout.write('   واجهة API: http://localhost:8000/api/')
        self.stdout.write('   توثيق API: http://localhost:8000/api/docs/')
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('🎉 بيئة التدريب جاهزة للاستخدام!'))
        self.stdout.write('='*60)

    def clear_existing_data(self):
        """Clear existing test data"""
        self.stdout.write('🧹 مسح البيانات الموجودة...')
        
        # Import models
        try:
            from Purchase_orders.models import PurchaseRequest, PurchaseRequestItem, Vendor
            from tasks.models import Task, TaskStep, TaskCategory
            from meetings.models import Meeting, Attendee, MeetingTask, MeetingTaskStep
            from inventory.models import (
                TblProducts, TblInvoices, TblInvoiceitems, 
                TblCategories, TblSuppliers, TblUnitsSpareparts
            )
            from employees.models import Employee, EmployeeBankAccount, EmployeeDocument
            from org.models import Branch, Department, Job
            
            # Clear in reverse dependency order
            models_to_clear = [
                (PurchaseRequestItem, 'عناصر طلبات الشراء'),
                (PurchaseRequest, 'طلبات الشراء'),
                (Vendor, 'موردي الشراء'),
                (TaskStep, 'خطوات المهام'),
                (Task, 'المهام'),
                (TaskCategory, 'فئات المهام'),
                (MeetingTaskStep, 'خطوات مهام الاجتماعات'),
                (MeetingTask, 'مهام الاجتماعات'),
                (Attendee, 'حضور الاجتماعات'),
                (Meeting, 'الاجتماعات'),
                (TblInvoiceitems, 'عناصر الفواتير'),
                (TblInvoices, 'الفواتير'),
                (TblProducts, 'المنتجات'),
                (TblSuppliers, 'الموردين'),
                (TblCategories, 'فئات المنتجات'),
                (TblUnitsSpareparts, 'وحدات القياس'),
                (EmployeeDocument, 'مستندات الموظفين'),
                (EmployeeBankAccount, 'حسابات الموظفين البنكية'),
                (Employee, 'الموظفين'),
                (Job, 'الوظائف'),
                (Department, 'الأقسام'),
                (Branch, 'الفروع'),
            ]
            
            for model, name in models_to_clear:
                count = model.objects.count()
                if count > 0:
                    model.objects.all().delete()
                    self.stdout.write(f'  • تم مسح {count} من {name}')
            
            # Clear non-admin users
            non_admin_users = User.objects.filter(is_superuser=False)
            user_count = non_admin_users.count()
            if user_count > 0:
                non_admin_users.delete()
                self.stdout.write(f'  • تم مسح {user_count} من المستخدمين العاديين')
            
        except ImportError as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  تعذر مسح بعض البيانات: {str(e)}')
            )

    def generate_demo_scenarios(self, created_objects):
        """Generate specific demo scenarios"""
        self.stdout.write('🎭 إنشاء سيناريوهات العرض التوضيحي...')
        
        try:
            from tasks.models import Task, TaskStep
            from meetings.models import Meeting, MeetingTask, MeetingTaskStep
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            # Create a demo project scenario
            users = created_objects.get('users', [])
            if len(users) >= 3:
                project_manager = users[1]  # Skip admin
                team_member1 = users[2]
                team_member2 = users[3] if len(users) > 3 else users[2]
                
                # Create a project meeting
                project_meeting = Meeting.objects.create(
                    title='اجتماع مشروع تطوير النظام الإلكتروني',
                    date=timezone.now() + timedelta(days=7),
                    topic='مناقشة تطوير النظام الإلكتروني الجديد وتوزيع المهام',
                    status='pending',
                    created_by=project_manager
                )
                
                # Create project tasks
                project_tasks = [
                    {
                        'title': 'تحليل المتطلبات الوظيفية',
                        'description': 'تحليل وتوثيق جميع المتطلبات الوظيفية للنظام الجديد',
                        'assigned_to': team_member1,
                        'priority': 'high',
                        'days_offset': 1
                    },
                    {
                        'title': 'تصميم قاعدة البيانات',
                        'description': 'تصميم هيكل قاعدة البيانات وإنشاء المخططات اللازمة',
                        'assigned_to': team_member2,
                        'priority': 'high',
                        'days_offset': 3
                    },
                    {
                        'title': 'تطوير واجهة المستخدم',
                        'description': 'تطوير واجهة المستخدم الرئيسية للنظام',
                        'assigned_to': team_member1,
                        'priority': 'medium',
                        'days_offset': 7
                    }
                ]
                
                for task_data in project_tasks:
                    start_date = timezone.now() + timedelta(days=task_data['days_offset'])
                    end_date = start_date + timedelta(days=14)
                    
                    task = Task.objects.create(
                        title=task_data['title'],
                        description=task_data['description'],
                        assigned_to=task_data['assigned_to'],
                        created_by=project_manager,
                        meeting=project_meeting,
                        priority=task_data['priority'],
                        status='pending',
                        start_date=start_date,
                        end_date=end_date,
                        progress=0
                    )
                    
                    # Add some steps to the first task
                    if task_data['title'] == 'تحليل المتطلبات الوظيفية':
                        steps = [
                            'مراجعة النظام الحالي',
                            'مقابلة أصحاب المصلحة',
                            'توثيق المتطلبات',
                            'مراجعة وتأكيد المتطلبات'
                        ]
                        
                        for step_desc in steps:
                            TaskStep.objects.create(
                                task=task,
                                description=step_desc,
                                created_by=task_data['assigned_to']
                            )
                
                self.stdout.write('  • تم إنشاء سيناريو مشروع تطوير النظام')
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  تعذر إنشاء بعض السيناريوهات: {str(e)}')
            )

    def print_login_info(self):
        """Print login information for testing"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🔑 معلومات تسجيل الدخول للاختبار:'))
        self.stdout.write('='*60)
        
        # Admin user
        self.stdout.write(self.style.HTTP_INFO('👑 المدير العام:'))
        self.stdout.write('   اسم المستخدم: admin')
        self.stdout.write('   كلمة المرور: admin123')
        self.stdout.write('')
        
        # Regular users
        self.stdout.write(self.style.HTTP_INFO('👥 المستخدمين العاديين:'))
        self.stdout.write('   اسم المستخدم: user001, user002, user003, ...')
        self.stdout.write('   كلمة المرور: password123')
        self.stdout.write('')
        
        # URLs
        self.stdout.write(self.style.HTTP_INFO('🌐 الروابط المهمة:'))
        self.stdout.write('   الصفحة الرئيسية: http://localhost:8000/')
        self.stdout.write('   لوحة الإدارة: http://localhost:8000/admin/')
        self.stdout.write('   واجهة API: http://localhost:8000/api/')
        self.stdout.write('   توثيق API: http://localhost:8000/api/docs/')
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('🎉 البيانات جاهزة للاختبار والتدريب!'))
        self.stdout.write('='*60)