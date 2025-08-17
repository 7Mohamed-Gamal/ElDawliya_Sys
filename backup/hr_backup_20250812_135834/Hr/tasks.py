"""
Celery tasks for HR System
"""

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import timedelta, date
import logging

logger = logging.getLogger('hr_system')


@shared_task
def sync_attendance_from_devices():
    """مزامنة سجلات الحضور من الأجهزة"""
    try:
        from .models_enhanced import AttendanceMachine
        from .services import AttendanceService
        
        attendance_service = AttendanceService()
        synced_count = 0
        
        # Get all active attendance machines
        machines = AttendanceMachine.objects.filter(is_active=True)
        
        for machine in machines:
            try:
                result = attendance_service.sync_from_device(machine)
                if result.get('success'):
                    synced_count += result.get('processed_count', 0)
                    machine.last_sync = timezone.now()
                    machine.save(update_fields=['last_sync'])
            except Exception as e:
                logger.error(f"Error syncing from machine {machine.name}: {e}")
        
        logger.info(f"Synced {synced_count} attendance records from {machines.count()} machines")
        return {'success': True, 'synced_count': synced_count}
        
    except Exception as e:
        logger.error(f"Error in sync_attendance_from_devices: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def check_document_expiry():
    """فحص انتهاء صلاحية الوثائق وإرسال تنبيهات"""
    try:
        from .models_enhanced import EmployeeFile
        from .services import NotificationService
        
        notification_service = NotificationService()
        warning_days = getattr(settings, 'HR_SETTINGS', {}).get('DOCUMENT_EXPIRY_WARNING_DAYS', 30)
        
        # Get documents expiring soon
        expiring_date = timezone.now().date() + timedelta(days=warning_days)
        expiring_files = EmployeeFile.objects.filter(
            expiry_date__lte=expiring_date,
            expiry_date__gte=timezone.now().date()
        ).select_related('employee')
        
        notifications_sent = 0
        
        for file in expiring_files:
            try:
                notification_service.send_document_expiry_notification(file)
                notifications_sent += 1
            except Exception as e:
                logger.error(f"Error sending notification for file {file.id}: {e}")
        
        logger.info(f"Sent {notifications_sent} document expiry notifications")
        return {'success': True, 'notifications_sent': notifications_sent}
        
    except Exception as e:
        logger.error(f"Error in check_document_expiry: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def calculate_monthly_leave_balances():
    """حساب أرصدة الإجازات الشهرية"""
    try:
        from .models_enhanced import Employee, EmployeeLeaveBalance, LeaveType
        from .services import LeaveService
        
        leave_service = LeaveService()
        current_year = timezone.now().year
        processed_count = 0
        
        # Get all active employees
        employees = Employee.objects.filter(is_active=True)
        leave_types = LeaveType.objects.filter(is_active=True)
        
        for employee in employees:
            for leave_type in leave_types:
                try:
                    leave_service.calculate_leave_balance(employee, leave_type, current_year)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Error calculating leave balance for {employee.employee_number}: {e}")
        
        logger.info(f"Processed {processed_count} leave balance calculations")
        return {'success': True, 'processed_count': processed_count}
        
    except Exception as e:
        logger.error(f"Error in calculate_monthly_leave_balances: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def generate_daily_attendance_summary():
    """إنشاء ملخص الحضور اليومي"""
    try:
        from .models_enhanced import Employee, AttendanceRecord
        from .services import AttendanceService
        
        attendance_service = AttendanceService()
        today = timezone.now().date()
        
        # Get all active employees
        employees = Employee.objects.filter(is_active=True)
        summaries_created = 0
        
        for employee in employees:
            try:
                summary = attendance_service.generate_daily_summary(employee, today)
                if summary:
                    summaries_created += 1
            except Exception as e:
                logger.error(f"Error generating summary for {employee.employee_number}: {e}")
        
        logger.info(f"Generated {summaries_created} daily attendance summaries")
        return {'success': True, 'summaries_created': summaries_created}
        
    except Exception as e:
        logger.error(f"Error in generate_daily_attendance_summary: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def send_birthday_notifications():
    """إرسال تهاني أعياد الميلاد"""
    try:
        from .models_enhanced import Employee
        from .services import NotificationService
        
        notification_service = NotificationService()
        today = timezone.now().date()
        
        # Get employees with birthday today
        birthday_employees = Employee.objects.filter(
            is_active=True,
            date_of_birth__month=today.month,
            date_of_birth__day=today.day
        )
        
        notifications_sent = 0
        
        for employee in birthday_employees:
            try:
                notification_service.send_birthday_notification(employee)
                notifications_sent += 1
            except Exception as e:
                logger.error(f"Error sending birthday notification for {employee.employee_number}: {e}")
        
        logger.info(f"Sent {notifications_sent} birthday notifications")
        return {'success': True, 'notifications_sent': notifications_sent}
        
    except Exception as e:
        logger.error(f"Error in send_birthday_notifications: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def backup_hr_data():
    """نسخ احتياطي لبيانات الموارد البشرية"""
    try:
        from django.core.management import call_command
        from django.core.files.storage import default_storage
        import os
        import gzip
        
        # Create backup filename with timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'hr_backup_{timestamp}.json'
        
        # Create backup
        backup_path = os.path.join(settings.MEDIA_ROOT, 'backups', backup_filename)
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        with open(backup_path, 'w') as f:
            call_command('dumpdata', 'Hr', stdout=f, indent=2)
        
        # Compress backup
        compressed_path = backup_path + '.gz'
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove uncompressed file
        os.remove(backup_path)
        
        logger.info(f"HR data backup created: {compressed_path}")
        return {'success': True, 'backup_file': compressed_path}
        
    except Exception as e:
        logger.error(f"Error in backup_hr_data: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def process_payroll_calculations(payroll_period_id):
    """معالجة حسابات الرواتب"""
    try:
        from .models_enhanced import PayrollPeriod
        from .services import PayrollService
        
        payroll_service = PayrollService()
        
        # Get payroll period
        payroll_period = PayrollPeriod.objects.get(id=payroll_period_id)
        
        # Process payroll
        result = payroll_service.process_period_payroll(payroll_period)
        
        logger.info(f"Processed payroll for period {payroll_period.name}")
        return result
        
    except Exception as e:
        logger.error(f"Error in process_payroll_calculations: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def send_email_notification(recipient_email, subject, template_name, context):
    """إرسال إشعار بريد إلكتروني"""
    try:
        # Render email content
        html_content = render_to_string(f'emails/{template_name}.html', context)
        text_content = render_to_string(f'emails/{template_name}.txt', context)
        
        # Send email
        from django.core.mail import EmailMultiAlternatives
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        logger.info(f"Email sent to {recipient_email}: {subject}")
        return {'success': True}
        
    except Exception as e:
        logger.error(f"Error sending email to {recipient_email}: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_files():
    """تنظيف الملفات القديمة"""
    try:
        import os
        from django.conf import settings
        
        # Clean old backup files (keep last 30 days)
        backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
        if os.path.exists(backup_dir):
            cutoff_date = timezone.now() - timedelta(days=30)
            
            for filename in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, filename)
                if os.path.isfile(file_path):
                    file_time = timezone.datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
        
        # Clean old log files
        log_files = ['hr_system.log', 'api.log']
        for log_file in log_files:
            log_path = os.path.join(settings.BASE_DIR, log_file)
            if os.path.exists(log_path):
                # Keep only last 100MB of log
                if os.path.getsize(log_path) > 100 * 1024 * 1024:  # 100MB
                    # Truncate log file
                    with open(log_path, 'r+') as f:
                        f.seek(50 * 1024 * 1024)  # Keep last 50MB
                        content = f.read()
                        f.seek(0)
                        f.write(content)
                        f.truncate()
        
        logger.info("File cleanup completed")
        return {'success': True}
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_files: {e}")
        return {'success': False, 'error': str(e)}