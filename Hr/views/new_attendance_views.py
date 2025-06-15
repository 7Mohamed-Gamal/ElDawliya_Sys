# =============================================================================
# ElDawliya HR Management System - New Attendance Views
# =============================================================================
# Views for attendance and time tracking management
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg, F
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from datetime import date, time, datetime, timedelta
import json

from Hr.models import (
    WorkShift, AttendanceMachine, EmployeeShiftAssignment,
    AttendanceRecord, Employee, Company, Branch
)
from Hr.forms.new_attendance_forms import (
    WorkShiftForm, AttendanceMachineForm, EmployeeShiftAssignmentForm,
    AttendanceRecordForm, AttendanceReportForm
)


# =============================================================================
# WORK SHIFT VIEWS
# =============================================================================

class NewWorkShiftListView(LoginRequiredMixin, ListView):
    """عرض قائمة الورديات الجديد"""
    model = WorkShift
    template_name = 'Hr/new_attendance/workshift_list.html'
    context_object_name = 'work_shifts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = WorkShift.objects.select_related('company').order_by('company__name', 'name')
        
        # التصفية حسب الشركة
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # التصفية حسب نوع الوردية
        shift_type = self.request.GET.get('shift_type')
        if shift_type:
            queryset = queryset.filter(shift_type=shift_type)
        
        # التصفية حسب الحالة
        status = self.request.GET.get('status')
        if status:
            is_active = status == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إدارة الورديات')
        context['companies'] = Company.objects.filter(is_active=True)
        context['shift_types'] = WorkShift._meta.get_field('shift_type').choices
        
        # إحصائيات
        context['total_shifts'] = WorkShift.objects.count()
        context['active_shifts'] = WorkShift.objects.filter(is_active=True).count()
        context['assigned_employees'] = EmployeeShiftAssignment.objects.filter(
            is_active=True
        ).count()
        
        return context


class NewWorkShiftDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل الوردية الجديد"""
    model = WorkShift
    template_name = 'Hr/new_attendance/workshift_detail.html'
    context_object_name = 'work_shift'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        work_shift = self.get_object()
        
        context['title'] = f"تفاصيل الوردية - {work_shift.name}"
        
        # الموظفين المعينين لهذه الوردية
        context['assigned_employees'] = work_shift.employee_assignments.filter(
            is_active=True
        ).select_related('employee')
        
        # إحصائيات الوردية
        context['total_assigned'] = work_shift.employee_assignments.filter(is_active=True).count()
        context['active_assignments'] = work_shift.employee_assignments.filter(
            is_active=True,
            start_date__lte=date.today(),
            end_date__gte=date.today()
        ).count()
        
        return context


class NewWorkShiftCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء وردية جديدة"""
    model = WorkShift
    form_class = WorkShiftForm
    template_name = 'Hr/new_attendance/workshift_form.html'
    permission_required = 'Hr.add_workshift'
    success_url = reverse_lazy('hr:new_workshift_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إضافة وردية جديدة')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء الوردية بنجاح'))
        return super().form_valid(form)


class NewWorkShiftUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """تحديث بيانات الوردية"""
    model = WorkShift
    form_class = WorkShiftForm
    template_name = 'Hr/new_attendance/workshift_form.html'
    permission_required = 'Hr.change_workshift'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"تحديث الوردية - {self.get_object().name}"
        context['action'] = 'update'
        return context
    
    def get_success_url(self):
        return reverse('hr:new_workshift_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث بيانات الوردية بنجاح'))
        return super().form_valid(form)


# =============================================================================
# ATTENDANCE MACHINE VIEWS
# =============================================================================

class NewAttendanceMachineListView(LoginRequiredMixin, ListView):
    """عرض قائمة أجهزة الحضور الجديد"""
    model = AttendanceMachine
    template_name = 'Hr/new_attendance/machine_list.html'
    context_object_name = 'machines'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AttendanceMachine.objects.select_related(
            'company', 'branch'
        ).order_by('company__name', 'branch__name', 'name')
        
        # التصفية حسب الشركة
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # التصفية حسب الفرع
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # التصفية حسب نوع الجهاز
        machine_type = self.request.GET.get('machine_type')
        if machine_type:
            queryset = queryset.filter(machine_type=machine_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إدارة أجهزة الحضور')
        context['companies'] = Company.objects.filter(is_active=True)
        context['branches'] = Branch.objects.filter(is_active=True)
        context['machine_types'] = AttendanceMachine._meta.get_field('machine_type').choices
        
        return context


class NewAttendanceMachineCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إضافة جهاز حضور جديد"""
    model = AttendanceMachine
    form_class = AttendanceMachineForm
    template_name = 'Hr/new_attendance/machine_form.html'
    permission_required = 'Hr.add_attendancemachine'
    success_url = reverse_lazy('hr:new_attendance_machine_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إضافة جهاز حضور جديد')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('تم إضافة جهاز الحضور بنجاح'))
        return super().form_valid(form)


# =============================================================================
# EMPLOYEE SHIFT ASSIGNMENT VIEWS
# =============================================================================

class NewEmployeeShiftAssignmentListView(LoginRequiredMixin, ListView):
    """عرض قائمة تعيينات الورديات الجديد"""
    model = EmployeeShiftAssignment
    template_name = 'Hr/new_attendance/shift_assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = EmployeeShiftAssignment.objects.select_related(
            'employee', 'work_shift', 'employee__department'
        ).order_by('-start_date', 'employee__full_name')
        
        # التصفية حسب الموظف
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # التصفية حسب الوردية
        work_shift_id = self.request.GET.get('work_shift')
        if work_shift_id:
            queryset = queryset.filter(work_shift_id=work_shift_id)
        
        # التصفية حسب الحالة
        status = self.request.GET.get('status')
        if status:
            is_active = status == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('تعيينات الورديات')
        context['employees'] = Employee.objects.filter(status='active')
        context['work_shifts'] = WorkShift.objects.filter(is_active=True)
        
        return context


class NewEmployeeShiftAssignmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """تعيين وردية للموظف"""
    model = EmployeeShiftAssignment
    form_class = EmployeeShiftAssignmentForm
    template_name = 'Hr/new_attendance/shift_assignment_form.html'
    permission_required = 'Hr.add_employeeshiftassignment'
    success_url = reverse_lazy('hr:new_shift_assignment_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        employee_id = self.request.GET.get('employee')
        if employee_id:
            try:
                kwargs['employee'] = Employee.objects.get(pk=employee_id)
            except Employee.DoesNotExist:
                pass
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('تعيين وردية للموظف')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _('تم تعيين الوردية للموظف بنجاح'))
        return super().form_valid(form)


# =============================================================================
# ATTENDANCE RECORD VIEWS
# =============================================================================

class NewAttendanceRecordListView(LoginRequiredMixin, ListView):
    """عرض سجلات الحضور الجديد"""
    model = AttendanceRecord
    template_name = 'Hr/new_attendance/attendance_list.html'
    context_object_name = 'attendance_records'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related(
            'employee', 'machine'
        ).order_by('-date', '-timestamp')
        
        # التصفية حسب التاريخ
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # إذا لم يتم تحديد تاريخ، اعرض آخر 7 أيام
        if not date_from and not date_to:
            week_ago = date.today() - timedelta(days=7)
            queryset = queryset.filter(date__gte=week_ago)
        
        # التصفية حسب الموظف
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # التصفية حسب الحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # التصفية حسب نوع الحضور
        attendance_type = self.request.GET.get('attendance_type')
        if attendance_type:
            queryset = queryset.filter(attendance_type=attendance_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('سجلات الحضور والانصراف')
        
        # خيارات التصفية
        context['employees'] = Employee.objects.filter(status='active')
        context['status_choices'] = AttendanceRecord.STATUS_CHOICES
        context['attendance_type_choices'] = AttendanceRecord.ATTENDANCE_TYPE_CHOICES
        
        # القيم المحددة في التصفية
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['employee_filter'] = self.request.GET.get('employee', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['attendance_type_filter'] = self.request.GET.get('attendance_type', '')
        
        # إحصائيات اليوم
        today = date.today()
        today_records = AttendanceRecord.objects.filter(date=today)
        
        context['today_stats'] = {
            'total_records': today_records.count(),
            'present_employees': today_records.filter(
                attendance_type='check_in'
            ).values('employee').distinct().count(),
            'late_employees': today_records.filter(
                status='late'
            ).values('employee').distinct().count(),
            'overtime_employees': today_records.filter(
                status='overtime'
            ).values('employee').distinct().count(),
        }
        
        return context


class NewAttendanceRecordCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """تسجيل حضور يدوي جديد"""
    model = AttendanceRecord
    form_class = AttendanceRecordForm
    template_name = 'Hr/new_attendance/attendance_form.html'
    permission_required = 'Hr.add_attendancerecord'
    success_url = reverse_lazy('hr:new_attendance_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('تسجيل حضور يدوي')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        form.instance.is_manual = True
        form.instance.created_by = self.request.user
        
        # حساب دقائق التأخير والوقت الإضافي
        self.calculate_attendance_metrics(form.instance)
        
        messages.success(self.request, _('تم تسجيل الحضور بنجاح'))
        return super().form_valid(form)
    
    def calculate_attendance_metrics(self, record):
        """حساب مؤشرات الحضور"""
        try:
            # الحصول على الوردية المعينة للموظف
            assignment = EmployeeShiftAssignment.objects.filter(
                employee=record.employee,
                is_active=True,
                start_date__lte=record.date,
                end_date__gte=record.date
            ).first()
            
            if assignment:
                work_shift = assignment.work_shift
                
                if record.attendance_type == 'check_in':
                    # حساب التأخير
                    scheduled_start = datetime.combine(record.date, work_shift.start_time)
                    actual_time = record.timestamp
                    
                    if actual_time > scheduled_start:
                        late_minutes = (actual_time - scheduled_start).total_seconds() / 60
                        if late_minutes > work_shift.grace_period_minutes:
                            record.late_minutes = int(late_minutes - work_shift.grace_period_minutes)
                            record.status = 'late'
                        else:
                            record.status = 'present'
                    else:
                        record.status = 'present'
                
                elif record.attendance_type == 'check_out':
                    # حساب الوقت الإضافي
                    scheduled_end = datetime.combine(record.date, work_shift.end_time)
                    actual_time = record.timestamp
                    
                    if actual_time > scheduled_end:
                        overtime_minutes = (actual_time - scheduled_end).total_seconds() / 60
                        if overtime_minutes > work_shift.overtime_threshold_minutes:
                            record.overtime_minutes = int(overtime_minutes)
                            record.status = 'overtime'
        
        except Exception as e:
            # في حالة حدوث خطأ، اتركه كما هو
            pass


# =============================================================================
# AJAX VIEWS
# =============================================================================

@login_required
def new_attendance_dashboard_data(request):
    """بيانات لوحة تحكم الحضور الجديد - AJAX"""
    today = date.today()
    
    # إحصائيات اليوم
    today_records = AttendanceRecord.objects.filter(date=today)
    
    data = {
        'today_stats': {
            'total_employees': Employee.objects.filter(status='active').count(),
            'present_employees': today_records.filter(
                attendance_type='check_in'
            ).values('employee').distinct().count(),
            'late_employees': today_records.filter(status='late').count(),
            'absent_employees': 0,  # سيتم حسابه لاحقاً
            'overtime_employees': today_records.filter(status='overtime').count(),
        },
        'recent_records': [
            {
                'employee_name': record.employee.full_name,
                'time': record.timestamp.strftime('%H:%M'),
                'type': record.get_attendance_type_display(),
                'status': record.get_status_display()
            }
            for record in today_records.order_by('-timestamp')[:10]
        ]
    }
    
    # حساب الموظفين الغائبين
    present_employee_ids = today_records.filter(
        attendance_type='check_in'
    ).values_list('employee_id', flat=True)
    
    data['today_stats']['absent_employees'] = Employee.objects.filter(
        status='active'
    ).exclude(id__in=present_employee_ids).count()
    
    return JsonResponse(data)


@login_required
def new_attendance_quick_add(request):
    """إضافة سريعة لسجل حضور - AJAX"""
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        attendance_type = request.POST.get('attendance_type')
        
        try:
            employee = Employee.objects.get(pk=employee_id)
            
            # إنشاء سجل حضور جديد
            record = AttendanceRecord.objects.create(
                employee=employee,
                date=date.today(),
                attendance_type=attendance_type,
                timestamp=timezone.now(),
                status='present',
                is_manual=True,
                created_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': f'تم تسجيل {record.get_attendance_type_display()} للموظف {employee.full_name}',
                'record_id': str(record.id)
            })
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'الموظف غير موجود'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'طلب غير صحيح'})


# =============================================================================
# ATTENDANCE REPORTS
# =============================================================================

class NewAttendanceReportView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """تقرير الحضور والانصراف الجديد"""
    model = AttendanceRecord
    template_name = 'Hr/new_attendance/attendance_report.html'
    context_object_name = 'attendance_data'
    permission_required = 'Hr.view_attendancerecord'

    def get_queryset(self):
        # سيتم تخصيص هذا في get_context_data
        return AttendanceRecord.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('تقرير الحضور والانصراف')

        # نموذج التقرير
        form = AttendanceReportForm(self.request.GET or None)
        context['form'] = form

        if form.is_valid():
            # تطبيق التصفية
            queryset = AttendanceRecord.objects.select_related('employee', 'machine')

            # التصفية حسب الشركة
            company = form.cleaned_data.get('company')
            if company:
                queryset = queryset.filter(employee__company=company)

            # التصفية حسب الفرع
            branch = form.cleaned_data.get('branch')
            if branch:
                queryset = queryset.filter(employee__branch=branch)

            # التصفية حسب الموظف
            employee = form.cleaned_data.get('employee')
            if employee:
                queryset = queryset.filter(employee=employee)

            # التصفية حسب التاريخ
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)

            # التصفية حسب الحالة
            status = form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)

            # ترتيب النتائج
            queryset = queryset.order_by('employee__full_name', 'date', 'timestamp')

            # تجميع البيانات حسب الموظف واليوم
            attendance_summary = self.generate_attendance_summary(queryset)
            context['attendance_summary'] = attendance_summary

            # إحصائيات التقرير
            context['report_stats'] = self.calculate_report_stats(queryset)

        return context

    def generate_attendance_summary(self, queryset):
        """تجميع بيانات الحضور حسب الموظف واليوم"""
        from collections import defaultdict

        summary = defaultdict(lambda: defaultdict(dict))

        for record in queryset:
            employee_key = record.employee.id
            date_key = record.date

            if employee_key not in summary:
                summary[employee_key]['employee'] = record.employee
                summary[employee_key]['days'] = {}

            if date_key not in summary[employee_key]['days']:
                summary[employee_key]['days'][date_key] = {
                    'date': date_key,
                    'check_in': None,
                    'check_out': None,
                    'status': 'absent',
                    'late_minutes': 0,
                    'overtime_minutes': 0,
                    'total_hours': 0
                }

            day_data = summary[employee_key]['days'][date_key]

            if record.attendance_type == 'check_in':
                day_data['check_in'] = record.timestamp.time()
                day_data['status'] = record.status
                day_data['late_minutes'] = record.late_minutes

            elif record.attendance_type == 'check_out':
                day_data['check_out'] = record.timestamp.time()
                day_data['overtime_minutes'] = record.overtime_minutes

                # حساب إجمالي ساعات العمل
                if day_data['check_in']:
                    check_in_dt = datetime.combine(date_key, day_data['check_in'])
                    check_out_dt = datetime.combine(date_key, day_data['check_out'])
                    total_seconds = (check_out_dt - check_in_dt).total_seconds()
                    day_data['total_hours'] = total_seconds / 3600

        return dict(summary)

    def calculate_report_stats(self, queryset):
        """حساب إحصائيات التقرير"""
        total_records = queryset.count()

        stats = {
            'total_records': total_records,
            'present_count': queryset.filter(status='present').count(),
            'late_count': queryset.filter(status='late').count(),
            'overtime_count': queryset.filter(status='overtime').count(),
            'absent_count': queryset.filter(status='absent').count(),
            'total_late_minutes': queryset.aggregate(
                total=Sum('late_minutes')
            )['total'] or 0,
            'total_overtime_minutes': queryset.aggregate(
                total=Sum('overtime_minutes')
            )['total'] or 0,
        }

        # حساب النسب المئوية
        if total_records > 0:
            stats['present_percentage'] = (stats['present_count'] / total_records) * 100
            stats['late_percentage'] = (stats['late_count'] / total_records) * 100
            stats['overtime_percentage'] = (stats['overtime_count'] / total_records) * 100
        else:
            stats['present_percentage'] = 0
            stats['late_percentage'] = 0
            stats['overtime_percentage'] = 0

        return stats
