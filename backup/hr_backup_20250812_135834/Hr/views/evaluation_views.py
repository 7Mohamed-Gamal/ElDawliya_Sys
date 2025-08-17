from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from Hr.models.evaluation_models import EmployeeEvaluation
from Hr.forms.evaluation_forms import EmployeeEvaluationForm

@login_required
def employee_evaluation_list(request):
    """عرض قائمة تقييمات الموظفين"""
    # Filter evaluations based on query parameters
    employee_id = request.GET.get('employee')
    evaluator_id = request.GET.get('evaluator')
    year = request.GET.get('year')
    
    evaluations = EmployeeEvaluation.objects.all()
    
    if employee_id:
        evaluations = evaluations.filter(employee_id=employee_id)
    
    if evaluator_id:
        evaluations = evaluations.filter(evaluator_id=evaluator_id)
    
    if year:
        evaluations = evaluations.filter(evaluation_date__year=year)
    
    # Default ordering
    evaluations = evaluations.order_by('-evaluation_date')
    
    # Get unique years for filtering
    years = EmployeeEvaluation.objects.dates('evaluation_date', 'year')
    years = [date.year for date in years]
    
    context = {
        'evaluations': evaluations,
        'years': years,
        'title': 'تقييمات الموظفين'
    }
    
    return render(request, 'Hr/evaluations/list.html', context)

@login_required
def employee_evaluation_create(request):
    """إنشاء تقييم جديد للموظف"""
    if request.method == 'POST':
        form = EmployeeEvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = request.user
            evaluation.save()
            messages.success(request, 'تم إنشاء التقييم بنجاح')
            return redirect('Hr:evaluations:list')
    else:
        # Pre-fill employee if provided in query string
        employee_id = request.GET.get('employee')
        initial_data = {
            'evaluation_date': timezone.now().date(),
        }
        
        if employee_id:
            initial_data['employee'] = employee_id
        
        form = EmployeeEvaluationForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'إنشاء تقييم جديد'
    }
    
    return render(request, 'Hr/evaluations/create.html', context)

@login_required
def employee_evaluation_detail(request, pk):
    """عرض تفاصيل تقييم"""
    evaluation = get_object_or_404(EmployeeEvaluation, pk=pk)
    
    context = {
        'evaluation': evaluation,
        'title': f'تفاصيل التقييم: {evaluation.employee} - {evaluation.evaluation_date}'
    }
    
    return render(request, 'Hr/evaluations/detail.html', context)

@login_required
def employee_evaluation_edit(request, pk):
    """تعديل تقييم"""
    evaluation = get_object_or_404(EmployeeEvaluation, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل التقييم بنجاح')
            return redirect('Hr:evaluations:detail', pk=evaluation.pk)
    else:
        form = EmployeeEvaluationForm(instance=evaluation)
    
    context = {
        'form': form,
        'evaluation': evaluation,
        'title': f'تعديل التقييم: {evaluation.employee} - {evaluation.evaluation_date}'
    }
    
    return render(request, 'Hr/evaluations/edit.html', context)

@login_required
def employee_evaluation_delete(request, pk):
    """حذف تقييم"""
    evaluation = get_object_or_404(EmployeeEvaluation, pk=pk)
    
    if request.method == 'POST':
        evaluation.delete()
        messages.success(request, 'تم حذف التقييم بنجاح')
        return redirect('Hr:evaluations:list')
    
    context = {
        'evaluation': evaluation,
        'title': f'حذف التقييم: {evaluation.employee} - {evaluation.evaluation_date}'
    }
    
    return render(request, 'Hr/evaluations/delete.html', context)

@login_required
def employee_evaluation_acknowledge(request, pk):
    """اطلاع الموظف على التقييم"""
    evaluation = get_object_or_404(EmployeeEvaluation, pk=pk)
    
    if evaluation.is_acknowledged:
        messages.error(request, 'تم الاطلاع على التقييم مسبقاً')
        return redirect('Hr:evaluations:detail', pk=evaluation.pk)
    
    if request.method == 'POST':
        comments = request.POST.get('employee_comments')
        
        evaluation.is_acknowledged = True
        evaluation.acknowledgement_date = timezone.now()
        evaluation.employee_comments = comments
        evaluation.save()
        
        messages.success(request, 'تم تسجيل اطلاعك على التقييم بنجاح')
        return redirect('Hr:evaluations:detail', pk=evaluation.pk)
    
    context = {
        'evaluation': evaluation,
        'title': f'اطلاع على التقييم: {evaluation.employee} - {evaluation.evaluation_date}'
    }
    
    return render(request, 'Hr/evaluations/acknowledge.html', context)
