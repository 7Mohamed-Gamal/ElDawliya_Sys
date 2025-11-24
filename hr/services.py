"""
HR Business Logic Services
Professional service layer for HR operations
"""

from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count, Min, Max
from decimal import Decimal
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class HRAnalyticsService:
    """Service for HR analytics and reporting"""

    @staticmethod
    def get_employee_statistics():
        """Get comprehensive employee statistics"""
        try:
            from employees.models import Employee
            from org.models import Department

            total_employees = Employee.objects.count()
            active_employees = Employee.objects.filter(emp_status='Active').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
            inactive_employees = total_employees - active_employees

            # Department distribution
            dept_stats = Department.objects.annotate(
                employee_count=Count('employee')
            ).order_by('-employee_count')

            # Age distribution
            from django.db.models import Case, When, IntegerField
            age_stats = Employee.objects.extra(
                select={
                    'age': "DATEDIFF(year, BirthDate, GETDATE())"
                }
            ).aggregate(
                avg_age=Avg('age'),
                min_age=Min('age'),
                max_age=Max('age')
            )

            return {
                'total_employees': total_employees,
                'active_employees': active_employees,
                'inactive_employees': inactive_employees,
                'activity_rate': (active_employees / total_employees * 100) if total_employees > 0 else 0,
                'department_distribution': list(dept_stats.values('dept_name', 'employee_count')),
                'age_statistics': age_stats
            }
        except Exception as e:
            logger.error(f"Error getting employee statistics: {str(e)}")
            return {}

    @staticmethod
    def get_attendance_analytics(start_date=None, end_date=None):
        """Get attendance analytics for specified period"""
        try:
            from attendance.models import AttendanceRecord, AttendanceSummary

            if not start_date:
                start_date = date.today().replace(day=1)  # First day of current month
            if not end_date:
                end_date = date.today()

            # Overall attendance metrics
            records = AttendanceRecord.objects.filter(
                date__range=[start_date, end_date]
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            total_records = records.count()
            present_records = records.filter(record_type='present').count()
            absent_records = records.filter(record_type='absent').count()
            leave_records = records.filter(record_type='leave').count()

            # Late and early leave statistics
            late_records = records.filter(late_minutes__gt=0)
            early_leave_records = records.filter(early_leave_minutes__gt=0)

            attendance_rate = (present_records / total_records * 100) if total_records > 0 else 0
            punctuality_rate = ((present_records - late_records.count()) / present_records * 100) if present_records > 0 else 0

            return {
                'period': {'start': start_date, 'end': end_date},
                'total_records': total_records,
                'present_records': present_records,
                'absent_records': absent_records,
                'leave_records': leave_records,
                'attendance_rate': attendance_rate,
                'punctuality_rate': punctuality_rate,
                'average_late_minutes': late_records.aggregate(avg=Avg('late_minutes'))['avg'] or 0,
                'average_early_leave_minutes': early_leave_records.aggregate(avg=Avg('early_leave_minutes'))['avg'] or 0
            }
        except Exception as e:
            logger.error(f"Error getting attendance analytics: {str(e)}")
            return {}

    @staticmethod
    def get_payroll_analytics(year=None, month=None):
        """Get payroll analytics for specified period"""
        try:
            from payrolls.models import PayrollRun, PayrollDetail

            if not year:
                year = date.today().year
            if not month:
                month = date.today().month

            # Get payroll runs for the period
            runs = PayrollRun.objects.filter(
                run_date__year=year,
                run_date__month=month,
                status='paid'
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            if not runs.exists():
                return {'message': 'No payroll data found for the specified period'}

            # Aggregate payroll statistics
            total_runs = runs.count()
            total_employees_paid = runs.aggregate(total=Sum('processed_employees'))['total'] or 0
            total_gross_amount = runs.aggregate(total=Sum('total_gross_amount'))['total'] or 0
            total_deductions = runs.aggregate(total=Sum('total_deductions'))['total'] or 0
            total_net_amount = runs.aggregate(total=Sum('total_net_amount'))['total'] or 0

            # Average salary statistics
            avg_gross = total_gross_amount / total_employees_paid if total_employees_paid > 0 else 0
            avg_deductions = total_deductions / total_employees_paid if total_employees_paid > 0 else 0
            avg_net = total_net_amount / total_employees_paid if total_employees_paid > 0 else 0

            return {
                'period': {'year': year, 'month': month},
                'total_runs': total_runs,
                'total_employees_paid': total_employees_paid,
                'total_gross_amount': float(total_gross_amount),
                'total_deductions': float(total_deductions),
                'total_net_amount': float(total_net_amount),
                'average_gross_salary': float(avg_gross),
                'average_deductions': float(avg_deductions),
                'average_net_salary': float(avg_net),
                'deduction_rate': (total_deductions / total_gross_amount * 100) if total_gross_amount > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting payroll analytics: {str(e)}")
            return {}


class EmployeeLifecycleService:
    """Service for managing employee lifecycle events"""

    @staticmethod
    @transaction.atomic
    def onboard_employee(employee_data, salary_data=None, attendance_profile_data=None):
        """Complete employee onboarding process"""
        try:
            from employees.models import Employee
            from payrolls.models import EmployeeSalary
            from attendance.models import EmployeeAttendanceProfile, AttendanceRule

            # Create employee record
            employee = Employee.objects.create(**employee_data)

            # Create salary record if provided
            if salary_data:
                salary_data['emp'] = employee
                salary_data['effective_date'] = employee.hire_date or date.today()
                EmployeeSalary.objects.create(**salary_data)

            # Create attendance profile if provided
            if attendance_profile_data:
                # Get default attendance rule if not specified
                if 'attendance_rule' not in attendance_profile_data:
                    default_rule = AttendanceRule.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()
                    if default_rule:
                        attendance_profile_data['attendance_rule'] = default_rule

                attendance_profile_data['employee'] = employee
                EmployeeAttendanceProfile.objects.create(**attendance_profile_data)

            logger.info(f"Successfully onboarded employee: {employee.emp_code}")
            return {'success': True, 'employee': employee}

        except Exception as e:
            logger.error(f"Error onboarding employee: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    @transaction.atomic
    def terminate_employee(employee, termination_date=None, reason=None):
        """Complete employee termination process"""
        try:
            if not termination_date:
                termination_date = date.today()

            # Update employee status
            employee.emp_status = 'Terminated'
            employee.termination_date = termination_date
            if reason:
                employee.notes = f"{employee.notes or ''}\nTermination Reason: {reason}".strip()
            employee.save()

            # End current salary
            from payrolls.models import EmployeeSalary
            current_salary = EmployeeSalary.objects.filter(
                emp=employee,
                is_current=True
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            if current_salary:
                current_salary.end_date = termination_date
                current_salary.is_current = False
                current_salary.save()

            # Update attendance profile
            from attendance.models import EmployeeAttendanceProfile
            try:
                profile = employee.attendance_profile
                profile.attendance_status = 'suspended'
                profile.salary_status = 'suspended'
                profile.save()
            except EmployeeAttendanceProfile.DoesNotExist:
                pass

            logger.info(f"Successfully terminated employee: {employee.emp_code}")
            return {'success': True, 'employee': employee}

        except Exception as e:
            logger.error(f"Error terminating employee: {str(e)}")
            return {'success': False, 'error': str(e)}


class PayrollCalculationService:
    """Service for advanced payroll calculations"""

    @staticmethod
    def calculate_employee_payroll(employee, period_start, period_end, include_overtime=True):
        """Calculate comprehensive payroll for an employee"""
        try:
            from payrolls.models import EmployeeSalary
            from attendance.models import AttendanceSummary

            # Get current salary
            salary = EmployeeSalary.objects.filter(
                emp=employee,
                is_current=True,
                effective_date__lte=period_end
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            if not salary:
                return {'success': False, 'error': 'No active salary found for employee'}

            # Get attendance data
            year = period_start.year
            month = period_start.month

            attendance_summary = AttendanceSummary.objects.filter(
                employee=employee,
                year=year,
                month=month
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            # Base calculations
            base_salary = salary.basic_salary
            total_allowances = salary.total_allowances
            gross_salary = base_salary + total_allowances

            # Calculate deductions
            base_deductions = salary.total_deductions

            # Attendance-based deductions
            attendance_deductions = Decimal('0')
            if attendance_summary and salary.deduct_absent_days:
                daily_rate = salary.calculate_daily_rate()
                attendance_deductions += daily_rate * Decimal(str(attendance_summary.absent_days))

            if attendance_summary and salary.deduct_late_minutes:
                hourly_rate = salary.calculate_hourly_rate()
                late_deduction = (hourly_rate / Decimal('60')) * Decimal(str(attendance_summary.late_minutes))
                attendance_deductions += late_deduction

            # Overtime calculations
            overtime_amount = Decimal('0')
            if include_overtime and attendance_summary:
                overtime_rate = salary.calculate_overtime_rate()
                overtime_amount = overtime_rate * (attendance_summary.overtime_hours or Decimal('0'))

            # Final calculations
            total_deductions = base_deductions + attendance_deductions
            total_earnings = gross_salary + overtime_amount
            net_salary = total_earnings - total_deductions

            return {
                'success': True,
                'employee': employee,
                'period': {'start': period_start, 'end': period_end},
                'calculations': {
                    'base_salary': float(base_salary),
                    'total_allowances': float(total_allowances),
                    'gross_salary': float(gross_salary),
                    'overtime_amount': float(overtime_amount),
                    'total_earnings': float(total_earnings),
                    'base_deductions': float(base_deductions),
                    'attendance_deductions': float(attendance_deductions),
                    'total_deductions': float(total_deductions),
                    'net_salary': float(net_salary)
                },
                'attendance_data': {
                    'present_days': attendance_summary.present_days if attendance_summary else 0,
                    'absent_days': attendance_summary.absent_days if attendance_summary else 0,
                    'late_minutes': attendance_summary.late_minutes if attendance_summary else 0,
                    'overtime_hours': float(attendance_summary.overtime_hours) if attendance_summary and attendance_summary.overtime_hours else 0
                }
            }

        except Exception as e:
            logger.error(f"Error calculating payroll for employee {employee.emp_code}: {str(e)}")
            return {'success': False, 'error': str(e)}
