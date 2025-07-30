"""
حقول مشفرة مخصصة للنماذج
"""

from django.db import models
from django.core.exceptions import ValidationError
from Hr.services.encryption_service import encryption_service
import logging

logger = logging.getLogger(__name__)


class EncryptedCharField(models.CharField):
    """حقل نصي مشفر"""
    
    description = "حقل نصي مشفر للبيانات الحساسة"
    
    def __init__(self, *args, **kwargs):
        # زيادة الحد الأقصى للطول لاستيعاب البيانات المشفرة
        if 'max_length' in kwargs:
            kwargs['max_length'] = kwargs['max_length'] * 2  # مضاعفة الطول للتشفير
        
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك تشفير القيمة عند قراءتها من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            return encryption_service.decrypt_text(value)
        except Exception as e:
            logger.error(f"خطأ في فك تشفير الحقل: {e}")
            return value
    
    def to_python(self, value):
        """تحويل القيمة إلى Python"""
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """تشفير القيمة قبل حفظها في قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            return encryption_service.encrypt_text(str(value))
        except Exception as e:
            logger.error(f"خطأ في تشفير الحقل: {e}")
            return value


class EncryptedTextField(models.TextField):
    """حقل نص طويل مشفر"""
    
    description = "حقل نص طويل مشفر للبيانات الحساسة"
    
    def from_db_value(self, value, expression, connection):
        """فك تشفير القيمة عند قراءتها من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            return encryption_service.decrypt_text(value)
        except Exception as e:
            logger.error(f"خطأ في فك تشفير النص الطويل: {e}")
            return value
    
    def to_python(self, value):
        """تحويل القيمة إلى Python"""
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """تشفير القيمة قبل حفظها في قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            return encryption_service.encrypt_text(str(value))
        except Exception as e:
            logger.error(f"خطأ في تشفير النص الطويل: {e}")
            return value


class EncryptedEmailField(models.EmailField):
    """حقل بريد إلكتروني مشفر"""
    
    description = "حقل بريد إلكتروني مشفر"
    
    def __init__(self, *args, **kwargs):
        # زيادة الحد الأقصى للطول
        kwargs['max_length'] = kwargs.get('max_length', 254) * 2
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك تشفير القيمة عند قراءتها من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            return encryption_service.decrypt_text(value)
        except Exception as e:
            logger.error(f"خطأ في فك تشفير البريد الإلكتروني: {e}")
            return value
    
    def to_python(self, value):
        """تحويل القيمة إلى Python مع التحقق من صحة البريد الإلكتروني"""
        value = super().to_python(value)
        return value
    
    def get_prep_value(self, value):
        """تشفير القيمة قبل حفظها في قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            return encryption_service.encrypt_text(str(value))
        except Exception as e:
            logger.error(f"خطأ في تشفير البريد الإلكتروني: {e}")
            return value


class EncryptedPhoneField(models.CharField):
    """حقل رقم هاتف مشفر"""
    
    description = "حقل رقم هاتف مشفر"
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 20) * 2
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك تشفير القيمة عند قراءتها من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            return encryption_service.decrypt_text(value)
        except Exception as e:
            logger.error(f"خطأ في فك تشفير رقم الهاتف: {e}")
            return value
    
    def to_python(self, value):
        """تحويل القيمة إلى Python"""
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """تشفير القيمة قبل حفظها في قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            return encryption_service.encrypt_text(str(value))
        except Exception as e:
            logger.error(f"خطأ في تشفير رقم الهاتف: {e}")
            return value
    
    def validate(self, value, model_instance):
        """التحقق من صحة رقم الهاتف"""
        super().validate(value, model_instance)
        
        if value and not self._is_valid_phone(value):
            raise ValidationError('رقم هاتف غير صحيح')
    
    def _is_valid_phone(self, phone):
        """التحقق من صحة رقم الهاتف"""
        import re
        # نمط بسيط للتحقق من رقم الهاتف
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        return re.match(phone_pattern, phone.replace(' ', '').replace('-', ''))


class EncryptedDecimalField(models.DecimalField):
    """حقل رقم عشري مشفر (للرواتب والمبالغ المالية)"""
    
    description = "حقل رقم عشري مشفر للمبالغ المالية"
    
    def from_db_value(self, value, expression, connection):
        """فك تشفير القيمة عند قراءتها من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            decrypted_value = encryption_service.decrypt_text(value)
            return self.to_python(decrypted_value)
        except Exception as e:
            logger.error(f"خطأ في فك تشفير الرقم العشري: {e}")
            return value
    
    def get_prep_value(self, value):
        """تشفير القيمة قبل حفظها في قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            # تحويل إلى string أولاً
            string_value = str(value)
            return encryption_service.encrypt_text(string_value)
        except Exception as e:
            logger.error(f"خطأ في تشفير الرقم العشري: {e}")
            return value


class EncryptedJSONField(models.JSONField):
    """حقل JSON مشفر"""
    
    description = "حقل JSON مشفر للبيانات المعقدة"
    
    def from_db_value(self, value, expression, connection):
        """فك تشفير القيمة عند قراءتها من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            decrypted_json = encryption_service.decrypt_text(value)
            return self.to_python(decrypted_json)
        except Exception as e:
            logger.error(f"خطأ في فك تشفير JSON: {e}")
            return value
    
    def get_prep_value(self, value):
        """تشفير القيمة قبل حفظها في قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            import json
            json_string = json.dumps(value, ensure_ascii=False)
            return encryption_service.encrypt_text(json_string)
        except Exception as e:
            logger.error(f"خطأ في تشفير JSON: {e}")
            return value


class MaskedCharField(models.CharField):
    """حقل نصي مع إخفاء جزئي للبيانات الحساسة"""
    
    description = "حقل نصي مع إخفاء جزئي للعرض"
    
    def __init__(self, mask_char='*', visible_chars=4, *args, **kwargs):
        self.mask_char = mask_char
        self.visible_chars = visible_chars
        super().__init__(*args, **kwargs)
    
    def get_masked_value(self, value):
        """الحصول على القيمة المخفية جزئياً"""
        if not value:
            return value
        
        return encryption_service.mask_sensitive_data(
            value, 
            self.mask_char, 
            self.visible_chars
        )


class EncryptedFileField(models.FileField):
    """حقل ملف مشفر"""
    
    description = "حقل ملف مشفر للملفات الحساسة"
    
    def save_form_data(self, instance, data):
        """حفظ الملف مع التشفير"""
        if data is not None:
            # حفظ الملف الأصلي أولاً
            super().save_form_data(instance, data)
            
            # تشفير الملف
            if hasattr(instance, self.attname):
                file_field = getattr(instance, self.attname)
                if file_field and hasattr(file_field, 'path'):
                    try:
                        encrypted_path = encryption_service.encrypt_file(file_field.path)
                        
                        # تسجيل عملية التشفير
                        encryption_service.create_encryption_audit_log(
                            'encrypt_file', 
                            'employee_file'
                        )
                        
                    except Exception as e:
                        logger.error(f"خطأ في تشفير الملف: {e}")


class SecurePasswordField(models.CharField):
    """حقل كلمة مرور آمن"""
    
    description = "حقل كلمة مرور مع تشفير آمن"
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 128)
        super().__init__(*args, **kwargs)
    
    def get_prep_value(self, value):
        """تشفير كلمة المرور قبل حفظها"""
        if value is None:
            return value
        
        try:
            return encryption_service.hash_password(value)
        except Exception as e:
            logger.error(f"خطأ في تشفير كلمة المرور: {e}")
            return value
    
    def verify_password(self, raw_password, hashed_password):
        """التحقق من كلمة المرور"""
        try:
            return encryption_service.verify_password(raw_password, hashed_password)
        except Exception as e:
            logger.error(f"خطأ في التحقق من كلمة المرور: {e}")
            return False


class EncryptedModelMixin:
    """Mixin للنماذج التي تحتوي على بيانات مشفرة"""
    
    def get_encrypted_fields(self):
        """الحصول على قائمة الحقول المشفرة"""
        encrypted_fields = []
        
        for field in self._meta.fields:
            if isinstance(field, (
                EncryptedCharField, 
                EncryptedTextField, 
                EncryptedEmailField,
                EncryptedPhoneField,
                EncryptedDecimalField,
                EncryptedJSONField
            )):
                encrypted_fields.append(field.name)
        
        return encrypted_fields
    
    def get_decrypted_data(self):
        """الحصول على البيانات مفكوكة التشفير"""
        data = {}
        
        for field_name in self.get_encrypted_fields():
            value = getattr(self, field_name, None)
            if value is not None:
                data[field_name] = value  # القيمة ستكون مفكوكة التشفير تلقائياً
        
        return data
    
    def get_masked_data(self):
        """الحصول على البيانات مع الإخفاء الجزئي"""
        data = {}
        
        for field_name in self.get_encrypted_fields():
            value = getattr(self, field_name, None)
            if value is not None:
                data[field_name] = encryption_service.mask_sensitive_data(str(value))
        
        return data
    
    def audit_encryption_access(self, operation='read', user=None):
        """تسجيل الوصول للبيانات المشفرة"""
        try:
            encryption_service.create_encryption_audit_log(
                operation=operation,
                data_type=self.__class__.__name__,
                user_id=str(user.id) if user else None
            )
        except Exception as e:
            logger.error(f"خطأ في تسجيل تدقيق التشفير: {e}")


# دالة مساعدة لتحديث النماذج الموجودة
def add_encryption_to_existing_model(model_class, field_mappings):
    """إضافة التشفير للنماذج الموجودة"""
    
    def encrypt_existing_data():
        """تشفير البيانات الموجودة"""
        try:
            for instance in model_class.objects.all():
                updated = False
                
                for field_name, should_encrypt in field_mappings.items():
                    if should_encrypt and hasattr(instance, field_name):
                        current_value = getattr(instance, field_name)
                        
                        if current_value and not _is_encrypted(current_value):
                            encrypted_value = encryption_service.encrypt_text(current_value)
                            setattr(instance, field_name, encrypted_value)
                            updated = True
                
                if updated:
                    instance.save()
                    
            logger.info(f"تم تشفير البيانات الموجودة في {model_class.__name__}")
            
        except Exception as e:
            logger.error(f"خطأ في تشفير البيانات الموجودة: {e}")
    
    def _is_encrypted(value):
        """التحقق من كون القيمة مشفرة بالفعل"""
        try:
            encryption_service.decrypt_text(value)
            return True
        except:
            return False
    
    return encrypt_existing_data