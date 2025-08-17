"""
Leave Service - خدمات إدارة الإجازات المتقدمة
"""

from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Count, Sum, Avg, F, Case, When
from decimal import Decimal
from datetime import date, datetime, timedelta
import logging
import json
import calendar
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger('hr_system')


class LeaveService:
    """خدمات إدارة الإجازات الشاملة"""
    
    def __init__(self):
        self.cache_timeout = 1800  # 30 minutes
    
    # =============================================================================
    # LEAVE REQUEST METHODS
    # =============================================================================
    
    def create_leave_request(self, employee_id: str, leave_type_id: str, 
                           start_date: date, end_date: date, 
                           reason: str = None, attachment_file=None) -> Dict:
        """إنشاء طلب إجازة"""
        try:
            from ..models import Employee, LeaveType, LeaveRequest
            
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                leave_type = LeaveType.objects.get(id=leave_type_id)
                
                # Validate leave request
                validation_result = self._validate_leave_request(
                    employee, leave_type, start_date, end_date
                )
                
                if not validation_result['is_valid']:
                    raise ValidationError(validation_result['errors'])
                
                # Calculate leave days
                leave_days = self._calculate_leave_days(start_date, end_date, leave_type)
                
                # Check leave balance
                balance_check = self._check_leave_balance(employee, leave_type, leave_days)
                if not balance_check['sufficient']:
                    raise ValidationError(f"رصيد الإجازة غير كافي. الرصيد المتاح: {balance_check['available_days']} يوم")
                
                # Create leave request
                leave_request = LeaveRequest.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    days_requested=leave_days,
                    reason=reason,
                    status='pending',
                    requested_at=timezone.now()
                )
                
                # Handle attachment if provided
                if attachment_file:
                    # Save attachment logic here
                    pass
                
                # Send notification to manager
                self._send_leave_request_notification(leave_request)
                
                logger.info(f"Created leave request {leave_request.id} for employee {employee.employee_number}")
                
                return {
                    'success': True,
                    'request_id': leave_request.id,
                    'days_requested': leave_days,
                    'status': leave_request.status,
                    'message': 'تم إنشاء طلب الإجازة بنجاح'
                }
                
        except (Employee.DoesNotExist, LeaveType.DoesNotExist):
            raise ValidationError("الموظف أو نوع الإجازة غير موجود")
        except Exception as e:
            logger.error(f"Error creating leave request: {e}")
            raise ValidationError(f"خطأ في إنشاء طلب الإجازة: {e}")
    
    def approve_leave_request(self, request_id: str, approved_by_id: str, 
                            comments: str = None, approved_days: int = None) -> Dict:
        """الموافقة على طلب إجازة"""
        try:
            from ..models import LeaveRequest, LeaveBalance
            
            with transaction.atomic():
                leave_request = LeaveRequest.objects.select_related(
                    'employee', 'leave_type'
                ).get(id=request_id)
                
                if leave_request.status != 'pending':
                    raise ValidationError("لا يمكن الموافقة على طلب إجازة غير معلق")
                
                # Use approved days or original requested days
                final_days = approved_days or leave_request.days_requested
                
                # Update leave request
                leave_request.status = 'approved'
                leave_request.approved_by_id = approved_by_id
                leave_request.approved_at = timezone.now()
                leave_request.approved_days = final_days
                leave_request.approval_comments = comments
                leave_request.save()
                
                # Update leave balance
                self._update_leave_balance(
                    leave_request.employee, 
                    leave_request.leave_type, 
                    -final_days,
                    f"إجازة معتمدة - طلب رقم {leave_request.id}"
                )
                
                # Send notification to employee
                self._send_leave_approval_notification(leave_request)
                
                logger.info(f"Approved leave request {request_id} for {final_days} days")
                
                return {
                    'success': True,
                    'request_id': request_id,
                    'approved_days': final_days,
                    'message': 'تم اعتماد طلب الإجازة بنجاح'
                }
                
        except LeaveRequest.DoesNotExist:
            raise ValidationError("طلب الإجازة غير موجود")
        except Exception as e:
            logger.error(f"Error approving leave request: {e}")
            raise ValidationError(f"خطأ في اعتماد طلب الإجازة: {e}")
    
    def reject_leave_request(self, request_id: str, rejected_by_id: str, 
                           rejection_reason: str) -> Dict:
        """رفض طلب إجازة"""
        try:
            from ..models import LeaveRequest
            
            leave_request = LeaveRequest.objects.get(id=request_id)
            
            if leave_request.status != 'pending':
                raise ValidationError("لا يمكن رفض طلب إجازة غير معلق")
            
            # Update leave request
            leave_request.status = 'rejected'
            leave_request.rejected_by_id = rejected_by_id
            leave_request.rejected_at = timezone.now()
            leave_request.rejection_reason = rejection_reason
            leave_request.save()
            
            # Send notification to employee
            self._send_leave_rejection_notification(leave_request)
            
            logger.info(f"Rejected leave request {request_id}")
            
            return {
                'success': True,
                'request_id': request_id,
                'message': 'تم رفض طلب الإجازة'
            }
            
        except LeaveRequest.DoesNotExist:
            raise ValidationError("طلب الإجازة غير موجود")
        except Exception as e:
            logger.error(f"Error rejecting leave request: {e}")
            raise ValidationError(f"خطأ في رفض طلب الإجازة: {e}")
    
    # =============================================================================
    # LEAVE BALANCE METHODS
    # =============================================================================
    
    def get_employee_leave_balance(self, employee_id: str, year: int = None) -> Dict:
        """الحصول على رصيد إجازات الموظف"""
        try:
            from ..models import Employee, LeaveBalance, LeaveType
            
            if year is None:
                year = date.today().year
            
            employee = Employee.objects.get(id=employee_id)
            
            # Get all leave types
            leave_types = LeaveType.objects.filter(is_active=True)
            
            balances = []
            for leave_type in leave_types:
                balance, created = LeaveBalance.objects.get_or_create(
                    employee=employee,
                    leave_type=leave_type,
                    year=year,
                    defaults={
                        'allocated_days': leave_type.default_days,
                        'used_days': 0,
                        'remaining_days': leave_type.default_days
                    }
                )
                
                balances.append({
                    'leave_type_id': leave_type.id,
                    'leave_type_name': leave_type.name,
                    'allocated_days': balance.allocated_days,
                    'used_days': balance.used_days,
                    'remaining_days': balance.remaining_days,
                    'pending_days': self._get_pending_leave_days(employee, leave_type, year),
                    'available_days': balance.remaining_days - self._get_pending_leave_days(employee, leave_type, year)
                })
            
            return {
                'employee': {
                    'id': employee.id,
                    'name': employee.full_name,
                    'employee_number': employee.employee_number
                },
                'year': year,
                'balances': balances,
                'generated_at': timezone.now()
            }
            
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"Error getting leave balance: {e}")
            raise ValidationError(f"خطأ في جلب رصيد الإجازات: {e}")
    
    def allocate_annual_leave(self, employee_id: str, year: int, 
                            leave_allocations: Dict[str, int]) -> Dict:
        """تخصيص الإجازات السنوية"""
        try:
            from ..models import Employee, LeaveBalance, LeaveType
            
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                
                allocated_types = []
                for leave_type_id, days in leave_allocations.items():
                    leave_type = LeaveType.objects.get(id=leave_type_id)
                    
                    balance, created = LeaveBalance.objects.get_or_create(
                        employee=employee,
                        leave_type=leave_type,
                        year=year,
                        defaults={
                            'allocated_days': days,
                            'used_days': 0,
                            'remaining_days': days
                        }
                    )
                    
                    if not created:
                        # Update existing balance
                        balance.allocated_days = days
                        balance.remaining_days = days - balance.used_days
                        balance.save()
                    
                    allocated_types.append({
                        'leave_type': leave_type.name,
                        'allocated_days': days
                    })
                
                logger.info(f"Allocated annual leave for employee {employee.employee_number} for year {year}")
                
                return {
                    'success': True,
                    'employee_id': employee_id,
                    'year': year,
                    'allocated_types': allocated_types,
                    'message': 'تم تخصيص الإجازات السنوية بنجاح'
                }
                
        except (Employee.DoesNotExist, LeaveType.DoesNotExist):
            raise ValidationError("الموظف أو نوع الإجازة غير موجود")
        except Exception as e:
            logger.error(f"Error allocating annual leave: {e}")
            raise ValidationError(f"خطأ في تخصيص الإجازات السنوية: {e}")
    
    def bulk_allocate_leave(self, employee_ids: List[str], year: int, 
                          leave_type_id: str, days: int) -> Dict:
        """تخصيص مجمع للإجازات"""
        try:
            from ..models import Employee, LeaveBalance, LeaveType
            
            leave_type = LeaveType.objects.get(id=leave_type_id)
            
            results = {
                'success_count': 0,
                'error_count': 0,
                'errors': []
            }
            
            with transaction.atomic():
                for employee_id in employee_ids:
                    try:
                        employee = Employee.objects.get(id=employee_id)
                        
                        balance, created = LeaveBalance.objects.get_or_create(
                            employee=employee,
                            leave_type=leave_type,
                            year=year,
                            defaults={
                                'allocated_days': days,
                                'used_days': 0,
                                'remaining_days': days
                            }
                        )
                        
                        if not created:
                            balance.allocated_days = days
                            balance.remaining_days = days - balance.used_days
                            balance.save()
                        
                        results['success_count'] += 1
                        
                    except Employee.DoesNotExist:
                        results['error_count'] += 1
                        results['errors'].append(f"الموظف {employee_id} غير موجود")
                    except Exception as e:
                        results['error_count'] += 1
                        results['errors'].append(f"خطأ في الموظف {employee_id}: {e}")
            
            logger.info(f"Bulk leave allocation completed: {results['success_count']} success, {results['error_count']} errors")
            
            return results
            
        except LeaveType.DoesNotExist:
            raise ValidationError("نوع الإجازة غير موجود")
        except Exception as e:
            logger.error(f"Error in bulk leave allocation: {e}")
            raise ValidationError(f"خطأ في التخصيص المجمع للإجازات: {e}")
    
    # =============================================================================
    # LEAVE REPORTING METHODS
    # =============================================================================
    
    def get_leave_report(self, start_date: date, end_date: date, 
                        department_id: str = None, leave_type_id: str = None) -> Dict:
        """تقرير الإجازات"""
        try:
            from ..models import LeaveRequest, Employee, Department, LeaveType
            
            # Build query
            query = Q(start_date__lte=end_date, end_date__gte=start_date, status='approved')
            
            if department_id:
                query &= Q(employee__department_id=department_id)
            if leave_type_id:
                query &= Q(leave_type_id=leave_type_id)
            
            leave_requests = LeaveRequest.objects.filter(query).select_related(
                'employee__department', 'leave_type'
            )
            
            # Calculate statistics
            total_requests = leave_requests.count()
            total_days = leave_requests.aggregate(
                total=Sum('approved_days')
            )['total'] or 0
            
            # By department
            by_department = leave_requests.values(
                'employee__department__name'
            ).annotate(
                request_count=Count('id'),
                total_days=Sum('approved_days')
            ).order_by('-total_days')
            
            # By leave type
            by_leave_type = leave_requests.values(
                'leave_type__name'
            ).annotate(
                request_count=Count('id'),
                total_days=Sum('approved_days')
            ).order_by('-total_days')
            
            # By month
            monthly_data = leave_requests.extra(
                select={'month': "MONTH(start_date)"}
            ).values('month').annotate(
                request_count=Count('id'),
                total_days=Sum('approved_days')
            ).order_by('month')
            
            # Top employees by leave days
            top_employees = leave_requests.values(
                'employee__full_name', 'employee__employee_number'
            ).annotate(
                total_days=Sum('approved_days')
            ).order_by('-total_days')[:10]
            
            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'department_id': department_id,
                    'leave_type_id': leave_type_id
                },
                'summary': {
                    'total_requests': total_requests,
                    'total_days': total_days,
                    'average_days_per_request': round(total_days / total_requests, 2) if total_requests > 0 else 0
                },
                'by_department': list(by_department),
                'by_leave_type': list(by_leave_type),
                'monthly_data': list(monthly_data),
                'top_employees': list(top_employees),
                'generated_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating leave report: {e}")
            raise ValidationError(f"خطأ في إنتاج تقرير الإجازات: {e}")
    
    def get_leave_calendar(self, year: int, month: int, 
                          department_id: str = None) -> Dict:
        """تقويم الإجازات"""
        try:
            from ..models import LeaveRequest
            
            # Get month date range
            start_date = date(year, month, 1)
            end_date = date(year, month, calendar.monthrange(year, month)[1])
            
            # Build query
            query = Q(
                start_date__lte=end_date,
                end_date__gte=start_date,
                status='approved'
            )
            
            if department_id:
                query &= Q(employee__department_id=department_id)
            
            leave_requests = LeaveRequest.objects.filter(query).select_related(
                'employee', 'leave_type'
            )
            
            # Build calendar data
            calendar_data = {}
            current_date = start_date
            
            while current_date <= end_date:
                calendar_data[current_date.isoformat()] = {
                    'date': current_date,
                    'employees_on_leave': [],
                    'total_employees': 0
                }
                current_date += timedelta(days=1)
            
            # Populate calendar with leave data
            for leave_request in leave_requests:
                current_date = max(leave_request.start_date, start_date)
                end_leave_date = min(leave_request.end_date, end_date)
                
                while current_date <= end_leave_date:
                    date_key = current_date.isoformat()
                    if date_key in calendar_data:
                        calendar_data[date_key]['employees_on_leave'].append({
                            'employee_id': leave_request.employee.id,
                            'employee_name': leave_request.employee.full_name,
                            'employee_number': leave_request.employee.employee_number,
                            'leave_type': leave_request.leave_type.name,
                            'leave_type_color': leave_request.leave_type.color or '#007bff'
                        })
                        calendar_data[date_key]['total_employees'] += 1
                    
                    current_date += timedelta(days=1)
            
            return {
                'year': year,
                'month': month,
                'month_name': calendar.month_name[month],
                'department_id': department_id,
                'calendar_data': calendar_data,
                'generated_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating leave calendar: {e}")
            raise ValidationError(f"خطأ في إنتاج تقويم الإجازات: {e}")
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _validate_leave_request(self, employee, leave_type, start_date, end_date) -> Dict:
        """التحقق من صحة طلب الإجازة"""
        errors = []
        
        # Check date validity
        if start_date > end_date:
            errors.append("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
        
        if start_date < date.today():
            errors.append("لا يمكن طلب إجازة في الماضي")
        
        # Check minimum notice period
        if leave_type.requires_approval and leave_type.min_notice_days:
            notice_date = date.today() + timedelta(days=leave_type.min_notice_days)
            if start_date < notice_date:
                errors.append(f"يجب تقديم الطلب قبل {leave_type.min_notice_days} يوم على الأقل")
        
        # Check maximum consecutive days
        if leave_type.max_consecutive_days:
            requested_days = (end_date - start_date).days + 1
            if requested_days > leave_type.max_consecutive_days:
                errors.append(f"الحد الأقصى للأيام المتتالية هو {leave_type.max_consecutive_days} يوم")
        
        # Check for overlapping requests
        from ..models import LeaveRequest
        overlapping = LeaveRequest.objects.filter(
            employee=employee,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status__in=['pending', 'approved']
        ).exists()
        
        if overlapping:
            errors.append("يوجد طلب إجازة متداخل في نفس الفترة")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _calculate_leave_days(self, start_date, end_date, leave_type) -> int:
        """حساب أيام الإجازة"""
        if leave_type.exclude_weekends:
            # Count only working days (exclude weekends)
            days = 0
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() < 5:  # Monday to Friday
                    days += 1
                current_date += timedelta(days=1)
            return days
        else:
            # Count all days
            return (end_date - start_date).days + 1
    
    def _check_leave_balance(self, employee, leave_type, requested_days) -> Dict:
        """فحص رصيد الإجازة"""
        try:
            from ..models import LeaveBalance
            
            year = date.today().year
            balance = LeaveBalance.objects.get(
                employee=employee,
                leave_type=leave_type,
                year=year
            )
            
            # Consider pending requests
            pending_days = self._get_pending_leave_days(employee, leave_type, year)
            available_days = balance.remaining_days - pending_days
            
            return {
                'sufficient': available_days >= requested_days,
                'available_days': available_days,
                'requested_days': requested_days
            }
            
        except LeaveBalance.DoesNotExist:
            # No balance record, assume no days available
            return {
                'sufficient': False,
                'available_days': 0,
                'requested_days': requested_days
            }
    
    def _get_pending_leave_days(self, employee, leave_type, year) -> int:
        """الحصول على أيام الإجازة المعلقة"""
        from ..models import LeaveRequest
        
        pending_requests = LeaveRequest.objects.filter(
            employee=employee,
            leave_type=leave_type,
            status='pending',
            start_date__year=year
        )
        
        return pending_requests.aggregate(
            total=Sum('days_requested')
        )['total'] or 0
    
    def _update_leave_balance(self, employee, leave_type, days_change, description):
        """تحديث رصيد الإجازة"""
        from ..models import LeaveBalance, LeaveBalanceTransaction
        
        year = date.today().year
        balance, created = LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            year=year,
            defaults={
                'allocated_days': leave_type.default_days,
                'used_days': 0,
                'remaining_days': leave_type.default_days
            }
        )
        
        # Update balance
        if days_change < 0:  # Using leave days
            balance.used_days += abs(days_change)
            balance.remaining_days -= abs(days_change)
        else:  # Adding leave days
            balance.remaining_days += days_change
        
        balance.save()
        
        # Create transaction record
        LeaveBalanceTransaction.objects.create(
            balance=balance,
            transaction_type='deduction' if days_change < 0 else 'addition',
            days=abs(days_change),
            description=description,
            created_at=timezone.now()
        )
    
    def _send_leave_request_notification(self, leave_request):
        """إرسال إشعار طلب الإجازة"""
        # This would send notification to manager
        # Implementation depends on your notification system
        pass
    
    def _send_leave_approval_notification(self, leave_request):
        """إرسال إشعار الموافقة على الإجازة"""
        # This would send notification to employee
        pass
    
    def _send_leave_rejection_notification(self, leave_request):
        """إرسال إشعار رفض الإجازة"""
        # This would send notification to employee
        pass