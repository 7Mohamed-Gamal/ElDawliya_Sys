from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from Hr.models.pickup_point_models import PickupPoint
from Hr.forms.pickup_point_forms import PickupPointForm

@login_required
def pickup_point_list(request):
    """عرض قائمة نقاط التجمع"""
    pickup_points = PickupPoint.objects.all().order_by('name')
    
    context = {
        'pickup_points': pickup_points,
        'title': 'نقاط التجمع'
    }
    
    return render(request, 'Hr/pickup_points/list.html', context)

@login_required
def pickup_point_create(request):
    """إنشاء نقطة تجمع جديدة"""
    if request.method == 'POST':
        form = PickupPointForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء نقطة التجمع بنجاح')
            return redirect('Hr:pickup_points:list')
    else:
        form = PickupPointForm()
    
    context = {
        'form': form,
        'title': 'إنشاء نقطة تجمع جديدة'
    }
    
    return render(request, 'Hr/pickup_points/create.html', context)

@login_required
def pickup_point_detail(request, pk):
    """عرض تفاصيل نقطة تجمع"""
    pickup_point = get_object_or_404(PickupPoint, pk=pk)
    
    context = {
        'pickup_point': pickup_point,
        'title': f'تفاصيل نقطة التجمع: {pickup_point.name}'
    }
    
    return render(request, 'Hr/pickup_points/detail.html', context)

@login_required
def pickup_point_edit(request, pk):
    """تعديل نقطة تجمع"""
    pickup_point = get_object_or_404(PickupPoint, pk=pk)
    
    if request.method == 'POST':
        form = PickupPointForm(request.POST, instance=pickup_point)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل نقطة التجمع بنجاح')
            return redirect('Hr:pickup_points:detail', pk=pickup_point.pk)
    else:
        form = PickupPointForm(instance=pickup_point)
    
    context = {
        'form': form,
        'pickup_point': pickup_point,
        'title': f'تعديل نقطة التجمع: {pickup_point.name}'
    }
    
    return render(request, 'Hr/pickup_points/edit.html', context)

@login_required
def pickup_point_delete(request, pk):
    """حذف نقطة تجمع"""
    pickup_point = get_object_or_404(PickupPoint, pk=pk)
    
    if request.method == 'POST':
        pickup_point.delete()
        messages.success(request, 'تم حذف نقطة التجمع بنجاح')
        return redirect('Hr:pickup_points:list')
    
    context = {
        'pickup_point': pickup_point,
        'title': f'حذف نقطة التجمع: {pickup_point.name}'
    }
    
    return render(request, 'Hr/pickup_points/delete.html', context)
