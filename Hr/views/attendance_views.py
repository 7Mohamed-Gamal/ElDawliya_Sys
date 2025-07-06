from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from Hr.models.attendance_models import (
    AttendanceRule, EmployeeAttendanceRule, OfficialHoliday,
    AttendanceMachine, AttendanceRecord, AttendanceSummary
)
from Hr.models.employee_model import Employee
from Hr.forms.attendance_forms import (
    AttendanceRuleForm, EmployeeAttendanceRuleForm, EmployeeAttendanceRuleBulkForm,
    OfficialHolidayForm, AttendanceMachineForm, AttendanceRecordForm, FetchAttendanceDataForm
)

@login_required
def attendance_rule_list(request):
    """View for listing attendance rules"""
    rules = AttendanceRule.objects.all()
    return render(request, 'Hr/attendance/attendance_rule_list.html', {
        'attendance_rules': rules,
        'page_title': _('قواعد الحضور')
    })

@login_required
def attendance_rule_create(request):
    """View for creating a new attendance rule"""
    if request.method == 'POST':
        form = AttendanceRuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم إنشاء قاعدة الحضور بنجاح'))
            return redirect('Hr:attendance:attendance_rule_list')
    else:
        form = AttendanceRuleForm()
    
    return render(request, 'Hr/attendance/attendance_rule_form.html', {
        'form': form,
        'page_title': _('إنشاء قاعدة حضور جديدة')
    })

@login_required
def attendance_rule_edit(request, pk):
    """View for editing an attendance rule"""
    rule = get_object_or_404(AttendanceRule, pk=pk)
    if request.method == 'POST':
        form = AttendanceRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث قاعدة الحضور بنجاح'))
            return redirect('Hr:attendance:attendance_rule_list')
    else:
        form = AttendanceRuleForm(instance=rule)
    
    return render(request, 'Hr/attendance/attendance_rule_form.html', {
        'form': form,
        'rule': rule,
        'page_title': _('تعديل قاعدة الحضور')
    })

@login_required
def attendance_rule_delete(request, pk):
    """View for deleting an attendance rule"""
    rule = get_object_or_404(AttendanceRule, pk=pk)
    if request.method == 'POST':
        rule.delete()
        messages.success(request, _('تم حذف قاعدة الحضور بنجاح'))
        return redirect('Hr:attendance:attendance_rule_list')
    
    return render(request, 'Hr/attendance/attendance_rule_confirm_delete.html', {
        'rule': rule,
        'page_title': _('حذف قاعدة الحضور')
    })

@login_required
def employee_attendance_rule_list(request):
    """View for listing employee attendance rules"""
    rules = EmployeeAttendanceRule.objects.select_related('employee', 'attendance_rule').all()
    
    # Filter by employee if provided
    employee_id = request.GET.get('employee')
    if employee_id:
        rules = rules.filter(employee_id=employee_id)
    
    # Get active employees for filter
    employees = Employee.objects.filter(working_condition='سارى')
    
    return render(request, 'Hr/attendance/employee_attendance_rule_list.html', {
        'rules': rules,
        'employees': employees,
        'selected_employee': employee_id,
        'page_title': _('قواعد حضور الموظفين')
    })

@login_required
def employee_attendance_rule_create(request):
    """View for creating a new employee attendance rule"""
    if request.method == 'POST':
        form = EmployeeAttendanceRuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم إنشاء قاعدة حضور الموظف بنجاح'))
            return redirect('Hr:attendance:employee_attendance_rule_list')
    else:
        form = EmployeeAttendanceRuleForm()
    
    return render(request, 'Hr/attendance/employee_attendance_rule_form.html', {
        'form': form,
        'page_title': _('إنشاء قاعدة حضور موظف جديدة')
    })

@login_required
def employee_attendance_rule_edit(request, pk):
    """View for editing an employee attendance rule"""
    rule = get_object_or_404(EmployeeAttendanceRule, pk=pk)
    if request.method == 'POST':
        form = EmployeeAttendanceRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث قاعدة حضور الموظف بنجاح'))
            return redirect('Hr:attendance:employee_attendance_rule_list')
    else:
        form = EmployeeAttendanceRuleForm(instance=rule)
    
    return render(request, 'Hr/attendance/employee_attendance_rule_form.html', {
        'form': form,
        'rule': rule,
        'page_title': _('تعديل قاعدة حضور الموظف')
    })

@login_required
def employee_attendance_rule_delete(request, pk):
    """View for deleting an employee attendance rule"""
    rule = get_object_or_404(EmployeeAttendanceRule, pk=pk)
    if request.method == 'POST':
        rule.delete()
        messages.success(request, _('تم حذف قاعدة حضور الموظف بنجاح'))
        return redirect('Hr:attendance:employee_attendance_rule_list')
    
    return render(request, 'Hr/attendance/employee_attendance_rule_confirm_delete.html', {
        'rule': rule,
        'page_title': _('حذف قاعدة حضور الموظف')
    })

@login_required
def employee_attendance_rule_bulk_create(request):
    """View for creating multiple employee attendance rules at once"""
    if request.method == 'POST':
        form = EmployeeAttendanceRuleBulkForm(request.POST)
        if form.is_valid():
            rule = form.cleaned_data['attendance_rule']
            employees = form.cleaned_data['employees']
            effective_date = form.cleaned_data['effective_date']
            end_date = form.cleaned_data['end_date']
            is_active = form.cleaned_data['is_active']
            
            # Create rules for each selected employee
            created_count = 0
            for employee in employees:
                EmployeeAttendanceRule.objects.create(
                    employee=employee,
                    attendance_rule=rule,
                    effective_date=effective_date,
                    end_date=end_date,
                    is_active=is_active
                )
                created_count += 1
            
            messages.success(request, _('تم إنشاء {} قاعدة حضور للموظفين بنجاح').format(created_count))
            return redirect('Hr:attendance:employee_attendance_rule_list')
    else:
        form = EmployeeAttendanceRuleBulkForm()
    
    return render(request, 'Hr/attendance/employee_attendance_rule_bulk_form.html', {
        'form': form,
        'page_title': _('إنشاء قواعد حضور متعددة للموظفين')
    })

@login_required
def official_holiday_list(request):
    """View for listing official holidays"""
    holidays = OfficialHoliday.objects.all().order_by('date')
    return render(request, 'Hr/attendance/official_holiday_list.html', {
        'holidays': holidays,
        'page_title': _('الإجازات الرسمية')
    })

@login_required
def official_holiday_create(request):
    """View for creating a new official holiday"""
    if request.method == 'POST':
        form = OfficialHolidayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم إنشاء الإجازة الرسمية بنجاح'))
            return redirect('Hr:attendance:official_holiday_list')
    else:
        form = OfficialHolidayForm()
    
    return render(request, 'Hr/attendance/official_holiday_form.html', {
        'form': form,
        'page_title': _('إنشاء إجازة رسمية جديدة')
    })

@login_required
def official_holiday_edit(request, pk):
    """View for editing an official holiday"""
    holiday = get_object_or_404(OfficialHoliday, pk=pk)
    if request.method == 'POST':
        form = OfficialHolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث الإجازة الرسمية بنجاح'))
            return redirect('Hr:attendance:official_holiday_list')
    else:
        form = OfficialHolidayForm(instance=holiday)
    
    return render(request, 'Hr/attendance/official_holiday_form.html', {
        'form': form,
        'holiday': holiday,
        'page_title': _('تعديل الإجازة الرسمية')
    })

@login_required
def official_holiday_delete(request, pk):
    """View for deleting an official holiday"""
    holiday = get_object_or_404(OfficialHoliday, pk=pk)
    if request.method == 'POST':
        holiday.delete()
        messages.success(request, _('تم حذف الإجازة الرسمية بنجاح'))
        return redirect('Hr:attendance:official_holiday_list')
    
    return render(request, 'Hr/attendance/official_holiday_confirm_delete.html', {
        'holiday': holiday,
        'page_title': _('حذف الإجازة الرسمية')
    })

@login_required
def attendance_machine_list(request):
    """View for listing attendance machines"""
    machines = AttendanceMachine.objects.all()
    return render(request, 'Hr/attendance/attendance_machine_list.html', {
        'machines': machines,
        'page_title': _('أجهزة البصمة')
    })

@login_required
def attendance_machine_create(request):
    """View for creating a new attendance machine"""
    if request.method == 'POST':
        form = AttendanceMachineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم إنشاء جهاز البصمة بنجاح'))
            return redirect('Hr:attendance:attendance_machine_list')
    else:
        form = AttendanceMachineForm()
    
    return render(request, 'Hr/attendance/attendance_machine_form.html', {
        'form': form,
        'page_title': _('إنشاء جهاز بصمة جديد')
    })

@login_required
def attendance_machine_edit(request, pk):
    """View for editing an attendance machine"""
    machine = get_object_or_404(AttendanceMachine, pk=pk)
    if request.method == 'POST':
        form = AttendanceMachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث جهاز البصمة بنجاح'))
            return redirect('Hr:attendance:attendance_machine_list')
    else:
        form = AttendanceMachineForm(instance=machine)
    
    return render(request, 'Hr/attendance/attendance_machine_form.html', {
        'form': form,
        'machine': machine,
        'page_title': _('تعديل جهاز البصمة')
    })

@login_required
def attendance_machine_delete(request, pk):
    """View for deleting an attendance machine"""
    machine = get_object_or_404(AttendanceMachine, pk=pk)
    if request.method == 'POST':
        machine.delete()
        messages.success(request, _('تم حذف جهاز البصمة بنجاح'))
        return redirect('Hr:attendance:attendance_machine_list')
    
    return render(request, 'Hr/attendance/attendance_machine_confirm_delete.html', {
        'machine': machine,
        'page_title': _('حذف جهاز البصمة')
    })

@login_required
def attendance_record_list(request):
    """View for listing attendance records"""
    records = AttendanceRecord.objects.select_related('employee', 'machine').all()
    
    # Apply filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    employee_id = request.GET.get('employee')
    record_type = request.GET.get('record_type')
    
    if date_from:
        records = records.filter(record_date__gte=date_from)
    if date_to:
        records = records.filter(record_date__lte=date_to)
    if employee_id:
        records = records.filter(employee_id=employee_id)
    if record_type:
        records = records.filter(record_type=record_type)
    
    # Order records
    records = records.order_by('-record_date', '-record_time')
    
    # Paginate results
    paginator = Paginator(records, 20)
    page = request.GET.get('page')
    records = paginator.get_page(page)
    
    # Get active employees for filter
    employees = Employee.objects.filter(working_condition='سارى')
    
    return render(request, 'Hr/attendance/attendance_record_list.html', {
        'records': records,
        'employees': employees,
        'record_types': dict(AttendanceRecord.RECORD_TYPE_CHOICES),
        'selected_employee': employee_id,
        'selected_record_type': record_type,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'page_title': _('سجلات الحضور والانصراف')
    })

@login_required
def attendance_record_create(request):
    """View for creating a new attendance record"""
    if request.method == 'POST':
        form = AttendanceRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.source = 'manual'
            record.save()
            messages.success(request, _('تم إنشاء سجل الحضور بنجاح'))
            return redirect('Hr:attendance:attendance_record_list')
    else:
        form = AttendanceRecordForm()
    
    return render(request, 'Hr/attendance/attendance_record_form.html', {
        'form': form,
        'page_title': _('إنشاء سجل حضور جديد')
    })

@login_required
def attendance_record_edit(request, pk):
    """View for editing an attendance record"""
    record = get_object_or_404(AttendanceRecord, pk=pk)
    if request.method == 'POST':
        form = AttendanceRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث سجل الحضور بنجاح'))
            return redirect('Hr:attendance:attendance_record_list')
    else:
        form = AttendanceRecordForm(instance=record)
    
    return render(request, 'Hr/attendance/attendance_record_form.html', {
        'form': form,
        'record': record,
        'page_title': _('تعديل سجل الحضور')
    })

@login_required
def attendance_record_delete(request, pk):
    """View for deleting an attendance record"""
    record = get_object_or_404(AttendanceRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, _('تم حذف سجل الحضور بنجاح'))
        return redirect('Hr:attendance:attendance_record_list')
    
    return render(request, 'Hr/attendance/attendance_record_confirm_delete.html', {
        'record': record,
        'page_title': _('حذف سجل الحضور')
    })

@login_required
def fetch_attendance_data(request):
    """View for fetching attendance data from machines"""
    if request.method == 'POST':
        form = FetchAttendanceDataForm(request.POST)
        if form.is_valid():
            machine = form.cleaned_data['machine']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            clear_existing = form.cleaned_data['clear_existing']

            try:
                from Hr.utils import ZKDeviceService, AttendanceProcessor
                from datetime import datetime, time
                from django.utils import timezone

                # Convert dates to datetime objects
                start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
                end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))

                # Connect to ZK device and fetch data
                with ZKDeviceService(machine.ip_address, machine.port) as zk_device:
                    if not zk_device.is_connected:
                        messages.error(request, _('فشل في الاتصال بجهاز البصمة'))
                        return redirect('Hr:attendance:fetch_attendance_data')

                    # Get attendance records from device
                    zk_records = zk_device.get_attendance_records(start_datetime, end_datetime)

                    if not zk_records:
                        messages.warning(request, _('لم يتم العثور على سجلات في الفترة المحددة'))
                        return redirect('Hr:attendance:attendance_record_list')

                    # Process and store records
                    processor = AttendanceProcessor()

                    # Validate records first
                    valid_records, validation_errors = processor.validate_zk_records(zk_records)

                    if validation_errors:
                        for error in validation_errors[:5]:  # Show first 5 errors
                            messages.warning(request, f'تحذير: {error}')

                    # Process valid records
                    if valid_records:
                        results = processor.process_zk_records(
                            machine=machine,
                            zk_records=valid_records,
                            clear_existing=clear_existing,
                            user=request.user
                        )

                        # Show results
                        if results['processed'] > 0:
                            messages.success(request,
                                _('تم جلب وحفظ {} سجل حضور بنجاح').format(results['processed']))

                        if results['skipped'] > 0:
                            messages.info(request,
                                _('تم تجاهل {} سجل موجود مسبقاً').format(results['skipped']))

                        if results['errors'] > 0:
                            messages.error(request,
                                _('حدثت أخطاء في {} سجل').format(results['errors']))

                            # Show first few error details
                            for error in results['error_details'][:3]:
                                messages.error(request, error)
                    else:
                        messages.error(request, _('لا توجد سجلات صالحة للمعالجة'))

                return redirect('Hr:attendance:attendance_record_list')

            except Exception as e:
                messages.error(request, _('حدث خطأ أثناء جلب البيانات: {}').format(str(e)))
    else:
        form = FetchAttendanceDataForm()
    
    return render(request, 'Hr/attendance/fetch_attendance_data.html', {
        'form': form,
        'page_title': _('جلب بيانات الحضور')
    })


@login_required
def zk_device_connection(request):
    """View for ZK device connection interface"""
    from Hr.models.attendance_models import AttendanceMachine

    attendance_machines = AttendanceMachine.objects.filter(is_active=True)

    return render(request, 'Hr/attendance/zk_device_connection.html', {
        'page_title': _('اتصال جهاز البصمة'),
        'attendance_machines': attendance_machines
    })


@login_required
def test_zk_connection(request):
    """AJAX view for testing ZK device connection"""
    if request.method == 'POST':
        try:
            import json
            from Hr.utils import ZKDeviceService

            data = json.loads(request.body)
            ip_address = data.get('ip_address')
            port = int(data.get('port', 4370))
            password = data.get('password', '')

            if not ip_address:
                return JsonResponse({
                    'success': False,
                    'error': 'عنوان IP مطلوب'
                })

            # Test connection
            zk_device = ZKDeviceService(ip_address, port, password)
            if zk_device.connect():
                device_info = zk_device.get_device_info()
                zk_device.disconnect()

                return JsonResponse({
                    'success': True,
                    'message': 'تم الاتصال بجهاز البصمة بنجاح',
                    'device_info': device_info
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'فشل في الاتصال بجهاز البصمة'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'خطأ في الاتصال: {str(e)}'
            })

    return JsonResponse({'success': False, 'error': 'طريقة غير مدعومة'})


@login_required
def fetch_zk_records_ajax(request):
    """AJAX view for fetching ZK records without saving"""
    if request.method == 'POST':
        try:
            import json
            from Hr.utils import ZKDeviceService
            from datetime import datetime, time
            from django.utils import timezone

            data = json.loads(request.body)
            ip_address = data.get('ip_address')
            port = int(data.get('port', 4370))
            password = data.get('password', '')
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            if not ip_address:
                return JsonResponse({
                    'success': False,
                    'error': 'عنوان IP مطلوب'
                })

            # Parse dates
            start_datetime = None
            end_datetime = None

            if start_date:
                start_datetime = timezone.make_aware(
                    datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(), time.min)
                )

            if end_date:
                end_datetime = timezone.make_aware(
                    datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(), time.max)
                )

            # Connect and fetch records
            with ZKDeviceService(ip_address, port, password) as zk_device:
                if not zk_device.is_connected:
                    return JsonResponse({
                        'success': False,
                        'error': 'فشل في الاتصال بجهاز البصمة'
                    })

                records = zk_device.get_attendance_records(start_datetime, end_datetime)

                # Format records for display
                formatted_records = []
                for record in records:
                    formatted_records.append({
                        'user_id': record.get('user_id', ''),
                        'timestamp': record.get('timestamp').strftime('%Y-%m-%d %H:%M:%S') if record.get('timestamp') else '',
                        'verify_type': record.get('verify_type', 0),
                        'in_out_mode': 'حضور' if record.get('in_out_mode') == 0 else 'انصراف',
                        'raw_data': record.get('raw_data', '')
                    })

                return JsonResponse({
                    'success': True,
                    'records': formatted_records,
                    'total_count': len(formatted_records)
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'خطأ في جلب البيانات: {str(e)}'
            })

    return JsonResponse({'success': False, 'error': 'طريقة غير مدعومة'})


@login_required
def save_zk_records_to_db(request):
    """AJAX view for saving ZK records to database"""
    if request.method == 'POST':
        try:
            import json
            from Hr.utils import ZKDeviceService, AttendanceProcessor
            from Hr.models.attendance_models import AttendanceMachine
            from datetime import datetime, time
            from django.utils import timezone

            data = json.loads(request.body)
            machine_id = data.get('machine_id')
            ip_address = data.get('ip_address')
            port = int(data.get('port', 4370))
            password = data.get('password', '')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            clear_existing = data.get('clear_existing', False)

            if not machine_id:
                return JsonResponse({
                    'success': False,
                    'error': 'معرف الجهاز مطلوب'
                })

            # Get machine
            try:
                machine = AttendanceMachine.objects.get(id=machine_id)
            except AttendanceMachine.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'جهاز البصمة غير موجود'
                })

            # Parse dates
            start_datetime = None
            end_datetime = None

            if start_date:
                start_datetime = timezone.make_aware(
                    datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(), time.min)
                )

            if end_date:
                end_datetime = timezone.make_aware(
                    datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(), time.max)
                )

            # Connect and fetch records
            with ZKDeviceService(ip_address, port, password) as zk_device:
                if not zk_device.is_connected:
                    return JsonResponse({
                        'success': False,
                        'error': 'فشل في الاتصال بجهاز البصمة'
                    })

                records = zk_device.get_attendance_records(start_datetime, end_datetime)

                if not records:
                    return JsonResponse({
                        'success': True,
                        'message': 'لا توجد سجلات في الفترة المحددة',
                        'results': {
                            'total_records': 0,
                            'processed': 0,
                            'skipped': 0,
                            'errors': 0
                        }
                    })

                # Process records
                processor = AttendanceProcessor()
                valid_records, validation_errors = processor.validate_zk_records(records)

                if valid_records:
                    results = processor.process_zk_records(
                        machine=machine,
                        zk_records=valid_records,
                        clear_existing=clear_existing,
                        user=request.user
                    )

                    return JsonResponse({
                        'success': True,
                        'message': f'تم معالجة {results["processed"]} سجل بنجاح',
                        'results': results,
                        'validation_errors': validation_errors
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'لا توجد سجلات صالحة للمعالجة',
                        'validation_errors': validation_errors
                    })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'خطأ في حفظ البيانات: {str(e)}'
            })

    return JsonResponse({'success': False, 'error': 'طريقة غير مدعومة'})

@login_required
def attendance_summary_list(request):
    """View for listing attendance summaries"""
    summaries = AttendanceSummary.objects.select_related('employee').all()
    
    # Apply filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    employee_id = request.GET.get('employee')
    status = request.GET.get('status')
    
    if date_from:
        summaries = summaries.filter(date__gte=date_from)
    if date_to:
        summaries = summaries.filter(date__lte=date_to)
    if employee_id:
        summaries = summaries.filter(employee_id=employee_id)
    if status:
        summaries = summaries.filter(status=status)
    
    # Order summaries
    summaries = summaries.order_by('-date')
    
    # Paginate results
    paginator = Paginator(summaries, 20)
    page = request.GET.get('page')
    summaries = paginator.get_page(page)
    
    # Get active employees for filter
    employees = Employee.objects.filter(working_condition='سارى')
    
    return render(request, 'Hr/attendance/attendance_summary_list.html', {
        'summaries': summaries,
        'employees': employees,
        'statuses': dict(AttendanceSummary.STATUS_CHOICES),
        'selected_employee': employee_id,
        'selected_status': status,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'page_title': _('ملخصات الحضور والانصراف')
    })

@login_required
def attendance_summary_detail(request, pk):
    """View for viewing attendance summary details"""
    summary = get_object_or_404(AttendanceSummary, pk=pk)
    return render(request, 'Hr/attendance/attendance_summary_detail.html', {
        'summary': summary,
        'page_title': _('تفاصيل ملخص الحضور والانصراف')
    })