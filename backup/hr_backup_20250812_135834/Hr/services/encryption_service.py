"""
خدمة تشفير البيانات الحساسة
"""

import base64
import hashlib
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.cache import cache
import os

logger = logging.getLogger(__name__)


class EncryptionService:
    """خدمة تشفير البيانات الحساسة"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_create_key(self):
        """الحصول على مفتاح التشفير أو إنشاؤه"""
        # محاولة الحصول على المفتاح من متغيرات البيئة
        key_from_env = os.environ.get('HR_ENCRYPTION_KEY')
        if key_from_env:
            return key_from_env.encode()
        
        # محاولة الحصول على المفتاح من الإعدادات
        key_from_settings = getattr(settings, 'HR_ENCRYPTION_KEY', None)
        if key_from_settings:
            return key_from_settings.encode()
        
        # إنشاء مفتاح جديد من كلمة مرور
        password = getattr(settings, 'SECRET_KEY', 'default_password').encode()
        salt = b'hr_system_salt_2024'  # يجب أن يكون ثابتاً لنفس البيانات
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_text(self, text):
        """تشفير النص"""
        if not text:
            return text
        
        try:
            if isinstance(text, str):
                text = text.encode('utf-8')
            
            encrypted_data = self.fernet.encrypt(text)
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        
        except Exception as e:
            logger.error(f'خطأ في تشفير النص: {e}')
            return text  # إرجاع النص الأصلي في حالة الخطأ
    
    def decrypt_text(self, encrypted_text):
        """فك تشفير النص"""
        if not encrypted_text:
            return encrypted_text
        
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
        
        except Exception as e:
            logger.error(f'خطأ في فك تشفير النص: {e}')
            return encrypted_text  # إرجاع النص المشفر في حالة الخطأ
    
    def encrypt_national_id(self, national_id):
        """تشفير رقم الهوية الوطنية"""
        if not national_id:
            return national_id
        
        # تنظيف رقم الهوية (إزالة المسافات والرموز)
        clean_id = ''.join(filter(str.isdigit, str(national_id)))
        
        if len(clean_id) < 10:  # التحقق من صحة رقم الهوية
            logger.warning(f'رقم هوية غير صحيح: {national_id}')
            return national_id
        
        return self.encrypt_text(clean_id)
    
    def decrypt_national_id(self, encrypted_id):
        """فك تشفير رقم الهوية الوطنية"""
        return self.decrypt_text(encrypted_id)
    
    def encrypt_phone_number(self, phone_number):
        """تشفير رقم الهاتف"""
        if not phone_number:
            return phone_number
        
        # تنظيف رقم الهاتف
        clean_phone = ''.join(filter(str.isdigit, str(phone_number)))
        
        if len(clean_phone) < 9:  # التحقق من صحة رقم الهاتف
            logger.warning(f'رقم هاتف غير صحيح: {phone_number}')
            return phone_number
        
        return self.encrypt_text(clean_phone)
    
    def decrypt_phone_number(self, encrypted_phone):
        """فك تشفير رقم الهاتف"""
        return self.decrypt_text(encrypted_phone)
    
    def encrypt_email(self, email):
        """تشفير البريد الإلكتروني"""
        if not email or '@' not in email:
            return email
        
        return self.encrypt_text(email.lower().strip())
    
    def decrypt_email(self, encrypted_email):
        """فك تشفير البريد الإلكتروني"""
        return self.decrypt_text(encrypted_email)
    
    def encrypt_salary(self, salary):
        """تشفير الراتب"""
        if not salary:
            return salary
        
        try:
            # تحويل إلى نص للتشفير
            salary_str = str(float(salary))
            return self.encrypt_text(salary_str)
        except (ValueError, TypeError) as e:
            logger.error(f'خطأ في تشفير الراتب: {e}')
            return salary
    
    def decrypt_salary(self, encrypted_salary):
        """فك تشفير الراتب"""
        decrypted = self.decrypt_text(encrypted_salary)
        if decrypted:
            try:
                return float(decrypted)
            except (ValueError, TypeError):
                return None
        return None
    
    def encrypt_bank_account(self, account_number):
        """تشفير رقم الحساب البنكي"""
        if not account_number:
            return account_number
        
        # تنظيف رقم الحساب
        clean_account = ''.join(filter(str.isalnum, str(account_number)))
        
        if len(clean_account) < 8:  # التحقق من صحة رقم الحساب
            logger.warning(f'رقم حساب بنكي غير صحيح: {account_number}')
            return account_number
        
        return self.encrypt_text(clean_account)
    
    def decrypt_bank_account(self, encrypted_account):
        """فك تشفير رقم الحساب البنكي"""
        return self.decrypt_text(encrypted_account)
    
    def hash_password(self, password):
        """تشفير كلمة المرور بـ hash"""
        if not password:
            return password
        
        # استخدام SHA-256 مع salt
        salt = settings.SECRET_KEY.encode('utf-8')
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # عدد التكرارات
        )
        
        return base64.urlsafe_b64encode(password_hash).decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """التحقق من كلمة المرور"""
        if not password or not hashed_password:
            return False
        
        try:
            return self.hash_password(password) == hashed_password
        except Exception as e:
            logger.error(f'خطأ في التحقق من كلمة المرور: {e}')
            return False
    
    def encrypt_sensitive_data(self, data_dict):
        """تشفير البيانات الحساسة في قاموس"""
        if not isinstance(data_dict, dict):
            return data_dict
        
        sensitive_fields = {
            'national_id': self.encrypt_national_id,
            'phone_number': self.encrypt_phone_number,
            'mobile_number': self.encrypt_phone_number,
            'email': self.encrypt_email,
            'personal_email': self.encrypt_email,
            'salary': self.encrypt_salary,
            'basic_salary': self.encrypt_salary,
            'bank_account': self.encrypt_bank_account,
            'account_number': self.encrypt_bank_account,
        }
        
        encrypted_data = data_dict.copy()
        
        for field, encrypt_func in sensitive_fields.items():
            if field in encrypted_data and encrypted_data[field]:
                try:
                    encrypted_data[field] = encrypt_func(encrypted_data[field])
                except Exception as e:
                    logger.error(f'خطأ في تشفير الحقل {field}: {e}')
        
        return encrypted_data
    
    def decrypt_sensitive_data(self, data_dict):
        """فك تشفير البيانات الحساسة في قاموس"""
        if not isinstance(data_dict, dict):
            return data_dict
        
        sensitive_fields = {
            'national_id': self.decrypt_national_id,
            'phone_number': self.decrypt_phone_number,
            'mobile_number': self.decrypt_phone_number,
            'email': self.decrypt_email,
            'personal_email': self.decrypt_email,
            'salary': self.decrypt_salary,
            'basic_salary': self.decrypt_salary,
            'bank_account': self.decrypt_bank_account,
            'account_number': self.decrypt_bank_account,
        }
        
        decrypted_data = data_dict.copy()
        
        for field, decrypt_func in sensitive_fields.items():
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = decrypt_func(decrypted_data[field])
                except Exception as e:
                    logger.error(f'خطأ في فك تشفير الحقل {field}: {e}')
        
        return decrypted_data
    
    def is_encrypted(self, text):
        """التحقق من كون النص مشفراً"""
        if not text or not isinstance(text, str):
            return False
        
        try:
            # محاولة فك التشفير
            base64.urlsafe_b64decode(text.encode('utf-8'))
            return True
        except Exception:
            return False
    
    def encrypt_file_content(self, file_content):
        """تشفير محتوى الملف"""
        if not file_content:
            return file_content
        
        try:
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
            
            encrypted_content = self.fernet.encrypt(file_content)
            return base64.urlsafe_b64encode(encrypted_content)
        
        except Exception as e:
            logger.error(f'خطأ في تشفير محتوى الملف: {e}')
            return file_content
    
    def decrypt_file_content(self, encrypted_content):
        """فك تشفير محتوى الملف"""
        if not encrypted_content:
            return encrypted_content
        
        try:
            if isinstance(encrypted_content, str):
                encrypted_content = encrypted_content.encode('utf-8')
            
            decoded_content = base64.urlsafe_b64decode(encrypted_content)
            decrypted_content = self.fernet.decrypt(decoded_content)
            return decrypted_content
        
        except Exception as e:
            logger.error(f'خطأ في فك تشفير محتوى الملف: {e}')
            return encrypted_content
    
    def generate_secure_token(self, length=32):
        """إنتاج رمز آمن عشوائي"""
        import secrets
        return secrets.token_urlsafe(length)
    
    def mask_sensitive_data(self, text, mask_char='*', visible_chars=2):
        """إخفاء البيانات الحساسة للعرض"""
        if not text or len(text) <= visible_chars * 2:
            return text
        
        visible_start = text[:visible_chars]
        visible_end = text[-visible_chars:]
        masked_middle = mask_char * (len(text) - visible_chars * 2)
        
        return f'{visible_start}{masked_middle}{visible_end}'
    
    def get_encryption_status(self):
        """الحصول على حالة التشفير"""
        return {
            'encryption_enabled': True,
            'key_source': 'environment' if os.environ.get('HR_ENCRYPTION_KEY') else 'generated',
            'algorithm': 'Fernet (AES 128)',
            'key_derivation': 'PBKDF2-HMAC-SHA256'
        }


# إنشاء مثيل الخدمة
encryption_service = EncryptionService()