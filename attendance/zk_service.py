"""
خدمة إدارة أجهزة ZK للحضور والانصراف
ZK Device Management Service for Attendance Tracking
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import (
    ZKDevice, ZKAttendanceRaw, EmployeeDeviceMapping,
    AttendanceProcessingLog, EmployeeAttendance, Employee
)

# تكوين السجلات
logger = logging.getLogger(__name__)

try:
    from zk import ZK
    ZK_LIBRARY_AVAILABLE = True
except ImportError:
    ZK_LIBRARY_AVAILABLE = False
    logger.warning("مكتبة pyzk غير متوفرة. تأكد من تثبيتها: pip install pyzk")


class ZKDeviceManager:
    """مدير أجهزة ZK للحضور والانصراف"""

    def __init__(self, device: ZKDevice):
        """__init__ function"""
        self.device = device
        self.connection = None

    def connect(self) -> bool:
        """الاتصال بجهاز ZK"""
        if not ZK_LIBRARY_AVAILABLE:
            logger.error("مكتبة pyzk غير متوفرة")
            return False

        try:
            zk = ZK(self.device.ip_address, port=self.device.port,
                   timeout=60, password=0, force_udp=False, ommit_ping=False)

            self.connection = zk.connect()
            if self.connection:
                logger.info(f"تم الاتصال بنجاح بجهاز {self.device.device_name}")
                return True
            else:
                logger.error(f"فشل الاتصال بجهاز {self.device.device_name}")
                return False

        except Exception as e:
            logger.error(f"خطأ في الاتصال بجهاز {self.device.device_name}: {str(e)}")
            return False

    def disconnect(self):
        """قطع الاتصال بجهاز ZK"""
        if self.connection:
            try:
                self.connection.disconnect()
                logger.info(f"تم قطع الاتصال بجهاز {self.device.device_name}")
            except Exception as e:
                logger.error(f"خطأ في قطع الاتصال: {str(e)}")
            finally:
                self.connection = None

    def get_device_info(self) -> Dict:
        """الحصول على معلومات الجهاز"""
        if not self.connection:
            return {}

        try:
            info = {
                'firmware_version': self.connection.get_firmware_version(),
                'serialnumber': self.connection.get_serialnumber(),
                'platform': self.connection.get_platform(),
                'device_name': self.connection.get_device_name(),
                'face_version': self.connection.get_face_version(),
                'fp_version': self.connection.get_fp_version(),
                'extend_fmt': self.connection.get_extend_fmt(),
                'user_extend_fmt': self.connection.get_user_extend_fmt(),
                'face_fun_on': self.connection.get_face_fun_on(),
                'compat_old_firmware': self.connection.get_compat_old_firmware(),
                'network_params': self.connection.get_network_params(),
                'pin_width': self.connection.get_pin_width(),
                'face_template_format': self.connection.get_face_template_format(),
                'time': self.connection.get_time(),
            }
            return info
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الجهاز: {str(e)}")
            return {}

    def fetch_attendance_data(self, start_date: datetime = None) -> List[Dict]:
        """سحب بيانات الحضور من الجهاز"""
        if not self.connection:
            logger.error("لا يوجد اتصال بالجهاز")
            return []

        try:
            # الحصول على جميع سجلات الحضور
            attendances = self.connection.get_attendance()

            attendance_data = []
            for att in attendances:
                # تصفية البيانات حسب التاريخ إذا تم تحديده
                if start_date and att.timestamp < start_date:
                    continue

                attendance_record = {
                    'user_id': str(att.user_id),
                    'timestamp': att.timestamp,
                    'punch_type': str(att.punch),
                    'verification_type': str(att.status) if hasattr(att, 'status') else None,
                }
                attendance_data.append(attendance_record)

            logger.info(f"تم سحب {len(attendance_data)} سجل حضور من جهاز {self.device.device_name}")
            return attendance_data

        except Exception as e:
            logger.error(f"خطأ في سحب بيانات الحضور: {str(e)}")
            return []

    def fetch_users(self) -> List[Dict]:
        """سحب قائمة المستخدمين من الجهاز"""
        if not self.connection:
            return []

        try:
            users = self.connection.get_users()
            user_data = []

            for user in users:
                user_record = {
                    'user_id': str(user.user_id),
                    'name': user.name,
                    'privilege': user.privilege,
                    'password': user.password,
                    'group_id': user.group_id,
                    'user_id_card': user.card if hasattr(user, 'card') else None,
                }
                user_data.append(user_record)

            logger.info(f"تم سحب {len(user_data)} مستخدم من جهاز {self.device.device_name}")
            return user_data

        except Exception as e:
            logger.error(f"خطأ في سحب قائمة المستخدمين: {str(e)}")
            return []

    def clear_attendance_data(self) -> bool:
        """مسح بيانات الحضور من الجهاز"""
        if not self.connection:
            return False

        try:
            self.connection.clear_attendance()
            logger.info(f"تم مسح بيانات الحضور من جهاز {self.device.device_name}")
            return True
        except Exception as e:
            logger.error(f"خطأ في مسح بيانات الحضور: {str(e)}")
            return False


class ZKDataProcessor:
    """معالج بيانات ZK"""

    @staticmethod
    def process_device_data(device: ZKDevice, force_sync: bool = False) -> AttendanceProcessingLog:
        """معالجة بيانات جهاز ZK محدد"""
        start_time = timezone.now()

        # تحديد تاريخ بداية السحب
        last_sync = device.last_sync
        if not force_sync and last_sync:
            start_date = last_sync
        else:
            # سحب بيانات آخر 30 يوم إذا لم يتم التحديد
            start_date = timezone.now() - timedelta(days=30)

        # إنشاء سجل معالجة
        log = AttendanceProcessingLog.objects.create(
            device=device,
            process_date=timezone.now().date(),
            status='failed'
        )

        try:
            # الاتصال بالجهاز
            manager = ZKDeviceManager(device)
            if not manager.connect():
                log.error_message = "فشل الاتصال بالجهاز"
                log.save()
                return log

            try:
                # سحب بيانات الحضور
                attendance_data = manager.fetch_attendance_data(start_date)
                log.records_fetched = len(attendance_data)

                # معالجة البيانات
                processed_count = 0
                failed_count = 0

                for record in attendance_data:
                    try:
                        ZKDataProcessor._process_single_record(device, record)
                        processed_count += 1
                    except Exception as e:
                        logger.error(f"خطأ في معالجة السجل: {str(e)}")
                        failed_count += 1

                # تحديث إحصائيات المعالجة
                log.records_processed = processed_count
                log.records_failed = failed_count

                if failed_count == 0:
                    log.status = 'success'
                elif processed_count > 0:
                    log.status = 'partial'

                # تحديث وقت آخر مزامنة
                device.last_sync = timezone.now()
                device.save()

            finally:
                manager.disconnect()

        except Exception as e:
            log.error_message = str(e)
            logger.error(f"خطأ في معالجة بيانات الجهاز {device.device_name}: {str(e)}")

        finally:
            # حساب وقت المعالجة
            end_time = timezone.now()
            log.processing_time = end_time - start_time
            log.save()

        return log

    @staticmethod
    def _process_single_record(device: ZKDevice, record: Dict):
        """معالجة سجل حضور واحد"""
        with transaction.atomic():
            # البحث عن الموظف المرتبط
            employee = None
            try:
                mapping = EmployeeDeviceMapping.objects.get(
                    device=device,
                    device_user_id=record['user_id'],
                    is_active=True
                )
                employee = mapping.employee
                mapping.last_used = timezone.now()
                mapping.save()
            except EmployeeDeviceMapping.DoesNotExist:
                logger.warning(f"لم يتم العثور على ربط للمستخدم {record['user_id']} في جهاز {device.device_name}")

            # إنشاء أو تحديث السجل الخام
            raw_record, created = ZKAttendanceRaw.objects.get_or_create(
                device=device,
                user_id=record['user_id'],
                timestamp=record['timestamp'],
                punch_type=record['punch_type'],
                defaults={
                    'employee': employee,
                    'verification_type': record.get('verification_type'),
                    'work_code': record.get('work_code'),
                    'is_processed': False
                }
            )

            if created and employee:
                # معالجة السجل لإنشاء سجل حضور
                ZKDataProcessor._create_attendance_record(raw_record)

    @staticmethod
    def _create_attendance_record(raw_record: ZKAttendanceRaw):
        """إنشاء سجل حضور من البيانات الخام"""
        if not raw_record.employee:
            return

        att_date = raw_record.timestamp.date()

        # البحث عن سجل الحضور لنفس اليوم أو إنشاء واحد جديد
        attendance, created = EmployeeAttendance.objects.get_or_create(
            emp=raw_record.employee,
            att_date=att_date,
            defaults={
                'status': 'Present',
                'rule_id': 1  # قاعدة افتراضية
            }
        )

        # تحديث أوقات الدخول والخروج حسب نوع البصمة
        if raw_record.punch_type in ['0', '4']:  # دخول أو دخول وقت إضافي
            if not attendance.check_in or raw_record.timestamp < attendance.check_in:
                attendance.check_in = raw_record.timestamp
        elif raw_record.punch_type in ['1', '5']:  # خروج أو خروج وقت إضافي
            if not attendance.check_out or raw_record.timestamp > attendance.check_out:
                attendance.check_out = raw_record.timestamp

        attendance.save()

        # تحديث حالة المعالجة
        raw_record.is_processed = True
        raw_record.save()

    @staticmethod
    def process_all_devices() -> List[AttendanceProcessingLog]:
        """معالجة جميع الأجهزة النشطة"""
        active_devices = ZKDevice.objects.filter(status='active')
        logs = []

        for device in active_devices:
            try:
                log = ZKDataProcessor.process_device_data(device)
                logs.append(log)
            except Exception as e:
                logger.error(f"خطأ في معالجة جهاز {device.device_name}: {str(e)}")

        return logs

    @staticmethod
    def sync_employee_mappings(device: ZKDevice) -> int:
        """مزامنة ربط الموظفين مع المستخدمين في الجهاز"""
        manager = ZKDeviceManager(device)
        if not manager.connect():
            return 0

        try:
            users = manager.fetch_users()
            synchronized_count = 0

            for user in users:
                try:
                    # البحث عن الموظف بناءً على كود الموظف
                    employee = Employee.objects.get(emp_code=user['user_id'])

                    # إنشاء أو تحديث الربط
                    mapping, created = EmployeeDeviceMapping.objects.get_or_create(
                        employee=employee,
                        device=device,
                        defaults={'device_user_id': user['user_id']}
                    )

                    if created:
                        synchronized_count += 1
                        logger.info(f"تم ربط الموظف {employee.emp_code} بجهاز {device.device_name}")

                except Employee.DoesNotExist:
                    logger.warning(f"لم يتم العثور على موظف برقم {user['user_id']}")
                except Exception as e:
                    logger.error(f"خطأ في ربط المستخدم {user['user_id']}: {str(e)}")

            return synchronized_count

        finally:
            manager.disconnect()


def test_device_connection(device_id: int) -> Dict:
    """اختبار الاتصال بجهاز ZK"""
    try:
        device = ZKDevice.objects.get(device_id=device_id)
        manager = ZKDeviceManager(device)

        result = {
            'device_name': device.device_name,
            'ip_address': device.ip_address,
            'connection_status': False,
            'error_message': None,
            'device_info': {}
        }

        if manager.connect():
            result['connection_status'] = True
            result['device_info'] = manager.get_device_info()
            manager.disconnect()
        else:
            result['error_message'] = "فشل الاتصال بالجهاز"

        return result

    except ZKDevice.DoesNotExist:
        return {
            'connection_status': False,
            'error_message': 'الجهاز غير موجود'
        }
    except Exception as e:
        return {
            'connection_status': False,
            'error_message': str(e)
        }


def manual_sync_device(device_id: int, days: int = 7) -> Dict:
    """مزامنة يدوية لجهاز محدد"""
    try:
        device = ZKDevice.objects.get(device_id=device_id)

        # تحديد تاريخ البداية
        start_date = timezone.now() - timedelta(days=days)

        # إنشاء سجل معالجة
        log = ZKDataProcessor.process_device_data(device, force_sync=True)

        return {
            'success': True,
            'device_name': device.device_name,
            'records_fetched': log.records_fetched,
            'records_processed': log.records_processed,
            'records_failed': log.records_failed,
            'status': log.status,
            'error_message': log.error_message
        }

    except ZKDevice.DoesNotExist:
        return {
            'success': False,
            'error_message': 'الجهاز غير موجود'
        }
    except Exception as e:
        return {
            'success': False,
            'error_message': str(e)
        }
