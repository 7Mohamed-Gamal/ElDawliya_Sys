"""
Payroll Service - خدمات إدارة الرواتب المتطورة
"""

from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Count, Sum, Avg, F, Case, When
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime, timedelta
import logging
import json
import calendar
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger('hr_system')


class PayrollService:
    """خدمات إدارة الرواتب الشاملة"""
    
    def __init__(self):
        self.cache_timeout = 1800  # 30 minutes
        self.rounding_precision = Decimal('0.01')  # Round to 2 decimal places
    
    # =============================================================================
    # SALARY CALCULATION METHODS
    # =============================================================================
    
    def calculate_employee_salary(self, employee_id: str, year: int, month: int, 
                                include_overtime: bool = True, 
                                include_deductions: bool = True) -> Dict:
        """حساب راتب الموظف لشهر محدد"""
        try:
            from ..models import Employee, AttendanceSummary
            
            employee = Employee.objects.select_related(
                'company', 'branch', 'department', 'job_position'
            ).get(id=employee_id)
            
            # Get month date range
            start_date = date(year, month, 1)
            end_date = date(year, month, calendar.monthrange(year, month)[1])
            
            # Basic salary components
            basic_salary = employee.basic_salary
            
            # Initialize salary breakdown
            salary_breakdown = {
                'employee_info': {
                    'id': employee.id,
                    'employee_number': employee.employee_number,
                    'name': employee.full_name,
                    'department': employee.department.name,
                    'position': employee.job_position.title
                },
                'period': {
                    'year': year,
                    'month': month,
                    'start_date': start_date,
                    'end_date': end_date,
                    'working_days': self._get_working_days(start_date, end_date)
                },
                'basic_components': {
                    'basic_salary': float(basic_salary),
                    'housing_allowance': 0,
                    'transportation_allowance': 0,
                    'food_allowance': 0,
                    'other_allowances': 0
                },
                'attendance_based': {
                    'overtime_amount': 0,
                    'late_deductions': 0,
                    'absence_deductions': 0,
                    'bonus_amount': 0
                },
                'statutory_deductions': {
                    'social_insurance_employee': 0,
                    'income_tax': 0,
                    'medical_insurance': 0
                },
                'other_deductions': {
                    'loan_deductions': 0,
                    'advance_deductions': 0,
                    'other': 0
                },
                'totals': {
                    'gross_salary': 0,
                    'total_allowances': 0,
                    'total_deductions': 0,
                    'net_salary': 0
                }
            }
            
            # Calculate allowances
            salary_breakdown['basic_components'].update(
                self._calculate_allowances(employee)
            )
            
            # Calculate attendance-based components
            if include_overtime:
                attendance_data = self._get_attendance_data(employee, start_date, end_date)
                salary_breakdown['attendance_based'].update(
                    self._calculate_attendance_based_components(employee, attendance_data)
                )
            
            # Calculate deductions
            if include_deductions:
                salary_breakdown['statutory_deductions'].update(
                    self._calculate_statutory_deductions(employee, salary_breakdown)
                )
                salary_breakdown['other_deductions'].update(
                    self._calculate_other_deductions(employee, year, month)
                )
            
            # Calculate totals
            salary_breakdown['totals'] = self._calculate_salary_totals(salary_breakdown)
            
            # Round all monetary values
            salary_breakdown = self._round_salary_values(salary_breakdown)
            
            logger.info(f"Calculated salary for employee {employee.employee_number} for {year}-{month}")
            
            return salary_breakdown
            
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"Error calculating salary for employee {employee_id}: {e}")
            raise ValidationError(f"خطأ في حساب الراتب: {e}")
    
    def calculate_bulk_payroll(self, employee_ids: List[str], year: int, month: int,
                             save_results: bool = False) -> Dict:
        """حساب الرواتب المجمع"""
        try:
            from ..models import Employee, PayrollRecord
            
            results = {
                'success_count': 0,
                'error_count': 0,
                'total_amount': Decimal('0'),
                'employees': [],
                'errors': [],
                'summary': {
                    'total_basic_salary': Decimal('0'),
                    'total_allowances': Decimal('0'),
                    'total_deductions': Decimal('0'),
                    'total_net_salary': Decimal('0')
                }
            }
            
            with transaction.atomic():
                for employee_id in employee_ids:
                    try:
                        # Calculate individual salary
                        salary_data = self.calculate_employee_salary(employee_id, year, month)
                        
                        # Add to results
                        results['employees'].append(salary_data)
                        results['success_count'] += 1
                        
                        # Update summary
                        totals = salary_data['totals']
                        results['summary']['total_basic_salary'] += Decimal(str(totals['gross_salary']))
                        results['summary']['total_allowances'] += Decimal(str(totals['total_allowances']))
                        results['summary']['total_deductions'] += Decimal(str(totals['total_deductions']))
                        results['summary']['total_net_salary'] += Decimal(str(totals['net_salary']))
                        
                        # Save payroll record if requested
                        if save_results:
                            self._save_payroll_record(employee_id, year, month, salary_data)
                        
                    except Exception as e:
                        results['error_count'] += 1
                        results['errors'].append({
                            'employee_id': employee_id,
                            'error': str(e)
                        })
                        logger.error(f"Error calculating salary for employee {employee_id}: {e}")
            
            # Convert Decimal to float for JSON serialization
            for key in results['summary']:
                results['summary'][key] = float(results['summary'][key])
            
            logger.info(f"Bulk payroll calculation completed: {results['success_count']} success, {results['error_count']} errors")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk payroll calculation: {e}")
            raise ValidationError(f"خطأ في حساب الرواتب المجمع: {e}")
    
    def generate_payslip(self, employee_id: str, year: int, month: int, 
                        format: str = 'pdf') -> bytes:
        """إنتاج كشف راتب"""
        try:
            # Calculate salary
            salary_data = self.calculate_employee_salary(employee_id, year, month)
            
            if format == 'pdf':
                return self._generate_pdf_payslip(salary_data)
            elif format == 'html':
                return self._generate_html_payslip(salary_data)
            else:
                raise ValidationError("تنسيق كشف الراتب غير مدعوم")
                
        except Exception as e:
            logger.error(f"Error generating payslip: {e}")
            raise ValidationError(f"خطأ في إنتاج كشف الراتب: {e}")
    
    # =============================================================================
    # PAYROLL MANAGEMENT METHODS
    # =============================================================================
    
    def create_payroll_batch(self, batch_name: str, employee_ids: List[str], 
                           year: int, month: int, created_by_id: str) -> Dict:
        """إنشاء دفعة رواتب"""
        try:
            from ..models import PayrollBatch, PayrollRecord
            
            with transaction.atomic():
                # Create batch
                batch = PayrollBatch.objects.create(
                    name=batch_name,
                    year=year,
                    month=month,
                    created_by_id=created_by_id,
                    status='draft',
                    total_employees=len(employee_ids)
                )
                
                # Calculate payroll for all employees
                payroll_results = self.calculate_bulk_payroll(employee_ids, year, month, save_results=False)
                
                # Create payroll records
                for salary_data in payroll_results['employees']:
                    PayrollRecord.objects.create(
                        batch=batch,
                        employee_id=salary_data['employee_info']['id'],
                        basic_salary=Decimal(str(salary_data['basic_components']['basic_salary'])),
                        total_allowances=Decimal(str(salary_data['totals']['total_allowances'])),
                        total_deductions=Decimal(str(salary_data['totals']['total_deductions'])),
                        gross_salary=Decimal(str(salary_data['totals']['gross_salary'])),
                        net_salary=Decimal(str(salary_data['totals']['net_salary'])),
                        salary_data=json.dumps(salary_data),
                        status='calculated'
                    )
                
                # Update batch totals
                batch.total_amount = Decimal(str(payroll_results['summary']['total_net_salary']))
                batch.processed_employees = payroll_results['success_count']
                batch.failed_employees = payroll_results['error_count']
                batch.save()
                
                logger.info(f"Created payroll batch {batch_name} with {len(employee_ids)} employees")
                
                return {
                    'batch_id': batch.id,
                    'batch_name': batch.name,
                    'total_employees': batch.total_employees,
                    'processed_employees': batch.processed_employees,
                    'total_amount': float(batch.total_amount),
                    'status': batch.status
                }
                
        except Exception as e:
            logger.error(f"Error creating payroll batch: {e}")
            raise ValidationError(f"خطأ في إنشاء دفعة الرواتب: {e}")
    
    def approve_payroll_batch(self, batch_id: str, approved_by_id: str) -> Dict:
        """اعتماد دفعة رواتب"""
        try:
            from ..models import PayrollBatch
            
            with transaction.atomic():
                batch = PayrollBatch.objects.get(id=batch_id)
                
                if batch.status != 'draft':
                    raise ValidationError("لا يمكن اعتماد دفعة رواتب غير مسودة")
                
                # Update batch status
                batch.status = 'approved'
                batch.approved_by_id = approved_by_id
                batch.approved_at = timezone.now()
                batch.save()
                
                # Update all payroll records in batch
                batch.payroll_records.update(
                    status='approved',
                    approved_at=timezone.now()
                )
                
                logger.info(f"Approved payroll batch {batch.name}")
                
                return {
                    'success': True,
                    'batch_id': batch.id,
                    'approved_at': batch.approved_at,
                    'message': f'تم اعتماد دفعة الرواتب {batch.name}'
                }
                
        except PayrollBatch.DoesNotExist:
            raise ValidationError("دفعة الرواتب غير موجودة")
        except Exception as e:
            logger.error(f"Error approving payroll batch: {e}")
            raise ValidationError(f"خطأ في اعتماد دفعة الرواتب: {e}")
    
    def get_payroll_summary(self, year: int, month: int = None, 
                          department_id: str = None) -> Dict:
        """ملخص الرواتب"""
        try:
            from ..models import PayrollRecord, Employee
            
            # Build query
            query = Q(batch__year=year)
            if month:
                query &= Q(batch__month=month)
            if department_id:
                query &= Q(employee__department_id=department_id)
            
            records = PayrollRecord.objects.filter(query).select_related(
                'employee__department', 'batch'
            )
            
            # Calculate summary statistics
            summary = records.aggregate(
                total_employees=Count('id'),
                total_basic_salary=Sum('basic_salary'),
                total_allowances=Sum('total_allowances'),
                total_deductions=Sum('total_deductions'),
                total_gross_salary=Sum('gross_salary'),
                total_net_salary=Sum('net_salary'),
                avg_net_salary=Avg('net_salary')
            )
            
            # Department breakdown
            dept_breakdown = records.values(
                'employee__department__name'
            ).annotate(
                employee_count=Count('id'),
                total_amount=Sum('net_salary'),
                avg_salary=Avg('net_salary')
            ).order_by('-total_amount')
            
            # Monthly breakdown (if year only)
            monthly_breakdown = []
            if not month:
                monthly_data = records.values('batch__month').annotate(
                    employee_count=Count('id'),
                    total_amount=Sum('net_salary')
                ).order_by('batch__month')
                
                for data in monthly_data:
                    monthly_breakdown.append({
                        'month': data['batch__month'],
                        'month_name': calendar.month_name[data['batch__month']],
                        'employee_count': data['employee_count'],
                        'total_amount': float(data['total_amount'] or 0)
                    })
            
            # Convert Decimal to float
            for key, value in summary.items():
                if value is not None:
                    summary[key] = float(value)
                else:
                    summary[key] = 0
            
            return {
                'period': {
                    'year': year,
                    'month': month,
                    'department_id': department_id
                },
                'summary': summary,
                'department_breakdown': list(dept_breakdown),
                'monthly_breakdown': monthly_breakdown,
                'generated_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting payroll summary: {e}")
            raise ValidationError(f"خطأ في جلب ملخص الرواتب: {e}")
    
    # =============================================================================
    # CALCULATION HELPER METHODS
    # =============================================================================
    
    def _calculate_allowances(self, employee) -> Dict:
        """حساب البدلات"""
        allowances = {
            'housing_allowance': 0,
            'transportation_allowance': 0,
            'food_allowance': 0,
            'other_allowances': 0
        }
        
        # Housing allowance (25% of basic salary if eligible)
        if hasattr(employee, 'housing_allowance') and employee.housing_allowance:
            allowances['housing_allowance'] = float(employee.basic_salary * Decimal('0.25'))
        
        # Transportation allowance (fixed amount)
        if hasattr(employee, 'transportation_allowance') and employee.transportation_allowance:
            allowances['transportation_allowance'] = 500.0  # Fixed amount
        
        # Food allowance (fixed amount)
        if hasattr(employee, 'food_allowance') and employee.food_allowance:
            allowances['food_allowance'] = 300.0  # Fixed amount
        
        # Other allowances from employee record
        if hasattr(employee, 'other_allowances') and employee.other_allowances:
            allowances['other_allowances'] = float(employee.other_allowances)
        
        return allowances
    
    def _get_attendance_data(self, employee, start_date, end_date) -> Dict:
        """الحصول على بيانات الحضور"""
        try:
            from ..models import AttendanceSummary
            
            summaries = AttendanceSummary.objects.filter(
                employee=employee,
                date__range=[start_date, end_date]
            )
            
            return {
                'total_work_hours': float(summaries.aggregate(
                    total=Sum('total_work_hours')
                )['total'] or 0),
                'overtime_hours': float(summaries.aggregate(
                    total=Sum('overtime_hours')
                )['total'] or 0),
                'late_minutes': summaries.aggregate(
                    total=Sum('late_minutes')
                )['total'] or 0,
                'absent_days': summaries.filter(is_absent=True).count(),
                'present_days': summaries.filter(is_present=True).count()
            }
            
        except Exception:
            return {
                'total_work_hours': 0,
                'overtime_hours': 0,
                'late_minutes': 0,
                'absent_days': 0,
                'present_days': 0
            }
    
    def _calculate_attendance_based_components(self, employee, attendance_data) -> Dict:
        """حساب المكونات المبنية على الحضور"""
        components = {
            'overtime_amount': 0,
            'late_deductions': 0,
            'absence_deductions': 0,
            'bonus_amount': 0
        }
        
        # Overtime calculation
        overtime_hours = attendance_data['overtime_hours']
        if overtime_hours > 0:
            hourly_rate = employee.basic_salary / Decimal('30') / Decimal('8')  # Monthly to hourly
            overtime_rate = Decimal('1.5')  # 1.5x for overtime
            components['overtime_amount'] = float(hourly_rate * overtime_rate * Decimal(str(overtime_hours)))
        
        # Late deductions (deduct per minute)
        late_minutes = attendance_data['late_minutes']
        if late_minutes > 0:
            minute_rate = employee.basic_salary / Decimal('30') / Decimal('8') / Decimal('60')
            components['late_deductions'] = float(minute_rate * Decimal(str(late_minutes)))
        
        # Absence deductions (deduct per day)
        absent_days = attendance_data['absent_days']
        if absent_days > 0:
            daily_rate = employee.basic_salary / Decimal('30')
            components['absence_deductions'] = float(daily_rate * Decimal(str(absent_days)))
        
        # Perfect attendance bonus
        if attendance_data['absent_days'] == 0 and attendance_data['late_minutes'] == 0:
            components['bonus_amount'] = 200.0  # Fixed bonus amount
        
        return components
    
    def _calculate_statutory_deductions(self, employee, salary_breakdown) -> Dict:
        """حساب الخصومات القانونية"""
        deductions = {
            'social_insurance_employee': 0,
            'income_tax': 0,
            'medical_insurance': 0
        }
        
        gross_salary = Decimal(str(salary_breakdown['totals'].get('gross_salary', 0)))
        if gross_salary == 0:
            # Calculate gross salary if not already calculated
            basic = Decimal(str(salary_breakdown['basic_components']['basic_salary']))
            allowances = sum(Decimal(str(v)) for v in salary_breakdown['basic_components'].values() if v != basic)
            gross_salary = basic + allowances
        
        # Social insurance (employee portion - 9%)
        deductions['social_insurance_employee'] = float(gross_salary * Decimal('0.09'))
        
        # Medical insurance (employee portion - 2%)
        deductions['medical_insurance'] = float(gross_salary * Decimal('0.02'))
        
        # Income tax (progressive rates)
        deductions['income_tax'] = float(self._calculate_income_tax(gross_salary))
        
        return deductions
    
    def _calculate_income_tax(self, gross_salary) -> Decimal:
        """حساب ضريبة الدخل"""
        # Simplified progressive tax calculation
        # This should be based on actual tax brackets
        
        annual_salary = gross_salary * 12
        tax = Decimal('0')
        
        # Tax brackets (example)
        if annual_salary > Decimal('600000'):  # Above 600K annually
            tax = (annual_salary - Decimal('600000')) * Decimal('0.20')
        elif annual_salary > Decimal('300000'):  # 300K - 600K
            tax = (annual_salary - Decimal('300000')) * Decimal('0.15')
        elif annual_salary > Decimal('120000'):  # 120K - 300K
            tax = (annual_salary - Decimal('120000')) * Decimal('0.10')
        # Below 120K is tax-free
        
        # Return monthly tax
        return tax / 12
    
    def _calculate_other_deductions(self, employee, year, month) -> Dict:
        """حساب الخصومات الأخرى"""
        deductions = {
            'loan_deductions': 0,
            'advance_deductions': 0,
            'other': 0
        }
        
        # This would typically come from loan and advance models
        # For now, return zeros
        
        return deductions
    
    def _calculate_salary_totals(self, salary_breakdown) -> Dict:
        """حساب إجماليات الراتب"""
        # Calculate gross salary
        basic_total = sum(salary_breakdown['basic_components'].values())
        attendance_earnings = (
            salary_breakdown['attendance_based']['overtime_amount'] +
            salary_breakdown['attendance_based']['bonus_amount']
        )
        gross_salary = basic_total + attendance_earnings
        
        # Calculate total allowances
        total_allowances = sum([
            salary_breakdown['basic_components']['housing_allowance'],
            salary_breakdown['basic_components']['transportation_allowance'],
            salary_breakdown['basic_components']['food_allowance'],
            salary_breakdown['basic_components']['other_allowances']
        ])
        
        # Calculate total deductions
        total_deductions = (
            sum(salary_breakdown['statutory_deductions'].values()) +
            sum(salary_breakdown['other_deductions'].values()) +
            salary_breakdown['attendance_based']['late_deductions'] +
            salary_breakdown['attendance_based']['absence_deductions']
        )
        
        # Calculate net salary
        net_salary = gross_salary - total_deductions
        
        return {
            'gross_salary': gross_salary,
            'total_allowances': total_allowances,
            'total_deductions': total_deductions,
            'net_salary': net_salary
        }
    
    def _round_salary_values(self, salary_breakdown) -> Dict:
        """تقريب قيم الراتب"""
        def round_dict_values(d):
            for key, value in d.items():
                if isinstance(value, (int, float)):
                    d[key] = float(Decimal(str(value)).quantize(self.rounding_precision, rounding=ROUND_HALF_UP))
                elif isinstance(value, dict):
                    d[key] = round_dict_values(value)
            return d
        
        return round_dict_values(salary_breakdown)
    
    def _get_working_days(self, start_date, end_date) -> int:
        """حساب أيام العمل في الفترة"""
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Skip Fridays and Saturdays (weekend)
            if current_date.weekday() not in [4, 5]:  # Friday=4, Saturday=5
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
    
    def _save_payroll_record(self, employee_id, year, month, salary_data):
        """حفظ سجل الراتب"""
        try:
            from ..models import PayrollRecord
            
            # This would save the payroll record to database
            # Implementation depends on your PayrollRecord model
            pass
            
        except Exception as e:
            logger.error(f"Error saving payroll record: {e}")
    
    # =============================================================================
    # REPORT GENERATION METHODS
    # =============================================================================
    
    def _generate_pdf_payslip(self, salary_data) -> bytes:
        """إنتاج كشف راتب PDF"""
        # This would use a PDF library like ReportLab
        # For now, return empty bytes
        return b''
    
    def _generate_html_payslip(self, salary_data) -> str:
        """إنتاج كشف راتب HTML"""
        # This would generate HTML payslip
        # For now, return empty string
        return ''