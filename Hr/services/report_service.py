"""
خدمة التقارير والتحليلات للموارد البشرية
"""

from django.db.models import Count, Q, Avg, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import json

from Hr.models.employee.employee_models import Employee
from Hr.models.organization.department_models import Department
from Hr.models.organization.position_models import Position
from Hr.models.attendance.attendance_record_models import AttendanceRecord
from Hr.models.payroll.employee_salary_structure_models import EmployeeSalaryStructure


class ReportService:
    """خدمة إنشاء التقارير والتحليلات"""
    
    @staticmethod
    def generate_employee_report(filters=None, export_format='json'):
        """
        إنشاء تقرير شامل للموظفين
        """
        if filters is None:
            filters = {}
        
        # بناء الاستعلام الأساسي
        queryset = Employee.objects.select_related(
            'company', 'branch', 'department', 'job_position'
        )
        
        # تطبيق الفلاتر
        if filters.get('company_id'):
            queryset = queryset.filter(company_id=filters['company_id'])
        
        if filters.get('department_id'):
            queryset = queryset.filter(department_id=filters['department_id'])
        
        if filters.get('branch_id'):
            queryset = queryset.filter(branch_id=filters['branch_id'])
        
        if filters.get('job_position_id'):
            queryset = queryset.filter(job_position_id=filters['job_position_id'])
        
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        
        if filters.get('employment_type'):
            queryset = queryset.filter(employment_type=filters['employment_type'])
        
        # تطبيق فلاتر التاريخ
        if filters.get('hire_date_from'):
            queryset = queryset.filter(hire_date__gte=filters['hire_date_from'])
        
        if filters.get('hire_date_to'):
            queryset = queryset.filter(hire_date__lte=filters['hire_date_to'])
        
        # إعداد البيانات للتقرير
        report_data = []
        for employee in queryset:
            report_data.append({
                'employee_number': employee.employee_number,
                'full_name': employee.full_name,
                'email': employee.email,
                'phone': employee.phone,
                'mobile': employee.mobile,
                'company': employee.company.name if employee.company else '',
                'branch': employee.branch.name if employee.branch else '',
                'department': employee.department.name if employee.department else '',
                'job_position': employee.job_position.title if employee.job_position else '',
                'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
                'employment_type': employee.get_employment_type_display(),
                'status': employee.get_status_display(),
                'basic_salary': float(employee.basic_salary) if employee.basic_salary else 0,
                'years_of_service': employee.years_of_service,
                'age': employee.age,
                'gender': employee.get_gender_display() if employee.gender else '',
                'nationality': employee.nationality,
                'marital_status': employee.get_marital_status_display() if employee.marital_status else '',
            })
        
        return {
            'title': 'تقرير الموظفين',
            'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_records': len(report_data),
            'filters_applied': filters,
            'data': report_data
        }
    
    @staticmethod
    def generate_attendance_report(start_date, end_date, filters=None):
        """
        إنشاء تقرير الحضور والغياب
        """
        if filters is None:
            filters = {}
        
        # بناء الاستعلام الأساسي
        queryset = AttendanceRecord.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('employee', 'employee__department', 'employee__job_position')
        
        # تطبيق الفلاتر
        if filters.get('employee_ids'):
            queryset = queryset.filter(employee_id__in=filters['employee_ids'])
        
        if filters.get('department_ids'):
            queryset = queryset.filter(employee__department_id__in=filters['department_ids'])
        
        # إعداد البيانات للتقرير
        report_data = []
        for record in queryset:
            report_data.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'employee_number': record.employee.employee_number,
                'employee_name': record.employee.full_name,
                'department': record.employee.department.name if record.employee.department else '',
                'job_position': record.employee.job_position.title if record.employee.job_position else '',
                'check_in_time': record.check_in_time.strftime('%H:%M:%S') if record.check_in_time else '',
                'check_out_time': record.check_out_time.strftime('%H:%M:%S') if record.check_out_time else '',
                'total_hours': float(record.total_hours) if record.total_hours else 0,
                'overtime_hours': float(record.overtime_hours) if record.overtime_hours else 0,
                'is_late': record.is_late,
                'is_early_departure': record.is_early_departure,
                'status': 'حاضر' if record.check_in_time else 'غائب',
                'notes': record.notes or ''
            })
        
        # حساب الإحصائيات
        total_records = len(report_data)
        present_count = sum(1 for r in report_data if r['check_in_time'])
        absent_count = total_records - present_count
        late_count = sum(1 for r in report_data if r['is_late'])
        total_work_hours = sum(r['total_hours'] for r in report_data)
        total_overtime_hours = sum(r['overtime_hours'] for r in report_data)
        
        return {
            'title': 'تقرير الحضور والغياب',
            'period': f"من {start_date} إلى {end_date}",
            'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': {
                'total_records': total_records,
                'present_count': present_count,
                'absent_count': absent_count,
                'late_count': late_count,
                'attendance_rate': round((present_count / total_records * 100), 2) if total_records > 0 else 0,
                'total_work_hours': total_work_hours,
                'total_overtime_hours': total_overtime_hours,
                'average_daily_hours': round(total_work_hours / present_count, 2) if present_count > 0 else 0
            },
            'data': report_data
        }
    
    @staticmethod
    def generate_payroll_report(payroll_period_id, filters=None):
        """
        إنشاء تقرير كشف الرواتب
        """
        from Hr.models.payroll.payroll_entry_models import PayrollEntry
        from Hr.models.payroll.payroll_period_models import PayrollPeriod
        
        try:
            payroll_period = PayrollPeriod.objects.get(id=payroll_period_id)
        except PayrollPeriod.DoesNotExist:
            return {'error': 'فترة الراتب غير موجودة'}
        
        if filters is None:
            filters = {}
        
        # بناء الاستعلام الأساسي
        queryset = PayrollEntry.objects.filter(
            payroll_period=payroll_period
        ).select_related('employee', 'employee__department', 'employee__job_position')
        
        # تطبيق الفلاتر
        if filters.get('department_ids'):
            queryset = queryset.filter(employee__department_id__in=filters['department_ids'])
        
        if filters.get('employee_ids'):
            queryset = queryset.filter(employee_id__in=filters['employee_ids'])
        
        # إعداد البيانات للتقرير
        report_data = []
        total_basic_salary = 0
        total_gross_salary = 0
        total_deductions = 0
        total_net_salary = 0
        
        for entry in queryset:
            report_data.append({
                'employee_number': entry.employee.employee_number,
                'employee_name': entry.employee.full_name,
                'department': entry.employee.department.name if entry.employee.department else '',
                'job_position': entry.employee.job_position.title if entry.employee.job_position else '',
                'basic_salary': float(entry.basic_salary) if entry.basic_salary else 0,
                'gross_salary': float(entry.gross_salary) if entry.gross_salary else 0,
                'total_deductions': float(entry.total_deductions) if entry.total_deductions else 0,
                'net_salary': float(entry.net_salary) if entry.net_salary else 0,
                'working_days': entry.working_days,
                'present_days': entry.present_days,
                'absent_days': entry.absent_days,
                'leave_days': entry.leave_days,
                'payment_method': entry.get_payment_method_display() if entry.payment_method else '',
                'payment_date': entry.payment_date.strftime('%Y-%m-%d') if entry.payment_date else '',
                'status': entry.get_status_display()
            })
            
            # تجميع الإجماليات
            total_basic_salary += float(entry.basic_salary) if entry.basic_salary else 0
            total_gross_salary += float(entry.gross_salary) if entry.gross_salary else 0
            total_deductions += float(entry.total_deductions) if entry.total_deductions else 0
            total_net_salary += float(entry.net_salary) if entry.net_salary else 0
        
        return {
            'title': 'تقرير كشف الرواتب',
            'payroll_period': {
                'name': payroll_period.name,
                'start_date': payroll_period.start_date.strftime('%Y-%m-%d'),
                'end_date': payroll_period.end_date.strftime('%Y-%m-%d'),
                'payment_date': payroll_period.payment_date.strftime('%Y-%m-%d') if payroll_period.payment_date else ''
            },
            'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': {
                'total_employees': len(report_data),
                'total_basic_salary': total_basic_salary,
                'total_gross_salary': total_gross_salary,
                'total_deductions': total_deductions,
                'total_net_salary': total_net_salary,
                'average_salary': round(total_net_salary / len(report_data), 2) if len(report_data) > 0 else 0
            },
            'data': report_data
        }
    
    @staticmethod
    def generate_leave_report(start_date, end_date, filters=None):
        """
        إنشاء تقرير الإجازات
        """
        from Hr.models.leave.leave_request_models import LeaveRequest
        
        if filters is None:
            filters = {}
        
        # بناء الاستعلام الأساسي
        queryset = LeaveRequest.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).select_related('employee', 'employee__department', 'leave_type')
        
        # تطبيق الفلاتر
        if filters.get('employee_ids'):
            queryset = queryset.filter(employee_id__in=filters['employee_ids'])
        
        if filters.get('department_ids'):
            queryset = queryset.filter(employee__department_id__in=filters['department_ids'])
        
        if filters.get('leave_type_ids'):
            queryset = queryset.filter(leave_type_id__in=filters['leave_type_ids'])
        
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        
        # إعداد البيانات للتقرير
        report_data = []
        total_days = 0
        
        for leave_request in queryset:
            report_data.append({
                'employee_number': leave_request.employee.employee_number,
                'employee_name': leave_request.employee.full_name,
                'department': leave_request.employee.department.name if leave_request.employee.department else '',
                'leave_type': leave_request.leave_type.name,
                'start_date': leave_request.start_date.strftime('%Y-%m-%d'),
                'end_date': leave_request.end_date.strftime('%Y-%m-%d'),
                'days': leave_request.days,
                'status': leave_request.get_status_display(),
                'reason': leave_request.reason or '',
                'approved_by': leave_request.approved_by.get_full_name() if leave_request.approved_by else '',
                'approved_at': leave_request.approved_at.strftime('%Y-%m-%d %H:%M:%S') if leave_request.approved_at else '',
                'created_at': leave_request.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            total_days += leave_request.days
        
        # حساب الإحصائيات حسب نوع الإجازة
        leave_type_stats = {}
        for request in report_data:
            leave_type = request['leave_type']
            if leave_type not in leave_type_stats:
                leave_type_stats[leave_type] = {'count': 0, 'total_days': 0}
            leave_type_stats[leave_type]['count'] += 1
            leave_type_stats[leave_type]['total_days'] += request['days']
        
        return {
            'title': 'تقرير الإجازات',
            'period': f"من {start_date} إلى {end_date}",
            'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': {
                'total_requests': len(report_data),
                'total_days': total_days,
                'average_days_per_request': round(total_days / len(report_data), 2) if len(report_data) > 0 else 0,
                'by_leave_type': leave_type_stats
            },
            'data': report_data
        }
    
    @staticmethod
    def generate_dashboard_statistics():
        """
        إنشاء إحصائيات لوحة التحكم
        """
        from datetime import date, timedelta
        
        today = date.today()
        this_month_start = today.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # إحصائيات الموظفين
        total_employees = Employee.objects.filter(status='active').count()
        new_hires_this_month = Employee.objects.filter(
            hire_date__gte=this_month_start,
            status='active'
        ).count()
        
        # إحصائيات الحضور لليوم
        today_attendance = AttendanceRecord.objects.filter(date=today)
        present_today = today_attendance.filter(check_in_time__isnull=False).count()
        late_today = today_attendance.filter(is_late=True).count()
        
        # إحصائيات الإجازات
        from Hr.models.leave.leave_request_models import LeaveRequest
        pending_leave_requests = LeaveRequest.objects.filter(status='pending').count()
        employees_on_leave_today = LeaveRequest.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).count()
        
        # إحصائيات الرواتب
        from Hr.models.payroll.payroll_period_models import PayrollPeriod
        current_payroll_period = PayrollPeriod.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()
        
        return {
            'employees': {
                'total_active': total_employees,
                'new_hires_this_month': new_hires_this_month,
                'by_department': Employee.objects.filter(status='active').values(
                    'department__name'
                ).annotate(count=Count('id')).order_by('-count')[:5],
                'by_employment_type': Employee.objects.filter(status='active').values(
                    'employment_type'
                ).annotate(count=Count('id'))
            },
            'attendance': {
                'present_today': present_today,
                'late_today': late_today,
                'attendance_rate_today': round((present_today / total_employees * 100), 2) if total_employees > 0 else 0,
                'employees_on_leave': employees_on_leave_today
            },
            'leaves': {
                'pending_requests': pending_leave_requests,
                'employees_on_leave_today': employees_on_leave_today,
                'most_used_leave_types': LeaveRequest.objects.filter(
                    created_at__gte=this_month_start
                ).values('leave_type__name').annotate(
                    count=Count('id')
                ).order_by('-count')[:5]
            },
            'payroll': {
                'current_period': current_payroll_period.name if current_payroll_period else 'غير محدد',
                'period_start': current_payroll_period.start_date.strftime('%Y-%m-%d') if current_payroll_period else '',
                'period_end': current_payroll_period.end_date.strftime('%Y-%m-%d') if current_payroll_period else ''
            },
            'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def export_report_to_csv(report_data, filename=None):
        """
        تصدير التقرير إلى ملف CSV
        """
        import csv
        import io
        
        if not filename:
            filename = f"report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output = io.StringIO()
        
        if report_data.get('data'):
            writer = csv.DictWriter(output, fieldnames=report_data['data'][0].keys())
            writer.writeheader()
            writer.writerows(report_data['data'])
        
        return {
            'filename': filename,
            'content': output.getvalue(),
            'content_type': 'text/csv'
        }
    
    @staticmethod
    def export_report_to_excel(report_data, filename=None):
        """
        تصدير التقرير إلى ملف Excel
        """
        try:
            import pandas as pd
            import io
            
            if not filename:
                filename = f"report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output = io.BytesIO()
            
            if report_data.get('data'):
                df = pd.DataFrame(report_data['data'])
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='التقرير', index=False)
                    
                    # إضافة ورقة للإحصائيات إذا كانت متوفرة
                    if report_data.get('statistics'):
                        stats_df = pd.DataFrame([report_data['statistics']])
                        stats_df.to_excel(writer, sheet_name='الإحصائيات', index=False)
            
            return {
                'filename': filename,
                'content': output.getvalue(),
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            
        except ImportError:
            # إذا لم تكن pandas متوفرة، استخدم openpyxl مباشرة
            from openpyxl import Workbook
            import io
            
            if not filename:
                filename = f"report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            wb = Workbook()
            ws = wb.active
            ws.title = "التقرير"
            
            if report_data.get('data') and len(report_data['data']) > 0:
                # إضافة العناوين
                headers = list(report_data['data'][0].keys())
                ws.append(headers)
                
                # إضافة البيانات
                for row_data in report_data['data']:
                    ws.append(list(row_data.values()))
            
            output = io.BytesIO()
            wb.save(output)
            
            return {
                'filename': filename,
                'content': output.getvalue(),
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            queryset = queryset.filter(hire_date__lte=filters['end_date'])
        
        # الإحصائيات الأساسية
        total_employees = queryset.count()
        active_employees = queryset.filter(is_active=True).count()
        inactive_employees = queryset.filter(is_active=False).count()
        
        # التوزيع حسب القسم
        department_distribution = queryset.values(
            'department__name_ar'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # التوزيع حسب الوظيفة
        position_distribution = queryset.values(
            'position__name_ar'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # التوزيع حسب الجنس
        gender_distribution = queryset.values(
            'gender'
        ).annotate(
            count=Count('id')
        )
        
        # الموظفين الجدد (آخر 30 يوم)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        new_employees = queryset.filter(
            hire_date__gte=thirty_days_ago
        ).count()
        
        return {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': inactive_employees,
            'new_employees': new_employees,
            'departments_count': Department.objects.count(),
            'positions_count': Position.objects.count(),
            'department_distribution': list(department_distribution),
            'position_distribution': list(position_distribution),
            'gender_distribution': list(gender_distribution),
            'employees': list(queryset.values(
                'full_name_ar',
                'employee_number',
                'department__name_ar',
                'position__name_ar',
                'hire_date',
                'is_active'
            )[:100])  # أول 100 موظف
        }
    
    @staticmethod
    def get_employee_details_report(filters=None):
        """
        إنشاء تقرير تفاصيل الموظفين
        """
        if filters is None:
            filters = {}
        
        # بناء الاستعلام
        queryset = Employee.objects.select_related(
            'department',
            'position',
            'branch'
        )
        
        # تطبيق الفلاتر
        if filters.get('department'):
            queryset = queryset.filter(department_id=filters['department'])
        
        if filters.get('branch'):
            queryset = queryset.filter(branch_id=filters['branch'])
        
        if filters.get('position'):
            queryset = queryset.filter(position_id=filters['position'])
        
        if filters.get('status'):
            is_active = filters['status'] == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        # تطبيق فلاتر التاريخ
        if filters.get('start_date'):
            queryset = queryset.filter(hire_date__gte=filters['start_date'])
        
        if filters.get('end_date'):
            queryset = queryset.filter(hire_date__lte=filters['end_date'])
        
        employees_data = []
        for employee in queryset:
            employees_data.append({
                'full_name': employee.full_name_ar,
                'employee_number': employee.employee_number,
                'national_id': employee.national_id,
                'department': employee.department.name_ar if employee.department else '',
                'position': employee.position.name_ar if employee.position else '',
                'branch': employee.branch.name_ar if employee.branch else '',
                'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
                'birth_date': employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else '',
                'gender': employee.get_gender_display(),
                'nationality': employee.nationality,
                'phone': employee.phone,
                'email': employee.email,
                'address': employee.address,
                'is_active': employee.is_active,
                'created_at': employee.created_at.strftime('%Y-%m-%d') if employee.created_at else ''
            })
        
        return {
            'total_employees': queryset.count(),
            'employees': employees_data
        }
    
    @staticmethod
    def get_organizational_structure_report():
        """
        إنشاء تقرير الهيكل التنظيمي
        """
        departments = Department.objects.annotate(
            employee_count=Count('employees')
        ).order_by('name_ar')
        
        structure_data = []
        for dept in departments:
            # الحصول على الوظائف في هذا القسم
            positions = Position.objects.filter(
                employees__department=dept
            ).annotate(
                employee_count=Count('employees')
            ).distinct()
            
            dept_data = {
                'department_name': dept.name_ar,
                'department_code': dept.code,
                'employee_count': dept.employee_count,
                'positions': []
            }
            
            for position in positions:
                dept_data['positions'].append({
                    'position_name': position.name_ar,
                    'position_code': position.code,
                    'employee_count': position.employee_count
                })
            
            structure_data.append(dept_data)
        
        return {
            'total_departments': departments.count(),
            'total_employees': Employee.objects.count(),
            'structure': structure_data
        }
    
    @staticmethod
    def get_new_employees_report(filters=None):
        """
        إنشاء تقرير الموظفين الجدد
        """
        if filters is None:
            filters = {}
        
        # تحديد الفترة الافتراضية (آخر 30 يوم)
        if not filters.get('start_date'):
            filters['start_date'] = timezone.now().date() - timedelta(days=30)
        
        if not filters.get('end_date'):
            filters['end_date'] = timezone.now().date()
        
        # بناء الاستعلام
        queryset = Employee.objects.filter(
            hire_date__gte=filters['start_date'],
            hire_date__lte=filters['end_date']
        ).select_related('department', 'position')
        
        # تطبيق الفلاتر الإضافية
        if filters.get('department'):
            queryset = queryset.filter(department_id=filters['department'])
        
        if filters.get('branch'):
            queryset = queryset.filter(branch_id=filters['branch'])
        
        # الإحصائيات
        total_new = queryset.count()
        
        # التوزيع حسب القسم
        dept_distribution = queryset.values(
            'department__name_ar'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # التوزيع حسب الشهر
        monthly_distribution = queryset.extra(
            select={'month': "strftime('%%Y-%%m', hire_date)"}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        employees_data = []
        for employee in queryset.order_by('-hire_date'):
            employees_data.append({
                'full_name': employee.full_name_ar,
                'employee_number': employee.employee_number,
                'department': employee.department.name_ar if employee.department else '',
                'position': employee.position.name_ar if employee.position else '',
                'hire_date': employee.hire_date.strftime('%Y-%m-%d'),
                'phone': employee.phone,
                'email': employee.email
            })
        
        return {
            'total_new_employees': total_new,
            'period_start': filters['start_date'].strftime('%Y-%m-%d'),
            'period_end': filters['end_date'].strftime('%Y-%m-%d'),
            'department_distribution': list(dept_distribution),
            'monthly_distribution': list(monthly_distribution),
            'employees': employees_data
        }
    
    @staticmethod
    def get_demographics_report(filters=None):
        """
        إنشاء تقرير التركيبة السكانية
        """
        if filters is None:
            filters = {}
        
        # بناء الاستعلام
        queryset = Employee.objects.all()
        
        # تطبيق الفلاتر
        if filters.get('department'):
            queryset = queryset.filter(department_id=filters['department'])
        
        if filters.get('status'):
            is_active = filters['status'] == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        # التوزيع حسب الجنس
        gender_distribution = queryset.values('gender').annotate(
            count=Count('id')
        )
        
        # التوزيع حسب الجنسية
        nationality_distribution = queryset.values('nationality').annotate(
            count=Count('id')
        ).order_by('-count')[:10]  # أعلى 10 جنسيات
        
        # التوزيع العمري
        today = timezone.now().date()
        age_groups = {
            '18-25': 0,
            '26-35': 0,
            '36-45': 0,
            '46-55': 0,
            '56+': 0
        }
        
        for employee in queryset.filter(birth_date__isnull=False):
            age = (today - employee.birth_date).days // 365
            if 18 <= age <= 25:
                age_groups['18-25'] += 1
            elif 26 <= age <= 35:
                age_groups['26-35'] += 1
            elif 36 <= age <= 45:
                age_groups['36-45'] += 1
            elif 46 <= age <= 55:
                age_groups['46-55'] += 1
            elif age > 55:
                age_groups['56+'] += 1
        
        # التوزيع حسب المؤهل العلمي
        education_distribution = queryset.values('education_level').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'total_employees': queryset.count(),
            'gender_distribution': list(gender_distribution),
            'nationality_distribution': list(nationality_distribution),
            'age_distribution': [
                {'age_group': k, 'count': v} for k, v in age_groups.items()
            ],
            'education_distribution': list(education_distribution)
        }
    
    @staticmethod
    def get_birthdays_anniversaries_report(filters=None):
        """
        إنشاء تقرير أعياد الميلاد وذكريات التوظيف
        """
        if filters is None:
            filters = {}
        
        # تحديد الفترة (الشهر الحالي افتراضياً)
        today = timezone.now().date()
        if not filters.get('start_date'):
            filters['start_date'] = today.replace(day=1)
        
        if not filters.get('end_date'):
            next_month = today.replace(day=28) + timedelta(days=4)
            filters['end_date'] = next_month - timedelta(days=next_month.day)
        
        # أعياد الميلاد
        birthdays = Employee.objects.filter(
            birth_date__month__gte=filters['start_date'].month,
            birth_date__month__lte=filters['end_date'].month,
            is_active=True
        ).select_related('department', 'position').order_by('birth_date__day')
        
        # ذكريات التوظيف
        anniversaries = Employee.objects.filter(
            hire_date__month__gte=filters['start_date'].month,
            hire_date__month__lte=filters['end_date'].month,
            is_active=True
        ).select_related('department', 'position').order_by('hire_date__day')
        
        birthdays_data = []
        for employee in birthdays:
            years_old = (today - employee.birth_date).days // 365 if employee.birth_date else 0
            birthdays_data.append({
                'full_name': employee.full_name_ar,
                'employee_number': employee.employee_number,
                'department': employee.department.name_ar if employee.department else '',
                'birth_date': employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else '',
                'age': years_old,
                'phone': employee.phone,
                'email': employee.email
            })
        
        anniversaries_data = []
        for employee in anniversaries:
            years_service = (today - employee.hire_date).days // 365 if employee.hire_date else 0
            anniversaries_data.append({
                'full_name': employee.full_name_ar,
                'employee_number': employee.employee_number,
                'department': employee.department.name_ar if employee.department else '',
                'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
                'years_of_service': years_service,
                'phone': employee.phone,
                'email': employee.email
            })
        
        return {
            'period_start': filters['start_date'].strftime('%Y-%m-%d'),
            'period_end': filters['end_date'].strftime('%Y-%m-%d'),
            'birthdays_count': len(birthdays_data),
            'anniversaries_count': len(anniversaries_data),
            'birthdays': birthdays_data,
            'anniversaries': anniversaries_data
        }
    
    @staticmethod
    def get_attendance_analytics(filters=None):
        """
        إنشاء تحليلات الحضور
        """
        if filters is None:
            filters = {}
        
        # تحديد الفترة (الشهر الحالي افتراضياً)
        today = timezone.now().date()
        if not filters.get('start_date'):
            filters['start_date'] = today.replace(day=1)
        
        if not filters.get('end_date'):
            filters['end_date'] = today
        
        # بناء الاستعلام
        attendance_records = AttendanceRecord.objects.filter(
            date__gte=filters['start_date'],
            date__lte=filters['end_date']
        )
        
        # تطبيق الفلاتر
        if filters.get('department'):
            attendance_records = attendance_records.filter(
                employee__department_id=filters['department']
            )
        
        # الإحصائيات الأساسية
        total_records = attendance_records.count()
        present_records = attendance_records.filter(status='present').count()
        absent_records = attendance_records.filter(status='absent').count()
        late_records = attendance_records.filter(is_late=True).count()
        
        # معدل الحضور
        attendance_rate = (present_records / total_records * 100) if total_records > 0 else 0
        
        # التوزيع حسب القسم
        dept_attendance = attendance_records.values(
            'employee__department__name_ar'
        ).annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent'))
        ).order_by('-total')
        
        return {
            'period_start': filters['start_date'].strftime('%Y-%m-%d'),
            'period_end': filters['end_date'].strftime('%Y-%m-%d'),
            'total_records': total_records,
            'present_records': present_records,
            'absent_records': absent_records,
            'late_records': late_records,
            'attendance_rate': round(attendance_rate, 2),
            'department_attendance': list(dept_attendance)
        }
    
    @staticmethod
    def get_salary_analytics(filters=None):
        """
        إنشاء تحليلات الرواتب
        """
        if filters is None:
            filters = {}
        
        # بناء الاستعلام
        salary_structures = EmployeeSalaryStructure.objects.filter(
            is_active=True
        ).select_related('employee', 'employee__department', 'employee__position')
        
        # تطبيق الفلاتر
        if filters.get('department'):
            salary_structures = salary_structures.filter(
                employee__department_id=filters['department']
            )
        
        # الإحصائيات الأساسية
        total_employees = salary_structures.count()
        total_basic_salary = salary_structures.aggregate(
            total=Sum('basic_salary')
        )['total'] or 0
        
        avg_basic_salary = salary_structures.aggregate(
            avg=Avg('basic_salary')
        )['avg'] or 0
        
        # التوزيع حسب القسم
        dept_salaries = salary_structures.values(
            'employee__department__name_ar'
        ).annotate(
            count=Count('id'),
            total_salary=Sum('basic_salary'),
            avg_salary=Avg('basic_salary')
        ).order_by('-avg_salary')
        
        # التوزيع حسب الوظيفة
        position_salaries = salary_structures.values(
            'employee__position__name_ar'
        ).annotate(
            count=Count('id'),
            total_salary=Sum('basic_salary'),
            avg_salary=Avg('basic_salary')
        ).order_by('-avg_salary')
        
        return {
            'total_employees': total_employees,
            'total_basic_salary': float(total_basic_salary),
            'avg_basic_salary': float(avg_basic_salary),
            'department_salaries': [
                {
                    'department': item['employee__department__name_ar'],
                    'count': item['count'],
                    'total_salary': float(item['total_salary'] or 0),
                    'avg_salary': float(item['avg_salary'] or 0)
                }
                for item in dept_salaries
            ],
            'position_salaries': [
                {
                    'position': item['employee__position__name_ar'],
                    'count': item['count'],
                    'total_salary': float(item['total_salary'] or 0),
                    'avg_salary': float(item['avg_salary'] or 0)
                }
                for item in position_salaries
            ]
        }
    
    @staticmethod
    def export_report_to_excel(report_data, report_type):
        """
        تصدير التقرير إلى Excel
        """
        try:
            import pandas as pd
            from io import BytesIO
            
            # إنشاء ملف Excel
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # إضافة البيانات حسب نوع التقرير
                if report_type == 'employee_summary':
                    # ملخص الموظفين
                    summary_df = pd.DataFrame([{
                        'المؤشر': 'إجمالي الموظفين',
                        'القيمة': report_data['total_employees']
                    }, {
                        'المؤشر': 'الموظفين النشطين',
                        'القيمة': report_data['active_employees']
                    }, {
                        'المؤشر': 'الموظفين غير النشطين',
                        'القيمة': report_data['inactive_employees']
                    }])
                    summary_df.to_excel(writer, sheet_name='الملخص', index=False)
                    
                    # التوزيع حسب القسم
                    if report_data['department_distribution']:
                        dept_df = pd.DataFrame(report_data['department_distribution'])
                        dept_df.to_excel(writer, sheet_name='التوزيع حسب القسم', index=False)
                
                elif report_type == 'employee_details':
                    # تفاصيل الموظفين
                    employees_df = pd.DataFrame(report_data['employees'])
                    employees_df.to_excel(writer, sheet_name='تفاصيل الموظفين', index=False)
                
                # يمكن إضافة المزيد من أنواع التقارير هنا
            
            output.seek(0)
            return output.getvalue()
            
        except ImportError:
            raise Exception("مكتبة pandas غير مثبتة. يرجى تثبيتها لتصدير Excel")
        except Exception as e:
            raise Exception(f"خطأ في تصدير Excel: {str(e)}")
    
    @staticmethod
    def export_report_to_pdf(report_data, report_type):
        """
        تصدير التقرير إلى PDF
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from io import BytesIO
            
            # إنشاء ملف PDF
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=A4)
            
            # إعداد الأنماط
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # وسط
            )
            
            # محتوى التقرير
            story = []
            
            # العنوان
            title_map = {
                'employee_summary': 'تقرير ملخص الموظفين',
                'employee_details': 'تقرير تفاصيل الموظفين',
                'org_structure': 'تقرير الهيكل التنظيمي',
                'new_employees': 'تقرير الموظفين الجدد',
                'demographics': 'تقرير التركيبة السكانية',
                'birthdays_anniversaries': 'تقرير أعياد الميلاد والذكريات'
            }
            
            title = title_map.get(report_type, 'تقرير الموظفين')
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # إضافة البيانات حسب نوع التقرير
            if report_type == 'employee_summary':
                # جدول الملخص
                summary_data = [
                    ['المؤشر', 'القيمة'],
                    ['إجمالي الموظفين', str(report_data['total_employees'])],
                    ['الموظفين النشطين', str(report_data['active_employees'])],
                    ['الموظفين غير النشطين', str(report_data['inactive_employees'])],
                    ['الموظفين الجدد', str(report_data['new_employees'])]
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
                
                story.append(summary_table)
            
            # بناء PDF
            doc.build(story)
            output.seek(0)
            return output.getvalue()
            
        except ImportError:
            raise Exception("مكتبة reportlab غير مثبتة. يرجى تثبيتها لتصدير PDF")
        except Exception as e:
            raise Exception(f"خطأ في تصدير PDF: {str(e)}")