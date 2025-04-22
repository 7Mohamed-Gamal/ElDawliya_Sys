from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse

from Hr.models.file_models import EmployeeFile
from Hr.forms.file_forms import EmployeeFileForm

@login_required
def employee_file_list(request):
    """عرض قائمة ملفات الموظفين"""
    # Filter files based on query parameters
    employee_id = request.GET.get('employee')
    file_type = request.GET.get('file_type')
    
    files = EmployeeFile.objects.all()
    
    if employee_id:
        files = files.filter(employee_id=employee_id)
    
    if file_type:
        files = files.filter(file_type=file_type)
    
    # Default ordering
    files = files.order_by('-created_at')
    
    context = {
        'files': files,
        'title': 'ملفات الموظفين'
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
