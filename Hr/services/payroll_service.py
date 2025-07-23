"""Payroll Services Module

This module provides services for payroll management, including:
- Salary calculation and processing
- Payroll period management
- Employee salary structure management
- Payroll reporting and analytics
"""

import uuid
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union, Any

from django.db import transaction
from django.db.models import Q, Count, Sum, Avg, F, Value, Max
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.conf import settings

from Hr.models.payroll.payroll_period_models import PayrollPeriod
from Hr.models.payroll.employee_salary_structure_models import EmployeeSalaryStructure, SalaryComponent
from Hr.models.employee.employee_models import Employee
from Hr.models.attendance.attendance_record_models import AttendanceRecord

# Setup logger
logger = logging.getLogger(__name__)


class PayrollService:
    """Service class for payroll management operations"""
    
    @staticmethod
    def get_payroll_period_by_id(period_id: uuid.UUID) -> Optional[PayrollPeriod]:
        """Retrieve a payroll period by ID
        
        Args:
            period_id: UUID of the payroll period
            
        Returns:
            PayrollPeriod object if found, None otherwise
        """
        try:
            return PayrollPeriod.objects.get(id=period_id)
        except PayrollPeriod.DoesNotExist:
            logger.warning(f"Payroll period with ID {period_id} not found")
            return None
    
    @staticmethod
    def get_current_payroll_period() -> Optional[PayrollPeriod]:
        """Get the current active payroll period
        
        Returns:
            PayrollPeriod object if found, None otherwise
        """
        try:
            today = date.today()
            return PayrollPeriod.objects.filter(
                start_date__lte=today,
                end_date__gte=today,
                is_active=True
            ).first()
        except Exception as e:
            logger.error(f"Error getting current payroll period: {str(e)}")
            return None
    
    @staticmethod
    def get_payroll_periods(year: int = None, month: int = None) -> List[PayrollPeriod]:
        """Get payroll periods with optional filtering
        
        Args:
            year: Year to filter by (optional)
            month: Month to filter by (optional)
            
        Returns:
            List of PayrollPeriod objects
        """
        try:
            queryset = PayrollPeriod.objects.all()
            
            if year:
                queryset = queryset.filter(start_date__year=year)
            
            if month:
                queryset = queryset.filter(start_date__month=month)
            
            return list(queryset.order_by('-start_date'))
            
        except Exception as e:
            logger.error(f"Error retrieving payroll periods: {str(e)}")
            return []
    
    @staticmethod
    @transaction.atomic
    def create_payroll_period(period_data: Dict) -> Tuple[PayrollPeriod, bool, str]:
        """Create a new payroll period
        
        Args:
            period_data: Dictionary with payroll period data
            
        Returns:
            Tuple of (PayrollPeriod object, success boolean, message string)
        """
        try:
            # Check for overlapping periods
            start_date = period_data['start_date']
            end_date = period_data['end_date']
            
            overlapping_periods = PayrollPeriod.objects.filter(
                Q(start_date__lte=end_date, end_date__gte=start_date)
            )
            
            if overlapping_periods.exists():
                return None, False, "Payroll period overlaps with existing period"
            
            # Create payroll period
            period = PayrollPeriod(**period_data)
            period.save()
            
            logger.info(f"Created payroll period: {period.name}")
            return period, True, "Payroll period created successfully"
            
        except Exception as e:
            logger.error(f"Error creating payroll period: {str(e)}")
            return None, False, f"Error creating payroll period: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def close_payroll_period(period_id: uuid.UUID) -> Tuple[bool, str]:
        """Close a payroll period
        
        Args:
            period_id: UUID of the payroll period to close
            
        Returns:
            Tuple of (success boolean, message string)
        """
        try:
            period = PayrollService.get_payroll_period_by_id(period_id)
            if not period:
                return False, f"Payroll period with ID {period_id} not found"
            
            if period.status == 'closed':
                return False, "Payroll period is already closed"
            
            period.status = 'closed'
            period.closed_date = timezone.now().date()
            period.save()
            
            logger.info(f"Closed payroll period: {period.name}")
            return True, "Payroll period closed successfully"
            
        except Exception as e:
            logger.error(f"Error closing payroll period: {str(e)}")
            return False, f"Error closing payroll period: {str(e)}"
    
    @staticmethod
    def get_employee_salary_structure(employee_id: uuid.UUID) -> Optional[EmployeeSalaryStructure]:
        """Get the current salary structure for an employee
        
        Args:
            employee_id: UUID of the employee
            
        Returns:
            EmployeeSalaryStructure object if found, None otherwise
        """
        try:
            return EmployeeSalaryStructure.objects.filter(
                employee_id=employee_id,
                is_active=True
            ).first()
        except Exception as e:
            logger.error(f"Error getting employee salary structure: {str(e)}")
            return None
    
    @staticmethod
    @transaction.atomic
    def create_employee_salary_structure(salary_data: Dict) -> Tuple[EmployeeSalaryStructure, bool, str]:
        """Create a new employee salary structure
        
        Args:
            salary_data: Dictionary with salary structure data
            
        Returns:
            Tuple of (EmployeeSalaryStructure object, success boolean, message string)
        """
        try:
            # Get employee
            try:
                employee = Employee.objects.get(id=salary_data['employee_id'])
            except Employee.DoesNotExist:
                return None, False, f"Employee with ID {salary_data['employee_id']} not found"
            
            # Deactivate existing salary structures
            EmployeeSalaryStructure.objects.filter(
                employee=employee,
                is_active=True
            ).update(is_active=False)
            
            # Create new salary structure
            salary_data['employee'] = employee
            del salary_data['employee_id']
            
            salary_structure = EmployeeSalaryStructure(**salary_data)
            salary_structure.save()
            
            logger.info(f"Created salary structure for employee: {employee.full_name}")
            return salary_structure, True, "Salary structure created successfully"
            
        except Exception as e:
            logger.error(f"Error creating salary structure: {str(e)}")
            return None, False, f"Error creating salary structure: {str(e)}"
    
    @staticmethod
    def calculate_employee_salary(employee_id: uuid.UUID, 
                                period_id: uuid.UUID,
                                include_attendance: bool = True) -> Dict:
        """Calculate salary for an employee for a specific payroll period
        
        Args:
            employee_id: UUID of the employee
            period_id: UUID of the payroll period
            include_attendance: Whether to include attendance-based calculations
            
        Returns:
            Dictionary with salary calculation details
        """
        try:
            # Get employee and salary structure
            employee = Employee.objects.get(id=employee_id)
            salary_structure = PayrollService.get_employee_salary_structure(employee_id)
            period = PayrollService.get_payroll_period_by_id(period_id)
            
            if not salary_structure:
                return {
                    'error': 'No active salary structure found for employee',
                    'employee_id': employee_id
                }
            
            if not period:
                return {
                    'error': 'Payroll period not found',
                    'period_id': period_id
                }
            
            # Initialize calculation
            calculation = {
                'employee_id': employee_id,
                'employee_name': employee.full_name,
                'period_id': period_id,
                'period_name': period.name,
                'basic_salary': salary_structure.basic_salary,
                'allowances': {},
                'deductions': {},
                'total_allowances': Decimal('0.00'),
                'total_deductions': Decimal('0.00'),
                'gross_salary': Decimal('0.00'),
                'net_salary': Decimal('0.00'),
                'worked_days': 0,
                'total_days': 0,
                'attendance_rate': 0.0
            }
            
            # Calculate attendance if requested
            if include_attendance:
                attendance_records = AttendanceRecord.objects.filter(
                    employee=employee,
                    date__gte=period.start_date,
                    date__lte=period.end_date
                )
                
                worked_days = attendance_records.filter(check_in_time__isnull=False).count()
                total_days = (period.end_date - period.start_date).days + 1
                
                calculation['worked_days'] = worked_days
                calculation['total_days'] = total_days
                calculation['attendance_rate'] = (worked_days / total_days * 100) if total_days > 0 else 0
                
                # Adjust basic salary based on attendance
                if worked_days < total_days:
                    daily_salary = salary_structure.basic_salary / total_days
                    calculation['basic_salary'] = daily_salary * worked_days
            
            # Calculate allowances
            for component in salary_structure.salary_components.filter(component_type='allowance', is_active=True):
                amount = PayrollService._calculate_component_amount(component, calculation['basic_salary'])
                calculation['allowances'][component.name] = amount
                calculation['total_allowances'] += amount
            
            # Calculate deductions
            for component in salary_structure.salary_components.filter(component_type='deduction', is_active=True):
                amount = PayrollService._calculate_component_amount(component, calculation['basic_salary'])
                calculation['deductions'][component.name] = amount
                calculation['total_deductions'] += amount
            
            # Calculate totals
            calculation['gross_salary'] = calculation['basic_salary'] + calculation['total_allowances']
            calculation['net_salary'] = calculation['gross_salary'] - calculation['total_deductions']
            
            return calculation
            
        except Employee.DoesNotExist:
            return {
                'error': 'Employee not found',
                'employee_id': employee_id
            }
        except Exception as e:
            logger.error(f"Error calculating employee salary: {str(e)}")
            return {
                'error': f"Error calculating salary: {str(e)}",
                'employee_id': employee_id
            }
    
    @staticmethod
    def calculate_salary_component_amount(component, employee, payroll_period, base_values=None):
        """
        حساب قيمة مكون الراتب لموظف معين وفترة معينة
        Calculate the amount for a salary component for a specific employee and payroll period
        """
        from decimal import Decimal
        if base_values is None:
            base_values = {}
        amount = Decimal('0')
        method = getattr(component, 'calculation_method', None)
        if method == 'fixed':
            amount = getattr(component, 'fixed_amount', Decimal('0')) or Decimal('0')
        elif method == 'percentage':
            basis_value = PayrollService._get_basis_value(component, employee, payroll_period, base_values)
            percentage_value = getattr(component, 'percentage_value', None)
            if basis_value and percentage_value:
                amount = basis_value * (percentage_value / 100)
        elif method == 'formula':
            amount = PayrollService._calculate_formula_amount(component, employee, payroll_period, base_values)
        elif method == 'attendance_based':
            amount = PayrollService._calculate_attendance_based_amount(component, employee, payroll_period)
        elif method == 'slab':
            amount = PayrollService._calculate_slab_amount(component, employee, payroll_period, base_values)
        # Apply limits
        min_amt = getattr(component, 'minimum_amount', None)
        max_amt = getattr(component, 'maximum_amount', None)
        if min_amt and amount < min_amt:
            amount = min_amt
        if max_amt and amount > max_amt:
            amount = max_amt
        return amount

    @staticmethod
    def calculate_employee_salary_component_amount(employee_salary_component, payroll_period=None, base_values=None):
        """
        حساب قيمة مكون راتب موظف (من خلال مكون الراتب المرتبط)
        Calculate the amount for an employee salary component (delegates to salary component)
        """
        if employee_salary_component.override_calculation:
            return employee_salary_component.amount
        return PayrollService.calculate_salary_component_amount(
            employee_salary_component.salary_component,
            employee_salary_component.salary_structure.employee,
            payroll_period,
            base_values
        )

    @staticmethod
    def _get_basis_value(component, employee, payroll_period, base_values):
        """
        جلب قيمة الأساس لحساب النسبة
        Get the basis value for percentage calculation
        """
        from decimal import Decimal
        basis = getattr(component, 'percentage_basis', None)
        if basis == 'basic_salary':
            return getattr(employee, 'basic_salary', Decimal('0')) or Decimal('0')
        elif basis == 'gross_salary':
            return base_values.get('gross_salary', Decimal('0'))
        elif basis == 'total_earnings':
            return base_values.get('total_earnings', Decimal('0'))
        elif basis == 'specific_component' and getattr(component, 'basis_component', None):
            return base_values.get(f"component_{component.basis_component.code}", Decimal('0'))
        elif basis == 'attendance_days':
            return Decimal(str(base_values.get('attendance_days', 0)))
        elif basis == 'working_hours':
            return Decimal(str(base_values.get('working_hours', 0)))
        return Decimal('0')

    @staticmethod
    def _calculate_formula_amount(component, employee, payroll_period, base_values):
        """
        حساب قيمة المكون بناءً على معادلة
        Calculate amount using formula (placeholder, needs real implementation)
        """
        from decimal import Decimal
        try:
            formula = getattr(component, 'calculation_formula', None)
            # TODO: implement formula evaluation logic
            return Decimal('0')
        except:
            return Decimal('0')

    @staticmethod
    def _calculate_attendance_based_amount(component, employee, payroll_period):
        """
        حساب قيمة المكون بناءً على الحضور
        Calculate amount based on attendance (placeholder)
        """
        from decimal import Decimal
        # TODO: implement attendance-based calculation
        return Decimal('0')

    @staticmethod
    def _calculate_slab_amount(component, employee, payroll_period, base_values):
        """
        حساب قيمة المكون بطريقة الشرائح
        Calculate amount using slab method
        """
        from decimal import Decimal
        slabs = getattr(component, 'slabs', [])
        if not slabs:
            return Decimal('0')
        basis_value = PayrollService._get_basis_value(component, employee, payroll_period, base_values)
        total_amount = Decimal('0')
        for slab in slabs:
            slab_min = Decimal(str(slab.get('min', 0)))
            slab_max = Decimal(str(slab.get('max', float('inf'))))
            slab_rate = Decimal(str(slab.get('rate', 0)))
            if basis_value > slab_min:
                applicable_amount = min(basis_value, slab_max) - slab_min
                if applicable_amount > 0:
                    total_amount += applicable_amount * (slab_rate / 100)
        return total_amount
    
    @staticmethod
    def _calculate_component_amount(component: SalaryComponent, basic_salary: Decimal) -> Decimal:
        """Calculate the amount for a salary component
        
        Args:
            component: SalaryComponent object
            basic_salary: Basic salary amount
            
        Returns:
            Calculated component amount
        """
        try:
            if component.calculation_type == 'fixed':
                return component.amount
            elif component.calculation_type == 'percentage':
                return (basic_salary * component.percentage) / 100
            else:
                return Decimal('0.00')
        except Exception as e:
            logger.error(f"Error calculating component amount: {str(e)}")
            return Decimal('0.00')
    
    @staticmethod
    def calculate_department_payroll(department_id: uuid.UUID, 
                                   period_id: uuid.UUID) -> Dict:
        """Calculate payroll for all employees in a department
        
        Args:
            department_id: UUID of the department
            period_id: UUID of the payroll period
            
        Returns:
            Dictionary with department payroll summary
        """
        try:
            # Get all active employees in the department
            employees = Employee.objects.filter(
                department_id=department_id,
                is_active=True
            )
            
            department_summary = {
                'department_id': department_id,
                'period_id': period_id,
                'total_employees': employees.count(),
                'processed_employees': 0,
                'total_basic_salary': Decimal('0.00'),
                'total_allowances': Decimal('0.00'),
                'total_deductions': Decimal('0.00'),
                'total_gross_salary': Decimal('0.00'),
                'total_net_salary': Decimal('0.00'),
                'employee_calculations': []
            }
            
            for employee in employees:
                calculation = PayrollService.calculate_employee_salary(
                    employee.id, 
                    period_id, 
                    include_attendance=True
                )
                
                if 'error' not in calculation:
                    department_summary['processed_employees'] += 1
                    department_summary['total_basic_salary'] += calculation['basic_salary']
                    department_summary['total_allowances'] += calculation['total_allowances']
                    department_summary['total_deductions'] += calculation['total_deductions']
                    department_summary['total_gross_salary'] += calculation['gross_salary']
                    department_summary['total_net_salary'] += calculation['net_salary']
                
                department_summary['employee_calculations'].append(calculation)
            
            return department_summary
            
        except Exception as e:
            logger.error(f"Error calculating department payroll: {str(e)}")
            return {
                'error': f"Error calculating department payroll: {str(e)}",
                'department_id': department_id
            }
    
    @staticmethod
    def get_payroll_summary(period_id: uuid.UUID) -> Dict:
        """Get overall payroll summary for a period
        
        Args:
            period_id: UUID of the payroll period
            
        Returns:
            Dictionary with payroll summary
        """
        try:
            period = PayrollService.get_payroll_period_by_id(period_id)
            if not period:
                return {'error': 'Payroll period not found'}
            
            # Get all active employees
            employees = Employee.objects.filter(is_active=True)
            
            summary = {
                'period_id': period_id,
                'period_name': period.name,
                'total_employees': employees.count(),
                'processed_employees': 0,
                'total_basic_salary': Decimal('0.00'),
                'total_allowances': Decimal('0.00'),
                'total_deductions': Decimal('0.00'),
                'total_gross_salary': Decimal('0.00'),
                'total_net_salary': Decimal('0.00'),
                'department_summaries': {}
            }
            
            # Group employees by department
            departments = employees.values_list('department_id', flat=True).distinct()
            
            for dept_id in departments:
                if dept_id:
                    dept_summary = PayrollService.calculate_department_payroll(dept_id, period_id)
                    summary['department_summaries'][str(dept_id)] = dept_summary
                    
                    if 'error' not in dept_summary:
                        summary['processed_employees'] += dept_summary['processed_employees']
                        summary['total_basic_salary'] += dept_summary['total_basic_salary']
                        summary['total_allowances'] += dept_summary['total_allowances']
                        summary['total_deductions'] += dept_summary['total_deductions']
                        summary['total_gross_salary'] += dept_summary['total_gross_salary']
                        summary['total_net_salary'] += dept_summary['total_net_salary']
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting payroll summary: {str(e)}")
            return {'error': f"Error getting payroll summary: {str(e)}"}


class SalaryComponentService:
    """Service class for salary component management operations"""
    
    @staticmethod
    def get_component_by_id(component_id: uuid.UUID) -> Optional[SalaryComponent]:
        """Retrieve a salary component by ID
        
        Args:
            component_id: UUID of the salary component
            
        Returns:
            SalaryComponent object if found, None otherwise
        """
        try:
            return SalaryComponent.objects.get(id=component_id)
        except SalaryComponent.DoesNotExist:
            logger.warning(f"Salary component with ID {component_id} not found")
            return None
    
    @staticmethod
    def get_all_components() -> List[SalaryComponent]:
        """Get all salary components
        
        Returns:
            List of SalaryComponent objects
        """
        return list(SalaryComponent.objects.all().order_by('component_type', 'name'))
    
    @staticmethod
    def get_active_components() -> List[SalaryComponent]:
        """Get all active salary components
        
        Returns:
            List of active SalaryComponent objects
        """
        return list(SalaryComponent.objects.filter(is_active=True).order_by('component_type', 'name'))
    
    @staticmethod
    def get_components_by_type(component_type: str) -> List[SalaryComponent]:
        """Get salary components by type
        
        Args:
            component_type: Type of components ('allowance' or 'deduction')
            
        Returns:
            List of SalaryComponent objects
        """
        return list(SalaryComponent.objects.filter(
            component_type=component_type,
            is_active=True
        ).order_by('name'))
    
    @staticmethod
    @transaction.atomic
    def create_component(component_data: Dict) -> Tuple[SalaryComponent, bool, str]:
        """Create a new salary component
        
        Args:
            component_data: Dictionary with salary component data
            
        Returns:
            Tuple of (SalaryComponent object, success boolean, message string)
        """
        try:
            # Check if component with same name already exists
            if SalaryComponent.objects.filter(name=component_data['name']).exists():
                return None, False, f"Salary component with name {component_data['name']} already exists"
            
            # Create salary component
            component = SalaryComponent(**component_data)
            component.save()
            
            logger.info(f"Created salary component: {component.name}")
            return component, True, "Salary component created successfully"
            
        except Exception as e:
            logger.error(f"Error creating salary component: {str(e)}")
            return None, False, f"Error creating salary component: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def update_component(component_id: uuid.UUID, component_data: Dict) -> Tuple[SalaryComponent, bool, str]:
        """Update an existing salary component
        
        Args:
            component_id: UUID of the salary component to update
            component_data: Dictionary with updated salary component data
            
        Returns:
            Tuple of (SalaryComponent object, success boolean, message string)
        """
        try:
            component = SalaryComponentService.get_component_by_id(component_id)
            if not component:
                return None, False, f"Salary component with ID {component_id} not found"
            
            # Check if name is being changed and already exists
            if 'name' in component_data and component_data['name'] != component.name:
                if SalaryComponent.objects.filter(name=component_data['name']).exists():
                    return None, False, f"Salary component with name {component_data['name']} already exists"
            
            # Update salary component fields
            for key, value in component_data.items():
                setattr(component, key, value)
            
            component.save()
            
            logger.info(f"Updated salary component: {component.name}")
            return component, True, "Salary component updated successfully"
            
        except Exception as e:
            logger.error(f"Error updating salary component: {str(e)}")
            return None, False, f"Error updating salary component: {str(e)}"