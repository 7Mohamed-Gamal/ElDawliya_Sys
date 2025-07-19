"""
Report Service for HR System
Handles generation of various HR reports in different formats
"""

import io
import csv
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional, Union

from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

# PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Excel generation
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.utils.dataframe import dataframe_to_rows
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from Hr.models import (
    Employee, Department, Company, Branch, JobPosition,
    AttendanceRecord, LeaveRequest, PayrollEntry, PayrollPeriod
)


class ReportService:
    """Service class for generating HR reports"""
    
    def __init__(self):
        self.setup_fonts()
    
    def setup_fonts(self):
        """Setup Arabic fonts for PDF generation"""
        if REPORTLAB_AVAILABLE:
            try:
                # Register Arabic font if available
                font_path = getattr(settings, 'ARABIC_FONT_PATH', None)
                if font_path:
                    pdfmetrics.registerFont(TTFont('Arabic', font_path))
                    self.arabic_font = 'Arabic'
                else:
                    self.arabic_font = 'Helvetica'
            except Exception:
                self.arabic_font = 'Helvetica'
        else:
            self.arabic_font = 'Helvetica'
    
    # Employee Reports
    def generate_employee_report(self, 
                               company_id: Optional[str] = None,
                               department_id: Optional[str] = None,
                               branch_id: Optional[str] = None,
                               status: Optional[str] = None,
                               format: str = 'csv') -> Union[HttpResponse, Dict]:
        """Generate comprehensive employee report"""
        
        # Build query
        queryset = Employee.objects.select_related(
            'company', 'branch', 'department', 'job_position', 'manager'
        )
        
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        if status:
            queryset = queryset.filter(status=status)
        
        # Prepare data
        data = []
        for employee in queryset:
            data.append({
                'رقم الموظف': employee.employee_number,
                'الاسم الكامل': employee.full_name,
                'البريد الإلكتروني': employee.email or '',
                'الهاتف': employee.mobile or employee.phone or '',
                'القسم': employee.department.name if employee.department else '',
                'الوظيفة': employee.job_position.title if employee.job_position else '',
                'المدير المباشر': employee.manager.full_name if employee.manager else '',
                'تاريخ التوظيف': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
                'سنوات الخدمة': employee.years_of_service or 0,
                'الراتب الأساسي': float(employee.basic_salary) if employee.basic_salary else 0,
                'الحالة': employee.get_status_display(),
                'نوع التوظيف': employee.get_employment_type_display(),
            })
        
        if format == 'json':
            return {'data': data, 'count': len(data)}
        elif format == 'excel':
            return self._generate_excel_report(data, 'تقرير الموظفين')
        elif format == 'pdf':
            return self._generate_pdf_report(data, 'تقرير الموظفين')
        else:  # CSV
            return self._generate_csv_report(data, 'employee_report')
    
    def generate_organizational_chart(self, company_id: Optional[str] = None) -> Dict:
        """Generate organizational chart data"""
        
        queryset = Employee.objects.select_related('department', 'job_position', 'manager')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Build hierarchy
        hierarchy = {}
        employees_by_manager = {}
        
        for employee in queryset.filter(status='active'):
            manager_id = str(employee.manager.id) if employee.manager else 'root'
            
            if manager_id not in employees_by_manager:
                employees_by_manager[manager_id] = []
            
            employees_by_manager[manager_id].append({
                'id': str(employee.id),
                'name': employee.full_name,
                'title': employee.job_position.title if employee.job_position else '',
                'department': employee.department.name if employee.department else '',
                'email': employee.email or '',
                'phone': employee.mobile or employee.phone or '',
            })
        
        def build_tree(manager_id='root'):
            children = employees_by_manager.get(manager_id, [])
            result = []
            
            for child in children:
                child_data = child.copy()
                child_data['children'] = build_tree(child['id'])
                result.append(child_data)
            
            return result
        
        return {
            'hierarchy': build_tree(),
            'total_employees': queryset.filter(status='active').count()
        }
    
    def generate_birthday_report(self, days_ahead: int = 30) -> Dict:
        """Generate upcoming birthdays report"""
        
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        # Handle year boundary
        if today.year == end_date.year:
            employees = Employee.objects.filter(
                birth_date__month__gte=today.month,
                birth_date__month__lte=end_date.month,
                birth_date__day__gte=today.day if today.month == end_date.month else 1,
                birth_date__day__lte=end_date.day if today.month == end_date.month else 31,
                status='active'
            )
        else:
            # Cross year boundary
            employees = Employee.objects.filter(
                Q(birth_date__month__gte=today.month, birth_date__day__gte=today.day) |
                Q(birth_date__month__lte=end_date.month, birth_date__day__lte=end_date.day),
                status='active'
            )
        
        birthdays = []
        for employee in employees.select_related('department'):
            if employee.birth_date:
                # Calculate next birthday
                next_birthday = employee.birth_date.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                
                days_until = (next_birthday - today).days
                
                if days_until <= days_ahead:
                    birthdays.append({
                        'employee': {
                            'id': str(employee.id),
                            'name': employee.full_name,
                            'department': employee.department.name if employee.department else '',
                            'email': employee.email or '',
                        },
                        'birth_date': employee.birth_date.strftime('%m-%d'),
                        'next_birthday': next_birthday.strftime('%Y-%m-%d'),
                        'days_until': days_until,
                        'age_turning': employee.age + 1 if employee.age else None
                    })
        
        # Sort by days until birthday
        birthdays.sort(key=lambda x: x['days_until'])
        
        return {
            'birthdays': birthdays,
            'count': len(birthdays),
            'period': f"{today.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    
    def generate_work_anniversary_report(self, days_ahead: int = 30) -> Dict:
        """Generate work anniversaries report"""
        
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        # Similar logic to birthdays but for hire_date
        if today.year == end_date.year:
            employees = Employee.objects.filter(
                hire_date__month__gte=today.month,
                hire_date__month__lte=end_date.month,
                hire_date__day__gte=today.day if today.month == end_date.month else 1,
                hire_date__day__lte=end_date.day if today.month == end_date.month else 31,
                status='active'
            )
        else:
            employees = Employee.objects.filter(
                Q(hire_date__month__gte=today.month, hire_date__day__gte=today.day) |
                Q(hire_date__month__lte=end_date.month, hire_date__day__lte=end_date.day),
                status='active'
            )
        
        anniversaries = []
        for employee in employees.select_related('department'):
            if employee.hire_date:
                # Calculate next anniversary
                next_anniversary = employee.hire_date.replace(year=today.year)
                if next_anniversary < today:
                    next_anniversary = next_anniversary.replace(year=today.year + 1)
                
                days_until = (next_anniversary - today).days
                
                if days_until <= days_ahead:
                    anniversaries.append({
                        'employee': {
                            'id': str(employee.id),
                            'name': employee.full_name,
                            'department': employee.department.name if employee.department else '',
                            'email': employee.email or '',
                        },
                        'hire_date': employee.hire_date.strftime('%Y-%m-%d'),
                        'next_anniversary': next_anniversary.strftime('%Y-%m-%d'),
                        'days_until': days_until,
                        'years_of_service': employee.years_of_service or 0
                    })
        
        # Sort by days until anniversary
        anniversaries.sort(key=lambda x: x['days_until'])
        
        return {
            'anniversaries': anniversaries,
            'count': len(anniversaries),
            'period': f"{today.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    
    # Attendance Reports
    def generate_attendance_report(self,
                                 start_date: date,
                                 end_date: date,
                                 department_id: Optional[str] = None,
                                 employee_id: Optional[str] = None,
                                 format: str = 'csv') -> Union[HttpResponse, Dict]:
        """Generate attendance report"""
        
        queryset = AttendanceRecord.objects.select_related(
            'employee', 'employee__department'
        ).filter(date__range=[start_date, end_date])
        
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        data = []
        for record in queryset:
            data.append({
                'التاريخ': record.date.strftime('%Y-%m-%d'),
                'رقم الموظف': record.employee.employee_number,
                'اسم الموظف': record.employee.full_name,
                'القسم': record.employee.department.name if record.employee.department else '',
                'وقت الحضور': record.check_in_time.strftime('%H:%M') if record.check_in_time else '',
                'وقت الانصراف': record.check_out_time.strftime('%H:%M') if record.check_out_time else '',
                'إجمالي الساعات': float(record.total_hours) if record.total_hours else 0,
                'متأخر': 'نعم' if record.is_late else 'لا',
                'انصراف مبكر': 'نعم' if record.is_early_departure else 'لا',
                'ملاحظات': record.notes or ''
            })
        
        if format == 'json':
            return {'data': data, 'count': len(data)}
        elif format == 'excel':
            return self._generate_excel_report(data, 'تقرير الحضور')
        elif format == 'pdf':
            return self._generate_pdf_report(data, 'تقرير الحضور')
        else:
            return self._generate_csv_report(data, 'attendance_report')
    
    def generate_attendance_summary(self,
                                  start_date: date,
                                  end_date: date,
                                  department_id: Optional[str] = None) -> Dict:
        """Generate attendance summary statistics"""
        
        queryset = AttendanceRecord.objects.select_related('employee')
        queryset = queryset.filter(date__range=[start_date, end_date])
        
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        
        # Calculate statistics
        total_records = queryset.count()
        late_arrivals = queryset.filter(is_late=True).count()
        early_departures = queryset.filter(is_early_departure=True).count()
        
        # Average working hours
        avg_hours = queryset.aggregate(avg_hours=Avg('total_hours'))['avg_hours'] or 0
        
        # Daily breakdown
        daily_stats = []
        current_date = start_date
        while current_date <= end_date:
            day_records = queryset.filter(date=current_date)
            daily_stats.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total_attendance': day_records.count(),
                'late_arrivals': day_records.filter(is_late=True).count(),
                'early_departures': day_records.filter(is_early_departure=True).count(),
                'avg_hours': float(day_records.aggregate(avg=Avg('total_hours'))['avg'] or 0)
            })
            current_date += timedelta(days=1)
        
        return {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'summary': {
                'total_records': total_records,
                'late_arrivals': late_arrivals,
                'early_departures': early_departures,
                'late_percentage': (late_arrivals / total_records * 100) if total_records > 0 else 0,
                'early_departure_percentage': (early_departures / total_records * 100) if total_records > 0 else 0,
                'average_working_hours': float(avg_hours)
            },
            'daily_breakdown': daily_stats
        }
    
    # Leave Reports
    def generate_leave_report(self,
                            start_date: date,
                            end_date: date,
                            department_id: Optional[str] = None,
                            status: Optional[str] = None,
                            format: str = 'csv') -> Union[HttpResponse, Dict]:
        """Generate leave requests report"""
        
        queryset = LeaveRequest.objects.select_related(
            'employee', 'employee__department', 'leave_type'
        ).filter(start_date__lte=end_date, end_date__gte=start_date)
        
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        if status:
            queryset = queryset.filter(status=status)
        
        data = []
        for leave in queryset:
            data.append({
                'رقم الموظف': leave.employee.employee_number,
                'اسم الموظف': leave.employee.full_name,
                'القسم': leave.employee.department.name if leave.employee.department else '',
                'نوع الإجازة': leave.leave_type.name,
                'تاريخ البداية': leave.start_date.strftime('%Y-%m-%d'),
                'تاريخ النهاية': leave.end_date.strftime('%Y-%m-%d'),
                'عدد الأيام': leave.days,
                'الحالة': leave.get_status_display(),
                'السبب': leave.reason or '',
                'تاريخ الطلب': leave.created_at.strftime('%Y-%m-%d')
            })
        
        if format == 'json':
            return {'data': data, 'count': len(data)}
        elif format == 'excel':
            return self._generate_excel_report(data, 'تقرير الإجازات')
        elif format == 'pdf':
            return self._generate_pdf_report(data, 'تقرير الإجازات')
        else:
            return self._generate_csv_report(data, 'leave_report')
    
    # Payroll Reports
    def generate_payroll_report(self,
                              payroll_period_id: str,
                              department_id: Optional[str] = None,
                              format: str = 'csv') -> Union[HttpResponse, Dict]:
        """Generate payroll report for a specific period"""
        
        try:
            period = PayrollPeriod.objects.get(id=payroll_period_id)
        except PayrollPeriod.DoesNotExist:
            raise ValueError("Payroll period not found")
        
        queryset = PayrollEntry.objects.select_related(
            'employee', 'employee__department'
        ).filter(payroll_period=period)
        
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        
        data = []
        total_gross = 0
        total_deductions = 0
        total_net = 0
        
        for entry in queryset:
            data.append({
                'رقم الموظف': entry.employee.employee_number,
                'اسم الموظف': entry.employee.full_name,
                'القسم': entry.employee.department.name if entry.employee.department else '',
                'الراتب الأساسي': float(entry.basic_salary),
                'إجمالي الراتب': float(entry.gross_salary),
                'إجمالي الخصومات': float(entry.total_deductions),
                'صافي الراتب': float(entry.net_salary),
                'أيام العمل': entry.working_days,
                'أيام الحضور': entry.present_days,
                'أيام الغياب': entry.absent_days,
                'أيام الإجازة': entry.leave_days,
                'الحالة': entry.get_status_display()
            })
            
            total_gross += float(entry.gross_salary)
            total_deductions += float(entry.total_deductions)
            total_net += float(entry.net_salary)
        
        # Add summary row
        data.append({
            'رقم الموظف': '',
            'اسم الموظف': 'الإجمالي',
            'القسم': '',
            'الراتب الأساسي': '',
            'إجمالي الراتب': total_gross,
            'إجمالي الخصومات': total_deductions,
            'صافي الراتب': total_net,
            'أيام العمل': '',
            'أيام الحضور': '',
            'أيام الغياب': '',
            'أيام الإجازة': '',
            'الحالة': ''
        })
        
        if format == 'json':
            return {
                'data': data[:-1],  # Exclude summary row
                'summary': {
                    'total_gross': total_gross,
                    'total_deductions': total_deductions,
                    'total_net': total_net,
                    'employee_count': len(data) - 1
                },
                'period': {
                    'name': period.name,
                    'start_date': period.start_date.strftime('%Y-%m-%d'),
                    'end_date': period.end_date.strftime('%Y-%m-%d')
                }
            }
        elif format == 'excel':
            return self._generate_excel_report(data, f'كشف رواتب - {period.name}')
        elif format == 'pdf':
            return self._generate_pdf_report(data, f'كشف رواتب - {period.name}')
        else:
            return self._generate_csv_report(data, f'payroll_report_{period.name}')
    
    # Format-specific generators
    def _generate_csv_report(self, data: List[Dict], filename: str) -> HttpResponse:
        """Generate CSV report"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        # Add BOM for proper UTF-8 encoding in Excel
        response.write('\ufeff')
        
        if data:
            writer = csv.DictWriter(response, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return response
    
    def _generate_excel_report(self, data: List[Dict], title: str) -> HttpResponse:
        """Generate Excel report"""
        if not OPENPYXL_AVAILABLE:
            raise ImportError("openpyxl is required for Excel export")
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = title
        
        if data:
            # Headers
            headers = list(data[0].keys())
            ws.append(headers)
            
            # Style headers
            header_font = Font(bold=True)
            header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
            
            # Data rows
            for row_data in data:
                ws.append(list(row_data.values()))
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{title}.xlsx"'
        wb.save(response)
        
        return response
    
    def _generate_pdf_report(self, data: List[Dict], title: str) -> HttpResponse:
        """Generate PDF report"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF export")
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{title}.pdf"'
        
        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=self.arabic_font,
            fontSize=16,
            alignment=1,  # Center
            spaceAfter=30
        )
        
        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))
        
        if data:
            # Prepare table data
            headers = list(data[0].keys())
            table_data = [headers]
            
            for row in data:
                table_data.append(list(row.values()))
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        return response
    
    # Utility methods
    def get_available_reports(self) -> Dict:
        """Get list of available reports"""
        return {
            'employee_reports': [
                {'key': 'employee_list', 'name': 'تقرير الموظفين', 'description': 'قائمة شاملة بالموظفين'},
                {'key': 'org_chart', 'name': 'الهيكل التنظيمي', 'description': 'مخطط الهيكل التنظيمي'},
                {'key': 'birthdays', 'name': 'أعياد الميلاد', 'description': 'أعياد ميلاد الموظفين القادمة'},
                {'key': 'anniversaries', 'name': 'ذكريات التوظيف', 'description': 'ذكريات توظيف الموظفين'},
            ],
            'attendance_reports': [
                {'key': 'attendance_detail', 'name': 'تقرير الحضور التفصيلي', 'description': 'سجلات الحضور التفصيلية'},
                {'key': 'attendance_summary', 'name': 'ملخص الحضور', 'description': 'إحصائيات الحضور'},
            ],
            'leave_reports': [
                {'key': 'leave_requests', 'name': 'تقرير الإجازات', 'description': 'طلبات الإجازات'},
                {'key': 'leave_balance', 'name': 'أرصدة الإجازات', 'description': 'أرصدة إجازات الموظفين'},
            ],
            'payroll_reports': [
                {'key': 'payroll_detail', 'name': 'كشف الرواتب', 'description': 'كشف رواتب تفصيلي'},
                {'key': 'payroll_summary', 'name': 'ملخص الرواتب', 'description': 'ملخص إحصائيات الرواتب'},
            ]
        }
    
    def schedule_report(self, report_type: str, parameters: Dict, schedule: str, recipients: List[str]) -> Dict:
        """Schedule a report to be generated and sent automatically"""
        # This would typically integrate with a task queue like Celery
        # For now, return a placeholder response
        
        return {
            'status': 'scheduled',
            'report_type': report_type,
            'schedule': schedule,
            'recipients': recipients,
            'next_run': timezone.now() + timedelta(days=1),  # Placeholder
            'message': 'تم جدولة التقرير بنجاح'
        }


# Singleton instance
report_service = ReportService()