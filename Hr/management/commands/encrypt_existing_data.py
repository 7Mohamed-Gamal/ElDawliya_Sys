"""
أمر تشفير البيانات الموجودة
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps
from Hr.services.encryption_service import encryption_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'تشفير البيانات الحساسة الموجودة في قاعدة البيانات'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='تشفير نموذج محدد (مثل: Employee)'
        )
        parser.add_argument(
            '--field',
            type=str,
            help='تشفير حقل محدد في النموذج'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='تشغيل تجريبي بدون حفظ التغييرات'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='حجم الدفعة للمعالجة (افتراضي: 100)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='إجبار إعادة التشفير حتى للبيانات المشفرة'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== بدء تشفير البيانات الموجودة ===')
        )

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('تشغيل تجريبي - لن يتم حفظ التغييرات')
            )

        # تعريف النماذج والحقول الحساسة
        sensitive_data_mapping = {
            'Employee': {
                'national_id': True,
                'passport_number': True,
                'phone_number': True,
                'personal_email': True,
                'bank_account_number': True,
                'iban': True,
                'tax_number': True,
                'social_security_number': True,
            },
            'EmployeeEmergencyContact': {
                'phone_number': True,
                'email': True,
            },
            'EmployeeInsurance': {
                'policy_number': True,
                'insurance_number': True,
            },
            'PayrollRecord': {
                'bank_account_number': True,
                'iban': True,
            }
        }

        total_encrypted = 0

        try:
            if options['model']:
                # تشفير نموذج محدد
                model_name = options['model']
                if model_name in sensitive_data_mapping:
                    encrypted_count = self.encrypt_model_data(
                        model_name,
                        sensitive_data_mapping[model_name],
                        options
                    )
                    total_encrypted += encrypted_count
                else:
                    self.stdout.write(
                        self.style.ERROR(f'النموذج {model_name} غير مدعوم')
                    )
            else:
                # تشفير جميع النماذج
                for model_name, field_mapping in sensitive_data_mapping.items():
                    encrypted_count = self.encrypt_model_data(
                        model_name,
                        field_mapping,
                        options
                    )
                    total_encrypted += encrypted_count

            # عرض النتائج
            self.stdout.write('\n' + self.style.SUCCESS('=== ملخص التشفير ==='))
            self.stdout.write(f'إجمالي السجلات المشفرة: {total_encrypted}')
            
            if not options['dry_run']:
                self.stdout.write(
                    self.style.SUCCESS('تم تشفير البيانات بنجاح!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('تشغيل تجريبي - لم يتم حفظ التغييرات')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطأ في عملية التشفير: {e}')
            )
            logger.error(f'خطأ في تشفير البيانات: {e}')

    def encrypt_model_data(self, model_name, field_mapping, options):
        """تشفير بيانات نموذج محدد"""
        try:
            # الحصول على النموذج
            model_class = apps.get_model('Hr', model_name)
            
            self.stdout.write(f'\nمعالجة نموذج: {model_name}')
            
            # الحصول على جميع السجلات
            queryset = model_class.objects.all()
            total_records = queryset.count()
            
            if total_records == 0:
                self.stdout.write('  لا توجد سجلات للمعالجة')
                return 0
            
            self.stdout.write(f'  إجمالي السجلات: {total_records}')
            
            encrypted_count = 0
            batch_size = options['batch_size']
            
            # معالجة البيانات على دفعات
            for i in range(0, total_records, batch_size):
                batch = queryset[i:i + batch_size]
                batch_encrypted = self.encrypt_batch(
                    batch, 
                    field_mapping, 
                    options
                )
                encrypted_count += batch_encrypted
                
                # عرض التقدم
                progress = min(i + batch_size, total_records)
                self.stdout.write(
                    f'  تم معالجة: {progress}/{total_records} '
                    f'({progress/total_records*100:.1f}%)'
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'  تم تشفير {encrypted_count} سجل في {model_name}')
            )
            
            return encrypted_count
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطأ في معالجة {model_name}: {e}')
            )
            return 0

    def encrypt_batch(self, batch, field_mapping, options):
        """تشفير دفعة من السجلات"""
        encrypted_count = 0
        
        try:
            with transaction.atomic():
                for instance in batch:
                    instance_updated = False
                    
                    # معالجة كل حقل حساس
                    for field_name, should_encrypt in field_mapping.items():
                        if not should_encrypt:
                            continue
                        
                        # التحقق من وجود الحقل في النموذج
                        if not hasattr(instance, field_name):
                            continue
                        
                        # معالجة حقل محدد إذا تم تحديده
                        if options['field'] and options['field'] != field_name:
                            continue
                        
                        current_value = getattr(instance, field_name)
                        
                        # تخطي القيم الفارغة
                        if not current_value:
                            continue
                        
                        # التحقق من كون البيانات مشفرة بالفعل
                        if not options['force'] and self.is_encrypted(current_value):
                            continue
                        
                        # تشفير القيمة
                        try:
                            encrypted_value = encryption_service.encrypt_text(str(current_value))
                            setattr(instance, field_name, encrypted_value)
                            instance_updated = True
                            
                            if options['dry_run']:
                                self.stdout.write(
                                    f'    [تجريبي] سيتم تشفير {field_name}: '
                                    f'{self.mask_value(current_value)}'
                                )
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'    خطأ في تشفير {field_name} للسجل {instance.id}: {e}'
                                )
                            )
                    
                    # حفظ السجل إذا تم تحديثه
                    if instance_updated:
                        if not options['dry_run']:
                            instance.save()
                            
                            # تسجيل عملية التشفير
                            encryption_service.create_encryption_audit_log(
                                'encrypt_existing_data',
                                instance.__class__.__name__
                            )
                        
                        encrypted_count += 1
                
                # إلغاء المعاملة في حالة التشغيل التجريبي
                if options['dry_run']:
                    transaction.set_rollback(True)
            
            return encrypted_count
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطأ في معالجة الدفعة: {e}')
            )
            return 0

    def is_encrypted(self, value):
        """التحقق من كون القيمة مشفرة بالفعل"""
        try:
            # محاولة فك التشفير
            decrypted = encryption_service.decrypt_text(value)
            # إذا نجح فك التشفير، فالقيمة مشفرة
            return True
        except:
            # إذا فشل فك التشفير، فالقيمة غير مشفرة
            return False

    def mask_value(self, value):
        """إخفاء القيمة جزئياً للعرض"""
        if not value:
            return value
        
        return encryption_service.mask_sensitive_data(str(value))

    def verify_encryption(self, model_name, field_mapping):
        """التحقق من صحة التشفير"""
        try:
            model_class = apps.get_model('Hr', model_name)
            
            self.stdout.write(f'\nالتحقق من تشفير {model_name}...')
            
            sample_size = min(10, model_class.objects.count())
            sample_records = model_class.objects.all()[:sample_size]
            
            verification_results = {
                'total_checked': 0,
                'encrypted_fields': 0,
                'decryption_successful': 0,
                'errors': 0
            }
            
            for instance in sample_records:
                verification_results['total_checked'] += 1
                
                for field_name, should_encrypt in field_mapping.items():
                    if not should_encrypt or not hasattr(instance, field_name):
                        continue
                    
                    current_value = getattr(instance, field_name)
                    if not current_value:
                        continue
                    
                    verification_results['encrypted_fields'] += 1
                    
                    try:
                        # محاولة فك التشفير
                        decrypted = encryption_service.decrypt_text(current_value)
                        verification_results['decryption_successful'] += 1
                        
                    except Exception as e:
                        verification_results['errors'] += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'  خطأ في فك تشفير {field_name}: {e}'
                            )
                        )
            
            # عرض نتائج التحقق
            self.stdout.write(f'  السجلات المفحوصة: {verification_results["total_checked"]}')
            self.stdout.write(f'  الحقول المشفرة: {verification_results["encrypted_fields"]}')
            self.stdout.write(f'  فك التشفير الناجح: {verification_results["decryption_successful"]}')
            self.stdout.write(f'  الأخطاء: {verification_results["errors"]}')
            
            if verification_results['errors'] == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ التحقق من {model_name} مكتمل بنجاح')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ يوجد أخطاء في تشفير {model_name}')
                )
            
            return verification_results
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطأ في التحقق من {model_name}: {e}')
            )
            return None