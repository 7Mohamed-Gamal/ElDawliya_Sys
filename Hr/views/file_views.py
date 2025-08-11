from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse

from Hr.models.legacy.legacy_models import EmployeeFile
from Hr.models.legacy_employee import LegacyEmployee
from Hr.forms.file_forms import EmployeeFileForm

@login_required
def employee_file_list(request):
    """عرض قائمة ملفات الموظفين مع تصفية متقدمة وترقيم صفحات"""
    from django.core.paginator import Paginator
    from django.utils.dateparse import parse_date
    from django.db.models import Q

    # Query params
    employee_id = request.GET.get('employee')
    file_type = request.GET.get('file_type')
    q = request.GET.get('q', '').strip()
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    order = request.GET.get('order', 'newest')

    files_qs = EmployeeFile.objects.select_related('employee').all()

    if employee_id:
        files_qs = files_qs.filter(employee_id=employee_id)

    if file_type:
        files_qs = files_qs.filter(file_type=file_type)

    if q:
        files_qs = files_qs.filter(
            Q(title__icontains=q) |
            Q(employee__emp_full_name__icontains=q) |
            Q(employee__emp_id__icontains=q)
        )

    # Date range filtering
    if date_from:
        df = parse_date(date_from)
        if df:
            files_qs = files_qs.filter(created_at__date__gte=df)
    if date_to:
        dt = parse_date(date_to)
        if dt:
            files_qs = files_qs.filter(created_at__date__lte=dt)

    # Ordering
    if order == 'oldest':
        files_qs = files_qs.order_by('created_at')
    else:
        files_qs = files_qs.order_by('-created_at')

    # Pagination
    paginator = Paginator(files_qs, 20)
    page_number = request.GET.get('page')
    files_page = paginator.get_page(page_number)

    # Determine if we should offer a Select2 dropdown for employees
    employees_for_filter = None
    try:
        total_employees = LegacyEmployee.objects.count()
        if total_employees and total_employees <= 200:  # threshold
            employees_for_filter = LegacyEmployee.objects.only('emp_id', 'emp_full_name').order_by('emp_full_name')
    except Exception:
        employees_for_filter = None

    context = {
        'files': files_page,  # keep name for template compatibility
        'page_obj': files_page,
        'paginator': paginator,
        'title': 'ملفات الموظفين',
        'employees_for_filter': employees_for_filter,
    }

    return render(request, 'Hr/files/list.html', context)

@login_required
def employee_file_create(request):
    """إنشاء ملف جديد للموظف"""
    if request.method == 'POST':
        form = EmployeeFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.uploaded_by = request.user
            file.save()
            messages.success(request, 'تم رفع الملف بنجاح')
            return redirect('Hr:files:list')
    else:
        # Pre-fill employee if provided in query string
        employee_id = request.GET.get('employee')
        initial_data = {}
        if employee_id:
            initial_data['employee'] = employee_id
        
        form = EmployeeFileForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'رفع ملف جديد'
    }
    
    return render(request, 'Hr/files/create.html', context)

@login_required
def employee_file_detail(request, pk):
    """عرض تفاصيل ملف"""
    file = get_object_or_404(EmployeeFile, pk=pk)
    
    context = {
        'file': file,
        'title': f'تفاصيل الملف: {file.title}'
    }
    
    return render(request, 'Hr/files/detail.html', context)

@login_required
def employee_file_edit(request, pk):
    """تعديل ملف"""
    file = get_object_or_404(EmployeeFile, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeFileForm(request.POST, request.FILES, instance=file)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الملف بنجاح')
            return redirect('Hr:files:detail', pk=file.pk)
    else:
        form = EmployeeFileForm(instance=file)
    
    context = {
        'form': form,
        'file': file,
        'title': f'تعديل الملف: {file.title}'
    }
    
    return render(request, 'Hr/files/edit.html', context)

@login_required
def employee_file_delete(request, pk):
    """حذف ملف"""
    file = get_object_or_404(EmployeeFile, pk=pk)
    
    if request.method == 'POST':
        file.delete()
        messages.success(request, 'تم حذف الملف بنجاح')
        return redirect('Hr:files:list')
    
    context = {
        'file': file,
        'title': f'حذف الملف: {file.title}'
    }
    
    return render(request, 'Hr/files/delete.html', context)

@login_required
def employee_file_download(request, pk):
    """تنزيل ملف"""
    file = get_object_or_404(EmployeeFile, pk=pk)
    
    # Open the file in binary mode
    response = FileResponse(file.file.open('rb'))
    
    # Set the Content-Disposition header to force download
    response['Content-Disposition'] = f'attachment; filename="{file.file.name.split("/")[-1]}"'
    
    return response
