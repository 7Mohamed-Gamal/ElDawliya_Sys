"""
عروض (Views) نظام التدريب
Training Management Views
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from datetime import date, datetime, timedelta
from decimal import Decimal

from .models import TrainingProvider, TrainingCourse, EmployeeTraining
from employees.models import Employee
from .forms import (
    TrainingProviderForm, TrainingCourseForm, EmployeeTrainingForm,
    EmployeeTrainingSearchForm
)


# ================================================================
# DASHBOARD & HOME
# ================================================================

@login_required
def training_dashboard(request):
    """لوحة معلومات نظام التدريب"""

    # Statistics
    total_providers = TrainingProvider.objects.count()
    total_courses = TrainingCourse.objects.count()
    active_courses = TrainingCourse.objects.filter(
        end_date__gte=date.today().prefetch_related()  # TODO: Add appropriate prefetch_related fields
    ).count()
    total_enrollments = EmployeeTraining.objects.count()
    completed_trainings = EmployeeTraining.objects.filter(status='Completed').prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

    # Recent courses
    recent_courses = TrainingCourse.objects.select_related('provider').order_by('-start_date')[:5]

    # Upcoming courses
    upcoming_courses = TrainingCourse.objects.filter(
        start_date__gte=date.today().prefetch_related()  # TODO: Add appropriate prefetch_related fields
    ).select_related('provider').order_by('start_date')[:5]

    # Recent enrollments
    recent_enrollments = EmployeeTraining.objects.select_related(
        'emp', 'course'
    ).order_by('-enrollment_date')[:10]

    # Training by status
    status_stats = EmployeeTraining.objects.values('status').annotate(
        count=Count('emp_training_id')
    )

    context = {
        'total_providers': total_providers,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'total_enrollments': total_enrollments,
        'completed_trainings': completed_trainings,
        'recent_courses': recent_courses,
        'upcoming_courses': upcoming_courses,
        'recent_enrollments': recent_enrollments,
        'status_stats': status_stats,
    }

    return render(request, 'training/dashboard.html', context)


# ================================================================
# TRAINING PROVIDERS CRUD
# ================================================================

@login_required
def provider_list(request):
    """قائمة مزودي التدريب"""
    search_query = request.GET.get('search', '')

    providers = TrainingProvider.objects.all().select_related()  # TODO: Add appropriate select_related fields

    if search_query:
        providers = providers.filter(
            Q(provider_name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    providers = providers.order_by('provider_name')

    # Pagination
    paginator = Paginator(providers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }

    return render(request, 'training/provider_list.html', context)


@login_required
def provider_detail(request, provider_id):
    """تفاصيل مزود تدريب"""
    provider = get_object_or_404(TrainingProvider, provider_id=provider_id)

    # Get courses by this provider
    courses = TrainingCourse.objects.filter(provider=provider).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('-start_date')

    # Statistics
    total_courses = courses.count()
    total_cost = courses.aggregate(Sum('cost'))['cost__sum'] or 0
    total_enrollments = EmployeeTraining.objects.filter(course__provider=provider).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

    context = {
        'provider': provider,
        'courses': courses,
        'total_courses': total_courses,
        'total_cost': total_cost,
        'total_enrollments': total_enrollments,
    }

    return render(request, 'training/provider_detail.html', context)


@login_required
def provider_create(request):
    """إضافة مزود تدريب جديد"""
    if request.method == 'POST':
        form = TrainingProviderForm(request.POST)
        if form.is_valid():
            provider = form.save()
            messages.success(request, f'تم إضافة مزود التدريب "{provider.provider_name}" بنجاح')
            return redirect('training:provider_detail', provider_id=provider.provider_id)
    else:
        form = TrainingProviderForm()

    context = {
        'form': form,
        'title': 'إضافة مزود تدريب جديد',
    }

    return render(request, 'training/provider_form.html', context)


@login_required
def provider_update(request, provider_id):
    """تعديل مزود تدريب"""
    provider = get_object_or_404(TrainingProvider, provider_id=provider_id)

    if request.method == 'POST':
        form = TrainingProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث بيانات مزود التدريب "{provider.provider_name}" بنجاح')
            return redirect('training:provider_detail', provider_id=provider.provider_id)
    else:
        form = TrainingProviderForm(instance=provider)

    context = {
        'form': form,
        'provider': provider,
        'title': f'تعديل مزود التدريب: {provider.provider_name}',
    }

    return render(request, 'training/provider_form.html', context)


@login_required
def provider_delete(request, provider_id):
    """حذف مزود تدريب"""
    provider = get_object_or_404(TrainingProvider, provider_id=provider_id)

    # Check if provider has courses
    courses_count = TrainingCourse.objects.filter(provider=provider).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

    if request.method == 'POST':
        if courses_count > 0:
            messages.error(request, f'لا يمكن حذف مزود التدريب "{provider.provider_name}" لأنه مرتبط بـ {courses_count} دورة تدريبية')
            return redirect('training:provider_detail', provider_id=provider.provider_id)

        provider_name = provider.provider_name
        provider.delete()
        messages.success(request, f'تم حذف مزود التدريب "{provider_name}" بنجاح')
        return redirect('training:provider_list')

    context = {
        'provider': provider,
        'courses_count': courses_count,
    }

    return render(request, 'training/provider_confirm_delete.html', context)


# ================================================================
# TRAINING COURSES CRUD
# ================================================================

@login_required
def course_list(request):
    """قائمة الدورات التدريبية"""
    search_query = request.GET.get('search', '')
    provider_filter = request.GET.get('provider', '')
    status_filter = request.GET.get('status', '')

    courses = TrainingCourse.objects.select_related('provider')

    if search_query:
        courses = courses.filter(
            Q(course_name__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if provider_filter:
        courses = courses.filter(provider_id=provider_filter)

    # Filter by status (upcoming, ongoing, completed)
    today = date.today()
    if status_filter == 'upcoming':
        courses = courses.filter(start_date__gt=today)
    elif status_filter == 'ongoing':
        courses = courses.filter(start_date__lte=today, end_date__gte=today)
    elif status_filter == 'completed':
        courses = courses.filter(end_date__lt=today)

    courses = courses.order_by('-start_date')

    # Pagination
    paginator = Paginator(courses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get providers for filter dropdown
    providers = TrainingProvider.objects.all().select_related()  # TODO: Add appropriate select_related fields.order_by('provider_name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'provider_filter': provider_filter,
        'status_filter': status_filter,
        'providers': providers,
    }

    return render(request, 'training/course_list.html', context)


@login_required
def course_detail(request, course_id):
    """تفاصيل دورة تدريبية"""
    course = get_object_or_404(TrainingCourse, course_id=course_id)

    # Get enrollments for this course
    enrollments = EmployeeTraining.objects.filter(
        course=course
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('emp').order_by('-enrollment_date')

    # Statistics
    total_enrollments = enrollments.count()
    completed_count = enrollments.filter(status='Completed').count()
    in_progress_count = enrollments.filter(status='In Progress').count()
    cancelled_count = enrollments.filter(status='Cancelled').count()

    # Calculate completion rate
    completion_rate = (completed_count / total_enrollments * 100) if total_enrollments > 0 else 0

    # Course status
    today = date.today()
    if course.start_date and course.end_date:
        if course.start_date > today:
            course_status = 'upcoming'
        elif course.start_date <= today <= course.end_date:
            course_status = 'ongoing'
        else:
            course_status = 'completed'
    else:
        course_status = 'unknown'

    context = {
        'course': course,
        'enrollments': enrollments,
        'total_enrollments': total_enrollments,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'cancelled_count': cancelled_count,
        'completion_rate': completion_rate,
        'course_status': course_status,
    }

    return render(request, 'training/course_detail.html', context)


@login_required
def course_create(request):
    """إضافة دورة تدريبية جديدة"""
    if request.method == 'POST':
        form = TrainingCourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'تم إضافة الدورة التدريبية "{course.course_name}" بنجاح')
            return redirect('training:course_detail', course_id=course.course_id)
    else:
        form = TrainingCourseForm()

    context = {
        'form': form,
        'title': 'إضافة دورة تدريبية جديدة',
    }

    return render(request, 'training/course_form.html', context)


@login_required
def course_update(request, course_id):
    """تعديل دورة تدريبية"""
    course = get_object_or_404(TrainingCourse, course_id=course_id)

    if request.method == 'POST':
        form = TrainingCourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث بيانات الدورة "{course.course_name}" بنجاح')
            return redirect('training:course_detail', course_id=course.course_id)
    else:
        form = TrainingCourseForm(instance=course)

    context = {
        'form': form,
        'course': course,
        'title': f'تعديل الدورة: {course.course_name}',
    }

    return render(request, 'training/course_form.html', context)


@login_required
def course_delete(request, course_id):
    """حذف دورة تدريبية"""
    course = get_object_or_404(TrainingCourse, course_id=course_id)

    # Check if course has enrollments
    enrollments_count = EmployeeTraining.objects.filter(course=course).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count()

    if request.method == 'POST':
        if enrollments_count > 0:
            messages.error(request, f'لا يمكن حذف الدورة "{course.course_name}" لأنها مرتبطة بـ {enrollments_count} تسجيل')
            return redirect('training:course_detail', course_id=course.course_id)

        course_name = course.course_name
        course.delete()
        messages.success(request, f'تم حذف الدورة التدريبية "{course_name}" بنجاح')
        return redirect('training:course_list')

    context = {
        'course': course,
        'enrollments_count': enrollments_count,
    }

    return render(request, 'training/course_confirm_delete.html', context)


# ================================================================
# EMPLOYEE TRAINING CRUD
# ================================================================

@login_required
def enrollment_list(request):
    """قائمة تسجيلات الموظفين في الدورات"""
    form = EmployeeTrainingSearchForm(request.GET or None)

    enrollments = EmployeeTraining.objects.select_related('emp', 'course', 'course__provider')

    # Apply filters
    if form.is_valid():
        if form.cleaned_data.get('employee'):
            enrollments = enrollments.filter(emp=form.cleaned_data['employee'])

        if form.cleaned_data.get('course'):
            enrollments = enrollments.filter(course=form.cleaned_data['course'])

        if form.cleaned_data.get('status'):
            enrollments = enrollments.filter(status=form.cleaned_data['status'])

        if form.cleaned_data.get('date_from'):
            enrollments = enrollments.filter(enrollment_date__gte=form.cleaned_data['date_from'])

        if form.cleaned_data.get('date_to'):
            enrollments = enrollments.filter(enrollment_date__lte=form.cleaned_data['date_to'])

    enrollments = enrollments.order_by('-enrollment_date')

    # Pagination
    paginator = Paginator(enrollments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
    }

    return render(request, 'training/enrollment_list.html', context)


@login_required
def enrollment_detail(request, enrollment_id):
    """تفاصيل تسجيل موظف في دورة"""
    enrollment = get_object_or_404(
        EmployeeTraining.objects.select_related('emp', 'course', 'course__provider'),
        emp_training_id=enrollment_id
    )

    context = {
        'enrollment': enrollment,
    }

    return render(request, 'training/enrollment_detail.html', context)


@login_required
def enrollment_create(request):
    """تسجيل موظف في دورة تدريبية"""
    if request.method == 'POST':
        form = EmployeeTrainingForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(
                request,
                f'تم تسجيل الموظف "{enrollment.emp.first_name} {enrollment.emp.last_name}" '
                f'في الدورة "{enrollment.course.course_name}" بنجاح'
            )
            return redirect('training:enrollment_detail', enrollment_id=enrollment.emp_training_id)
    else:
        # Pre-fill enrollment date with today
        initial_data = {'enrollment_date': date.today(), 'status': 'Registered'}
        form = EmployeeTrainingForm(initial=initial_data)

    context = {
        'form': form,
        'title': 'تسجيل موظف في دورة تدريبية',
    }

    return render(request, 'training/enrollment_form.html', context)


@login_required
def enrollment_update(request, enrollment_id):
    """تعديل تسجيل موظف في دورة"""
    enrollment = get_object_or_404(EmployeeTraining, emp_training_id=enrollment_id)

    if request.method == 'POST':
        form = EmployeeTrainingForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات التسجيل بنجاح')
            return redirect('training:enrollment_detail', enrollment_id=enrollment.emp_training_id)
    else:
        form = EmployeeTrainingForm(instance=enrollment)

    context = {
        'form': form,
        'enrollment': enrollment,
        'title': f'تعديل تسجيل: {enrollment.emp.first_name} - {enrollment.course.course_name}',
    }

    return render(request, 'training/enrollment_form.html', context)


@login_required
def enrollment_delete(request, enrollment_id):
    """حذف تسجيل موظف من دورة"""
    enrollment = get_object_or_404(EmployeeTraining, emp_training_id=enrollment_id)

    if request.method == 'POST':
        emp_name = f"{enrollment.emp.first_name} {enrollment.emp.last_name}"
        course_name = enrollment.course.course_name
        enrollment.delete()
        messages.success(request, f'تم حذف تسجيل "{emp_name}" من الدورة "{course_name}" بنجاح')
        return redirect('training:enrollment_list')

    context = {
        'enrollment': enrollment,
    }

    return render(request, 'training/enrollment_confirm_delete.html', context)


# ================================================================
# EMPLOYEE TRAINING HISTORY
# ================================================================

@login_required
def employee_training_history(request, emp_id):
    """سجل تدريبات موظف معين"""
    employee = get_object_or_404(Employee, emp_id=emp_id)

    enrollments = EmployeeTraining.objects.filter(
        emp=employee
    ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('course', 'course__provider').order_by('-enrollment_date')

    # Statistics
    total_trainings = enrollments.count()
    completed_trainings = enrollments.filter(status='Completed').count()
    in_progress_trainings = enrollments.filter(status='In Progress').count()
    total_hours = enrollments.filter(
        status='Completed'
    ).aggregate(Sum('course__duration_hours'))['course__duration_hours__sum'] or 0

    context = {
        'employee': employee,
        'enrollments': enrollments,
        'total_trainings': total_trainings,
        'completed_trainings': completed_trainings,
        'in_progress_trainings': in_progress_trainings,
        'total_hours': total_hours,
    }

    return render(request, 'training/employee_training_history.html', context)
