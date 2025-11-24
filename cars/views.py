from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import Car, Supplier, Trip, Settings, RoutePoint
from employees.models import Employee
from .forms import CarForm, SupplierForm, TripForm, SettingsForm, RoutePointForm


@login_required
def dashboard(request):
    """لوحة تحكم السيارات"""
    today = date.today()

    # إحصائيات عامة
    total_cars = Car.objects.count()
    active_cars = Car.objects.filter(car_status='active').count()
    total_suppliers = Supplier.objects.count()
    total_trips = Trip.objects.count()

    # رحلات اليوم
    today_trips = Trip.objects.filter(date=today).count()
    today_distance = Trip.objects.filter(date=today).aggregate(
        total_distance=Sum('distance')
    )['total_distance'] or 0

    # إجمالي التكاليف الشهرية
    current_month = today.replace(day=1)
    monthly_costs = Trip.objects.filter(
        date__gte=current_month
    ).aggregate(
        total_cost=Sum('final_price'),
        total_distance=Sum('distance'),
        total_trips=Count('id')
    )

    # أكثر السيارات استخداماً
    most_used_cars = Car.objects.annotate(
        trip_count=Count('trips'),
        total_distance=Sum('trips__distance'),
        total_cost=Sum('trips__final_price')
    ).filter(trip_count__gt=0).order_by('-trip_count')[:5]

    # توزيع السيارات حسب النوع
    car_type_distribution = Car.objects.values('car_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # إحصائيات الموردين
    supplier_stats = Supplier.objects.annotate(
        car_count=Count('cars')
    ).filter(car_count__gt=0).order_by('-car_count')[:5]

    # اتجاهات التكلفة الأسبوعية
    week_ago = today - timedelta(days=7)
    weekly_costs = Trip.objects.filter(
        date__gte=week_ago
    ).values('date').annotate(
        daily_cost=Sum('final_price'),
        daily_distance=Sum('distance')
    ).order_by('date')

    context = {
        'total_cars': total_cars,
        'active_cars': active_cars,
        'total_suppliers': total_suppliers,
        'total_trips': total_trips,
        'today_trips': today_trips,
        'today_distance': today_distance,
        'monthly_costs': monthly_costs,
        'most_used_cars': most_used_cars,
        'car_type_distribution': car_type_distribution,
        'supplier_stats': supplier_stats,
        'weekly_costs': weekly_costs,
    }

    return render(request, 'cars/dashboard.html', context)


# إدارة السيارات
@login_required
def car_list(request):
    """قائمة السيارات"""
    cars = Car.objects.select_related('supplier').annotate(
        trip_count=Count('trips'),
        total_distance=Sum('trips__distance'),
        total_cost=Sum('trips__final_price')
    ).all()

    # البحث والفلترة
    search = request.GET.get('search')
    if search:
        cars = cars.filter(
            Q(car_code__icontains=search) |
            Q(car_name__icontains=search)
        )

    # فلترة حسب النوع
    car_type = request.GET.get('car_type')
    if car_type:
        cars = cars.filter(car_type=car_type)

    # فلترة حسب المورد
    supplier = request.GET.get('supplier')
    if supplier:
        cars = cars.filter(supplier_id=supplier)

    # فلترة حسب الحالة
    status = request.GET.get('status')
    if status:
        cars = cars.filter(car_status=status)

    # ترتيب النتائج
    cars = cars.order_by('car_code')

    # التقسيم إلى صفحات
    paginator = Paginator(cars, 20)
    page_number = request.GET.get('page')
    cars = paginator.get_page(page_number)

    # قوائم للفلترة
    suppliers = Supplier.objects.all().order_by('name')

    context = {
        'cars': cars,
        'suppliers': suppliers,
        'car_types': Car._meta.get_field('car_type').choices,
        'car_statuses': Car._meta.get_field('car_status').choices,
    }

    return render(request, 'cars/car_list.html', context)


@login_required
def add_car(request):
    """إضافة سيارة جديدة"""
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save()
            messages.success(request, f'تم إضافة السيارة {car.car_code} - {car.car_name} بنجاح.')
            return redirect('cars:car_detail', car_id=car.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = CarForm()

    context = {
        'form': form,
        'title': 'إضافة سيارة جديدة'
    }

    return render(request, 'cars/car_form.html', context)


@login_required
def car_detail(request, car_id):
    """تفاصيل السيارة"""
    car = get_object_or_404(Car, id=car_id)

    # رحلات السيارة الأخيرة
    recent_trips = Trip.objects.filter(car=car).order_by('-date')[:10]

    # إحصائيات السيارة
    car_stats = Trip.objects.filter(car=car).aggregate(
        total_trips=Count('id'),
        total_distance=Sum('distance'),
        total_cost=Sum('final_price'),
        avg_cost_per_km=Avg('final_price') / Avg('distance') if Trip.objects.filter(car=car).exists() else 0
    )

    # نقاط خط السير
    route_points = RoutePoint.objects.filter(car=car).order_by('order')

    # إحصائيات شهرية
    today = date.today()
    current_month = today.replace(day=1)
    monthly_stats = Trip.objects.filter(
        car=car,
        date__gte=current_month
    ).aggregate(
        monthly_trips=Count('id'),
        monthly_distance=Sum('distance'),
        monthly_cost=Sum('final_price')
    )

    context = {
        'car': car,
        'recent_trips': recent_trips,
        'car_stats': car_stats,
        'route_points': route_points,
        'monthly_stats': monthly_stats,
    }

    return render(request, 'cars/car_detail.html', context)


@login_required
def edit_car(request, car_id):
    """تعديل السيارة"""
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            car = form.save()
            messages.success(request, f'تم تحديث السيارة {car.car_code} - {car.car_name} بنجاح.')
            return redirect('cars:car_detail', car_id=car.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = CarForm(instance=car)

    context = {
        'form': form,
        'car': car,
        'title': 'تعديل السيارة'
    }

    return render(request, 'cars/car_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_car(request, car_id):
    """حذف السيارة"""
    car = get_object_or_404(Car, id=car_id)

    try:
        # التحقق من وجود رحلات مرتبطة
        if Trip.objects.filter(car=car).exists():
            messages.error(request, f'لا يمكن حذف السيارة {car.car_code} لأنها مرتبطة برحلات.')
        else:
            car_name = f"{car.car_code} - {car.car_name}"
            car.delete()
            messages.success(request, f'تم حذف السيارة {car_name} بنجاح.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف السيارة: {str(e)}')

    return redirect('cars:car_list')


# إدارة الموردين
@login_required
def supplier_list(request):
    """قائمة الموردين"""
    suppliers = Supplier.objects.annotate(
        car_count=Count('cars')
    ).order_by('name')

    # البحث
    search = request.GET.get('search')
    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )

    context = {
        'suppliers': suppliers,
    }

    return render(request, 'cars/supplier_list.html', context)


@login_required
def add_supplier(request):
    """إضافة مورد جديد"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'تم إضافة المورد {supplier.name} بنجاح.')
            return redirect('cars:supplier_detail', supplier_id=supplier.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = SupplierForm()

    context = {
        'form': form,
        'title': 'إضافة مورد جديد'
    }

    return render(request, 'cars/supplier_form.html', context)


@login_required
def supplier_detail(request, supplier_id):
    """تفاصيل المورد"""
    supplier = get_object_or_404(Supplier, id=supplier_id)

    # سيارات المورد
    cars = Car.objects.filter(supplier=supplier).annotate(
        trip_count=Count('trips'),
        total_distance=Sum('trips__distance')
    ).order_by('car_code')

    context = {
        'supplier': supplier,
        'cars': cars,
    }

    return render(request, 'cars/supplier_detail.html', context)


@login_required
def edit_supplier(request, supplier_id):
    """تعديل المورد"""
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات المورد بنجاح.')
            return redirect('cars:supplier_detail', supplier_id=supplier.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = SupplierForm(instance=supplier)

    context = {
        'form': form,
        'supplier': supplier,
        'title': 'تعديل المورد'
    }

    return render(request, 'cars/supplier_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_supplier(request, supplier_id):
    """حذف المورد"""
    supplier = get_object_or_404(Supplier, id=supplier_id)

    # التحقق من وجود سيارات مرتبطة
    if Car.objects.filter(supplier=supplier).exists():
        messages.error(request, 'لا يمكن حذف المورد لوجود سيارات مرتبطة به.')
        return redirect('cars:supplier_detail', supplier_id=supplier.id)

    supplier_name = supplier.name
    supplier.delete()
    messages.success(request, f'تم حذف المورد "{supplier_name}" بنجاح.')
    return redirect('cars:supplier_list')


# إدارة الرحلات
@login_required
def trip_list(request):
    """قائمة الرحلات"""
    trips = Trip.objects.select_related('car').all()

    # البحث والفلترة
    search = request.GET.get('search')
    if search:
        trips = trips.filter(
            Q(car__car_code__icontains=search) |
            Q(car__car_name__icontains=search)
        )

    # فلترة حسب السيارة
    car = request.GET.get('car')
    if car:
        trips = trips.filter(car_id=car)

    # فلترة حسب التاريخ
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        trips = trips.filter(date__gte=date_from)
    if date_to:
        trips = trips.filter(date__lte=date_to)

    # ترتيب النتائج
    trips = trips.order_by('-date', 'car__car_code')

    # التقسيم إلى صفحات
    paginator = Paginator(trips, 20)
    page_number = request.GET.get('page')
    trips = paginator.get_page(page_number)

    # قوائم للفلترة
    cars = Car.objects.filter(car_status='active').order_by('car_code')

    context = {
        'trips': trips,
        'cars': cars,
    }

    return render(request, 'cars/trip_list.html', context)


@login_required
def add_trip(request):
    """إضافة رحلة جديدة"""
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save()
            messages.success(request, f'تم إضافة الرحلة للسيارة {trip.car.car_code} بنجاح.')
            return redirect('cars:trip_detail', trip_id=trip.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = TripForm()

    context = {
        'form': form,
        'title': 'إضافة رحلة جديدة'
    }

    return render(request, 'cars/trip_form.html', context)


@login_required
def trip_detail(request, trip_id):
    """تفاصيل الرحلة"""
    trip = get_object_or_404(Trip, id=trip_id)

    context = {
        'trip': trip,
    }

    return render(request, 'cars/trip_detail.html', context)


@login_required
def edit_trip(request, trip_id):
    """تعديل الرحلة"""
    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات الرحلة بنجاح.')
            return redirect('cars:trip_detail', trip_id=trip.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = TripForm(instance=trip)

    context = {
        'form': form,
        'trip': trip,
        'title': 'تعديل الرحلة'
    }

    return render(request, 'cars/trip_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_trip(request, trip_id):
    """حذف الرحلة"""
    trip = get_object_or_404(Trip, id=trip_id)

    trip_info = f"رحلة السيارة {trip.car.car_code} بتاريخ {trip.date}"
    trip.delete()
    messages.success(request, f'تم حذف {trip_info} بنجاح.')
    return redirect('cars:trip_list')


# إدارة الإعدادات
@login_required
def settings_view(request):
    """إعدادات النظام"""
    settings_obj = Settings.objects.first()

    if request.method == 'POST':
        if settings_obj:
            form = SettingsForm(request.POST, instance=settings_obj)
        else:
            form = SettingsForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الإعدادات بنجاح.')
            return redirect('cars:settings')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        if settings_obj:
            form = SettingsForm(instance=settings_obj)
        else:
            form = SettingsForm()

    context = {
        'form': form,
        'settings_obj': settings_obj,
    }

    return render(request, 'cars/settings.html', context)


# التقارير
@login_required
def reports(request):
    """تقارير السيارات"""
    today = date.today()

    # إحصائيات عامة
    total_cars = Car.objects.count()
    total_trips = Trip.objects.count()
    total_distance = Trip.objects.aggregate(Sum('distance'))['distance__sum'] or 0
    total_cost = Trip.objects.aggregate(Sum('final_price'))['final_price__sum'] or 0

    # إحصائيات شهرية
    current_month = today.replace(day=1)
    monthly_stats = Trip.objects.filter(
        date__gte=current_month
    ).aggregate(
        monthly_trips=Count('id'),
        monthly_distance=Sum('distance'),
        monthly_cost=Sum('final_price')
    )

    # أكثر السيارات استخداماً
    most_used_cars = Car.objects.annotate(
        trip_count=Count('trips'),
        total_distance=Sum('trips__distance'),
        total_cost=Sum('trips__final_price')
    ).filter(trip_count__gt=0).order_by('-trip_count')[:10]

    # اتجاهات التكلفة الشهرية
    monthly_trends = Trip.objects.extra(
        select={'month': "MONTH(date)", 'year': "YEAR(date)"}
    ).values('month', 'year').annotate(
        total_cost=Sum('final_price'),
        total_distance=Sum('distance'),
        trip_count=Count('id')
    ).order_by('year', 'month')[-12:]

    context = {
        'total_cars': total_cars,
        'total_trips': total_trips,
        'total_distance': total_distance,
        'total_cost': total_cost,
        'monthly_stats': monthly_stats,
        'most_used_cars': most_used_cars,
        'monthly_trends': monthly_trends,
    }

    return render(request, 'cars/reports.html', context)


@login_required
def export_trips(request):
    """تصدير بيانات الرحلات"""
    import csv

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="trips.csv"'

    writer = csv.writer(response)
    writer.writerow(['التاريخ', 'السيارة', 'المسافة', 'تكلفة الوقود', 'تكلفة الصيانة', 'الإهلاك', 'الرخصة', 'ربح السائق', 'الضريبة', 'التكلفة النهائية'])

    trips = Trip.objects.select_related('car').all()
    for trip in trips:
        writer.writerow([
            trip.date,
            f"{trip.car.car_code} - {trip.car.car_name}",
            trip.distance,
            trip.fuel_cost or 0,
            trip.maintenance_cost or 0,
            trip.depreciation_cost or 0,
            trip.license_cost or 0,
            trip.driver_profit or 0,
            trip.tax_amount or 0,
            trip.final_price or 0
        ])

    return response


# AJAX Views
@login_required
def calculate_trip_cost(request):
    """حساب تكلفة الرحلة عبر AJAX"""
    car_id = request.GET.get('car_id')
    distance = request.GET.get('distance')

    if not car_id or not distance:
        return JsonResponse({'error': 'بيانات ناقصة'}, status=400)

    try:
        car = Car.objects.get(id=car_id)
        distance = float(distance)
        settings_obj = Settings.objects.first()

        if not settings_obj:
            return JsonResponse({'error': 'لم يتم تحديد إعدادات النظام'}, status=400)

        # تحديد سعر الوقود
        if car.fuel_type == 'diesel':
            fuel_price = settings_obj.diesel_price
        elif car.fuel_type == 'gasoline':
            fuel_price = settings_obj.gasoline_price
        else:  # gas
            fuel_price = settings_obj.gas_price

        # حساب التكاليف
        fuel_cost = distance * car.fuel_consumption_rate * fuel_price
        maintenance_cost = distance * settings_obj.maintenance_rate
        depreciation_cost = distance * settings_obj.depreciation_rate
        license_cost = distance * settings_obj.license_rate
        driver_profit = distance * settings_obj.driver_profit_rate

        total_base_cost = fuel_cost + maintenance_cost + depreciation_cost + license_cost + driver_profit
        tax_amount = total_base_cost * (settings_obj.tax_rate / 100)
        final_price = total_base_cost + tax_amount

        data = {
            'fuel_cost': round(fuel_cost, 2),
            'maintenance_cost': round(maintenance_cost, 2),
            'depreciation_cost': round(depreciation_cost, 2),
            'license_cost': round(license_cost, 2),
            'driver_profit': round(driver_profit, 2),
            'total_base_cost': round(total_base_cost, 2),
            'tax_amount': round(tax_amount, 2),
            'final_price': round(final_price, 2)
        }

        return JsonResponse(data)
    except (Car.DoesNotExist, ValueError):
        return JsonResponse({'error': 'بيانات غير صحيحة'}, status=400)


# Analytics
@login_required
def car_analytics(request):
    """تحليلات السيارات"""
    # توزيع السيارات حسب النوع
    car_type_distribution = Car.objects.values('car_type').annotate(
        count=Count('id'),
        total_distance=Sum('trips__distance'),
        total_cost=Sum('trips__final_price')
    ).order_by('-count')

    # كفاءة استهلاك الوقود
    fuel_efficiency = Car.objects.annotate(
        total_distance=Sum('trips__distance'),
        total_fuel_cost=Sum('trips__fuel_cost')
    ).filter(total_distance__gt=0).order_by('fuel_consumption_rate')

    # اتجاهات الاستخدام الشهرية
    monthly_usage = Trip.objects.extra(
        select={'month': "MONTH(date)", 'year': "YEAR(date)"}
    ).values('month', 'year').annotate(
        total_trips=Count('id'),
        total_distance=Sum('distance'),
        avg_cost_per_km=Sum('final_price') / Sum('distance')
    ).order_by('year', 'month')[-12:]

    context = {
        'car_type_distribution': car_type_distribution,
        'fuel_efficiency': fuel_efficiency,
        'monthly_usage': monthly_usage,
    }

    return render(request, 'cars/car_analytics.html', context)
