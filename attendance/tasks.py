"""
مهام Celery لنظام الحضور والانصراف
Celery Tasks for Attendance Management System
"""

from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def sync_all_zk_devices(self):
    """
    مهمة مجدولة لمزامنة جميع أجهزة ZK
    Scheduled task to sync all ZK devices
    """
    try:
        from .zk_service import ZKDataProcessor
        from .models import ZKDevice

        # الحصول على جميع الأجهزة النشطة
        active_devices = ZKDevice.objects.filter(status='active')

        if not active_devices.exists():
            logger.info("لا توجد أجهزة ZK نشطة للمزامنة")
            return {'status': 'success', 'message': 'لا توجد أجهزة نشطة', 'devices_count': 0}

        # معالجة كل جهاز
        total_records_fetched = 0
        total_records_processed = 0
        total_devices_processed = 0
        failed_devices = []

        for device in active_devices:
            try:
                # معالجة بيانات الجهاز
                log = ZKDataProcessor.process_device_data(device)

                if log.status == 'success':
                    total_records_fetched += log.records_fetched
                    total_records_processed += log.records_processed
                    total_devices_processed += 1
                    logger.info(f"تم مزامنة جهاز {device.device_name} بنجاح")
                else:
                    failed_devices.append({
                        'device_name': device.device_name,
                        'error': log.error_message
                    })
                    logger.error(f"فشل في مزامنة جهاز {device.device_name}: {log.error_message}")

            except Exception as e:
                failed_devices.append({
                    'device_name': device.device_name,
                    'error': str(e)
                })
                logger.error(f"خطأ في معالجة جهاز {device.device_name}: {str(e)}")

        # إرسال تقرير بالبريد الإلكتروني إذا كان مفعلاً
        if getattr(settings, 'SEND_ATTENDANCE_REPORTS', False):
            send_sync_report.delay(
                total_devices_processed,
                total_records_fetched,
                total_records_processed,
                failed_devices
            )

        result = {
            'status': 'success',
            'devices_processed': total_devices_processed,
            'total_devices': active_devices.count(),
            'records_fetched': total_records_fetched,
            'records_processed': total_records_processed,
            'failed_devices': failed_devices,
            'timestamp': timezone.now().isoformat()
        }

        logger.info(f"انتهت مزامنة الأجهزة: {total_devices_processed}/{active_devices.count()} أجهزة")
        return result

    except Exception as e:
        logger.error(f"خطأ في مهمة مزامنة الأجهزة: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def sync_single_device(device_id, days=1):
    """
    مزامنة جهاز ZK واحد
    Sync a single ZK device
    """
    try:
        from .models import ZKDevice
        from .zk_service import ZKDataProcessor

        device = ZKDevice.objects.get(device_id=device_id)

        # معالجة بيانات الجهاز
        log = ZKDataProcessor.process_device_data(device)

        result = {
            'device_name': device.device_name,
            'status': log.status,
            'records_fetched': log.records_fetched,
            'records_processed': log.records_processed,
            'records_failed': log.records_failed,
            'error_message': log.error_message,
            'timestamp': timezone.now().isoformat()
        }

        logger.info(f"مزامنة جهاز {device.device_name}: {log.status}")
        return result

    except Exception as e:
        logger.error(f"خطأ في مزامنة الجهاز {device_id}: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def generate_daily_attendance_summary():
    """
    إنشاء ملخص الحضور اليومي
    Generate daily attendance summary
    """
    try:
        from .models import EmployeeAttendance, AttendanceSummary
        from employees.models import Employee
        from django.db.models import Count, Q
        from datetime import date

        today = date.today()
        current_month = today.month
        current_year = today.year

        # تحديث ملخصات الحضور للشهر الحالي
        active_employees = Employee.objects.filter(emp_status='Active')
        updated_count = 0

        for employee in active_employees:
            # حساب إحصائيات الموظف للشهر الحالي
            monthly_records = EmployeeAttendance.objects.filter(
                emp=employee,
                att_date__year=current_year,
                att_date__month=current_month
            )

            if monthly_records.exists():
                stats = monthly_records.aggregate(
                    total_days=Count('att_id'),
                    present_days=Count('att_id', filter=Q(status='Present')),
                    absent_days=Count('att_id', filter=Q(status='Absent')),
                    late_days=Count('att_id', filter=Q(status='Late'))
                )

                # حساب ساعات العمل ودقائق التأخير
                total_work_hours = 0
                total_late_minutes = 0

                for record in monthly_records:
                    if record.check_in and record.check_out:
                        work_duration = record.check_out - record.check_in
                        total_work_hours += work_duration.total_seconds() / 3600

                    total_late_minutes += record.calculate_late_minutes()

                # إنشاء أو تحديث الملخص
                summary, created = AttendanceSummary.objects.update_or_create(
                    employee=employee,
                    year=current_year,
                    month=current_month,
                    defaults={
                        'total_work_days': stats['total_days'],
                        'present_days': stats['present_days'],
                        'absent_days': stats['absent_days'],
                        'late_days': stats['late_days'],
                        'total_work_hours': round(total_work_hours, 2),
                        'late_minutes': total_late_minutes
                    }
                )

                if created:
                    updated_count += 1

        logger.info(f"تم تحديث ملخصات الحضور لـ {updated_count} موظف")

        return {
            'status': 'success',
            'employees_processed': active_employees.count(),
            'summaries_updated': updated_count,
            'month': current_month,
            'year': current_year,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"خطأ في إنشاء ملخص الحضور اليومي: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def send_sync_report(devices_processed, records_fetched, records_processed, failed_devices):
    """
    إرسال تقرير المزامنة بالبريد الإلكتروني
    Send sync report via email
    """
    try:
        subject = f"تقرير مزامنة أجهزة الحضور - {timezone.now().strftime('%Y-%m-%d %H:%M')}"

        message = f"""
        تقرير مزامنة أجهزة الحضور

        النتائج:
        - عدد الأجهزة المعالجة: {devices_processed}
        - إجمالي السجلات المسحوبة: {records_fetched}
        - السجلات المعالجة بنجاح: {records_processed}
        - الأجهزة الفاشلة: {len(failed_devices)}

        """

        if failed_devices:
            message += "\n\nالأجهزة التي فشلت في المزامنة:\n"
            for device in failed_devices:
                message += f"- {device['device_name']}: {device['error']}\n"

        message += f"\n\nوقت التقرير: {timezone.now()}\n"

        # قائمة المستلمين
        recipients = getattr(settings, 'ATTENDANCE_REPORT_RECIPIENTS', [])

        if recipients:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False
            )

            logger.info(f"تم إرسال تقرير المزامنة إلى {len(recipients)} مستلم")

        return {
            'status': 'success',
            'recipients_count': len(recipients)
        }

    except Exception as e:
        logger.error(f"خطأ في إرسال تقرير المزامنة: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def cleanup_old_zk_data(days_to_keep=90):
    """
    تنظيف البيانات القديمة من جدول ZK
    Cleanup old ZK raw data
    """
    try:
        from .models import ZKAttendanceRaw, AttendanceProcessingLog
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days_to_keep)

        # حذف البيانات الخام القديمة والمعالجة
        old_raw_data = ZKAttendanceRaw.objects.filter(
            timestamp__lt=cutoff_date,
            is_processed=True
        )

        deleted_raw_count = old_raw_data.count()
        old_raw_data.delete()

        # حذف سجلات المعالجة القديمة
        old_logs = AttendanceProcessingLog.objects.filter(
            created_at__lt=cutoff_date
        )

        deleted_logs_count = old_logs.count()
        old_logs.delete()

        logger.info(f"تم حذف {deleted_raw_count} سجل خام و {deleted_logs_count} سجل معالجة")

        return {
            'status': 'success',
            'deleted_raw_records': deleted_raw_count,
            'deleted_logs': deleted_logs_count,
            'cutoff_date': cutoff_date.isoformat(),
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"خطأ في تنظيف البيانات القديمة: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def check_device_connectivity():
    """
    فحص اتصال أجهزة ZK
    Check ZK devices connectivity
    """
    try:
        from .models import ZKDevice

        devices = ZKDevice.objects.filter(status='active')
        online_devices = []
        offline_devices = []

        for device in devices:
            if device.is_online():
                online_devices.append(device.device_name)
            else:
                offline_devices.append(device.device_name)

        # إرسال تنبيه إذا كان هناك أجهزة غير متصلة
        if offline_devices and getattr(settings, 'SEND_CONNECTIVITY_ALERTS', False):
            send_connectivity_alert.delay(offline_devices)

        logger.info(f"فحص الاتصال: {len(online_devices)} متصل، {len(offline_devices)} غير متصل")

        return {
            'status': 'success',
            'total_devices': devices.count(),
            'online_devices': online_devices,
            'offline_devices': offline_devices,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"خطأ في فحص اتصال الأجهزة: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def send_connectivity_alert(offline_devices):
    """
    إرسال تنبيه انقطاع الاتصال
    Send connectivity alert
    """
    try:
        subject = "تنبيه: أجهزة حضور غير متصلة"

        message = f"""
        تنبيه: تم اكتشاف أجهزة حضور غير متصلة

        الأجهزة غير المتصلة:
        """

        for device in offline_devices:
            message += f"- {device}\n"

        message += f"\n\nوقت الفحص: {timezone.now()}\n"
        message += "يرجى التحقق من حالة الأجهزة والشبكة.\n"

        recipients = getattr(settings, 'CONNECTIVITY_ALERT_RECIPIENTS', [])

        if recipients:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False
            )

            logger.info(f"تم إرسال تنبيه الاتصال إلى {len(recipients)} مستلم")

        return {
            'status': 'success',
            'recipients_count': len(recipients)
        }

    except Exception as e:
        logger.error(f"خطأ في إرسال تنبيه الاتصال: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def generate_monthly_attendance_report():
    """
    إنشاء تقرير الحضور الشهري
    Generate monthly attendance report
    """
    try:
        from .models import AttendanceSummary, EmployeeAttendance
        from employees.models import Employee
        from django.db.models import Count, Q, Avg, Sum
        from datetime import date
        import calendar

        today = date.today()
        # التقرير للشهر الماضي
        if today.month == 1:
            report_month = 12
            report_year = today.year - 1
        else:
            report_month = today.month - 1
            report_year = today.year

        # إحصائيات عامة
        total_employees = Employee.objects.filter(emp_status='Active').count()

        summaries = AttendanceSummary.objects.filter(
            year=report_year,
            month=report_month
        )

        if summaries.exists():
            stats = summaries.aggregate(
                avg_attendance_rate=Avg('attendance_rate'),
                avg_punctuality_rate=Avg('punctuality_rate'),
                total_present_days=Sum('present_days'),
                total_absent_days=Sum('absent_days'),
                total_late_days=Sum('late_days'),
                total_work_hours=Sum('total_work_hours')
            )

            # إنشاء التقرير
            month_name = calendar.month_name[report_month]

            report_content = f"""
            تقرير الحضور الشهري - {month_name} {report_year}

            الإحصائيات العامة:
            - إجمالي الموظفين: {total_employees}
            - متوسط نسبة الحضور: {stats['avg_attendance_rate']:.1f}%
            - متوسط نسبة الالتزام بالوقت: {stats['avg_punctuality_rate']:.1f}%
            - إجمالي أيام الحضور: {stats['total_present_days']}
            - إجمالي أيام الغياب: {stats['total_absent_days']}
            - إجمالي أيام التأخير: {stats['total_late_days']}
            - إجمالي ساعات العمل: {stats['total_work_hours']:.1f}

            تاريخ التقرير: {timezone.now()}
            """

            # إرسال التقرير
            recipients = getattr(settings, 'MONTHLY_REPORT_RECIPIENTS', [])

            if recipients:
                send_mail(
                    subject=f"تقرير الحضور الشهري - {month_name} {report_year}",
                    message=report_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipients,
                    fail_silently=False
                )

                logger.info(f"تم إرسال التقرير الشهري إلى {len(recipients)} مستلم")

            return {
                'status': 'success',
                'month': report_month,
                'year': report_year,
                'total_employees': total_employees,
                'summaries_count': summaries.count(),
                'recipients_count': len(recipients)
            }
        else:
            logger.warning(f"لا توجد ملخصات حضور للشهر {report_month}/{report_year}")
            return {
                'status': 'warning',
                'message': 'لا توجد بيانات للشهر المحدد'
            }

    except Exception as e:
        logger.error(f"خطأ في إنشاء التقرير الشهري: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


# مهام الصيانة والتحسين
@shared_task
def optimize_attendance_data():
    """
    تحسين بيانات الحضور
    Optimize attendance data
    """
    try:
        from .models import EmployeeAttendance
        from django.db import connection

        # تحديث الحالات المفقودة
        updated_count = 0

        # البحث عن السجلات بدون حالة
        records_without_status = EmployeeAttendance.objects.filter(
            status__isnull=True
        )

        for record in records_without_status:
            if record.check_in and record.check_out:
                record.status = 'Present'
            elif record.check_in:
                record.status = 'Present'  # دخول بدون خروج
            else:
                record.status = 'Absent'

            record.save()
            updated_count += 1

        # تحسين فهارس قاعدة البيانات
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE STATISTICS [EmployeeAttendance] WITH FULLSCAN"
            )

        logger.info(f"تم تحسين {updated_count} سجل حضور")

        return {
            'status': 'success',
            'updated_records': updated_count,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"خطأ في تحسين بيانات الحضور: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }
