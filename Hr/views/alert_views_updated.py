from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import F

from Hr.models.employee_model import Employee
from Hr.models.car_models import Car
from Hr.models.hr_task_models import HrTask
from Hr.models.task_models import EmployeeTask


@login_required
def alert_list(request):
    """عرض قائمة التنبيهات"""
    today = timezone.now().date()
    
    # الحصول على إعدادات التنبيهات (لاحقاً، سيتم تخزينها في قاعدة البيانات)
    settings = get_alert_settings(request)
    
    # قائمة تنبيهات العقود
    contract_alerts = []
    contract_expiry_query = Employee.objects.filter(
        contract_expiry_date__isnull=False,
        contract_expiry_date__gte=today,
        contract_expiry_date__lte=today + timedelta(days=settings.get('contract_alert_days', 30)),
    ).order_by('contract_expiry_date')
    
    for employee in contract_expiry_query:
        days_remaining = (employee.contract_expiry_date - today).days
        contract_alerts.append({
            'employee': employee,
            'days_remaining': days_remaining
        })
    
    # قائمة تنبيهات البطاقات الصحية
    health_card_alerts = []
    health_card_query = Employee.objects.filter(
        health_card_expiry_date__isnull=False,
        health_card_expiry_date__gte=today,
        health_card_expiry_date__lte=today + timedelta(days=settings.get('health_card_alert_days', 30)),
    ).order_by('health_card_expiry_date')
    
    for employee in health_card_query:
        days_remaining = (employee.health_card_expiry_date - today).days
        health_card_alerts.append({
            'employee': employee,
            'days_remaining': days_remaining
        })
    
    # قائمة تنبيهات المهام المتأخرة
    task_alerts = []
    task_query = EmployeeTask.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=today - timedelta(days=settings.get('task_overdue_days', 0))
    ).order_by('due_date')
    
    for task in task_query:
        days_overdue = (today - task.due_date).days
        task_alerts.append({
            'task': task,
            'days_overdue': days_overdue
        })
    
    # قائمة تنبيهات مهام الموارد البشرية المتأخرة
    hr_task_alerts = []
    hr_task_query = HrTask.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=today - timedelta(days=settings.get('task_overdue_days', 0))
    ).order_by('due_date')
    
    for task in hr_task_query:
        days_overdue = (today - task.due_date).days
        hr_task_alerts.append({
            'task': task,
            'days_overdue': days_overdue
        })
    
    # قائمة تنبيهات تراخيص السيارات
    car_license_alerts = []
    car_license_query = Car.objects.filter(
        car_license_expiration_date__isnull=False,
        car_license_expiration_date__gte=today,
        car_license_expiration_date__lte=today + timedelta(days=settings.get('car_license_alert_days', 30)),
    ).order_by('car_license_expiration_date')
    
    for car in car_license_query:
        days_remaining = (car.car_license_expiration_date - today).days
        car_license_alerts.append({
            'car': car,
            'days_remaining': days_remaining
        })
    
    # قائمة تنبيهات تراخيص السائقين
    driver_license_alerts = []
    driver_license_query = Car.objects.filter(
        driver_license_expiration_date__isnull=False,
        driver_license_expiration_date__gte=today,
        driver_license_expiration_date__lte=today + timedelta(days=settings.get('driver_license_alert_days', 30)),
    ).order_by('driver_license_expiration_date')
    
    for car in driver_license_query:
        days_remaining = (car.driver_license_expiration_date - today).days
        driver_license_alerts.append({
            'car': car,
            'days_remaining': days_remaining
        })
    
    # قائمة تنبيهات التأمينات
    insurance_alerts = []
    # هذه مجرد عينة، يمكن تغييرها حسب احتياجك
    insurance_query = Employee.objects.filter(
        insurance_status='مؤمن عليه',
        insurance_date__lte=today - timedelta(days=365)
    ).order_by('insurance_date')
    
    for employee in insurance_query:
        days_since = (today - employee.insurance_date).days
        insurance_alerts.append({
            'employee': employee,
            'days_since': days_since
        })
    
    context = {
        'settings': settings,
        'contract_alerts': contract_alerts,
        'health_card_alerts': health_card_alerts,
        'task_alerts': task_alerts,
        'hr_task_alerts': hr_task_alerts,
        'car_license_alerts': car_license_alerts,
        'driver_license_alerts': driver_license_alerts,
        'insurance_alerts': insurance_alerts,
        'title': 'التنبيهات'
    }
    
    return render(request, 'Hr/alerts/alert_list.html', context)


@login_required
def alert_settings(request):
    """إعدادات التنبيهات"""
    settings = get_alert_settings(request)
    
    if request.method == 'POST':
        # تحديث إعدادات التنبيهات
        new_settings = {
            'contract_alert_days': int(request.POST.get('contract_alert_days', 30)),
            'health_card_alert_days': int(request.POST.get('health_card_alert_days', 30)),
            'task_overdue_days': int(request.POST.get('task_overdue_days', 0)),
            'car_license_alert_days': int(request.POST.get('car_license_alert_days', 30)),
            'driver_license_alert_days': int(request.POST.get('driver_license_alert_days', 30)),
            'transportation_allowance_days': int(request.POST.get('transportation_allowance_days', 30)),
            'alert_importance_level': request.POST.get('alert_importance_level', 'medium'),
            'email_notifications': request.POST.get('email_notifications') == 'on',
        }
        
        # حفظ الإعدادات في قاعدة البيانات أو في جلسة المستخدم
        # هنا نستخدم جلسة المستخدم للتبسيط
        request.session['alert_settings'] = new_settings
        
        messages.success(request, 'تم تحديث إعدادات التنبيهات بنجاح')
        return redirect('Hr:alerts:list')
    
    context = {
        'settings': settings,
        'title': 'إعدادات التنبيهات'
    }
    
    return render(request, 'Hr/alerts/alert_settings.html', context)


@login_required
def renew_contract(request, emp_id):
    """تجديد عقد موظف"""
    employee = get_object_or_404(Employee, emp_id=emp_id)
    
    if request.method == 'POST':
        # تحديث تاريخ انتهاء العقد
        new_expiry_date = request.POST.get('new_expiry_date')
        if new_expiry_date:
            try:
                employee.contract_expiry_date = timezone.datetime.strptime(new_expiry_date, '%Y-%m-%d').date()
                employee.save()
                messages.success(request, f'تم تجديد عقد {employee.emp_full_name} بنجاح')
                return redirect('Hr:employees:detail', emp_id=employee.emp_id)
            except (ValueError, TypeError):
                messages.error(request, 'صيغة التاريخ غير صحيحة')
    
    context = {
        'employee': employee,
        'title': f'تجديد عقد {employee.emp_full_name}'
    }
    
    return render(request, 'Hr/employees/renew_contract.html', context)


@login_required
def renew_health_card(request, emp_id):
    """تجديد البطاقة الصحية لموظف"""
    employee = get_object_or_404(Employee, emp_id=emp_id)
    
    if request.method == 'POST':
        # تحديث تاريخ انتهاء البطاقة الصحية
        new_expiry_date = request.POST.get('new_expiry_date')
        if new_expiry_date:
            try:
                employee.health_card_expiry_date = timezone.datetime.strptime(new_expiry_date, '%Y-%m-%d').date()
                employee.save()
                messages.success(request, f'تم تجديد البطاقة الصحية لـ {employee.emp_full_name} بنجاح')
                return redirect('Hr:employees:detail', emp_id=employee.emp_id)
            except (ValueError, TypeError):
                messages.error(request, 'صيغة التاريخ غير صحيحة')
    
    context = {
        'employee': employee,
        'title': f'تجديد البطاقة الصحية لـ {employee.emp_full_name}'
    }
    
    return render(request, 'Hr/employees/renew_health_card.html', context)


# وظائف مساعدة
def get_alert_settings(request):
    """الحصول على إعدادات التنبيهات"""
    # في الواقع، يمكن تخزين هذه الإعدادات في قاعدة البيانات
    # هنا نستخدم جلسة المستخدم للتبسيط
    default_settings = {
        'contract_alert_days': 30,
        'health_card_alert_days': 30,
        'task_overdue_days': 1,
        'car_license_alert_days': 30,
        'driver_license_alert_days': 30,
        'transportation_allowance_days': 30,
        'alert_importance_level': 'medium',
        'email_notifications': False,
    }
    
    return request.session.get('alert_settings', default_settings)
