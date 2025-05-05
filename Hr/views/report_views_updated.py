from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
import csv
import xlwt
from datetime import datetime, timedelta
import json

from Hr.models.department_models import Department
from Hr.models.employee_model import Employee
from Hr.models.leave_models import EmployeeLeave
from Hr.models.task_models import EmployeeTask
from Hr.models.hr_task_models import HrTask
from Hr.models.salary_models import PayrollEntry
from Hr.models.attendance_models import AttendanceRecord, AttendanceSummary

@login_required
def report_list(request):
    """عرض قائمة التقارير المتاحة"""
    reports = [
        {
            'id': 'employees',
            'name': 'تقرير الموظفين',
            'description': 'تقرير تفصيلي عن بيانات الموظفين',
            'icon': 'fas fa-users'
        },
        {
            'id': 'leaves',
            'name': 'تقرير الإجازات',
            'description': 'تقرير عن إجازات الموظفين',
            'icon': 'fas fa-calendar-alt'
        },
        {
            'id': 'attendance',
            'name': 'تقرير الحضور والانصراف',
            'description': 'تقرير عن حضور وانصراف الموظفين',
            'icon': 'fas fa-clock'
        },
        {
            'id': 'tasks',
            'name': 'تقرير المهام',
            'description': 'تقرير عن مهام الموظفين',
            'icon': 'fas fa-tasks'
        },
        {
            'id': 'hr_tasks',
            'name': 'تقرير مهام الموارد البشرية',
            'description': 'تقرير عن مهام قسم الموارد البشرية',
            'icon': 'fas fa-clipboard-list'
        },
        {
            'id': 'payroll',
            'name': 'تقرير الرواتب',
            'description': 'تقرير عن رواتب الموظفين',
            'icon': 'fas fa-money-bill-wave'
        },
        {
            'id': 'insurance',
            'name': 'تقرير التأمينات',
            'description': 'تقرير عن تأمينات الموظفين',
            'icon': 'fas fa-shield-alt'
        },
    ]

    context = {
        'reports': reports,
        'title': 'التقارير'
    }

    return render(request, 'Hr/reports/list.html', context)


@login_required
def export_data(request):
    """واجهة تصدير البيانات"""
    if request.method == 'POST':
        # تحديد تنسيق التصدير
        export_format = request.POST.get('export_format', 'excel')
        
        # الحصول على الحقول المحددة
        fields = request.POST.getlist('fields[]')
        
        # تصفية بيانات الموظفين
        employees = Employee.objects.all()
        
        # تصفية حسب اختيار الموظفين
        employee_selection = request.POST.get('employee_selection')
        if employee_selection == 'selected':
            employee_ids = request.POST.getlist('employees[]')
            if employee_ids:
                employees = employees.filter(emp_id__in=employee_ids)
        
        # تصفية حسب اختيار الأقسام
        department_selection = request.POST.get('department_selection')
        if department_selection == 'selected':
            department_codes = request.POST.getlist('departments[]')
            if department_codes:
                employees = employees.filter(department__dept_code__in=department_codes)
        
        # تصفية حسب حالة الموظف
        status_filters = []
        if request.POST.get('status_active'):
            status_filters.append('سارى')
        if request.POST.get('status_leave'):
            status_filters.append('إجازة')
        if request.POST.get('status_resigned'):
            status_filters.append('استقالة')
        if request.POST.get('status_terminated'):
            status_filters.append('انقطاع عن العمل')
        
        if status_filters:
            employees = employees.filter(working_condition__in=status_filters)
        
        # تصفية حسب حالة التأمين
        insurance_filters = []
        if request.POST.get('insurance_yes'):
            insurance_filters.append('مؤمن عليه')
        if request.POST.get('insurance_no'):
            insurance_filters.append('غير مؤمن عليه')
        
        if insurance_filters:
            employees = employees.filter(insurance_status__in=insurance_filters)
        
        # تصفية حسب التاريخ
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                employees = employees.filter(emp_date_hiring__gte=date_from)
            except (ValueError, TypeError):
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                employees = employees.filter(emp_date_hiring__lte=date_to)
            except (ValueError, TypeError):
                pass
        
        # تصدير البيانات
        if export_format == 'excel':
            return export_employees_to_excel(employees, fields)
        else:
            return export_employees_to_pdf(employees, fields)
    
    # عرض صفحة التصدير
    departments = Department.objects.all()
    employees = Employee.objects.all()
    
    context = {
        'departments': departments,
        'employees': employees,
        'title': 'تصدير البيانات'
    }
    
    return render(request, 'Hr/reports/export.html', context)


@login_required
def department_report(request, dept_code):
    """تقرير خاص بقسم محدد"""
    department = get_object_or_404(Department, dept_code=dept_code)
    
    # الحصول على موظفي القسم
    employees = Employee.objects.filter(department=department)
    
    # إحصائيات عامة
    total_employees = employees.count()
    active_employees = employees.filter(working_condition='سارى',Insurance_Status='مؤمن عليه').count()
    on_leave_employees = employees.filter(working_condition='إجازة').count()
    resigned_employees = employees.filter(working_condition='استقالة').count()
    
    # إحصائيات التأمين
    insured_employees = employees.filter(insurance_status='مؤمن عليه').count()
    uninsured_employees = employees.filter(insurance_status='غير مؤمن عليه').count()
    
    # إحصائيات المهام
    tasks = EmployeeTask.objects.filter(employee__in=employees)
    completed_tasks = tasks.filter(status='completed').count()
    pending_tasks = tasks.filter(status='pending').count()
    overdue_tasks = tasks.filter(status='in_progress', due_date__lt=timezone.now().date()).count()
    
    # تصدير البيانات
    export_format = request.GET.get('export')
    if export_format:
        if export_format == 'excel':
            return export_department_to_excel(department, employees)
        elif export_format == 'pdf':
            return export_department_to_pdf(department, employees)
    
    context = {
        'department': department,
        'employees': employees,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'on_leave_employees': on_leave_employees,
        'resigned_employees': resigned_employees,
        'insured_employees': insured_employees,
        'uninsured_employees': uninsured_employees,
        'tasks': tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'title': f'تقرير قسم {department.dept_name}'
    }
    
    return render(request, 'Hr/reports/department_report.html', context)


# وظائف التصدير
def export_employees_to_excel(employees, fields):
    """تصدير بيانات الموظفين إلى Excel"""
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="employee_export.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Employees')

    # عنوان الملف
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # تحديد أسماء الأعمدة بناءً على الحقول المختارة
    columns = []
    for field in fields:
        if field == 'emp_id':
            columns.append('الرقم الوظيفي')
        elif field == 'emp_full_name':
            columns.append('الاسم الكامل')
        elif field == 'department':
            columns.append('القسم')
        elif field == 'jop_name':
            columns.append('المسمى الوظيفي')
        elif field == 'emp_date_hiring':
            columns.append('تاريخ التعيين')
        elif field == 'working_condition':
            columns.append('حالة العمل')
        elif field == 'contract_expiry_date':
            columns.append('تاريخ انتهاء العقد')
        elif field == 'insurance_status':
            columns.append('حالة التأمين')
        elif field == 'insurance_number':
            columns.append('رقم التأمين')
        elif field == 'national_id':
            columns.append('الرقم القومي')
        elif field == 'emp_phone1':
            columns.append('رقم الهاتف')
        elif field == 'emp_address':
            columns.append('العنوان')
        elif field == 'date_birth':
            columns.append('تاريخ الميلاد')
        elif field == 'emp_car':
            columns.append('السيارة')
        elif field == 'car_pick_up_point':
            columns.append('نقطة الالتقاط')
        # يمكن إضافة المزيد من الحقول حسب الحاجة

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    # محتوى الملف
    font_style = xlwt.XFStyle()

    for employee in employees:
        row_num += 1
        row = []

        for field in fields:
            if field == 'emp_id':
                row.append(employee.emp_id)
            elif field == 'emp_full_name':
                row.append(employee.emp_full_name or '')
            elif field == 'department':
                row.append(employee.department.dept_name if employee.department else '')
            elif field == 'jop_name':
                row.append(employee.jop_name or '')
            elif field == 'emp_date_hiring':
                row.append(employee.emp_date_hiring.strftime('%Y-%m-%d') if employee.emp_date_hiring else '')
            elif field == 'working_condition':
                row.append(employee.working_condition or '')
            elif field == 'contract_expiry_date':
                row.append(employee.contract_expiry_date.strftime('%Y-%m-%d') if employee.contract_expiry_date else '')
            elif field == 'insurance_status':
                row.append(employee.insurance_status or '')
            elif field == 'insurance_number':
                row.append(employee.insurance_number or '')
            elif field == 'national_id':
                row.append(employee.national_id or '')
            elif field == 'emp_phone1':
                row.append(employee.emp_phone1 or '')
            elif field == 'emp_address':
                row.append(employee.emp_address or '')
            elif field == 'date_birth':
                row.append(employee.date_birth.strftime('%Y-%m-%d') if employee.date_birth else '')
            elif field == 'emp_car':
                row.append(employee.emp_car.car_name if employee.emp_car else '')
            elif field == 'car_pick_up_point':
                row.append(employee.car_pick_up_point.pick_up_point_description if employee.car_pick_up_point else '')
            # يمكن إضافة المزيد من الحقول حسب الحاجة

        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


def export_employees_to_pdf(employees, fields):
    """تصدير بيانات الموظفين إلى PDF - للتبسيط، نستخدم استجابة HttpResponse"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="employee_export.pdf"'
    
    # ملاحظة: هذه وظيفة بسيطة للعرض فقط
    # في التطبيق الفعلي، يجب استخدام مكتبة مثل ReportLab أو WeasyPrint لإنشاء ملف PDF

    # إنشاء محتوى نصي مؤقت للتوضيح
    content = "تقرير الموظفين\n\n"
    
    # إضافة عناوين الأعمدة
    headers = []
    for field in fields:
        if field == 'emp_id':
            headers.append('الرقم الوظيفي')
        elif field == 'emp_full_name':
            headers.append('الاسم الكامل')
        elif field == 'department':
            headers.append('القسم')
        # يمكن إضافة المزيد من الحقول حسب الحاجة
    
    content += " | ".join(headers) + "\n"
    content += "-" * 50 + "\n"
    
    # إضافة بيانات الموظفين
    for employee in employees:
        row = []
        for field in fields:
            if field == 'emp_id':
                row.append(str(employee.emp_id))
            elif field == 'emp_full_name':
                row.append(employee.emp_full_name or '')
            elif field == 'department':
                row.append(employee.department.dept_name if employee.department else '')
            # يمكن إضافة المزيد من الحقول حسب الحاجة
        
        content += " | ".join(row) + "\n"
    
    response.write(content.encode('utf-8'))
    return response


def export_department_to_excel(department, employees):
    """تصدير تقرير قسم إلى Excel"""
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="department_{department.dept_code}_report.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Department')

    # معلومات القسم
    ws.write(0, 0, 'كود القسم:', xlwt.easyxf('font: bold on'))
    ws.write(0, 1, department.dept_code)
    ws.write(1, 0, 'اسم القسم:', xlwt.easyxf('font: bold on'))
    ws.write(1, 1, department.dept_name)
    ws.write(2, 0, 'مدير القسم:', xlwt.easyxf('font: bold on'))
    ws.write(2, 1, department.manager.emp_full_name if department.manager else 'غير محدد')
    
    # إحصائيات الموظفين
    ws.write(4, 0, 'إحصائيات الموظفين', xlwt.easyxf('font: bold on'))
    ws.write(5, 0, 'إجمالي الموظفين:')
    ws.write(5, 1, employees.count())
    ws.write(6, 0, 'الموظفين النشطين:')
    ws.write(6, 1, employees.filter(working_condition='سارى').count())
    ws.write(7, 0, 'الموظفين في إجازة:')
    ws.write(7, 1, employees.filter(working_condition='إجازة').count())
    ws.write(8, 0, 'الموظفين المستقيلين:')
    ws.write(8, 1, employees.filter(working_condition='استقالة').count())
    
    # قائمة الموظفين
    row_num = 10
    ws.write(row_num, 0, 'قائمة الموظفين', xlwt.easyxf('font: bold on'))
    row_num += 1
    
    # عناوين الجدول
    font_style = xlwt.easyxf('font: bold on')
    columns = ['الرقم الوظيفي', 'الاسم', 'المسمى الوظيفي', 'حالة العمل', 'تاريخ التعيين']
    
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)
    
    # بيانات الموظفين
    font_style = xlwt.XFStyle()
    
    for employee in employees:
        row_num += 1
        ws.write(row_num, 0, employee.emp_id)
        ws.write(row_num, 1, employee.emp_full_name or '')
        ws.write(row_num, 2, employee.jop_name or '')
        ws.write(row_num, 3, employee.working_condition or '')
        ws.write(row_num, 4, employee.emp_date_hiring.strftime('%Y-%m-%d') if employee.emp_date_hiring else '')
    
    wb.save(response)
    return response


def export_department_to_pdf(department, employees):
    """تصدير تقرير قسم إلى PDF - للتبسيط، نستخدم استجابة HttpResponse"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="department_{department.dept_code}_report.pdf"'
    
    # ملاحظة: هذه وظيفة بسيطة للعرض فقط
    # في التطبيق الفعلي، يجب استخدام مكتبة مثل ReportLab أو WeasyPrint لإنشاء ملف PDF
    
    content = f"تقرير قسم {department.dept_name}\n\n"
    content += f"كود القسم: {department.dept_code}\n"
    content += f"مدير القسم: {department.manager.emp_full_name if department.manager else 'غير محدد'}\n\n"
    
    content += "إحصائيات الموظفين\n"
    content += f"إجمالي الموظفين: {employees.count()}\n"
    content += f"الموظفين النشطين: {employees.filter(working_condition='سارى').count()}\n"
    content += f"الموظفين في إجازة: {employees.filter(working_condition='إجازة').count()}\n"
    content += f"الموظفين المستقيلين: {employees.filter(working_condition='استقالة').count()}\n\n"
    
    content += "قائمة الموظفين\n"
    content += "الرقم | الاسم | المسمى الوظيفي | حالة العمل\n"
    content += "-" * 50 + "\n"
    
    for employee in employees:
        content += f"{employee.emp_id} | {employee.emp_full_name or ''} | {employee.jop_name or ''} | {employee.working_condition or ''}\n"
    
    response.write(content.encode('utf-8'))
    return response
