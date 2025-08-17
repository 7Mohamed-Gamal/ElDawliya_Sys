"""
خدمة تقارير الموارد البشرية

هذا الملف يحتوي على خدمات إنشاء التقارير التحليلية المتكاملة
لجميع أنظمة الموارد البشرية، بما يسمح برؤية شاملة لأداء النظام
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Avg, Q, F, Case, When, Value, IntegerField, DecimalField
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear
from django.utils import timezone
from collections import defaultdict

# إعداد نظام التسجيل
logger = logging.getLogger(__name__)

class HrReportService:
    """
    خدمة تقارير الموارد البشرية

    توفر هذه الخدمة وظائف لإنشاء تقارير متكاملة من جميع أنظمة الموارد البشرية
    مثل تقارير الحضور، الإجازات، الرواتب، والأداء، مع تقديم تحليلات ومؤشرات أداء
    """

    @staticmethod
    def generate_monthly_attendance_report(company, year, month, department=None):
        """
        إنشاء تقرير الحضور الشهري

        يقدم إحصائيات شاملة عن حضور الموظفين خلال شهر محدد
        """
        from Hr.models.attendance.attendance_models import AttendanceRecord, AttendanceStatus
        from Hr.models.employee.employee_models import Employee

        try:
            # تحديد فترة التقرير
            first_day = date(year, month, 1)
            if month == 12:
                last_day = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(year, month + 1, 1) - timedelta(days=1)

            # فلتر الموظفين
            employee_filter = {'company': company, 'is_active': True}
            if department:
                employee_filter['department'] = department

            employees = Employee.objects.filter(**employee_filter)

            # نتائج التقرير
            report_data = {
                'period': {
                    'year': year,
                    'month': month,
                    'first_day': first_day,
                    'last_day': last_day,
                    'total_days': (last_day - first_day).days + 1
                },
                'company': {
                    'id': str(company.id),
                    'name': company.name
                },
                'department': None if not department else {
                    'id': str(department.id),
                    'name': department.name
                },
                'summary': {
                    'total_employees': employees.count(),
                    'total_present_days': 0,
                    'total_absent_days': 0,
                    'total_leave_days': 0,
                    'total_late_days': 0,
                    'total_late_minutes': 0,
                    'average_attendance_percentage': 0
                },
                'employees': []
            }

            # الإحصائيات العامة
            attendance_stats = AttendanceRecord.objects.filter(
                company=company,
                attendance_date__gte=first_day,
                attendance_date__lte=last_day
            ).aggregate(
                present_days=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
                absent_days=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
                leave_days=Count('id', filter=Q(status=AttendanceStatus.LEAVE)),
                late_days=Count('id', filter=Q(status=AttendanceStatus.PRESENT, late_minutes__gt=0)),
                total_late_minutes=Sum(Coalesce('late_minutes', 0))
            )

            # تحديث ملخص التقرير
            report_data['summary']['total_present_days'] = attendance_stats['present_days'] or 0
            report_data['summary']['total_absent_days'] = attendance_stats['absent_days'] or 0
            report_data['summary']['total_leave_days'] = attendance_stats['leave_days'] or 0
            report_data['summary']['total_late_days'] = attendance_stats['late_days'] or 0
            report_data['summary']['total_late_minutes'] = attendance_stats['total_late_minutes'] or 0

            # حساب نسبة الحضور
            business_days = 0
            current_date = first_day
            while current_date <= last_day:
                if current_date.weekday() < 5:  # 0-4 هي أيام الإثنين إلى الجمعة
                    business_days += 1
                current_date += timedelta(days=1)

            total_possible_attendance = employees.count() * business_days
            if total_possible_attendance > 0:
                attendance_percentage = (report_data['summary']['total_present_days'] / total_possible_attendance) * 100
                report_data['summary']['average_attendance_percentage'] = round(attendance_percentage, 2)

            # تفاصيل الموظفين
            for employee in employees:
                employee_records = AttendanceRecord.objects.filter(
                    employee=employee,
                    attendance_date__gte=first_day,
                    attendance_date__lte=last_day
                )

                employee_stats = employee_records.aggregate(
                    present_days=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
                    absent_days=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
                    leave_days=Count('id', filter=Q(status=AttendanceStatus.LEAVE)),
                    late_days=Count('id', filter=Q(status=AttendanceStatus.PRESENT, late_minutes__gt=0)),
                    total_late_minutes=Sum(Coalesce('late_minutes', 0)),
                    early_leaving_days=Count('id', filter=Q(status=AttendanceStatus.PRESENT, early_leaving_minutes__gt=0)),
                    overtime_days=Count('id', filter=Q(status=AttendanceStatus.PRESENT, overtime_minutes__gt=0)),
                    total_overtime_minutes=Sum(Coalesce('overtime_minutes', 0))
                )

                # حساب نسبة الحضور
                attendance_percentage = 0
                if business_days > 0:
                    attendance_percentage = ((employee_stats['present_days'] or 0) / business_days) * 100

                employee_data = {
                    'id': str(employee.id),
                    'employee_id': employee.employee_id,
                    'name': employee.full_name,
                    'department': employee.department.name if employee.department else '',
                    'job_position': employee.job_position.name if employee.job_position else '',
                    'stats': {
                        'present_days': employee_stats['present_days'] or 0,
                        'absent_days': employee_stats['absent_days'] or 0,
                        'leave_days': employee_stats['leave_days'] or 0,
                        'late_days': employee_stats['late_days'] or 0,
                        'total_late_minutes': employee_stats['total_late_minutes'] or 0,
                        'early_leaving_days': employee_stats['early_leaving_days'] or 0,
                        'overtime_days': employee_stats['overtime_days'] or 0,
                        'total_overtime_minutes': employee_stats['total_overtime_minutes'] or 0,
                        'attendance_percentage': round(attendance_percentage, 2)
                    }
                }

                report_data['employees'].append(employee_data)

            logger.info(f"تم إنشاء تقرير الحضور الشهري للشركة {company.name} - {month}/{year}")
            return True, report_data

        except Exception as e:
            logger.error(f"خطأ في إنشاء تقرير الحضور الشهري: {str(e)}")
            return False, f"خطأ في إنشاء التقرير: {str(e)}"

    @staticmethod
    def generate_leave_report(company, start_date, end_date, department=None):
        """
        إنشاء تقرير الإجازات

        يقدم إحصائيات عن إجازات الموظفين خلال فترة محددة
        """
        from Hr.models.leave.leave_models import LeaveRequest, LeaveType
        from Hr.models.employee.employee_models import Employee

        try:
            # فلتر الموظفين
            employee_filter = {'company': company, 'is_active': True}
            if department:
                employee_filter['department'] = department

            employees = Employee.objects.filter(**employee_filter)

            # نتائج التقرير
            report_data = {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_days': (end_date - start_date).days + 1
                },
                'company': {
                    'id': str(company.id),
                    'name': company.name
                },
                'department': None if not department else {
                    'id': str(department.id),
                    'name': department.name
                },
                'summary': {
                    'total_employees': employees.count(),
                    'total_leave_requests': 0,
                    'total_leave_days': 0,
                    'approved_leave_requests': 0,
                    'rejected_leave_requests': 0,
                    'pending_leave_requests': 0
                },
                'leave_types': [],
                'employees': []
            }

            # الإحصائيات العامة
            leave_filter = {
                'company': company,
                'Q': Q(start_date__gte=start_date, start_date__lte=end_date) | 
                     Q(end_date__gte=start_date, end_date__lte=end_date) |
                     Q(start_date__lte=start_date, end_date__gte=end_date)
            }

            if department:
                leave_filter['employee__department'] = department

            leave_requests = LeaveRequest.objects.filter(**{k: v for k, v in leave_filter.items() if k != 'Q'}).filter(leave_filter['Q'])

            leave_stats = leave_requests.aggregate(
                total_requests=Count('id'),
                approved_requests=Count('id', filter=Q(status='approved')),
                rejected_requests=Count('id', filter=Q(status='rejected')),
                pending_requests=Count('id', filter=Q(status='pending')),
                total_days=Sum('days')
            )

            # تحديث ملخص التقرير
            report_data['summary']['total_leave_requests'] = leave_stats['total_requests'] or 0
            report_data['summary']['total_leave_days'] = leave_stats['total_days'] or 0
            report_data['summary']['approved_leave_requests'] = leave_stats['approved_requests'] or 0
            report_data['summary']['rejected_leave_requests'] = leave_stats['rejected_requests'] or 0
            report_data['summary']['pending_leave_requests'] = leave_stats['pending_requests'] or 0

            # إحصائيات حسب نوع الإجازة
            leave_types = LeaveType.objects.filter(company=company, is_active=True)
            for leave_type in leave_types:
                type_stats = leave_requests.filter(leave_type=leave_type).aggregate(
                    total_requests=Count('id'),
                    total_days=Sum('days'),
                    approved_requests=Count('id', filter=Q(status='approved')),
                    approved_days=Sum('days', filter=Q(status='approved'))
                )

                leave_type_data = {
                    'id': str(leave_type.id),
                    'name': leave_type.name,
                    'total_requests': type_stats['total_requests'] or 0,
                    'total_days': type_stats['total_days'] or 0,
                    'approved_requests': type_stats['approved_requests'] or 0,
                    'approved_days': type_stats['approved_days'] or 0
                }

                report_data['leave_types'].append(leave_type_data)

            # تفاصيل الموظفين
            for employee in employees:
                employee_leaves = leave_requests.filter(employee=employee)

                employee_leave_stats = employee_leaves.aggregate(
                    total_requests=Count('id'),
                    total_days=Sum('days'),
                    approved_requests=Count('id', filter=Q(status='approved')),
                    approved_days=Sum('days', filter=Q(status='approved')),
                    pending_requests=Count('id', filter=Q(status='pending')),
                    rejected_requests=Count('id', filter=Q(status='rejected'))
                )

                # تفاصيل حسب نوع الإجازة
                employee_leave_types = []
                for leave_type in leave_types:
                    type_requests = employee_leaves.filter(leave_type=leave_type)
                    if type_requests.exists():
                        type_days = type_requests.aggregate(total_days=Sum('days'))['total_days'] or 0
                        employee_leave_types.append({
                            'leave_type': leave_type.name,
                            'requests': type_requests.count(),
                            'days': type_days
                        })

                employee_data = {
                    'id': str(employee.id),
                    'employee_id': employee.employee_id,
                    'name': employee.full_name,
                    'department': employee.department.name if employee.department else '',
                    'job_position': employee.job_position.name if employee.job_position else '',
                    'stats': {
                        'total_requests': employee_leave_stats['total_requests'] or 0,
                        'total_days': employee_leave_stats['total_days'] or 0,
                        'approved_requests': employee_leave_stats['approved_requests'] or 0,
                        'approved_days': employee_leave_stats['approved_days'] or 0,
                        'pending_requests': employee_leave_stats['pending_requests'] or 0,
                        'rejected_requests': employee_leave_stats['rejected_requests'] or 0
                    },
                    'leave_types': employee_leave_types
                }

                report_data['employees'].append(employee_data)

            logger.info(f"تم إنشاء تقرير الإجازات للشركة {company.name} - من {start_date} إلى {end_date}")
            return True, report_data

        except Exception as e:
            logger.error(f"خطأ في إنشاء تقرير الإجازات: {str(e)}")
            return False, f"خطأ في إنشاء التقرير: {str(e)}"

    @staticmethod
    def generate_salary_report(company, year, month, department=None):
        """
        إنشاء تقرير الرواتب

        يقدم تحليلاً مفصلاً للرواتب والاستحقاقات والاستقطاعات
        """
        from Hr.models.payroll.payroll_models import Payroll, PayrollEmployee, PayrollComponent

        try:
            # البحث عن كشف الراتب المناسب
            payroll_filter = {
                'company': company,
                'payroll_month': month,
                'payroll_year': year,
                'status__in': ['approved', 'paid']
            }

            if department:
                payroll_filter['department'] = department

            payroll = Payroll.objects.filter(**payroll_filter).first()

            if not payroll:
                logger.warning(f"لم يتم العثور على كشف راتب للشركة {company.name} - {month}/{year}")
                return False, "لم يتم العثور على كشف راتب مناسب"

            # نتائج التقرير
            report_data = {
                'period': {
                    'year': year,
                    'month': month,
                    'period_start': payroll.period_start,
                    'period_end': payroll.period_end
                },
                'company': {
                    'id': str(company.id),
                    'name': company.name
                },
                'department': None if not department else {
                    'id': str(department.id),
                    'name': department.name
                },
                'payroll': {
                    'id': str(payroll.id),
                    'name': payroll.name,
                    'status': payroll.status
                },
                'summary': {
                    'total_employees': payroll.payroll_employees.count(),
                    'total_basic_salary': 0,
                    'total_gross_salary': payroll.total_gross_salary or 0,
                    'total_deductions': payroll.total_deductions or 0,
                    'total_net_salary': payroll.total_net_salary or 0,
                    'average_salary': 0,
                    'salary_distribution': {
                        'ranges': [],
                        'departments': []
                    }
                },
                'components': [],
                'employees': []
            }

            # الإحصائيات العامة
            salary_stats = payroll.payroll_employees.aggregate(
                total_basic=Sum('basic_salary'),
                avg_salary=Avg('net_salary')
            )

            report_data['summary']['total_basic_salary'] = salary_stats['total_basic'] or 0
            report_data['summary']['average_salary'] = round(salary_stats['avg_salary'] or 0, 2)

            # إحصائيات مكونات الراتب
            components = PayrollComponent.objects.filter(payroll_employee__payroll=payroll)
            component_stats = components.values('component_name', 'component_type').annotate(
                count=Count('id'),
                total=Sum('amount'),
                avg=Avg('amount')
            )

            for comp in component_stats:
                report_data['components'].append({
                    'name': comp['component_name'],
                    'type': comp['component_type'],
                    'count': comp['count'],
                    'total': comp['total'],
                    'average': round(comp['avg'], 2)
                })

            # توزيع الرواتب حسب النطاق
            salary_ranges = [
                {'min': 0, 'max': 5000},
                {'min': 5001, 'max': 10000},
                {'min': 10001, 'max': 15000},
                {'min': 15001, 'max': 20000},
                {'min': 20001, 'max': float('inf')}
            ]

            for salary_range in salary_ranges:
                min_val = salary_range['min']
                max_val = salary_range['max']

                range_filter = Q(net_salary__gte=min_val)
                if max_val != float('inf'):
                    range_filter &= Q(net_salary__lte=max_val)

                count = payroll.payroll_employees.filter(range_filter).count()

                range_label = f"{min_val:,} - {max_val:,}" if max_val != float('inf') else f"{min_val:,}+"
                report_data['summary']['salary_distribution']['ranges'].append({
                    'range': range_label,
                    'count': count,
                    'percentage': round((count / report_data['summary']['total_employees']) * 100, 2) if report_data['summary']['total_employees'] > 0 else 0
                })

            # توزيع الرواتب حسب القسم
            if department is None:
                department_stats = payroll.payroll_employees.values('department__name').annotate(
                    count=Count('id'),
                    total=Sum('net_salary'),
                    avg=Avg('net_salary')
                ).order_by('-total')

                for dept in department_stats:
                    if not dept['department__name']:
                        continue

                    report_data['summary']['salary_distribution']['departments'].append({
                        'department': dept['department__name'],
                        'count': dept['count'],
                        'total': dept['total'],
                        'average': round(dept['avg'], 2),
                        'percentage': round((dept['total'] / report_data['summary']['total_net_salary']) * 100, 2) if report_data['summary']['total_net_salary'] > 0 else 0
                    })

            # تفاصيل الموظفين
            for payroll_employee in payroll.payroll_employees.all():
                employee = payroll_employee.employee

                employee_components = components.filter(payroll_employee=payroll_employee).values('component_name', 'component_type', 'amount')

                employee_data = {
                    'id': str(employee.id),
                    'employee_id': employee.employee_id,
                    'name': employee.full_name,
                    'department': employee.department.name if employee.department else '',
                    'job_position': employee.job_position.name if employee.job_position else '',
                    'salary': {
                        'basic': payroll_employee.basic_salary,
                        'gross': payroll_employee.gross_salary,
                        'deductions': payroll_employee.total_deductions,
                        'net': payroll_employee.net_salary
                    },
                    'components': list(employee_components)
                }

                report_data['employees'].append(employee_data)

            logger.info(f"تم إنشاء تقرير الرواتب للشركة {company.name} - {month}/{year}")
            return True, report_data

        except Exception as e:
            logger.error(f"خطأ في إنشاء تقرير الرواتب: {str(e)}")
            return False, f"خطأ في إنشاء التقرير: {str(e)}"

    @staticmethod
    def generate_dashboard_stats(company):
        """
        إنشاء إحصائيات لوحة التحكم

        يقدم إحصائيات سريعة لعرضها في لوحة تحكم نظام الموارد البشرية
        """
        from Hr.models.employee.employee_models import Employee, EmploymentStatus
        from Hr.models.attendance.attendance_models import AttendanceRecord, AttendanceStatus
        from Hr.models.leave.leave_models import LeaveRequest

        try:
            today = date.today()

            # إحصائيات الموظفين
            employee_stats = Employee.objects.filter(company=company).aggregate(
                total=Count('id'),
                active=Count('id', filter=Q(is_active=True)),
                on_leave=Count('id', filter=Q(is_active=True, employment_status=EmploymentStatus.ON_LEAVE)),
                new_this_month=Count('id', filter=Q(is_active=True, joining_date__month=today.month, joining_date__year=today.year))
            )

            # إحصائيات الحضور لليوم الحالي
            attendance_stats = AttendanceRecord.objects.filter(
                company=company,
                attendance_date=today
            ).aggregate(
                present=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
                absent=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
                late=Count('id', filter=Q(status=AttendanceStatus.PRESENT, late_minutes__gt=0))
            )

            # إحصائيات الإجازات
            leave_stats = LeaveRequest.objects.filter(
                company=company,
                status='approved',
                start_date__lte=today,
                end_date__gte=today
            ).aggregate(
                on_leave_today=Count('id')
            )

            # الإحصائيات القادمة
            upcoming_leaves = LeaveRequest.objects.filter(
                company=company,
                status='approved',
                start_date__gt=today,
                start_date__lte=today + timedelta(days=30)
            ).count()

            upcoming_birthdays = Employee.objects.filter(
                company=company,
                is_active=True
            ).annotate(
                birthday_this_year=Case(
                    When(
                        date_of_birth__month=ExtractMonth('date_of_birth'),
                        date_of_birth__day=ExtractDay('date_of_birth'),
                        then=Value(1)
                    ),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).filter(
                birthday_this_year=1,
                date_of_birth__month__gte=today.month,
                date_of_birth__day__gte=today.day
            ).order_by('date_of_birth__month', 'date_of_birth__day').count()

            # تجميع الإحصائيات
            dashboard_stats = {
                'employees': {
                    'total': employee_stats['total'] or 0,
                    'active': employee_stats['active'] or 0,
                    'on_leave': employee_stats['on_leave'] or 0,
                    'new_this_month': employee_stats['new_this_month'] or 0
                },
                'attendance_today': {
                    'date': today,
                    'present': attendance_stats['present'] or 0,
                    'absent': attendance_stats['absent'] or 0,
                    'late': attendance_stats['late'] or 0,
                    'on_leave': leave_stats['on_leave_today'] or 0
                },
                'upcoming': {
                    'leaves': upcoming_leaves,
                    'birthdays': upcoming_birthdays
                }
            }

            # حساب نسبة الحضور
            if dashboard_stats['employees']['active'] > 0:
                attendance_percentage = (dashboard_stats['attendance_today']['present'] / dashboard_stats['employees']['active']) * 100
                dashboard_stats['attendance_today']['attendance_percentage'] = round(attendance_percentage, 2)
            else:
                dashboard_stats['attendance_today']['attendance_percentage'] = 0

            logger.info(f"تم إنشاء إحصائيات لوحة التحكم للشركة {company.name}")
            return True, dashboard_stats

        except Exception as e:
            logger.error(f"خطأ في إنشاء إحصائيات لوحة التحكم: {str(e)}")
            return False, f"خطأ في إنشاء الإحصائيات: {str(e)}"
