"""
Attendance Service - خدمات إدارة الحضور المتقدمة
"""

from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Count, Sum, Avg, F, Case, When
from decimal import Decimal
from datetime import date, datetime, timedelta, time
import logging
import json
import hashlib
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger('hr_system')


class AttendanceService:
    """خدمات إدارة الحضور الشاملة"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    # =============================================================================
    # ATTENDANCE RECORDING METHODS
    # =============================================================================
    
    def record_attendance(self, employee_id: str, attendance_type: str, 
                         machine_id: str = None, location_data: Dict = None,
                         verification_data: Dict = None) -> Dict:
        """تسجيل الحضور أو الانصراف"""
        try:
            from ..models import Employee, AttendanceRecordEnhanced, AttendanceMachineEnhanced
            
            with transaction.atomic():
                employee = Employee.objects.select_related('company', 'branch').get(id=employee_id)
                
                # Get or create machine record
                machine = None
                if machine_id:
                    try:
                        machine = AttendanceMachineEnhanced.objects.get(id=machine_id)
                    except AttendanceMachineEnhanced.DoesNotExist:
                        # Create default machine if not found
                        machine = self._create_default_machine(employee.branch)
                
                # Get current shift
                current_shift = self._get_employee_current_shift(employee)
                
                # Create attendance record
                now = timezone.now()
                attendance_record = AttendanceRecordEnhanced.objects.create(
                    employee=employee,
                    machine=machine,
                    shift=current_shift,
                    date=now.date(),
                    timestamp=now,
                    attendance_type=attendance_type,
                    verification_method=verification_data.get('method', 'manual') if verification_data else 'manual',
                    verification_score=verification_data.get('score') if verification_data else None,
                    latitude=location_data.get('latitude') if location_data else None,
                    longitude=location_data.get('longitude') if location_data else None,
                    location_accuracy=location_data.get('accuracy') if location_data else None,
                    scheduled_time=self._get_scheduled_time(current_shift, attendance_type),
                    raw_data=json.dumps({
                        'location': location_data,
                        'verification': verification_data,
                        'timestamp': now.isoformat()
                    })
                )
                
                # Calculate time difference and status
                attendance_record.calculate_time_difference()
                attendance_record.save()
                
                # Update daily summary
                self._update_attendance_summary(employee, now.date())
                
                # Clear cache
                self._clear_attendance_cache(employee_id)
                
                logger.info(f"Recorded {attendance_type} for employee {employee.employee_number}")
                
                return {
                    'success': True,
                    'record_id': attendance_record.id,
                    'timestamp': attendance_record.timestamp,
                    'status': attendance_record.status,
                    'time_difference': attendance_record.time_difference,
                    'message': self._get_attendance_message(attendance_record)
                }
                
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"Error recording attendance for employee {employee_id}: {e}")
            raise ValidationError(f"خطأ في تسجيل الحضور: {e}")
    
    def bulk_import_attendance(self, attendance_data: List[Dict], machine_id: str = None) -> Dict:
        """استيراد مجمع لسجلات الحضور"""
        try:
            from ..models import Employee, AttendanceRecordEnhanced, AttendanceMachineEnhanced
            
            results = {
                'success_count': 0,
                'error_count': 0,
                'errors': [],
                'duplicates': 0
            }
            
            machine = None
            if machine_id:
                try:
                    machine = AttendanceMachineEnhanced.objects.get(id=machine_id)
                except AttendanceMachineEnhanced.DoesNotExist:
                    pass
            
            with transaction.atomic():
                for record_data in attendance_data:
                    try:
                        # Validate required fields
                        required_fields = ['employee_number', 'timestamp', 'attendance_type']
                        for field in required_fields:
                            if field not in record_data:
                                raise ValidationError(f"الحقل {field} مطلوب")
                        
                        # Get employee
                        employee = Employee.objects.get(
                            employee_number=record_data['employee_number']
                        )
                        
                        # Parse timestamp
                        if isinstance(record_data['timestamp'], str):
                            timestamp = datetime.fromisoformat(record_data['timestamp'])
                        else:
                            timestamp = record_data['timestamp']
                        
                        # Check for duplicates
                        existing = AttendanceRecordEnhanced.objects.filter(
                            employee=employee,
                            timestamp=timestamp,
                            attendance_type=record_data['attendance_type']
                        ).exists()
                        
                        if existing:
                            results['duplicates'] += 1
                            continue
                        
                        # Create record
                        AttendanceRecordEnhanced.objects.create(
                            employee=employee,
                            machine=machine,
                            date=timestamp.date(),
                            timestamp=timestamp,
                            attendance_type=record_data['attendance_type'],
                            verification_method=record_data.get('verification_method', 'imported'),
                            device_user_id=record_data.get('device_user_id'),
                            raw_data=json.dumps(record_data)
                        )
                        
                        results['success_count'] += 1
                        
                    except Employee.DoesNotExist:
                        results['error_count'] += 1
                        results['errors'].append(f"الموظف {record_data.get('employee_number')} غير موجود")
                    except Exception as e:
                        results['error_count'] += 1
                        results['errors'].append(f"خطأ في السجل {record_data}: {e}")
            
            logger.info(f"Bulk import completed: {results['success_count']} success, {results['error_count']} errors")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk attendance import: {e}")
            raise ValidationError(f"خطأ في الاستيراد المجمع: {e}")
    
    # =============================================================================
    # ATTENDANCE ANALYSIS METHODS
    # =============================================================================
    
    def get_employee_attendance_summary(self, employee_id: str, start_date: date, 
                                      end_date: date) -> Dict:
        """ملخص حضور الموظف لفترة محددة"""
        try:
            from ..models import Employee, AttendanceSummary, AttendanceRecordEnhanced
            
            cache_key = f"attendance_summary_{employee_id}_{start_date}_{end_date}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            employee = Employee.objects.get(id=employee_id)
            
            # Get attendance summaries
            summaries = AttendanceSummary.objects.filter(
                employee=employee,
                date__range=[start_date, end_date]
            ).order_by('date')
            
            # Calculate statistics
            total_days = (end_date - start_date).days + 1
            present_days = summaries.filter(is_present=True).count()
            absent_days = summaries.filter(is_absent=True).count()
            late_days = summaries.filter(is_late=True).count()
            early_leave_days = summaries.filter(is_early_leave=True).count()
            
            # Calculate work hours
            total_work_hours = summaries.aggregate(
                total=Sum('total_work_hours')
            )['total'] or Decimal('0')
            
            total_overtime_hours = summaries.aggregate(
                total=Sum('overtime_hours')
            )['total'] or Decimal('0')
            
            # Calculate averages
            avg_work_hours = total_work_hours / present_days if present_days > 0 else Decimal('0')
            attendance_rate = (present_days / total_days) * 100 if total_days > 0 else 0
            
            # Get detailed records for analysis
            records = AttendanceRecordEnhanced.objects.filter(
                employee=employee,
                date__range=[start_date, end_date]
            ).order_by('date', 'timestamp')
            
            # Analyze patterns
            patterns = self._analyze_attendance_patterns(records)
            
            result = {
                'employee': {
                    'id': employee.id,
                    'name': employee.full_name,
                    'employee_number': employee.employee_number
                },
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_days': total_days
                },
                'statistics': {
                    'present_days': present_days,
                    'absent_days': absent_days,
                    'late_days': late_days,
                    'early_leave_days': early_leave_days,
                    'attendance_rate': round(attendance_rate, 2),
                    'total_work_hours': float(total_work_hours),
                    'total_overtime_hours': float(total_overtime_hours),
                    'avg_work_hours': float(avg_work_hours)
                },
                'patterns': patterns,
                'daily_summaries': list(summaries.values()),
                'generated_at': timezone.now()
            }
            
            # Cache for 1 hour
            cache.set(cache_key, result, 3600)
            
            return result
            
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"Error getting attendance summary for {employee_id}: {e}")
            raise ValidationError(f"خطأ في جلب ملخص الحضور: {e}")
    
    def get_department_attendance_report(self, department_id: str, date_filter: date) -> Dict:
        """تقرير حضور القسم ليوم محدد"""
        try:
            from ..models import Department, Employee, AttendanceSummary
            
            department = Department.objects.get(id=department_id)
            employees = Employee.objects.filter(department=department, is_active=True)
            
            # Get attendance summaries for the date
            summaries = AttendanceSummary.objects.filter(
                employee__in=employees,
                date=date_filter
            ).select_related('employee')
            
            # Create summary dict for quick lookup
            summary_dict = {s.employee_id: s for s in summaries}
            
            # Prepare employee data
            employee_data = []
            for employee in employees:
                summary = summary_dict.get(employee.id)
                
                employee_data.append({
                    'employee_id': employee.id,
                    'employee_number': employee.employee_number,
                    'name': employee.full_name,
                    'position': employee.job_position.title,
                    'status': summary.attendance_status if summary else 'غير محدد',
                    'check_in_time': summary.check_in_time if summary else None,
                    'check_out_time': summary.check_out_time if summary else None,
                    'work_hours': float(summary.total_work_hours) if summary else 0,
                    'is_present': summary.is_present if summary else False,
                    'is_late': summary.is_late if summary else False,
                    'late_minutes': summary.late_minutes if summary else 0
                })
            
            # Calculate department statistics
            total_employees = len(employee_data)
            present_count = sum(1 for emp in employee_data if emp['is_present'])
            absent_count = total_employees - present_count
            late_count = sum(1 for emp in employee_data if emp['is_late'])
            
            return {
                'department': {
                    'id': department.id,
                    'name': department.name
                },
                'date': date_filter,
                'statistics': {
                    'total_employees': total_employees,
                    'present_count': present_count,
                    'absent_count': absent_count,
                    'late_count': late_count,
                    'attendance_rate': round((present_count / total_employees) * 100, 2) if total_employees > 0 else 0
                },
                'employees': employee_data,
                'generated_at': timezone.now()
            }
            
        except Department.DoesNotExist:
            raise ValidationError("القسم غير موجود")
        except Exception as e:
            logger.error(f"Error getting department attendance report: {e}")
            raise ValidationError(f"خطأ في جلب تقرير حضور القسم: {e}")
    
    def detect_attendance_anomalies(self, employee_id: str = None, 
                                  date_range: Tuple[date, date] = None) -> List[Dict]:
        """كشف الشذوذ في أنماط الحضور"""
        try:
            from ..models import Employee, AttendanceRecordEnhanced
            
            if date_range:
                start_date, end_date = date_range
            else:
                # Default to last 30 days
                end_date = date.today()
                start_date = end_date - timedelta(days=30)
            
            # Build query
            query = Q(date__range=[start_date, end_date])
            if employee_id:
                query &= Q(employee_id=employee_id)
            
            records = AttendanceRecordEnhanced.objects.filter(query).select_related('employee')
            
            anomalies = []
            
            # Group records by employee
            employee_records = {}
            for record in records:
                emp_id = record.employee_id
                if emp_id not in employee_records:
                    employee_records[emp_id] = []
                employee_records[emp_id].append(record)
            
            for emp_id, emp_records in employee_records.items():
                employee = emp_records[0].employee
                
                # Detect various anomalies
                emp_anomalies = []
                
                # 1. Multiple check-ins without check-out
                check_ins = [r for r in emp_records if r.attendance_type == 'check_in']
                check_outs = [r for r in emp_records if r.attendance_type == 'check_out']
                
                if len(check_ins) > len(check_outs) + 1:  # Allow for current day
                    emp_anomalies.append({
                        'type': 'missing_checkout',
                        'description': 'دخول متعدد بدون خروج',
                        'severity': 'medium',
                        'count': len(check_ins) - len(check_outs)
                    })
                
                # 2. Very long work hours (>12 hours)
                daily_records = {}
                for record in emp_records:
                    date_key = record.date
                    if date_key not in daily_records:
                        daily_records[date_key] = []
                    daily_records[date_key].append(record)
                
                for date_key, day_records in daily_records.items():
                    day_check_ins = [r for r in day_records if r.attendance_type == 'check_in']
                    day_check_outs = [r for r in day_records if r.attendance_type == 'check_out']
                    
                    if day_check_ins and day_check_outs:
                        first_in = min(day_check_ins, key=lambda x: x.timestamp)
                        last_out = max(day_check_outs, key=lambda x: x.timestamp)
                        
                        work_duration = last_out.timestamp - first_in.timestamp
                        if work_duration.total_seconds() > 12 * 3600:  # 12 hours
                            emp_anomalies.append({
                                'type': 'excessive_hours',
                                'description': f'ساعات عمل مفرطة في {date_key}',
                                'severity': 'high',
                                'duration_hours': round(work_duration.total_seconds() / 3600, 2),
                                'date': date_key
                            })
                
                # 3. Weekend attendance (if not scheduled)
                weekend_records = [r for r in emp_records if r.date.weekday() in [4, 5]]  # Friday, Saturday
                if weekend_records:
                    emp_anomalies.append({
                        'type': 'weekend_attendance',
                        'description': 'حضور في عطلة نهاية الأسبوع',
                        'severity': 'low',
                        'count': len(weekend_records)
                    })
                
                # 4. Unusual timing patterns
                unusual_times = []
                for record in emp_records:
                    hour = record.timestamp.hour
                    if record.attendance_type == 'check_in' and (hour < 6 or hour > 10):
                        unusual_times.append(record)
                    elif record.attendance_type == 'check_out' and (hour < 14 or hour > 22):
                        unusual_times.append(record)
                
                if unusual_times:
                    emp_anomalies.append({
                        'type': 'unusual_timing',
                        'description': 'أوقات حضور غير اعتيادية',
                        'severity': 'medium',
                        'count': len(unusual_times)
                    })
                
                if emp_anomalies:
                    anomalies.append({
                        'employee': {
                            'id': employee.id,
                            'name': employee.full_name,
                            'employee_number': employee.employee_number
                        },
                        'anomalies': emp_anomalies,
                        'total_anomalies': len(emp_anomalies)
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting attendance anomalies: {e}")
            raise ValidationError(f"خطأ في كشف شذوذ الحضور: {e}")
    
    # =============================================================================
    # SHIFT MANAGEMENT METHODS
    # =============================================================================
    
    def assign_employee_to_shift(self, employee_id: str, shift_id: str, 
                               start_date: date, end_date: date = None) -> Dict:
        """تعيين موظف لوردية"""
        try:
            from ..models import Employee, WorkShiftEnhanced, EmployeeShiftAssignment
            
            employee = Employee.objects.get(id=employee_id)
            shift = WorkShiftEnhanced.objects.get(id=shift_id)
            
            # Check for overlapping assignments
            overlapping = EmployeeShiftAssignment.objects.filter(
                employee=employee,
                start_date__lte=end_date or date.max,
                end_date__gte=start_date,
                is_active=True
            ).exists()
            
            if overlapping:
                raise ValidationError("يوجد تعيين وردية متداخل للموظف في هذه الفترة")
            
            # Create assignment
            assignment = EmployeeShiftAssignment.objects.create(
                employee=employee,
                shift=shift,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            
            logger.info(f"Assigned employee {employee.employee_number} to shift {shift.name}")
            
            return {
                'success': True,
                'assignment_id': assignment.id,
                'message': f'تم تعيين الموظف {employee.full_name} للوردية {shift.name}'
            }
            
        except (Employee.DoesNotExist, WorkShiftEnhanced.DoesNotExist):
            raise ValidationError("الموظف أو الوردية غير موجودة")
        except Exception as e:
            logger.error(f"Error assigning employee to shift: {e}")
            raise ValidationError(f"خطأ في تعيين الوردية: {e}")
    
    def get_shift_schedule(self, shift_id: str, start_date: date, end_date: date) -> Dict:
        """جدول الوردية لفترة محددة"""
        try:
            from ..models import WorkShiftEnhanced, EmployeeShiftAssignment
            
            shift = WorkShiftEnhanced.objects.get(id=shift_id)
            
            # Get employees assigned to this shift
            assignments = EmployeeShiftAssignment.objects.filter(
                shift=shift,
                start_date__lte=end_date,
                end_date__gte=start_date,
                is_active=True
            ).select_related('employee')
            
            # Generate schedule
            schedule = []
            current_date = start_date
            
            while current_date <= end_date:
                # Check if it's a working day for this shift
                is_working_day = shift.is_working_day(current_date)
                
                # Get employees scheduled for this date
                scheduled_employees = []
                for assignment in assignments:
                    if (assignment.start_date <= current_date and 
                        (assignment.end_date is None or assignment.end_date >= current_date)):
                        scheduled_employees.append({
                            'employee_id': assignment.employee.id,
                            'employee_number': assignment.employee.employee_number,
                            'name': assignment.employee.full_name,
                            'department': assignment.employee.department.name
                        })
                
                schedule.append({
                    'date': current_date,
                    'is_working_day': is_working_day,
                    'start_time': shift.start_time if is_working_day else None,
                    'end_time': shift.end_time if is_working_day else None,
                    'scheduled_employees': scheduled_employees,
                    'employee_count': len(scheduled_employees)
                })
                
                current_date += timedelta(days=1)
            
            return {
                'shift': {
                    'id': shift.id,
                    'name': shift.name,
                    'type': shift.shift_type
                },
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'schedule': schedule,
                'total_days': len(schedule),
                'working_days': sum(1 for day in schedule if day['is_working_day'])
            }
            
        except WorkShiftEnhanced.DoesNotExist:
            raise ValidationError("الوردية غير موجودة")
        except Exception as e:
            logger.error(f"Error getting shift schedule: {e}")
            raise ValidationError(f"خطأ في جلب جدول الوردية: {e}")
    
    # =============================================================================
    # MACHINE MANAGEMENT METHODS
    # =============================================================================
    
    def sync_attendance_machine(self, machine_id: str) -> Dict:
        """مزامنة جهاز الحضور"""
        try:
            from ..models import AttendanceMachineEnhanced
            
            machine = AttendanceMachineEnhanced.objects.get(id=machine_id)
            
            # Test connection
            if machine.ping():
                # Perform sync operations
                sync_result = self._perform_machine_sync(machine)
                
                # Update machine status
                machine.last_sync = timezone.now()
                machine.status = 'online'
                machine.save()
                
                logger.info(f"Successfully synced machine {machine.name}")
                
                return {
                    'success': True,
                    'machine_name': machine.name,
                    'sync_time': machine.last_sync,
                    'records_synced': sync_result.get('records_count', 0),
                    'message': 'تمت المزامنة بنجاح'
                }
            else:
                machine.status = 'offline'
                machine.save()
                
                return {
                    'success': False,
                    'message': 'فشل في الاتصال بالجهاز'
                }
                
        except AttendanceMachineEnhanced.DoesNotExist:
            raise ValidationError("جهاز الحضور غير موجود")
        except Exception as e:
            logger.error(f"Error syncing attendance machine {machine_id}: {e}")
            raise ValidationError(f"خطأ في مزامنة الجهاز: {e}")
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _get_employee_current_shift(self, employee):
        """الحصول على الوردية الحالية للموظف"""
        try:
            from ..models import EmployeeShiftAssignment
            
            today = date.today()
            assignment = EmployeeShiftAssignment.objects.filter(
                employee=employee,
                start_date__lte=today,
                end_date__gte=today,
                is_active=True
            ).select_related('shift').first()
            
            return assignment.shift if assignment else None
            
        except Exception:
            return None
    
    def _get_scheduled_time(self, shift, attendance_type):
        """الحصول على الوقت المجدول"""
        if not shift:
            return None
        
        if attendance_type == 'check_in':
            return shift.start_time
        elif attendance_type == 'check_out':
            return shift.end_time
        else:
            return None
    
    def _create_default_machine(self, branch):
        """إنشاء جهاز افتراضي"""
        from ..models import AttendanceMachineEnhanced
        
        return AttendanceMachineEnhanced.objects.create(
            company=branch.company,
            branch=branch,
            name=f"جهاز افتراضي - {branch.name}",
            serial_number=f"DEFAULT-{branch.id}",
            machine_type='manual',
            connection_type='manual',
            location=branch.address or 'غير محدد',
            status='online'
        )
    
    def _update_attendance_summary(self, employee, date_obj):
        """تحديث ملخص الحضور اليومي"""
        try:
            from ..models import AttendanceSummary, AttendanceRecordEnhanced
            
            # Get or create summary
            summary, created = AttendanceSummary.objects.get_or_create(
                employee=employee,
                date=date_obj,
                defaults={'is_present': False, 'is_absent': True}
            )
            
            # Get all records for this date
            records = AttendanceRecordEnhanced.objects.filter(
                employee=employee,
                date=date_obj
            ).order_by('timestamp')
            
            if records.exists():
                # Find check-in and check-out times
                check_ins = records.filter(attendance_type='check_in')
                check_outs = records.filter(attendance_type='check_out')
                
                if check_ins.exists():
                    summary.check_in_time = check_ins.first().actual_time
                    summary.is_present = True
                    summary.is_absent = False
                    
                    # Check if late
                    first_checkin = check_ins.first()
                    if first_checkin.status == 'late':
                        summary.is_late = True
                        summary.late_minutes = first_checkin.time_difference
                
                if check_outs.exists():
                    summary.check_out_time = check_outs.last().actual_time
                    
                    # Check for early leave
                    last_checkout = check_outs.last()
                    if last_checkout.status == 'early':
                        summary.is_early_leave = True
                        summary.early_leave_minutes = abs(last_checkout.time_difference)
                
                # Calculate work hours
                summary.calculate_work_hours()
                
            summary.save()
            
        except Exception as e:
            logger.error(f"Error updating attendance summary: {e}")
    
    def _analyze_attendance_patterns(self, records):
        """تحليل أنماط الحضور"""
        patterns = {
            'most_common_checkin_hour': None,
            'most_common_checkout_hour': None,
            'average_work_hours': 0,
            'late_frequency': 0,
            'early_leave_frequency': 0
        }
        
        if not records:
            return patterns
        
        # Analyze check-in times
        checkin_hours = []
        checkout_hours = []
        work_durations = []
        late_count = 0
        early_leave_count = 0
        
        daily_records = {}
        for record in records:
            date_key = record.date
            if date_key not in daily_records:
                daily_records[date_key] = {'checkin': None, 'checkout': None}
            
            if record.attendance_type == 'check_in':
                daily_records[date_key]['checkin'] = record
                checkin_hours.append(record.timestamp.hour)
                if record.status == 'late':
                    late_count += 1
            elif record.attendance_type == 'check_out':
                daily_records[date_key]['checkout'] = record
                checkout_hours.append(record.timestamp.hour)
                if record.status == 'early':
                    early_leave_count += 1
        
        # Calculate work durations
        for date_key, day_data in daily_records.items():
            if day_data['checkin'] and day_data['checkout']:
                duration = day_data['checkout'].timestamp - day_data['checkin'].timestamp
                work_durations.append(duration.total_seconds() / 3600)  # Convert to hours
        
        # Calculate patterns
        if checkin_hours:
            patterns['most_common_checkin_hour'] = max(set(checkin_hours), key=checkin_hours.count)
        
        if checkout_hours:
            patterns['most_common_checkout_hour'] = max(set(checkout_hours), key=checkout_hours.count)
        
        if work_durations:
            patterns['average_work_hours'] = round(sum(work_durations) / len(work_durations), 2)
        
        total_days = len(daily_records)
        if total_days > 0:
            patterns['late_frequency'] = round((late_count / total_days) * 100, 2)
            patterns['early_leave_frequency'] = round((early_leave_count / total_days) * 100, 2)
        
        return patterns
    
    def _perform_machine_sync(self, machine):
        """تنفيذ مزامنة الجهاز"""
        # This would contain the actual machine sync logic
        # For now, return a mock result
        return {
            'records_count': 0,
            'success': True
        }
    
    def _clear_attendance_cache(self, employee_id):
        """مسح الكاش المتعلق بالحضور"""
        # Clear relevant cache keys
        cache_patterns = [
            f"attendance_summary_{employee_id}_*",
            f"employee_attendance_{employee_id}_*"
        ]
        
        # In a real implementation, you'd iterate through cache keys
        # and delete matching patterns
        pass
    
    def _get_attendance_message(self, record):
        """الحصول على رسالة الحضور"""
        if record.status == 'on_time':
            return "تم تسجيل الحضور في الوقت المحدد"
        elif record.status == 'late':
            return f"تم تسجيل الحضور مع تأخير {record.time_difference} دقيقة"
        elif record.status == 'early':
            return f"تم تسجيل الحضور مبكراً بـ {abs(record.time_difference)} دقيقة"
        else:
            return "تم تسجيل الحضور"