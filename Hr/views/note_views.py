from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from Hr.models.note_models import EmployeeNote
from Hr.forms.note_forms import EmployeeNoteForm

@login_required
def employee_note_list(request):
    """عرض قائمة ملاحظات الموظفين"""
    # Filter notes based on query parameters
    employee_id = request.GET.get('employee')
    important_only = request.GET.get('important') == 'true'
    
    notes = EmployeeNote.objects.all()
    
    if employee_id:
        notes = notes.filter(employee_id=employee_id)
    
    if important_only:
        notes = notes.filter(is_important=True)
    
    # Default ordering
    notes = notes.order_by('-created_at')
    
    context = {
        'notes': notes,
        'title': 'ملاحظات الموظفين'
    }
    
    return render(request, 'Hr/notes/list.html', context)

@login_required
def employee_note_create(request):
    """إنشاء ملاحظة جديدة للموظف"""
    if request.method == 'POST':
        form = EmployeeNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.created_by = request.user
            note.save()
            messages.success(request, 'تم إنشاء الملاحظة بنجاح')
            return redirect('Hr:notes:list')
    else:
        # Pre-fill employee if provided in query string
        employee_id = request.GET.get('employee')
        initial_data = {}
        if employee_id:
            initial_data['employee'] = employee_id
        
        form = EmployeeNoteForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'إنشاء ملاحظة جديدة'
    }
    
    return render(request, 'Hr/notes/create.html', context)

@login_required
def employee_note_detail(request, pk):
    """عرض تفاصيل ملاحظة"""
    note = get_object_or_404(EmployeeNote, pk=pk)
    
    context = {
        'note': note,
        'title': f'تفاصيل الملاحظة: {note.title}'
    }
    
    return render(request, 'Hr/notes/detail.html', context)

@login_required
def employee_note_edit(request, pk):
    """تعديل ملاحظة"""
    note = get_object_or_404(EmployeeNote, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الملاحظة بنجاح')
            return redirect('Hr:notes:detail', pk=note.pk)
    else:
        form = EmployeeNoteForm(instance=note)
    
    context = {
        'form': form,
        'note': note,
        'title': f'تعديل الملاحظة: {note.title}'
    }
    
    return render(request, 'Hr/notes/edit.html', context)

@login_required
def employee_note_delete(request, pk):
    """حذف ملاحظة"""
    note = get_object_or_404(EmployeeNote, pk=pk)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'تم حذف الملاحظة بنجاح')
        return redirect('Hr:notes:list')
    
    context = {
        'note': note,
        'title': f'حذف الملاحظة: {note.title}'
    }
    
    return render(request, 'Hr/notes/delete.html', context)
