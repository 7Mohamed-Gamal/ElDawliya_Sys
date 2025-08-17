from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

# Use the legacy Employee model that matches the existing database table
from Hr.models.legacy_employee import LegacyEmployee as Employee
from Hr.models.car_models import HrCar as Car
from Hr.models.hr_task_models import HrTaskNew as HrTask
from Hr.models.task_models import HrEmployeeTask as EmployeeTask

@login_required
def alert_list(request):
    """عرض قائمة التنبيهات"""
    today = timezone.now().date()
    
    # Contract renewals due in the next 30 days
    # NOTE: Disabled - contract_renewal_date field not available in legacy schema
    contract_renewals = Employee.objects.none()  # Empty queryset for legacy compatibility

    # Health cards expiring in the next 30 days
    # NOTE: Disabled - health_card_expiry_date field not available in legacy schema
    health_cards = Employee.objects.none()  # Empty queryset for legacy compatibility
    
    # Car licenses expiring in the next 30 days
    car_licenses = Car.objects.filter(
        car_license_expiration_date__isnull=False,
        car_license_expiration_date__gte=today,
        car_license_expiration_date__lte=today + timedelta(days=30)
    ).order_by('car_license_expiration_date')
    
    # Driver licenses expiring in the next 30 days
    driver_licenses = Car.objects.filter(
        driver_license_expiration_date__isnull=False,
        driver_license_expiration_date__gte=today,
        driver_license_expiration_date__lte=today + timedelta(days=30)
    ).order_by('driver_license_expiration_date')
    
    # HR tasks due in the next 7 days
    hr_tasks = HrTask.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__gte=today,
        due_date__lte=today + timedelta(days=7)
    ).order_by('due_date')
    
    # Overdue HR tasks
    overdue_hr_tasks = HrTask.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=today
    ).order_by('due_date')
    
    # Employee tasks due in the next 7 days
    employee_tasks = EmployeeTask.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__gte=today,
        due_date__lte=today + timedelta(days=7)
    ).order_by('due_date')
    
    # Overdue employee tasks
    overdue_employee_tasks = EmployeeTask.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=today
    ).order_by('due_date')
    
    context = {
        'contract_renewals': contract_renewals,
        'health_cards': health_cards,
        'car_licenses': car_licenses,
        'driver_licenses': driver_licenses,
        'hr_tasks': hr_tasks,
        'overdue_hr_tasks': overdue_hr_tasks,
        'employee_tasks': employee_tasks,
        'overdue_employee_tasks': overdue_employee_tasks,
        'title': 'التنبيهات'
    }
    
    return render(request, 'Hr/alerts/list.html', context)
