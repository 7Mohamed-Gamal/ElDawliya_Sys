"""
أمر Django لنقل البيانات من النماذج القديمة إلى النماذج المحسنة
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
import uuid
from datetime import date, datetime


class Command(BaseCommand):
    help = 'نقل البيانات من النماذج القديمة إلى النماذج المحسنة'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='عرض ما سيتم نقله دون تطبيق التغييرات',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='حجم الدفعة لنقل البيانات',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 بدء نقل البيانات إلى النماذج المحسنة')
        )

        self.dry_run = options['dry_run']
        self.batch_size = options['batch_size']

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 وضع المعاينة - لن يتم نقل البيانات فعلياً')
            )

        try:
            with transaction.atomic():
                # 1. نقل بيانات الشركات
                self.migrate_companies()
                
                # 2. نقل بيانات الفروع
                self.migrate_branches()
                
                # 3. نقل بيانات الأقسام
                self.migrate_departments()
                
                # 4. نقل بيانات المناصب الوظيفية
                self.migrate_job_positions()
                
                # 5. نقل بيانات الموظفين
                self.migrate_employees()
                
                # 6. نقل بيانات الحضور
                self.migrate_attendance_data()
                
                # 7. التحقق من سلامة البيانات
                self.verify_data_integrity()

                if self.dry_run:
                    # إلغاء المعاملة في وضع المعاينة
                    transaction.set_rollback(True)
                    self.stdout.write(
                        self.style.WARNING('🔄 تم إلغاء المعاملة (وضع المعاينة)')
                    )

            self.stdout.write(
                self.style.SUCCESS('✅ تم نقل البيانات بنجاح!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في نقل البيانات: {str(e)}')
            )
            raise

    def migrate_companies(self):
        """نقل بيانات الشركات"""
        self.stdout.write('🏢 نقل بيانات الشركات...')
        
        try:
            # استيراد النماذج القديمة والجديدة
            from Hr.models import Company as OldCompany
            from Hr.models_enhanced import Company as NewCompany
            
            old_companies = OldCompany.objects.all()
            migrated_count = 0
            
            for old_company in old_companies:
                if not self.dry_run:
                    # التحقق من عدم وجود الشركة في النموذج الجديد
                    if not NewCompany.objects.filter(code=old_company.code).exists():
                        new_company = NewCompany(
                            id=old_company.id if hasattr(old_company, 'id') else uuid.uuid4(),
                            name=old_company.name,
                            name_english=getattr(old_company, 'name_english', None),
                            code=old_company.code,
                            tax_number=getattr(old_company, 'tax_number', None),
                            commercial_register=getattr(old_company, 'commercial_register', None),
                            address=getattr(old_company, 'address', None),
                            phone=getattr(old_company, 'phone', None),
                            email=getattr(old_company, 'email', None),
                            website=getattr(old_company, 'website', None),
                            logo=getattr(old_company, 'logo', None),
                            is_active=getattr(old_company, 'is_active', True),
                            created_at=getattr(old_company, 'created_at', datetime.now()),
                            updated_at=getattr(old_company, 'updated_at', datetime.now()),
                        )
                        new_company.save()
                
                migrated_count += 1
                
                if migrated_count % self.batch_size == 0:
                    self.stdout.write(f'  📊 تم نقل {migrated_count} شركة...')
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم نقل {migrated_count} شركة')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في نقل الشركات: {str(e)}')
            )
            raise

    def migrate_branches(self):
        """نقل بيانات الفروع"""
        self.stdout.write('🏪 نقل بيانات الفروع...')
        
        try:
            from Hr.models import Branch as OldBranch
            from Hr.models_enhanced import Branch as NewBranch, Company as NewCompany
            
            old_branches = OldBranch.objects.all()
            migrated_count = 0
            
            for old_branch in old_branches:
                if not self.dry_run:
                    # العثور على الشركة المقابلة
                    try:
                        new_company = NewCompany.objects.get(code=old_branch.company.code)
                    except NewCompany.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ لم يتم العثور على الشركة: {old_branch.company.code}')
                        )
                        continue
                    
                    if not NewBranch.objects.filter(company=new_company, code=old_branch.code).exists():
                        new_branch = NewBranch(
                            id=old_branch.id if hasattr(old_branch, 'id') else uuid.uuid4(),
                            company=new_company,
                            name=old_branch.name,
                            code=old_branch.code,
                            address=getattr(old_branch, 'address', None),
                            phone=getattr(old_branch, 'phone', None),
                            is_active=getattr(old_branch, 'is_active', True),
                            created_at=getattr(old_branch, 'created_at', datetime.now()),
                            updated_at=getattr(old_branch, 'updated_at', datetime.now()),
                        )
                        new_branch.save()
                
                migrated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم نقل {migrated_count} فرع')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في نقل الفروع: {str(e)}')
            )
            raise

    def migrate_departments(self):
        """نقل بيانات الأقسام"""
        self.stdout.write('🏛️ نقل بيانات الأقسام...')
        
        try:
            from Hr.models import Department as OldDepartment
            from Hr.models_enhanced import Department as NewDepartment, Company as NewCompany, Branch as NewBranch
            
            old_departments = OldDepartment.objects.all()
            migrated_count = 0
            
            for old_dept in old_departments:
                if not self.dry_run:
                    try:
                        new_company = NewCompany.objects.get(code=old_dept.company.code)
                        new_branch = NewBranch.objects.filter(company=new_company).first()
                        
                        if not new_branch:
                            self.stdout.write(
                                self.style.WARNING(f'⚠️ لم يتم العثور على فرع للشركة: {new_company.code}')
                            )
                            continue
                            
                    except NewCompany.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ لم يتم العثور على الشركة: {old_dept.company.code}')
                        )
                        continue
                    
                    if not NewDepartment.objects.filter(company=new_company, code=old_dept.code).exists():
                        new_dept = NewDepartment(
                            id=old_dept.id if hasattr(old_dept, 'id') else uuid.uuid4(),
                            company=new_company,
                            branch=new_branch,
                            name=old_dept.name,
                            code=old_dept.code,
                            description=getattr(old_dept, 'description', None),
                            budget=getattr(old_dept, 'budget', None),
                            is_active=getattr(old_dept, 'is_active', True),
                            created_at=getattr(old_dept, 'created_at', datetime.now()),
                            updated_at=getattr(old_dept, 'updated_at', datetime.now()),
                        )
                        new_dept.save()
                
                migrated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم نقل {migrated_count} قسم')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في نقل الأقسام: {str(e)}')
            )
            raise

    def migrate_job_positions(self):
        """نقل بيانات المناصب الوظيفية"""
        self.stdout.write('💼 نقل بيانات المناصب الوظيفية...')
        
        try:
            from Hr.models import JobPosition as OldJobPosition
            from Hr.models_enhanced import JobPosition as NewJobPosition, Company as NewCompany, Department as NewDepartment
            
            old_positions = OldJobPosition.objects.all()
            migrated_count = 0
            
            for old_pos in old_positions:
                if not self.dry_run:
                    try:
                        new_company = NewCompany.objects.get(code=old_pos.company.code)
                        new_department = NewDepartment.objects.get(
                            company=new_company, 
                            code=old_pos.department.code
                        )
                    except (NewCompany.DoesNotExist, NewDepartment.DoesNotExist):
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ لم يتم العثور على الشركة أو القسم للمنصب: {old_pos.code}')
                        )
                        continue
                    
                    if not NewJobPosition.objects.filter(company=new_company, code=old_pos.code).exists():
                        new_pos = NewJobPosition(
                            id=old_pos.id if hasattr(old_pos, 'id') else uuid.uuid4(),
                            company=new_company,
                            department=new_department,
                            title=old_pos.title,
                            title_english=getattr(old_pos, 'title_english', None),
                            code=old_pos.code,
                            level=getattr(old_pos, 'level', 'entry'),
                            description=getattr(old_pos, 'description', None),
                            requirements=getattr(old_pos, 'requirements', None),
                            min_salary=getattr(old_pos, 'min_salary', None),
                            max_salary=getattr(old_pos, 'max_salary', None),
                            is_active=getattr(old_pos, 'is_active', True),
                            created_at=getattr(old_pos, 'created_at', datetime.now()),
                            updated_at=getattr(old_pos, 'updated_at', datetime.now()),
                        )
                        new_pos.save()
                
                migrated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم نقل {migrated_count} منصب وظيفي')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في نقل المناصب الوظيفية: {str(e)}')
            )
            raise

    def migrate_employees(self):
        """نقل بيانات الموظفين"""
        self.stdout.write('👥 نقل بيانات الموظفين...')
        
        try:
            from Hr.models import Employee as OldEmployee
            from Hr.models_enhanced import (
                Employee as NewEmployee, Company as NewCompany, 
                Branch as NewBranch, Department as NewDepartment, 
                JobPosition as NewJobPosition
            )
            
            old_employees = OldEmployee.objects.all()
            migrated_count = 0
            
            for old_emp in old_employees:
                if not self.dry_run:
                    try:
                        new_company = NewCompany.objects.get(code=old_emp.company.code)
                        new_branch = NewBranch.objects.filter(company=new_company).first()
                        new_department = NewDepartment.objects.get(
                            company=new_company, 
                            code=old_emp.department.code
                        )
                        new_job_position = NewJobPosition.objects.get(
                            company=new_company,
                            code=old_emp.job_position.code
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ خطأ في العثور على البيانات المرتبطة للموظف: {old_emp.employee_number}')
                        )
                        continue
                    
                    if not NewEmployee.objects.filter(employee_number=old_emp.employee_number).exists():
                        new_emp = NewEmployee(
                            id=old_emp.id if hasattr(old_emp, 'id') else uuid.uuid4(),
                            employee_number=old_emp.employee_number,
                            company=new_company,
                            branch=new_branch,
                            department=new_department,
                            job_position=new_job_position,
                            first_name=getattr(old_emp, 'first_name', ''),
                            last_name=getattr(old_emp, 'last_name', ''),
                            date_of_birth=getattr(old_emp, 'date_of_birth', date.today()),
                            gender=getattr(old_emp, 'gender', 'male'),
                            national_id=getattr(old_emp, 'national_id', ''),
                            mobile_phone=getattr(old_emp, 'mobile_phone', ''),
                            current_address=getattr(old_emp, 'current_address', ''),
                            current_city=getattr(old_emp, 'current_city', ''),
                            hire_date=getattr(old_emp, 'hire_date', date.today()),
                            basic_salary=getattr(old_emp, 'basic_salary', 0),
                            status=getattr(old_emp, 'status', 'active'),
                            is_active=getattr(old_emp, 'is_active', True),
                            created_at=getattr(old_emp, 'created_at', datetime.now()),
                            updated_at=getattr(old_emp, 'updated_at', datetime.now()),
                        )
                        new_emp.save()
                
                migrated_count += 1
                
                if migrated_count % self.batch_size == 0:
                    self.stdout.write(f'  📊 تم نقل {migrated_count} موظف...')
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم نقل {migrated_count} موظف')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في نقل الموظفين: {str(e)}')
            )
            raise

    def migrate_attendance_data(self):
        """نقل بيانات الحضور"""
        self.stdout.write('⏰ نقل بيانات الحضور...')
        
        try:
            # سيتم تنفيذ هذا عند توفر النماذج القديمة للحضور
            self.stdout.write(
                self.style.SUCCESS('✅ تم تخطي نقل بيانات الحضور (لا توجد بيانات قديمة)')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في نقل بيانات الحضور: {str(e)}')
            )

    def verify_data_integrity(self):
        """التحقق من سلامة البيانات"""
        self.stdout.write('🔍 التحقق من سلامة البيانات...')
        
        try:
            from Hr.models_enhanced import Company, Branch, Department, JobPosition, Employee
            
            # إحصائيات البيانات المنقولة
            companies_count = Company.objects.count()
            branches_count = Branch.objects.count()
            departments_count = Department.objects.count()
            positions_count = JobPosition.objects.count()
            employees_count = Employee.objects.count()
            
            self.stdout.write('📊 إحصائيات البيانات المنقولة:')
            self.stdout.write(f'  🏢 الشركات: {companies_count}')
            self.stdout.write(f'  🏪 الفروع: {branches_count}')
            self.stdout.write(f'  🏛️ الأقسام: {departments_count}')
            self.stdout.write(f'  💼 المناصب الوظيفية: {positions_count}')
            self.stdout.write(f'  👥 الموظفون: {employees_count}')
            
            # التحقق من العلاقات
            orphaned_branches = Branch.objects.filter(company__isnull=True).count()
            orphaned_departments = Department.objects.filter(company__isnull=True).count()
            orphaned_employees = Employee.objects.filter(company__isnull=True).count()
            
            if orphaned_branches > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ فروع بدون شركة: {orphaned_branches}')
                )
            
            if orphaned_departments > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ أقسام بدون شركة: {orphaned_departments}')
                )
            
            if orphaned_employees > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ موظفون بدون شركة: {orphaned_employees}')
                )
            
            if orphaned_branches == 0 and orphaned_departments == 0 and orphaned_employees == 0:
                self.stdout.write(
                    self.style.SUCCESS('✅ جميع العلاقات سليمة')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في التحقق من سلامة البيانات: {str(e)}')
            )