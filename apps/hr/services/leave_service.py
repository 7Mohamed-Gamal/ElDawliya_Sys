"""
خدمة إدارة الإجازات وسير العمل
Leave Management and Workflow Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from core.services.base import BaseService
from core.models.leaves import (
    LeaveType, LeaveBalance, LeaveRequest, LeaveRecord, PublicHoliday
)


class LeaveService(BaseService):
    """
    خدمة إدارة الإجازات وسير العمل
    Comprehensive leave management with approval workflow
    """

    def submit_leave_request(self, employee_id, data):
        """
        تقديم طلب إجازة
        Submit leave request
        """
        self.check_permission('leaves.add_leaverequest')

        required_fields = ['leave_type_id', 'start_date', 'end_date', 'reason']
        self.validate_required_fields(data, required_fields)

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)
            leave_type = LeaveType.objects.get(id=data['leave_type_id'])

            # Validate leave request
            validation_result = self._validate_leave_request(employee, leave_type, data)
            if not validation_result['valid']:
                return self.format_response(
                    success=False,
                    message=validation_result['message']
                )

            # Calculate leave days
            leave_days = self._calculate_leave_days(
                data['start_date'],
                data['end_date'],
                leave_type.include_weekends,
                leave_type.include_holidays
            )

            with transaction.atomic():
                # Create leave request
                leave_request = LeaveRequest.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    start_date=data['start_date'],
                    end_date=data['end_date'],
                    leave_days=leave_days,
                    reason=data['reason'],
                    emergency_contact=data.get('emergency_contact'),
                    emergency_phone=data.get('emergency_phone'),
                    status='pending',
                    created_by=self.user,
                    updated_by=self.user
                )

                # Start approval workflow
                self._initiate_approval_workflow(leave_request)

                # Log the action
                self.log_action(
                    action='create',
                    resource='leave_request',
                    content_object=leave_request,
                    new_values=data,
                    message=f'تم تقديم طلب إجازة للموظف: {employee.get_full_name()}'
                )

                # Send notification to approvers
                self._notify_approvers(leave_request)

                return self.format_response(
                    data={
                        'leave_request_id': leave_request.id,
                        'leave_days': leave_days,
                        'status': leave_request.status
                    },
                    message='تم تقديم طلب الإجازة بنجاح'
                )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except LeaveType.DoesNotExist:
            return self.format_response(
                success=False,
                message='نوع الإجازة غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'submit_leave_request', f'leave_request/{employee_id}', data)

    def approve_leave_request(self, leave_request_id, action, comments=None):
        """
        اعتماد أو رفض طلب الإجازة
        Approve or reject leave request
        """
        self.check_permission('leaves.change_leaverequest')

        if action not in ['approve', 'reject']:
            return self.format_response(
                success=False,
                message='الإجراء غير صحيح. يجب أن يكون approve أو reject'
            )

        try:
            leave_request = LeaveRequest.objects.select_related(
                'employee', 'leave_type'
            ).get(id=leave_request_id)

            # Check if user can approve this request
            if not self._can_approve_request(leave_request, self.user):
                return self.format_response(
                    success=False,
                    message='ليس لديك صلاحية اعتماد هذا الطلب'
                )

            if leave_request.status != 'pending':
                return self.format_response(
                    success=False,
                    message='لا يمكن تعديل طلب إجازة غير معلق'
                )

            with transaction.atomic():
                # Create approval record
                approval = LeaveApproval.objects.create(
                    leave_request=leave_request,
                    approver=self.user,
                    action=action,
                    comments=comments,
                    approval_date=timezone.now(),
                    created_by=self.user,
                    updated_by=self.user
                )

                if action == 'approve':
                    # Check if this is the final approval
                    if self._is_final_approval(leave_request, approval):
                        leave_request.status = 'approved'
                        leave_request.approved_by = self.user
                        leave_request.approved_at = timezone.now()

                        # Deduct from leave balance
                        self._deduct_leave_balance(leave_request)

                        # Send approval notification
                        self._send_approval_notification(leave_request, 'approved')
                    else:
                        # Move to next approval level
                        leave_request.status = 'pending'
                        self._notify_next_approver(leave_request)
                else:
                    # Reject the request
                    leave_request.status = 'rejected'
                    leave_request.rejected_by = self.user
                    leave_request.rejected_at = timezone.now()

                    # Send rejection notification
                    self._send_approval_notification(leave_request, 'rejected')

                leave_request.updated_by = self.user
                leave_request.save()

                # Log the action
                self.log_action(
                    action=action,
                    resource='leave_approval',
                    content_object=leave_request,
                    details={
                        'action': action,
                        'comments': comments,
                        'approver_id': self.user.id
                    },
                    message=f'تم {action} طلب إجازة الموظف: {leave_request.employee.get_full_name()}'
                )

                return self.format_response(
                    data={
                        'leave_request_id': leave_request.id,
                        'new_status': leave_request.status
                    },
                    message=f'تم {action} طلب الإجازة بنجاح'
                )

        except LeaveRequest.DoesNotExist:
            return self.format_response(
                success=False,
                message='طلب الإجازة غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'approve_leave_request', f'leave_approval/{leave_request_id}')

    def get_employee_leave_balance(self, employee_id, leave_type_id=None):
        """
        الحصول على رصيد إجازات الموظف
        Get employee leave balance
        """
        self.check_permission('leaves.view_leavebalance')

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)

            # Check object-level permission
            self.check_object_permission('leaves.view_leavebalance', employee)

            queryset = LeaveBalance.objects.filter(employee=employee)

            if leave_type_id:
                queryset = queryset.filter(leave_type_id=leave_type_id)

            balances = queryset.select_related('leave_type').values(
                'leave_type__name_ar',
                'leave_type__name_en',
                'total_days',
                'used_days',
                'remaining_days',
                'year'
            )

            return self.format_response(
                data=list(balances),
                message='تم الحصول على رصيد الإجازات بنجاح'
            )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_employee_leave_balance', f'leave_balance/{employee_id}')

    def get_leave_requests(self, filters=None, page=1, page_size=20):
        """
        الحصول على طلبات الإجازات
        Get leave requests with filters
        """
        self.check_permission('leaves.view_leaverequest')

        try:
            queryset = LeaveRequest.objects.select_related(
                'employee', 'leave_type', 'approved_by', 'rejected_by'
            )

            # Apply filters
            if filters:
                if filters.get('employee_id'):
                    queryset = queryset.filter(employee_id=filters['employee_id'])

                if filters.get('department_id'):
                    queryset = queryset.filter(employee__department_id=filters['department_id'])

                if filters.get('leave_type_id'):
                    queryset = queryset.filter(leave_type_id=filters['leave_type_id'])

                if filters.get('status'):
                    queryset = queryset.filter(status=filters['status'])

                if filters.get('start_date'):
                    queryset = queryset.filter(start_date__gte=filters['start_date'])

                if filters.get('end_date'):
                    queryset = queryset.filter(end_date__lte=filters['end_date'])

            # Apply user-level filtering if not admin
            if not self.user.is_superuser and not self.user.has_perm('leaves.view_all_requests'):
                # Show only requests from same department or own requests
                user_employee = getattr(self.user, 'employee', None)
                if user_employee:
                    if user_employee.department:
                        queryset = queryset.filter(
                            Q(employee__department=user_employee.department) |
                            Q(employee=user_employee)
                        )
                    else:
                        queryset = queryset.filter(employee=user_employee)

            queryset = queryset.order_by('-created_at')

            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)

            # Format leave request data
            leave_requests = []
            for request in paginated_data['results']:
                leave_requests.append({
                    'id': request.id,
                    'employee_name': request.employee.get_full_name(),
                    'employee_code': request.employee.emp_code,
                    'leave_type': request.leave_type.name_ar,
                    'start_date': request.start_date,
                    'end_date': request.end_date,
                    'leave_days': request.leave_days,
                    'reason': request.reason,
                    'status': request.status,
                    'submitted_at': request.created_at,
                    'approved_by': request.approved_by.get_full_name() if request.approved_by else None,
                    'approved_at': request.approved_at,
                })

            paginated_data['results'] = leave_requests

            return self.format_response(
                data=paginated_data,
                message='تم الحصول على طلبات الإجازات بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_leave_requests', 'leave_requests', filters)

    def calculate_annual_leave_entitlement(self, employee_id, year=None):
        """
        حساب استحقاق الإجازة السنوية
        Calculate annual leave entitlement
        """
        self.check_permission('leaves.view_leavebalance')

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)
            year = year or timezone.now().year

            # Get leave policy for annual leave
            annual_leave_type = LeaveType.objects.filter(
                code='annual',
                is_active=True
            ).first()

            if not annual_leave_type:
                return self.format_response(
                    success=False,
                    message='نوع الإجازة السنوية غير موجود'
                )

            # Calculate service years
            if not employee.hire_date:
                return self.format_response(
                    success=False,
                    message='تاريخ التوظيف غير محدد'
                )

            service_years = self._calculate_service_years_at_year_end(employee.hire_date, year)

            # Get leave policy
            leave_policy = LeavePolicy.objects.filter(
                leave_type=annual_leave_type,
                min_service_years__lte=service_years,
                is_active=True
            ).order_by('-min_service_years').first()

            if not leave_policy:
                # Default entitlement
                entitlement_days = 21  # Default 21 days
            else:
                entitlement_days = leave_policy.days_per_year

            # Check if balance already exists
            leave_balance, created = LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=annual_leave_type,
                year=year,
                defaults={
                    'total_days': entitlement_days,
                    'used_days': 0,
                    'remaining_days': entitlement_days,
                    'created_by': self.user,
                    'updated_by': self.user
                }
            )

            if not created and leave_balance.total_days != entitlement_days:
                # Update entitlement if changed
                leave_balance.total_days = entitlement_days
                leave_balance.remaining_days = entitlement_days - leave_balance.used_days
                leave_balance.updated_by = self.user
                leave_balance.save()

            return self.format_response(
                data={
                    'employee_name': employee.get_full_name(),
                    'year': year,
                    'service_years': service_years,
                    'entitlement_days': entitlement_days,
                    'used_days': leave_balance.used_days,
                    'remaining_days': leave_balance.remaining_days,
                },
                message='تم حساب استحقاق الإجازة السنوية بنجاح'
            )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'calculate_annual_leave_entitlement', f'leave_entitlement/{employee_id}')

    def get_leave_calendar(self, start_date=None, end_date=None):
        """
        الحصول على تقويم الإجازات
        Get leave calendar
        """
        self.check_permission('leaves.view_leaverequest')

        try:
            # Set default date range if not provided
            if not start_date:
                start_date = timezone.now().date().replace(day=1)  # First day of current month
            if not end_date:
                end_date = start_date.replace(month=start_date.month + 1) - timedelta(days=1)  # Last day of month

            # Get approved leave requests in date range
            leave_requests = LeaveRequest.objects.filter(
                status='approved',
                start_date__lte=end_date,
                end_date__gte=start_date
            ).select_related('employee', 'leave_type')

            # Get holidays
            holidays = HolidayCalendar.objects.filter(
                holiday_date__range=[start_date, end_date],
                is_active=True
            )

            # Format calendar data
            calendar_events = []

            # Add leave requests
            for leave in leave_requests:
                calendar_events.append({
                    'type': 'leave',
                    'id': leave.id,
                    'title': f'{leave.employee.get_full_name()} - {leave.leave_type.name_ar}',
                    'start_date': leave.start_date,
                    'end_date': leave.end_date,
                    'employee_name': leave.employee.get_full_name(),
                    'leave_type': leave.leave_type.name_ar,
                    'days': leave.leave_days,
                })

            # Add holidays
            for holiday in holidays:
                calendar_events.append({
                    'type': 'holiday',
                    'id': holiday.id,
                    'title': holiday.name_ar,
                    'start_date': holiday.holiday_date,
                    'end_date': holiday.holiday_date,
                    'description': holiday.description,
                })

            return self.format_response(
                data={
                    'start_date': start_date,
                    'end_date': end_date,
                    'events': calendar_events
                },
                message='تم الحصول على تقويم الإجازات بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_leave_calendar', 'leave_calendar')

    def _validate_leave_request(self, employee, leave_type, data):
        """التحقق من صحة طلب الإجازة"""
        try:
            start_date = data['start_date']
            end_date = data['end_date']

            # Check date validity
            if start_date > end_date:
                return {'valid': False, 'message': 'تاريخ البداية يجب أن يكون قبل تاريخ النهاية'}

            if start_date < timezone.now().date():
                return {'valid': False, 'message': 'لا يمكن تقديم طلب إجازة لتاريخ سابق'}

            # Check minimum notice period
            if leave_type.min_notice_days:
                notice_days = (start_date - timezone.now().date()).days
                if notice_days < leave_type.min_notice_days:
                    return {
                        'valid': False,
                        'message': f'يجب تقديم الطلب قبل {leave_type.min_notice_days} أيام على الأقل'
                    }

            # Check maximum days per request
            if leave_type.max_days_per_request:
                leave_days = self._calculate_leave_days(start_date, end_date, False, False)
                if leave_days > leave_type.max_days_per_request:
                    return {
                        'valid': False,
                        'message': f'الحد الأقصى للإجازة {leave_type.max_days_per_request} أيام'
                    }

            # Check leave balance
            if leave_type.requires_balance:
                leave_days = self._calculate_leave_days(start_date, end_date, False, False)
                balance = LeaveBalance.objects.filter(
                    employee=employee,
                    leave_type=leave_type,
                    year=start_date.year
                ).first()

                if not balance or balance.remaining_days < leave_days:
                    return {'valid': False, 'message': 'رصيد الإجازة غير كافي'}

            # Check overlapping requests
            overlapping = LeaveRequest.objects.filter(
                employee=employee,
                status__in=['pending', 'approved'],
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exists()

            if overlapping:
                return {'valid': False, 'message': 'يوجد طلب إجازة متداخل مع هذه الفترة'}

            return {'valid': True, 'message': 'طلب الإجازة صحيح'}

        except Exception as e:
            return {'valid': False, 'message': f'خطأ في التحقق من الطلب: {str(e)}'}

    def _calculate_leave_days(self, start_date, end_date, include_weekends=False, include_holidays=False):
        """حساب أيام الإجازة"""
        total_days = 0
        current_date = start_date

        while current_date <= end_date:
            # Skip weekends if not included
            if not include_weekends and current_date.weekday() in [4, 5]:  # Friday, Saturday
                current_date += timedelta(days=1)
                continue

            # Skip holidays if not included
            if not include_holidays:
                is_holiday = HolidayCalendar.objects.filter(
                    holiday_date=current_date,
                    is_active=True
                ).exists()
                if is_holiday:
                    current_date += timedelta(days=1)
                    continue

            total_days += 1
            current_date += timedelta(days=1)

        return total_days

    def _calculate_service_years_at_year_end(self, hire_date, year):
        """حساب سنوات الخدمة في نهاية السنة"""
        year_end = date(year, 12, 31)
        if hire_date > year_end:
            return 0

        service_period = year_end - hire_date
        return service_period.days / 365.25

    def _initiate_approval_workflow(self, leave_request):
        """بدء سير عمل الاعتماد"""
        # This would implement the approval workflow logic
        # For now, we'll use a simple manager approval
        pass

    def _can_approve_request(self, leave_request, user):
        """فحص إمكانية اعتماد الطلب"""
        # Check if user is the employee's manager
        if leave_request.employee.manager and leave_request.employee.manager.user == user:
            return True

        # Check if user has approval permission
        if user.has_perm('leaves.approve_leaverequest'):
            return True

        return False

    def _is_final_approval(self, leave_request, approval):
        """فحص إذا كان هذا الاعتماد الأخير"""
        # For now, assume single-level approval
        return True

    def _deduct_leave_balance(self, leave_request):
        """خصم من رصيد الإجازة"""
        if leave_request.leave_type.requires_balance:
            balance = LeaveBalance.objects.filter(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            ).first()

            if balance:
                balance.used_days += leave_request.leave_days
                balance.remaining_days = balance.total_days - balance.used_days
                balance.save()

    def _notify_approvers(self, leave_request):
        """إشعار المعتمدين"""
        try:
            if leave_request.employee.manager and leave_request.employee.manager.user:
                self.send_notification(
                    recipient=leave_request.employee.manager.user,
                    template_name='leave_request_submitted',
                    context={'leave_request': leave_request},
                    channels=['in_app', 'email']
                )
        except Exception as e:
            self.logger.warning(f"Failed to notify approvers: {e}")

    def _notify_next_approver(self, leave_request):
        """إشعار المعتمد التالي"""
        # This would implement multi-level approval notifications
        pass

    def _send_approval_notification(self, leave_request, action):
        """إرسال إشعار الاعتماد أو الرفض"""
        try:
            template_name = f'leave_request_{action}'
            recipient = leave_request.employee.user if leave_request.employee.user else leave_request.employee

            self.send_notification(
                recipient=recipient,
                template_name=template_name,
                context={'leave_request': leave_request},
                channels=['in_app', 'email']
            )
        except Exception as e:
            self.logger.warning(f"Failed to send approval notification: {e}")
