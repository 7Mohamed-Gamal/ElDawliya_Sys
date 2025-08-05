"""
أمر تشفير البيانات الموجودة
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from Hr.services.encryption_service import encryption_service
from Hr.models import Employee
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'تشفير البيانات الحساسة الموجودة في قاعدة البيانات'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            choices=['employee', 'all'],
            default='all',
            help='النموذج المراد تشفير بياناته'
        )
        
        parser.add_argument(
            '--field',
            type=str,
            help='الحقل المحدد للتشفير (اختياري)'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='حجم الدفعة للمعالجة (افتراضي: 100)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='تشغيل تجريبي بدون حفظ التغييرات'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='إجبار التشفير حتى لو كانت البيانات مشفرة'
        )

    def handle(self, *args, **options):
        model = options['model']
        field = options['field']
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        force = options['force']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('تشغيل تجريبي - لن يتم حفظ التغييرات')
            )
        
        if model == 'employee' or model == 'all':
            self.encrypt_employee_data(field, batch_size, dry_run, force)
        
        if model == 'all':
            # يمكن إضافة نماذج أخرى هنا
            pass
        
        self.stdout.write(
            self.style.SUCCESS('تم الانتهاء من عملية التشفير')
        )

    def encrypt_employee_data(self, specific_field, batch_size, dry_run, force):
        """تشفير بيانات الموظفين"""
        self.stdout.write(
            self.style.SUCCESS('بدء تشفير بيانات الموظفين...')
        )
        
        # الحقول الحساسة في نموذج الموظف
        sensitive_fields = {
            'national_id': 'رقم الهوية الوطنية',
            'phone_number': 'رقم الهاتف',
            'mobile_number': 'رقم الجوال',
            'personal_email': 'البريد الإلكتروني الشخصي',
            'emergency_contact_phone': 'هاتف جهة الاتصال الطارئة',
        }
        
        # تحديد الحقول المراد تشفيرها
        fields_to_encrypt = {}
        if specific_field:
            if specific_field in sensitive_fields:
                fields_to_encrypt[specific_field] = sensitive_fields[specific_field]
            else:
                self.stdout.write(
                    self.style.ERROR(f'الحقل {specific_field} غير موجود في القائمة الحساسة')
                )
                return
        else:
            fields_to_encrypt = sensitive_fields
        
        # الحصول على جميع الموظفين
        total_employees = Employee.objects.count()
        self.stdout.write(f'إجمالي الموظفين: {total_employees}')
        
        encrypted_count = 0
        skipped_count = 0
        error_count = 0
        
        # معالجة على دفعات
        for start in range(0, total_employees, batch_size):
            end = min(start + batch_size, total_employees)
            employees = Employee.objects.all()[start:end]
            
            self.stdout.write(
                f'معالجة الدفعة {start//batch_size + 1}: '
                f'الموظفين {start + 1} إلى {end}'
            )
            
            with transaction.atomic():
                for employee in employees:
                    try:
                        updated = False
                        
                        for field_name, field_desc in fields_to_encrypt.items():
                            if hasattr(employee, field_name):
                                current_value = getattr(employee, field_name)
                                
                                if current_value:
                                    # التحقق من كون البيانات مشفرة بالفعل
                                    if not force and encryption_service.is_encrypted(str(current_value)):
                                        self.stdout.write(
                                            f'  تم تخطي {field_desc} للموظف {employee.employee_id} - مشفر بالفعل'
                                        )
                                        skipped_count += 1
                                        continue
                                    
                                    # تشفير البيانات
                                    encrypted_value = self.encrypt_field_value(
                                        field_name, current_value
                                    )
                                    
                                    if encrypted_value != current_value:
                                        if not dry_run:
                                            setattr(employee, field_name, encrypted_value)
                                            updated = True
                                        
                                        self.stdout.write(
                                            f'  تم تشفير {field_desc} للموظف {employee.employee_id}'
                                        )
                                        encrypted_count += 1
                        
                        # حفظ التغييرات
                        if updated and not dry_run:
                            employee.save(update_fields=list(fields_to_encrypt.keys()))
                    
                    except Exception as e:
                        error_count += 1
                        logger.error(
                            f'خطأ في تشفير بيانات الموظف {employee.employee_id}: {e}'
                        )
                        self.stdout.write(
                            self.style.ERROR(
                                f'  خطأ في معالجة الموظف {employee.employee_id}: {e}'
                            )
                        )
                
                # إذا كان تشغيل تجريبي، تراجع عن المعاملة
                if dry_run:
                    transaction.set_rollback(True)
        
        # ملخص النتائج
        self.stdout.write(
            self.style.SUCCESS(
                f'\\nملخص تشفير بيانات الموظفين:'
                f'\\n  تم التشفير: {encrypted_count}'
                f'\\n  تم التخطي: {skipped_count}'
                f'\\n  أخطاء: {error_count}'
            )
        )

    def encrypt_field_value(self, field_name, value):
        """تشفير قيمة حقل محدد"""
        try:
            if field_name == 'national_id':
                return encryption_service.encrypt_national_id(value)
            elif field_name in ['phone_number', 'mobile_number', 'emergency_contact_phone']:
                return encryption_service.encrypt_phone_number(value)
            elif field_name == 'personal_email':
                return encryption_service.encrypt_email(value)
            else:
                return encryption_service.encrypt_text(value)
        except Exception as e:
            logger.error(f'خطأ في تشفير الحقل {field_name}: {e}')
            return value

    def decrypt_employee_data(self, specific_field, batch_size, dry_run):
        """فك تشفير بيانات الموظفين (للاختبار)"""
        self.stdout.write(
            self.style.WARNING('بدء فك تشفير بيانات الموظفين...')
        )
        
        sensitive_fields = {
            'national_id': 'رقم الهوية الوطنية',
            'phone_number': 'رقم الهاتف',
            'mobile_number': 'رقم الجوال',
            'personal_email': 'البريد الإلكتروني الشخصي',
            'emergency_contact_phone': 'هاتف جهة الاتصال الطارئة',
        }
        
        fields_to_decrypt = {}
        if specific_field:
            if specific_field in sensitive_fields:
                fields_to_decrypt[specific_field] = sensitive_fields[specific_field]
            else:
                self.stdout.write(
                    self.style.ERROR(f'الحقل {specific_field} غير موجود في القائمة الحساسة')
                )
                return
        else:
            fields_to_decrypt = sensitive_fields
        
        total_employees = Employee.objects.count()
        decrypted_count = 0
        error_count = 0
        
        for start in range(0, total_employees, batch_size):
            end = min(start + batch_size, total_employees)
            employees = Employee.objects.all()[start:end]
            
            with transaction.atomic():
                for employee in employees:
                    try:
                        updated = False
                        
                        for field_name, field_desc in fields_to_decrypt.items():
                            if hasattr(employee, field_name):
                                current_value = getattr(employee, field_name)
                                
                                if current_value and encryption_service.is_encrypted(str(current_value)):
                                    # فك التشفير
                                    decrypted_value = self.decrypt_field_value(
                                        field_name, current_value
                                    )
                                    
                                    if decrypted_value != current_value:
                                        if not dry_run:
                                            setattr(employee, field_name, decrypted_value)
                                            updated = True
                                        
                                        self.stdout.write(
                                            f'  تم فك تشفير {field_desc} للموظف {employee.employee_id}'
                                        )
                                        decrypted_count += 1
                        
                        if updated and not dry_run:
                            employee.save(update_fields=list(fields_to_decrypt.keys()))
                    
                    except Exception as e:
                        error_count += 1
                        logger.error(
                            f'خطأ في فك تشفير بيانات الموظف {employee.employee_id}: {e}'
                        )
                
                if dry_run:
                    transaction.set_rollback(True)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\\nملخص فك تشفير بيانات الموظفين:'
                f'\\n  تم فك التشفير: {decrypted_count}'
                f'\\n  أخطاء: {error_count}'
            )
        )

    def decrypt_field_value(self, field_name, value):
        """فك تشفير قيمة حقل محدد"""
        try:
            if field_name == 'national_id':
                return encryption_service.decrypt_national_id(value)
            elif field_name in ['phone_number', 'mobile_number', 'emergency_contact_phone']:
                return encryption_service.decrypt_phone_number(value)
            elif field_name == 'personal_email':
                return encryption_service.decrypt_email(value)
            else:
                return encryption_service.decrypt_text(value)
        except Exception as e:
            logger.error(f'خطأ في فك تشفير الحقل {field_name}: {e}')
            return value

    def verify_encryption(self):
        """التحقق من صحة التشفير"""
        self.stdout.write(
            self.style.SUCCESS('التحقق من صحة التشفير...')
        )
        
        # اختبار عينة من الموظفين
        sample_employees = Employee.objects.all()[:10]
        
        for employee in sample_employees:
            self.stdout.write(f'\\nالموظف: {employee.employee_id}')
            
            # فحص الحقول الحساسة
            sensitive_fields = ['national_id', 'phone_number', 'personal_email']
            
            for field_name in sensitive_fields:
                if hasattr(employee, field_name):
                    value = getattr(employee, field_name)
                    if value:
                        is_encrypted = encryption_service.is_encrypted(str(value))
                        status = 'مشفر' if is_encrypted else 'غير مشفر'
                        self.stdout.write(f'  {field_name}: {status}')
                        
                        # محاولة فك التشفير للتأكد
                        if is_encrypted:
                            try:
                                decrypted = self.decrypt_field_value(field_name, value)
                                masked = encryption_service.mask_sensitive_data(decrypted)
                                self.stdout.write(f'    القيمة المفكوكة: {masked}')
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(f'    خطأ في فك التشفير: {e}')
                                )