"""
Encryption and Data Protection Service
خدمة التشفير وحماية البيانات

This service provides comprehensive encryption and data protection capabilities
for securing sensitive data throughout the system.
"""

import os
import base64
import hashlib
import secrets
import logging
from typing import Union, Optional, Dict, Any
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Comprehensive encryption service for data protection
    خدمة التشفير الشاملة لحماية البيانات
    """
    
    def __init__(self):
        self.backend = default_backend()
        self._fernet_key = self._get_or_create_fernet_key()
        self._fernet = Fernet(self._fernet_key)
        
    def _get_or_create_fernet_key(self) -> bytes:
        """
        Get or create Fernet encryption key
        الحصول على أو إنشاء مفتاح تشفير Fernet
        """
        # Try to get key from settings
        key_setting = getattr(settings, 'ENCRYPTION_KEY', None)
        if key_setting:
            return key_setting.encode() if isinstance(key_setting, str) else key_setting
        
        # Try to get key from environment
        key_env = os.environ.get('ENCRYPTION_KEY')
        if key_env:
            return key_env.encode()
        
        # Generate new key (for development only)
        if settings.DEBUG:
            logger.warning("Generating new encryption key for development. This should not happen in production!")
            return Fernet.generate_key()
        
        raise ValueError("No encryption key found. Set ENCRYPTION_KEY in settings or environment.")
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string using Fernet symmetric encryption
        تشفير نص باستخدام التشفير المتماثل Fernet
        """
        if not plaintext:
            return plaintext
        
        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """
        Decrypt a string using Fernet symmetric encryption
        فك تشفير نص باستخدام التشفير المتماثل Fernet
        """
        if not encrypted_text:
            return encrypted_text
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Encrypt a dictionary as JSON string
        تشفير قاموس كسلسلة JSON
        """
        import json
        json_string = json.dumps(data, ensure_ascii=False)
        return self.encrypt_string(json_string)
    
    def decrypt_dict(self, encrypted_text: str) -> Dict[str, Any]:
        """
        Decrypt a JSON string back to dictionary
        فك تشفير سلسلة JSON إلى قاموس
        """
        import json
        json_string = self.decrypt_string(encrypted_text)
        return json.loads(json_string)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """
        Hash password with salt using PBKDF2
        تشفير كلمة المرور مع الملح باستخدام PBKDF2
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode('utf-8'),
            iterations=100000,
            backend=self.backend
        )
        
        password_hash = base64.urlsafe_b64encode(
            kdf.derive(password.encode('utf-8'))
        ).decode('utf-8')
        
        return {
            'hash': password_hash,
            'salt': salt,
            'algorithm': 'pbkdf2_sha256',
            'iterations': 100000
        }
    
    def verify_password(self, password: str, password_data: Dict[str, str]) -> bool:
        """
        Verify password against stored hash
        التحقق من كلمة المرور مقابل التشفير المخزن
        """
        try:
            salt = password_data['salt']
            stored_hash = password_data['hash']
            iterations = password_data.get('iterations', 100000)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode('utf-8'),
                iterations=iterations,
                backend=self.backend
            )
            
            password_hash = base64.urlsafe_b64encode(
                kdf.derive(password.encode('utf-8'))
            ).decode('utf-8')
            
            return secrets.compare_digest(password_hash, stored_hash)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate cryptographically secure random token
        توليد رمز عشوائي آمن تشفيرياً
        """
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self) -> Dict[str, str]:
        """
        Generate secure API key with metadata
        توليد مفتاح API آمن مع البيانات الوصفية
        """
        key = secrets.token_urlsafe(32)
        secret = secrets.token_urlsafe(64)
        
        return {
            'key': key,
            'secret': secret,
            'created_at': timezone.now().isoformat()
        }
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file using AES encryption
        تشفير ملف باستخدام تشفير AES
        """
        if output_path is None:
            output_path = file_path + '.encrypted'
        
        # Generate random key and IV
        key = os.urandom(32)  # 256-bit key
        iv = os.urandom(16)   # 128-bit IV
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        try:
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                # Write IV to beginning of file
                outfile.write(iv)
                
                # Encrypt file in chunks
                while True:
                    chunk = infile.read(8192)
                    if not chunk:
                        break
                    
                    # Pad last chunk if necessary
                    if len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - len(chunk) % 16)
                    
                    encrypted_chunk = encryptor.update(chunk)
                    outfile.write(encrypted_chunk)
                
                # Finalize encryption
                outfile.write(encryptor.finalize())
            
            # Store key securely (in production, use key management service)
            key_file = output_path + '.key'
            with open(key_file, 'wb') as keyfile:
                keyfile.write(key)
            
            return output_path
            
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise
    
    def decrypt_file(self, encrypted_path: str, key_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file using AES encryption
        فك تشفير ملف باستخدام تشفير AES
        """
        if output_path is None:
            output_path = encrypted_path.replace('.encrypted', '.decrypted')
        
        try:
            # Read key
            with open(key_path, 'rb') as keyfile:
                key = keyfile.read()
            
            with open(encrypted_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                # Read IV from beginning of file
                iv = infile.read(16)
                
                # Create cipher
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.CBC(iv),
                    backend=self.backend
                )
                decryptor = cipher.decryptor()
                
                # Decrypt file in chunks
                while True:
                    chunk = infile.read(8192)
                    if not chunk:
                        break
                    
                    decrypted_chunk = decryptor.update(chunk)
                    outfile.write(decrypted_chunk)
                
                # Finalize decryption
                outfile.write(decryptor.finalize())
            
            return output_path
            
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            raise


class AsymmetricEncryption:
    """
    Asymmetric (RSA) encryption service
    خدمة التشفير غير المتماثل (RSA)
    """
    
    def __init__(self):
        self.backend = default_backend()
    
    def generate_key_pair(self, key_size: int = 2048) -> Dict[str, bytes]:
        """
        Generate RSA key pair
        توليد زوج مفاتيح RSA
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            'private_key': private_pem,
            'public_key': public_pem
        }
    
    def encrypt_with_public_key(self, plaintext: str, public_key_pem: bytes) -> str:
        """
        Encrypt data with RSA public key
        تشفير البيانات بمفتاح RSA العام
        """
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=self.backend
        )
        
        encrypted = public_key.encrypt(
            plaintext.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_with_private_key(self, encrypted_text: str, private_key_pem: bytes) -> str:
        """
        Decrypt data with RSA private key
        فك تشفير البيانات بمفتاح RSA الخاص
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=self.backend
        )
        
        encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
        
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted.decode('utf-8')
    
    def sign_data(self, data: str, private_key_pem: bytes) -> str:
        """
        Sign data with RSA private key
        توقيع البيانات بمفتاح RSA الخاص
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=self.backend
        )
        
        signature = private_key.sign(
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, data: str, signature: str, public_key_pem: bytes) -> bool:
        """
        Verify signature with RSA public key
        التحقق من التوقيع بمفتاح RSA العام
        """
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=self.backend
            )
            
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            
            public_key.verify(
                signature_bytes,
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
        except Exception:
            return False


class DataProtectionService:
    """
    Comprehensive data protection and privacy service
    خدمة حماية البيانات والخصوصية الشاملة
    """
    
    def __init__(self):
        self.encryption_service = EncryptionService()
        self.sensitive_fields = self._get_sensitive_fields()
    
    def _get_sensitive_fields(self) -> set:
        """
        Get list of sensitive field names
        الحصول على قائمة أسماء الحقول الحساسة
        """
        return {
            'password', 'ssn', 'national_id', 'passport_number',
            'credit_card', 'bank_account', 'salary', 'phone',
            'email', 'address', 'medical_info', 'personal_notes'
        }
    
    def protect_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically encrypt sensitive fields in data
        تشفير الحقول الحساسة تلقائياً في البيانات
        """
        protected_data = data.copy()
        
        for field_name, value in data.items():
            if self._is_sensitive_field(field_name) and value:
                try:
                    protected_data[field_name] = self.encryption_service.encrypt_string(str(value))
                    protected_data[f"{field_name}_encrypted"] = True
                except Exception as e:
                    logger.error(f"Failed to encrypt field {field_name}: {e}")
        
        return protected_data
    
    def unprotect_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically decrypt sensitive fields in data
        فك تشفير الحقول الحساسة تلقائياً في البيانات
        """
        unprotected_data = data.copy()
        
        for field_name, value in data.items():
            if field_name.endswith('_encrypted'):
                continue
            
            if self._is_sensitive_field(field_name) and value:
                encrypted_flag = data.get(f"{field_name}_encrypted", False)
                if encrypted_flag:
                    try:
                        unprotected_data[field_name] = self.encryption_service.decrypt_string(value)
                    except Exception as e:
                        logger.error(f"Failed to decrypt field {field_name}: {e}")
        
        return unprotected_data
    
    def _is_sensitive_field(self, field_name: str) -> bool:
        """
        Check if field name indicates sensitive data
        التحقق من كون اسم الحقل يشير إلى بيانات حساسة
        """
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in self.sensitive_fields)
    
    def mask_sensitive_data(self, data: Dict[str, Any], mask_char: str = '*') -> Dict[str, Any]:
        """
        Mask sensitive data for display purposes
        إخفاء البيانات الحساسة لأغراض العرض
        """
        masked_data = data.copy()
        
        for field_name, value in data.items():
            if self._is_sensitive_field(field_name) and value:
                str_value = str(value)
                if len(str_value) > 4:
                    # Show first 2 and last 2 characters
                    masked_value = str_value[:2] + mask_char * (len(str_value) - 4) + str_value[-2:]
                else:
                    masked_value = mask_char * len(str_value)
                
                masked_data[field_name] = masked_value
        
        return masked_data
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize data by removing or hashing identifiable information
        إخفاء هوية البيانات بإزالة أو تشفير المعلومات القابلة للتحديد
        """
        anonymized_data = data.copy()
        
        # Remove direct identifiers
        identifiers = ['name', 'email', 'phone', 'address', 'ssn', 'national_id']
        for identifier in identifiers:
            if identifier in anonymized_data:
                del anonymized_data[identifier]
        
        # Hash quasi-identifiers
        quasi_identifiers = ['birth_date', 'zip_code', 'job_title']
        for qi in quasi_identifiers:
            if qi in anonymized_data and anonymized_data[qi]:
                anonymized_data[qi] = hashlib.sha256(
                    str(anonymized_data[qi]).encode()
                ).hexdigest()[:8]
        
        return anonymized_data
    
    def generate_data_hash(self, data: Dict[str, Any]) -> str:
        """
        Generate hash of data for integrity checking
        توليد تشفير للبيانات للتحقق من السلامة
        """
        import json
        
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
        
        return hashlib.sha256(sorted_data.encode('utf-8')).hexdigest()
    
    def verify_data_integrity(self, data: Dict[str, Any], expected_hash: str) -> bool:
        """
        Verify data integrity using hash
        التحقق من سلامة البيانات باستخدام التشفير
        """
        actual_hash = self.generate_data_hash(data)
        return secrets.compare_digest(actual_hash, expected_hash)


class SecureStorage:
    """
    Secure storage service for sensitive files and data
    خدمة التخزين الآمن للملفات والبيانات الحساسة
    """
    
    def __init__(self):
        self.encryption_service = EncryptionService()
        self.storage_path = getattr(settings, 'SECURE_STORAGE_PATH', '/tmp/secure_storage')
        os.makedirs(self.storage_path, exist_ok=True)
    
    def store_secure_file(self, file_content: bytes, filename: str, metadata: Optional[Dict] = None) -> str:
        """
        Store file securely with encryption
        تخزين الملف بأمان مع التشفير
        """
        # Generate unique file ID
        file_id = secrets.token_urlsafe(16)
        
        # Create file paths
        encrypted_path = os.path.join(self.storage_path, f"{file_id}.enc")
        metadata_path = os.path.join(self.storage_path, f"{file_id}.meta")
        
        try:
            # Encrypt file content
            encrypted_content = self.encryption_service._fernet.encrypt(file_content)
            
            # Write encrypted file
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_content)
            
            # Store metadata
            file_metadata = {
                'original_filename': filename,
                'file_size': len(file_content),
                'created_at': timezone.now().isoformat(),
                'content_type': metadata.get('content_type', 'application/octet-stream') if metadata else 'application/octet-stream',
                'checksum': hashlib.sha256(file_content).hexdigest(),
                'custom_metadata': metadata or {}
            }
            
            with open(metadata_path, 'w') as f:
                import json
                json.dump(file_metadata, f)
            
            return file_id
            
        except Exception as e:
            logger.error(f"Secure file storage failed: {e}")
            # Clean up partial files
            for path in [encrypted_path, metadata_path]:
                if os.path.exists(path):
                    os.remove(path)
            raise
    
    def retrieve_secure_file(self, file_id: str) -> Dict[str, Any]:
        """
        Retrieve and decrypt stored file
        استرداد وفك تشفير الملف المخزن
        """
        encrypted_path = os.path.join(self.storage_path, f"{file_id}.enc")
        metadata_path = os.path.join(self.storage_path, f"{file_id}.meta")
        
        if not os.path.exists(encrypted_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Secure file {file_id} not found")
        
        try:
            # Read metadata
            with open(metadata_path, 'r') as f:
                import json
                metadata = json.load(f)
            
            # Read and decrypt file
            with open(encrypted_path, 'rb') as f:
                encrypted_content = f.read()
            
            decrypted_content = self.encryption_service._fernet.decrypt(encrypted_content)
            
            # Verify checksum
            actual_checksum = hashlib.sha256(decrypted_content).hexdigest()
            if actual_checksum != metadata['checksum']:
                raise ValueError("File integrity check failed")
            
            return {
                'content': decrypted_content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Secure file retrieval failed: {e}")
            raise
    
    def delete_secure_file(self, file_id: str) -> bool:
        """
        Securely delete stored file
        حذف الملف المخزن بأمان
        """
        encrypted_path = os.path.join(self.storage_path, f"{file_id}.enc")
        metadata_path = os.path.join(self.storage_path, f"{file_id}.meta")
        
        try:
            # Overwrite files with random data before deletion
            for path in [encrypted_path, metadata_path]:
                if os.path.exists(path):
                    file_size = os.path.getsize(path)
                    with open(path, 'wb') as f:
                        f.write(os.urandom(file_size))
                    os.remove(path)
            
            return True
            
        except Exception as e:
            logger.error(f"Secure file deletion failed: {e}")
            return False


# Global instances
encryption_service = EncryptionService()
asymmetric_encryption = AsymmetricEncryption()
data_protection_service = DataProtectionService()
secure_storage = SecureStorage()