"""
خدمات نظام التقارير الشامل
===========================

يحتوي على جميع خدمات إنتاج وإدارة التقارير لأنظمة الموارد البشرية
"""

from django.db import models, connection
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import date, datetime, timedelta
from decimal import Decimal
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False
import json
import logging
from io import BytesIO
import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from .models import ReportTemplate, GeneratedReport, ReportCategory
from employees.models import Employee
from org.models import Department
from attendance.models import EmployeeAttendance, AttendanceSummary
from leaves.models import EmployeeLeave, LeaveBalance, LeaveType
from payrolls.models import PayrollRun, PayrollDetail, EmployeeSalary
from loans.models import EmployeeLoan, LoanInstallment
from training.models import TrainingCourse
from evaluations.models import EmployeeEvaluation

logger = logging.getLogger(__name__)


class ReportDataService:
    """خدمة استخراج البيانات للتقارير"""

    def __init__(self):
        """__init__ function"""
        self.cache = {}

    def get_attendance_data(self, start_date, end_date, employee_ids=None, department_ids=None):
        """استخراج بيانات الحضور"""
        queryset = EmployeeAttendance.objects.filter(
            att_date__range=[start_date, end_date]
        ).select_related('emp', 'emp__dept')

        if employee_ids:
            queryset = queryset.filter(emp_id__in=employee_ids)

        if department_ids:
            queryset = queryset.filter(emp__dept_id__in=department_ids)

        # إحصائيات أساسية
        stats = queryset.aggregate(
            total_records=Count('att_id'),
            present_count=Count('att_id', filter=Q(status='Present')),
            absent_count=Count('att_id', filter=Q(status='Absent')),
            late_count=Count('att_id', filter=Q(status='Late')),
            total_employees=Count('emp', distinct=True)
        )

        # تفاصيل حسب الموظف
        employee_stats = queryset.values(
            'emp__emp_id', 'emp__first_name', 'emp__last_name',
            'emp__emp_code', 'emp__dept__dept_name'
        ).annotate(
            total_days=Count('att_id'),
            present_days=Count('att_id', filter=Q(status='Present')),
            absent_days=Count('att_id', filter=Q(status='Absent')),
            late_days=Count('att_id', filter=Q(status='Late')),
            attendance_rate=models.Case(
                models.When(total_days__gt=0, then=F('present_days') * 100.0 / F('total_days')),
                default=0,
                output_field=models.FloatField()
            )
        ).order_by('emp__emp_code')

        # تفاصيل حسب القسم
        department_stats = queryset.values('emp__dept__dept_name').annotate(
            total_employees=Count('emp', distinct=True),
            total_records=Count('att_id'),
            present_count=Count('att_id', filter=Q(status='Present')),
            absent_count=Count('att_id', filter=Q(status='Absent')),
            late_count=Count('att_id', filter=Q(status='Late')),
            attendance_rate=models.Case(
                models.When(total_records__gt=0, then=F('present_count') * 100.0 / F('total_records')),
                default=0,
                output_field=models.FloatField()
            )
        ).order_by('-attendance_rate')

        return {
            'summary': stats,
            'employee_details': list(employee_stats),
            'department_summary': list(department_stats),
            'date_range': {'start': start_date, 'end': end_date}
        }

    def get_leave_data(self, start_date, end_date, employee_ids=None, department_ids=None):
        """استخراج بيانات الإجازات"""
        queryset = EmployeeLeave.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).select_related('emp', 'emp__dept', 'leave_type')

        if employee_ids:
            queryset = queryset.filter(emp_id__in=employee_ids)

        if department_ids:
            queryset = queryset.filter(emp__dept_id__in=department_ids)

        # إحصائيات أساسية
        stats = queryset.aggregate(
            total_leaves=Count('leave_id'),
            approved_leaves=Count('leave_id', filter=Q(status='Approved')),
            pending_leaves=Count('leave_id', filter=Q(status='Pending')),
            rejected_leaves=Count('leave_id', filter=Q(status='Rejected')),
            total_days=Sum(F('end_date') - F('start_date') + 1),
            unique_employees=Count('emp', distinct=True)
        )

        # تفاصيل حسب نوع الإجازة
        leave_type_stats = queryset.values(
            'leave_type__leave_name', 'leave_type__is_paid'
        ).annotate(
            count=Count('leave_id'),
            total_days=Sum(F('end_date') - F('start_date') + 1),
            approved_count=Count('leave_id', filter=Q(status='Approved'))
        ).order_by('-count')

        # تفاصيل حسب الموظف
        employee_stats = queryset.values(
            'emp__emp_id', 'emp__first_name', 'emp__last_name',
            'emp__emp_code', 'emp__dept__dept_name'
        ).annotate(
            total_leaves=Count('leave_id'),
            approved_leaves=Count('leave_id', filter=Q(status='Approved')),
            total_days=Sum(F('end_date') - F('start_date') + 1),
            paid_days=Sum(
                F('end_date') - F('start_date') + 1,
                filter=Q(leave_type__is_paid=True, status='Approved')
            ),
            unpaid_days=Sum(
                F('end_date') - F('start_date') + 1,
                filter=Q(leave_type__is_paid=False, status='Approved')
            )
        ).order_by('emp__emp_code')

        return {
            'summary': stats,
            'leave_type_breakdown': list(leave_type_stats),
            'employee_details': list(employee_stats),
            'date_range': {'start': start_date, 'end': end_date}
        }

    def get_payroll_data(self, start_date, end_date, employee_ids=None, department_ids=None):
        """استخراج بيانات الرواتب"""
        queryset = PayrollDetail.objects.filter(
            run__period_start__lte=end_date,
            run__period_end__gte=start_date
        ).select_related('emp', 'emp__dept', 'run')

        if employee_ids:
            queryset = queryset.filter(emp_id__in=employee_ids)

        if department_ids:
            queryset = queryset.filter(emp__dept_id__in=department_ids)

        # إحصائيات أساسية
        stats = queryset.aggregate(
            total_employees=Count('emp', distinct=True),
            total_payroll_runs=Count('run', distinct=True),
            total_gross=Sum('gross_salary'),
            total_basic=Sum('basic_salary'),
            total_allowances=Sum('total_allowances'),
            total_deductions=Sum('total_deductions'),
            total_net=Sum('net_salary'),
            avg_net_salary=Avg('net_salary'),
            total_overtime=Sum('overtime_amount'),
            total_bonuses=Sum('bonus_amount')
        )

        # تفاصيل حسب الموظف
        employee_stats = queryset.values(
            'emp__emp_id', 'emp__first_name', 'emp__last_name',
            'emp__emp_code', 'emp__dept__dept_name'
        ).annotate(
            payroll_count=Count('payroll_detail_id'),
            avg_gross=Avg('gross_salary'),
            avg_net=Avg('net_salary'),
            total_gross=Sum('gross_salary'),
            total_net=Sum('net_salary'),
            total_overtime=Sum('overtime_amount'),
            total_bonuses=Sum('bonus_amount'),
            total_deductions=Sum('total_deductions')
        ).order_by('emp__emp_code')

        # تفاصيل حسب القسم
        department_stats = queryset.values('emp__dept__dept_name').annotate(
            employee_count=Count('emp', distinct=True),
            total_gross=Sum('gross_salary'),
            total_net=Sum('net_salary'),
            avg_salary=Avg('net_salary'),
            total_overtime=Sum('overtime_amount'),
            total_bonuses=Sum('bonus_amount')
        ).order_by('-total_net')

        return {
            'summary': stats,
            'employee_details': list(employee_stats),
            'department_summary': list(department_stats),
            'date_range': {'start': start_date, 'end': end_date}
        }

    def get_employee_data(self, employee_ids=None, department_ids=None, status_filter=None):
        """استخراج بيانات الموظفين"""
        queryset = Employee.objects.select_related('dept', 'position')

        if employee_ids:
            queryset = queryset.filter(emp_id__in=employee_ids)

        if department_ids:
            queryset = queryset.filter(dept_id__in=department_ids)

        if status_filter:
            queryset = queryset.filter(emp_status=status_filter)

        # إحصائيات أساسية
        stats = queryset.aggregate(
            total_employees=Count('emp_id'),
            active_employees=Count('emp_id', filter=Q(emp_status='Active')),
            inactive_employees=Count('emp_id', filter=Q(emp_status='Inactive')),
            male_employees=Count('emp_id', filter=Q(gender='M')),
            female_employees=Count('emp_id', filter=Q(gender='F'))
        )

        # توزيع حسب القسم
        department_distribution = queryset.values('dept__dept_name').annotate(
            count=Count('emp_id'),
            active_count=Count('emp_id', filter=Q(emp_status='Active'))
        ).order_by('-count')

        # توزيع حسب المنصب
        position_distribution = queryset.values('position__name').annotate(
            count=Count('emp_id')
        ).order_by('-count')

        # توزيع حسب العمر
        current_year = date.today().year
        age_distribution = queryset.extra(
            select={
                'age_group': f"""
                    CASE
                        WHEN {current_year} - YEAR(birth_date) < 25 THEN 'أقل من 25'
                        WHEN {current_year} - YEAR(birth_date) < 35 THEN '25-34'
                        WHEN {current_year} - YEAR(birth_date) < 45 THEN '35-44'
                        WHEN {current_year} - YEAR(birth_date) < 55 THEN '45-54'
                        ELSE '55 وأكثر'
                    END
                """
            }
        ).values('age_group').annotate(count=Count('emp_id')).order_by('age_group')

        return {
            'summary': stats,
            'department_distribution': list(department_distribution),
            'position_distribution': list(position_distribution),
            'age_distribution': list(age_distribution)
        }


class ReportGeneratorService:
    """خدمة إنتاج التقارير"""

    def __init__(self):
        """__init__ function"""
        self.data_service = ReportDataService()

    def generate_attendance_report(self, parameters):
        """إنتاج تقرير الحضور"""
        start_date = parameters.get('start_date')
        end_date = parameters.get('end_date')
        format_type = parameters.get('format', 'html')
        employee_ids = parameters.get('employee_ids')
        department_ids = parameters.get('department_ids')

        # استخراج البيانات
        data = self.data_service.get_attendance_data(
            start_date, end_date, employee_ids, department_ids
        )

        if format_type == 'html':
            return self._generate_html_report('attendance_report.html', data)
        elif format_type == 'excel':
            return self._generate_excel_attendance_report(data)
        elif format_type == 'pdf':
            return self._generate_pdf_attendance_report(data)
        elif format_type == 'csv':
            return self._generate_csv_report(data['employee_details'])
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def generate_payroll_report(self, parameters):
        """إنتاج تقرير الرواتب"""
        start_date = parameters.get('start_date')
        end_date = parameters.get('end_date')
        format_type = parameters.get('format', 'html')
        employee_ids = parameters.get('employee_ids')
        department_ids = parameters.get('department_ids')

        # استخراج البيانات
        data = self.data_service.get_payroll_data(
            start_date, end_date, employee_ids, department_ids
        )

        if format_type == 'html':
            return self._generate_html_report('payroll_report.html', data)
        elif format_type == 'excel':
            return self._generate_excel_payroll_report(data)
        elif format_type == 'pdf':
            return self._generate_pdf_payroll_report(data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def generate_leave_report(self, parameters):
        """إنتاج تقرير الإجازات"""
        start_date = parameters.get('start_date')
        end_date = parameters.get('end_date')
        format_type = parameters.get('format', 'html')
        employee_ids = parameters.get('employee_ids')
        department_ids = parameters.get('department_ids')

        # استخراج البيانات
        data = self.data_service.get_leave_data(
            start_date, end_date, employee_ids, department_ids
        )

        if format_type == 'html':
            return self._generate_html_report('leave_report.html', data)
        elif format_type == 'excel':
            return self._generate_excel_leave_report(data)
        elif format_type == 'pdf':
            return self._generate_pdf_leave_report(data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def generate_comprehensive_hr_report(self, parameters):
        """إنتاج تقرير شامل للموارد البشرية"""
        start_date = parameters.get('start_date')
        end_date = parameters.get('end_date')
        format_type = parameters.get('format', 'html')

        # جمع البيانات من جميع الأنظمة
        attendance_data = self.data_service.get_attendance_data(start_date, end_date)
        leave_data = self.data_service.get_leave_data(start_date, end_date)
        payroll_data = self.data_service.get_payroll_data(start_date, end_date)
        employee_data = self.data_service.get_employee_data()

        comprehensive_data = {
            'attendance': attendance_data,
            'leaves': leave_data,
            'payroll': payroll_data,
            'employees': employee_data,
            'period': {'start': start_date, 'end': end_date},
            'generated_at': timezone.now()
        }

        if format_type == 'html':
            return self._generate_html_report('comprehensive_hr_report.html', comprehensive_data)
        elif format_type == 'pdf':
            return self._generate_pdf_comprehensive_report(comprehensive_data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _generate_html_report(self, template_name, data):
        """إنتاج تقرير HTML"""
        html_content = render_to_string(f'reports/{template_name}', {'data': data})
        return {
            'content': html_content,
            'content_type': 'text/html',
            'filename': f"report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.html"
        }

    def _generate_excel_attendance_report(self, data):
        """إنتاج تقرير حضور Excel"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)

        # ورقة الملخص
        summary_sheet = workbook.add_worksheet('ملخص الحضور')
        bold = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})

        # كتابة الملخص
        summary_sheet.write('A1', 'إحصائيات الحضور', bold)
        summary_sheet.write('A3', 'إجمالي السجلات')
        summary_sheet.write('B3', data['summary']['total_records'])
        summary_sheet.write('A4', 'عدد الحضور')
        summary_sheet.write('B4', data['summary']['present_count'])
        summary_sheet.write('A5', 'عدد الغياب')
        summary_sheet.write('B5', data['summary']['absent_count'])
        summary_sheet.write('A6', 'عدد المتأخرين')
        summary_sheet.write('B6', data['summary']['late_count'])

        # ورقة تفاصيل الموظفين
        detail_sheet = workbook.add_worksheet('تفاصيل الموظفين')
        headers = ['رمز الموظف', 'الاسم', 'القسم', 'إجمالي الأيام', 'أيام الحضور', 'أيام الغياب', 'معدل الحضور %']

        for col, header in enumerate(headers):
            detail_sheet.write(0, col, header, bold)

        for row, employee in enumerate(data['employee_details'], 1):
            detail_sheet.write(row, 0, employee['emp__emp_code'])
            detail_sheet.write(row, 1, f"{employee['emp__first_name']} {employee['emp__last_name']}")
            detail_sheet.write(row, 2, employee['emp__dept__dept_name'])
            detail_sheet.write(row, 3, employee['total_days'])
            detail_sheet.write(row, 4, employee['present_days'])
            detail_sheet.write(row, 5, employee['absent_days'])
            detail_sheet.write(row, 6, f"{employee['attendance_rate']:.1f}%")

        workbook.close()
        output.seek(0)

        return {
            'content': output.getvalue(),
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'filename': f"attendance_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }

    def _generate_pdf_attendance_report(self, data):
        """إنتاج تقرير حضور PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # عنوان التقرير
        title = Paragraph("تقرير الحضور والانصراف", styles['Title'])
        elements.append(title)

        # ملخص الإحصائيات
        summary_data = [
            ['البيان', 'القيمة'],
            ['إجمالي السجلات', str(data['summary']['total_records'])],
            ['عدد الحضور', str(data['summary']['present_count'])],
            ['عدد الغياب', str(data['summary']['absent_count'])],
            ['عدد المتأخرين', str(data['summary']['late_count'])],
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(summary_table)

        doc.build(elements)
        buffer.seek(0)

        return {
            'content': buffer.getvalue(),
            'content_type': 'application/pdf',
            'filename': f"attendance_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        }

    def _generate_csv_report(self, data):
        """إنتاج تقرير CSV"""
        output = BytesIO()

        # تحويل البيانات إلى DataFrame
        df = pd.DataFrame(data)

        # حفظ كـ CSV
        csv_content = df.to_csv(index=False, encoding='utf-8-sig')

        return {
            'content': csv_content.encode('utf-8-sig'),
            'content_type': 'text/csv',
            'filename': f"report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }


class ReportSchedulerService:
    """خدمة جدولة التقارير"""

    def __init__(self):
        """__init__ function"""
        self.generator = ReportGeneratorService()

    def process_scheduled_reports(self):
        """معالجة التقارير المجدولة"""
        from .models import ReportSchedule

        now = timezone.now()
        due_schedules = ReportSchedule.objects.filter(
            status='active',
            next_run__lte=now
        )

        for schedule in due_schedules:
            try:
                self._execute_scheduled_report(schedule)
                self._update_next_run(schedule)
            except Exception as e:
                logger.error(f"Error executing scheduled report {schedule.schedule_id}: {str(e)}")
                schedule.error_count += 1
                schedule.last_error = str(e)
                schedule.save()

    def _execute_scheduled_report(self, schedule):
        """تنفيذ تقرير مجدول"""
        # إنشاء سجل تقرير جديد
        report = GeneratedReport.objects.create(
            template=schedule.template,
            schedule=schedule,
            name=f"{schedule.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            parameters=schedule.parameters,
            output_format=schedule.output_format,
            status='processing'
        )

        try:
            # إنتاج التقرير
            result = self._generate_report_by_template(schedule.template, schedule.parameters)

            # حفظ الملف
            file_path = self._save_report_file(report, result)

            # تحديث سجل التقرير
            report.file_path = file_path
            report.file_size = len(result['content'])
            report.status = 'completed'
            report.completed_at = timezone.now()
            report.save()

            # إرسال بريد إلكتروني إذا كان مطلوباً
            if schedule.email_recipients:
                self._send_report_email(schedule, report)

            # تحديث إحصائيات الجدولة
            schedule.run_count += 1
            schedule.last_run = timezone.now()
            schedule.save()

        except Exception as e:
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
            raise

    def _generate_report_by_template(self, template, parameters):
        """إنتاج تقرير حسب القالب"""
        # يمكن إضافة منطق إضافي هنا حسب نوع التقرير
        if 'attendance' in template.code:
            return self.generator.generate_attendance_report(parameters)
        elif 'payroll' in template.code:
            return self.generator.generate_payroll_report(parameters)
        elif 'leave' in template.code:
            return self.generator.generate_leave_report(parameters)
        else:
            raise ValueError(f"Unknown report template: {template.code}")


class ReportAnalyticsService:
    """خدمة تحليلات التقارير"""

    def get_usage_statistics(self):
        """إحصائيات استخدام التقارير"""
        from .models import GeneratedReport, ReportAccessLog

        # إحصائيات التقارير المُنتجة
        report_stats = GeneratedReport.objects.aggregate(
            total_reports=Count('report_id'),
            completed_reports=Count('report_id', filter=Q(status='completed')),
            failed_reports=Count('report_id', filter=Q(status='failed')),
            total_downloads=Sum('download_count'),
            avg_execution_time=Avg('execution_time')
        )

        # التقارير الأكثر استخداماً
        popular_templates = GeneratedReport.objects.values(
            'template__name'
        ).annotate(
            generation_count=Count('report_id'),
            total_downloads=Sum('download_count')
        ).order_by('-generation_count')[:10]

        # إحصائيات الوصول
        access_stats = ReportAccessLog.objects.aggregate(
            total_accesses=Count('log_id'),
            unique_users=Count('user', distinct=True),
            successful_accesses=Count('log_id', filter=Q(success=True))
        )

        return {
            'report_statistics': report_stats,
            'popular_templates': list(popular_templates),
            'access_statistics': access_stats
        }
