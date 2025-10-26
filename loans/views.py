from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django import forms
from datetime import date, datetime, timedelta
from decimal import Decimal
from .models import LoanType, EmployeeLoan, LoanInstallment
from employees.models import Employee
from org.models import Department
from .forms import LoanTypeForm, EmployeeLoanForm, LoanInstallmentForm


@login_required
def dashboard(request):
    """لوحة تحكم القروض والسلف"""
    today = date.today()
    
    # إحصائيات عامة
    total_loan_types = LoanType.objects.count()
    total_loans = EmployeeLoan.objects.count()
    active_loans = EmployeeLoan.objects.filter(status='Active').count()
    pending_loans = EmployeeLoan.objects.filter(status='Pending').count()
    
    # إجمالي المبالغ
    loan_amounts = EmployeeLoan.objects.filter(status='Active').aggregate(
        total_requested=Sum('request_amount'),
        total_approved=Sum('approved_amount')
    )
    
    # الأقساط المستحقة
    due_installments = LoanInstallment.objects.filter(
        due_date__lte=today,
        status='Pending'
    ).count()
    
    overdue_installments = LoanInstallment.objects.filter(
        due_date__lt=today,
        status='Pending'
    ).count()
    
    # إجمالي الأقساط المستحقة
    due_amount = LoanInstallment.objects.filter(
        due_date__lte=today,
        status='Pending'
    ).aggregate(
        total_due=Sum('amount')
    )['total_due'] or 0
    
    # القروض الحديثة
    recent_loans = EmployeeLoan.objects.select_related(
        'emp', 'loan_type'
    ).order_by('-start_date')[:5]
    
    # إحصائيات أنواع القروض
    loan_type_stats = LoanType.objects.annotate(
        loan_count=Count('employeeloan'),
        total_amount=Sum('employeeloan__approved_amount'),
        avg_amount=Avg('employeeloan__approved_amount')
    ).filter(loan_count__gt=0).order_by('-total_amount')
    
    # إحصائيات الأقسام
    department_stats = Department.objects.annotate(
        loan_count=Count('employee__employeeloan'),
        total_amount=Sum('employee__employeeloan__approved_amount')
    ).filter(loan_count__gt=0).order_by('-total_amount')[:5]
    
    # الأقساط المستحقة هذا الشهر
    current_month = today.replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    monthly_installments = LoanInstallment.objects.filter(
        due_date__gte=current_month,
        due_date__lt=next_month
    ).aggregate(
        count=Count('installment_id'),
        total_amount=Sum('amount')
    )
    
    context = {
        'total_loan_types': total_loan_types,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'pending_loans': pending_loans,
        'loan_amounts': loan_amounts,
        'due_installments': due_installments,
        'overdue_installments': overdue_installments,
        'due_amount': due_amount,
        'recent_loans': recent_loans,
        'loan_type_stats': loan_type_stats,
        'department_stats': department_stats,
        'monthly_installments': monthly_installments,
    }
    
    return render(request, 'loans/dashboard.html', context)


# إدارة أنواع القروض
@login_required
def loan_type_list(request):
    """قائمة أنواع القروض"""
    loan_types = LoanType.objects.annotate(
        loan_count=Count('employeeloan'),
        total_amount=Sum('employeeloan__approved_amount'),
        avg_amount=Avg('employeeloan__approved_amount')
    ).order_by('type_name')
    
    context = {
        'loan_types': loan_types,
    }
    
    return render(request, 'loans/loan_type_list.html', context)


@login_required
def add_loan_type(request):
    """إضافة نوع قرض جديد"""
    if request.method == 'POST':
        form = LoanTypeForm(request.POST)
        if form.is_valid():
            loan_type = form.save()
            messages.success(request, f'تم إضافة نوع القرض {loan_type.type_name} بنجاح.')
            return redirect('loans:loan_type_detail', type_id=loan_type.loan_type_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = LoanTypeForm()
    
    context = {
        'form': form,
        'title': 'إضافة نوع قرض جديد'
    }
    
    return render(request, 'loans/loan_type_form.html', context)


@login_required
def loan_type_detail(request, type_id):
    """تفاصيل نوع القرض"""
    loan_type = get_object_or_404(LoanType, loan_type_id=type_id)
    
    # قروض هذا النوع
    loans = EmployeeLoan.objects.filter(
        loan_type=loan_type
    ).select_related('emp').order_by('-start_date')
    
    # إحصائيات النوع
    type_stats = loans.aggregate(
        total_loans=Count('loan_id'),
        active_loans=Count('loan_id', filter=Q(status='Active')),
        pending_loans=Count('loan_id', filter=Q(status='Pending')),
        total_requested=Sum('request_amount'),
        total_approved=Sum('approved_amount'),
        avg_amount=Avg('approved_amount')
    )
    
    context = {
        'loan_type': loan_type,
        'loans': loans,
        'type_stats': type_stats,
    }
    
    return render(request, 'loans/loan_type_detail.html', context)


# إدارة قروض الموظفين
@login_required
def loan_list(request):
    """قائمة قروض الموظفين"""
    loans = EmployeeLoan.objects.select_related('emp', 'loan_type').all()
    
    # البحث والفلترة
    search = request.GET.get('search')
    if search:
        loans = loans.filter(
            Q(emp__first_name__icontains=search) |
            Q(emp__last_name__icontains=search) |
            Q(emp__emp_code__icontains=search)
        )
    
    # فلترة حسب نوع القرض
    loan_type = request.GET.get('loan_type')
    if loan_type:
        loans = loans.filter(loan_type_id=loan_type)
    
    # فلترة حسب الحالة
    status = request.GET.get('status')
    if status:
        loans = loans.filter(status=status)
    
    # فلترة حسب القسم
    department = request.GET.get('department')
    if department:
        loans = loans.filter(emp__dept_id=department)
    
    # ترتيب النتائج
    loans = loans.order_by('-start_date')
    
    # التقسيم إلى صفحات
    paginator = Paginator(loans, 20)
    page_number = request.GET.get('page')
    loans = paginator.get_page(page_number)
    
    # قوائم للفلترة
    loan_types = LoanType.objects.all().order_by('type_name')
    departments = Department.objects.filter(is_active=True).order_by('dept_name')
    
    context = {
        'loans': loans,
        'loan_types': loan_types,
        'departments': departments,
    }
    
    return render(request, 'loans/loan_list.html', context)


@login_required
def add_loan(request):
    """إضافة قرض جديد"""
    if request.method == 'POST':
        form = EmployeeLoanForm(request.POST)
        if form.is_valid():
            loan = form.save()
            messages.success(request, f'تم إضافة القرض للموظف {loan.emp.first_name} {loan.emp.last_name} بنجاح.')
            return redirect('loans:loan_detail', loan_id=loan.loan_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeLoanForm()
    
    context = {
        'form': form,
        'title': 'إضافة قرض جديد'
    }
    
    return render(request, 'loans/loan_form.html', context)


@login_required
def loan_detail(request, loan_id):
    """تفاصيل القرض"""
    loan = get_object_or_404(EmployeeLoan, loan_id=loan_id)
    
    # أقساط القرض
    installments = LoanInstallment.objects.filter(
        loan=loan
    ).order_by('due_date')
    
    # إحصائيات القرض
    installment_stats = installments.aggregate(
        total_installments=Count('installment_id'),
        paid_installments=Count('installment_id', filter=Q(status='Paid')),
        pending_installments=Count('installment_id', filter=Q(status='Pending')),
        overdue_installments=Count('installment_id', filter=Q(due_date__lt=date.today(), status='Pending')),
        total_paid=Sum('amount', filter=Q(status='Paid')),
        total_pending=Sum('amount', filter=Q(status='Pending'))
    )
    
    # حساب المبلغ المتبقي
    remaining_amount = (loan.approved_amount or 0) - (installment_stats['total_paid'] or 0)
    
    context = {
        'loan': loan,
        'installments': installments,
        'installment_stats': installment_stats,
        'remaining_amount': remaining_amount,
    }
    
    return render(request, 'loans/loan_detail.html', context)


@login_required
def edit_loan(request, loan_id):
    """تعديل القرض"""
    loan = get_object_or_404(EmployeeLoan, loan_id=loan_id)
    
    if request.method == 'POST':
        form = EmployeeLoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save()
            messages.success(request, f'تم تحديث القرض للموظف {loan.emp.first_name} {loan.emp.last_name} بنجاح.')
            return redirect('loans:loan_detail', loan_id=loan.loan_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeLoanForm(instance=loan)
    
    context = {
        'form': form,
        'loan': loan,
        'title': 'تعديل القرض'
    }
    
    return render(request, 'loans/loan_form.html', context)


@login_required
@require_http_methods(["POST"])
def approve_loan(request, loan_id):
    """اعتماد القرض"""
    loan = get_object_or_404(EmployeeLoan, loan_id=loan_id)
    
    if loan.status == 'Pending':
        loan.status = 'Active'
        loan.approved_by = request.user.id  # يجب تعديل هذا حسب نموذج المستخدم
        loan.save()
        
        # إنشاء الأقساط تلقائياً
        if loan.approved_amount and loan.installment_amt:
            installment_count = int(loan.approved_amount / loan.installment_amt)
            
            for i in range(installment_count):
                due_date = loan.start_date + timedelta(days=30 * (i + 1))
                LoanInstallment.objects.create(
                    loan=loan,
                    due_date=due_date,
                    amount=loan.installment_amt,
                    status='Pending'
                )
        
        messages.success(request, f'تم اعتماد القرض للموظف {loan.emp.first_name} {loan.emp.last_name}.')
    else:
        messages.warning(request, 'القرض معتمد مسبقاً أو في حالة أخرى.')
    
    return redirect('loans:loan_detail', loan_id=loan_id)


@login_required
@require_http_methods(["POST"])
def reject_loan(request, loan_id):
    """رفض القرض"""
    loan = get_object_or_404(EmployeeLoan, loan_id=loan_id)
    
    if loan.status == 'Pending':
        loan.status = 'Rejected'
        loan.save()
        
        messages.success(request, f'تم رفض القرض للموظف {loan.emp.first_name} {loan.emp.last_name}.')
    else:
        messages.warning(request, 'لا يمكن رفض القرض في هذه الحالة.')
    
    return redirect('loans:loan_detail', loan_id=loan_id)


# إدارة الأقساط
@login_required
def installment_list(request):
    """قائمة الأقساط"""
    installments = LoanInstallment.objects.select_related('loan__emp', 'loan__loan_type').all()
    
    # فلترة حسب الحالة
    status = request.GET.get('status')
    if status:
        installments = installments.filter(status=status)
    elif status == 'overdue':
        installments = installments.filter(
            due_date__lt=date.today(),
            status='Pending'
        )
    
    # فلترة حسب التاريخ
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        installments = installments.filter(due_date__gte=date_from)
    if date_to:
        installments = installments.filter(due_date__lte=date_to)
    
    # ترتيب النتائج
    installments = installments.order_by('due_date', 'loan__emp__first_name')
    
    # التقسيم إلى صفحات
    paginator = Paginator(installments, 20)
    page_number = request.GET.get('page')
    installments = paginator.get_page(page_number)
    
    context = {
        'installments': installments,
    }
    
    return render(request, 'loans/installment_list.html', context)


@login_required
@require_http_methods(["POST"])
def pay_installment(request, installment_id):
    """دفع قسط"""
    installment = get_object_or_404(LoanInstallment, installment_id=installment_id)
    
    if installment.status == 'Pending':
        installment.status = 'Paid'
        installment.paid_date = date.today()
        installment.save()
        
        # التحقق من اكتمال دفع القرض
        remaining_installments = LoanInstallment.objects.filter(
            loan=installment.loan,
            status='Pending'
        ).count()
        
        if remaining_installments == 0:
            installment.loan.status = 'Completed'
            installment.loan.save()
        
        messages.success(request, f'تم دفع القسط للموظف {installment.loan.emp.first_name} {installment.loan.emp.last_name}.')
    else:
        messages.warning(request, 'القسط مدفوع مسبقاً.')
    
    return redirect('loans:loan_detail', loan_id=installment.loan.loan_id)


# بوابة الموظف
@login_required
def my_loans(request):
    """قروضي الشخصية"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('loans:dashboard')
    
    employee = request.user.employee
    
    # قروض الموظف
    my_loans = EmployeeLoan.objects.filter(
        emp=employee
    ).select_related('loan_type').order_by('-start_date')
    
    # إحصائيات شخصية
    personal_stats = my_loans.aggregate(
        total_loans=Count('loan_id'),
        active_loans=Count('loan_id', filter=Q(status='Active')),
        completed_loans=Count('loan_id', filter=Q(status='Completed')),
        total_borrowed=Sum('approved_amount'),
        total_remaining=Sum('approved_amount', filter=Q(status='Active'))
    )
    
    context = {
        'my_loans': my_loans,
        'personal_stats': personal_stats,
        'employee': employee,
    }
    
    return render(request, 'loans/my_loans.html', context)


@login_required
def request_loan(request):
    """طلب قرض جديد (للموظف)"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'لا يمكن الوصول لهذه الصفحة.')
        return redirect('loans:dashboard')
    
    if request.method == 'POST':
        form = EmployeeLoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.emp = request.user.employee
            loan.status = 'Pending'
            loan.save()
            messages.success(request, 'تم إرسال طلب القرض بنجاح.')
            return redirect('loans:my_loans')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeLoanForm()
        # إخفاء حقل الموظف لأنه سيتم تعيينه تلقائياً
        form.fields['emp'].widget = forms.HiddenInput()
        form.fields['emp'].initial = request.user.employee
        form.fields['status'].widget = forms.HiddenInput()
        form.fields['status'].initial = 'Pending'
    
    context = {
        'form': form,
        'title': 'طلب قرض جديد'
    }
    
    return render(request, 'loans/request_loan.html', context)


# التقارير
@login_required
def reports(request):
    """تقارير القروض"""
    today = date.today()
    
    # إحصائيات عامة
    total_loans = EmployeeLoan.objects.count()
    active_loans = EmployeeLoan.objects.filter(status='Active').count()
    completed_loans = EmployeeLoan.objects.filter(status='Completed').count()
    
    # إجمالي المبالغ
    amount_stats = EmployeeLoan.objects.aggregate(
        total_requested=Sum('request_amount'),
        total_approved=Sum('approved_amount'),
        avg_loan_amount=Avg('approved_amount')
    )
    
    # إحصائيات الأقساط
    installment_stats = LoanInstallment.objects.aggregate(
        total_installments=Count('installment_id'),
        paid_installments=Count('installment_id', filter=Q(status='Paid')),
        overdue_installments=Count('installment_id', filter=Q(due_date__lt=today, status='Pending')),
        total_paid_amount=Sum('amount', filter=Q(status='Paid')),
        total_overdue_amount=Sum('amount', filter=Q(due_date__lt=today, status='Pending'))
    )
    
    # إحصائيات أنواع القروض
    loan_type_stats = LoanType.objects.annotate(
        loan_count=Count('employeeloan'),
        total_amount=Sum('employeeloan__approved_amount'),
        avg_amount=Avg('employeeloan__approved_amount')
    ).filter(loan_count__gt=0).order_by('-total_amount')
    
    # إحصائيات الأقسام
    department_stats = Department.objects.annotate(
        loan_count=Count('employee__employeeloan'),
        total_amount=Sum('employee__employeeloan__approved_amount'),
        active_loans=Count('employee__employeeloan', filter=Q(employee__employeeloan__status='Active'))
    ).filter(loan_count__gt=0).order_by('-total_amount')
    
    # اتجاهات القروض الشهرية
    monthly_trends = EmployeeLoan.objects.filter(
        start_date__isnull=False
    ).extra(
        select={'month': "MONTH(start_date)", 'year': "YEAR(start_date)"}
    ).values('month', 'year').annotate(
        loan_count=Count('loan_id'),
        total_amount=Sum('approved_amount')
    ).order_by('year', 'month')[-12:]
    
    context = {
        'total_loans': total_loans,
        'active_loans': active_loans,
        'completed_loans': completed_loans,
        'amount_stats': amount_stats,
        'installment_stats': installment_stats,
        'loan_type_stats': loan_type_stats,
        'department_stats': department_stats,
        'monthly_trends': monthly_trends,
    }
    
    return render(request, 'loans/reports.html', context)


@login_required
def export_loans(request):
    """تصدير بيانات القروض"""
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="loans.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['الموظف', 'نوع القرض', 'المبلغ المطلوب', 'المبلغ المعتمد', 'قسط شهري', 'تاريخ البداية', 'تاريخ النهاية', 'الحالة'])
    
    loans = EmployeeLoan.objects.select_related('emp', 'loan_type').all()
    for loan in loans:
        writer.writerow([
            f"{loan.emp.first_name} {loan.emp.last_name}",
            loan.loan_type.type_name if loan.loan_type else '',
            loan.request_amount or 0,
            loan.approved_amount or 0,
            loan.installment_amt or 0,
            loan.start_date or '',
            loan.end_date or '',
            loan.status
        ])
    
    return response


# AJAX Views
@login_required
def calculate_installments(request):
    """حساب الأقساط عبر AJAX"""
    loan_amount = request.GET.get('loan_amount')
    installment_amount = request.GET.get('installment_amount')
    interest_rate = request.GET.get('interest_rate', '0')
    
    if not loan_amount or not installment_amount:
        return JsonResponse({'error': 'بيانات ناقصة'}, status=400)
    
    try:
        loan_amount = Decimal(loan_amount)
        installment_amount = Decimal(installment_amount)
        interest_rate = Decimal(interest_rate)
        
        # حساب عدد الأقساط
        installment_count = int(loan_amount / installment_amount)
        
        # حساب الفوائد إذا وجدت
        total_interest = loan_amount * (interest_rate / 100)
        total_amount = loan_amount + total_interest
        
        # إعادة حساب القسط مع الفوائد
        if interest_rate > 0:
            installment_with_interest = total_amount / installment_count
        else:
            installment_with_interest = installment_amount
        
        data = {
            'installment_count': installment_count,
            'total_interest': float(total_interest),
            'total_amount': float(total_amount),
            'installment_with_interest': float(installment_with_interest)
        }
        
        return JsonResponse(data)
    except (ValueError, ZeroDivisionError):
        return JsonResponse({'error': 'بيانات غير صحيحة'}, status=400)


@login_required
def loan_eligibility_check(request, emp_id):
    """فحص أهلية الموظف للقرض عبر AJAX"""
    try:
        employee = Employee.objects.get(emp_id=emp_id)
        
        # فحص القروض النشطة
        active_loans = EmployeeLoan.objects.filter(
            emp=employee,
            status='Active'
        ).count()
        
        # حساب إجمالي المبالغ النشطة
        total_active_amount = EmployeeLoan.objects.filter(
            emp=employee,
            status='Active'
        ).aggregate(
            total=Sum('approved_amount')
        )['total'] or 0
        
        # فحص الأقساط المتأخرة
        overdue_installments = LoanInstallment.objects.filter(
            loan__emp=employee,
            due_date__lt=date.today(),
            status='Pending'
        ).count()
        
        # تحديد الأهلية
        is_eligible = True
        reasons = []
        
        if active_loans >= 3:  # حد أقصى 3 قروض نشطة
            is_eligible = False
            reasons.append('يوجد 3 قروض نشطة أو أكثر')
        
        if total_active_amount > 50000:  # حد أقصى 50,000
            is_eligible = False
            reasons.append('إجمالي القروض النشطة يتجاوز الحد المسموح')
        
        if overdue_installments > 0:
            is_eligible = False
            reasons.append('يوجد أقساط متأخرة')
        
        data = {
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'is_eligible': is_eligible,
            'active_loans': active_loans,
            'total_active_amount': float(total_active_amount),
            'overdue_installments': overdue_installments,
            'reasons': reasons
        }
        
        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'الموظف غير موجود'}, status=404)