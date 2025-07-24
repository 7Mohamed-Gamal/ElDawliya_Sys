"""
لوحة قياس أداء الموارد البشرية (KPI Dashboard)

هذا الملف يحتوي على واجهات عرض مؤشرات الأداء الرئيسية
لقياس فعالية وكفاءة أنشطة الموارد البشرية
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
import json

from Hr.models.employee.employee_models import Employee, EmploymentStatus
from Hr.models.attendance.attendance_models import AttendanceRecord, AttendanceStatus
from Hr.models.leave.leave_models import LeaveRequest, LeaveType, LeaveBalance
from Hr.models.payroll.payroll_models import Payroll, PayrollEmployee
from Hr.services.hr_reports_service import HrReportService


class HrKpiDashboardView(LoginRequiredMixin, TemplateView):
    """
    لوحة قياس أداء الموارد البشرية الرئيسية

    توفر نظرة عامة على مؤشرات الأداء الرئيسية للموارد البشرية
    """
    template_name = 'hr/dashboard/hr_kpi_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # التحقق من وجود شركة مرتبطة بالمستخدم
        if hasattr(user, 'employee') and user.employee and user.employee.company:
            company = user.employee.company
            context['company'] = company

            # بيانات الفلترة
            today = date.today()
            context['filter_year'] = int(self.request.GET.get('year', today.year))
            context['filter_month'] = int(self.request.GET.get('month', today.month))

            year = context['filter_year']
            month = context['filter_month']

            # تحديد فترة التقرير
            first_day = date(year, month, 1)
            last_day = date(year, month, calendar.monthrange(year, month)[1])

            context['period_start'] = first_day
            context['period_end'] = last_day

            # مؤشرات الأداء الرئيسية
            kpi_data = self.get_hr_kpi_data(company, first_day, last_day)
            context.update(kpi_data)

            # سنوات التقارير (للفلاتر)
            current_year = date.today().year
            context['years'] = list(range(current_year - 5, current_year + 1))

        return context

    def get_hr_kpi_data(self, company, start_date, end_date):
        """
        الحصول على بيانات مؤشرات الأداء الرئيسية للموارد البشرية
        """
        # إحصائيات عامة للموظفين
        employees = Employee.objects.filter(company=company)
        active_employees = employees.filter(is_active=True)

        # 1. معدل دوران الموظفين (Turnover Rate)
        # عدد الموظفين في بداية الفترة
        employees_start = employees.filter(
            joining_date__lt=start_date
        ).filter(
            Q(termination_date__gt=start_date) | Q(termination_date__isnull=True)
        ).count()

        # عدد الموظفين في نهاية الفترة
        employees_end = employees.filter(
            joining_date__lte=end_date
        ).filter(
            Q(termination_date__gt=end_date) | Q(termination_date__isnull=True)
        ).count()

        # متوسط عدد الموظفين خلال الفترة
        avg_employees = (employees_start + employees_end) / 2 if (employees_start + employees_end) > 0 else 0

        # عدد الموظفين الذين تركوا العمل خلال الفترة
        terminations = employees.filter(
            termination_date__gte=start_date,
            termination_date__lte=end_date
        ).count()

        # حساب معدل الدوران
        turnover_rate = (terminations / avg_employees) * 100 if avg_employees > 0 else 0

        # 2. معدل التوظيف الجديد (New Hire Rate)
        new_hires = employees.filter(
            joining_date__gte=start_date,
            joining_date__lte=end_date
        ).count()

        new_hire_rate = (new_hires / avg_employees) * 100 if avg_employees > 0 else 0

        # 3. معدل الغياب (Absenteeism Rate)
        # إجمالي أيام العمل المتوقعة لجميع الموظفين
        business_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 0-4 هي أيام الإثنين إلى الجمعة
                business_days += 1
            current_date += timedelta(days=1)

        expected_attendance_days = active_employees.count() * business_days

        # إجمالي أيام الغياب (بدون عذر)
        absent_days = AttendanceRecord.objects.filter(
            company=company,
            attendance_date__gte=start_date,
            attendance_date__lte=end_date,
            status=AttendanceStatus.ABSENT,
            is_approved=False
        ).count()

        absenteeism_rate = (absent_days / expected_attendance_days) * 100 if expected_attendance_days > 0 else 0

        # 4. معدل الحضور (Attendance Rate)
        # إجمالي أيام الحضور الفعلية
        present_days = AttendanceRecord.objects.filter(
            company=company,
            attendance_date__gte=start_date,
            attendance_date__lte=end_date,
            status=AttendanceStatus.PRESENT
        ).count()

        attendance_rate = (present_days / expected_attendance_days) * 100 if expected_attendance_days > 0 else 0

        # 5. معدل التأخير (Tardiness Rate)
        late_records = AttendanceRecord.objects.filter(
            company=company,
            attendance_date__gte=start_date,
            attendance_date__lte=end_date,
            status=AttendanceStatus.PRESENT,
            late_minutes__gt=0
        )

        late_days = late_records.count()
        tardiness_rate = (late_days / present_days) * 100 if present_days > 0 else 0

        # متوسط دقائق التأخير لكل موظف
        avg_late_minutes = late_records.aggregate(avg=Avg('late_minutes'))['avg'] or 0

        # 6. معدل استخدام الإجازات (Leave Utilization Rate)
        # إجمالي أيام الإجازات المتاحة
        leave_balances = LeaveBalance.objects.filter(
            company=company,
            year=start_date.year,
            is_active=True
        ).aggregate(
            total_allocated=Sum('allocated_days'),
            total_additional=Sum('additional_days'),
            total_taken=Sum('taken_days')
        )

        total_allocated_days = (leave_balances['total_allocated'] or 0) + (leave_balances['total_additional'] or 0)
        total_taken_days = leave_balances['total_taken'] or 0

        leave_utilization_rate = (total_taken_days / total_allocated_days) * 100 if total_allocated_days > 0 else 0

        # 7. وقت الاستجابة لطلبات الإجازة (Leave Request Response Time)
        # حساب متوسط الوقت بين تقديم طلب الإجازة والرد عليه
        leave_requests = LeaveRequest.objects.filter(
            company=company,
            created_at__gte=start_date,
            created_at__lte=end_date,
            status__in=['approved', 'rejected']
        )

        total_response_time = timedelta(0)
        count_with_response = 0

        for request in leave_requests:
            if request.approved_at:
                response_time = request.approved_at - request.created_at
                total_response_time += response_time
                count_with_response += 1

        avg_leave_response_hours = (total_response_time.total_seconds() / 3600) / count_with_response if count_with_response > 0 else 0

        # 8. معدل اكتمال التدريب (Training Completion Rate)
        # هذا المؤشر يتطلب وجود نظام تدريب مرتبط
        # هنا نضع قيم افتراضية للتوضيح
        training_completion_rate = 75.5

        # 9. تكلفة التوظيف لكل موظف جديد (Cost Per Hire)
        # هذا المؤشر يتطلب بيانات تكاليف التوظيف
        # هنا نضع قيم افتراضية للتوضيح
        cost_per_hire = 5000

        # 10. مؤشر رضا الموظفين (Employee Satisfaction Index)
        # هذا المؤشر يتطلب استبيانات رضا الموظفين
        # هنا نضع قيم افتراضية للتوضيح
        employee_satisfaction = 82.3

        # تجميع كل المؤشرات
        kpi_data = {
            'employees_count': {
                'total': active_employees.count(),
                'start': employees_start,
                'end': employees_end,
                'new_hires': new_hires,
                'terminations': terminations
            },
            'turnover_kpi': {
                'rate': round(turnover_rate, 1),
                'status': self.get_kpi_status(turnover_rate, 10, 5, 'reverse'),  # أقل أفضل
                'trend': self.get_kpi_trend(company, 'turnover', start_date, turnover_rate)
            },
            'new_hire_kpi': {
                'rate': round(new_hire_rate, 1),
                'status': self.get_kpi_status(new_hire_rate, 5, 10),  # أعلى أفضل
                'trend': self.get_kpi_trend(company, 'new_hire', start_date, new_hire_rate)
            },
            'attendance_kpi': {
                'rate': round(attendance_rate, 1),
                'status': self.get_kpi_status(attendance_rate, 90, 95),  # أعلى أفضل
                'trend': self.get_kpi_trend(company, 'attendance', start_date, attendance_rate)
            },
            'absenteeism_kpi': {
                'rate': round(absenteeism_rate, 1),
                'status': self.get_kpi_status(absenteeism_rate, 5, 2, 'reverse'),  # أقل أفضل
                'trend': self.get_kpi_trend(company, 'absenteeism', start_date, absenteeism_rate)
            },
            'tardiness_kpi': {
                'rate': round(tardiness_rate, 1),
                'avg_minutes': round(avg_late_minutes, 1),
                'status': self.get_kpi_status(tardiness_rate, 10, 5, 'reverse'),  # أقل أفضل
                'trend': self.get_kpi_trend(company, 'tardiness', start_date, tardiness_rate)
            },
            'leave_kpi': {
                'utilization_rate': round(leave_utilization_rate, 1),
                'response_hours': round(avg_leave_response_hours, 1),
                'status': self.get_kpi_status(avg_leave_response_hours, 48, 24, 'reverse'),  # أقل أفضل
                'trend': self.get_kpi_trend(company, 'leave_response', start_date, avg_leave_response_hours)
            },
            'other_kpi': {
                'training_completion': training_completion_rate,
                'cost_per_hire': cost_per_hire,
                'employee_satisfaction': employee_satisfaction
            }
        }

        return kpi_data

    def get_kpi_status(self, value, threshold_warning, threshold_success, direction='normal'):
        """
        تحديد حالة المؤشر (نجاح، تحذير، خطر) بناءً على القيمة والعتبات

        direction: 'normal' تعني أن القيمة الأعلى أفضل، 'reverse' تعني أن القيمة الأقل أفضل
        """
        if direction == 'normal':
            if value >= threshold_success:
                return 'success'
            elif value >= threshold_warning:
                return 'warning'
            else:
                return 'danger'
        else:  # reverse
            if value <= threshold_success:
                return 'success'
            elif value <= threshold_warning:
                return 'warning'
            else:
                return 'danger'

    def get_kpi_trend(self, company, kpi_type, current_date, current_value):
        """
        تحديد اتجاه المؤشر (تحسن، تدهور، استقرار) بالمقارنة مع الشهر السابق
        """
        # تحديد الشهر السابق
        if current_date.month == 1:
            previous_month = 12
            previous_year = current_date.year - 1
        else:
            previous_month = current_date.month - 1
            previous_year = current_date.year

        # قيمة افتراضية للشهر السابق (في التطبيق الفعلي، يجب استرجاعها من قاعدة البيانات)
        # هنا نضع قيمة مع تغيير عشوائي بسيط لتوضيح الاتجاه
        import random
        variation = random.uniform(-10, 10)
        previous_value = max(0, current_value + variation)

        # تحديد الاتجاه
        if current_value > previous_value * 1.05:  # زيادة بنسبة 5% أو أكثر
            trend = 'up'
        elif current_value < previous_value * 0.95:  # انخفاض بنسبة 5% أو أكثر
            trend = 'down'
        else:
            trend = 'stable'

        # تحديد ما إذا كان الاتجاه إيجابيًا أم سلبيًا
        positive_kpis = ['new_hire', 'attendance']  # المؤشرات التي تكون الزيادة فيها إيجابية
        negative_kpis = ['turnover', 'absenteeism', 'tardiness', 'leave_response']  # المؤشرات التي تكون الزيادة فيها سلبية

        is_positive = False

        if kpi_type in positive_kpis and trend == 'up':
            is_positive = True
        elif kpi_type in positive_kpis and trend == 'down':
            is_positive = False
        elif kpi_type in negative_kpis and trend == 'up':
            is_positive = False
        elif kpi_type in negative_kpis and trend == 'down':
            is_positive = True
        else:
            is_positive = True  # استقرار نعتبره إيجابيًا

        return {
            'direction': trend,
            'is_positive': is_positive,
            'percentage': round(abs((current_value - previous_value) / previous_value * 100) if previous_value > 0 else 0, 1)
        }


class DepartmentKpiView(LoginRequiredMixin, TemplateView):
    """
    لوحة قياس أداء الأقسام

    توفر مقارنة بين أداء الأقسام المختلفة في مؤشرات الأداء الرئيسية
    """
    template_name = 'hr/dashboard/department_kpi_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # التحقق من وجود شركة مرتبطة بالمستخدم
        if hasattr(user, 'employee') and user.employee and user.employee.company:
            company = user.employee.company
            context['company'] = company

            # بيانات الفلترة
            today = date.today()
            context['filter_year'] = int(self.request.GET.get('year', today.year))
            context['filter_month'] = int(self.request.GET.get('month', today.month))

            year = context['filter_year']
            month = context['filter_month']

            # تحديد فترة التقرير
            first_day = date(year, month, 1)
            last_day = date(year, month, calendar.monthrange(year, month)[1])

            context['period_start'] = first_day
            context['period_end'] = last_day

            # الحصول على الأقسام
            departments = company.departments.filter(is_active=True).order_by('name')
            context['departments'] = departments

            # بيانات مؤشرات الأداء الرئيسية لكل قسم
            department_kpi_data = self.get_department_kpi_data(company, departments, first_day, last_day)
            context['department_kpi_data'] = department_kpi_data

            # سنوات التقارير (للفلاتر)
            current_year = date.today().year
            context['years'] = list(range(current_year - 5, current_year + 1))

        return context

    def get_department_kpi_data(self, company, departments, start_date, end_date):
        """
        الحصول على بيانات مؤشرات الأداء الرئيسية لكل قسم
        """
        department_data = []

        # حساب عدد أيام العمل في الفترة
        business_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 0-4 هي أيام الإثنين إلى الجمعة
                business_days += 1
            current_date += timedelta(days=1)

        # حساب المؤشرات لكل قسم
        for department in departments:
            # الموظفين في القسم
            employees = Employee.objects.filter(company=company, department=department)
            active_employees = employees.filter(is_active=True)
            active_count = active_employees.count()

            # مؤشرات القسم
            dept_data = {
                'id': str(department.id),
                'name': department.name,
                'employee_count': active_count,
                'kpi': {}
            }

            # عدد الموظفين في بداية الفترة
            employees_start = employees.filter(
                joining_date__lt=start_date
            ).filter(
                Q(termination_date__gt=start_date) | Q(termination_date__isnull=True)
            ).count()

            # معدل الغياب
            expected_attendance_days = active_count * business_days

            absent_days = AttendanceRecord.objects.filter(
                company=company,
                employee__department=department,
                attendance_date__gte=start_date,
                attendance_date__lte=end_date,
                status=AttendanceStatus.ABSENT,
                is_approved=False
            ).count()

            absenteeism_rate = (absent_days / expected_attendance_days) * 100 if expected_attendance_days > 0 else 0

            # معدل الحضور
            present_days = AttendanceRecord.objects.filter(
                company=company,
                employee__department=department,
                attendance_date__gte=start_date,
                attendance_date__lte=end_date,
                status=AttendanceStatus.PRESENT
            ).count()

            attendance_rate = (present_days / expected_attendance_days) * 100 if expected_attendance_days > 0 else 0

            # معدل التأخير
            late_records = AttendanceRecord.objects.filter(
                company=company,
                employee__department=department,
                attendance_date__gte=start_date,
                attendance_date__lte=end_date,
                status=AttendanceStatus.PRESENT,
                late_minutes__gt=0
            )

            late_days = late_records.count()
            tardiness_rate = (late_days / present_days) * 100 if present_days > 0 else 0

            # تحديث بيانات المؤشرات للقسم
            dept_data['kpi'] = {
                'attendance_rate': round(attendance_rate, 1),
                'absenteeism_rate': round(absenteeism_rate, 1),
                'tardiness_rate': round(tardiness_rate, 1)
            }

            department_data.append(dept_data)

        return department_data


class EmployeePerformanceDashboardView(LoginRequiredMixin, TemplateView):
    """
    لوحة قياس أداء الموظفين

    توفر تحليلاً لأداء الموظفين في مختلف المؤشرات
    """
    template_name = 'hr/dashboard/employee_performance_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # التحقق من وجود شركة مرتبطة بالمستخدم
        if hasattr(user, 'employee') and user.employee and user.employee.company:
            company = user.employee.company
            context['company'] = company

            # بيانات الفلترة
            today = date.today()
            context['filter_year'] = int(self.request.GET.get('year', today.year))
            context['filter_month'] = int(self.request.GET.get('month', today.month))
            context['filter_department'] = self.request.GET.get('department', '')

            year = context['filter_year']
            month = context['filter_month']

            # تحديد فترة التقرير
            first_day = date(year, month, 1)
            last_day = date(year, month, calendar.monthrange(year, month)[1])

            context['period_start'] = first_day
            context['period_end'] = last_day

            # الحصول على الأقسام لفلاتر التقارير
            context['departments'] = company.departments.filter(is_active=True)

            # فلتر الأقسام إن وجد
            department_filter = {}
            if context['filter_department']:
                department_filter['department_id'] = context['filter_department']

            # بيانات أداء الموظفين
            employee_performance_data = self.get_employee_performance_data(
                company, first_day, last_day, department_filter
            )
            context['employee_performance_data'] = employee_performance_data

            # سنوات التقارير (للفلاتر)
            current_year = date.today().year
            context['years'] = list(range(current_year - 5, current_year + 1))

        return context

    def get_employee_performance_data(self, company, start_date, end_date, department_filter):
        """
        الحصول على بيانات أداء الموظفين
        """
        # الموظفين النشطين
        active_employees = Employee.objects.filter(
            company=company,
            is_active=True,
            **department_filter
        ).select_related('department', 'job_position')

        # حساب عدد أيام العمل في الفترة
        business_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 0-4 هي أيام الإثنين إلى الجمعة
                business_days += 1
            current_date += timedelta(days=1)

        employee_data = []

        for employee in active_employees:
            # بيانات الحضور
            attendance_records = AttendanceRecord.objects.filter(
                employee=employee,
                attendance_date__gte=start_date,
                attendance_date__lte=end_date
            )

            present_days = attendance_records.filter(status=AttendanceStatus.PRESENT).count()
            absent_days = attendance_records.filter(status=AttendanceStatus.ABSENT).count()
            leave_days = attendance_records.filter(status=AttendanceStatus.LEAVE).count()
            late_days = attendance_records.filter(status=AttendanceStatus.PRESENT, late_minutes__gt=0).count()

            # بيانات التأخير
            total_late_minutes = attendance_records.filter(
                status=AttendanceStatus.PRESENT, 
                late_minutes__gt=0
            ).aggregate(total=Sum('late_minutes'))['total'] or 0

            # حساب نسبة الحضور
            attendance_rate = (present_days / business_days) * 100 if business_days > 0 else 0

            # حساب معدل التأخير
            tardiness_rate = (late_days / present_days) * 100 if present_days > 0 else 0

            # بيانات الإجازات
            leave_requests = LeaveRequest.objects.filter(
                employee=employee,
                start_date__gte=start_date,
                end_date__lte=end_date,
                status='approved'
            )

            total_leave_days = leave_requests.aggregate(total=Sum('days'))['total'] or 0

            # إنشاء بيانات الأداء للموظف
            emp_data = {
                'id': str(employee.id),
                'employee_id': employee.employee_id,
                'name': employee.full_name,
                'department': employee.department.name if employee.department else '',
                'job_position': employee.job_position.name if employee.job_position else '',
                'attendance_stats': {
                    'present_days': present_days,
                    'absent_days': absent_days,
                    'leave_days': leave_days,
                    'late_days': late_days,
                    'attendance_rate': round(attendance_rate, 1),
                    'tardiness_rate': round(tardiness_rate, 1),
                    'total_late_minutes': total_late_minutes
                },
                'leave_stats': {
                    'total_leave_days': total_leave_days,
                    'leave_requests': leave_requests.count()
                }
            }

            employee_data.append(emp_data)

        return employee_data
