"""Attendance Services Module

This module provides services for attendance management, including:
- Attendance record management
- Work shift management
- Attendance machine integration
- Attendance calculations and reporting
"""

import uuid
import logging
from datetime import date, datetime, timedelta, time
from typing import Dict, List, Optional, Tuple, Union, Any

from django.db import transaction
from django.db.models import Q, Count, Sum, Avg, F, Value, Min, Max
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.conf import settings

from Hr.models.attendance.attendance_record_models import AttendanceRecord
from Hr.models.attendance.work_shift_models import WorkShift
from Hr.models.attendance.attendance_machine_models import AttendanceMachine
from Hr.models.employee.employee_models import Employee

# Setup logger
logger = logging.getLogger(__name__)


class AttendanceService:
    """Service class for attendance management operations"""
    
    @staticmethod
    def get_attendance_record_by_id(record_id: uuid.UUID) -> Optional[AttendanceRecord]:
        """Retrieve an attendance record by ID
        
        Args:
            record_id: UUID of the attendance record
            
        Returns:
            AttendanceRecord object if found, None otherwise
        """
        try:
            return AttendanceRecord.objects.get(id=record_id)
        except AttendanceRecord.DoesNotExist:
            logger.warning(f"Attendance record with ID {record_id} not found")
            return None
    
    @staticmethod
    def get_employee_attendance_records(employee_id: uuid.UUID, 
                                      start_date: date = None, 
                                      end_date: date = None) -> List[AttendanceRecord]:
        """Get attendance records for an employee within a date range
        
        Args:
            employee_id: UUID of the employee
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            
        Returns:
            List of AttendanceRecord objects
        """
        try:
            queryset = AttendanceRecord.objects.filter(employee_id=employee_id)
            
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
            
            return list(queryset.order_by('-date', '-check_in_time'))
            
        except Exception as e:
            logger.error(f"Error retrieving attendance records: {str(e)}")
            return []
    
    @staticmethod
    def get_daily_attendance_records(target_date: date) -> List[AttendanceRecord]:
        """Get all attendance records for a specific date
        
        Args:
            target_date: Date to get records for
            
        Returns:
            List of AttendanceRecord objects
        """
        try:
            return list(AttendanceRecord.objects.filter(date=target_date).order_by('employee__full_name'))
            
        except Exception as e:
            logger.error(f"Error retrieving daily attendance records: {str(e)}")
            return []
    
    @staticmethod
    @transaction.atomic
    def record_check_in(employee_id: uuid.UUID, 
                       check_in_time: datetime = None,
                       machine_id: uuid.UUID = None,
                       notes: str = None) -> Tuple[AttendanceRecord, bool, str]:
        """Record employee check-in
        
        Args:
            employee_id: UUID of the employee
            check_in_time: Check-in time (defaults to now)
            machine_id: UUID of the attendance machine (optional)
            notes: Additional notes (optional)
            
        Returns:
            Tuple of (AttendanceRecord object, success boolean, message string)
        """
        try:
            # Get employee
            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                return None, False, f"Employee with ID {employee_id} not found"
            
            if not employee.is_active:
                return None, False, "Employee is not active"
            
            # Use current time if not provided
            if not check_in_time:
                check_in_time = timezone.now()
            
            record_date = check_in_time.date()
            
            # Check if employee already has a record for today
            existing_record = AttendanceRecord.objects.filter(
                employee=employee,
                date=record_date
            ).first()
            
            if existing_record:
                if existing_record.check_in_time:
                    return None, False, "Employee has already checked in today"
                else:
                    # Update existing record with check-in time
                    existing_record.check_in_time = check_in_time.time()
                    if machine_id:
                        try:
                            machine = AttendanceMachine.objects.get(id=machine_id)
                            existing_record.machine = machine
                        except AttendanceMachine.DoesNotExist:
                            pass
                    if notes:
                        existing_record.notes = f"{existing_record.notes}\\n{notes}" if existing_record.notes else notes
                    existing_record.save()
                    
                    logger.info(f"Updated check-in for employee {employee.full_name} at {check_in_time}")
                    return existing_record, True, "Check-in recorded successfully"
            else:
                # Create new attendance record
                record_data = {
                    'employee': employee,
                    'date': record_date,
                    'check_in_time': check_in_time.time(),
                    'notes': notes
                }
                
                if machine_id:
                    try:
                        machine = AttendanceMachine.objects.get(id=machine_id)
                        record_data['machine'] = machine
                    except AttendanceMachine.DoesNotExist:
                        pass
                
                record = AttendanceRecord(**record_data)
                record.save()
                
                logger.info(f"Recorded check-in for employee {employee.full_name} at {check_in_time}")
                return record, True, "Check-in recorded successfully"
                
        except Exception as e:
            logger.error(f"Error recording check-in: {str(e)}")
            return None, False, f"Error recording check-in: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def record_check_out(employee_id: uuid.UUID, 
                        check_out_time: datetime = None,
                        machine_id: uuid.UUID = None,
                        notes: str = None) -> Tuple[AttendanceRecord, bool, str]:
        """Record employee check-out
        
        Args:
            employee_id: UUID of the employee
            check_out_time: Check-out time (defaults to now)
            machine_id: UUID of the attendance machine (optional)
            notes: Additional notes (optional)
            
        Returns:
            Tuple of (AttendanceRecord object, success boolean, message string)
        """
        try:
            # Get employee
            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                return None, False, f"Employee with ID {employee_id} not found"
            
            # Use current time if not provided
            if not check_out_time:
                check_out_time = timezone.now()
            
            record_date = check_out_time.date()
            
            # Find today's attendance record
            record = AttendanceRecord.objects.filter(
                employee=employee,
                date=record_date
            ).first()
            
            if not record:
                return None, False, "No check-in record found for today"
            
            if not record.check_in_time:
                return None, False, "Employee has not checked in yet"
            
            if record.check_out_time:
                return None, False, "Employee has already checked out today"
            
            # Update record with check-out time
            record.check_out_time = check_out_time.time()
            
            if machine_id:
                try:
                    machine = AttendanceMachine.objects.get(id=machine_id)
                    record.machine = machine
                except AttendanceMachine.DoesNotExist:
                    pass
            
            if notes:
                record.notes = f"{record.notes}\\n{notes}" if record.notes else notes
            
            # Calculate worked hours
            record.calculate_worked_hours()
            record.save()
            
            logger.info(f"Recorded check-out for employee {employee.full_name} at {check_out_time}")
            return record, True, "Check-out recorded successfully"
            
        except Exception as e:
            logger.error(f"Error recording check-out: {str(e)}")
            return None, False, f"Error recording check-out: {str(e)}"
    
    @staticmethod
    def get_employee_attendance_summary(employee_id: uuid.UUID, 
                                      start_date: date, 
                                      end_date: date) -> Dict:
        """Get attendance summary for an employee within a date range
        
        Args:
            employee_id: UUID of the employee
            start_date: Start date for the summary
            end_date: End date for the summary
            
        Returns:
            Dictionary with attendance summary
        """
        try:
            records = AttendanceRecord.objects.filter(
                employee_id=employee_id,
                date__gte=start_date,
                date__lte=end_date
            )
            
            total_days = (end_date - start_date).days + 1
            present_days = records.filter(check_in_time__isnull=False).count()
            absent_days = total_days - present_days
            
            # Calculate total worked hours
            total_worked_hours = sum([
                record.worked_hours or 0 
                for record in records 
                if record.worked_hours
            ])
            
            # Calculate late arrivals (assuming 9:00 AM as standard start time)
            standard_start_time = time(9, 0)
            late_arrivals = records.filter(
                check_in_time__gt=standard_start_time
            ).count()
            
            # Calculate early departures (assuming 5:00 PM as standard end time)
            standard_end_time = time(17, 0)
            early_departures = records.filter(
                check_out_time__lt=standard_end_time,
                check_out_time__isnull=False
            ).count()
            
            return {
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'attendance_rate': (present_days / total_days * 100) if total_days > 0 else 0,
                'total_worked_hours': total_worked_hours,
                'average_daily_hours': (total_worked_hours / present_days) if present_days > 0 else 0,
                'late_arrivals': late_arrivals,
                'early_departures': early_departures,
            }
            
        except Exception as e:
            logger.error(f"Error calculating attendance summary: {str(e)}")
            return {}
    
    @staticmethod
    def get_department_attendance_summary(department_id: uuid.UUID, 
                                        target_date: date) -> Dict:
        """Get attendance summary for a department on a specific date
        
        Args:
            department_id: UUID of the department
            target_date: Date to get summary for
            
        Returns:
            Dictionary with department attendance summary
        """
        try:
            # Get all employees in the department
            employees = Employee.objects.filter(
                department_id=department_id,
                is_active=True
            )
            
            total_employees = employees.count()
            
            # Get attendance records for the date
            records = AttendanceRecord.objects.filter(
                employee__in=employees,
                date=target_date
            )
            
            present_employees = records.filter(check_in_time__isnull=False).count()
            absent_employees = total_employees - present_employees
            
            # Calculate late arrivals
            standard_start_time = time(9, 0)
            late_employees = records.filter(
                check_in_time__gt=standard_start_time
            ).count()
            
            return {
                'total_employees': total_employees,
                'present_employees': present_employees,
                'absent_employees': absent_employees,
                'attendance_rate': (present_employees / total_employees * 100) if total_employees > 0 else 0,
                'late_employees': late_employees,
                'late_rate': (late_employees / present_employees * 100) if present_employees > 0 else 0,
            }
            
        except Exception as e:
            logger.error(f"Error calculating department attendance summary: {str(e)}")
            return {}
    
    @staticmethod
    @transaction.atomic
    def bulk_import_attendance_records(records_data: List[Dict]) -> Tuple[int, int, List[str]]:
        """Bulk import attendance records from external source
        
        Args:
            records_data: List of dictionaries with attendance data
            
        Returns:
            Tuple of (successful_count, failed_count, error_messages)
        """
        successful_count = 0
        failed_count = 0
        error_messages = []
        
        for record_data in records_data:
            try:
                # Validate required fields
                required_fields = ['employee_id', 'date', 'check_in_time']
                missing_fields = [field for field in required_fields if field not in record_data]
                
                if missing_fields:
                    error_messages.append(f"Missing required fields: {', '.join(missing_fields)}")
                    failed_count += 1
                    continue
                
                # Get employee
                try:
                    employee = Employee.objects.get(id=record_data['employee_id'])
                except Employee.DoesNotExist:
                    error_messages.append(f"Employee with ID {record_data['employee_id']} not found")
                    failed_count += 1
                    continue
                
                # Check if record already exists
                existing_record = AttendanceRecord.objects.filter(
                    employee=employee,
                    date=record_data['date']
                ).first()
                
                if existing_record:
                    # Update existing record
                    for key, value in record_data.items():
                        if key != 'employee_id' and hasattr(existing_record, key):
                            setattr(existing_record, key, value)
                    existing_record.save()
                else:
                    # Create new record
                    record_data['employee'] = employee
                    del record_data['employee_id']
                    
                    record = AttendanceRecord(**record_data)
                    record.save()
                
                successful_count += 1
                
            except Exception as e:
                error_messages.append(f"Error processing record: {str(e)}")
                failed_count += 1
        
        logger.info(f"Bulk import completed: {successful_count} successful, {failed_count} failed")
        return successful_count, failed_count, error_messages


class WorkShiftService:
    """Service class for work shift management operations"""
    
    @staticmethod
    def get_shift_by_id(shift_id: uuid.UUID) -> Optional[WorkShift]:
        """Retrieve a work shift by ID
        
        Args:
            shift_id: UUID of the work shift
            
        Returns:
            WorkShift object if found, None otherwise
        """
        try:
            return WorkShift.objects.get(id=shift_id)
        except WorkShift.DoesNotExist:
            logger.warning(f"Work shift with ID {shift_id} not found")
            return None
    
    @staticmethod
    def get_all_shifts() -> List[WorkShift]:
        """Get all work shifts
        
        Returns:
            List of WorkShift objects
        """
        return list(WorkShift.objects.all().order_by('name'))
    
    @staticmethod
    def get_active_shifts() -> List[WorkShift]:
        """Get all active work shifts
        
        Returns:
            List of active WorkShift objects
        """
        return list(WorkShift.objects.filter(is_active=True).order_by('name'))
    
    @staticmethod
    @transaction.atomic
    def create_shift(shift_data: Dict) -> Tuple[WorkShift, bool, str]:
        """Create a new work shift
        
        Args:
            shift_data: Dictionary with work shift data
            
        Returns:
            Tuple of (WorkShift object, success boolean, message string)
        """
        try:
            # Check if shift with same name already exists
            if WorkShift.objects.filter(name=shift_data['name']).exists():
                return None, False, f"Work shift with name {shift_data['name']} already exists"
            
            # Create work shift
            shift = WorkShift(**shift_data)
            shift.save()
            
            logger.info(f"Created work shift: {shift.name}")
            return shift, True, "Work shift created successfully"
            
        except Exception as e:
            logger.error(f"Error creating work shift: {str(e)}")
            return None, False, f"Error creating work shift: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def update_shift(shift_id: uuid.UUID, shift_data: Dict) -> Tuple[WorkShift, bool, str]:
        """Update an existing work shift
        
        Args:
            shift_id: UUID of the work shift to update
            shift_data: Dictionary with updated work shift data
            
        Returns:
            Tuple of (WorkShift object, success boolean, message string)
        """
        try:
            shift = WorkShiftService.get_shift_by_id(shift_id)
            if not shift:
                return None, False, f"Work shift with ID {shift_id} not found"
            
            # Check if name is being changed and already exists
            if 'name' in shift_data and shift_data['name'] != shift.name:
                if WorkShift.objects.filter(name=shift_data['name']).exists():
                    return None, False, f"Work shift with name {shift_data['name']} already exists"
            
            # Update work shift fields
            for key, value in shift_data.items():
                setattr(shift, key, value)
            
            shift.save()
            
            logger.info(f"Updated work shift: {shift.name}")
            return shift, True, "Work shift updated successfully"
            
        except Exception as e:
            logger.error(f"Error updating work shift: {str(e)}")
            return None, False, f"Error updating work shift: {str(e)}"


class AttendanceMachineService:
    """Service class for attendance machine management operations"""
    
    @staticmethod
    def get_machine_by_id(machine_id: uuid.UUID) -> Optional[AttendanceMachine]:
        """Retrieve an attendance machine by ID
        
        Args:
            machine_id: UUID of the attendance machine
            
        Returns:
            AttendanceMachine object if found, None otherwise
        """
        try:
            return AttendanceMachine.objects.get(id=machine_id)
        except AttendanceMachine.DoesNotExist:
            logger.warning(f"Attendance machine with ID {machine_id} not found")
            return None
    
    @staticmethod
    def get_all_machines() -> List[AttendanceMachine]:
        """Get all attendance machines
        
        Returns:
            List of AttendanceMachine objects
        """
        return list(AttendanceMachine.objects.all().order_by('name'))
    
    @staticmethod
    def get_active_machines() -> List[AttendanceMachine]:
        """Get all active attendance machines
        
        Returns:
            List of active AttendanceMachine objects
        """
        return list(AttendanceMachine.objects.filter(is_active=True).order_by('name'))
    
    @staticmethod
    @transaction.atomic
    def create_machine(machine_data: Dict) -> Tuple[AttendanceMachine, bool, str]:
        """Create a new attendance machine
        
        Args:
            machine_data: Dictionary with attendance machine data
            
        Returns:
            Tuple of (AttendanceMachine object, success boolean, message string)
        """
        try:
            # Check if machine with same name or IP already exists
            if AttendanceMachine.objects.filter(name=machine_data['name']).exists():
                return None, False, f"Attendance machine with name {machine_data['name']} already exists"
            
            if 'ip_address' in machine_data and AttendanceMachine.objects.filter(ip_address=machine_data['ip_address']).exists():
                return None, False, f"Attendance machine with IP {machine_data['ip_address']} already exists"
            
            # Create attendance machine
            machine = AttendanceMachine(**machine_data)
            machine.save()
            
            logger.info(f"Created attendance machine: {machine.name}")
            return machine, True, "Attendance machine created successfully"
            
        except Exception as e:
            logger.error(f"Error creating attendance machine: {str(e)}")
            return None, False, f"Error creating attendance machine: {str(e)}"
    
    @staticmethod
    def test_machine_connection(machine_id: uuid.UUID) -> Tuple[bool, str]:
        """Test connection to an attendance machine
        
        Args:
            machine_id: UUID of the attendance machine
            
        Returns:
            Tuple of (success boolean, message string)
        """
        try:
            machine = AttendanceMachineService.get_machine_by_id(machine_id)
            if not machine:
                return False, f"Attendance machine with ID {machine_id} not found"
            
            # TODO: Implement actual connection test based on machine type
            # This is a placeholder implementation
            
            logger.info(f"Tested connection to attendance machine: {machine.name}")
            return True, "Connection test successful"
            
        except Exception as e:
            logger.error(f"Error testing machine connection: {str(e)}")
            return False, f"Error testing machine connection: {str(e)}"