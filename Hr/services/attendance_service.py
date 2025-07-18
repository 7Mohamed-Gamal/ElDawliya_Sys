# -*- coding: utf-8 -*-
"""
Attendance Service for HRMS
Handles attendance business logic and operations
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import logging

from Hr.models import (
    Employee, WorkShift, ShiftAssignment, AttendanceMachine, MachineUser,
    AttendanceRecord, AttendanceSummary
)

logger = logging.getLogger(__name__)


class AttendanceService:
    """
    خدمة إدارة الحضور - تحتوي على منطق العمل الخاص بالحضور والوقت
    """
    
    @staticmethod
    def record_attendance(employee_id, machine_id, record_type, timestamp=None, verification_method='fingerprint'):
        """
        تسجيل حضور الموظف
        """
        try:
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                machine = AttendanceMachine.objects.get(id=machine_id)
                
                if not timestamp:
                    timestamp = timezone.now()
                
                # التحقق من وجود المستخدم في الجهاز
                machine_user = MachineUser.objects.filter(
                    employee=employee,
                    machine=machine,
                    is_active=True
                ).first()
                
                if not machine_user:
                    raise ValidationError("الموظف غير مسجل في هذا الجهاز")
                
                # إنشاء سجل الحضور
                attendance_record = AttendanceRecord.objects.create(
                    employee=employee,
                    machine=machine,
                    record_type=record_type,
                    timestamp=timestamp,
                    verification_method=verification_method,
                    device_user_id=machine_user.user_id
                )
                
                # تحديث ملخص الحضور اليومي
                AttendanceService.update_daily_summary(employee, timestamp.date())
                
                logger.info(f"تم تسجيل حضور: {employee.full_name} - {record_type} في {timestamp}")
                return attendance_record
                
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except AttendanceMachine.DoesNotExist:
            raise ValidationError("جهاز الحضور غير موجود")
        except Exception as e:
            logger.error(f"خطأ في تسجيل الحضور: {str(e)}")
            raise
    
    @staticmethod
    def update_daily_summary(employee, date):
        """
        تحديث ملخص الحضور اليومي للموظف
        """
        try:
            # الحصول على الوردية المخصصة للموظف
            shift_assignment = ShiftAssignment.objects.filter(
                employee=employee,
                start_date__lte=date,
                is_active=True
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=date)
            ).first()
            
            shift = shift_assignment.shift if shift_assignment else None
            
            # إنشاء أو تحديث الملخص اليومي
            summary, created = AttendanceSummary.objects.get_or_create(
                employee=employee,
                date=date,
                defaults={'shift': shift}
            )
            
            # تحديث الوردية إذا تغيرت
            if summary.shift != shift:
                summary.shift = shift
            
            # حساب الملخص من السجلات
            summary.calculate_summary()
            summary.save()
            
            return summary
            
        except Exception as e:
            logger.error(f"خطأ في تحديث ملخص الحضور: {str(e)}")
            raise
    
    @staticmethod
    def calculate_working_hours(employee, start_date, end_date):
        """
        حساب ساعات العمل للموظف خلال فترة معينة
        """
        summaries = AttendanceSummary.objects.filter(
            employee=employee,
            date__range=[start_date, end_date]
        )
        
        total_hours = sum(float(summary.total_hours) for summary in summaries)
        regular_hours = sum(float(summary.regular_hours) for summary in summaries)
        overtime_hours = sum(float(summary.overtime_hours) for summary in summaries)
        
        return {
            'total_hours': total_hours,
            'regular_hours': regular_hours,
            'overtime_hours': overtime_hours,
            'working_days': summaries.filter(status='present').count(),
            'absent_days': summaries.filter(status='absent').count(),
            'late_days': summaries.filter(status='late').count()
        }
    
    @staticmethod
    def get_employee_attendance_summary(employee_id, month=None, year=None):
        """
        الحصول على ملخص حضور الموظف لشهر معين
        """
        if not month:
            month = date.today().month
        if not year:
            year = date.today().year
        
        summaries = AttendanceSummary.objects.filter(
            employee_id=employee_id,
            date__year=year,
            date__month=month
        ).order_by('date')
        
        # حساب الإحصائيات
        total_days = summaries.count()
        present_days = summaries.filter(status='present').count()
        absent_days = summaries.filter(status='absent').count()
        late_days = summaries.filter(status='late').count()
        
        total_hours = sum(float(s.total_hours) for s in summaries)
        overtime_hours = sum(float(s.overtime_hours) for s in summaries)
        total_late_minutes = sum(s.late_minutes for s in summaries)
        
        return {
            'summaries': summaries,
            'statistics': {
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'late_days': late_days,
                'attendance_rate': round((present_days / total_days * 100), 2) if total_days > 0 else 0,
                'total_hours': total_hours,
                'overtime_hours': overtime_hours,
                'total_late_minutes': total_late_minutes,
                'average_daily_hours': round(total_hours / present_days, 2) if present_days > 0 else 0
            }
        }
    
    @staticmethod
    def get_department_attendance_report(department_id, start_date, end_date):
        """
        تقرير حضور القسم
        """
        employees = Employee.objects.filter(
            department_id=department_id,
            is_active=True
        )
        
        report_data = []
        
        for employee in employees:
            summary = AttendanceService.calculate_working_hours(
                employee, start_date, end_date
            )
            summary['employee'] = employee
            report_data.append(summary)
        
        # حساب إجماليات القسم
        total_employees = len(report_data)
        total_working_hours = sum(emp['total_hours'] for emp in report_data)
        total_overtime_hours = sum(emp['overtime_hours'] for emp in report_data)
        average_attendance_rate = sum(
            (emp['working_days'] / ((end_date - start_date).days + 1)) * 100 
            for emp in report_data
        ) / total_employees if total_employees > 0 else 0
        
        return {
            'employees': report_data,
            'department_summary': {
                'total_employees': total_employees,
                'total_working_hours': total_working_hours,
                'total_overtime_hours': total_overtime_hours,
                'average_attendance_rate': round(average_attendance_rate, 2)
            }
        }
    
    @staticmethod
    def sync_attendance_machine(machine_id):
        """
        مزامنة بيانات الحضور من الجهاز
        """
        try:
            machine = AttendanceMachine.objects.get(id=machine_id)
            
            if not machine.is_online:
                raise ValidationError("الجهاز غير متصل")
            
            # هنا سيتم تنفيذ منطق المزامنة مع الجهاز
            # يمكن استخدام مكتبة مثل pyzk للاتصال بأجهزة ZKTeco
            
            # تحديث وقت آخر مزامنة
            machine.mark_sync_completed()
            
            logger.info(f"تم مزامنة جهاز الحضور: {machine.name}")
            return True
            
        except AttendanceMachine.DoesNotExist:
            raise ValidationError("جهاز الحضور غير موجود")
        except Exception as e:
            logger.error(f"خطأ في مزامنة الجهاز: {str(e)}")
            raise
    
    @staticmethod
    def enroll_employee_to_machine(employee_id, machine_id, user_id=None):
        """
        تسجيل موظف في جهاز الحضور
        """
        try:
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                machine = AttendanceMachine.objects.get(id=machine_id)
                
                # إنشاء أو تحديث مستخدم الجهاز
                machine_user, created = MachineUser.objects.get_or_create(
                    employee=employee,
                    machine=machine,
                    defaults={
                        'user_id': user_id or employee.employee_number,
                        'is_active': True
                    }
                )
                
                if not created:
                    machine_user.user_id = user_id or employee.employee_number
                    machine_user.is_active = True
                    machine_user.save()
                
                # تسجيل المستخدم في الجهاز
                success = machine_user.enroll_user()
                
                if success:
                    logger.info(f"تم تسجيل الموظف {employee.full_name} في جهاز {machine.name}")
                else:
                    raise ValidationError("فشل في تسجيل الموظف في الجهاز")
                
                return machine_user
                
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except AttendanceMachine.DoesNotExist:
            raise ValidationError("جهاز الحضور غير موجود")
        except Exception as e:
            logger.error(f"خطأ في تسجيل الموظف في الجهاز: {str(e)}")
            raise
    
    @staticmethod
    def create_manual_attendance(employee_id, record_type, timestamp, created_by, notes=""):
        """
        إنشاء سجل حضور يدوي
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            
            attendance_record = AttendanceRecord.create_manual_record(
                employee=employee,
                record_type=record_type,
                timestamp=timestamp,
                created_by=created_by,
                notes=notes
            )
            
            # تحديث ملخص الحضور اليومي
            AttendanceService.update_daily_summary(employee, timestamp.date())
            
            logger.info(f"تم إنشاء سجل حضور يدوي: {employee.full_name} - {record_type}")
            return attendance_record
            
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"خطأ في إنشاء سجل الحضور اليدوي: {str(e)}")
            raise
    
    @staticmethod
    def get_late_employees_today():
        """
        الحصول على الموظفين المتأخرين اليوم
        """
        today = date.today()
        
        late_summaries = AttendanceSummary.objects.filter(
            date=today,
            status='late',
            late_minutes__gt=0
        ).select_related('employee', 'shift').order_by('-late_minutes')
        
        return late_summaries
    
    @staticmethod
    def get_absent_employees_today():
        """
        الحصول على الموظفين الغائبين اليوم
        """
        today = date.today()
        
        absent_summaries = AttendanceSummary.objects.filter(
            date=today,
            status='absent'
        ).select_related('employee')
        
        return absent_summaries
    
    @staticmethod
    def get_attendance_statistics(start_date=None, end_date=None):
        """
        الحصول على إحصائيات الحضور
        """
        if not start_date:
            start_date = date.today().replace(day=1)  # بداية الشهر الحالي
        if not end_date:
            end_date = date.today()
        
        summaries = AttendanceSummary.objects.filter(
            date__range=[start_date, end_date]
        )
        
        total_records = summaries.count()
        
        stats = {
            'total_records': total_records,
            'present_count': summaries.filter(status='present').count(),
            'absent_count': summaries.filter(status='absent').count(),
            'late_count': summaries.filter(status='late').count(),
            'half_day_count': summaries.filter(status='half_day').count(),
            'total_working_hours': sum(float(s.total_hours) for s in summaries),
            'total_overtime_hours': sum(float(s.overtime_hours) for s in summaries),
            'average_daily_hours': 0,
            'attendance_rate': 0
        }
        
        if total_records > 0:
            stats['attendance_rate'] = round(
                (stats['present_count'] / total_records) * 100, 2
            )
            
            present_summaries = summaries.filter(status__in=['present', 'late'])
            if present_summaries.exists():
                stats['average_daily_hours'] = round(
                    sum(float(s.total_hours) for s in present_summaries) / present_summaries.count(), 2
                )
        
        return stats
    
    @staticmethod
    def generate_attendance_summaries_for_period(start_date, end_date):
        """
        إنشاء ملخصات الحضور لفترة معينة لجميع الموظفين النشطين
        """
        employees = Employee.objects.filter(is_active=True)
        generated_count = 0
        
        for employee in employees:
            current_date = start_date
            while current_date <= end_date:
                try:
                    AttendanceService.update_daily_summary(employee, current_date)
                    generated_count += 1
                except Exception as e:
                    logger.error(f"خطأ في إنشاء ملخص الحضور للموظف {employee.full_name} في {current_date}: {str(e)}")
                
                current_date += timedelta(days=1)
        
        logger.info(f"تم إنشاء {generated_count} ملخص حضور للفترة من {start_date} إلى {end_date}")
        return generated_count