"""
Employee File Service - خدمات إدارة ملفات الموظفين
"""

from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import os
import mimetypes
import logging

logger = logging.getLogger('hr_system')


class EmployeeFileService:
    """خدمات إدارة ملفات الموظفين"""
    
    ALLOWED_FILE_TYPES = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
        'document': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
        'spreadsheet': ['xls', 'xlsx', 'csv'],
        'archive': ['zip', 'rar', '7z'],
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def upload_employee_file(self, employee, file_data, uploaded_file, uploaded_by):
        """رفع ملف للموظف مع التحقق من النوع والحجم"""
        try:
            from ..models_enhanced import EmployeeFile
            
            # Validate file
            self._validate_file(uploaded_file)
            
            # Generate unique filename
            filename = self._generate_unique_filename(uploaded_file.name, employee.employee_number)
            
            # Save file
            file_path = default_storage.save(f'employee_files/{filename}', uploaded_file)
            
            # Get file info
            file_size = uploaded_file.size
            mime_type = mimetypes.guess_type(uploaded_file.name)[0]
            
            # Create file record
            employee_file = EmployeeFile.objects.create(
                employee=employee,
                file_type=file_data.get('file_type'),
                title=file_data.get('title'),
                description=file_data.get('description', ''),
                file=file_path,
                file_size=file_size,
                mime_type=mime_type,
                document_date=file_data.get('document_date'),
                expiry_date=file_data.get('expiry_date'),
                confidentiality_level=file_data.get('confidentiality_level', 'internal'),
                uploaded_by=uploaded_by
            )
            
            logger.info(f"Uploaded file {filename} for employee {employee.employee_number}")
            return employee_file
            
        except Exception as e:
            logger.error(f"Error uploading file for employee {employee.employee_number}: {e}")
            raise ValidationError(f"خطأ في رفع الملف: {e}")
    
    def check_document_expiry(self, warning_days=None):
        """فحص الوثائق منتهية الصلاحية وإرسال تنبيهات"""
        try:
            from ..models_enhanced import EmployeeFile
            
            if warning_days is None:
                warning_days = getattr(settings, 'HR_SETTINGS', {}).get('DOCUMENT_EXPIRY_WARNING_DAYS', 30)
            
            warning_date = timezone.now().date() + timedelta(days=warning_days)
            
            # Get expiring files
            expiring_files = EmployeeFile.objects.filter(
                expiry_date__lte=warning_date,
                expiry_date__gte=timezone.now().date()
            ).select_related('employee', 'uploaded_by')
            
            # Get expired files
            expired_files = EmployeeFile.objects.filter(
                expiry_date__lt=timezone.now().date()
            ).select_related('employee', 'uploaded_by')
            
            return {
                'expiring_files': expiring_files,
                'expired_files': expired_files,
                'expiring_count': expiring_files.count(),
                'expired_count': expired_files.count()
            }
            
        except Exception as e:
            logger.error(f"Error checking document expiry: {e}")
            raise ValidationError(f"خطأ في فحص انتهاء الوثائق: {e}")
    
    def organize_employee_files(self, employee_id):
        """تنظيم ملفات الموظف حسب النوع والتاريخ"""
        try:
            from ..models_enhanced import EmployeeFile, Employee
            
            employee = Employee.objects.get(id=employee_id)
            files = EmployeeFile.objects.filter(employee=employee).order_by('-uploaded_at')
            
            organized_files = {}
            
            for file in files:
                file_type = file.get_file_type_display()
                if file_type not in organized_files:
                    organized_files[file_type] = []
                
                organized_files[file_type].append({
                    'file': file,
                    'is_expired': file.is_expired,
                    'is_expiring_soon': file.is_expiring_soon,
                    'days_until_expiry': file.days_until_expiry
                })
            
            return {
                'employee': employee,
                'organized_files': organized_files,
                'total_files': files.count()
            }
            
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"Error organizing files for employee {employee_id}: {e}")
            raise ValidationError(f"خطأ في تنظيم الملفات: {e}")
    
    def generate_file_access_log(self, employee_id, user=None):
        """إنشاء سجل الوصول للملفات"""
        try:
            from ..models_enhanced import EmployeeFile, Employee
            
            employee = Employee.objects.get(id=employee_id)
            files = EmployeeFile.objects.filter(employee=employee)
            
            access_log = []
            
            for file in files:
                log_entry = {
                    'file': file,
                    'download_count': file.download_count,
                    'last_accessed': file.updated_at,
                    'can_access': self._check_file_access_permission(file, user)
                }
                access_log.append(log_entry)
            
            return {
                'employee': employee,
                'access_log': access_log,
                'total_downloads': sum(entry['download_count'] for entry in access_log)
            }
            
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"Error generating access log for employee {employee_id}: {e}")
            raise ValidationError(f"خطأ في إنشاء سجل الوصول: {e}")
    
    def search_files(self, search_params):
        """البحث في الملفات"""
        try:
            from ..models_enhanced import EmployeeFile
            from django.db.models import Q
            
            files = EmployeeFile.objects.select_related('employee')
            
            # Apply filters
            if search_params.get('employee_id'):
                files = files.filter(employee_id=search_params['employee_id'])
            
            if search_params.get('file_type'):
                files = files.filter(file_type=search_params['file_type'])
            
            if search_params.get('title'):
                files = files.filter(title__icontains=search_params['title'])
            
            if search_params.get('date_from'):
                files = files.filter(uploaded_at__gte=search_params['date_from'])
            
            if search_params.get('date_to'):
                files = files.filter(uploaded_at__lte=search_params['date_to'])
            
            if search_params.get('expiry_status'):
                if search_params['expiry_status'] == 'expired':
                    files = files.filter(expiry_date__lt=timezone.now().date())
                elif search_params['expiry_status'] == 'expiring_soon':
                    warning_days = getattr(settings, 'HR_SETTINGS', {}).get('DOCUMENT_EXPIRY_WARNING_DAYS', 30)
                    warning_date = timezone.now().date() + timedelta(days=warning_days)
                    files = files.filter(
                        expiry_date__lte=warning_date,
                        expiry_date__gte=timezone.now().date()
                    )
            
            if search_params.get('confidentiality_level'):
                files = files.filter(confidentiality_level=search_params['confidentiality_level'])
            
            # Text search in title and description
            if search_params.get('search_text'):
                files = files.filter(
                    Q(title__icontains=search_params['search_text']) |
                    Q(description__icontains=search_params['search_text'])
                )
            
            return files.order_by('-uploaded_at')
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            raise ValidationError(f"خطأ في البحث: {e}")
    
    def delete_file(self, file_id, user, reason=None):
        """حذف ملف مع تسجيل السبب"""
        try:
            from ..models_enhanced import EmployeeFile
            
            file = EmployeeFile.objects.get(id=file_id)
            
            # Check permissions
            if not self._check_file_delete_permission(file, user):
                raise ValidationError("ليس لديك صلاحية لحذف هذا الملف")
            
            # Delete physical file
            if file.file and default_storage.exists(file.file.name):
                default_storage.delete(file.file.name)
            
            # Log deletion
            logger.info(f"File {file.title} deleted by {user.username}. Reason: {reason}")
            
            # Delete record
            file.delete()
            
            return True
            
        except EmployeeFile.DoesNotExist:
            raise ValidationError("الملف غير موجود")
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            raise ValidationError(f"خطأ في حذف الملف: {e}")
    
    def _validate_file(self, uploaded_file):
        """التحقق من صحة الملف"""
        # Check file size
        if uploaded_file.size > self.MAX_FILE_SIZE:
            raise ValidationError(f"حجم الملف كبير جداً. الحد الأقصى {self.MAX_FILE_SIZE / (1024*1024):.1f} ميجابايت")
        
        # Check file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        allowed_extensions = []
        for extensions in self.ALLOWED_FILE_TYPES.values():
            allowed_extensions.extend(extensions)
        
        if file_extension not in allowed_extensions:
            raise ValidationError(f"نوع الملف غير مدعوم. الأنواع المدعومة: {', '.join(allowed_extensions)}")
        
        # Check for malicious files (basic check)
        dangerous_extensions = ['exe', 'bat', 'cmd', 'scr', 'pif', 'com']
        if file_extension in dangerous_extensions:
            raise ValidationError("نوع الملف غير آمن")
    
    def _generate_unique_filename(self, original_filename, employee_number):
        """إنشاء اسم ملف فريد"""
        import uuid
        from datetime import datetime
        
        # Get file extension
        file_extension = original_filename.split('.')[-1].lower()
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{employee_number}_{timestamp}_{unique_id}.{file_extension}"
    
    def _check_file_access_permission(self, file, user):
        """التحقق من صلاحية الوصول للملف"""
        if not user:
            return False
        
        # Super admin can access all files
        if user.is_superuser:
            return True
        
        # File owner can access
        if file.uploaded_by == user:
            return True
        
        # Employee can access their own files
        if hasattr(user, 'employee_profile') and file.employee == user.employee_profile:
            return True
        
        # HR staff can access based on confidentiality level
        if hasattr(user, 'hr_permissions'):
            if file.confidentiality_level == 'public':
                return True
            elif file.confidentiality_level == 'internal' and user.hr_permissions.filter(module='employee_files', permission_level='view').exists():
                return True
            elif file.confidentiality_level in ['confidential', 'highly_confidential'] and user.hr_permissions.filter(module='employee_files', permission_level='view_sensitive').exists():
                return True
        
        return False
    
    def _check_file_delete_permission(self, file, user):
        """التحقق من صلاحية حذف الملف"""
        if not user:
            return False
        
        # Super admin can delete all files
        if user.is_superuser:
            return True
        
        # File uploader can delete within 24 hours
        if file.uploaded_by == user and (timezone.now() - file.uploaded_at).days < 1:
            return True
        
        # HR admin can delete
        if hasattr(user, 'hr_permissions') and user.hr_permissions.filter(module='employee_files', permission_level='delete').exists():
            return True
        
        return False