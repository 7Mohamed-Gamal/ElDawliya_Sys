from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import os
import mimetypes
from .models import Employee, EmployeeBankAccount, EmployeeDocument
from org.models import Department, Job, Branch
from .forms import EmployeeForm


@login_required
def dashboard(request):
    """صفحة لوحة التحكم الرئيسية لتطبيق الموظفين"""
    # إحصائيات عامة
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(emp_status='Active').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()
    total_departments = Department.objects.count()
    total_jobs = Job.objects.count()

    # الموظفين المضافين حديثاً
    recent_employees = Employee.objects.select_related('dept', 'job').order_by('-created_at')[:5]

    # إحصائيات الأقسام
    department_stats = Department.objects.annotate(
        employee_count=Count('employee')
    ).filter(employee_count__gt=0).order_by('-employee_count')[:5]

    # حساب النسب المئوية
    for dept in department_stats:
        dept.percentage = (dept.employee_count / total_employees * 100) if total_employees > 0 else 0

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_departments': total_departments,
        'total_jobs': total_jobs,
        'recent_employees': recent_employees,
        'department_stats': department_stats,
    }

    return render(request, 'employees/index.html', context)


@login_required
def employee_list(request):
    """عرض قائمة الموظفين مع البحث والفلترة"""
    employees = Employee.objects.select_related('dept', 'job', 'branch').all()

    # البحث
    search = request.GET.get('search')
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(emp_code__icontains=search) |
            Q(email__icontains=search) |
            Q(mobile__icontains=search)
        )

    # فلترة حسب القسم
    department = request.GET.get('department')
    if department:
        employees = employees.filter(dept_id=department)

    # فلترة حسب الحالة
    status = request.GET.get('status')
    if status:
        employees = employees.filter(emp_status=status)

    # ترتيب النتائج
    employees = employees.order_by('emp_code')

    # التقسيم إلى صفحات
    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    employees = paginator.get_page(page_number)

    # قائمة الأقسام للفلترة
    departments = Department.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('dept_name')

    context = {
        'employees': employees,
        'departments': departments,
    }

    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_detail(request, emp_id):
    """عرض تفاصيل موظف محدد"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    context = {
        'employee': employee,
    }

    return render(request, 'employees/employee_detail.html', context)


@login_required
def add_employee(request):
    """إضافة موظف جديد"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'تم إضافة الموظف {employee.first_name} {employee.last_name} بنجاح.')
            return redirect('employees:detail', emp_id=employee.emp_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'employee': Employee(),  # موظف فارغ للقالب
    }

    return render(request, 'employees/employee_form.html', context)


@login_required
def edit_employee(request, emp_id):
    """تعديل بيانات موظف - يعيد التوجيه للتعديل الشامل"""
    # Redirect to comprehensive edit for better user experience
    return redirect('employees:comprehensive_edit', emp_id=emp_id)


@login_required
@require_http_methods(["POST"])
def employee_delete(request, emp_id):
    """حذف موظف"""
    employee = get_object_or_404(Employee, emp_id=emp_id)
    employee_name = f"{employee.first_name} {employee.last_name}"

    try:
        employee.delete()
        messages.success(request, f'تم حذف الموظف {employee_name} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف الموظف: {str(e)}')

    return redirect('employees:employee_list')


@login_required
def department_list(request):
    """عرض قائمة الأقسام"""
    departments = Department.objects.annotate(
        employee_count=Count('employee')
    ).order_by('dept_name')

    context = {
        'departments': departments,
    }

    return render(request, 'employees/department_list.html', context)


@login_required
def job_list(request):
    """عرض قائمة الوظائف"""
    jobs = Job.objects.annotate(
        employee_count=Count('employee')
    ).order_by('job_title')

    context = {
        'jobs': jobs,
    }

    return render(request, 'employees/job_list.html', context)


# API Views for AJAX requests
@login_required
def get_departments_by_branch(request):
    """API لجلب الأقسام حسب الفرع"""
    branch_id = request.GET.get('branch_id')
    if branch_id:
        departments = Department.objects.filter(
            branch_id=branch_id,
            is_active=True
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.values('dept_id', 'dept_name')
        return JsonResponse(list(departments), safe=False)
    return JsonResponse([], safe=False)


@login_required
def get_employees_by_department(request):
    """API لجلب الموظفين حسب القسم (للمدير المباشر)"""
    dept_id = request.GET.get('dept_id')
    if dept_id:
        employees = Employee.objects.filter(
            dept_id=dept_id,
            emp_status='Active'
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.values('emp_id', 'first_name', 'last_name', 'emp_code')

        # تنسيق البيانات
        employee_list = []
        for emp in employees:
            employee_list.append({
                'emp_id': emp['emp_id'],
                'name': f"{emp['first_name']} {emp['last_name']} ({emp['emp_code']})"
            })

        return JsonResponse(employee_list, safe=False)
    return JsonResponse([], safe=False)


@login_required
def delete_employee(request, emp_id):
    """حذف موظف"""
    return employee_delete(request, emp_id)


@login_required
def employee_profile(request, emp_id):
    """عرض ملف الموظف الشخصي"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    # جلب الحسابات البنكية
    bank_accounts = EmployeeBankAccount.objects.filter(emp=employee).prefetch_related()  # TODO: Add appropriate prefetch_related fields

    # جلب المستندات
    documents = EmployeeDocument.objects.filter(emp=employee).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('-upload_date')

    context = {
        'employee': employee,
        'bank_accounts': bank_accounts,
        'documents': documents,
    }

    return render(request, 'employees/employee_profile.html', context)


@login_required
def add_department(request):
    """إضافة قسم جديد"""
    from .forms import DepartmentForm

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'تم إضافة القسم {department.dept_name} بنجاح.')
            return redirect('employees:department_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = DepartmentForm()

    context = {
        'form': form,
        'title': 'إضافة قسم جديد'
    }

    return render(request, 'employees/department_form.html', context)


@login_required
def department_detail(request, dept_id):
    """عرض تفاصيل قسم"""
    department = get_object_or_404(Department, dept_id=dept_id)
    employees = Employee.objects.filter(dept=department).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('emp_code')

    context = {
        'department': department,
        'employees': employees,
    }

    return render(request, 'employees/department_detail.html', context)


@login_required
def edit_department(request, dept_id):
    """تعديل قسم"""
    from .forms import DepartmentForm

    department = get_object_or_404(Department, dept_id=dept_id)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'تم تحديث القسم {department.dept_name} بنجاح.')
            return redirect('employees:department_detail', dept_id=department.dept_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = DepartmentForm(instance=department)

    context = {
        'form': form,
        'department': department,
        'title': 'تعديل القسم'
    }

    return render(request, 'employees/department_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_department(request, dept_id):
    """حذف قسم"""
    department = get_object_or_404(Department, dept_id=dept_id)
    department_name = department.dept_name

    try:
        # التحقق من وجود موظفين في القسم
        if Employee.objects.filter(dept=department).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exists():
            messages.error(request, f'لا يمكن حذف القسم {department_name} لأنه يحتوي على موظفين.')
        else:
            department.delete()
            messages.success(request, f'تم حذف القسم {department_name} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف القسم: {str(e)}')

    return redirect('employees:department_list')


@login_required
def position_list(request):
    """عرض قائمة الوظائف"""
    return job_list(request)


@login_required
def add_position(request):
    """إضافة وظيفة جديدة"""
    from .forms import JobForm

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'تم إضافة الوظيفة {job.job_title} بنجاح.')
            return redirect('employees:position_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = JobForm()

    context = {
        'form': form,
        'title': 'إضافة وظيفة جديدة'
    }

    return render(request, 'employees/job_form.html', context)


@login_required
def position_detail(request, position_id):
    """عرض تفاصيل وظيفة"""
    job = get_object_or_404(Job, job_id=position_id)
    employees = Employee.objects.filter(job=job).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('emp_code')

    context = {
        'job': job,
        'employees': employees,
    }

    return render(request, 'employees/job_detail.html', context)


@login_required
def edit_position(request, position_id):
    """تعديل وظيفة"""
    from .forms import JobForm

    job = get_object_or_404(Job, job_id=position_id)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'تم تحديث الوظيفة {job.job_title} بنجاح.')
            return redirect('employees:position_detail', position_id=job.job_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = JobForm(instance=job)

    context = {
        'form': form,
        'job': job,
        'title': 'تعديل الوظيفة'
    }

    return render(request, 'employees/job_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_position(request, position_id):
    """حذف وظيفة"""
    job = get_object_or_404(Job, job_id=position_id)
    job_title = job.job_title

    try:
        # التحقق من وجود موظفين في الوظيفة
        if Employee.objects.filter(job=job).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exists():
            messages.error(request, f'لا يمكن حذف الوظيفة {job_title} لأنها مرتبطة بموظفين.')
        else:
            job.delete()
            messages.success(request, f'تم حذف الوظيفة {job_title} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف الوظيفة: {str(e)}')

    return redirect('employees:position_list')


@login_required
def reports(request):
    """تقارير الموظفين"""
    # إحصائيات عامة
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(emp_status='Active').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

    # إحصائيات الأقسام
    department_stats = Department.objects.annotate(
        employee_count=Count('employee')
    ).order_by('-employee_count')

    # إحصائيات الوظائف
    job_stats = Job.objects.annotate(
        employee_count=Count('employee')
    ).order_by('-employee_count')

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'department_stats': department_stats,
        'job_stats': job_stats,
    }

    return render(request, 'employees/reports.html', context)


@login_required
def export_employees(request):
    """تصدير بيانات الموظفين"""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'

    writer = csv.writer(response)
    writer.writerow(['كود الموظف', 'الاسم الأول', 'الاسم الأخير', 'القسم', 'الوظيفة', 'الحالة'])

    employees = Employee.objects.select_related('dept', 'job').all()
    for emp in employees:
        writer.writerow([
            emp.emp_code,
            emp.first_name,
            emp.last_name,
            emp.dept.dept_name if emp.dept else '',
            emp.job.job_title if emp.job else '',
            emp.emp_status
        ])

    return response


@login_required
def department_summary(request):
    """ملخص الأقسام"""
    departments = Department.objects.annotate(
        employee_count=Count('employee'),
        active_count=Count('employee', filter=Q(employee__emp_status='Active'))
    ).order_by('dept_name')

    context = {
        'departments': departments,
    }

    return render(request, 'employees/department_summary.html', context)


# AJAX Views
@login_required
def get_employee_ajax(request, emp_id):
    """جلب بيانات موظف عبر AJAX"""
    try:
        employee = Employee.objects.select_related('dept', 'job', 'branch').get(emp_id=emp_id)
        data = {
            'emp_id': employee.emp_id,
            'emp_code': employee.emp_code,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'email': employee.email,
            'mobile': employee.mobile,
            'dept_name': employee.dept.dept_name if employee.dept else '',
            'job_title': employee.job.job_title if employee.job else '',
            'emp_status': employee.emp_status,
        }
        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'الموظف غير موجود'}, status=404)


@login_required
def search_employees_ajax(request):
    """البحث في الموظفين عبر AJAX"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)

    employees = Employee.objects.filter(
        Q(first_name__icontains=query).prefetch_related()  # TODO: Add appropriate prefetch_related fields |
        Q(last_name__icontains=query) |
        Q(emp_code__icontains=query)
    ).select_related('dept', 'job')[:10]

    results = []
    for emp in employees:
        results.append({
            'emp_id': emp.emp_id,
            'emp_code': emp.emp_code,
            'name': f"{emp.first_name} {emp.last_name}",
            'dept': emp.dept.dept_name if emp.dept else '',
            'job': emp.job.job_title if emp.job else '',
        })

    return JsonResponse(results, safe=False)


@login_required
def department_employees_ajax(request, dept_id):
    """جلب موظفي قسم معين عبر AJAX"""
    employees = Employee.objects.filter(
        dept_id=dept_id,
        emp_status='Active'
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.values('emp_id', 'first_name', 'last_name', 'emp_code')

    return JsonResponse(list(employees), safe=False)


# Bulk Operations
@login_required
def bulk_import_employees(request):
    """استيراد الموظفين بالجملة"""
    if request.method == 'POST':
        # معالجة ملف الاستيراد
        pass

    return render(request, 'employees/bulk_import.html')


@login_required
def bulk_export_employees(request):
    """تصدير الموظفين بالجملة"""
    return export_employees(request)


@login_required
def bulk_update_employees(request):
    """تحديث الموظفين بالجملة"""
    if request.method == 'POST':
        # معالجة التحديث الجماعي
        pass

    return render(request, 'employees/bulk_update.html')


# Document Management
@login_required
def employee_documents(request, emp_id):
    """إدارة مستندات الموظف"""
    employee = get_object_or_404(Employee, emp_id=emp_id)
    documents = EmployeeDocument.objects.filter(emp=employee).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('-upload_date')

    context = {
        'employee': employee,
        'documents': documents,
    }

    return render(request, 'employees/employee_documents.html', context)


@login_required
def upload_document(request, emp_id):
    """رفع مستند للموظف"""
    from .forms import EmployeeDocumentForm

    employee = get_object_or_404(Employee, emp_id=emp_id)

    if request.method == 'POST':
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.emp = employee

            # معالجة الملف المرفوع
            file_upload = form.cleaned_data.get('file_upload')
            if file_upload:
                document.file_data = file_upload.read()
                document.file_ext = file_upload.name.split('.')[-1].lower()

            document.save()
            messages.success(request, 'تم رفع المستند بنجاح.')
            return redirect('employees:employee_documents', emp_id=emp_id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = EmployeeDocumentForm()

    context = {
        'form': form,
        'employee': employee,
    }

    return render(request, 'employees/upload_document.html', context)


@login_required
@require_http_methods(["POST"])
def delete_document(request, doc_id):
    """حذف مستند"""
    document = get_object_or_404(EmployeeDocument, doc_id=doc_id)
    emp_id = document.emp.emp_id

    try:
        document.delete()
        messages.success(request, 'تم حذف المستند بنجاح.')
        return JsonResponse({'success': True, 'message': 'تم حذف المستند بنجاح.'})
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف المستند: {str(e)}')
        return JsonResponse({'success': False, 'message': f'حدث خطأ أثناء حذف المستند: {str(e)}'})


@login_required
def download_document(request, doc_id):
    """تحميل مستند"""
    document = get_object_or_404(EmployeeDocument, doc_id=doc_id)

    if document.file_data:
        response = HttpResponse(document.file_data, content_type='application/octet-stream')
        filename = f"{document.doc_name or document.doc_type}.{document.file_ext or 'bin'}"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        messages.error(request, 'الملف غير موجود.')
        return redirect('employees:detail', emp_id=document.emp.emp_id)


@login_required
def preview_document(request, doc_id):
    """معاينة مستند"""
    document = get_object_or_404(EmployeeDocument, doc_id=doc_id)

    if document.file_data:
        # تحديد نوع المحتوى بناءً على امتداد الملف
        content_type = 'application/octet-stream'
        if document.file_ext:
            if document.file_ext.lower() == 'pdf':
                content_type = 'application/pdf'
            elif document.file_ext.lower() in ['jpg', 'jpeg']:
                content_type = 'image/jpeg'
            elif document.file_ext.lower() == 'png':
                content_type = 'image/png'
            elif document.file_ext.lower() == 'gif':
                content_type = 'image/gif'

        response = HttpResponse(document.file_data, content_type=content_type)
        filename = f"{document.doc_name or document.doc_type}.{document.file_ext or 'bin'}"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    else:
        messages.error(request, 'الملف غير موجود.')
        return redirect('employees:detail', emp_id=document.emp.emp_id)


@login_required
@require_http_methods(["POST"])
def ajax_upload_document(request, emp_id):
    """رفع مستند عبر AJAX"""
    import logging
    from .forms import EmployeeDocumentForm

    logger = logging.getLogger(__name__)

    try:
        employee = get_object_or_404(Employee, emp_id=emp_id)
        logger.info(f"Processing document upload for employee {emp_id}")

        if request.method == 'POST':
            logger.info(f"POST data: {request.POST}")
            logger.info(f"FILES data: {list(request.FILES.keys())}")

            form = EmployeeDocumentForm(request.POST, request.FILES)
            if form.is_valid():
                logger.info("Form is valid, processing upload")

                document = form.save(commit=False)
                document.emp = employee

                # معالجة الملف المرفوع
                file_upload = form.cleaned_data.get('file_upload')
                if file_upload:
                    logger.info(f"Processing file: {file_upload.name}, size: {file_upload.size}")

                    document.file_data = file_upload.read()
                    document.file_ext = file_upload.name.split('.')[-1].lower()

                    # حساب حجم الملف
                    file_size = len(document.file_data)
                    logger.info(f"File size after reading: {file_size} bytes")

                    # التحقق من حجم الملف (10 ميجابايت كحد أقصى)
                    if file_size > 10 * 1024 * 1024:
                        logger.warning(f"File too large: {file_size} bytes")
                        return JsonResponse({
                            'success': False,
                            'message': 'حجم الملف يجب أن يكون أقل من 10 ميجابايت.'
                        })
                else:
                    logger.warning("No file uploaded")
                    return JsonResponse({
                        'success': False,
                        'message': 'لم يتم اختيار ملف للرفع.'
                    })

                # حفظ المستند
                document.save()
                logger.info(f"Document saved successfully with ID: {document.doc_id}")

                # إرجاع بيانات المستند الجديد
                return JsonResponse({
                    'success': True,
                    'message': 'تم رفع المستند بنجاح.',
                    'document': {
                        'id': document.doc_id,
                        'type': document.doc_type,
                        'name': document.doc_name or 'غير محدد',
                        'upload_date': document.upload_date.strftime('%d/%m/%Y'),
                        'file_ext': document.file_ext,
                        'notes': document.notes or ''
                    }
                })
            else:
                logger.error(f"Form validation failed: {form.errors}")
                return JsonResponse({
                    'success': False,
                    'message': 'يرجى تصحيح الأخطاء في النموذج.',
                    'errors': form.errors
                })

        return JsonResponse({'success': False, 'message': 'طريقة الطلب غير صحيحة.'})

    except Exception as e:
        logger.error(f"Error in ajax_upload_document: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ أثناء رفع المستند: {str(e)}'
        })


# Error Handlers
def custom_404(request, exception):
    """صفحة خطأ 404 مخصصة"""
    return render(request, 'employees/errors/404.html', status=404)


def custom_500(request):
    """صفحة خطأ 500 مخصصة"""
    return render(request, 'employees/errors/500.html', status=500)


def custom_403(request, exception):
    """صفحة خطأ 403 مخصصة"""
    return render(request, 'employees/errors/403.html', status=403)
