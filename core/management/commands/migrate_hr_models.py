"""
Django management command to migrate data from old HR models to new unified models
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command class"""
    help = 'Migrate data from old HR models to new unified core models'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration in dry-run mode (no actual changes)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each batch',
        )
        parser.add_argument(
            '--model',
            type=str,
            choices=['employees', 'salaries', 'attendance', 'leaves', 'evaluations', 'all'],
            default='all',
            help='Specific model to migrate',
        )

    def handle(self, *args, **options):
        """handle function"""
        self.dry_run = options['dry_run']
        self.batch_size = options['batch_size']
        self.model = options['model']

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('Running in DRY-RUN mode - no changes will be made')
            )

        try:
            if self.model == 'all':
                self.migrate_all_models()
            else:
                self.migrate_specific_model(self.model)

            self.stdout.write(
                self.style.SUCCESS('Migration completed successfully!')
            )
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise CommandError(f'Migration failed: {str(e)}')

    def migrate_all_models(self):
        """Migrate all models in the correct order"""
        migration_order = [
            'employees',
            'salaries',
            'attendance',
            'leaves',
            'evaluations'
        ]

        for model_name in migration_order:
            self.stdout.write(f"Migrating {model_name}...")
            self.migrate_specific_model(model_name)

    def migrate_specific_model(self, model_name):
        """Migrate a specific model"""
        migration_methods = {
            'employees': self.migrate_employees,
            'salaries': self.migrate_salaries,
            'attendance': self.migrate_attendance,
            'leaves': self.migrate_leaves,
            'evaluations': self.migrate_evaluations,
        }

        if model_name in migration_methods:
            migration_methods[model_name]()
        else:
            raise CommandError(f"Unknown model: {model_name}")

    def migrate_employees(self):
        """Migrate employee data from old models to new core models"""
        try:
            # Import old models
            from employees.models import Employee as OldEmployee
            from employees.models import EmployeeBankAccount as OldBankAccount
            from employees.models import EmployeeDocument as OldDocument

            # Import new models
            from core.models.hr import Employee, EmployeeBankAccount, EmployeeDocument
            from core.models.hr import Department, JobPosition

            # Migrate employees
            old_employees = OldEmployee.objects.all().select_related()  # TODO: Add appropriate select_related fields
            migrated_count = 0

            for old_emp in old_employees.iterator(chunk_size=self.batch_size):
                if not self.dry_run:
                    with transaction.atomic():
                        # Create or get department
                        department, _ = Department.objects.get_or_create(
                            name=old_emp.dept.name if old_emp.dept else 'غير محدد',
                            defaults={
                                'code': old_emp.dept.dept_code if old_emp.dept else 'UNKNOWN',
                                'created_at': timezone.now()
                            }
                        )

                        # Create or get job position
                        job_position, _ = JobPosition.objects.get_or_create(
                            title=old_emp.job.job_title if old_emp.job else 'غير محدد',
                            department=department,
                            defaults={
                                'code': old_emp.job.job_code if old_emp.job else 'UNKNOWN',
                                'created_at': timezone.now()
                            }
                        )

                        # Create new employee
                        new_emp, created = Employee.objects.get_or_create(
                            emp_code=old_emp.emp_code,
                            defaults={
                                'first_name': old_emp.first_name or '',
                                'second_name': old_emp.second_name or '',
                                'third_name': old_emp.third_name or '',
                                'last_name': old_emp.last_name or '',
                                'gender': old_emp.gender or 'M',
                                'birth_date': old_emp.birth_date,
                                'nationality': old_emp.nationality,
                                'national_id': old_emp.national_id,
                                'passport_no': old_emp.passport_no,
                                'mobile': old_emp.mobile,
                                'email': old_emp.email,
                                'street_address': old_emp.address,
                                'department': department,
                                'job_position': job_position,
                                'hire_date': old_emp.hire_date or timezone.now().date(),
                                'join_date': old_emp.join_date,
                                'probation_end_date': old_emp.probation_end,
                                'emp_status': self._map_employee_status(old_emp.emp_status),
                                'termination_date': old_emp.termination_date,
                                'created_at': old_emp.created_at or timezone.now(),
                                'updated_at': old_emp.updated_at or timezone.now(),
                            }
                        )

                        if created:
                            migrated_count += 1

                if migrated_count % 50 == 0:
                    self.stdout.write(f"Migrated {migrated_count} employees...")

            self.stdout.write(
                self.style.SUCCESS(f"Successfully migrated {migrated_count} employees")
            )

        except Exception as e:
            logger.error(f"Employee migration failed: {str(e)}")
            raise

    def migrate_salaries(self):
        """Migrate salary data"""
        try:
            from payrolls.models import EmployeeSalary as OldSalary
            from core.models.hr import EmployeeSalary, Employee

            old_salaries = OldSalary.objects.all().select_related()  # TODO: Add appropriate select_related fields
            migrated_count = 0

            for old_salary in old_salaries.iterator(chunk_size=self.batch_size):
                if not self.dry_run:
                    try:
                        employee = Employee.objects.get(emp_code=old_salary.emp.emp_code)

                        new_salary, created = EmployeeSalary.objects.get_or_create(
                            employee=employee,
                            effective_date=old_salary.effective_date or timezone.now().date(),
                            defaults={
                                'basic_salary': old_salary.basic_salary or 0,
                                'housing_allowance': old_salary.housing_allow or 0,
                                'transport_allowance': old_salary.transport_allow or 0,
                                'other_allowances': old_salary.other_allow or 0,
                                'gosi_employee': old_salary.gosi_deduction or 0,
                                'income_tax': old_salary.tax_deduction or 0,
                                'currency': old_salary.currency or 'SAR',
                                'is_current': old_salary.is_current,
                                'created_at': timezone.now(),
                            }
                        )

                        if created:
                            migrated_count += 1

                    except Employee.DoesNotExist:
                        logger.warning(f"Employee not found for salary: {old_salary.emp.emp_code}")
                        continue

            self.stdout.write(
                self.style.SUCCESS(f"Successfully migrated {migrated_count} salary records")
            )

        except Exception as e:
            logger.error(f"Salary migration failed: {str(e)}")
            raise

    def migrate_attendance(self):
        """Migrate attendance data"""
        try:
            from attendance.models import EmployeeAttendance as OldAttendance
            from core.models.attendance import AttendanceRecord
            from core.models.hr import Employee

            old_records = OldAttendance.objects.all().select_related()  # TODO: Add appropriate select_related fields
            migrated_count = 0

            for old_record in old_records.iterator(chunk_size=self.batch_size):
                if not self.dry_run:
                    try:
                        employee = Employee.objects.get(emp_code=old_record.emp.emp_code)

                        new_record, created = AttendanceRecord.objects.get_or_create(
                            employee=employee,
                            attendance_date=old_record.att_date,
                            defaults={
                                'check_in_time': old_record.check_in,
                                'check_out_time': old_record.check_out,
                                'record_type': self._map_attendance_status(old_record.status),
                                'created_at': timezone.now(),
                            }
                        )

                        if created:
                            migrated_count += 1

                    except Employee.DoesNotExist:
                        logger.warning(f"Employee not found for attendance: {old_record.emp.emp_code}")
                        continue

            self.stdout.write(
                self.style.SUCCESS(f"Successfully migrated {migrated_count} attendance records")
            )

        except Exception as e:
            logger.error(f"Attendance migration failed: {str(e)}")
            raise

    def migrate_leaves(self):
        """Migrate leave data"""
        try:
            from leaves.models import LeaveType as OldLeaveType
            from leaves.models import EmployeeLeave as OldLeave
            from core.models.leaves import LeaveType, LeaveRecord
            from core.models.hr import Employee

            # Migrate leave types first
            old_leave_types = OldLeaveType.objects.all().select_related()  # TODO: Add appropriate select_related fields
            for old_type in old_leave_types:
                if not self.dry_run:
                    LeaveType.objects.get_or_create(
                        name=old_type.leave_name,
                        defaults={
                            'code': old_type.leave_name[:10].upper(),
                            'is_paid': old_type.is_paid,
                            'max_days_per_year': old_type.max_days_per_year,
                            'requires_approval': old_type.requires_approval,
                            'created_at': timezone.now(),
                        }
                    )

            # Migrate leave records
            old_leaves = OldLeave.objects.filter(status='Approved').prefetch_related()  # TODO: Add appropriate prefetch_related fields
            migrated_count = 0

            for old_leave in old_leaves.iterator(chunk_size=self.batch_size):
                if not self.dry_run:
                    try:
                        employee = Employee.objects.get(emp_code=old_leave.emp.emp_code)
                        leave_type = LeaveType.objects.get(name=old_leave.leave_type.leave_name)

                        new_record, created = LeaveRecord.objects.get_or_create(
                            employee=employee,
                            start_date=old_leave.start_date,
                            end_date=old_leave.end_date,
                            defaults={
                                'leave_type': leave_type,
                                'duration_days': (old_leave.end_date - old_leave.start_date).days + 1,
                                'reason': old_leave.reason or '',
                                'created_at': old_leave.created_at or timezone.now(),
                            }
                        )

                        if created:
                            migrated_count += 1

                    except (Employee.DoesNotExist, LeaveType.DoesNotExist) as e:
                        logger.warning(f"Related object not found for leave: {str(e)}")
                        continue

            self.stdout.write(
                self.style.SUCCESS(f"Successfully migrated {migrated_count} leave records")
            )

        except Exception as e:
            logger.error(f"Leave migration failed: {str(e)}")
            raise

    def migrate_evaluations(self):
        """Migrate evaluation data"""
        try:
            from evaluations.models import EvaluationPeriod as OldPeriod
            from evaluations.models import EmployeeEvaluation as OldEvaluation
            from core.models.evaluations import EvaluationPeriod, EmployeeEvaluation
            from core.models.hr import Employee

            # Migrate evaluation periods
            old_periods = OldPeriod.objects.all().select_related()  # TODO: Add appropriate select_related fields
            for old_period in old_periods:
                if not self.dry_run:
                    EvaluationPeriod.objects.get_or_create(
                        name=old_period.period_name,
                        defaults={
                            'start_date': old_period.start_date,
                            'end_date': old_period.end_date,
                            'evaluation_deadline': old_period.end_date,
                            'status': 'active' if old_period.is_active else 'completed',
                            'created_at': old_period.created_at or timezone.now(),
                        }
                    )

            # Migrate evaluations
            old_evaluations = OldEvaluation.objects.all().select_related()  # TODO: Add appropriate select_related fields
            migrated_count = 0

            for old_eval in old_evaluations.iterator(chunk_size=self.batch_size):
                if not self.dry_run:
                    try:
                        employee = Employee.objects.get(emp_code=old_eval.emp.emp_code)
                        period = EvaluationPeriod.objects.get(name=old_eval.period.period_name)

                        new_eval, created = EmployeeEvaluation.objects.get_or_create(
                            employee=employee,
                            period=period,
                            defaults={
                                'total_score': old_eval.score or 0,
                                'percentage_score': old_eval.score or 0,
                                'evaluator_comments': old_eval.notes,
                                'evaluation_date': old_eval.eval_date,
                                'status': self._map_evaluation_status(old_eval.status),
                                'created_at': old_eval.created_at or timezone.now(),
                            }
                        )

                        if created:
                            migrated_count += 1

                    except (Employee.DoesNotExist, EvaluationPeriod.DoesNotExist) as e:
                        logger.warning(f"Related object not found for evaluation: {str(e)}")
                        continue

            self.stdout.write(
                self.style.SUCCESS(f"Successfully migrated {migrated_count} evaluation records")
            )

        except Exception as e:
            logger.error(f"Evaluation migration failed: {str(e)}")
            raise

    def _map_employee_status(self, old_status):
        """Map old employee status to new status"""
        status_mapping = {
            'Active': 'active',
            'Inactive': 'inactive',
            'Terminated': 'terminated',
            'Suspended': 'suspended',
            'On Leave': 'on_leave',
        }
        return status_mapping.get(old_status, 'active')

    def _map_attendance_status(self, old_status):
        """Map old attendance status to new record type"""
        status_mapping = {
            'Present': 'present',
            'Absent': 'absent',
            'Late': 'late',
            'Holiday': 'holiday',
            'Leave': 'leave',
        }
        return status_mapping.get(old_status, 'present')

    def _map_evaluation_status(self, old_status):
        """Map old evaluation status to new status"""
        status_mapping = {
            'draft': 'draft',
            'submitted': 'manager_review',
            'approved': 'approved',
            'rejected': 'rejected',
        }
        return status_mapping.get(old_status, 'draft')
