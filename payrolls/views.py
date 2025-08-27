from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
import logging

from .models import (
    EmployeeSalary, PayrollRun, PayrollDetail, 
    PayrollBonus, PayrollDeduction, PayrollCalculationRule
)
from employees.models import Employee
from org.models import Department
from .forms import EmployeeSalaryForm, PayrollRunForm, PayrollDetailForm
from .services import PayrollCalculationService, PayrollRunService, PayrollReportService

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """لوحة تحكم الرواتب"""
    today = date.today()
    current_month = today.strftime('%Y-%m')
    
    # إحصائيات عامة
    total_employees_with_salary = EmployeeSalary.objects.filter(is_current=True).count()
    total_payroll_runs = PayrollRun.objects.count()
    current_month_runs = PayrollRun.objects.filter(month_year=current_month).count()
    
    # إجمالي الرواتب الشهرية
    monthly_salary_total = EmployeeSalary.objects.filter(
        is_current=True
    ).aggregate(
        total_basic=Sum('basic_salary'),
        total_housing=Sum('housing_allow'),
        total_transport=Sum('transport'),
        total_other=Sum('other_allow'),
        total_gosi=Sum('gosi_deduction'),
        total_tax=Sum('tax_deduction')
    )
    
    # حساب إجمالي الراتب الصافي المتوقع
    net_salary_total = (
        (monthly_salary_total['total_basic'] or 0) +
        (monthly_salary_total['total_housing'] or 0) +
        (monthly_salary_total['total_transport'] or 0) +
        (monthly_salary_total['total_other'] or 0) -
        (monthly_salary_total['total_gosi'] or 0) -
        (monthly_salary_total['total_tax'] or 0)
    )
    
    # آخر تشغيل رواتب
    latest_payroll_run = PayrollRun.objects.order_by('-run_date').first()
    
    # إحصائيات تشغيل الرواتب الحالي
    current_run_stats = None
    if latest_payroll_run:
        current_run_stats = PayrollDetail.objects.filter(
            run=latest_payroll_run
        ).aggregate(
            total_employees=Count('payroll_detail_id'),
            total_net_salary=Sum('net_salary'),
            total_basic=Sum('basic_salary'),
            total_deductions=Sum('gosi') + Sum('tax') + Sum('loan_deduction')
        )
    
    # توزيع الرواتب حسب النطاقات
    salary_ranges = EmployeeSalary.objects.filter(is_current=True).extra(
        select={
            'salary_range': """
                CASE 
                    WHEN basic_salary >= 15000 THEN 'عالي (15000+)'
                    WHEN basic_salary >= 10000 THEN 'متوسط عالي (10000-14999)'
                    WHEN basic_salary >= 5000 THEN 'متوسط (5000-9999)'
                    WHEN basic_salary >= 3000 THEN 'منخفض (3000-4999)'
                    ELSE 'منخفض جداً (أقل من 3000)'
                END
            """
        }
    ).values('salary_range').annotate(
        count=Count('salary_id')
    ).order_by('-count')
    
    # إحصائيات الأقسام
    department_salary_stats = Department.objects.annotate(
        employee_count=Count('employee__employeesalary', filter=Q(employee__employeesalary__is_current=True)),
        avg_salary=Avg('employee__employeesalary__basic_salary', filter=Q(employee__employeesalary__is_current=True)),
        total_salary=Sum('employee__employeesalary__basic_salary', filter=Q(employee__employeesalary__is_current=True))
    ).filter(employee_count__gt=0).order_by('-total_salary')[:5]
    
    context = {
        'total_employees_with_salary': total_employees_with_salary,
        'total_payroll_runs': total_payroll_runs,
        'current_month_runs': current_month_runs,
        'monthly_salary_total': monthly_salary_total,
        'net_salary_total': net_salary_total,
        'latest_payroll_run': latest_payroll_run,
        'current_run_stats': current_run_stats,
        'salary_ranges': salary_ranges,
        'department_salary_stats': department_salary_stats,
    }
    
    return render(request, 'payrolls/dashboard.html', context)


@login_required
def salary_list(request):
    """قائمة رواتب الموظفين"""
    salaries = EmployeeSalary.objects.select_related('emp').filter(is_current=True)
    
    # البحث والفلترة
    search = request.GET.get('search')
    if search:
        salaries = salaries.filter(
            Q(emp__first_name__icontains=search) |
            Q(emp__last_name__icontains=search) |
            Q(emp__emp_code__icontains=search)
        )
    
    # فلترة حسب القسم
    department = request.GET.get('department')
    if department:
        salaries = salaries.filter(emp__dept_id=department)
    
    # فلترة حسب نطاق الراتب
    salary_range = request.GET.get('salary_range')
    if salary_range:
        if salary_range == 'high':
            salaries = salaries.filter(basic_salary__gte=15000)
        elif salary_range == 'medium_high':
            salaries = salaries.filter(basic_salary__gte=10000, basic_salary__lt=15000)
        elif salary_range == 'medium':
            salaries = salaries.filter(basic_salary__gte=5000, basic_salary__lt=10000)
        elif salary_range == 'low':
            salaries = salaries.filter(basic_salary__gte=3000, basic_salary__lt=5000)
        elif salary_range == 'very_low':
            salaries = salaries.filter(basic_salary__lt=3000)
    
    # فلترة حسب العملة
    currency = request.GET.get('currency')
    if currency:
        salaries = salaries.filter(currency=currency)
    
    # ترتيب النتائج
    salaries = salaries.order_by('-basic_salary')
    
    # التقسيم إلى صفحات
    paginator = Paginator(salaries, 20)
    page_number = request.GET.get('page')
    salaries = paginator.get_page(page_number)
    
    # قوائم للفلترة
    departments = Department.objects.filter(is_active=True).order_by('dept_name')
    
    context = {
        'salaries': salaries,
        'departments': departments,
    }
    
    return render(request, 'payrolls/salary_list.html', context)


@login_required
def add_salary(request):
    """إضافة راتب جديد"""
    if request.method == 'POST':
        form = EmployeeSalaryForm(request.POST)
        if form.is_valid():
            salary = form.save()
            messages.success(request, f'تم إضافة راتب الموظف {salary.emp.first_name} {salary.emp.last_name} بنجاح.')
            return redirect('payrolls:salary_detail', salary_id=salary.salary_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeSalaryForm()
    
    context = {
        'form': form,
        'title': 'إضافة راتب جديد'
    }
    
    return render(request, 'payrolls/salary_form.html', context)


@login_required
def salary_detail(request, salary_id):
    """تفاصيل راتب الموظف"""
    salary = get_object_or_404(EmployeeSalary, salary_id=salary_id)
    
    # حساب إجمالي البدلات والاستقطاعات
    total_allowances = (
        (salary.housing_allow or 0) +
        (salary.transport or 0) +
        (salary.other_allow or 0)
    )
    
    total_deductions = (
        (salary.gosi_deduction or 0) +
        (salary.tax_deduction or 0)
    )
    
    # حساب الراتب الصافي
    net_salary = (
        (salary.basic_salary or 0) +
        total_allowances -
        total_deductions
    )
    
    # تاريخ الرواتب السابقة للموظف
    salary_history = EmployeeSalary.objects.filter(
        emp=salary.emp
    ).exclude(salary_id=salary_id).order_by('-effective_date')[:5]
    
    context = {
        'salary': salary,
        'total_allowances': total_allowances,
        'total_deductions': total_deductions,
        'net_salary': net_salary,
        'salary_history': salary_history,
    }
    
    return render(request, 'payrolls/salary_detail.html', context)


@login_required
def edit_salary(request, salary_id):
    """تعديل راتب الموظف"""
    salary = get_object_or_404(EmployeeSalary, salary_id=salary_id)
    
    if request.method == 'POST':
        form = EmployeeSalaryForm(request.POST, instance=salary)
        if form.is_valid():
            salary = form.save()
            messages.success(request, f'تم تحديث راتب الموظف {salary.emp.first_name} {salary.emp.last_name} بنجاح.')
            return redirect('payrolls:salary_detail', salary_id=salary.salary_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeSalaryForm(instance=salary)
    
    context = {
        'form': form,
        'salary': salary,
        'title': 'تعديل الراتب'
    }
    
    return render(request, 'payrolls/salary_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_salary(request, salary_id):
    """حذف راتب الموظف"""
    salary = get_object_or_404(EmployeeSalary, salary_id=salary_id)
    
    try:
        salary.delete()
        messages.success(request, f'تم حذف راتب الموظف {salary.emp.first_name} {salary.emp.last_name} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف الراتب: {str(e)}')
    
    return redirect('payrolls:salary_list')


@login_required
def copy_salary(request, salary_id):
    """نسخ راتب الموظف"""
    original_salary = get_object_or_404(EmployeeSalary, salary_id=salary_id)
    
    if request.method == 'POST':
        # إنشاء نسخة جديدة
        new_salary = EmployeeSalary.objects.create(
            emp=original_salary.emp,
            basic_salary=original_salary.basic_salary,
            housing_allow=original_salary.housing_allow,
            transport=original_salary.transport,
            other_allow=original_salary.other_allow,
            gosi_deduction=original_salary.gosi_deduction,
            tax_deduction=original_salary.tax_deduction,
            currency=original_salary.currency,
            effective_date=date.today(),
            is_current=False  # يجب تفعيلها يدوياً
        )
        
        messages.success(request, f'تم نسخ راتب الموظف {original_salary.emp.first_name} {original_salary.emp.last_name} بنجاح.')
        return redirect('payrolls:salary_detail', salary_id=new_salary.salary_id)
    
    context = {
        'salary': original_salary,
    }
    
    return render(request, 'payrolls/salary_copy_confirm.html', context)


@login_required
def salary_history(request, salary_id):
    """تاريخ رواتب الموظف"""
    current_salary = get_object_or_404(EmployeeSalary, salary_id=salary_id)
    
    # جميع رواتب الموظف
    salary_history = EmployeeSalary.objects.filter(
        emp=current_salary.emp
    ).order_by('-effective_date')
    
    context = {
        'current_salary': current_salary,
        'salary_history': salary_history,
    }
    
    return render(request, 'payrolls/salary_history.html', context)


# إدارة تشغيل الرواتب
@login_required
def payroll_runs(request):
    """قائمة تشغيلات الرواتب"""
    runs = PayrollRun.objects.annotate(
        employee_count=Count('payrolldetail'),
        total_net_salary=Sum('payrolldetail__net_salary')
    ).order_by('-run_date')
    
    # فلترة حسب الحالة
    status = request.GET.get('status')
    if status:
        runs = runs.filter(status=status)
    
    # فلترة حسب الشهر
    month_year = request.GET.get('month_year')
    if month_year:
        runs = runs.filter(month_year=month_year)
    
    # التقسيم إلى صفحات
    paginator = Paginator(runs, 20)
    page_number = request.GET.get('page')
    runs = paginator.get_page(page_number)
    
    context = {
        'runs': runs,
    }
    
    return render(request, 'payrolls/payroll_runs.html', context)


@login_required
def create_payroll_run(request):
    """إنشاء تشغيل رواتب جديد"""
    if request.method == 'POST':
        form = PayrollRunForm(request.POST)
        if form.is_valid():
            payroll_run = form.save()
            messages.success(request, f'تم إنشاء تشغيل الرواتب لشهر {payroll_run.month_year} بنجاح.')
            return redirect('payrolls:payroll_run_detail', run_id=payroll_run.run_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PayrollRunForm()
        # تعيين الشهر الحالي كافتراضي
        form.fields['month_year'].initial = date.today().strftime('%Y-%m')
    
    context = {
        'form': form,
        'title': 'إنشاء تشغيل رواتب جديد'
    }
    
    return render(request, 'payrolls/payroll_run_form.html', context)


@login_required
def payroll_run_detail(request, run_id):
    """تفاصيل تشغيل الرواتب"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    
    # تفاصيل الرواتب
    payroll_details = PayrollDetail.objects.filter(
        run=payroll_run
    ).select_related('emp').order_by('emp__first_name')
    
    # إحصائيات التشغيل
    run_stats = payroll_details.aggregate(
        total_employees=Count('payroll_detail_id'),
        total_basic_salary=Sum('basic_salary'),
        total_housing=Sum('housing'),
        total_transport=Sum('transport'),
        total_overtime=Sum('overtime'),
        total_gosi=Sum('gosi'),
        total_tax=Sum('tax'),
        total_loan_deduction=Sum('loan_deduction'),
        total_net_salary=Sum('net_salary')
    )
    
    context = {
        'payroll_run': payroll_run,
        'payroll_details': payroll_details,
        'run_stats': run_stats,
    }
    
    return render(request, 'payrolls/payroll_run_detail.html', context)


@login_required
def edit_payroll_run(request, run_id):
    """تعديل تشغيل الرواتب"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    
    if request.method == 'POST':
        form = PayrollRunForm(request.POST, instance=payroll_run)
        if form.is_valid():
            payroll_run = form.save()
            messages.success(request, f'تم تحديث تشغيل الرواتب لشهر {payroll_run.month_year} بنجاح.')
            return redirect('payrolls:payroll_run_detail', run_id=payroll_run.run_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PayrollRunForm(instance=payroll_run)
    
    context = {
        'form': form,
        'payroll_run': payroll_run,
        'title': 'تعديل تشغيل الرواتب'
    }
    
    return render(request, 'payrolls/payroll_run_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_payroll_run(request, run_id):
    """حذف تشغيل الرواتب"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    
    try:
        # التحقق من أن التشغيل لم يتم تأكيده
        if payroll_run.status == 'Confirmed':
            messages.error(request, 'لا يمكن حذف تشغيل رواتب مؤكد.')
        else:
            payroll_run.delete()
            messages.success(request, f'تم حذف تشغيل الرواتب لشهر {payroll_run.month_year} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف تشغيل الرواتب: {str(e)}')
    
    return redirect('payrolls:payroll_runs')


@login_required
@require_http_methods(["POST"])
def confirm_payroll_run(request, run_id):
    """تأكيد تشغيل الرواتب"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    
    if payroll_run.status == 'Draft':
        payroll_run.status = 'Confirmed'
        payroll_run.confirmed_by = request.user.id  # يجب تعديل هذا حسب نموذج المستخدم
        payroll_run.save()
        
        messages.success(request, f'تم تأكيد تشغيل الرواتب لشهر {payroll_run.month_year}.')
    else:
        messages.warning(request, 'تشغيل الرواتب مؤكد مسبقاً.')
    
    return redirect('payrolls:payroll_run_detail', run_id=run_id)


@login_required
def process_payroll_run(request, run_id):
    """معالجة تشغيل الرواتب"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    
    if request.method == 'POST':
        # معالجة الرواتب - إنشاء تفاصيل الرواتب للموظفين
        active_salaries = EmployeeSalary.objects.filter(is_current=True).select_related('emp')
        
        created_count = 0
        for salary in active_salaries:
            # التحقق من عدم وجود تفصيل راتب مسبق
            if not PayrollDetail.objects.filter(run=payroll_run, emp=salary.emp).exists():
                # حساب الراتب الصافي
                basic_salary = salary.basic_salary or 0
                housing = salary.housing_allow or 0
                transport = salary.transport or 0
                overtime = 0  # يمكن حسابه من سجلات الحضور
                gosi = salary.gosi_deduction or 0
                tax = salary.tax_deduction or 0
                loan_deduction = 0  # يمكن حسابه من سجلات القروض
                
                net_salary = basic_salary + housing + transport + overtime - gosi - tax - loan_deduction
                
                PayrollDetail.objects.create(
                    run=payroll_run,
                    emp=salary.emp,
                    basic_salary=basic_salary,
                    housing=housing,
                    transport=transport,
                    overtime=overtime,
                    gosi=gosi,
                    tax=tax,
                    loan_deduction=loan_deduction,
                    net_salary=net_salary
                )
                created_count += 1
        
        messages.success(request, f'تم معالجة {created_count} راتب بنجاح.')
        return redirect('payrolls:payroll_run_detail', run_id=run_id)
    
    context = {
        'payroll_run': payroll_run,
    }
    
    return render(request, 'payrolls/process_payroll_confirm.html', context)


# كشوف الرواتب
@login_required
def payslips(request):
    """قائمة كشوف الرواتب"""
    payslips = PayrollDetail.objects.select_related('emp', 'run').all()
    
    # فلترة حسب الشهر
    month_year = request.GET.get('month_year')
    if month_year:
        payslips = payslips.filter(run__month_year=month_year)
    
    # فلترة حسب الموظف
    employee = request.GET.get('employee')
    if employee:
        payslips = payslips.filter(emp_id=employee)
    
    # ترتيب النتائج
    payslips = payslips.order_by('-run__run_date', 'emp__first_name')
    
    # التقسيم إلى صفحات
    paginator = Paginator(payslips, 20)
    page_number = request.GET.get('page')
    payslips = paginator.get_page(page_number)
    
    context = {
        'payslips': payslips,
    }
    
    return render(request, 'payrolls/payslips.html', context)


@login_required
def payslip_detail(request, payslip_id):
    """تفاصيل كشف الراتب"""
    payslip = get_object_or_404(PayrollDetail, payroll_detail_id=payslip_id)
    
    context = {
        'payslip': payslip,
    }
    
    return render(request, 'payrolls/payslip_detail.html', context)


@login_required
def print_payslip(request, payslip_id):
    """طباعة كشف الراتب"""
    payslip = get_object_or_404(PayrollDetail, payroll_detail_id=payslip_id)
    
    context = {
        'payslip': payslip,
    }
    
    return render(request, 'payrolls/payslip_print.html', context)


# بوابة الموظف
@login_required
def my_payslips(request):
    """كشوف رواتبي الشخصية"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('payrolls:dashboard')
    
    employee = request.user.employee
    
    # كشوف رواتب الموظف
    my_payslips = PayrollDetail.objects.filter(
        emp=employee
    ).select_related('run').order_by('-run__run_date')
    
    context = {
        'my_payslips': my_payslips,
        'employee': employee,
    }
    
    return render(request, 'payrolls/my_payslips.html', context)


@login_required
def my_salary(request):
    """راتبي الحالي"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('payrolls:dashboard')
    
    employee = request.user.employee
    
    # الراتب الحالي
    current_salary = EmployeeSalary.objects.filter(
        emp=employee,
        is_current=True
    ).first()
    
    if not current_salary:
        messages.info(request, 'لم يتم تحديد راتب لك بعد.')
        return redirect('payrolls:dashboard')
    
    # حساب التفاصيل
    total_allowances = (
        (current_salary.housing_allow or 0) +
        (current_salary.transport or 0) +
        (current_salary.other_allow or 0)
    )
    
    total_deductions = (
        (current_salary.gosi_deduction or 0) +
        (current_salary.tax_deduction or 0)
    )
    
    net_salary = (
        (current_salary.basic_salary or 0) +
        total_allowances -
        total_deductions
    )
    
    context = {
        'current_salary': current_salary,
        'total_allowances': total_allowances,
        'total_deductions': total_deductions,
        'net_salary': net_salary,
        'employee': employee,
    }
    
    return render(request, 'payrolls/my_salary.html', context)


# التقارير
@login_required
def reports(request):
    """تقارير الرواتب"""
    today = date.today()
    
    # إحصائيات عامة
    total_employees_with_salary = EmployeeSalary.objects.filter(is_current=True).count()
    total_payroll_runs = PayrollRun.objects.count()
    
    # إجمالي الرواتب الشهرية
    monthly_totals = EmployeeSalary.objects.filter(is_current=True).aggregate(
        total_basic=Sum('basic_salary'),
        total_allowances=Sum('housing_allow') + Sum('transport') + Sum('other_allow'),
        total_deductions=Sum('gosi_deduction') + Sum('tax_deduction')
    )
    
    # إحصائيات الأقسام
    department_stats = Department.objects.annotate(
        employee_count=Count('employee__employeesalary', filter=Q(employee__employeesalary__is_current=True)),
        avg_salary=Avg('employee__employeesalary__basic_salary', filter=Q(employee__employeesalary__is_current=True)),
        total_salary=Sum('employee__employeesalary__basic_salary', filter=Q(employee__employeesalary__is_current=True))
    ).filter(employee_count__gt=0).order_by('-total_salary')
    
    # اتجاهات الرواتب الشهرية
    monthly_trends = PayrollRun.objects.annotate(
        total_net_salary=Sum('payrolldetail__net_salary'),
        employee_count=Count('payrolldetail')
    ).order_by('-run_date')[:12]
    
    context = {
        'total_employees_with_salary': total_employees_with_salary,
        'total_payroll_runs': total_payroll_runs,
        'monthly_totals': monthly_totals,
        'department_stats': department_stats,
        'monthly_trends': monthly_trends,
    }
    
    return render(request, 'payrolls/reports.html', context)


@login_required
def export_payroll(request):
    """تصدير بيانات الرواتب"""
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payroll.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['الموظف', 'الراتب الأساسي', 'بدل السكن', 'بدل النقل', 'بدلات أخرى', 'GOSI', 'الضريبة', 'الراتب الصافي'])
    
    salaries = EmployeeSalary.objects.filter(is_current=True).select_related('emp')
    for salary in salaries:
        net_salary = (
            (salary.basic_salary or 0) +
            (salary.housing_allow or 0) +
            (salary.transport or 0) +
            (salary.other_allow or 0) -
            (salary.gosi_deduction or 0) -
            (salary.tax_deduction or 0)
        )
        
        writer.writerow([
            f"{salary.emp.first_name} {salary.emp.last_name}",
            salary.basic_salary or 0,
            salary.housing_allow or 0,
            salary.transport or 0,
            salary.other_allow or 0,
            salary.gosi_deduction or 0,
            salary.tax_deduction or 0,
            net_salary
        ])
    
    return response


# AJAX Views
@login_required
def calculate_salary_ajax(request):
    """حساب الراتب عبر AJAX"""
    basic_salary = Decimal(request.GET.get('basic_salary', '0'))
    housing_allow = Decimal(request.GET.get('housing_allow', '0'))
    transport = Decimal(request.GET.get('transport', '0'))
    other_allow = Decimal(request.GET.get('other_allow', '0'))
    gosi_deduction = Decimal(request.GET.get('gosi_deduction', '0'))
    tax_deduction = Decimal(request.GET.get('tax_deduction', '0'))
    
    # حساب الإجماليات
    total_allowances = housing_allow + transport + other_allow
    total_deductions = gosi_deduction + tax_deduction
    gross_salary = basic_salary + total_allowances
    net_salary = gross_salary - total_deductions
    
    data = {
        'total_allowances': float(total_allowances),
        'total_deductions': float(total_deductions),
        'gross_salary': float(gross_salary),
        'net_salary': float(net_salary)
    }
    
    return JsonResponse(data)


@login_required
def employee_salary_ajax(request, emp_id):
    """جلب راتب الموظف عبر AJAX"""
    try:
        employee = Employee.objects.get(emp_id=emp_id)
        current_salary = EmployeeSalary.objects.filter(
            emp=employee,
            is_current=True
        ).first()
        
        if current_salary:
            data = {
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'basic_salary': float(current_salary.basic_salary or 0),
                'housing_allow': float(current_salary.housing_allow or 0),
                'transport': float(current_salary.transport or 0),
                'other_allow': float(current_salary.other_allow or 0),
                'gosi_deduction': float(current_salary.gosi_deduction or 0),
                'tax_deduction': float(current_salary.tax_deduction or 0),
                'currency': current_salary.currency,
                'effective_date': current_salary.effective_date.strftime('%Y-%m-%d') if current_salary.effective_date else None
            }
        else:
            data = {
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'basic_salary': 0,
                'housing_allow': 0,
                'transport': 0,
                'other_allow': 0,
                'gosi_deduction': 0,
                'tax_deduction': 0,
                'currency': 'SAR',
                'effective_date': None
            }
        
        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'الموظف غير موجود'}, status=404)


# Bulk Operations
@login_required
def bulk_salary_update(request):
    """تحديث الرواتب بالجملة"""
    if request.method == 'POST':
        # معالجة التحديث الجماعي
        pass
    
    return render(request, 'payrolls/bulk_salary_update.html')


@login_required
def bulk_payslip_generation(request):
    """إنتاج كشوف الرواتب بالجملة"""
    if request.method == 'POST':
        run_id = request.POST.get('run_id')
        if run_id:
            payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
            
            # إنتاج كشوف الرواتب
            payslips = PayrollDetail.objects.filter(run=payroll_run)
            
            messages.success(request, f'تم إنتاج {payslips.count()} كشف راتب.')
        else:
            messages.error(request, 'يرجى تحديد تشغيل الرواتب.')
    
    return redirect('payrolls:payroll_runs')


# Analytics
@login_required
def payroll_analytics(request):
    """تحليلات الرواتب"""
    # تحليلات متقدمة للرواتب
    
    # توزيع الرواتب
    salary_distribution = EmployeeSalary.objects.filter(is_current=True).extra(
        select={
            'salary_range': """
                CASE 
                    WHEN basic_salary >= 20000 THEN 'عالي جداً (20000+)'
                    WHEN basic_salary >= 15000 THEN 'عالي (15000-19999)'
                    WHEN basic_salary >= 10000 THEN 'متوسط عالي (10000-14999)'
                    WHEN basic_salary >= 5000 THEN 'متوسط (5000-9999)'
                    WHEN basic_salary >= 3000 THEN 'منخفض (3000-4999)'
                    ELSE 'منخفض جداً (أقل من 3000)'
                END
            """
        }
    ).values('salary_range').annotate(
        count=Count('salary_id'),
        avg_salary=Avg('basic_salary')
    ).order_by('-avg_salary')
    
    # اتجاهات التكلفة الشهرية
    monthly_costs = PayrollRun.objects.annotate(
        total_cost=Sum('payrolldetail__net_salary')
    ).order_by('-run_date')[:12]
    
    context = {
        'salary_distribution': salary_distribution,
        'monthly_costs': monthly_costs,
    }
    
    return render(request, 'payrolls/analytics.html', context)


# ==== Enhanced Payroll Processing Views Using Services ====

@login_required
def advanced_payroll_processing(request, run_id):
    """معالجة متقدمة للرواتب باستخدام الخدمات"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    payroll_service = PayrollRunService()
    
    if request.method == 'POST':
        try:
            # فلتر الموظفين (اختياري)
            employee_filter = {}
            
            department_id = request.POST.get('department_id')
            if department_id:
                employee_filter['dept_id'] = department_id
            
            employee_status = request.POST.get('employee_status')
            if employee_status:
                employee_filter['emp_status'] = employee_status
            
            # معالجة الرواتب
            result = payroll_service.process_payroll_run(payroll_run, employee_filter)
            
            if result['success']:
                messages.success(
                    request, 
                    f'تم معالجة {result["processed_employees"]} موظف من أصل {result["total_employees"]} بنجاح.'
                )
                
                if result['errors']:
                    for error in result['errors'][:5]:  # عرض أول 5 أخطاء فقط
                        messages.warning(request, error)
            
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء معالجة الرواتب: {str(e)}')
            logger.error(f'Payroll processing error: {str(e)}')
        
        return redirect('payrolls:payroll_run_detail', run_id=run_id)
    
    # بيانات النموذج
    departments = Department.objects.filter(is_active=True).order_by('dept_name')
    
    context = {
        'payroll_run': payroll_run,
        'departments': departments,
    }
    
    return render(request, 'payrolls/advanced_processing.html', context)


@login_required
@require_http_methods(["POST"])
def approve_payroll_run_view(request, run_id):
    """اعتماد تشغيل الرواتب"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    payroll_service = PayrollRunService()
    
    try:
        # الحصول على بيانات الموظف المعتمد
        approved_by = None
        if hasattr(request.user, 'employee'):
            approved_by = request.user.employee
        
        payroll_service.approve_payroll_run(payroll_run, approved_by)
        messages.success(request, f'تم اعتماد تشغيل الرواتب لشهر {payroll_run.month_year} بنجاح.')
        
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء اعتماد تشغيل الرواتب: {str(e)}')
        logger.error(f'Payroll approval error: {str(e)}')
    
    return redirect('payrolls:payroll_run_detail', run_id=run_id)


@login_required
@require_http_methods(["POST"])
def mark_payroll_paid_view(request, run_id):
    """تحديد تشغيل الرواتب كمدفوع"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    payroll_service = PayrollRunService()
    
    try:
        # الحصول على بيانات الموظف المؤكد
        confirmed_by = None
        if hasattr(request.user, 'employee'):
            confirmed_by = request.user.employee
        
        payroll_service.mark_payroll_as_paid(payroll_run, confirmed_by)
        messages.success(request, f'تم تحديد تشغيل الرواتب لشهر {payroll_run.month_year} كمدفوع.')
        
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء تحديد حالة الدفع: {str(e)}')
        logger.error(f'Payroll payment marking error: {str(e)}')
    
    return redirect('payrolls:payroll_run_detail', run_id=run_id)


@login_required
@require_http_methods(["POST"])
def cancel_payroll_run_view(request, run_id):
    """إلغاء تشغيل الرواتب"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    payroll_service = PayrollRunService()
    
    try:
        payroll_service.cancel_payroll_run(payroll_run)
        messages.success(request, f'تم إلغاء تشغيل الرواتب لشهر {payroll_run.month_year} بنجاح.')
        
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء إلغاء تشغيل الرواتب: {str(e)}')
        logger.error(f'Payroll cancellation error: {str(e)}')
    
    return redirect('payrolls:payroll_runs')


@login_required
def create_advanced_payroll_run(request):
    """إنشاء تشغيل رواتب متقدم"""
    payroll_service = PayrollRunService()
    
    if request.method == 'POST':
        try:
            month_year = request.POST.get('month_year')
            payroll_type = request.POST.get('payroll_type', 'monthly')
            
            # الحصول على بيانات الموظف المنشئ
            created_by = None
            if hasattr(request.user, 'employee'):
                created_by = request.user.employee
            
            payroll_run = payroll_service.create_payroll_run(
                month_year=month_year,
                payroll_type=payroll_type,
                created_by=created_by
            )
            
            messages.success(
                request, 
                f'تم إنشاء تشغيل الرواتب لشهر {payroll_run.month_year} بنجاح.'
            )
            
            return redirect('payrolls:payroll_run_detail', run_id=payroll_run.run_id)
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء تشغيل الرواتب: {str(e)}')
            logger.error(f'Payroll run creation error: {str(e)}')
    
    # تحديد الشهر الافتراضي
    today = date.today()
    default_month_year = today.strftime('%Y-%m')
    
    payroll_types = PayrollRun.PAYROLL_TYPES
    
    context = {
        'default_month_year': default_month_year,
        'payroll_types': payroll_types,
        'title': 'إنشاء تشغيل رواتب جديد'
    }
    
    return render(request, 'payrolls/create_advanced_payroll_run.html', context)


@login_required
def detailed_payslip_view(request, payslip_id):
    """عرض كشف راتب مفصل"""
    payroll_detail = get_object_or_404(PayrollDetail, payroll_detail_id=payslip_id)
    report_service = PayrollReportService()
    
    # إنشاء كشف راتب مفصل
    payslip_data = report_service.generate_employee_payslip(payroll_detail)
    
    context = {
        'payroll_detail': payroll_detail,
        'payslip_data': payslip_data,
    }
    
    return render(request, 'payrolls/detailed_payslip.html', context)


@login_required
def payroll_summary_report(request, run_id):
    """تقرير ملخص الرواتب"""
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    report_service = PayrollReportService()
    
    # إنشاء تقرير الملخص
    summary_data = report_service.generate_payroll_summary_report(payroll_run)
    
    # تفاصيل إضافية
    department_breakdown = PayrollDetail.objects.filter(
        run=payroll_run
    ).values(
        'emp__dept__dept_name'
    ).annotate(
        employee_count=Count('payroll_detail_id'),
        total_basic=Sum('basic_salary'),
        total_allowances=Sum('total_allowances'),
        total_deductions=Sum('total_deductions'),
        total_net=Sum('net_salary')
    ).order_by('-total_net')
    
    context = {
        'payroll_run': payroll_run,
        'summary_data': summary_data,
        'department_breakdown': department_breakdown,
    }
    
    return render(request, 'payrolls/payroll_summary_report.html', context)


@login_required
@csrf_exempt
def recalculate_employee_payroll(request, run_id, emp_id):
    """إعادة حساب راتب موظف محدد"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
        employee = get_object_or_404(Employee, emp_id=emp_id)
        
        if payroll_run.status not in ['draft', 'calculating', 'review']:
            return JsonResponse(
                {'error': 'لا يمكن إعادة حساب الرواتب في هذه الحالة'}, 
                status=400
            )
        
        calculation_service = PayrollCalculationService()
        
        # إعادة حساب راتب الموظف
        payroll_detail = calculation_service.calculate_employee_payroll(
            employee, payroll_run
        )
        
        if payroll_detail:
            return JsonResponse({
                'success': True,
                'message': f'تم إعادة حساب راتب {employee.emp_full_name} بنجاح',
                'net_salary': float(payroll_detail.net_salary),
                'gross_salary': float(payroll_detail.gross_salary),
                'total_deductions': float(payroll_detail.total_deductions)
            })
        else:
            return JsonResponse(
                {'error': 'فشل في إعادة حساب الراتب'}, 
                status=400
            )
    
    except Exception as e:
        logger.error(f'Employee payroll recalculation error: {str(e)}')
        return JsonResponse(
            {'error': f'حدث خطأ أثناء إعادة الحساب: {str(e)}'}, 
            status=500
        )


@login_required
def payroll_processing_status(request, run_id):
    """حالة معالجة الرواتب (AJAX)"""
    try:
        payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
        
        # حساب نسبة الإنجاز
        progress = payroll_run.processing_progress
        
        data = {
            'status': payroll_run.status,
            'progress': progress,
            'processed_employees': payroll_run.processed_employees,
            'total_employees': payroll_run.total_employees,
            'total_net_amount': float(payroll_run.total_net_amount),
            'is_complete': progress >= 100
        }
        
        return JsonResponse(data)
        
    except PayrollRun.DoesNotExist:
        return JsonResponse({'error': 'تشغيل الرواتب غير موجود'}, status=404)
    except Exception as e:
        logger.error(f'Payroll status check error: {str(e)}')
        return JsonResponse({'error': 'حدث خطأ أثناء فحص الحالة'}, status=500)


@login_required
def employee_payroll_preview(request, run_id, emp_id):
    """معاينة راتب موظف قبل المعالجة"""
    try:
        payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
        employee = get_object_or_404(Employee, emp_id=emp_id)
        
        calculation_service = PayrollCalculationService()
        
        # حساب معاينة للراتب
        preview_detail = calculation_service.calculate_employee_payroll(
            employee, payroll_run
        )
        
        if preview_detail:
            data = {
                'employee_name': employee.emp_full_name,
                'basic_salary': float(preview_detail.basic_salary),
                'total_allowances': float(preview_detail.total_allowances),
                'overtime_amount': float(preview_detail.overtime_amount),
                'bonus_amount': float(preview_detail.bonus_amount),
                'gross_salary': float(preview_detail.gross_salary),
                'total_deductions': float(preview_detail.total_deductions),
                'net_salary': float(preview_detail.net_salary),
                'worked_days': float(preview_detail.worked_days),
                'absent_days': float(preview_detail.absent_days),
                'leave_days': float(preview_detail.leave_days),
                'overtime_hours': float(preview_detail.overtime_hours),
                'calculation_notes': preview_detail.calculation_notes
            }
            
            return JsonResponse(data)
        else:
            return JsonResponse(
                {'error': 'لا يمكن حساب راتب هذا الموظف'}, 
                status=400
            )
    
    except Exception as e:
        logger.error(f'Employee payroll preview error: {str(e)}')
        return JsonResponse(
            {'error': f'حدث خطأ أثناء المعاينة: {str(e)}'}, 
            status=500
        )