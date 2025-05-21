from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.http import JsonResponse

# Updated import to use HR's Employee model
from Hr.models.employee_model import Employee
from .models import Car, Trip, Settings, Supplier, RoutePoint
from .forms import CarForm, TripForm, SettingsForm, SupplierForm, RoutePointForm


def home(request):
    """Home view showing the main dashboard"""
    # Check if settings exist, if not create default
    if not Settings.objects.exists():
        Settings.objects.create()
    
    # Get active cars count
    active_cars = Car.objects.filter(car_status='active').count()
    
    # Get total trips
    total_trips = Trip.objects.count()
    
    # Get total distance traveled
    total_distance = Trip.objects.aggregate(total=Sum('distance'))['total'] or 0
    
    # Get total amount
    total_amount = Trip.objects.aggregate(total=Sum('final_price'))['total'] or 0
    
    # Get suppliers count
    suppliers_count = Supplier.objects.count()
    
    context = {
        'active_cars': active_cars,
        'total_trips': total_trips,
        'total_distance': total_distance,
        'total_amount': total_amount,
        'suppliers_count': suppliers_count,
    }
    
    return render(request, 'cars/home.html', context)


def car_list(request):
    """View for listing all cars"""
    cars = Car.objects.all()
    
    # Calculate statistics for the dashboard
    active_cars_count = Car.objects.filter(car_status='active').count()
    diesel_cars_count = Car.objects.filter(fuel_type='diesel').count()
    non_diesel_cars_count = Car.objects.exclude(fuel_type='diesel').count()
    
    context = {
        'cars': cars,
        'active_cars_count': active_cars_count,
        'diesel_cars_count': diesel_cars_count,
        'non_diesel_cars_count': non_diesel_cars_count,
    }
    
    return render(request, 'cars/car_list.html', context)


def car_add(request):
    """View for adding a new car"""
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car added successfully!')
            return redirect('cars:car_list')
    else:
        form = CarForm()
    
    context = {
        'form': form,
        'title': 'Add a New Car'
    }
    
    return render(request, 'cars/car_form.html', context)


def car_edit(request, car_id):
    """View for editing an existing car"""
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car updated successfully!')
            return redirect('cars:car_list')
    else:
        form = CarForm(instance=car)
    
    context = {
        'form': form,
        'title': 'Edit Car'
    }
    
    return render(request, 'cars/car_form.html', context)


def car_delete(request, car_id):
    """View for deleting a car"""
    car = get_object_or_404(Car, id=car_id)
    
    # Check if car can be deleted (has no trips)
    if Trip.objects.filter(car=car).exists():
        messages.error(request, 'Cannot delete car with existing trips!')
        return redirect('cars:car_list')
    
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Car deleted successfully!')
        return redirect('cars:car_list')
    
    context = {
        'car': car
    }
    
    return render(request, 'cars/car_confirm_delete.html', context)


def supplier_list(request):
    """View for listing all suppliers"""
    suppliers = Supplier.objects.all()
    
    # Count cars for each supplier
    suppliers_with_counts = []
    for supplier in suppliers:
        supplier_data = {
            'supplier': supplier,
            'cars_count': Car.objects.filter(supplier=supplier).count()
        }
        suppliers_with_counts.append(supplier_data)
    
    context = {
        'suppliers': suppliers_with_counts,
    }
    
    return render(request, 'cars/supplier_list.html', context)


def supplier_add(request):
    """View for adding a new supplier"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('cars:supplier_list')
    else:
        form = SupplierForm()
    
    context = {
        'form': form,
        'title': 'Add a New Supplier'
    }
    
    return render(request, 'cars/supplier_form.html', context)


def supplier_edit(request, supplier_id):
    """View for editing an existing supplier"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('cars:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    context = {
        'form': form,
        'title': 'Edit Supplier'
    }
    
    return render(request, 'cars/supplier_form.html', context)


def supplier_delete(request, supplier_id):
    """View for deleting a supplier"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    # Check if supplier can be deleted (has no cars)
    if Car.objects.filter(supplier=supplier).exists():
        messages.error(request, 'Cannot delete supplier with associated cars!')
        return redirect('cars:supplier_list')
    
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully!')
        return redirect('cars:supplier_list')
    
    context = {
        'supplier': supplier
    }
    
    return render(request, 'cars/supplier_confirm_delete.html', context)


def average_price_calculation(request):
    """View for calculating the average price"""
    # Get all active cars
    active_cars = Car.objects.filter(car_status='active')
    
    # Get the latest settings
    settings = Settings.objects.latest('id') if Settings.objects.exists() else Settings.objects.create()
    
    # Calculate average price for each car
    cars_with_calculations = []
    
    for car in active_cars:
        # Determine fuel price based on car's fuel type
        fuel_price = 0
        if car.fuel_type == 'diesel':
            fuel_price = settings.diesel_price
        elif car.fuel_type == 'gasoline':
            fuel_price = settings.gasoline_price
        else:  # gas
            fuel_price = settings.gas_price
        
        # Calculate costs for a standard 100km trip
        standard_distance = 100
        fuel_cost = standard_distance * car.fuel_consumption_rate * fuel_price
        maintenance_cost = standard_distance * settings.maintenance_rate
        depreciation_cost = standard_distance * settings.depreciation_rate
        license_cost = standard_distance * settings.license_rate
        driver_profit = standard_distance * settings.driver_profit_rate
        
        total_base_cost = fuel_cost + maintenance_cost + depreciation_cost + license_cost + driver_profit
        tax_amount = total_base_cost * (settings.tax_rate / 100)
        final_price = total_base_cost + tax_amount
        
        # Calculate the average price per km
        average_price = final_price / standard_distance
        
        car_data = {
            'car': car,
            'fuel_price': fuel_price,
            'fuel_cost': fuel_cost,
            'maintenance_cost': maintenance_cost,
            'depreciation_cost': depreciation_cost,
            'license_cost': license_cost,
            'driver_profit': driver_profit,
            'total_base_cost': total_base_cost,
            'tax_amount': tax_amount,
            'final_price': final_price,
            'average_price': average_price
        }
        
        cars_with_calculations.append(car_data)
    
    # Sort by average price (most economical first)
    cars_with_calculations.sort(key=lambda x: x['average_price'])
    
    context = {
        'cars': cars_with_calculations,
        'settings': settings
    }
    
    return render(request, 'cars/average_price.html', context)


def trip_list(request):
    """View for listing all trips"""
    trips = Trip.objects.all()
    
    context = {
        'trips': trips,
    }
    
    return render(request, 'cars/trip_list.html', context)


def trip_add(request):
    """View for adding a new trip"""
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save()
            messages.success(request, 'Trip added successfully!')
            return redirect('cars:trip_list')
    else:
        form = TripForm()
    
    context = {
        'form': form,
        'title': 'Add a New Trip'
    }
    
    return render(request, 'cars/trip_form.html', context)


def trip_edit(request, trip_id):
    """View for editing an existing trip"""
    trip = get_object_or_404(Trip, id=trip_id)
    
    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            trip = form.save()
            trip.calculate_costs()  # Recalculate costs
            messages.success(request, 'Trip updated successfully!')
            return redirect('cars:trip_list')
    else:
        form = TripForm(instance=trip)
    
    context = {
        'form': form,
        'title': 'Edit Trip'
    }
    
    return render(request, 'cars/trip_form.html', context)


def trip_delete(request, trip_id):
    """View for deleting a trip"""
    trip = get_object_or_404(Trip, id=trip_id)
    
    if request.method == 'POST':
        # Update car's distance traveled
        trip.car.distance_traveled -= trip.distance
        trip.car.save()
        
        trip.delete()
        messages.success(request, 'Trip deleted successfully!')
        return redirect('cars:trip_list')
    
    context = {
        'trip': trip
    }
    
    return render(request, 'cars/trip_confirm_delete.html', context)


def settings_edit(request):
    """View for editing system settings"""
    # Get or create settings
    settings = Settings.objects.latest('id') if Settings.objects.exists() else Settings.objects.create()
    
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('cars:settings_edit')
    else:
        form = SettingsForm(instance=settings)
    
    context = {
        'form': form,
    }
    
    return render(request, 'cars/settings_form.html', context)


def reports(request):
    """View for generating reports"""
    # Car report
    car_report = Car.objects.annotate(
        trips_count=Count('trips'),
        total_distance=Sum('trips__distance'),
        total_amount=Sum('trips__final_price')
    )
    
    # Car type report
    car_type_report = Car.objects.values('car_type').annotate(
        cars_count=Count('id'),
        trips_count=Count('trips'),
        total_distance=Sum('trips__distance'),
        total_amount=Sum('trips__final_price')
    )
    
    # Financial summary
    total_distance = Trip.objects.aggregate(total=Sum('distance'))['total'] or 0
    total_amount = Trip.objects.aggregate(total=Sum('final_price'))['total'] or 0
    total_fuel = Trip.objects.aggregate(total=Sum('fuel_cost'))['total'] or 0
    total_profit = Trip.objects.aggregate(total=Sum('driver_profit'))['total'] or 0
    
    context = {
        'car_report': car_report,
        'car_type_report': car_type_report,
        'total_distance': total_distance,
        'total_amount': total_amount,
        'total_fuel': total_fuel,
        'total_profit': total_profit,
    }
    
    return render(request, 'cars/reports.html', context)


# Employee Views
def employee_list(request):
    """View for listing all employees"""
    employees = Employee.objects.all()
    
    context = {
        'employees': employees,
    }
    
    return render(request, 'cars/employee_list.html', context)


def employee_add(request):
    """View for adding a new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('cars:employee_list')
    else:
        form = EmployeeForm()
    
    context = {
        'form': form,
        'title': 'Add a New Employee'
    }
    
    return render(request, 'cars/employee_form.html', context)


def employee_edit(request, employee_id):
    """View for editing an existing employee"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('cars:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'form': form,
        'title': 'Edit Employee'
    }
    
    return render(request, 'cars/employee_form.html', context)


def employee_delete(request, employee_id):
    """View for deleting an employee"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Check if employee can be deleted (not assigned to any route points)
    if employee.routepoint_set.exists():
        messages.error(request, 'Cannot delete employee assigned to route points!')
        return redirect('cars:employee_list')
    
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('cars:employee_list')
    
    context = {
        'employee': employee
    }
    
    return render(request, 'cars/employee_confirm_delete.html', context)


# Route Point Views
def route_point_list(request, car_id):
    """View for listing all route points for a car"""
    car = get_object_or_404(Car, id=car_id)
    route_points = RoutePoint.objects.filter(car=car).order_by('order')
    
    context = {
        'car': car,
        'route_points': route_points,
    }
    
    return render(request, 'cars/route_point_list.html', context)


def route_point_add(request, car_id):
    """View for adding a new route point to a car"""
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        form = RoutePointForm(request.POST)
        if form.is_valid():
            route_point = form.save(commit=False)
            route_point.car = car
            
            # Get the highest order value for this car and add 1
            highest_order = RoutePoint.objects.filter(car=car).order_by('-order').values_list('order', flat=True).first()
            route_point.order = 1 if highest_order is None else highest_order + 1
            
            route_point.save()
            # Save many-to-many relationships
            form.save_m2m()
            messages.success(request, 'Route point added successfully!')
            return redirect('cars:route_point_list', car_id=car.id)
    else:
        form = RoutePointForm()
    
    context = {
        'form': form,
        'car': car,
        'title': 'Add a New Route Point'
    }
    
    return render(request, 'cars/route_point_form.html', context)


def route_point_edit(request, point_id):
    """View for editing an existing route point"""
    route_point = get_object_or_404(RoutePoint, id=point_id)
    car = route_point.car
    original_order = route_point.order
    
    if request.method == 'POST':
        form = RoutePointForm(request.POST, instance=route_point)
        if form.is_valid():
            updated_point = form.save(commit=False)
            # Keep the original order value
            updated_point.order = original_order
            updated_point.save()
            form.save_m2m()
            messages.success(request, 'Route point updated successfully!')
            return redirect('cars:route_point_list', car_id=car.id)
    else:
        form = RoutePointForm(instance=route_point)
    
    context = {
        'form': form,
        'car': car,
        'route_point': route_point,
        'title': 'Edit Route Point'
    }
    
    return render(request, 'cars/route_point_form.html', context)


def route_point_delete(request, point_id):
    """View for deleting a route point"""
    route_point = get_object_or_404(RoutePoint, id=point_id)
    car = route_point.car
    
    if request.method == 'POST':
        route_point.delete()
        messages.success(request, 'Route point deleted successfully!')
        return redirect('cars:route_point_list', car_id=car.id)
    
    context = {
        'route_point': route_point,
        'car': car
    }
    
    return render(request, 'cars/route_point_confirm_delete.html', context)


def car_route_report(request, car_id):
    """View for generating a report of a car's route with all employees"""
    car = get_object_or_404(Car, id=car_id)
    route_points = RoutePoint.objects.filter(car=car).order_by('order')
    
    context = {
        'car': car,
        'route_points': route_points,
    }
    
    return render(request, 'cars/car_route_report.html', context)
