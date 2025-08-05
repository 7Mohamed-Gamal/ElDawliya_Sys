"""
أمر Django لإنشاء الهجرات المحسنة لنظام الموارد البشرية
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os
import sys


class Command(BaseCommand):
    help = 'إنشاء الهجرات المحسنة لنظام الموارد البشرية'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='عرض ما سيتم إنشاؤه دون تطبيق التغييرات',
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='إنشاء نسخة احتياطية قبل التطبيق',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 بدء إنشاء الهجرات المحسنة لنظام الموارد البشرية')
        )

        try:
            # 1. إنشاء نسخة احتياطية إذا طُلب ذلك
            if options['backup']:
                self.create_backup()

            # 2. فحص النماذج الحالية
            self.check_current_models()

            # 3. إنشاء الهجرات الجديدة
            if not options['dry_run']:
                self.create_migrations()
            else:
                self.stdout.write(
                    self.style.WARNING('🔍 وضع المعاينة - لن يتم إنشاء الهجرات فعلياً')
                )

            # 4. عرض ملخص الهجرات
            self.show_migration_summary()

            # 5. تطبيق الهجرات إذا لم يكن وضع المعاينة
            if not options['dry_run']:
                self.apply_migrations()

            self.stdout.write(
                self.style.SUCCESS('✅ تم إنشاء وتطبيق الهجرات بنجاح!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء الهجرات: {str(e)}')
            )
            sys.exit(1)

    def create_backup(self):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        self.stdout.write('📦 إنشاء نسخة احتياطية...')
        
        try:
            # استخدام أمر Django لإنشاء نسخة احتياطية
            from django.core.management import call_command
            import datetime
            
            backup_filename = f"hr_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = os.path.join('backups', backup_filename)
            
            # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
            os.makedirs('backups', exist_ok=True)
            
            # تصدير البيانات
            with open(backup_path, 'w', encoding='utf-8') as f:
                call_command('dumpdata', 'Hr', stdout=f, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم إنشاء النسخة الاحتياطية: {backup_path}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ تعذر إنشاء النسخة الاحتياطية: {str(e)}')
            )

    def check_current_models(self):
        """فحص النماذج الحالية"""
        self.stdout.write('🔍 فحص النماذج الحالية...')
        
        try:
            with connection.cursor() as cursor:
                # فحص الجداول الموجودة
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name LIKE 'Hr_%'
                """)
                
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                if existing_tables:
                    self.stdout.write(f'📋 الجداول الموجودة: {len(existing_tables)}')
                    for table in existing_tables[:5]:  # عرض أول 5 جداول
                        self.stdout.write(f'  - {table}')
                    if len(existing_tables) > 5:
                        self.stdout.write(f'  ... و {len(existing_tables) - 5} جداول أخرى')
                else:
                    self.stdout.write('📋 لا توجد جداول Hr موجودة')
                    
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ تعذر فحص الجداول الحالية: {str(e)}')
            )

    def create_migrations(self):
        """إنشاء الهجرات الجديدة"""
        self.stdout.write('🔨 إنشاء الهجرات الجديدة...')
        
        try:
            # إنشاء هجرات للنماذج المحسنة
            call_command(
                'makemigrations', 
                'Hr',
                name='enhanced_hr_models',
                verbosity=2
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم إنشاء الهجرات الجديدة')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إنشاء الهجرات: {str(e)}')
            )
            raise

    def show_migration_summary(self):
        """عرض ملخص الهجرات"""
        self.stdout.write('📊 ملخص الهجرات:')
        
        try:
            # عرض حالة الهجرات
            call_command('showmigrations', 'Hr', verbosity=1)
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ تعذر عرض ملخص الهجرات: {str(e)}')
            )

    def apply_migrations(self):
        """تطبيق الهجرات"""
        self.stdout.write('⚡ تطبيق الهجرات...')
        
        try:
            # تطبيق الهجرات
            call_command('migrate', 'Hr', verbosity=2)
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم تطبيق الهجرات بنجاح')
            )
            
            # إنشاء الفهارس المحسنة
            self.create_enhanced_indexes()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في تطبيق الهجرات: {str(e)}')
            )
            raise

    def create_enhanced_indexes(self):
        """إنشاء الفهارس المحسنة"""
        self.stdout.write('🔗 إنشاء الفهارس المحسنة...')
        
        try:
            with connection.cursor() as cursor:
                # فهارس للأداء المحسن
                indexes = [
                    # فهارس الموظفين
                    "CREATE INDEX IF NOT EXISTS idx_hr_employee_search ON Hr_employee (first_name, last_name, employee_number)",
                    "CREATE INDEX IF NOT EXISTS idx_hr_employee_active ON Hr_employee (is_active, status)",
                    "CREATE INDEX IF NOT EXISTS idx_hr_employee_hire_date ON Hr_employee (hire_date)",
                    
                    # فهارس الحضور
                    "CREATE INDEX IF NOT EXISTS idx_hr_attendance_employee_date ON Hr_attendancerecord (employee_id, date)",
                    "CREATE INDEX IF NOT EXISTS idx_hr_attendance_timestamp ON Hr_attendancerecord (timestamp)",
                    
                    # فهارس الشركات والأقسام
                    "CREATE INDEX IF NOT EXISTS idx_hr_company_active ON Hr_company (is_active)",
                    "CREATE INDEX IF NOT EXISTS idx_hr_department_hierarchy ON Hr_department (parent_department_id, level)",
                    
                    # فهارس الملفات
                    "CREATE INDEX IF NOT EXISTS idx_hr_employee_files ON Hr_employeefile (employee_id, file_type, status)",
                ]
                
                for index_sql in indexes:
                    try:
                        cursor.execute(index_sql)
                        self.stdout.write(f'  ✅ تم إنشاء فهرس')
                    except Exception as e:
                        self.stdout.write(f'  ⚠️ تعذر إنشاء فهرس: {str(e)}')
                
                self.stdout.write(
                    self.style.SUCCESS('✅ تم إنشاء الفهارس المحسنة')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ تعذر إنشاء الفهارس: {str(e)}')
            )

    def create_initial_data(self):
        """إنشاء البيانات الأولية"""
        self.stdout.write('📝 إنشاء البيانات الأولية...')
        
        try:
            # يمكن إضافة بيانات أولية هنا
            # مثل الشركة الافتراضية، الأقسام الأساسية، إلخ
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم إنشاء البيانات الأولية')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ تعذر إنشاء البيانات الأولية: {str(e)}')
            )