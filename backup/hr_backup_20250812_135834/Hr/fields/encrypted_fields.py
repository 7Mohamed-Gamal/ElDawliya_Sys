"""
حقول قاعدة البيانات المشفرة
"""

from django.db import models
from django.core.exceptions import ValidationError
from Hr.services.encryption_service import encryption_service
import logging

logger = logging.getLogger(__name__)


class EncryptedTextField(models.TextField):
    """حقل نص مشفر"""
    
    description = "حقل نص مشفر"
    
    def __init__(self, *args, **kwargs):
        self.encrypt_on_save = kwargs.pop('encrypt_on_save', True)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك التشفير عند القراءة من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            # التحقق من كون القيمة مشفرة
            if encryption_service.is_encrypted(value):
                return encryption_service.decrypt_text(value)
            return value
        except Exception as e:
            logger.error(f'خطأ في فك تشفير النص: {e}')
            return value
    
    def to_python(self, value):
        """تحويل القيمة إلى Python"""
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """تحضير القيمة للحفظ في قاعدة البيانات"""
        if value is None:
            return value
        
        if self.encrypt_on_save and value:
            try:
                # تشفير القيمة إذا لم تكن مشفرة بالفعل
                if not encryption_service.is_encrypted(str(value)):
                    return encryption_service.encrypt_text(str(value))
            except Exception as e:
                logger.error(f'خطأ في تشفير النص: {e}')
        
        return str(value)


class EncryptedCharField(models.CharField):
    """حقل نص قصير مشفر"""
    
    description = "حقل نص قصير مشفر"
    
    def __init__(self, *args, **kwargs):
        self.encrypt_on_save = kwargs.pop('encrypt_on_save', True)
        # زيادة الحد الأقصى للطول لاستيعاب التشفير
        if 'max_length' in kwargs:
            kwargs['max_length'] = max(kwargs['max_length'] * 2, 255)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك التشفير عند القراءة من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            if encryption_service.is_encrypted(value):
                return encryption_service.decrypt_text(value)
            return value
        except Exception as e:
            logger.error(f'خطأ في فك تشفير النص: {e}')
            return value
    
    def to_python(self, value):
        """تحويل القيمة إلى Python"""
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """تحضير القيمة للحفظ في قاعدة البيانات"""
        if value is None:
            return value
        
        if self.encrypt_on_save and value:
            try:
                if not encryption_service.is_encrypted(str(value)):
                    return encryption_service.encrypt_text(str(value))
            except Exception as e:
                logger.error(f'خطأ في تشفير النص: {e}')
        
        return str(value)


class EncryptedNationalIDField(EncryptedCharField):
    """حقل رقم الهوية الوطنية المشفر"""
    
    description = "حقل رقم الهوية الوطنية المشفر"
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك التشفير عند القراءة من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            if encryption_service.is_encrypted(value):
                return encryption_service.decrypt_national_id(value)
            return value
        except Exception as e:
            logger.error(f'خطأ في فك تشفير رقم الهوية: {e}')
            return value
    
    def get_prep_value(self, value):
        """تحضير القيمة للحفظ في قاعدة البيانات"""
        if value is None:
            return value
        
        if self.encrypt_on_save and value:
            try:
                if not encryption_service.is_encrypted(str(value)):
                    return encryption_service.encrypt_national_id(str(value))
            except Exception as e:
                logger.error(f'خطأ في تشفير رقم الهوية: {e}')
        
        return str(value)
    
    def validate(self, value, model_instance):
        """التحقق من صحة رقم الهوية"""
        super().validate(value, model_instance)
        
        if value:
            # فك التشفير للتحقق من الصحة
            decrypted_value = value
            if encryption_service.is_encrypted(str(value)):
                decrypted_value = encryption_service.decrypt_national_id(str(value))
            
            # التحقق من صحة رقم الهوية
            clean_id = ''.join(filter(str.isdigit, str(decrypted_value)))
            if len(clean_id) < 10:
                raise ValidationError('رقم الهوية الوطنية يجب أن يكون 10 أرقام على الأقل')


class EncryptedPhoneField(EncryptedCharField):
    """حقل رقم الهاتف المشفر"""
    
    description = "حقل رقم الهاتف المشفر"
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك التشفير عند القراءة من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            if encryption_service.is_encrypted(value):
                return encryption_service.decrypt_phone_number(value)
            return value
        except Exception as e:
            logger.error(f'خطأ في فك تشفير رقم الهاتف: {e}')
            return value
    
    def get_prep_value(self, value):
        """تحضير القيمة للحفظ في قاعدة البيانات"""
        if value is None:
            return value
        
        if self.encrypt_on_save and value:
            try:
                if not encryption_service.is_encrypted(str(value)):
                    return encryption_service.encrypt_phone_number(str(value))
            except Exception as e:
                logger.error(f'خطأ في تشفير رقم الهاتف: {e}')
        
        return str(value)
    
    def validate(self, value, model_instance):
        """التحقق من صحة رقم الهاتف"""
        super().validate(value, model_instance)
        
        if value:
            # فك التشفير للتحقق من الصحة
            decrypted_value = value
            if encryption_service.is_encrypted(str(value)):
                decrypted_value = encryption_service.decrypt_phone_number(str(value))
            
            # التحقق من صحة رقم الهاتف
            clean_phone = ''.join(filter(str.isdigit, str(decrypted_value)))
            if len(clean_phone) < 9:
                raise ValidationError('رقم الهاتف يجب أن يكون 9 أرقام على الأقل')


class EncryptedEmailField(models.EmailField):
    """حقل البريد الإلكتروني المشفر"""
    
    description = "حقل البريد الإلكتروني المشفر"
    
    def __init__(self, *args, **kwargs):
        self.encrypt_on_save = kwargs.pop('encrypt_on_save', True)
        kwargs.setdefault('max_length', 255)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك التشفير عند القراءة من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            if encryption_service.is_encrypted(value):
                return encryption_service.decrypt_email(value)
            return value
        except Exception as e:
            logger.error(f'خطأ في فك تشفير البريد الإلكتروني: {e}')
            return value
    
    def to_python(self, value):
        """تحويل القيمة إلى Python"""
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """تحضير القيمة للحفظ في قاعدة البيانات"""
        if value is None:
            return value
        
        if self.encrypt_on_save and value:
            try:
                if not encryption_service.is_encrypted(str(value)):
                    return encryption_service.encrypt_email(str(value))
            except Exception as e:
                logger.error(f'خطأ في تشفير البريد الإلكتروني: {e}')
        
        return str(value)


class EncryptedDecimalField(models.DecimalField):
    """حقل رقم عشري مشفر (للرواتب)"""
    
    description = "حقل رقم عشري مشفر"
    
    def __init__(self, *args, **kwargs):
        self.encrypt_on_save = kwargs.pop('encrypt_on_save', True)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك التشفير عند القراءة من قاعدة البيانات"""
        if value is None:
            return value
        
        # إذا كانت القيمة نص (مشفرة)
        if isinstance(value, str):
            try:
                if encryption_service.is_encrypted(value):
                    decrypted = encryption_service.decrypt_salary(value)
                    return self.to_python(decrypted)
                return self.to_python(value)
            except Exception as e:
                logger.error(f'خطأ في فك تشفير الراتب: {e}')
                return value
        
        return value
    
    def get_prep_value(self, value):
        """تحضير القيمة للحفظ في قاعدة البيانات"""
        if value is None:
            return value
        
        if self.encrypt_on_save and value:
            try:
                # تحويل إلى نص وتشفير
                return encryption_service.encrypt_salary(value)
            except Exception as e:
                logger.error(f'خطأ في تشفير الراتب: {e}')
        
        return super().get_prep_value(value)


class EncryptedBankAccountField(EncryptedCharField):
    """حقل رقم الحساب البنكي المشفر"""
    
    description = "حقل رقم الحساب البنكي المشفر"
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """فك التشفير عند القراءة من قاعدة البيانات"""
        if value is None:
            return value
        
        try:
            if encryption_service.is_encrypted(value):
                return encryption_service.decrypt_bank_account(value)
            return value
        except Exception as e:
            logger.error(f'خطأ في فك تشفير رقم الحساب البنكي: {e}')
            return value
    
    def get_prep_value(self, value):
        """تحضير القيمة للحفظ في قاعدة البيانات"""
        if value is None:
            return value
        
        if self.encrypt_on_save and value:
            try:
                if not encryption_service.is_encrypted(str(value)):
                    return encryption_service.encrypt_bank_account(str(value))
            except Exception as e:
                logger.error(f'خطأ في تشفير رقم الحساب البنكي: {e}')
        
        return str(value)
    
    def validate(self, value, model_instance):
        """التحقق من صحة رقم الحساب البنكي"""
        super().validate(value, model_instance)
        
        if value:
            # فك التشفير للتحقق من الصحة
            decrypted_value = value
            if encryption_service.is_encrypted(str(value)):
                decrypted_value = encryption_service.decrypt_bank_account(str(value))
            
            # التحقق من صحة رقم الحساب
            clean_account = ''.join(filter(str.isalnum, str(decrypted_value)))
            if len(clean_account) < 8:
                raise ValidationError('رقم الحساب البنكي يجب أن يكون 8 أحرف/أرقام على الأقل')


class EncryptedFileField(models.FileField):
    """حقل ملف مشفر"""
    
    description = "حقل ملف مشفر"
    
    def __init__(self, *args, **kwargs):
        self.encrypt_content = kwargs.pop('encrypt_content', True)
        super().__init__(*args, **kwargs)
    
    def save_form_data(self, instance, data):
        """حفظ بيانات النموذج مع التشفير"""
        if data and self.encrypt_content:
            try:
                # قراءة محتوى الملف
                content = data.read()
                
                # تشفير المحتوى
                encrypted_content = encryption_service.encrypt_file_content(content)
                
                # إنشاء ملف جديد بالمحتوى المشفر
                from django.core.files.base import ContentFile
                encrypted_file = ContentFile(encrypted_content, name=data.name)
                
                super().save_form_data(instance, encrypted_file)
            except Exception as e:
                logger.error(f'خطأ في تشفير الملف: {e}')
                super().save_form_data(instance, data)
        else:
            super().save_form_data(instance, data)


# دالة مساعدة لإنشاء حقل مشفر حسب النوع
def create_encrypted_field(field_type, **kwargs):
    """إنشاء حقل مشفر حسب النوع"""
    field_mapping = {
        'text': EncryptedTextField,
        'char': EncryptedCharField,
        'national_id': EncryptedNationalIDField,
        'phone': EncryptedPhoneField,
        'email': EncryptedEmailField,
        'decimal': EncryptedDecimalField,
        'bank_account': EncryptedBankAccountField,
        'file': EncryptedFileField,
    }
    
    field_class = field_mapping.get(field_type, EncryptedTextField)
    return field_class(**kwargs)