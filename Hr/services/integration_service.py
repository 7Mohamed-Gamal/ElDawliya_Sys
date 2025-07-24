"""
خدمة التكامل بين أنظمة الموارد البشرية

هذا الملف يحتوي على خدمات التكامل بين أنظمة الموارد البشرية المختلفة:
- نظام الموظفين
- نظام الحضور والانصراف
- نظام الرواتب
- نظام الإجازات
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

# إعداد نظام التسجيل
logger = logging.getLogger(__name__)

class HrIntegrationService:
    """
    خدمة التكامل بين أنظمة الموارد البشرية

    تقوم هذه الخدمة بتنسيق العمليات التي تتطلب تكاملاً بين أكثر من نظام فرعي
    من أنظمة الموارد البشرية، مثل حساب الرواتب بناءً على الحضور والإجازات.
    """

    @staticmethod
    def update_attendance_from_leave(leave_request):
        """
        تحديث سجلات الحضور بناءً على طلب إجازة معتمد

        عند الموافقة على طلب إجازة، يتم إنشاء سجلات حضور مناسبة
        لتجنب احتساب الموظف غائباً خلال فترة الإجازة
        """
        from Hr.models.attendance.attendance_models import AttendanceRecord, AttendanceStatus
        from django.db.models import Q

        try:
            # فقط للإجازات المعتمدة
            if leave_request.status != 'approved':
                logger.info(f"لم يتم تحديث الحضور لأن حالة الإجازة {leave_request.status}")
                return False

            employee = leave_request.employee
            start_date = leave_request.start_date
            end_date = leave_request.end_date
            current_date = start_date

            # إنشاء أو تحديث سجلات الحضور لكل يوم في فترة الإجازة
            while current_date <= end_date:
                # البحث عن سجل حضور موجود
                existing_record = AttendanceRecord.objects.filter(
                    employee=employee,
                    attendance_date=current_date
                ).first()

                if existing_record:
                    # تحديث السجل الموجود
                    existing_record.status = AttendanceStatus.LEAVE
                    existing_record.remarks = f"إجازة {leave_request.leave_type.name} - معتمدة"
                    existing_record.updated_at = timezone.now()
                    existing_record.save()
                    logger.debug(f"تم تحديث سجل الحضور للموظف {employee.id} بتاريخ {current_date}")
                else:
                    # إنشاء سجل جديد
                    AttendanceRecord.objects.create(
                        employee=employee,
                        company=employee.company,
                        attendance_date=current_date,
                        status=AttendanceStatus.LEAVE,
                        remarks=f"إجازة {leave_request.leave_type.name} - معتمدة",
                        is_processed=True
                    )
                    logger.debug(f"تم إنشاء سجل الحضور للموظف {employee.id} بتاريخ {current_date}")

                current_date += timedelta(days=1)

            logger.info(f"تم تحديث سجلات الحضور للموظف {employee.id} خلال فترة الإجازة من {start_date} إلى {end_date}")
            return True

        except Exception as e:
            logger.error(f"خطأ في تحديث سجلات الحضور من الإجازة: {str(e)}")
            return False

    @staticmethod
    def update_leave_balance(employee, leave_type, days_count, transaction_type, remarks=None):
        """
        تحديث رصيد الإجازات للموظف

        يقوم بتحديث رصيد إجازات الموظف لنوع إجازة محدد،
        سواء بالخصم في حالة طلب إجازة أو بالإضافة في حالة إلغاء الإجازة

        transaction_type: 'deduct' أو 'add'
        """
        from Hr.models.leave.leave_models import LeaveBalance, LeaveTransaction

        try:
            current_year = date.today().year

            # الحصول على رصيد الإجازة الحالي أو إنشاء رصيد جديد
            leave_balance, created = LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                company=employee.company,
                year=current_year,
                defaults={
                    'allocated_days': 0,
                    'taken_days': 0,
                    'pending_days': 0
                }
            )

            # تحديث الرصيد حسب نوع العملية
            if transaction_type == 'deduct':
                # التحقق من كفاية الرصيد
                available_balance = leave_balance.allocated_days + leave_balance.additional_days + leave_balance.carryforward_days - leave_balance.taken_days - leave_balance.pending_days

                if days_count > available_balance:
                    logger.warning(f"رصيد الإجازات غير كافٍ للموظف {employee.id}. المطلوب: {days_count}، المتاح: {available_balance}")
                    return False, "رصيد الإجازات غير كافٍ"

                leave_balance.pending_days += Decimal(str(days_count))

            elif transaction_type == 'add':
                leave_balance.pending_days -= Decimal(str(days_count))
                # تصحيح القيمة السالبة إن وجدت
                if leave_balance.pending_days < 0:
                    leave_balance.taken_days += leave_balance.pending_days
                    leave_balance.pending_days = 0

            elif transaction_type == 'confirm':
                # تحويل من معلق إلى مأخوذ
                if leave_balance.pending_days >= Decimal(str(days_count)):
                    leave_balance.taken_days += Decimal(str(days_count))
                    leave_balance.pending_days -= Decimal(str(days_count))
                else:
                    logger.warning(f"الأيام المعلقة غير كافية للموظف {employee.id}. المطلوب: {days_count}، المتاح: {leave_balance.pending_days}")
                    return False, "الأيام المعلقة غير كافية"

            # حفظ التغييرات
            leave_balance.save()

            # إنشاء سجل للعملية
            LeaveTransaction.objects.create(
                employee=employee,
                company=employee.company,
                leave_type=leave_type,
                leave_balance=leave_balance,
                transaction_date=timezone.now().date(),
                transaction_type=transaction_type,
                days=days_count,
                remarks=remarks or f"تعديل رصيد الإجازات - {transaction_type}"
            )

            logger.info(f"تم تحديث رصيد الإجازات للموظف {employee.id} لنوع الإجازة {leave_type.id}: {transaction_type} {days_count} يوم")
            return True, "تم تحديث الرصيد بنجاح"

        except Exception as e:
            logger.error(f"خطأ في تحديث رصيد الإجازات: {str(e)}")
            return False, f"خطأ في تحديث الرصيد: {str(e)}"

    @staticmethod
    def calculate_salary_deductions_from_attendance(employee, period_start, period_end):
        """
        حساب الاستقطاعات من الراتب بناءً على سجلات الحضور

        يقوم بحساب الاستقطاعات المترتبة على الغياب والتأخير وفقاً لسياسة الشركة
        """
        from Hr.models.attendance.attendance_models import AttendanceRecord, AttendanceStatus
        from django.db.models import Sum, Count, Q

        try:
            # الحصول على جميع سجلات الحضور في الفترة المحددة
            attendance_records = AttendanceRecord.objects.filter(
                employee=employee,
                attendance_date__gte=period_start,
                attendance_date__lte=period_end
            )

            # حساب أيام الغياب (غير مبرر)
            absent_days = attendance_records.filter(
                status=AttendanceStatus.ABSENT,
                is_approved=False
            ).count()

            # حساب أيام التأخير
            late_days = attendance_records.filter(
                status=AttendanceStatus.PRESENT,
                late_minutes__gt=0
            ).count()

            # حساب إجمالي دقائق التأخير
            total_late_minutes = attendance_records.filter(
                status=AttendanceStatus.PRESENT,
                late_minutes__gt=0
            ).aggregate(total=Sum('late_minutes'))['total'] or 0

            # حساب أيام المغادرة المبكرة
            early_leaving_days = attendance_records.filter(
                status=AttendanceStatus.PRESENT,
                early_leaving_minutes__gt=0
            ).count()

            # حساب إجمالي دقائق المغادرة المبكرة
            total_early_leaving_minutes = attendance_records.filter(
                status=AttendanceStatus.PRESENT,
                early_leaving_minutes__gt=0
            ).aggregate(total=Sum('early_leaving_minutes'))['total'] or 0

            # حساب إجمالي دقائق العمل الإضافي
            total_overtime_minutes = attendance_records.filter(
                status=AttendanceStatus.PRESENT,
                overtime_minutes__gt=0,
                overtime_approved=True
            ).aggregate(total=Sum('overtime_minutes'))['total'] or 0

            # حساب الاستقطاعات المالية
            deductions = 0
            overtime_pay = 0

            # الحصول على راتب الموظف اليومي
            daily_salary = 0
            if employee.basic_salary:
                monthly_salary = employee.basic_salary
                daily_salary = monthly_salary / 30  # افتراض 30 يوم في الشهر

            # حساب استقطاعات الغياب
            absence_deduction = absent_days * daily_salary

            # حساب استقطاعات التأخير (يعتمد على سياسة الشركة)
            # مثال: كل 60 دقيقة تأخير = خصم 1/4 يوم
            late_deduction = (total_late_minutes / 60) * (daily_salary / 4)

            # حساب استقطاعات المغادرة المبكرة
            early_leaving_deduction = (total_early_leaving_minutes / 60) * (daily_salary / 4)

            # حساب مبلغ العمل الإضافي
            # مثال: كل ساعة عمل إضافي = 1.5 من الراتب الساعي
            hourly_rate = daily_salary / 8  # افتراض 8 ساعات عمل يومياً
            overtime_pay = (total_overtime_minutes / 60) * hourly_rate * 1.5

            # إجمالي الاستقطاعات
            total_deductions = absence_deduction + late_deduction + early_leaving_deduction

            # إعداد النتائج
            results = {
                'absent_days': absent_days,
                'late_days': late_days,
                'total_late_minutes': total_late_minutes,
                'early_leaving_days': early_leaving_days,
                'total_early_leaving_minutes': total_early_leaving_minutes,
                'total_overtime_minutes': total_overtime_minutes,
                'absence_deduction': round(absence_deduction, 2),
                'late_deduction': round(late_deduction, 2),
                'early_leaving_deduction': round(early_leaving_deduction, 2),
                'total_deductions': round(total_deductions, 2),
                'overtime_pay': round(overtime_pay, 2)
            }

            logger.info(f"تم حساب استقطاعات الراتب للموظف {employee.id} للفترة من {period_start} إلى {period_end}")
            return True, results

        except Exception as e:
            logger.error(f"خطأ في حساب استقطاعات الراتب من الحضور: {str(e)}")
            return False, f"خطأ في الحساب: {str(e)}"

    @staticmethod
    def sync_employee_data():
        """
        مزامنة بيانات الموظفين بين الأنظمة الفرعية

        يقوم بتحديث بيانات الموظف في جميع الأنظمة الفرعية لضمان اتساقها
        """
        from Hr.models.employee.employee_models import Employee

        try:
            employees = Employee.objects.filter(is_active=True)
            sync_count = 0

            for employee in employees:
                # تحديث بيانات الموظف في نظام الرواتب
                HrIntegrationService.sync_employee_payroll_data(employee)

                # تحديث بيانات الموظف في نظام الحضور
                HrIntegrationService.sync_employee_attendance_data(employee)

                # تحديث بيانات الموظف في نظام الإجازات
                HrIntegrationService.sync_employee_leave_data(employee)

                sync_count += 1

            logger.info(f"تمت مزامنة بيانات {sync_count} موظف بنجاح")
            return True, f"تمت مزامنة بيانات {sync_count} موظف بنجاح"

        except Exception as e:
            logger.error(f"خطأ في مزامنة بيانات الموظفين: {str(e)}")
            return False, f"خطأ في المزامنة: {str(e)}"

    @staticmethod
    def sync_employee_payroll_data(employee):
        """مزامنة بيانات الموظف في نظام الرواتب"""
        # تنفيذ المزامنة مع نظام الرواتب
        pass

    @staticmethod
    def sync_employee_attendance_data(employee):
        """مزامنة بيانات الموظف في نظام الحضور"""
        # تنفيذ المزامنة مع نظام الحضور
        pass

    @staticmethod
    def sync_employee_leave_data(employee):
        """مزامنة بيانات الموظف في نظام الإجازات"""
        # تنفيذ المزامنة مع نظام الإجازات
        pass
