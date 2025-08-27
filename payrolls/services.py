"""
خدمات نظام المرتبات المتقدمة
===========================

يحتوي هذا الملف على جميع خدمات حساب الرواتب والتكامل مع أنظمة الحضور والإجازات
"""

from django.db import transaction
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange
import logging

from .models import (
    EmployeeSalary, PayrollRun, PayrollDetail, 
    PayrollBonus, PayrollDeduction, PayrollCalculationRule
)
from employees.models import Employee
from attendance.models import EmployeeAttendance, AttendanceSummary
from leaves.models import EmployeeLeave, LeaveBalance, LeaveType
from loans.models import EmployeeLoan, LoanInstallment

logger = logging.getLogger(__name__)


class PayrollCalculationService:
    """خدمة حساب الرواتب المتقدمة"""
    
    def __init__(self):
        self.working_days_per_month = 22  # الافتراضي: 22 يوم عمل في الشهر
        self.working_hours_per_day = 8    # الافتراضي: 8 ساعات عمل يومياً
    
    def calculate_employee_payroll(self, employee, payroll_run):
        """
        حساب راتب موظف محدد لفترة معينة
        
        Args:
            employee: كائن الموظف
            payroll_run: كائن تشغيل الرواتب
            
        Returns:
            PayrollDetail: كائن تفاصيل الراتب المحسوب
        """
        try:
            # الحصول على راتب الموظف الحالي
            employee_salary = self._get_employee_current_salary(employee, payroll_run.period_end)
            
            if not employee_salary:
                logger.warning(f"No active salary found for employee {employee.emp_code}")
                return None
            
            # حساب بيانات الحضور للفترة
            attendance_data = self._calculate_attendance_data(employee, payroll_run)
            
            # حساب بيانات الإجازات للفترة
            leave_data = self._calculate_leave_data(employee, payroll_run)
            
            # حساب الوقت الإضافي
            overtime_data = self._calculate_overtime(employee, payroll_run, attendance_data)
            
            # حساب المكافآت
            bonus_data = self._calculate_bonuses(employee, payroll_run)
            
            # حساب الخصومات
            deduction_data = self._calculate_deductions(employee, payroll_run, attendance_data, leave_data)
            
            # حساب أقساط القروض
            loan_data = self._calculate_loan_installments(employee, payroll_run)
            
            # إنشاء كائن تفاصيل الراتب
            payroll_detail = self._create_payroll_detail(
                employee, payroll_run, employee_salary,
                attendance_data, leave_data, overtime_data,
                bonus_data, deduction_data, loan_data
            )
            
            return payroll_detail
            
        except Exception as e:
            logger.error(f"Error calculating payroll for employee {employee.emp_code}: {str(e)}")
            raise
    
    def _get_employee_current_salary(self, employee, as_of_date):
        """الحصول على راتب الموظف الساري في تاريخ محدد"""
        return EmployeeSalary.objects.filter(
            emp=employee,
            effective_date__lte=as_of_date,
            is_current=True
        ).order_by('-effective_date').first()
    
    def _calculate_attendance_data(self, employee, payroll_run):
        """حساب بيانات الحضور للموظف في الفترة المحددة"""
        attendance_records = EmployeeAttendance.objects.filter(
            emp=employee,
            att_date__range=[payroll_run.period_start, payroll_run.period_end]
        )
        
        # حساب أيام العمل الفعلية
        worked_days = attendance_records.filter(
            status__in=['Present', 'Late']
        ).count()
        
        # حساب أيام الغياب
        absent_days = attendance_records.filter(status='Absent').count()
        
        # حساب دقائق التأخير الإجمالية
        total_late_minutes = 0
        for record in attendance_records.filter(status='Late'):
            if hasattr(record, 'calculate_late_minutes'):
                total_late_minutes += record.calculate_late_minutes()
        
        # حساب ساعات العمل الإجمالية
        total_work_hours = 0
        for record in attendance_records.filter(check_in__isnull=False, check_out__isnull=False):
            work_minutes = record.calculate_work_minutes()
            total_work_hours += work_minutes / 60
        
        # حساب أيام العمل المتوقعة في الفترة
        expected_work_days = self._calculate_expected_work_days(
            payroll_run.period_start, 
            payroll_run.period_end
        )
        
        return {
            'worked_days': worked_days,
            'absent_days': absent_days,
            'expected_work_days': expected_work_days,
            'attendance_rate': (worked_days / expected_work_days * 100) if expected_work_days > 0 else 0,
            'total_late_minutes': total_late_minutes,
            'total_work_hours': total_work_hours,
            'average_daily_hours': total_work_hours / worked_days if worked_days > 0 else 0
        }
    
    def _calculate_leave_data(self, employee, payroll_run):
        """حساب بيانات الإجازات للموظف في الفترة المحددة"""
        leave_records = EmployeeLeave.objects.filter(
            emp=employee,
            status='Approved',
            start_date__lte=payroll_run.period_end,
            end_date__gte=payroll_run.period_start
        )
        
        paid_leave_days = 0
        unpaid_leave_days = 0
        
        for leave in leave_records:
            # حساب الأيام المتداخلة مع فترة الراتب
            leave_start = max(leave.start_date, payroll_run.period_start)
            leave_end = min(leave.end_date, payroll_run.period_end)
            
            if leave_start <= leave_end:
                leave_days = (leave_end - leave_start).days + 1
                
                if leave.leave_type.is_paid:
                    paid_leave_days += leave_days
                else:
                    unpaid_leave_days += leave_days
        
        return {
            'total_leave_days': paid_leave_days + unpaid_leave_days,
            'paid_leave_days': paid_leave_days,
            'unpaid_leave_days': unpaid_leave_days,
            'leave_records': leave_records
        }
    
    def _calculate_overtime(self, employee, payroll_run, attendance_data):
        """حساب الوقت الإضافي"""
        overtime_hours = 0
        overtime_amount = Decimal('0.00')
        
        # الحصول على راتب الموظف لحساب سعر الساعة
        employee_salary = self._get_employee_current_salary(employee, payroll_run.period_end)
        
        if employee_salary and attendance_data['total_work_hours'] > 0:
            # حساب الساعات الإضافية (أكثر من 8 ساعات يومياً)
            expected_daily_hours = self.working_hours_per_day
            daily_records = EmployeeAttendance.objects.filter(
                emp=employee,
                att_date__range=[payroll_run.period_start, payroll_run.period_end],
                check_in__isnull=False,
                check_out__isnull=False
            )
            
            for record in daily_records:
                daily_hours = record.calculate_work_minutes() / 60
                if daily_hours > expected_daily_hours:
                    overtime_hours += daily_hours - expected_daily_hours
            
            # حساب مبلغ الوقت الإضافي
            if overtime_hours > 0:
                hourly_rate = employee_salary.calculate_hourly_rate()
                overtime_rate = employee_salary.overtime_rate or Decimal('1.5')
                overtime_amount = Decimal(str(overtime_hours)) * hourly_rate * overtime_rate
        
        return {
            'overtime_hours': overtime_hours,
            'overtime_amount': overtime_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        }
    
    def _calculate_bonuses(self, employee, payroll_run):
        """حساب المكافآت للفترة المحددة"""
        bonuses = PayrollBonus.objects.filter(
            employee=employee,
            effective_date__range=[payroll_run.period_start, payroll_run.period_end],
            is_active=True
        )
        
        total_bonus_amount = bonuses.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        return {
            'bonus_records': bonuses,
            'total_bonus_amount': total_bonus_amount
        }
    
    def _calculate_deductions(self, employee, payroll_run, attendance_data, leave_data):
        """حساب الخصومات"""
        deductions = {}
        
        # خصومات ثابتة (التأمينات، الضرائب، إلخ)
        employee_salary = self._get_employee_current_salary(employee, payroll_run.period_end)
        if employee_salary:
            deductions['gosi'] = employee_salary.gosi_deduction or Decimal('0.00')
            deductions['tax'] = employee_salary.tax_deduction or Decimal('0.00')
            deductions['insurance'] = employee_salary.insurance_deduction or Decimal('0.00')
            deductions['other'] = employee_salary.other_deduction or Decimal('0.00')
        
        # خصم الغياب
        absence_deduction = Decimal('0.00')
        if employee_salary and employee_salary.deduct_absent_days and attendance_data['absent_days'] > 0:
            daily_rate = employee_salary.calculate_daily_rate()
            absence_deduction = Decimal(str(attendance_data['absent_days'])) * daily_rate
        
        # خصم الإجازات غير مدفوعة الأجر
        unpaid_leave_deduction = Decimal('0.00')
        if employee_salary and employee_salary.deduct_unpaid_leave and leave_data['unpaid_leave_days'] > 0:
            daily_rate = employee_salary.calculate_daily_rate()
            unpaid_leave_deduction = Decimal(str(leave_data['unpaid_leave_days'])) * daily_rate
        
        # خصم التأخير
        late_deduction = Decimal('0.00')
        if employee_salary and employee_salary.deduct_late_minutes and attendance_data['total_late_minutes'] > 0:
            hourly_rate = employee_salary.calculate_hourly_rate()
            late_hours = Decimal(str(attendance_data['total_late_minutes'])) / 60
            late_deduction = late_hours * hourly_rate
        
        # خصومات إضافية
        additional_deductions = PayrollDeduction.objects.filter(
            employee=employee,
            effective_date__lte=payroll_run.period_end,
            is_active=True
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=payroll_run.period_start)
        )
        
        additional_deduction_amount = additional_deductions.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        deductions.update({
            'absence_deduction': absence_deduction,
            'unpaid_leave_deduction': unpaid_leave_deduction,
            'late_deduction': late_deduction,
            'additional_deductions': additional_deduction_amount,
            'deduction_records': additional_deductions
        })
        
        return deductions
    
    def _calculate_loan_installments(self, employee, payroll_run):
        """حساب أقساط القروض المستحقة"""
        # البحث عن الأقساط المستحقة في فترة الراتب
        due_installments = LoanInstallment.objects.filter(
            loan__emp=employee,
            due_date__range=[payroll_run.period_start, payroll_run.period_end],
            status='pending'
        )
        
        total_installment_amount = due_installments.aggregate(
            total=Sum('installment_amount')
        )['total'] or Decimal('0.00')
        
        return {
            'installment_records': due_installments,
            'total_installment_amount': total_installment_amount
        }
    
    def _create_payroll_detail(self, employee, payroll_run, employee_salary, 
                             attendance_data, leave_data, overtime_data, 
                             bonus_data, deduction_data, loan_data):
        """إنشاء كائن تفاصيل الراتب"""
        
        # حساب الراتب الأساسي المتناسب مع أيام العمل
        basic_salary_amount = self._calculate_prorated_salary(
            employee_salary.basic_salary,
            attendance_data['worked_days'],
            attendance_data['expected_work_days']
        )
        
        # حساب البدلات
        housing_allowance = self._calculate_prorated_salary(
            employee_salary.housing_allow,
            attendance_data['worked_days'],
            attendance_data['expected_work_days']
        )
        
        transport_allowance = self._calculate_prorated_salary(
            employee_salary.transport_allow,
            attendance_data['worked_days'],
            attendance_data['expected_work_days']
        )
        
        food_allowance = self._calculate_prorated_salary(
            employee_salary.food_allow,
            attendance_data['worked_days'],
            attendance_data['expected_work_days']
        )
        
        mobile_allowance = self._calculate_prorated_salary(
            employee_salary.mobile_allow,
            attendance_data['worked_days'],
            attendance_data['expected_work_days']
        )
        
        other_allowances = self._calculate_prorated_salary(
            employee_salary.other_allow,
            attendance_data['worked_days'],
            attendance_data['expected_work_days']
        )
        
        # إنشاء أو تحديث سجل تفاصيل الراتب
        payroll_detail, created = PayrollDetail.objects.update_or_create(
            run=payroll_run,
            emp=employee,
            defaults={
                'basic_salary': basic_salary_amount,
                'housing_allowance': housing_allowance,
                'transport_allowance': transport_allowance,
                'food_allowance': food_allowance,
                'mobile_allowance': mobile_allowance,
                'other_allowances': other_allowances,
                
                # الوقت الإضافي والمكافآت
                'overtime_hours': overtime_data['overtime_hours'],
                'overtime_amount': overtime_data['overtime_amount'],
                'bonus_amount': bonus_data['total_bonus_amount'],
                
                # بيانات الحضور
                'worked_days': attendance_data['worked_days'],
                'absent_days': attendance_data['absent_days'],
                'leave_days': leave_data['total_leave_days'],
                'late_minutes': attendance_data['total_late_minutes'],
                
                # الخصومات
                'gosi_deduction': deduction_data.get('gosi', Decimal('0.00')),
                'tax_deduction': deduction_data.get('tax', Decimal('0.00')),
                'insurance_deduction': deduction_data.get('insurance', Decimal('0.00')),
                'loan_deduction': loan_data['total_installment_amount'],
                'absence_deduction': deduction_data['absence_deduction'],
                'late_deduction': deduction_data['late_deduction'],
                'other_deductions': (
                    deduction_data['unpaid_leave_deduction'] + 
                    deduction_data['additional_deductions'] +
                    deduction_data.get('other', Decimal('0.00'))
                ),
                
                # ملاحظات الحساب
                'calculation_notes': self._generate_calculation_notes(
                    attendance_data, leave_data, overtime_data, 
                    bonus_data, deduction_data, loan_data
                ),
                
                'is_processed': True
            }
        )
        
        # تحديث حالة أقساط القروض المدفوعة
        if loan_data['installment_records'].exists():
            loan_data['installment_records'].update(status='paid')
        
        return payroll_detail
    
    def _calculate_prorated_salary(self, full_amount, worked_days, expected_days):
        """حساب الراتب المتناسب مع أيام العمل الفعلية"""
        if expected_days <= 0:
            return Decimal('0.00')
        
        proration_factor = Decimal(str(worked_days)) / Decimal(str(expected_days))
        prorated_amount = full_amount * proration_factor
        
        return prorated_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _calculate_expected_work_days(self, start_date, end_date):
        """حساب أيام العمل المتوقعة في فترة معينة (باستثناء عطل نهاية الأسبوع)"""
        work_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # إذا لم يكن يوم جمعة (4) أو سبت (5)
            if current_date.weekday() not in [4, 5]:  # الجمعة=4, السبت=5
                work_days += 1
            current_date += timedelta(days=1)
        
        return work_days
    
    def _generate_calculation_notes(self, attendance_data, leave_data, overtime_data, 
                                  bonus_data, deduction_data, loan_data):
        """إنشاء ملاحظات توضيحية لحساب الراتب"""
        notes = []
        
        # ملاحظات الحضور
        if attendance_data['absent_days'] > 0:
            notes.append(f"أيام غياب: {attendance_data['absent_days']}")
        
        if attendance_data['total_late_minutes'] > 0:
            notes.append(f"دقائق تأخير: {attendance_data['total_late_minutes']}")
        
        # ملاحظات الإجازات
        if leave_data['unpaid_leave_days'] > 0:
            notes.append(f"إجازات غير مدفوعة: {leave_data['unpaid_leave_days']} أيام")
        
        # ملاحظات الوقت الإضافي
        if overtime_data['overtime_hours'] > 0:
            notes.append(f"ساعات إضافية: {overtime_data['overtime_hours']:.2f}")
        
        # ملاحظات المكافآت
        if bonus_data['total_bonus_amount'] > 0:
            notes.append(f"مكافآت: {bonus_data['total_bonus_amount']}")
        
        # ملاحظات القروض
        if loan_data['total_installment_amount'] > 0:
            notes.append(f"أقساط قروض: {loan_data['total_installment_amount']}")
        
        return " | ".join(notes) if notes else "حساب اعتيادي"


class PayrollRunService:
    """خدمة إدارة تشغيلات الرواتب"""
    
    def __init__(self):
        self.calculation_service = PayrollCalculationService()
    
    @transaction.atomic
    def create_payroll_run(self, month_year, payroll_type='monthly', created_by=None):
        """إنشاء تشغيل رواتب جديد"""
        try:
            # تحليل month_year لاستخراج الشهر والسنة
            year, month = map(int, month_year.split('-'))
            
            # حساب فترة الراتب
            period_start = date(year, month, 1)
            _, last_day = monthrange(year, month)
            period_end = date(year, month, last_day)
            
            # التحقق من عدم وجود تشغيل راتب آخر لنفس الفترة
            existing_run = PayrollRun.objects.filter(
                month_year=month_year,
                status__in=['draft', 'calculating', 'review', 'approved']
            ).first()
            
            if existing_run:
                raise ValueError(f"يوجد تشغيل راتب آخر لشهر {month_year}")
            
            # إنشاء تشغيل الراتب
            payroll_run = PayrollRun.objects.create(
                payroll_type=payroll_type,
                period_start=period_start,
                period_end=period_end,
                month_year=month_year,
                status='draft',
                created_by=created_by
            )
            
            return payroll_run
            
        except Exception as e:
            logger.error(f"Error creating payroll run: {str(e)}")
            raise
    
    @transaction.atomic
    def process_payroll_run(self, payroll_run, employee_filter=None):
        """معالجة تشغيل الرواتب"""
        try:
            if payroll_run.status != 'draft':
                raise ValueError("يمكن معالجة تشغيلات الرواتب في حالة المسودة فقط")
            
            # تحديث حالة التشغيل
            payroll_run.start_calculation()
            
            # الحصول على قائمة الموظفين
            employees = Employee.objects.filter(emp_status='Active')
            
            # تطبيق فلتر إضافي إذا تم تحديده
            if employee_filter:
                employees = employees.filter(**employee_filter)
            
            # تحديث إجمالي الموظفين
            payroll_run.total_employees = employees.count()
            payroll_run.save()
            
            processed_count = 0
            errors = []
            
            # معالجة كل موظف
            for employee in employees:
                try:
                    # تجاهل الموظفين الذين ليس لديهم راتب ساري
                    current_salary = self.calculation_service._get_employee_current_salary(
                        employee, payroll_run.period_end
                    )
                    
                    if not current_salary:
                        logger.warning(f"Employee {employee.emp_code} has no active salary")
                        continue
                    
                    # حساب راتب الموظف
                    payroll_detail = self.calculation_service.calculate_employee_payroll(
                        employee, payroll_run
                    )
                    
                    if payroll_detail:
                        processed_count += 1
                        
                        # تحديث تقدم المعالجة
                        payroll_run.processed_employees = processed_count
                        payroll_run.save()
                        
                except Exception as e:
                    error_msg = f"Error processing employee {employee.emp_code}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # إنهاء عملية الحساب
            payroll_run.complete_calculation()
            
            return {
                'success': True,
                'processed_employees': processed_count,
                'total_employees': payroll_run.total_employees,
                'errors': errors
            }
            
        except Exception as e:
            # في حالة حدوث خطأ، إعادة التشغيل إلى حالة المسودة
            payroll_run.status = 'draft'
            payroll_run.save()
            
            error_msg = f"Error processing payroll run: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def approve_payroll_run(self, payroll_run, approved_by):
        """اعتماد تشغيل الرواتب"""
        if payroll_run.status != 'review':
            raise ValueError("يمكن اعتماد تشغيلات الرواتب في حالة المراجعة فقط")
        
        payroll_run.approve(approved_by)
        return True
    
    def mark_payroll_as_paid(self, payroll_run, confirmed_by):
        """تحديد تشغيل الرواتب كمدفوع"""
        if payroll_run.status != 'approved':
            raise ValueError("يمكن تحديد تشغيلات الرواتب المعتمدة فقط كمدفوعة")
        
        payroll_run.mark_as_paid(confirmed_by)
        return True
    
    def cancel_payroll_run(self, payroll_run):
        """إلغاء تشغيل الرواتب"""
        if payroll_run.status not in ['draft', 'calculating', 'review']:
            raise ValueError("لا يمكن إلغاء تشغيل الرواتب في هذه الحالة")
        
        # حذف تفاصيل الرواتب المرتبطة
        PayrollDetail.objects.filter(run=payroll_run).delete()
        
        payroll_run.cancel()
        return True


class PayrollReportService:
    """خدمة تقارير الرواتب"""
    
    def generate_payroll_summary_report(self, payroll_run):
        """إنشاء تقرير ملخص الرواتب"""
        details = PayrollDetail.objects.filter(run=payroll_run)
        
        summary = details.aggregate(
            total_employees=Count('payroll_detail_id'),
            total_basic_salary=Sum('basic_salary'),
            total_allowances=Sum('total_allowances'),
            total_overtime=Sum('overtime_amount'),
            total_bonuses=Sum('bonus_amount'),
            total_gross=Sum('gross_salary'),
            total_deductions=Sum('total_deductions'),
            total_net=Sum('net_salary'),
            avg_salary=Avg('net_salary')
        )
        
        return summary
    
    def generate_employee_payslip(self, payroll_detail):
        """إنشاء كشف راتب الموظف"""
        return {
            'employee': payroll_detail.emp,
            'payroll_run': payroll_detail.run,
            'earnings': {
                'basic_salary': payroll_detail.basic_salary,
                'housing_allowance': payroll_detail.housing_allowance,
                'transport_allowance': payroll_detail.transport_allowance,
                'food_allowance': payroll_detail.food_allowance,
                'mobile_allowance': payroll_detail.mobile_allowance,
                'other_allowances': payroll_detail.other_allowances,
                'overtime_amount': payroll_detail.overtime_amount,
                'bonus_amount': payroll_detail.bonus_amount,
                'total_earnings': payroll_detail.gross_salary
            },
            'deductions': {
                'gosi_deduction': payroll_detail.gosi_deduction,
                'tax_deduction': payroll_detail.tax_deduction,
                'insurance_deduction': payroll_detail.insurance_deduction,
                'loan_deduction': payroll_detail.loan_deduction,
                'absence_deduction': payroll_detail.absence_deduction,
                'late_deduction': payroll_detail.late_deduction,
                'other_deductions': payroll_detail.other_deductions,
                'total_deductions': payroll_detail.total_deductions
            },
            'attendance': {
                'worked_days': payroll_detail.worked_days,
                'absent_days': payroll_detail.absent_days,
                'leave_days': payroll_detail.leave_days,
                'late_minutes': payroll_detail.late_minutes,
                'overtime_hours': payroll_detail.overtime_hours
            },
            'net_salary': payroll_detail.net_salary,
            'calculation_notes': payroll_detail.calculation_notes
        }