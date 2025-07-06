"""
Attendance Processor for processing and storing attendance records
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

from Hr.models.attendance_models import AttendanceMachine, AttendanceRecord, AttendanceSummary
from Hr.models.employee_model import Employee

logger = logging.getLogger(__name__)


class AttendanceProcessor:
    """Service for processing attendance records from ZK devices"""
    
    def __init__(self):
        """Initialize attendance processor"""
        pass
    
    def process_zk_records(self, machine: AttendanceMachine, 
                          zk_records: List[Dict], 
                          clear_existing: bool = False,
                          user: Optional[User] = None) -> Dict:
        """
        Process ZK device records and store them in database
        
        Args:
            machine: AttendanceMachine instance
            zk_records: List of records from ZK device
            clear_existing: Whether to clear existing records first
            user: User performing the operation
            
        Returns:
            Dictionary with processing results
        """
        results = {
            'total_records': len(zk_records),
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'error_details': []
        }
        
        try:
            with transaction.atomic():
                # Clear existing records if requested
                if clear_existing:
                    deleted_count = AttendanceRecord.objects.filter(machine=machine).delete()[0]
                    logger.info(f"Cleared {deleted_count} existing records for machine {machine.name}")
                
                # Process each record
                for zk_record in zk_records:
                    try:
                        result = self._process_single_record(machine, zk_record, user)
                        if result == 'processed':
                            results['processed'] += 1
                        elif result == 'skipped':
                            results['skipped'] += 1
                    except Exception as e:
                        results['errors'] += 1
                        error_msg = f"Error processing record {zk_record}: {str(e)}"
                        results['error_details'].append(error_msg)
                        logger.error(error_msg)
                
                # Generate attendance summaries
                self._generate_attendance_summaries(machine, zk_records)
                
                logger.info(f"Processed {results['processed']} records from machine {machine.name}")
                
        except Exception as e:
            logger.error(f"Error processing ZK records: {str(e)}")
            results['errors'] = len(zk_records)
            results['error_details'].append(f"Transaction failed: {str(e)}")
        
        return results
    
    def _process_single_record(self, machine: AttendanceMachine, 
                              zk_record: Dict, user: Optional[User] = None) -> str:
        """
        Process a single ZK record
        
        Returns:
            'processed', 'skipped', or raises exception
        """
        # Extract data from ZK record
        user_id = zk_record.get('user_id')
        timestamp = zk_record.get('timestamp')
        verify_type = zk_record.get('verify_type', 1)  # 1 = fingerprint
        in_out_mode = zk_record.get('in_out_mode', 0)  # 0 = check-in, 1 = check-out
        
        if not user_id or not timestamp:
            raise ValueError("Missing required fields: user_id or timestamp")
        
        # Find employee by user_id (assuming user_id maps to employee_id or emp_code)
        try:
            employee = Employee.objects.get(emp_code=user_id)
        except Employee.DoesNotExist:
            # Try by ID if emp_code doesn't match
            try:
                employee = Employee.objects.get(id=int(user_id))
            except (Employee.DoesNotExist, ValueError):
                raise ValueError(f"Employee not found for user_id: {user_id}")
        
        # Determine record type
        record_type = 'in' if in_out_mode == 0 else 'out'
        
        # Check if record already exists
        existing_record = AttendanceRecord.objects.filter(
            employee=employee,
            machine=machine,
            timestamp=timestamp
        ).first()
        
        if existing_record:
            return 'skipped'
        
        # Create new attendance record
        attendance_record = AttendanceRecord.objects.create(
            employee=employee,
            machine=machine,
            timestamp=timestamp,
            record_type=record_type,
            source='machine',
            verify_type=self._get_verify_type_display(verify_type),
            raw_data=zk_record.get('raw_data', ''),
            created_by=user
        )
        
        logger.debug(f"Created attendance record: {attendance_record}")
        return 'processed'
    
    def _get_verify_type_display(self, verify_type: int) -> str:
        """Convert ZK verify type to display string"""
        verify_types = {
            0: 'Password',
            1: 'Fingerprint',
            2: 'Card',
            3: 'Face',
            4: 'Voice',
            5: 'Palm'
        }
        return verify_types.get(verify_type, 'Unknown')
    
    def _generate_attendance_summaries(self, machine: AttendanceMachine, 
                                     zk_records: List[Dict]) -> None:
        """Generate daily attendance summaries for processed records"""
        try:
            # Get unique dates from records
            dates = set()
            for record in zk_records:
                timestamp = record.get('timestamp')
                if timestamp:
                    dates.add(timestamp.date())
            
            # Generate summary for each date
            for date in dates:
                self._generate_daily_summary(machine, date)
                
        except Exception as e:
            logger.error(f"Error generating attendance summaries: {str(e)}")
    
    def _generate_daily_summary(self, machine: AttendanceMachine, date: datetime.date) -> None:
        """Generate daily attendance summary for a specific date"""
        try:
            # Get all records for this date and machine
            start_datetime = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            end_datetime = timezone.make_aware(datetime.combine(date, datetime.max.time()))
            
            records = AttendanceRecord.objects.filter(
                machine=machine,
                timestamp__range=(start_datetime, end_datetime)
            ).select_related('employee')
            
            # Group records by employee
            employee_records = {}
            for record in records:
                emp_id = record.employee.id
                if emp_id not in employee_records:
                    employee_records[emp_id] = {
                        'employee': record.employee,
                        'check_ins': [],
                        'check_outs': []
                    }
                
                if record.record_type == 'in':
                    employee_records[emp_id]['check_ins'].append(record)
                else:
                    employee_records[emp_id]['check_outs'].append(record)
            
            # Create or update summaries for each employee
            for emp_id, data in employee_records.items():
                employee = data['employee']
                check_ins = sorted(data['check_ins'], key=lambda x: x.timestamp)
                check_outs = sorted(data['check_outs'], key=lambda x: x.timestamp)
                
                # Calculate work hours
                total_hours = self._calculate_work_hours(check_ins, check_outs)
                
                # Get or create summary
                summary, created = AttendanceSummary.objects.get_or_create(
                    employee=employee,
                    date=date,
                    defaults={
                        'check_in_time': check_ins[0].timestamp.time() if check_ins else None,
                        'check_out_time': check_outs[-1].timestamp.time() if check_outs else None,
                        'total_hours': total_hours,
                        'status': self._determine_attendance_status(check_ins, check_outs, total_hours),
                        'machine': machine
                    }
                )
                
                if not created:
                    # Update existing summary
                    summary.check_in_time = check_ins[0].timestamp.time() if check_ins else summary.check_in_time
                    summary.check_out_time = check_outs[-1].timestamp.time() if check_outs else summary.check_out_time
                    summary.total_hours = total_hours
                    summary.status = self._determine_attendance_status(check_ins, check_outs, total_hours)
                    summary.save()
                
                logger.debug(f"{'Created' if created else 'Updated'} attendance summary for {employee} on {date}")
                
        except Exception as e:
            logger.error(f"Error generating daily summary for {date}: {str(e)}")
    
    def _calculate_work_hours(self, check_ins: List, check_outs: List) -> float:
        """Calculate total work hours from check-in/check-out records"""
        if not check_ins or not check_outs:
            return 0.0
        
        total_seconds = 0
        
        # Simple calculation: pair each check-in with the next check-out
        for i, check_in in enumerate(check_ins):
            if i < len(check_outs):
                check_out = check_outs[i]
                if check_out.timestamp > check_in.timestamp:
                    duration = check_out.timestamp - check_in.timestamp
                    total_seconds += duration.total_seconds()
        
        return round(total_seconds / 3600, 2)  # Convert to hours
    
    def _determine_attendance_status(self, check_ins: List, check_outs: List, 
                                   total_hours: float) -> str:
        """Determine attendance status based on records"""
        if not check_ins:
            return 'absent'
        
        if not check_outs:
            return 'incomplete'
        
        # This is a simplified logic - you might want to implement
        # more sophisticated rules based on work schedules
        if total_hours >= 8:
            return 'present'
        elif total_hours >= 4:
            return 'half_day'
        else:
            return 'incomplete'
    
    def validate_zk_records(self, zk_records: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """
        Validate ZK records before processing
        
        Returns:
            Tuple of (valid_records, error_messages)
        """
        valid_records = []
        errors = []
        
        for i, record in enumerate(zk_records):
            try:
                # Check required fields
                if not record.get('user_id'):
                    errors.append(f"Record {i+1}: Missing user_id")
                    continue
                
                if not record.get('timestamp'):
                    errors.append(f"Record {i+1}: Missing timestamp")
                    continue
                
                # Validate timestamp
                timestamp = record.get('timestamp')
                if not isinstance(timestamp, datetime):
                    errors.append(f"Record {i+1}: Invalid timestamp format")
                    continue
                
                # Check if timestamp is reasonable (not too old or in future)
                now = timezone.now()
                if timestamp > now:
                    errors.append(f"Record {i+1}: Timestamp is in the future")
                    continue
                
                if timestamp < now - timedelta(days=365):
                    errors.append(f"Record {i+1}: Timestamp is too old (>1 year)")
                    continue
                
                valid_records.append(record)
                
            except Exception as e:
                errors.append(f"Record {i+1}: Validation error - {str(e)}")
        
        return valid_records, errors
    
    def get_processing_statistics(self, machine: AttendanceMachine, 
                                date_from: Optional[datetime] = None,
                                date_to: Optional[datetime] = None) -> Dict:
        """Get processing statistics for a machine"""
        try:
            queryset = AttendanceRecord.objects.filter(machine=machine)
            
            if date_from:
                queryset = queryset.filter(timestamp__gte=date_from)
            if date_to:
                queryset = queryset.filter(timestamp__lte=date_to)
            
            total_records = queryset.count()
            unique_employees = queryset.values('employee').distinct().count()
            
            # Group by source
            machine_records = queryset.filter(source='machine').count()
            manual_records = queryset.filter(source='manual').count()
            
            return {
                'total_records': total_records,
                'unique_employees': unique_employees,
                'machine_records': machine_records,
                'manual_records': manual_records,
                'date_range': {
                    'from': date_from.isoformat() if date_from else None,
                    'to': date_to.isoformat() if date_to else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting processing statistics: {str(e)}")
            return {}
