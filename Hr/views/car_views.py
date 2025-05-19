from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from Hr.models.car_models import Car
from Hr.forms.employee_forms import CarForm
from administrator.decorators import django_permission_required
from Hr.decorators import hr_module_permission_required

@login_required
@django_permission_required('hr.view_car')
def car_list(request):
    """عرض قائمة السيارات"""
    cars = Car.objects.all()

    context = {
        'cars': cars,
        'title': 'قائمة السيارات'
    }

    return render(request, 'Hr/cars/car_list.html', context)

@login_required
@django_permission_required('hr.add_car')
def car_create(request):
    """إنشاء سيارة جديدة"""
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء السيارة بنجاح')
            return redirect('Hr:cars:list')
    else:
        form = CarForm()

    context = {
        'form': form,
        'title': 'إنشاء سيارة جديدة'
    }

    return render(request, 'Hr/cars/create.html', context)

@login_required
@django_permission_required('hr.view_car')
def car_detail(request, car_id):
    """عرض تفاصيل سيارة"""
    car = get_object_or_404(Car, car_id=car_id)

    # Get pickup points for this car
    pickup_points = car.pickup_points.all()

    # Get employees using this car
    employees = car.employee_set.all()

    context = {
        'car': car,
        'pickup_points': pickup_points,
        'employees': employees,
        'title': f'تفاصيل السيارة: {car.car_name or car.car_id}'
    }

    return render(request, 'Hr/cars/detail.html', context)

@login_required
@hr_module_permission_required('cars', 'edit')
def car_edit(request, car_id):
    """تعديل سيارة"""
    car = get_object_or_404(Car, car_id=car_id)

    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل السيارة بنجاح')
            return redirect('Hr:cars:detail', car_id=car.car_id)
    else:
        form = CarForm(instance=car)

    context = {
        'form': form,
        'car': car,
        'title': f'تعديل السيارة: {car.car_name or car.car_id}'
    }

    return render(request, 'Hr/cars/edit.html', context)

@login_required
@hr_module_permission_required('cars', 'delete')
def car_delete(request, car_id):
    """حذف سيارة"""
    car = get_object_or_404(Car, car_id=car_id)

    if request.method == 'POST':
        # Check if there are any employees using this car
        if car.employee_set.exists():
            messages.error(request, 'لا يمكن حذف السيارة لأنها مرتبطة بموظفين')
            return redirect('Hr:cars:detail', car_id=car.car_id)

        # Check if there are any pickup points for this car
        if car.pickup_points.exists():
            messages.error(request, 'لا يمكن حذف السيارة لأنها مرتبطة بنقاط تجمع')
            return redirect('Hr:cars:detail', car_id=car.car_id)

        car.delete()
        messages.success(request, 'تم حذف السيارة بنجاح')
        return redirect('Hr:cars:list')

    context = {
        'car': car,
        'title': f'حذف السيارة: {car.car_name or car.car_id}'
    }

    return render(request, 'Hr/cars/delete.html', context)
