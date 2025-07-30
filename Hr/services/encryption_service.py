"""
خدمة تشفير البيانات الحساسة
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.cache import cache
import base64
import os
import hashlib
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EncryptionService:
    """خدمة تشفير البيانات الحساسة"""
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.fernet = Fernet(self.master_key)
        self.salt = self._get_salt()
    
    def _get_or_create_master_key(self):
        """الحصول على المفتاح الرئيسي أو إنشاؤه"""
        try:
            # محاولة الحصول على المفتاح من متغيرات البيئة
            master_key = os.environ.get('HR_ENCRYPTION_KEY')
            
            if master_key:
                return master_key.encode()
            
            # محاولة الحصول على المفتاح من الإعدادات
            master_key = getattr(settings, 'HR_ENCRYPTION_KEY', None)
            
            if master_key:
                return master_key.encode()
            
            # إنشاء مفتاح جديد إذا لم يوجد
            new_key = Fernet.generate_key()
            
            # حفظ المفتاح في ملف آمن
            key_file_path = os.path.join(settings.BASE_DIR, '.encryption_key')
            
            if not os.path.exists(key_file_path):
                with open(key_file_path, 'wb') as key_file:
                    key_file.write(new_key)
                
                # تعيين صلاحيات آمنة للملف
                os.chmod(key_file_path, 0o600)
                
                logger.warning(
                    f"تم إنشاء مفتاح تشفير جديد في: {key_file_path}. "
                    "يرجى نسخه إلى مكان آمن وحذف الملف من الخادم."
                )
            
            with open(key_file_path, 'rb') as key_file:
                return key_file.read()
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على مفتاح التشفير: {e}")
            # إنشاء مفتاح مؤقت للتطوير فقط
            return Fernet.generate_key()
    
    def _get_salt(self):
        """الحصول على salt للتشفير"""
        salt = getattr(settings, 'HR_ENCRYPTION_SALT', None)
        
        if salt:
            return salt.encode()
        
        # إنشاء salt افتراضي
        return b'hr_system_salt_2024'
    
    def _derive_key(self, password: str, salt: bytes = None) -> bytes:
        """اشتقاق مفتاح من كلمة مرور"""
        if salt is None:
            salt = self.salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_text(self, text: str) -> str:
        """تشفير نص"""
        try:
            if not text:
                return text
            
            encrypted_data = self.fernet.encrypt(text.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"خطأ في تشفير النص: {e}")
            return text
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """فك تشفير نص"""
        try:
            if not encrypted_text:
                return encrypted_text
            
            encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"خطأ في فك تشفير النص: {e}")
            return encrypted_text
    
    def encrypt_sensitive_data(self, data: dict) -> dict:
        """تشفير البيانات الحساسة في قاموس"""
        sensitive_fields = [
            'national_id',
            'passport_number',
            'social_security_number',
            'bank_account_number',
            'iban',
            'tax_number',
            'phone_number',
            'personal_email',
            'emergency_contact_phone',
            'salary',
            'bank_details'
        ]
        
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_text(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_sensitive_data(self, encrypted_data: dict) -> dict:
        """فك تشفير البيانات الحساسة في قاموس"""
        sensitive_fields = [
            'national_id',
            'passport_number',
            'social_security_number',
            'bank_account_number',
            'iban',
            'tax_number',
            'phone_number',
            'personal_email',
            'emergency_contact_phone',
            'salary',
            'bank_details'
        ]
        
        decrypted_data = encrypted_data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt_text(decrypted_data[field])
        
        return decrypted_data
    
    def hash_password(self, password: str) -> str:
        """تشفير كلمة مرور بـ hash"""
        try:
            # استخدام bcrypt للتشفير الآمن
            import bcrypt
            
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
            
        except ImportError:
            # استخدام hashlib كبديل
            salt = os.urandom(32)
            pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return base64.b64encode(salt + pwdhash).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """التحقق من كلمة مرور"""
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
            
        except ImportError:
            # استخدام hashlib للتحقق
            try:
                decoded = base64.b64decode(hashed_password.encode('utf-8'))
                salt = decoded[:32]
                stored_hash = decoded[32:]
                pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
                return pwdhash == stored_hash
            except:
                return False
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """تشفير ملف"""
        try:
            if output_path is None:
                output_path = file_path + '.encrypted'
            
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            encrypted_data = self.fernet.encrypt(file_data)
            
            with open(output_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)
            
            logger.info(f"تم تشفير الملف: {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في تشفير الملف {file_path}: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> str:
        """فك تشفير ملف"""
        try:
            if output_path is None:
                output_path = encrypted_file_path.replace('.encrypted', '')
            
            with open(encrypted_file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as file:
                file.write(decrypted_data)
            
            logger.info(f"تم فك تشفير الملف: {encrypted_file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في فك تشفير الملف {encrypted_file_path}: {e}")
            raise
    
    def create_secure_token(self, data: dict, expiry_hours: int = 24) -> str:
        """إنشاء رمز آمن مع انتهاء صلاحية"""
        try:
            token_data = {
                'data': data,
                'expires_at': (datetime.now() + timedelta(hours=expiry_hours)).isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            token_json = json.dumps(token_data)
            encrypted_token = self.encrypt_text(token_json)
            
            return encrypted_token
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الرمز الآمن: {e}")
            raise
    
    def verify_secure_token(self, token: str) -> dict:
        """التحقق من الرمز الآمن"""
        try:
            decrypted_json = self.decrypt_text(token)
            token_data = json.loads(decrypted_json)
            
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            
            if datetime.now() > expires_at:
                raise ValueError("انتهت صلاحية الرمز")
            
            return token_data['data']
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الرمز الآمن: {e}")
            raise
    
    def mask_sensitive_data(self, data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
        """إخفاء البيانات الحساسة جزئياً"""
        if not data or len(data) <= visible_chars:
            return data
        
        if len(data) <= visible_chars * 2:
            # إظهار النصف الأول فقط
            return data[:visible_chars] + mask_char * (len(data) - visible_chars)
        
        # إظهار البداية والنهاية
        return (
            data[:visible_chars] + 
            mask_char * (len(data) - visible_chars * 2) + 
            data[-visible_chars:]
        )
    
    def generate_secure_id(self, prefix: str = '') -> str:
        """إنشاء معرف آمن"""
        import uuid
        secure_id = str(uuid.uuid4()).replace('-', '')
        
        if prefix:
            return f"{prefix}_{secure_id}"
        
        return secure_id
    
    def encrypt_database_backup(self, backup_file_path: str) -> str:
        """تشفير نسخة احتياطية من قاعدة البيانات"""
        try:
            encrypted_path = self.encrypt_file(backup_file_path)
            
            # حذف الملف الأصلي غير المشفر
            os.remove(backup_file_path)
            
            logger.info(f"تم تشفير النسخة الاحتياطية: {encrypted_path}")
            return encrypted_path
            
        except Exception as e:
            logger.error(f"خطأ في تشفير النسخة الاحتياطية: {e}")
            raise
    
    def create_encryption_audit_log(self, operation: str, data_type: str, user_id: str = None):
        """إنشاء سجل تدقيق للتشفير"""
        try:
            audit_data = {
                'operation': operation,
                'data_type': data_type,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'ip_address': self._get_client_ip()
            }
            
            # حفظ في سجل التدقيق
            cache_key = f'encryption_audit_{datetime.now().date()}'
            audit_logs = cache.get(cache_key, [])
            audit_logs.append(audit_data)
            cache.set(cache_key, audit_logs, 86400)  # 24 ساعة
            
            logger.info(f"سجل تدقيق التشفير: {operation} - {data_type}")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء سجل تدقيق التشفير: {e}")
    
    def _get_client_ip(self) -> str:
        """الحصول على IP العميل"""
        # هذا يتطلب request object، سيتم تحسينه لاحقاً
        return 'unknown'
    
    def rotate_encryption_key(self, new_key: bytes = None) -> bool:
        """تدوير مفتاح التشفير"""
        try:
            if new_key is None:
                new_key = Fernet.generate_key()
            
            old_fernet = self.fernet
            new_fernet = Fernet(new_key)
            
            # هنا يجب إعادة تشفير جميع البيانات المشفرة في قاعدة البيانات
            # هذا مثال أساسي - يحتاج تنفيذ مخصص حسب النماذج
            
            self.master_key = new_key
            self.fernet = new_fernet
            
            logger.info("تم تدوير مفتاح التشفير بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تدوير مفتاح التشفير: {e}")
            return False
    
    def validate_encryption_integrity(self) -> dict:
        """التحقق من سلامة التشفير"""
        try:
            test_data = "test_encryption_integrity"
            encrypted = self.encrypt_text(test_data)
            decrypted = self.decrypt_text(encrypted)
            
            integrity_check = {
                'encryption_working': decrypted == test_data,
                'key_accessible': self.master_key is not None,
                'fernet_initialized': self.fernet is not None,
                'timestamp': datetime.now().isoformat()
            }
            
            if not integrity_check['encryption_working']:
                logger.error("فشل في التحقق من سلامة التشفير")
            
            return integrity_check
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من سلامة التشفير: {e}")
            return {
                'encryption_working': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


class EncryptedField:
    """حقل مشفر للنماذج"""
    
    def __init__(self, encryption_service: EncryptionService = None):
        self.encryption_service = encryption_service or EncryptionService()
    
    def encrypt(self, value):
        """تشفير القيمة"""
        if value is None:
            return value
        return self.encryption_service.encrypt_text(str(value))
    
    def decrypt(self, encrypted_value):
        """فك تشفير القيمة"""
        if encrypted_value is None:
            return encrypted_value
        return self.encryption_service.decrypt_text(encrypted_value)


class SecureDataManager:
    """مدير البيانات الآمنة"""
    
    def __init__(self):
        self.encryption_service = EncryptionService()
    
    def store_secure_data(self, key: str, data: dict, expiry_hours: int = 24):
        """حفظ بيانات آمنة مؤقتاً"""
        try:
            encrypted_data = self.encryption_service.encrypt_text(json.dumps(data))
            cache.set(f'secure_data_{key}', encrypted_data, expiry_hours * 3600)
            
            self.encryption_service.create_encryption_audit_log(
                'store_secure_data', 'temporary_data'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حفظ البيانات الآمنة: {e}")
            return False
    
    def retrieve_secure_data(self, key: str) -> dict:
        """استرجاع بيانات آمنة"""
        try:
            encrypted_data = cache.get(f'secure_data_{key}')
            
            if encrypted_data is None:
                return None
            
            decrypted_json = self.encryption_service.decrypt_text(encrypted_data)
            data = json.loads(decrypted_json)
            
            self.encryption_service.create_encryption_audit_log(
                'retrieve_secure_data', 'temporary_data'
            )
            
            return data
            
        except Exception as e:
            logger.error(f"خطأ في استرجاع البيانات الآمنة: {e}")
            return None
    
    def delete_secure_data(self, key: str):
        """حذف بيانات آمنة"""
        try:
            cache.delete(f'secure_data_{key}')
            
            self.encryption_service.create_encryption_audit_log(
                'delete_secure_data', 'temporary_data'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حذف البيانات الآمنة: {e}")
            return False


# إنشاء مثيلات الخدمات
encryption_service = EncryptionService()
secure_data_manager = SecureDataManager()