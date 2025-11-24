"""
خدمة الحضور والانصراف المتقدمة
Advanced Attendance Management Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import date, datetime, timedelta
from core.services.base import BaseService
from core.models.attendance import EmployeeAttendance, AttendanceRule, OvertimeRecord, AttendanceDevice


class AttendanceService(BaseService):
    """
    خدمة الحضور والانصراف المتقدمة
    Advanced attendance management with device integration
    """

    def record_attendance(self, employee_id, att_date=None, check_in_time=None,
                         check_out_time=None, device_id=None, manual_entry=False):
        """
        تسجيل حضور الموظف
        Record employee attendance
        """
        self.check_permission('attendance.add_employeeattendance')

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)
            att_date = att_date or timezone.now().date()

            # Check if attendance already exists for this date
            existing_attendance = EmployeeAttendance.objects.filter(
                employee=employee,
                att_date=att_date
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            if existing_attendance and not manual_entry:
                # Update existing record
                if check_in_time and not existing_attendance.check_in_time:
                    existing_attendance.check_in_time = check_in_time
                elif check_out_time and not existing_attendance.check_out_time:
                    existing_attendance.check_out_time = check_out_time

                existing_attendance.device_id = device_id
                existing_attendance.updated_by = self.user
                existing_attendance.save()

                # Recalculate attendance status
                self._calculate_attendance_status(existing_attendance)

                return self.format_response(
                    data={'attendance_id': existing_attendance.id},
                    message='تم تحديث سجل الحضور'
                )

            # Create new attendance record
            attendance_data = {
                'employee': employee,
                'att_date': att_date,
                'check_in_time': check_in_time,
                'check_out_time': check_out_time,
                'device_id': device_id,
                'is_manual_entry': manual_entry,
                'created_by': self.user,
                'updated_by': self.user
            }

            attendance = EmployeeAttendance.objects.create(**attendance_data)

            # Calculate attendance status and working hours
            self._calculate_attendance_status(attendance)

            # Log the action
            self.log_action(
                action='create',
                resource='attendance',
                content_object=attendance,
                new_values=attendance_data,
                message=f'تم تسجيل حضور الموظف: {employee.get_full_name()}'
            )

            return self.format_response(
                data={'attendance_id': attendance.id},
                message='تم تسجيل الحضور بنجاح'
            )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'record_attendance', 'attendance', {
                'employee_id': employee_id,
                'att_date': att_date
            })

    def get_employee_attendance(self, employee_id, start_date=None, end_date=None,
                              page=1, page_size=20):
        """
        الحصول على سجل حضور الموظف
        Get employee attendance records
        """
        self.check_permission('attendance.view_employeeattendance')

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)

            # Check object-level permission
            self.check_object_permission('attendance.view_employeeattendance', employee)

            queryset = EmployeeAttendance.objects.filter(employee=employee).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            # Apply date filters
            if start_date:
                queryset = queryset.filter(att_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(att_date__lte=end_date)

            queryset = queryset.order_by('-att_date')

            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)

            # Format attendance data
            attendance_records = []
            for record in paginated_data['results']:
                attendance_records.append({
                    'id': record.id,
                    'att_date': record.att_date,
                    'check_in_time': record.check_in_time,
                    'check_out_time': record.check_out_time,
                    'working_hours': record.working_hours,
                    'overtime_hours': record.overtime_hours,
                    'status': record.status,
                    'late_minutes': record.late_minutes,
                    'early_departure_minutes': record.early_departure_minutes,
                    'is_manual_entry': record.is_manual_entry,
                    'notes': record.notes,
                })

            paginated_data['results'] = attendance_records

            return self.format_response(
                data=paginated_data,
                message='تم الحصول على سجل الحضور بنجاح'
            )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_employee_attendance', f'attendance/{employee_id}')

    def calculate_monthly_summary(self, employee_id, year, month):
        """
        حساب ملخص الحضور الشهري
        Calculate monthly attendance summary
        """
        self.check_permission('attendance.view_employeeattendance')

        try:
            from core.models.hr import Employee
            from calendar import monthrange

            employee = Employee.objects.get(id=employee_id)

            # Get month date range
            start_date = date(year, month, 1)
            end_date = date(year, month, monthrange(year, month)[1])

            # Get attendance records for the month
            attendance_records = EmployeeAttendance.objects.filter(
                employee=employee,
                att_date__range=[start_date, end_date]
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            # Calculate summary statistics
            summary = attendance_records.aggregate(
                total_days=Count('id'),
                present_days=Count('id', filter=Q(status='present')),
                absent_days=Count('id', filter=Q(status='absent')),
                late_days=Count('id', filter=Q(status='late')),
                total_working_hours=Sum('working_hours'),
                total_overtime_hours=Sum('overtime_hours'),
                avg_working_hours=Avg('working_hours'),
                total_late_minutes=Sum('late_minutes'),
            )

            # Calculate working days in month (excluding weekends)
            working_days = self._count_working_days(start_date, end_date)

            # Calculate attendance percentage
            attendance_percentage = (
                (summary['present_days'] or 0) / working_days * 100
            ) if working_days > 0 else 0

            summary.update({
                'working_days_in_month': working_days,
                'attendance_percentage': round(attendance_percentage, 2),
                'year': year,
                'month': month,
                'employee_name': employee.get_full_name(),
            })

            return self.format_response(
                data=summary,
                message='تم حساب ملخص الحضور الشهري بنجاح'
            )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'calculate_monthly_summary', f'attendance_summary/{employee_id}')

    def get_department_attendance_report(self, department_id, report_date=None):
        """
        تقرير حضور القسم
        Department attendance report
        """
        self.check_permission('attendance.view_employeeattendance')

        try:
            from core.models.hr import Department, Employee

            department = Department.objects.get(id=department_id)
            report_date = report_date or timezone.now().date()

            # Get department employees
            employees = Employee.objects.filter(
                department=department,
                is_active=True
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('job_position')

            # Get attendance records for the date
            attendance_records = EmployeeAttendance.objects.filter(
                employee__department=department,
                att_date=report_date
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('employee')

            # Create attendance map
            attendance_map = {record.employee_id: record for record in attendance_records}

            # Build report data
            report_data = []
            for employee in employees:
                attendance = attendance_map.get(employee.id)

                report_data.append({
                    'employee_id': employee.id,
                    'emp_code': employee.emp_code,
                    'employee_name': employee.get_full_name(),
                    'job_position': employee.job_position.title_ar if employee.job_position else '',
                    'status': attendance.status if attendance else 'absent',
                    'check_in_time': attendance.check_in_time if attendance else None,
                    'check_out_time': attendance.check_out_time if attendance else None,
                    'working_hours': attendance.working_hours if attendance else 0,
                    'late_minutes': attendance.late_minutes if attendance else 0,
                })

            # Calculate summary
            total_employees = len(employees)
            present_count = sum(1 for emp in report_data if emp['status'] == 'present')
            late_count = sum(1 for emp in report_data if emp['status'] == 'late')
            absent_count = sum(1 for emp in report_data if emp['status'] == 'absent')

            summary = {
                'department_name': department.name_ar,
                'report_date': report_date,
                'total_employees': total_employees,
                'present_count': present_count,
                'late_count': late_count,
                'absent_count': absent_count,
                'attendance_percentage': round((present_count / total_employees * 100), 2) if total_employees > 0 else 0,
            }

            return self.format_response(
                data={
                    'summary': summary,
                    'employees': report_data
                },
                message='تم إنشاء تقرير حضور القسم بنجاح'
            )

        except Department.DoesNotExist:
            return self.format_response(
                success=False,
                message='القسم غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_department_attendance_report', f'department_attendance/{department_id}')

    def calculate_overtime(self, employee_id, att_date, overtime_hours, reason=None, approved_by=None):
        """
        حساب وتسجيل الساعات الإضافية
        Calculate and record overtime hours
        """
        self.check_permission('attendance.add_overtimerecord')

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)

            # Get attendance record
            attendance = EmployeeAttendance.objects.filter(
                employee=employee,
                att_date=att_date
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            if not attendance:
                return self.format_response(
                    success=False,
                    message='لا يوجد سجل حضور لهذا التاريخ'
                )

            # Get overtime rules
            overtime_rule = AttendanceRule.objects.filter(
                rule_type='overtime',
                is_active=True
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            # Calculate overtime rate
            overtime_rate = 1.5  # Default 150%
            if overtime_rule and overtime_rule.overtime_rate:
                overtime_rate = overtime_rule.overtime_rate

            # Create overtime record
            overtime_record = OvertimeRecord.objects.create(
                employee=employee,
                attendance=attendance,
                overtime_date=att_date,
                overtime_hours=overtime_hours,
                overtime_rate=overtime_rate,
                reason=reason,
                approved_by_id=approved_by,
                status='pending' if not approved_by else 'approved',
                created_by=self.user,
                updated_by=self.user
            )

            # Update attendance record
            attendance.overtime_hours = overtime_hours
            attendance.save()

            # Log the action
            self.log_action(
                action='create',
                resource='overtime',
                content_object=overtime_record,
                message=f'تم تسجيل ساعات إضافية للموظف: {employee.get_full_name()}'
            )

            return self.format_response(
                data={'overtime_id': overtime_record.id},
                message='تم تسجيل الساعات الإضافية بنجاح'
            )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'calculate_overtime', f'overtime/{employee_id}')

    def sync_attendance_from_device(self, device_id, start_date=None, end_date=None):
        """
        مزامنة الحضور من الجهاز
        Sync attendance data from device
        """
        self.check_permission('attendance.add_employeeattendance')

        try:
            device = AttendanceDevice.objects.get(id=device_id)

            if not device.is_active:
                return self.format_response(
                    success=False,
                    message='الجهاز غير مفعل'
                )

            # Set default date range if not provided
            if not start_date:
                start_date = timezone.now().date() - timedelta(days=7)
            if not end_date:
                end_date = timezone.now().date()

            # This would integrate with actual device API
            # For now, we'll simulate the sync process
            synced_records = self._simulate_device_sync(device, start_date, end_date)

            # Process synced records
            processed_count = 0
            error_count = 0

            for record_data in synced_records:
                try:
                    result = self.record_attendance(
                        employee_id=record_data['employee_id'],
                        att_date=record_data['att_date'],
                        check_in_time=record_data.get('check_in_time'),
                        check_out_time=record_data.get('check_out_time'),
                        device_id=device_id,
                        manual_entry=False
                    )

                    if result['success']:
                        processed_count += 1
                    else:
                        error_count += 1

                except Exception as e:
                    error_count += 1
                    self.logger.error(f"Error processing attendance record: {e}")

            # Update device last sync time
            device.last_sync_time = timezone.now()
            device.save()

            # Log the sync operation
            self.log_action(
                action='sync',
                resource='attendance_device',
                content_object=device,
                details={
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'processed_count': processed_count,
                    'error_count': error_count
                },
                message=f'تم مزامنة الحضور من الجهاز: {device.name}'
            )

            return self.format_response(
                data={
                    'processed_count': processed_count,
                    'error_count': error_count,
                    'total_records': len(synced_records)
                },
                message=f'تم مزامنة {processed_count} سجل حضور بنجاح'
            )

        except AttendanceDevice.DoesNotExist:
            return self.format_response(
                success=False,
                message='جهاز الحضور غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'sync_attendance_from_device', f'device_sync/{device_id}')

    def _calculate_attendance_status(self, attendance):
        """حساب حالة الحضور"""
        try:
            # Get attendance rules
            rules = AttendanceRule.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            if not rules:
                # Default rules
                work_start_time = datetime.strptime('08:00', '%H:%M').time()
                work_end_time = datetime.strptime('17:00', '%H:%M').time()
                late_threshold = 15  # minutes
            else:
                work_start_time = rules.work_start_time
                work_end_time = rules.work_end_time
                late_threshold = rules.late_threshold_minutes or 15

            # Calculate status based on check-in time
            if attendance.check_in_time:
                if attendance.check_in_time <= work_start_time:
                    attendance.status = 'present'
                    attendance.late_minutes = 0
                else:
                    # Calculate late minutes
                    work_start_datetime = datetime.combine(attendance.att_date, work_start_time)
                    check_in_datetime = datetime.combine(attendance.att_date, attendance.check_in_time)
                    late_minutes = (check_in_datetime - work_start_datetime).total_seconds() / 60

                    attendance.late_minutes = int(late_minutes)

                    if late_minutes <= late_threshold:
                        attendance.status = 'present'
                    else:
                        attendance.status = 'late'
            else:
                attendance.status = 'absent'
                attendance.late_minutes = 0

            # Calculate working hours
            if attendance.check_in_time and attendance.check_out_time:
                check_in_datetime = datetime.combine(attendance.att_date, attendance.check_in_time)
                check_out_datetime = datetime.combine(attendance.att_date, attendance.check_out_time)

                working_duration = check_out_datetime - check_in_datetime
                attendance.working_hours = working_duration.total_seconds() / 3600

                # Calculate early departure
                if attendance.check_out_time < work_end_time:
                    work_end_datetime = datetime.combine(attendance.att_date, work_end_time)
                    early_departure = (work_end_datetime - check_out_datetime).total_seconds() / 60
                    attendance.early_departure_minutes = int(early_departure)

            attendance.save()

        except Exception as e:
            self.logger.error(f"Error calculating attendance status: {e}")

    def _count_working_days(self, start_date, end_date):
        """حساب أيام العمل (باستثناء عطل نهاية الأسبوع)"""
        working_days = 0
        current_date = start_date

        while current_date <= end_date:
            # Skip Friday (4) and Saturday (5) - weekend in many Arab countries
            if current_date.weekday() not in [4, 5]:
                working_days += 1
            current_date += timedelta(days=1)

        return working_days

    def _simulate_device_sync(self, device, start_date, end_date):
        """محاكاة مزامنة البيانات من الجهاز"""
        # This is a simulation - in real implementation, this would
        # connect to the actual attendance device API

        from core.models.hr import Employee
        import random

        employees = Employee.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields[:10]  # Limit for simulation
        synced_records = []

        current_date = start_date
        while current_date <= end_date:
            for employee in employees:
                # Simulate random attendance data
                if random.choice([True, False, True, True]):  # 75% attendance rate
                    check_in_hour = random.randint(7, 9)
                    check_in_minute = random.randint(0, 59)
                    check_out_hour = random.randint(16, 18)
                    check_out_minute = random.randint(0, 59)

                    synced_records.append({
                        'employee_id': employee.id,
                        'att_date': current_date,
                        'check_in_time': datetime.strptime(f'{check_in_hour:02d}:{check_in_minute:02d}', '%H:%M').time(),
                        'check_out_time': datetime.strptime(f'{check_out_hour:02d}:{check_out_minute:02d}', '%H:%M').time(),
                    })

            current_date += timedelta(days=1)

        return synced_records
