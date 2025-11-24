"""
Test Data Validation and Quality Assurance
==========================================

This module provides comprehensive validation for test data to ensure:
- Data integrity and consistency
- Realistic data patterns
- Performance optimization
- Edge case coverage
"""

import re
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db import models, connection
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.apps import apps

User = get_user_model()


class TestDataValidator:
    """Comprehensive test data validator"""

    def __init__(self):
        """__init__ function"""
        self.validation_results = {}
        self.warnings = []
        self.errors = []
        self.statistics = {}

    def validate_all_data(self, verbose=True):
        """Run comprehensive validation on all test data"""
        if verbose:
            print("🔍 بدء التحقق الشامل من جودة البيانات التجريبية...")

        validation_checks = [
            ('المستخدمين', self.validate_users),
            ('الهيكل التنظيمي', self.validate_organization),
            ('الموظفين', self.validate_employees),
            ('المخزون', self.validate_inventory),
            ('المهام', self.validate_tasks),
            ('الاجتماعات', self.validate_meetings),
            ('طلبات الشراء', self.validate_purchase_orders),
            ('الحضور والانصراف', self.validate_attendance),
            ('الرواتب', self.validate_payroll),
            ('الإجازات', self.validate_leaves),
        ]

        all_valid = True

        for check_name, validation_func in validation_checks:
            try:
                is_valid, details = validation_func()
                self.validation_results[check_name] = {
                    'valid': is_valid,
                    'details': details
                }

                if verbose:
                    if is_valid:
                        print(f"  ✅ {check_name}: صحيح ({details.get('count', 0)} عنصر)")
                    else:
                        print(f"  ❌ {check_name}: يحتوي على أخطاء")
                        for error in details.get('errors', []):
                            print(f"    • {error}")

                if not is_valid:
                    all_valid = False

            except Exception as e:
                error_msg = f"خطأ في التحقق من {check_name}: {str(e)}"
                self.errors.append(error_msg)
                if verbose:
                    print(f"  ⚠️  {error_msg}")
                all_valid = False

        # Run cross-validation checks
        cross_validation_result = self.validate_cross_references()
        if not cross_validation_result['valid']:
            all_valid = False
            if verbose:
                print(f"  ❌ التحقق المتقاطع: يحتوي على أخطاء")
                for error in cross_validation_result['errors']:
                    print(f"    • {error}")

        # Generate statistics
        self.generate_statistics()

        if verbose:
            if all_valid:
                print("✅ جميع البيانات صحيحة ومتسقة")
            else:
                print("❌ توجد أخطاء في البيانات - يرجى المراجعة")

            self.print_statistics()

        return {
            'valid': all_valid,
            'results': self.validation_results,
            'warnings': self.warnings,
            'errors': self.errors,
            'statistics': self.statistics
        }

    def validate_users(self):
        """Validate user data"""
        errors = []
        count = User.objects.count()

        if count == 0:
            return False, {'errors': ['لا توجد مستخدمين في النظام'], 'count': 0}

        # Check for duplicate usernames
        total_users = User.objects.count()
        unique_usernames = User.objects.values('username').distinct().count()

        if total_users != unique_usernames:
            errors.append(f"أسماء مستخدمين مكررة: {total_users - unique_usernames}")

        # Check for users without email
        users_without_email = User.objects.filter(email='').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
        if users_without_email > 0:
            errors.append(f"مستخدمين بدون بريد إلكتروني: {users_without_email}")

        # Check for invalid email formats
        invalid_emails = 0
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        for user in User.objects.exclude(email=''):
            if not email_pattern.match(user.email):
                invalid_emails += 1

        if invalid_emails > 0:
            errors.append(f"بريد إلكتروني بصيغة غير صحيحة: {invalid_emails}")

        # Check for users without names
        users_without_names = User.objects.filter(
            models.Q(first_name='').prefetch_related()  # TODO: Add appropriate prefetch_related fields | models.Q(last_name='')
        ).count()

        if users_without_names > 0:
            self.warnings.append(f"مستخدمين بدون أسماء كاملة: {users_without_names}")

        return len(errors) == 0, {
            'errors': errors,
            'count': count,
            'warnings': len(self.warnings)
        }

    def validate_organization(self):
        """Validate organizational structure"""
        errors = []

        try:
            from org.models import Branch, Department, Job

            # Check branches
            branches_count = Branch.objects.count()
            if branches_count == 0:
                errors.append("لا توجد فروع في النظام")

            # Check departments
            departments_count = Department.objects.count()
            if departments_count == 0:
                errors.append("لا توجد أقسام في النظام")

            # Check jobs
            jobs_count = Job.objects.count()
            if jobs_count == 0:
                errors.append("لا توجد وظائف في النظام")

            # Check for duplicate codes
            duplicate_branch_codes = Branch.objects.values('branch_code').annotate(
                count=models.Count('branch_code')
            ).filter(count__gt=1).count()

            if duplicate_branch_codes > 0:
                errors.append(f"رموز فروع مكررة: {duplicate_branch_codes}")

            duplicate_dept_codes = Department.objects.values('dept_code').annotate(
                count=models.Count('dept_code')
            ).filter(count__gt=1).count()

            if duplicate_dept_codes > 0:
                errors.append(f"رموز أقسام مكررة: {duplicate_dept_codes}")

            total_count = branches_count + departments_count + jobs_count

            return len(errors) == 0, {
                'errors': errors,
                'count': total_count,
                'branches': branches_count,
                'departments': departments_count,
                'jobs': jobs_count
            }

        except ImportError:
            return True, {'errors': [], 'count': 0, 'note': 'نماذج التنظيم غير متاحة'}

    def validate_employees(self):
        """Validate employee data"""
        errors = []

        try:
            from employees.models import Employee

            count = Employee.objects.count()
            if count == 0:
                return True, {'errors': [], 'count': 0, 'note': 'لا توجد موظفين'}

            # Check for employees without required fields
            employees_without_code = Employee.objects.filter(emp_code='').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if employees_without_code > 0:
                errors.append(f"موظفين بدون رمز: {employees_without_code}")

            # Check for duplicate employee codes
            total_employees = Employee.objects.count()
            unique_codes = Employee.objects.values('emp_code').distinct().count()

            if total_employees != unique_codes:
                errors.append(f"رموز موظفين مكررة: {total_employees - unique_codes}")

            # Check for employees without departments
            employees_without_dept = Employee.objects.filter(dept__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if employees_without_dept > 0:
                errors.append(f"موظفين بدون قسم: {employees_without_dept}")

            # Check for employees without jobs
            employees_without_job = Employee.objects.filter(job__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if employees_without_job > 0:
                errors.append(f"موظفين بدون وظيفة: {employees_without_job}")

            # Check for invalid hire dates (future dates)
            future_hire_dates = Employee.objects.filter(
                hire_date__gt=date.today().prefetch_related()  # TODO: Add appropriate prefetch_related fields
            ).count()
            if future_hire_dates > 0:
                self.warnings.append(f"موظفين بتاريخ توظيف مستقبلي: {future_hire_dates}")

            # Check for invalid birth dates
            invalid_birth_dates = Employee.objects.filter(
                models.Q(birth_date__gt=date.today().prefetch_related()  # TODO: Add appropriate prefetch_related fields) |
                models.Q(birth_date__lt=date.today() - timedelta(days=80*365))
            ).count()
            if invalid_birth_dates > 0:
                errors.append(f"موظفين بتاريخ ميلاد غير صحيح: {invalid_birth_dates}")

            # Check for invalid phone numbers
            invalid_phones = 0
            phone_pattern = re.compile(r'^05[0-9]{8}$')
            for employee in Employee.objects.exclude(mobile=''):
                if not phone_pattern.match(employee.mobile):
                    invalid_phones += 1

            if invalid_phones > 0:
                self.warnings.append(f"موظفين بأرقام هواتف غير صحيحة: {invalid_phones}")

            return len(errors) == 0, {
                'errors': errors,
                'count': count
            }

        except ImportError:
            return True, {'errors': [], 'count': 0, 'note': 'نموذج الموظفين غير متاح'}

    def validate_inventory(self):
        """Validate inventory data"""
        errors = []

        try:
            from inventory.models import TblProducts, TblCategories, TblUnitsSpareparts

            # Check products
            products_count = TblProducts.objects.count()
            if products_count == 0:
                return True, {'errors': [], 'count': 0, 'note': 'لا توجد منتجات'}

            # Check for products with negative stock
            negative_stock = TblProducts.objects.filter(qte_in_stock__lt=0).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if negative_stock > 0:
                errors.append(f"منتجات برصيد سالب: {negative_stock}")

            # Check for products without categories
            no_category = TblProducts.objects.filter(cat__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if no_category > 0:
                errors.append(f"منتجات بدون فئة: {no_category}")

            # Check for products without units
            no_unit = TblProducts.objects.filter(unit__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if no_unit > 0:
                errors.append(f"منتجات بدون وحدة قياس: {no_unit}")

            # Check for products with zero or negative prices
            invalid_prices = TblProducts.objects.filter(
                models.Q(unit_price__lte=0).prefetch_related()  # TODO: Add appropriate prefetch_related fields | models.Q(unit_price__isnull=True)
            ).count()
            if invalid_prices > 0:
                errors.append(f"منتجات بأسعار غير صحيحة: {invalid_prices}")

            # Check for products below minimum threshold
            below_minimum = TblProducts.objects.filter(
                qte_in_stock__lt=models.F('minimum_threshold').prefetch_related()  # TODO: Add appropriate prefetch_related fields
            ).count()
            if below_minimum > 0:
                self.warnings.append(f"منتجات تحت الحد الأدنى: {below_minimum}")

            # Check categories and units
            categories_count = TblCategories.objects.count()
            units_count = TblUnitsSpareparts.objects.count()

            if categories_count == 0:
                errors.append("لا توجد فئات منتجات")

            if units_count == 0:
                errors.append("لا توجد وحدات قياس")

            total_count = products_count + categories_count + units_count

            return len(errors) == 0, {
                'errors': errors,
                'count': total_count,
                'products': products_count,
                'categories': categories_count,
                'units': units_count
            }

        except ImportError:
            return True, {'errors': [], 'count': 0, 'note': 'نماذج المخزون غير متاحة'}

    def validate_tasks(self):
        """Validate task data"""
        errors = []

        try:
            from tasks.models import Task

            count = Task.objects.count()
            if count == 0:
                return True, {'errors': [], 'count': 0, 'note': 'لا توجد مهام'}

            # Check for tasks with end date before start date
            invalid_dates = Task.objects.filter(end_date__lt=models.F('start_date').prefetch_related()  # TODO: Add appropriate prefetch_related fields).count()
            if invalid_dates > 0:
                errors.append(f"مهام بتواريخ غير صحيحة: {invalid_dates}")

            # Check for tasks without assigned users
            no_assignee = Task.objects.filter(assigned_to__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if no_assignee > 0:
                errors.append(f"مهام غير مُعيَّنة: {no_assignee}")

            # Check for tasks without creators
            no_creator = Task.objects.filter(created_by__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if no_creator > 0:
                errors.append(f"مهام بدون منشئ: {no_creator}")

            # Check for invalid progress values
            invalid_progress = Task.objects.filter(
                models.Q(progress__lt=0).prefetch_related()  # TODO: Add appropriate prefetch_related fields | models.Q(progress__gt=100)
            ).count()
            if invalid_progress > 0:
                errors.append(f"مهام بنسبة إنجاز غير صحيحة: {invalid_progress}")

            # Check for overdue tasks
            overdue_tasks = Task.objects.filter(
                end_date__lt=date.today().prefetch_related()  # TODO: Add appropriate prefetch_related fields,
                status__in=['pending', 'in_progress']
            ).count()
            if overdue_tasks > 0:
                self.warnings.append(f"مهام متأخرة: {overdue_tasks}")

            return len(errors) == 0, {
                'errors': errors,
                'count': count
            }

        except ImportError:
            return True, {'errors': [], 'count': 0, 'note': 'نموذج المهام غير متاح'}

    def validate_meetings(self):
        """Validate meeting data"""
        errors = []

        try:
            from meetings.models import Meeting, Attendee

            count = Meeting.objects.count()
            if count == 0:
                return True, {'errors': [], 'count': 0, 'note': 'لا توجد اجتماعات'}

            # Check for meetings without creators
            no_creator = Meeting.objects.filter(created_by__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if no_creator > 0:
                errors.append(f"اجتماعات بدون منشئ: {no_creator}")

            # Check for meetings without attendees
            meetings_without_attendees = Meeting.objects.filter(
                attendee__isnull=True
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.distinct().count()
            if meetings_without_attendees > 0:
                self.warnings.append(f"اجتماعات بدون حضور: {meetings_without_attendees}")

            # Check for meetings with only one attendee
            single_attendee_meetings = Meeting.objects.annotate(
                attendee_count=models.Count('attendee')
            ).filter(attendee_count=1).count()
            if single_attendee_meetings > 0:
                self.warnings.append(f"اجتماعات بحضور واحد فقط: {single_attendee_meetings}")

            return len(errors) == 0, {
                'errors': errors,
                'count': count
            }

        except ImportError:
            return True, {'errors': [], 'count': 0, 'note': 'نموذج الاجتماعات غير متاح'}

    def validate_purchase_orders(self):
        """Validate purchase order data"""
        errors = []

        try:
            from Purchase_orders.models import PurchaseRequest, PurchaseRequestItem

            count = PurchaseRequest.objects.count()
            if count == 0:
                return True, {'errors': [], 'count': 0, 'note': 'لا توجد طلبات شراء'}

            # Check for requests without items
            requests_without_items = PurchaseRequest.objects.filter(
                purchaserequestitem__isnull=True
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.distinct().count()
            if requests_without_items > 0:
                errors.append(f"طلبات شراء بدون عناصر: {requests_without_items}")

            # Check for items with zero or negative quantities
            invalid_quantities = PurchaseRequestItem.objects.filter(
                quantity_requested__lte=0
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if invalid_quantities > 0:
                errors.append(f"عناصر بكميات غير صحيحة: {invalid_quantities}")

            return len(errors) == 0, {
                'errors': errors,
                'count': count
            }

        except ImportError:
            return True, {'errors': [], 'count': 0, 'note': 'نموذج طلبات الشراء غير متاح'}

    def validate_attendance(self):
        """Validate attendance data"""
        errors = []

        try:
            from attendance.models import EmployeeAttendance

            count = EmployeeAttendance.objects.count()
            if count == 0:
                return True, {'errors': [], 'count': 0, 'note': 'لا توجد سجلات حضور'}

            # Check for attendance without employees
            no_employee = EmployeeAttendance.objects.filter(employee__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if no_employee > 0:
                errors.append(f"سجلات حضور بدون موظف: {no_employee}")

            # Check for check-out before check-in
            invalid_times = EmployeeAttendance.objects.filter(
                check_out__lt=models.F('check_in').prefetch_related()  # TODO: Add appropriate prefetch_related fields
            ).count()
            if invalid_times > 0:
                errors.append(f"سجلات بأوقات غير صحيحة: {invalid_times}")

            # Check for future attendance dates
            future_attendance = EmployeeAttendance.objects.filter(
                att_date__gt=date.today().prefetch_related()  # TODO: Add appropriate prefetch_related fields
            ).count()
            if future_attendance > 0:
                self.warnings.append(f"سجلات حضور مستقبلية: {future_attendance}")

            return len(errors) == 0, {
                'errors': errors,
                'count': count
            }

        except ImportError:
            return True, {'errors': [], 'count': 0, 'note': 'نموذج الحضور غير متاح'}

    def validate_payroll(self):
        """Validate payroll data"""
        errors = []

        try:
            from payrolls.models import PayrollRecord

            count = PayrollRecord.objects.count()
            if count == 0:
                return True, {'errors': [], 'count': 0, 'note': 'لا توجد سجلات رواتب'}

            # Check for payroll without employees
            no_employee = PayrollRecord.objects.filter(employee__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if no_employee > 0:
                errors.append(f"سجلات رواتب بدون موظف: {no_employee}")

            # Check for negative salaries
            negative_salaries = PayrollRecord.objects.filter(
                models.Q(basic_salary__lt=0).prefetch_related()  # TODO: Add appropriate prefetch_related fields |
                models.Q(net_salary__lt=0)
            ).count()
            if negative_salaries > 0:
                errors.append(f"رواتب بقيم سالبة: {negative_salaries}")

            # Check for inconsistent calculations
            inconsistent_calculations = PayrollRecord.objects.filter(
                net_salary__gt=models.F('gross_salary').prefetch_related()  # TODO: Add appropriate prefetch_related fields
            ).count()
            if inconsistent_calculations > 0:
                errors.append(f"حسابات رواتب غير متسقة: {inconsistent_calculations}")

            return len(errors) == 0, {
                'errors': errors,
                'count': count
            }

        except ImportError:
            return True, {'errors': [], 'count': 0, 'note': 'نموذج الرواتب غير متاح'}

    def validate_leaves(self):
        """Validate leave data"""
        errors = []

        try:
            from leaves.models import LeaveRequest

            count = LeaveRequest.objects.count()
            if count == 0:
                return True, {'errors': [], 'count': 0, 'note': 'لا توجد طلبات إجازات'}

            # Check for leaves without employees
            no_employee = LeaveRequest.objects.filter(employee__isnull=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if no_employee > 0:
                errors.append(f"طلبات إجازات بدون موظف: {no_employee}")

            # Check for invalid date ranges
            invalid_dates = LeaveRequest.objects.filter(
                end_date__lt=models.F('start_date').prefetch_related()  # TODO: Add appropriate prefetch_related fields
            ).count()
            if invalid_dates > 0:
                errors.append(f"طلبات إجازات بتواريخ غير صحيحة: {invalid_dates}")

            # Check for zero or negative days
            invalid_days = LeaveRequest.objects.filter(
                days_requested__lte=0
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if invalid_days > 0:
                errors.append(f"طلبات إجازات بأيام غير صحيحة: {invalid_days}")

            return len(errors) == 0, {
                'errors': errors,
                'count': count
            }

        except ImportError:
            return True, {'errors': [], 'count': 0, 'note': 'نموذج الإجازات غير متاح'}

    def validate_cross_references(self):
        """Validate cross-references between models"""
        errors = []

        try:
            # Check employee-user relationships
            from employees.models import Employee

            employees_without_users = Employee.objects.filter(
                user__isnull=True
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if employees_without_users > 0:
                self.warnings.append(f"موظفين بدون حسابات مستخدمين: {employees_without_users}")

            # Check task assignments to valid users
            from tasks.models import Task

            tasks_with_invalid_assignees = Task.objects.filter(
                assigned_to__is_active=False
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if tasks_with_invalid_assignees > 0:
                self.warnings.append(f"مهام مُعيَّنة لمستخدمين غير نشطين: {tasks_with_invalid_assignees}")

            # Check product-category relationships
            from inventory.models import TblProducts

            products_with_invalid_categories = TblProducts.objects.filter(
                cat__isnull=False,
                cat_name__isnull=True
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            if products_with_invalid_categories > 0:
                errors.append(f"منتجات بفئات غير صحيحة: {products_with_invalid_categories}")

        except ImportError:
            pass

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def generate_statistics(self):
        """Generate comprehensive statistics about test data"""
        self.statistics = {}

        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
        staff_users = User.objects.filter(is_staff=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

        self.statistics['users'] = {
            'total': total_users,
            'active': active_users,
            'staff': staff_users,
            'active_percentage': (active_users / total_users * 100) if total_users > 0 else 0
        }

        # Employee statistics
        try:
            from employees.models import Employee

            total_employees = Employee.objects.count()
            active_employees = Employee.objects.filter(emp_status='Active').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

            self.statistics['employees'] = {
                'total': total_employees,
                'active': active_employees,
                'active_percentage': (active_employees / total_employees * 100) if total_employees > 0 else 0
            }

        except ImportError:
            self.statistics['employees'] = {'note': 'غير متاح'}

        # Task statistics
        try:
            from tasks.models import Task

            total_tasks = Task.objects.count()
            completed_tasks = Task.objects.filter(status='completed').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            pending_tasks = Task.objects.filter(status='pending').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            in_progress_tasks = Task.objects.filter(status='in_progress').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

            self.statistics['tasks'] = {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': pending_tasks,
                'in_progress': in_progress_tasks,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }

        except ImportError:
            self.statistics['tasks'] = {'note': 'غير متاح'}

        # Inventory statistics
        try:
            from inventory.models import TblProducts

            total_products = TblProducts.objects.count()
            low_stock_products = TblProducts.objects.filter(
                qte_in_stock__lt=models.F('minimum_threshold').prefetch_related()  # TODO: Add appropriate prefetch_related fields
            ).count()

            self.statistics['inventory'] = {
                'total_products': total_products,
                'low_stock': low_stock_products,
                'low_stock_percentage': (low_stock_products / total_products * 100) if total_products > 0 else 0
            }

        except ImportError:
            self.statistics['inventory'] = {'note': 'غير متاح'}

    def print_statistics(self):
        """Print detailed statistics"""
        print("\n📊 إحصائيات البيانات التجريبية:")
        print("=" * 50)

        for category, stats in self.statistics.items():
            if 'note' in stats:
                print(f"{category}: {stats['note']}")
                continue

            if category == 'users':
                print(f"👥 المستخدمين:")
                print(f"  • المجموع: {stats['total']}")
                print(f"  • النشطين: {stats['active']} ({stats['active_percentage']:.1f}%)")
                print(f"  • الموظفين: {stats['staff']}")

            elif category == 'employees':
                print(f"👨‍💼 الموظفين:")
                print(f"  • المجموع: {stats['total']}")
                print(f"  • النشطين: {stats['active']} ({stats['active_percentage']:.1f}%)")

            elif category == 'tasks':
                print(f"📋 المهام:")
                print(f"  • المجموع: {stats['total']}")
                print(f"  • المكتملة: {stats['completed']} ({stats['completion_rate']:.1f}%)")
                print(f"  • قيد التنفيذ: {stats['in_progress']}")
                print(f"  • في الانتظار: {stats['pending']}")

            elif category == 'inventory':
                print(f"📦 المخزون:")
                print(f"  • المنتجات: {stats['total_products']}")
                print(f"  • مخزون منخفض: {stats['low_stock']} ({stats['low_stock_percentage']:.1f}%)")

        print("=" * 50)

        if self.warnings:
            print(f"⚠️  التحذيرات: {len(self.warnings)}")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  ... و {len(self.warnings) - 5} تحذيرات أخرى")

        if self.errors:
            print(f"❌ الأخطاء: {len(self.errors)}")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  • {error}")
            if len(self.errors) > 5:
                print(f"  ... و {len(self.errors) - 5} أخطاء أخرى")

    def export_validation_report(self, filename='validation_report.json'):
        """Export validation report to JSON file"""
        import json

        report = {
            'timestamp': datetime.now().isoformat(),
            'validation_results': self.validation_results,
            'statistics': self.statistics,
            'warnings': self.warnings,
            'errors': self.errors,
            'summary': {
                'total_checks': len(self.validation_results),
                'passed_checks': sum(1 for r in self.validation_results.values() if r['valid']),
                'failed_checks': sum(1 for r in self.validation_results.values() if not r['valid']),
                'total_warnings': len(self.warnings),
                'total_errors': len(self.errors)
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        print(f"📄 تم تصدير تقرير التحقق إلى: {filename}")
        return filename


class TestDataQualityAssurance:
    """Quality assurance for test data"""

    def __init__(self):
        """__init__ function"""
        self.quality_metrics = {}

    def assess_data_quality(self):
        """Assess overall data quality"""
        print("🎯 تقييم جودة البيانات التجريبية...")

        # Run validation
        validator = TestDataValidator()
        validation_result = validator.validate_all_data(verbose=False)

        # Calculate quality score
        quality_score = self.calculate_quality_score(validation_result)

        # Generate recommendations
        recommendations = self.generate_recommendations(validation_result)

        # Print quality assessment
        self.print_quality_assessment(quality_score, recommendations)

        return {
            'quality_score': quality_score,
            'validation_result': validation_result,
            'recommendations': recommendations
        }

    def calculate_quality_score(self, validation_result):
        """Calculate overall quality score (0-100)"""
        total_checks = len(validation_result['results'])
        passed_checks = sum(1 for r in validation_result['results'].values() if r['valid'])

        if total_checks == 0:
            return 0

        base_score = (passed_checks / total_checks) * 100

        # Deduct points for warnings and errors
        warning_penalty = min(len(validation_result['warnings']) * 2, 20)
        error_penalty = min(len(validation_result['errors']) * 5, 30)

        quality_score = max(0, base_score - warning_penalty - error_penalty)

        return round(quality_score, 1)

    def generate_recommendations(self, validation_result):
        """Generate recommendations for improving data quality"""
        recommendations = []

        # Check for common issues
        if not validation_result['valid']:
            recommendations.append("إصلاح الأخطاء المحددة في التحقق من البيانات")

        if len(validation_result['warnings']) > 10:
            recommendations.append("مراجعة التحذيرات وتحسين جودة البيانات")

        # Check statistics for recommendations
        stats = validation_result.get('statistics', {})

        if 'users' in stats and stats['users'].get('active_percentage', 0) < 80:
            recommendations.append("زيادة نسبة المستخدمين النشطين")

        if 'tasks' in stats and stats['tasks'].get('completion_rate', 0) < 30:
            recommendations.append("إضافة المزيد من المهام المكتملة لتحسين الواقعية")

        if 'inventory' in stats and stats['inventory'].get('low_stock_percentage', 0) > 20:
            recommendations.append("تقليل نسبة المنتجات ذات المخزون المنخفض")

        # Add general recommendations
        recommendations.extend([
            "إضافة المزيد من البيانات المترابطة لتحسين الواقعية",
            "التأكد من تنوع البيانات لتغطية جميع الحالات",
            "إضافة بيانات تاريخية لاختبار التقارير الزمنية"
        ])

        return recommendations[:5]  # Return top 5 recommendations

    def print_quality_assessment(self, quality_score, recommendations):
        """Print quality assessment results"""
        print("\n🏆 تقييم جودة البيانات:")
        print("=" * 40)

        # Quality score with color coding
        if quality_score >= 90:
            score_status = "ممتاز 🟢"
        elif quality_score >= 75:
            score_status = "جيد 🟡"
        elif quality_score >= 60:
            score_status = "مقبول 🟠"
        else:
            score_status = "يحتاج تحسين 🔴"

        print(f"نقاط الجودة: {quality_score}/100 - {score_status}")

        print(f"\n💡 التوصيات للتحسين:")
        for i, recommendation in enumerate(recommendations, 1):
            print(f"  {i}. {recommendation}")

        print("=" * 40)


def run_comprehensive_validation():
    """Run comprehensive validation and quality assessment"""
    print("🚀 بدء التحقق الشامل من جودة البيانات التجريبية...")

    # Run validation
    validator = TestDataValidator()
    validation_result = validator.validate_all_data()

    # Export validation report
    report_file = validator.export_validation_report()

    # Run quality assessment
    qa = TestDataQualityAssurance()
    quality_result = qa.assess_data_quality()

    print("\n✅ تم إكمال التحقق الشامل من جودة البيانات!")

    return {
        'validation': validation_result,
        'quality': quality_result,
        'report_file': report_file
    }


if __name__ == "__main__":
    run_comprehensive_validation()
