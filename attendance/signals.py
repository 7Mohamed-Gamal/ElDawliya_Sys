"""
إشارات نظام الحضور والانصراف
Attendance System Signals
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from datetime import date, datetime
import logging

from .models import (
    EmployeeAttendance,
    ZKAttendanceRaw,
    AttendanceProcessingLog,
    AttendanceSummary,
    EmployeeDeviceMapping,
    ZKDevice
)
from employees.models import Employee

logger = logging.getLogger(__name__)


@receiver(post_save, sender=EmployeeAttendance)
def update_attendance_summary_on_save(sender, instance, created, **kwargs):
    """
    تحديث ملخص الحضور عند إضافة أو تعديل سجل حضور
    Update attendance summary when attendance record is created or updated
    """
    try:
        if instance.att_date:
            year = instance.att_date.year
            month = instance.att_date.month

            # البحث عن ملخص الحضور للموظف والشهر
            summary, created = AttendanceSummary.objects.get_or_create(
                employee=instance.emp,
                year=year,
                month=month,
                defaults={
                    'total_work_days': 0,
                    'present_days': 0,
                    'absent_days': 0,
                    'late_days': 0,
                    'total_work_hours': 0,
                    'late_minutes': 0
                }
            )

            # إعادة حساب الإحصائيات للشهر
            monthly_records = EmployeeAttendance.objects.filter(
                emp=instance.emp,
                att_date__year=year,
                att_date__month=month
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            # حساب الإحصائيات
            total_days = monthly_records.count()
            present_days = monthly_records.filter(status='Present').count()
            absent_days = monthly_records.filter(status='Absent').count()
            late_days = monthly_records.filter(status='Late').count()

            # حساب ساعات العمل ودقائق التأخير
            total_work_hours = 0
            total_late_minutes = 0

            for record in monthly_records:
                if record.check_in and record.check_out:
                    work_duration = record.check_out - record.check_in
                    total_work_hours += work_duration.total_seconds() / 3600

                total_late_minutes += record.calculate_late_minutes()

            # تحديث الملخص
            summary.total_work_days = total_days
            summary.present_days = present_days
            summary.absent_days = absent_days
            summary.late_days = late_days
            summary.total_work_hours = round(total_work_hours, 2)
            summary.late_minutes = total_late_minutes
            summary.save()

            logger.info(f"تم تحديث ملخص الحضور للموظف {instance.emp.emp_code} للشهر {month}/{year}")

    except Exception as e:
        logger.error(f"خطأ في تحديث ملخص الحضور: {str(e)}")


@receiver(post_delete, sender=EmployeeAttendance)
def update_attendance_summary_on_delete(sender, instance, **kwargs):
    """
    تحديث ملخص الحضور عند حذف سجل حضور
    Update attendance summary when attendance record is deleted
    """
    try:
        if instance.att_date:
            year = instance.att_date.year
            month = instance.att_date.month

            try:
                summary = AttendanceSummary.objects.get(
                    employee=instance.emp,
                    year=year,
                    month=month
                )

                # إعادة حساب الإحصائيات بعد الحذف
                monthly_records = EmployeeAttendance.objects.filter(
                    emp=instance.emp,
                    att_date__year=year,
                    att_date__month=month
                ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

                if monthly_records.exists():
                    # تحديث الإحصائيات
                    total_days = monthly_records.count()
                    present_days = monthly_records.filter(status='Present').count()
                    absent_days = monthly_records.filter(status='Absent').count()
                    late_days = monthly_records.filter(status='Late').count()

                    total_work_hours = 0
                    total_late_minutes = 0

                    for record in monthly_records:
                        if record.check_in and record.check_out:
                            work_duration = record.check_out - record.check_in
                            total_work_hours += work_duration.total_seconds() / 3600

                        total_late_minutes += record.calculate_late_minutes()

                    summary.total_work_days = total_days
                    summary.present_days = present_days
                    summary.absent_days = absent_days
                    summary.late_days = late_days
                    summary.total_work_hours = round(total_work_hours, 2)
                    summary.late_minutes = total_late_minutes
                    summary.save()
                else:
                    # حذف الملخص إذا لم تعد هناك سجلات
                    summary.delete()

                logger.info(f"تم تحديث ملخص الحضور بعد الحذف للموظف {instance.emp.emp_code}")

            except AttendanceSummary.DoesNotExist:
                pass

    except Exception as e:
        logger.error(f"خطأ في تحديث ملخص الحضور بعد الحذف: {str(e)}")


@receiver(post_save, sender=ZKAttendanceRaw)
def process_zk_raw_data(sender, instance, created, **kwargs):
    """
    معالجة البيانات الخام من أجهزة ZK تلقائياً
    Automatically process ZK raw data
    """
    if created and not instance.is_processed and instance.employee:
        try:
            from .zk_service import ZKDataProcessor

            # معالجة السجل الخام
            ZKDataProcessor._create_attendance_record(instance)

            logger.info(f"تم معالجة السجل الخام {instance.raw_id} تلقائياً")

        except Exception as e:
            logger.error(f"خطأ في معالجة السجل الخام {instance.raw_id}: {str(e)}")


@receiver(post_save, sender=ZKDevice)
def clear_device_cache_on_update(sender, instance, **kwargs):
    """
    مسح الذاكرة المؤقتة عند تحديث بيانات الجهاز
    Clear device cache when device data is updated
    """
    try:
        # مسح ذاكرة حالة الجهاز المؤقتة
        cache_key = f"zk_device_status_{instance.device_id}"
        cache.delete(cache_key)

        # مسح ذاكرة قائمة الأجهزة النشطة
        cache.delete("active_zk_devices")

        logger.debug(f"تم مسح الذاكرة المؤقتة للجهاز {instance.device_name}")

    except Exception as e:
        logger.error(f"خطأ في مسح الذاكرة المؤقتة للجهاز: {str(e)}")


@receiver(post_save, sender=EmployeeDeviceMapping)
def update_zk_raw_data_on_mapping(sender, instance, created, **kwargs):
    """
    تحديث البيانات الخام عند إضافة ربط جديد للموظف
    Update ZK raw data when new employee mapping is created
    """
    if created and instance.is_active:
        try:
            # البحث عن البيانات الخام غير المرتبطة بموظف لهذا الجهاز ومعرف المستخدم
            unlinked_records = ZKAttendanceRaw.objects.filter(
                device=instance.device,
                user_id=instance.device_user_id,
                employee__isnull=True
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            if unlinked_records.exists():
                # ربط البيانات الخام بالموظف
                updated_count = unlinked_records.update(employee=instance.employee)

                logger.info(
                    f"تم ربط {updated_count} سجل خام بالموظف {instance.employee.emp_code} "
                    f"في جهاز {instance.device.device_name}"
                )

                # معالجة السجلات غير المعالجة
                from .zk_service import ZKDataProcessor

                for record in unlinked_records.filter(is_processed=False):
                    try:
                        ZKDataProcessor._create_attendance_record(record)
                    except Exception as e:
                        logger.error(f"خطأ في معالجة السجل {record.raw_id}: {str(e)}")

        except Exception as e:
            logger.error(f"خطأ في تحديث البيانات الخام عند الربط: {str(e)}")


@receiver(pre_save, sender=EmployeeAttendance)
def calculate_attendance_status(sender, instance, **kwargs):
    """
    حساب حالة الحضور تلقائياً قبل الحفظ
    Automatically calculate attendance status before saving
    """
    try:
        if instance.check_in and instance.att_date and instance.rule:
            # حساب التأخير
            late_minutes = instance.calculate_late_minutes()
            early_leave_minutes = instance.calculate_early_leave_minutes()

            # تحديد الحالة بناءً على المنطق
            if not instance.check_out:
                # لم يسجل خروج بعد
                if late_minutes > (instance.rule.late_threshold or 0):
                    instance.status = 'Late'
                else:
                    instance.status = 'Present'
            else:
                # سجل دخول وخروج
                if late_minutes > (instance.rule.late_threshold or 0):
                    instance.status = 'Late'
                elif early_leave_minutes > (instance.rule.early_threshold or 0):
                    instance.status = 'EarlyLeave'
                else:
                    instance.status = 'Present'
        elif not instance.check_in and not instance.check_out:
            # لم يسجل حضور
            instance.status = 'Absent'

    except Exception as e:
        logger.error(f"خطأ في حساب حالة الحضور: {str(e)}")


@receiver(post_save, sender=AttendanceProcessingLog)
def notify_processing_completion(sender, instance, created, **kwargs):
    """
    إرسال إشعار عند اكتمال معالجة البيانات
    Send notification when processing is completed
    """
    if created and instance.status in ['success', 'failed']:
        try:
            # يمكن إضافة منطق الإشعارات هنا
            # مثل إرسال بريد إلكتروني أو إشعار داخلي

            if instance.status == 'failed':
                logger.warning(
                    f"فشلت معالجة بيانات جهاز {instance.device.device_name}: "
                    f"{instance.error_message}"
                )
            else:
                logger.info(
                    f"اكتملت معالجة بيانات جهاز {instance.device.device_name} بنجاح: "
                    f"{instance.records_processed} سجل من أصل {instance.records_fetched}"
                )

        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار المعالجة: {str(e)}")


@receiver(post_save, sender=Employee)
def create_default_attendance_profile(sender, instance, created, **kwargs):
    """
    إنشاء ملف حضور افتراضي للموظف الجديد
    Create default attendance profile for new employee
    """
    if created:
        try:
            from .models import AttendanceRules, EmployeeAttendanceProfile

            # البحث عن قاعدة الحضور الافتراضية
            default_rule = AttendanceRules.objects.filter(is_default=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            if default_rule:
                # إنشاء ملف الحضور
                profile, profile_created = EmployeeAttendanceProfile.objects.get_or_create(
                    employee=instance,
                    defaults={
                        'attendance_rule': default_rule,
                        'work_hours_per_day': 8.0,
                        'salary_status': 'active',
                        'attendance_status': 'active'
                    }
                )

                if profile_created:
                    logger.info(f"تم إنشاء ملف حضور افتراضي للموظف {instance.emp_code}")

        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف الحضور للموظف الجديد: {str(e)}")


# إشارات تنظيف البيانات القديمة
@receiver(post_save, sender=ZKAttendanceRaw)
def cleanup_old_processed_data(sender, instance, **kwargs):
    """
    تنظيف البيانات الخام القديمة والمعالجة
    Cleanup old processed raw data
    """
    if instance.is_processed:
        try:
            from datetime import timedelta

            # حذف البيانات الخام المعالجة الأقدم من 90 يوم
            cutoff_date = timezone.now() - timedelta(days=90)

            old_records = ZKAttendanceRaw.objects.filter(
                device=instance.device,
                is_processed=True,
                timestamp__lt=cutoff_date
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            # حذف بشكل دوري وليس مع كل سجل
            if old_records.count() > 1000:
                deleted_count = old_records[:500].delete()[0]
                logger.info(f"تم حذف {deleted_count} سجل خام قديم من جهاز {instance.device.device_name}")

        except Exception as e:
            logger.error(f"خطأ في تنظيف البيانات القديمة: {str(e)}")


# إشارات الأمان والتدقيق
@receiver(post_save, sender=EmployeeAttendance)
@receiver(post_delete, sender=EmployeeAttendance)
def log_attendance_changes(sender, instance, **kwargs):
    """
    تسجيل تغييرات الحضور في سجل التدقيق
    Log attendance changes in audit trail
    """
    try:
        # يمكن إضافة منطق تسجيل التغييرات هنا
        # للتكامل مع نظام التدقيق (audit app)
        pass

    except Exception as e:
        logger.error(f"خطأ في تسجيل تغييرات الحضور: {str(e)}")


# إشارات التحقق من صحة البيانات
@receiver(pre_save, sender=ZKAttendanceRaw)
def validate_zk_raw_data(sender, instance, **kwargs):
    """
    التحقق من صحة البيانات الخام قبل الحفظ
    Validate ZK raw data before saving
    """
    try:
        # التحقق من صحة التاريخ والوقت
        if instance.timestamp:
            if instance.timestamp > timezone.now():
                logger.warning(f"سجل خام بتاريخ مستقبلي: {instance.timestamp}")

            # التحقق من عدم تكرار السجل
            existing = ZKAttendanceRaw.objects.filter(
                device=instance.device,
                user_id=instance.user_id,
                timestamp=instance.timestamp,
                punch_type=instance.punch_type
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exclude(pk=instance.pk).exists()

            if existing:
                logger.warning(f"سجل خام مكرر: جهاز {instance.device.device_name}, مستخدم {instance.user_id}")

    except Exception as e:
        logger.error(f"خطأ في التحقق من صحة البيانات الخام: {str(e)}")
