# -*- coding: utf-8 -*-
"""
Payroll Service for HRMS
Handles payroll business logic and operations
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, Sum, Count
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from Hr.models import (
    Employee, SalaryComponent, PayrollPeriod, 
    EmployeeSalaryStructure, EmployeeSalaryComponent,
    AttendanceSummary
)

logger = logging.getLogger(__name__)


class PayrollService:
    """
    خدمة إدارة الرواتب - تحتوي على منطق العمل الخاص بالرواتب والكشوفات
    """
    
    @staticmethod
    def create_salary_structure(employee_id, structure_data, created_by=None):
        """
        إنشاء هيكل راتب جديد للموظف
        """
        try:
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                
                # إلغاء تفعيل الهياكل الحالية
                EmployeeSalaryStructure.objects.filter(
                    employee=employee,
                    is_current=True
                ).update(is_current=False)
                
                # إنشاء الهيكل الجديد
                salary_structure = EmployeeSalaryStructure.objects.create(
                    employee=employee,
                    structure_name=structure_data.get('structure_name'),
                    basic_salary=structure_data.get('basic_salary'),
                    effective_from=structure_data.get('effective_from', date.today()),
                    currency=structure_data.get('currency', 'EGP'),
                    is_current=True,
                    created_by=created_by
                )
                
                # إضافة مكونات الراتب
                components = structure_data.get('components', [])
                for component_data in components:
                    EmployeeSalaryComponent.objects.create(
                        salary_structure=salary_structure,
                        salary_component_id=component_data['component_id'],
                        amount=component_data['amount'],
                        override_calculation=component_data.get('override_calculation', False)
                    )
                
                # حساب الإجماليات
                salary_structure.calculate_totals()
                salary_structure.save()
                
                logger.info(f"تم إنشاء هيكل راتب جديد للموظف: {employee.full_name}")
                return salary_structure
                
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"خطأ في إنشاء هيكل الراتب: {str(e)}")
            raise
    
    @staticmethod
    def calculate_employee_payroll(employee_id, payroll_period_id):
        """
        حساب راتب الموظف لفترة معينة
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            payroll_period = PayrollPeriod.objects.get(id=payroll_period_id)
            
            # الحصول على هيكل الراتب الحالي
            salary_structure = EmployeeSalaryStructure.objects.filter(
                employee=employee,
                is_current=True,
                effective_from__lte=payroll_period.end_date
            ).first()
            
            if not salary_structure:
                raise ValidationError("لا يوجد هيكل راتب للموظف")
            
            # حساب بيانات الحضور للفترة
            attendance_data = PayrollService._calculate_attendance_data(
                employee, payroll_period.start_date, payroll_period.end_date
            )
            
            # حساب مكونات الراتب
            earnings = Decimal('0')
            deductions = Decimal('0')
            
            base_values = {
                'basic_salary': salary_structure.basic_salary,
                'attendance_days': attendance_data['working_days'],
                'working_hours': attendance_data['total_hours'],
                'overtime_hours': attendance_data['overtime_hours']
            }
            
            payroll_components = []
            
            for salary_component in salary_structure.salary_components.filter(is_active=True):
                component = salary_component.salary_component
                
                # حساب مبلغ المكون
                if salary_component.override_calculation:
                    amount = salary_component.amount
                else:
                    amount = component.calculate_amount(employee, payroll_period, base_values)
                
                payroll_components.append({
                    'component': component,
                    'amount': amount,
                    'is_earning': component.is_earning,
                    'is_deduction': component.is_deduction
                })
                
                if component.is_earning:
                    earnings += amount
                elif component.is_deduction:
                    deductions += amount
                
                # تحديث base_values للمكونات التالية
                base_values[f'component_{component.code}'] = amount
                base_values['gross_salary'] = earnings
                base_values['total_earnings'] = earnings
            
            net_salary = earnings - deductions
            
            payroll_data = {
                'employee': employee,
                'payroll_period': payroll_period,
                'salary_structure': salary_structure,
                'basic_salary': salary_structure.basic_salary,
                'total_earnings': earnings,
                'total_deductions': deductions,
                'net_salary': net_salary,
                'components': payroll_components,
                'attendance_data': attendance_data
            }
            
            logger.info(f"تم حساب راتب الموظف: {employee.full_name} للفترة {payroll_period.name}")
            return payroll_data
            
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except PayrollPeriod.DoesNotExist:
            raise ValidationError("فترة الراتب غير موجودة")
        except Exception as e:
            logger.error(f"خطأ في حساب الراتب: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_attendance_data(employee, start_date, end_date):
        """
        حساب بيانات الحضور للموظف خلال فترة معينة
        """
        summaries = AttendanceSummary.objects.filter(
            employee=employee,
            date__range=[start_date, end_date]
        )
        
        total_days = (end_date - start_date).days + 1
        working_days = summaries.filter(status__in=['present', 'late']).count()
        absent_days = summaries.filter(status='absent').count()
        late_days = summaries.filter(status='late').count()
        
        total_hours = sum(float(s.total_hours) for s in summaries)
        regular_hours = sum(float(s.regular_hours) for s in summaries)
        overtime_hours = sum(float(s.overtime_hours) for s in summaries)
        total_late_minutes = sum(s.late_minutes for s in summaries)
        
        return {
            'total_days': total_days,
            'working_days': working_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'total_hours': total_hours,
            'regular_hours': regular_hours,
            'overtime_hours': overtime_hours,
            'total_late_minutes': total_late_minutes,
            'attendance_rate': round((working_days / total_days) * 100, 2) if total_days > 0 else 0
        }
    
    @staticmethod
    def process_payroll_period(payroll_period_id, processed_by=None):
        """
        معالجة فترة الراتب لجميع الموظفين
        """
        try:
            with transaction.atomic():
                payroll_period = PayrollPeriod.objects.get(id=payroll_period_id)
                
                if not payroll_period.can_be_processed():
                    raise ValidationError("لا يمكن معالجة هذه الفترة")
                
                # تحديث حالة الفترة
                payroll_period.status = 'processing'
                payroll_period.save()
                
                # الحصول على الموظفين النشطين
                employees = Employee.objects.filter(
                    is_active=True,
                    hire_date__lte=payroll_period.end_date
                )
                
                processed_count = 0
                total_gross = Decimal('0')
                total_deductions = Decimal('0')
                total_net = Decimal('0')
                
                for employee in employees:
                    try:
                        payroll_data = PayrollService.calculate_employee_payroll(
                            employee.id, payroll_period_id
                        )
                        
                        # هنا يمكن حفظ بيانات كشف الراتب في جدول منفصل
                        # PayrollEntry.objects.create(...)
                        
                        processed_count += 1
                        total_gross += payroll_data['total_earnings']
                        total_deductions += payroll_data['total_deductions']
                        total_net += payroll_data['net_salary']
                        
                    except Exception as e:
                        logger.error(f"خطأ في معالجة راتب الموظف {employee.full_name}: {str(e)}")
                        continue
                
                # تحديث إجماليات الفترة
                payroll_period.total_employees = processed_count
                payroll_period.total_gross_salary = total_gross
                payroll_period.total_deductions = total_deductions
                payroll_period.total_net_salary = total_net
                payroll_period.status = 'completed'
                payroll_period.processed_at = timezone.now()
                payroll_period.save()
                
                logger.info(f"تم معالجة فترة الراتب: {payroll_period.name} لـ {processed_count} موظف")
                return {
                    'processed_count': processed_count,
                    'total_gross': total_gross,
                    'total_deductions': total_deductions,
                    'total_net': total_net
                }
                
        except PayrollPeriod.DoesNotExist:
            raise ValidationError("فترة الراتب غير موجودة")
        except Exception as e:
            logger.error(f"خطأ في معالجة فترة الراتب: {str(e)}")
            # إعادة تعيين حالة الفترة في حالة الخطأ
            try:
                payroll_period.status = 'active'
                payroll_period.save()
            except:
                pass
            raise
    
    @staticmethod
    def create_payroll_period(period_data, created_by=None):
        """
        إنشاء فترة راتب جديدة
        """
        try:
            with transaction.atomic():
                # التحقق من عدم تداخل الفترات
                overlapping_periods = PayrollPeriod.objects.filter(
                    period_type=period_data.get('period_type', 'monthly'),
                    is_active=True
                ).filter(
                    Q(start_date__lte=period_data['end_date']) &
                    Q(end_date__gte=period_data['start_date'])
                )
                
                if overlapping_periods.exists():
                    raise ValidationError("توجد فترة راتب متداخلة مع هذه الفترة")
                
                payroll_period = PayrollPeriod.objects.create(
                    name=period_data['name'],
                    name_en=period_data.get('name_en', ''),
                    period_type=period_data.get('period_type', 'monthly'),
                    start_date=period_data['start_date'],
                    end_date=period_data['end_date'],
                    pay_date=period_data['pay_date'],
                    notes=period_data.get('notes', ''),
                    created_by=created_by
                )
                
                logger.info(f"تم إنشاء فترة راتب جديدة: {payroll_period.name}")
                return payroll_period
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء فترة الراتب: {str(e)}")
            raise
    
    @staticmethod
    def get_employee_payroll_history(employee_id, limit=12):
        """
        الحصول على تاريخ رواتب الموظف
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # هنا سيتم الحصول على سجلات كشوف الرواتب من جدول منفصل
            # payroll_entries = PayrollEntry.objects.filter(employee=employee).order_by('-period__start_date')[:limit]
            
            # مؤقتاً، سنحصل على فترات الرواتب المكتملة
            completed_periods = PayrollPeriod.objects.filter(
                status='completed',
                start_date__lte=employee.hire_date if employee.hire_date else date.today()
            ).order_by('-start_date')[:limit]
            
            payroll_history = []
            for period in completed_periods:
                try:
                    payroll_data = PayrollService.calculate_employee_payroll(
                        employee_id, period.id
                    )
                    payroll_history.append(payroll_data)
                except Exception as e:
                    logger.warning(f"خطأ في حساب راتب الموظف للفترة {period.name}: {str(e)}")
                    continue
            
            return payroll_history
            
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"خطأ في الحصول على تاريخ الرواتب: {str(e)}")
            raise
    
    @staticmethod
    def get_payroll_statistics(payroll_period_id=None):
        """
        الحصول على إحصائيات الرواتب
        """
        try:
            if payroll_period_id:
                # إحصائيات فترة معينة
                payroll_period = PayrollPeriod.objects.get(id=payroll_period_id)
                
                stats = {
                    'period_name': payroll_period.name,
                    'total_employees': payroll_period.total_employees,
                    'total_gross_salary': float(payroll_period.total_gross_salary),
                    'total_deductions': float(payroll_period.total_deductions),
                    'total_net_salary': float(payroll_period.total_net_salary),
                    'average_salary': float(payroll_period.total_net_salary / payroll_period.total_employees) if payroll_period.total_employees > 0 else 0,
                    'status': payroll_period.status
                }
            else:
                # إحصائيات عامة
                current_year = date.today().year
                completed_periods = PayrollPeriod.objects.filter(
                    status='completed',
                    start_date__year=current_year
                )
                
                total_periods = completed_periods.count()
                total_gross = sum(float(p.total_gross_salary) for p in completed_periods)
                total_deductions = sum(float(p.total_deductions) for p in completed_periods)
                total_net = sum(float(p.total_net_salary) for p in completed_periods)
                
                stats = {
                    'current_year': current_year,
                    'total_periods_processed': total_periods,
                    'total_gross_salary': total_gross,
                    'total_deductions': total_deductions,
                    'total_net_salary': total_net,
                    'average_monthly_payroll': total_net / total_periods if total_periods > 0 else 0
                }
            
            return stats
            
        except PayrollPeriod.DoesNotExist:
            raise ValidationError("فترة الراتب غير موجودة")
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات الرواتب: {str(e)}")
            raise
    
    @staticmethod
    def bulk_update_salary_components(updates, updated_by=None):
        """
        تحديث مجمع لمكونات الرواتب
        """
        try:
            with transaction.atomic():
                updated_count = 0
                
                for component_id, update_data in updates.items():
                    try:
                        component = SalaryComponent.objects.get(id=component_id)
                        
                        for field, value in update_data.items():
                            if hasattr(component, field):
                                setattr(component, field, value)
                        
                        component.save()
                        updated_count += 1
                        
                    except SalaryComponent.DoesNotExist:
                        logger.warning(f"مكون الراتب غير موجود: {component_id}")
                        continue
                
                logger.info(f"تم تحديث {updated_count} مكون راتب بنجاح")
                return updated_count
                
        except Exception as e:
            logger.error(f"خطأ في التحديث المجمع لمكونات الراتب: {str(e)}")
            raise
    
    @staticmethod
    def generate_payslip_data(employee_id, payroll_period_id):
        """
        إنتاج بيانات كشف الراتب للطباعة
        """
        try:
            payroll_data = PayrollService.calculate_employee_payroll(
                employee_id, payroll_period_id
            )
            
            # تنسيق البيانات لكشف الراتب
            payslip_data = {
                'employee': payroll_data['employee'],
                'period': payroll_data['payroll_period'],
                'basic_salary': payroll_data['basic_salary'],
                'earnings': [c for c in payroll_data['components'] if c['is_earning']],
                'deductions': [c for c in payroll_data['components'] if c['is_deduction']],
                'total_earnings': payroll_data['total_earnings'],
                'total_deductions': payroll_data['total_deductions'],
                'net_salary': payroll_data['net_salary'],
                'attendance_summary': payroll_data['attendance_data'],
                'generated_at': timezone.now()
            }
            
            return payslip_data
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج كشف الراتب: {str(e)}")
            raise