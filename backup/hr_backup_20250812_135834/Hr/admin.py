from django.contrib import admin
from django.utils.translation import gettext_lazy as _
import csv
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from django.templatetags.static import static
from django.conf import settings
import os

admin.site.site_header = _('نظام الدولية للموارد البشرية')
admin.site.site_title = _('إدارة الموارد البشرية')
admin.site.index_title = _('لوحة تحكم الموارد البشرية')

from Hr.models.core import Company, Branch, Department, JobPosition
from Hr.models.employee import Employee
from Hr.models.leave import LeaveType, LeaveRequest
from Hr.models.payroll import SalaryComponent
from Hr.models.payroll.payroll_period_models import PayrollPeriod
from Hr.models.payroll.payroll_entry_models import PayrollEntry
from Hr.models.payroll.employee_salary_structure_models import EmployeeSalaryStructure

# Core Models
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_id', 'registration_number', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'tax_id', 'registration_number']

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'company', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'company', 'manager', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'department', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['title', 'code']

# Employee Models
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'position', 'status']
    list_filter = ['status', 'department', 'position']
    search_fields = ['employee_id', 'first_name', 'last_name', 'national_id']
    date_hierarchy = 'join_date'

# Payroll Models
@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'component_type', 'is_active']
    list_filter = ['component_type', 'is_active']
    search_fields = ['name', 'code']

# Leave Models
@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_paid', 'is_active']
    list_filter = ['is_paid', 'is_active']
    search_fields = ['name', 'code']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['leave_type', 'status']
    search_fields = ['employee__full_name']
    date_hierarchy = 'start_date'

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'period_type', 'start_date', 'end_date', 'pay_date', 'status', 'is_active']
    list_filter = ['period_type', 'status', 'is_active']
    search_fields = ['name']
    date_hierarchy = 'start_date'
    actions = ['close_period']
    
    def close_period(self, request, queryset):
        from Hr.services.payroll_service import PayrollService
        closed = 0
        for period in queryset:
            ok, msg = PayrollService.close_payroll_period(period.id)
            if ok:
                closed += 1
        self.message_user(request, f"تم إغلاق {closed} فترة رواتب بنجاح.")
    close_period.short_description = 'إغلاق الفترات المحددة'

@admin.register(PayrollEntry)
class PayrollEntryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_period', 'status', 'basic_salary', 'total_earnings', 'total_deductions', 'net_salary']
    list_filter = ['status', 'payroll_period']
    search_fields = ['employee__full_name', 'payroll_period__name']
    actions = ['mark_as_paid', 'export_as_csv', 'export_as_pdf']
    
    def mark_as_paid(self, request, queryset):
        paid = 0
        for entry in queryset:
            entry.status = 'paid'
            entry.save()
            paid += 1
        self.message_user(request, f"تم تعليم {paid} قيد راتب كمدفوع.")
    mark_as_paid.short_description = 'تعليم كمدفوع'

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = ['employee', 'payroll_period', 'status', 'basic_salary', 'total_earnings', 'total_deductions', 'net_salary', 'working_days', 'present_days', 'absent_days', 'leave_days', 'overtime_hours', 'payment_method', 'payment_reference', 'payment_date']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=payroll_entries.csv'
        writer = csv.writer(response)
        writer.writerow([meta.get_field(f).verbose_name if hasattr(meta.get_field(f), 'verbose_name') else f for f in field_names])
        for obj in queryset:
            row = [getattr(obj, f) for f in field_names]
            writer.writerow(row)
        return response
    export_as_csv.short_description = 'تصدير إلى CSV'

    def export_as_pdf(self, request, queryset):
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        import io
        from datetime import datetime

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=3*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        style_center = styles['Heading2'].clone('centered')
        style_center.alignment = TA_CENTER

        # شعار الشركة (إذا توفر)
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
        if os.path.exists(logo_path):
            elements.append(Image(logo_path, width=4*cm, height=4*cm))
        elements.append(Paragraph('كشف الرواتب', style_center))
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(f'تاريخ التصدير: {datetime.now().strftime("%Y-%m-%d %H:%M")}', styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))

        headers = ['#', 'الموظف', 'الفترة', 'الحالة', 'الراتب الأساسي', 'الاستحقاقات', 'الخصومات', 'الصافي']
        data = [headers]
        for idx, obj in enumerate(queryset, 1):
            data.append([
                idx,
                str(obj.employee),
                str(obj.payroll_period),
                str(obj.status),
                f"{obj.basic_salary:,.2f}",
                f"{obj.total_earnings:,.2f}",
                f"{obj.total_deductions:,.2f}",
                f"{obj.net_salary:,.2f}",
            ])
        table = Table(data, colWidths=[1.2*cm, 4*cm, 3*cm, 2.2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph('توقيع المدير المالي: .................................', styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph('توقيع المدير العام: .................................', styles['Normal']))

        def header_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            canvas.drawString(2*cm, A4[1] - 1.2*cm, 'نظام الدولية للموارد البشرية')
            canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.2*cm, f'صفحة {doc.page}')
            canvas.drawString(2*cm, 1.2*cm, 'سري - للاستخدام الداخلي فقط')
            canvas.restoreState()

        doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')
    export_as_pdf.short_description = 'تصدير إلى PDF (احترافي)'

@admin.register(EmployeeSalaryStructure)
class EmployeeSalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['employee', 'structure_name', 'basic_salary', 'total_earnings', 'total_deductions', 'net_salary', 'is_active', 'is_current']
    list_filter = ['is_active', 'is_current']
    search_fields = ['employee__full_name', 'structure_name']
    date_hierarchy = 'effective_from'

# =============================================================================
# IMPORT ENHANCED ADMIN CONFIGURATIONS
# =============================================================================

# Import enhanced admin configurations
try:
    from .admin_enhanced import *
except ImportError:
    pass  # Enhanced admin not available