"""Leave Services Module

This module provides services for leave management, including:
- Leave request processing and approval workflow
- Leave balance calculation and tracking
- Leave type management
- Leave reporting and analytics
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
from django.contrib.auth import get_user_model

from Hr.models.employee.employee_models import Employee

# Setup logger
logger = logging.getLogger(__name__)
User = get_user_model()


class LeaveService:
    """Service class for leave management operations"""
    
    @staticmethod
    def get_leave_types() -> List[Dict]:
        """Get all available leave types
        
        Returns:
            List of leave type dictionaries
        """
        # This is a placeholder - in a real implementation, you would have a LeaveType model
        return [
            {
                'id': 'annual',
                'name': 'Annual Leave',
                'name_ar': 'إجازة سنوية',
                'max_days_per_year': 30,
                'carry_forward': True,
                'requires_approval': True,
                'is_paid': True
            },
            {
                'id': 'sick',
                'name': 'Sick Leave',
                'name_ar': 'إجازة مرضية',
                'max_days_per_year': 15,
                'carry_forward': False,
                'requires_approval': False,
                'is_paid': True
            },
            {
                'id': 'emergency',
                'name': 'Emergency Leave',
                'name_ar': 'إجازة طارئة',
                'max_days_per_year': 5,
                'carry_forward': False,
                'requires_approval': True,
                'is_paid': False
            },
            {
                'id': 'maternity',
                'name': 'Maternity Leave',
                'name_ar': 'إجازة أمومة',
                'max_days_per_year': 90,
                'carry_forward': False,
                'requires_approval': True,
                'is_paid': True
            },
            {
                'id': 'paternity',
                'name': 'Paternity Leave',
                'name_ar': 'إجازة أبوة',
                'max_days_per_year': 7,
                'carry_forward': False,
                'requires_approval': True,
                'is_paid': True
            }
        ]
    
    @staticmethod
    def get_leave_type_by_id(leave_type_id: str) -> Optional[Dict]:
        """Get a specific leave type by ID
        
        Args:
            leave_type_id: ID of the leave type
            
        Returns:
            Leave type dictionary if found, None otherwise
        """
        leave_types = LeaveService.get_leave_types()
        return next((lt for lt in leave_types if lt['id'] == leave_type_id), None)
    
    @staticmethod
    def calculate_employee_leave_balance(employee_id: uuid.UUID, 
                                       leave_type_id: str,
                                       year: int = None) -> Dict:
        """Calculate leave balance for an employee
        
        Args:
            employee_id: UUID of the employee
            leave_type_id: ID of the leave type
            year: Year to calculate for (defaults to current year)
            
        Returns:
            Dictionary with leave balance information
        """
        try:
            # Get employee
            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                return {'error': f'Employee with ID {employee_id} not found'}
            
            # Get leave type
            leave_type = LeaveService.get_leave_type_by_id(leave_type_id)
            if not leave_type:
                return {'error': f'Leave type {leave_type_id} not found'}
            
            if not year:
                year = date.today().year
            
            # Calculate entitlement based on employment date and leave type
            entitlement = LeaveService._calculate_leave_entitlement(employee, leave_type, year)
            
            # Calculate used leave (placeholder - would query actual leave records)
            used_days = LeaveService._calculate_used_leave(employee_id, leave_type_id, year)
            
            # Calculate carry forward from previous year
            carry_forward = 0
            if leave_type['carry_forward'] and year > employee.hire_date.year:
                carry_forward = LeaveService._calculate_carry_forward(employee_id, leave_type_id, year - 1)
            
            # Calculate available balance
            total_entitlement = entitlement + carry_forward
            available_balance = total_entitlement - used_days
            
            return {
                'employee_id': employee_id,
                'employee_name': employee.full_name,
                'leave_type_id': leave_type_id,
                'leave_type_name': leave_type['name'],
                'year': year,
                'entitlement': entitlement,
                'carry_forward': carry_forward,
                'total_entitlement': total_entitlement,
                'used_days': used_days,
                'available_balance': available_balance,
                'pending_requests': 0  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error calculating leave balance: {str(e)}")
            return {'error': f'Error calculating leave balance: {str(e)}'}
    
    @staticmethod
    def _calculate_leave_entitlement(employee: Employee, leave_type: Dict, year: int) -> int:
        """Calculate leave entitlement for an employee
        
        Args:
            employee: Employee object
            leave_type: Leave type dictionary
            year: Year to calculate for
            
        Returns:
            Number of entitled leave days
        """
        try:
            # If employee was hired in the current year, calculate pro-rata
            if employee.hire_date.year == year:
                months_worked = 12 - employee.hire_date.month + 1
                pro_rata_entitlement = (leave_type['max_days_per_year'] * months_worked) / 12
                return int(pro_rata_entitlement)
            else:
                return leave_type['max_days_per_year']
                
        except Exception as e:
            logger.error(f"Error calculating leave entitlement: {str(e)}")
            return 0
    
    @staticmethod
    def _calculate_used_leave(employee_id: uuid.UUID, leave_type_id: str, year: int) -> int:
        """Calculate used leave days for an employee
        
        Args:
            employee_id: UUID of the employee
            leave_type_id: ID of the leave type
            year: Year to calculate for
            
        Returns:
            Number of used leave days
        """
        # Placeholder implementation - would query actual leave records
        # In a real implementation, you would have a LeaveRequest model
        return 0
    
    @staticmethod
    def _calculate_carry_forward(employee_id: uuid.UUID, leave_type_id: str, year: int) -> int:
        """Calculate carry forward leave days from previous year
        
        Args:
            employee_id: UUID of the employee
            leave_type_id: ID of the leave type
            year: Previous year to calculate carry forward from
            
        Returns:
            Number of carry forward leave days
        """
        # Placeholder implementation - would calculate based on previous year's balance
        return 0
    
    @staticmethod
    def get_employee_leave_summary(employee_id: uuid.UUID, year: int = None) -> Dict:
        """Get comprehensive leave summary for an employee
        
        Args:
            employee_id: UUID of the employee
            year: Year to get summary for (defaults to current year)
            
        Returns:
            Dictionary with complete leave summary
        """
        try:
            if not year:
                year = date.today().year
            
            # Get employee
            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                return {'error': f'Employee with ID {employee_id} not found'}
            
            summary = {
                'employee_id': employee_id,
                'employee_name': employee.full_name,
                'year': year,
                'leave_balances': {},
                'total_entitlement': 0,
                'total_used': 0,
                'total_available': 0
            }
            
            # Calculate balance for each leave type
            for leave_type in LeaveService.get_leave_types():
                balance = LeaveService.calculate_employee_leave_balance(
                    employee_id, 
                    leave_type['id'], 
                    year
                )
                
                if 'error' not in balance:
                    summary['leave_balances'][leave_type['id']] = balance
                    summary['total_entitlement'] += balance['total_entitlement']
                    summary['total_used'] += balance['used_days']
                    summary['total_available'] += balance['available_balance']
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting employee leave summary: {str(e)}")
            return {'error': f'Error getting employee leave summary: {str(e)}'}
    
    @staticmethod
    def validate_leave_request(employee_id: uuid.UUID, 
                             leave_type_id: str,
                             start_date: date,
                             end_date: date,
                             days_requested: int = None) -> Dict:
        """Validate a leave request
        
        Args:
            employee_id: UUID of the employee
            leave_type_id: ID of the leave type
            start_date: Start date of leave
            end_date: End date of leave
            days_requested: Number of days requested (optional, calculated if not provided)
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Get employee
            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f'Employee with ID {employee_id} not found')
                return validation_result
            
            # Get leave type
            leave_type = LeaveService.get_leave_type_by_id(leave_type_id)
            if not leave_type:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f'Leave type {leave_type_id} not found')
                return validation_result
            
            # Validate dates
            if start_date > end_date:
                validation_result['is_valid'] = False
                validation_result['errors'].append('Start date cannot be after end date')
            
            if start_date < date.today():
                validation_result['warnings'].append('Leave request is for a past date')
            
            # Calculate days if not provided
            if not days_requested:
                days_requested = (end_date - start_date).days + 1
            
            # Check leave balance
            balance = LeaveService.calculate_employee_leave_balance(
                employee_id, 
                leave_type_id, 
                start_date.year
            )
            
            if 'error' not in balance:
                if days_requested > balance['available_balance']:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(
                        f'Insufficient leave balance. Available: {balance["available_balance"]}, Requested: {days_requested}'
                    )
            
            # Check for overlapping leave requests (placeholder)
            # In a real implementation, you would check against existing leave requests
            
            # Check minimum notice period (placeholder)
            notice_days = (start_date - date.today()).days
            if notice_days < 1 and leave_type['requires_approval']:
                validation_result['warnings'].append('Leave request has insufficient notice period')
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating leave request: {str(e)}")
            return {
                'is_valid': False,
                'errors': [f'Error validating leave request: {str(e)}'],
                'warnings': []
            }
    
    @staticmethod
    def get_department_leave_summary(department_id: uuid.UUID, 
                                   start_date: date = None,
                                   end_date: date = None) -> Dict:
        """Get leave summary for a department
        
        Args:
            department_id: UUID of the department
            start_date: Start date for the summary (optional)
            end_date: End date for the summary (optional)
            
        Returns:
            Dictionary with department leave summary
        """
        try:
            if not start_date:
                start_date = date(date.today().year, 1, 1)
            if not end_date:
                end_date = date(date.today().year, 12, 31)
            
            # Get all employees in the department
            employees = Employee.objects.filter(
                department_id=department_id,
                is_active=True
            )
            
            summary = {
                'department_id': department_id,
                'period_start': start_date,
                'period_end': end_date,
                'total_employees': employees.count(),
                'employee_summaries': [],
                'leave_type_totals': {},
                'overall_totals': {
                    'total_entitlement': 0,
                    'total_used': 0,
                    'total_available': 0
                }
            }
            
            # Get summary for each employee
            for employee in employees:
                employee_summary = LeaveService.get_employee_leave_summary(
                    employee.id, 
                    start_date.year
                )
                
                if 'error' not in employee_summary:
                    summary['employee_summaries'].append(employee_summary)
                    summary['overall_totals']['total_entitlement'] += employee_summary['total_entitlement']
                    summary['overall_totals']['total_used'] += employee_summary['total_used']
                    summary['overall_totals']['total_available'] += employee_summary['total_available']
            
            # Calculate totals by leave type
            for leave_type in LeaveService.get_leave_types():
                leave_type_total = {
                    'total_entitlement': 0,
                    'total_used': 0,
                    'total_available': 0
                }
                
                for emp_summary in summary['employee_summaries']:
                    if leave_type['id'] in emp_summary['leave_balances']:
                        balance = emp_summary['leave_balances'][leave_type['id']]
                        leave_type_total['total_entitlement'] += balance['total_entitlement']
                        leave_type_total['total_used'] += balance['used_days']
                        leave_type_total['total_available'] += balance['available_balance']
                
                summary['leave_type_totals'][leave_type['id']] = leave_type_total
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting department leave summary: {str(e)}")
            return {'error': f'Error getting department leave summary: {str(e)}'}
    
    @staticmethod
    def get_leave_calendar(department_id: uuid.UUID = None,
                          start_date: date = None,
                          end_date: date = None) -> Dict:
        """Get leave calendar showing who is on leave when
        
        Args:
            department_id: UUID of the department (optional, all departments if not provided)
            start_date: Start date for the calendar (optional)
            end_date: End date for the calendar (optional)
            
        Returns:
            Dictionary with leave calendar data
        """
        try:
            if not start_date:
                start_date = date.today()
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            # Get employees
            if department_id:
                employees = Employee.objects.filter(
                    department_id=department_id,
                    is_active=True
                )
            else:
                employees = Employee.objects.filter(is_active=True)
            
            calendar_data = {
                'start_date': start_date,
                'end_date': end_date,
                'department_id': department_id,
                'daily_leave_data': {},
                'employee_leave_periods': []
            }
            
            # Initialize daily data
            current_date = start_date
            while current_date <= end_date:
                calendar_data['daily_leave_data'][current_date.isoformat()] = {
                    'date': current_date,
                    'employees_on_leave': [],
                    'total_on_leave': 0
                }
                current_date += timedelta(days=1)
            
            # Placeholder for actual leave data
            # In a real implementation, you would query leave requests and populate the calendar
            
            return calendar_data
            
        except Exception as e:
            logger.error(f"Error getting leave calendar: {str(e)}")
            return {'error': f'Error getting leave calendar: {str(e)}'}
    
    @staticmethod
    def generate_leave_report(report_type: str, 
                            filters: Dict = None) -> Dict:
        """Generate various leave reports
        
        Args:
            report_type: Type of report ('balance', 'usage', 'trends', 'compliance')
            filters: Dictionary with filter parameters
            
        Returns:
            Dictionary with report data
        """
        try:
            if not filters:
                filters = {}
            
            report_data = {
                'report_type': report_type,
                'generated_at': timezone.now(),
                'filters': filters,
                'data': {}
            }
            
            if report_type == 'balance':
                # Leave balance report
                report_data['data'] = LeaveService._generate_balance_report(filters)
            elif report_type == 'usage':
                # Leave usage report
                report_data['data'] = LeaveService._generate_usage_report(filters)
            elif report_type == 'trends':
                # Leave trends report
                report_data['data'] = LeaveService._generate_trends_report(filters)
            elif report_type == 'compliance':
                # Leave compliance report
                report_data['data'] = LeaveService._generate_compliance_report(filters)
            else:
                report_data['error'] = f'Unknown report type: {report_type}'
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating leave report: {str(e)}")
            return {'error': f'Error generating leave report: {str(e)}'}
    
    @staticmethod
    def _generate_balance_report(filters: Dict) -> Dict:
        """Generate leave balance report
        
        Args:
            filters: Filter parameters
            
        Returns:
            Dictionary with balance report data
        """
        # Placeholder implementation
        return {
            'title': 'Leave Balance Report',
            'summary': 'Employee leave balances by type',
            'data': []
        }
    
    @staticmethod
    def _generate_usage_report(filters: Dict) -> Dict:
        """Generate leave usage report
        
        Args:
            filters: Filter parameters
            
        Returns:
            Dictionary with usage report data
        """
        # Placeholder implementation
        return {
            'title': 'Leave Usage Report',
            'summary': 'Leave usage patterns and statistics',
            'data': []
        }
    
    @staticmethod
    def _generate_trends_report(filters: Dict) -> Dict:
        """Generate leave trends report
        
        Args:
            filters: Filter parameters
            
        Returns:
            Dictionary with trends report data
        """
        # Placeholder implementation
        return {
            'title': 'Leave Trends Report',
            'summary': 'Leave usage trends over time',
            'data': []
        }
    
    @staticmethod
    def _generate_compliance_report(filters: Dict) -> Dict:
        """Generate leave compliance report
        
        Args:
            filters: Filter parameters
            
        Returns:
            Dictionary with compliance report data
        """
        # Placeholder implementation
        return {
            'title': 'Leave Compliance Report',
            'summary': 'Leave policy compliance and violations',
            'data': []
        }