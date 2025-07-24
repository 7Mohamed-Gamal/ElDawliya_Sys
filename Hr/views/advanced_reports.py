"""
واجهات التقارير التحليلية المتقدمة

هذا الملف يحتوي على واجهات عرض التقارير التحليلية المتقدمة
التي تدعم اتخاذ القرارات في إدارة الموارد البشرية
"""

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q, Case, When, Value, DecimalField
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear, TruncMonth
from datetime import datetime, date, timedelta
import calendar
import csv
import io
import xlsxwriter
from decimal import Decimal

from Hr.models.employee.employee_models import Employee, EmploymentStatus
from Hr.models.attendance.attendance_models import AttendanceRecord, AttendanceStatus
from Hr.models.leave.leave_models import LeaveRequest, LeaveType, LeaveBalance
from Hr.models.payroll.payroll_models import Payroll, PayrollEmployee
from Hr.services.hr_reports_service import HrReportService


class AdvancedReportBaseView(LoginRequiredMixin, TemplateView):
    """
    الصنف الأساسي لجميع التقارير المتقدمة
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # التحقق من وجود شركة مرتبطة بالمستخدم
        if hasattr(user, 'employee') and user.employee and user.employee.company:
            company = user.employee.company
            context['company'] = company

            # الحصول على الأقسام لفلاتر التقارير
            context['departments'] = company.departments.filter(is_active=True)

            # بيانات الفلترة
            context['filter_year'] = int(self.request.GET.get('year', date.today().year))
            context['filter_month'] = int(self.request.GET.get('month', date.today().month))
            context['filter_department'] = self.request.GET.get('department', '')

            # سنوات التقارير (للفلاتر)
            current_year = date.today().year
            context['years'] = list(range(current_year - 5, current_year + 1))

        return context

    def export_as_excel(self, data, filename):
        """
        تصدير البيانات كملف Excel
        """
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        # تنسيقات الخلايا
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4e73df',
            'color': 'white',
            'border': 1
        })

        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        number_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00'
        })

        # كتابة رأس الجدول
        for col_num, header in enumerate(data['headers']):
            worksheet.write(0, col_num, header, header_format)
            worksheet.set_column(col_num, col_num, 15)

        # كتابة البيانات
        for row_num, row_data in enumerate(data['rows'], 1):
            for col_num, cell_value in enumerate(row_data):
                if isinstance(cell_value, (int, float, Decimal)):
                    worksheet.write(row_num, col_num, cell_value, number_format)
                else:
                    worksheet.write(row_num, col_num, cell_value, cell_format)

        workbook.close()
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    def export_as_csv(self, data, filename):
        """
        تصدير البيانات كملف CSV
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        writer = csv.writer(response)
        writer.writerow(data['headers'])
        writer.writerows(data['rows'])

        return response


class HeadcountAnalysisView(AdvancedReportBaseView):
    """
    تقرير تحليل عدد الموظفين وتطوره
    """
    template_name = 'hr/reports/headcount_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'company' not in context:
            return context

        company = context['company']
        filter_year = context['filter_year']
        filter_department = context['filter_department']

        # فلتر الأقسام إن وجد
        department_filter = {}
        if filter_department:
            department_filter['department_id'] = filter_department

        # الإحصائيات الحالية
        current_stats = self.get_current_headcount_stats(company, department_filter)
        context['current_stats'] = current_stats

        # تطور عدد الموظفين شهرياً
        monthly_stats = self.get_monthly_headcount_stats(company, filter_year, department_filter)
        context['monthly_stats'] = monthly_stats

        # معدل دوران الموظفين
        turnover_stats = self.get_turnover_stats(company, filter_year, department_filter)
        context['turnover_stats'] = turnover_stats

        # توزيع الموظفين حسب المعايير المختلفة
        distribution_stats = self.get_distribution_stats(company, department_filter)
        context['distribution_stats'] = distribution_stats

        return context

    def get_current_headcount_stats(self, company, department_filter):
        """
        الحصول على إحصائيات عدد الموظفين الحالية
        """
        employees = Employee.objects.filter(company=company, **department_filter)
        active_employees = employees.filter(is_active=True)

        # الإحصائيات العامة
        stats = {
            'total': active_employees.count(),
            'male': active_employees.filter(gender='male').count(),
            'female': active_employees.filter(gender='female').count(),
            'full_time': active_employees.filter(employment_type='full_time').count(),
            'part_time': active_employees.filter(employment_type='part_time').count(),
            'contract': active_employees.filter(employment_type='contract').count(),
            'probation': active_employees.filter(employment_status=EmploymentStatus.PROBATION).count(),
        }

        # حساب النسب المئوية
        if stats['total'] > 0:
            stats['male_percentage'] = round((stats['male'] / stats['total']) * 100, 1)
            stats['female_percentage'] = round((stats['female'] / stats['total']) * 100, 1)
            stats['full_time_percentage'] = round((stats['full_time'] / stats['total']) * 100, 1)
            stats['part_time_percentage'] = round((stats['part_time'] / stats['total']) * 100, 1)
            stats['contract_percentage'] = round((stats['contract'] / stats['total']) * 100, 1)
            stats['probation_percentage'] = round((stats['probation'] / stats['total']) * 100, 1)
        else:
            stats.update({
                'male_percentage': 0,
                'female_percentage': 0,
                'full_time_percentage': 0,
                'part_time_percentage': 0,
                'contract_percentage': 0,
                'probation_percentage': 0
            })

        return stats

    def get_monthly_headcount_stats(self, company, year, department_filter):
        """
        الحصول على إحصائيات تطور عدد الموظفين شهرياً
        """
        months_data = []

        # لكل شهر في السنة
        for month in range(1, 13):
            # تاريخ نهاية الشهر
            last_day = calendar.monthrange(year, month)[1]
            end_date = date(year, month, last_day)

            # عدد الموظفين حتى نهاية الشهر
            active_count = Employee.objects.filter(
                company=company,
                joining_date__lte=end_date,
                **department_filter
            ).filter(
                Q(termination_date__gt=end_date) | Q(termination_date__isnull=True)
            ).count()

            # عدد التوظيفات الجديدة خلال الشهر
            new_hires = Employee.objects.filter(
                company=company,
                joining_date__year=year,
                joining_date__month=month,
                **department_filter
            ).count()

            # عدد الموظفين الذين تركوا العمل خلال الشهر
            terminations = Employee.objects.filter(
                company=company,
                termination_date__year=year,
                termination_date__month=month,
                **department_filter
            ).count()

            month_name = calendar.month_name[month]
            months_data.append({
                'month': month,
                'month_name': month_name,
                'active_count': active_count,
                'new_hires': new_hires,
                'terminations': terminations
            })

        return months_data

    def get_turnover_stats(self, company, year, department_filter):
        """
        حساب معدل دوران الموظفين
        """
        stats = []

        # لكل شهر في السنة
        for month in range(1, 13):
            # تاريخ نهاية الشهر
            last_day = calendar.monthrange(year, month)[1]
            end_date = date(year, month, last_day)

            # عدد الموظفين في بداية الشهر
            start_of_month = date(year, month, 1)

            employees_start = Employee.objects.filter(
                company=company,
                joining_date__lt=start_of_month,
                **department_filter
            ).filter(
                Q(termination_date__gt=start_of_month) | Q(termination_date__isnull=True)
            ).count()

            # عدد الموظفين في نهاية الشهر
            employees_end = Employee.objects.filter(
                company=company,
                joining_date__lte=end_date,
                **department_filter
            ).filter(
                Q(termination_date__gt=end_date) | Q(termination_date__isnull=True)
            ).count()

            # متوسط عدد الموظفين خلال الشهر
            avg_employees = (employees_start + employees_end) / 2 if (employees_start + employees_end) > 0 else 0

            # عدد الموظفين الذين تركوا العمل خلال الشهر
            terminations = Employee.objects.filter(
                company=company,
                termination_date__year=year,
                termination_date__month=month,
                **department_filter
            ).count()

            # حساب معدل الدوران
            turnover_rate = (terminations / avg_employees) * 100 if avg_employees > 0 else 0

            month_name = calendar.month_name[month]
            stats.append({
                'month': month,
                'month_name': month_name,
                'employees_start': employees_start,
                'employees_end': employees_end,
                'avg_employees': round(avg_employees, 1),
                'terminations': terminations,
                'turnover_rate': round(turnover_rate, 1)
            })

        return stats

    def get_distribution_stats(self, company, department_filter):
        """
        الحصول على إحصائيات توزيع الموظفين
        """
        employees = Employee.objects.filter(company=company, is_active=True, **department_filter)

        # توزيع الموظفين حسب القسم
        departments = employees.values('department__name').annotate(
            count=Count('id')
        ).order_by('-count')

        # توزيع الموظفين حسب المنصب الوظيفي
        job_positions = employees.values('job_position__name').annotate(
            count=Count('id')
        ).order_by('-count')

        # توزيع الموظفين حسب الجنسية
        nationalities = employees.values('nationality').annotate(
            count=Count('id')
        ).order_by('-count')

        # توزيع الموظفين حسب العمر
        today = date.today()
        age_ranges = {
            '<25': Count('id', filter=Q(date_of_birth__gt=today.replace(year=today.year-25))),
            '25-35': Count('id', filter=Q(date_of_birth__lte=today.replace(year=today.year-25)) & Q(date_of_birth__gt=today.replace(year=today.year-35))),
            '36-45': Count('id', filter=Q(date_of_birth__lte=today.replace(year=today.year-35)) & Q(date_of_birth__gt=today.replace(year=today.year-45))),
            '46-55': Count('id', filter=Q(date_of_birth__lte=today.replace(year=today.year-45)) & Q(date_of_birth__gt=today.replace(year=today.year-55))),
            '>55': Count('id', filter=Q(date_of_birth__lte=today.replace(year=today.year-55)))
        }

        age_distribution = employees.aggregate(**age_ranges)

        # توزيع الموظفين حسب مدة الخدمة
        service_ranges = {
            '<1': Count('id', filter=Q(joining_date__gt=today.replace(year=today.year-1))),
            '1-3': Count('id', filter=Q(joining_date__lte=today.replace(year=today.year-1)) & Q(joining_date__gt=today.replace(year=today.year-3))),
            '3-5': Count('id', filter=Q(joining_date__lte=today.replace(year=today.year-3)) & Q(joining_date__gt=today.replace(year=today.year-5))),
            '5-10': Count('id', filter=Q(joining_date__lte=today.replace(year=today.year-5)) & Q(joining_date__gt=today.replace(year=today.year-10))),
            '>10': Count('id', filter=Q(joining_date__lte=today.replace(year=today.year-10)))
        }

        service_distribution = employees.aggregate(**service_ranges)

        return {
            'departments': departments,
            'job_positions': job_positions,
            'nationalities': nationalities,
            'age_distribution': age_distribution,
            'service_distribution': service_distribution
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # التعامل مع طلبات التصدير
        export_format = request.GET.get('export')
        if export_format and 'company' in context:
            # إعداد بيانات التصدير
            data = self.prepare_export_data(context)
            filename = f'headcount_analysis_{context["filter_year"]}.{export_format}'

            if export_format == 'xlsx':
                return self.export_as_excel(data, filename)
            elif export_format == 'csv':
                return self.export_as_csv(data, filename)

        return super().get(request, *args, **kwargs)

    def prepare_export_data(self, context):
        """
        إعداد بيانات التصدير
        """
        # بيانات الإحصائيات الشهرية
        headers = ['الشهر', 'عدد الموظفين', 'التوظيفات الجديدة', 'إنهاء الخدمة', 'معدل الدوران (%)']
        rows = []

        for month in context['monthly_stats']:
            # البحث عن معدل الدوران المقابل لهذا الشهر
            turnover_rate = 0
            for t in context['turnover_stats']:
                if t['month'] == month['month']:
                    turnover_rate = t['turnover_rate']
                    break

            rows.append([
                month['month_name'],
                month['active_count'],
                month['new_hires'],
                month['terminations'],
                turnover_rate
            ])

        return {
            'headers': headers,
            'rows': rows
        }


class AttendanceAnalysisView(AdvancedReportBaseView):
    """
    تقرير تحليل الحضور والانصراف
    """
    template_name = 'hr/reports/attendance_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'company' not in context:
            return context

        company = context['company']
        filter_year = context['filter_year']
        filter_month = context['filter_month']
        filter_department = context['filter_department']

        # فلتر الأقسام إن وجد
        department_filter = {}
        if filter_department:
            department_filter['department_id'] = filter_department

        # تحديد فترة التقرير
        if filter_month:
            # تقرير شهري
            first_day = date(filter_year, filter_month, 1)
            if filter_month == 12:
                last_day = date(filter_year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(filter_year, filter_month + 1, 1) - timedelta(days=1)
        else:
            # تقرير سنوي
            first_day = date(filter_year, 1, 1)
            last_day = date(filter_year, 12, 31)

        context['report_period'] = {
            'first_day': first_day,
            'last_day': last_day
        }

        # الحصول على إحصائيات الحضور
        attendance_stats = HrReportService.generate_monthly_attendance_report(
            company=company,
            year=filter_year,
            month=filter_month if filter_month else None,
            department=context['departments'].filter(id=filter_department).first() if filter_department else None
        )

        if attendance_stats[0]:  # إذا كانت العملية ناجحة
            context['attendance_report'] = attendance_stats[1]

            # إعداد بيانات الرسوم البيانية
            context['attendance_summary_chart'] = self.prepare_summary_chart_data(attendance_stats[1])

            if filter_month:
                # تفاصيل الحضور اليومي (للتقرير الشهري فقط)
                daily_stats = self.get_daily_attendance_stats(
                    company, 
                    first_day, 
                    last_day, 
                    department_filter
                )
                context['daily_stats'] = daily_stats

        return context

    def prepare_summary_chart_data(self, attendance_report):
        """
        إعداد بيانات الرسم البياني لملخص الحضور
        """
        summary = attendance_report['summary']

        total_days = summary['total_present_days'] + summary['total_absent_days'] + summary['total_leave_days']

        if total_days > 0:
            present_percentage = (summary['total_present_days'] / total_days) * 100
            absent_percentage = (summary['total_absent_days'] / total_days) * 100
            leave_percentage = (summary['total_leave_days'] / total_days) * 100
        else:
            present_percentage = absent_percentage = leave_percentage = 0

        return {
            'labels': ['الحضور', 'الغياب', 'الإجازات'],
            'data': [
                round(present_percentage, 1),
                round(absent_percentage, 1),
                round(leave_percentage, 1)
            ]
        }

    def get_daily_attendance_stats(self, company, start_date, end_date, department_filter):
        """
        الحصول على إحصائيات الحضور اليومية للفترة المحددة
        """
        # الحصول على جميع أيام الفترة
        days = []
        current_date = start_date
        while current_date <= end_date:
            days.append(current_date)
            current_date += timedelta(days=1)

        daily_stats = []

        for day in days:
            # الحصول على إحصائيات هذا اليوم
            records = AttendanceRecord.objects.filter(
                company=company,
                attendance_date=day
            )

            if department_filter:
                records = records.filter(employee__department_id=department_filter['department_id'])

            stats = records.aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
                absent=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
                leave=Count('id', filter=Q(status=AttendanceStatus.LEAVE)),
                late=Count('id', filter=Q(status=AttendanceStatus.PRESENT, late_minutes__gt=0)),
                early_leaving=Count('id', filter=Q(status=AttendanceStatus.PRESENT, early_leaving_minutes__gt=0)),
                total_late_minutes=Sum('late_minutes', filter=Q(late_minutes__gt=0)),
                total_early_minutes=Sum('early_leaving_minutes', filter=Q(early_leaving_minutes__gt=0))
            )

            # حساب النسب المئوية
            if stats['total'] > 0:
                attendance_percentage = (stats['present'] / stats['total']) * 100
            else:
                attendance_percentage = 0

            daily_stats.append({
                'date': day,
                'day_name': calendar.day_name[day.weekday()],
                'total': stats['total'],
                'present': stats['present'] or 0,
                'absent': stats['absent'] or 0,
                'leave': stats['leave'] or 0,
                'late': stats['late'] or 0,
                'early_leaving': stats['early_leaving'] or 0,
                'total_late_minutes': stats['total_late_minutes'] or 0,
                'total_early_minutes': stats['total_early_minutes'] or 0,
                'attendance_percentage': round(attendance_percentage, 1)
            })

        return daily_stats

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # التعامل مع طلبات التصدير
        export_format = request.GET.get('export')
        if export_format and 'company' in context and 'attendance_report' in context:
            # إعداد بيانات التصدير
            data = self.prepare_export_data(context)

            period_name = f"{context['filter_year']}"
            if context['filter_month']:
                period_name += f"_{context['filter_month']}"

            filename = f'attendance_analysis_{period_name}.{export_format}'

            if export_format == 'xlsx':
                return self.export_as_excel(data, filename)
            elif export_format == 'csv':
                return self.export_as_csv(data, filename)

        return super().get(request, *args, **kwargs)

    def prepare_export_data(self, context):
        """
        إعداد بيانات التصدير
        """
        headers = [
            'الموظف', 'رقم الموظف', 'القسم', 'أيام الحضور', 'أيام الغياب',
            'أيام الإجازات', 'أيام التأخير', 'إجمالي دقائق التأخير',
            'نسبة الحضور (%)'
        ]

        rows = []
        for employee in context['attendance_report']['employees']:
            stats = employee['stats']
            rows.append([
                employee['name'],
                employee['employee_id'],
                employee['department'],
                stats['present_days'],
                stats['absent_days'],
                stats['leave_days'],
                stats['late_days'],
                stats['total_late_minutes'],
                stats['attendance_percentage']
            ])

        return {
            'headers': headers,
            'rows': rows
        }


# إضافة المزيد من واجهات التقارير المتقدمة هنا...
