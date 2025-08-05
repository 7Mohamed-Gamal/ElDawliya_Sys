"""
خدمة إدارة الملفات المحسنة - Employee File Service Enhanced
يوفر جميع العمليات المتعلقة بإدارة ملفات الموظفين مع ميزات متقدمة للأمان والتشفير
"""

from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.cache import cache
from django.db.models import Q, Count, Sum, Avg
from datetime import timedelta, date
import os
import mimetypes
import logging
import hashlib
import json
from PIL import Image
import magic
import zipfile
import tempfile
from io import BytesIO

logger = logging.getLogger('hr_system')


class EmployeeFileServiceEnhanced:
    """خدمات إدارة ملفات الموظفين المحسنة"""
    
    # File type categories with enhanced validation
    ALLOWED_FILE_TYPES = {
        'identity': {
            'extensions': ['pdf', 'jpg', 'jpeg', 'png'],
            'max_size': 5 * 1024 * 1024,  # 5MB
            'description': 'وثائق الهوية'
        },
        'passport': {
            'extensions': ['pdf', 'jpg', 'jpeg', 'png'],
            'max_size': 5 * 1024 * 1024,
            'description': 'جواز السفر'
        },
        'visa': {
            'extensions': ['pdf', 'jpg', 'jpeg', 'png'],
            'max_size': 5 * 1024 * 1024,
            'description': 'التأشيرة'
        },
        'contract': {
            'extensions': ['pdf', 'doc', 'docx'],
            'max_size': 10 * 1024 * 1024,  # 10MB
            'description': 'عقود العمل'
        },
        'certificate': {
            'extensions': ['pdf', 'jpg', 'jpeg', 'png'],
            'max_size': 5 * 1024 * 1024,
            'description': 'الشهادات والمؤهلات'
        },
        'medical': {
            'extensions': ['pdf', 'jpg', 'jpeg', 'png'],
            'max_size': 5 * 1024 * 1024,
            'description': 'التقارير الطبية'
        },
        'insurance': {
            'extensions': ['pdf', 'doc', 'docx'],
            'max_size': 5 * 1024 * 1024,
            'description': 'وثائق التأمين'
        },
        'bank': {
            'extensions': ['pdf', 'jpg', 'jpeg', 'png'],
            'max_size': 5 * 1024 * 1024,
            'description': 'الوثائق البنكية'
        },
        'training': {
            'extensions': ['pdf', 'doc', 'docx', 'ppt', 'pptx'],
            'max_size': 20 * 1024 * 1024,  # 20MB
            'description': 'شهادات التدريب'
        },
        'evaluation': {
            'extensions': ['pdf', 'doc', 'docx', 'xls', 'xlsx'],
            'max_size': 10 * 1024 * 1024,
            'description': 'تقييمات الأداء'
        },
        'other': {
            'extensions': ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'],
            'max_size': 10 * 1024 * 1024,
            'description': 'ملفات أخرى'
        }
    }
    
    # Confidentiality levels
    CONFIDENTIALITY_LEVELS = {
        'public': {'level': 1, 'description': 'عام'},
        'internal': {'level': 2, 'description': 'داخلي'},
        'confidential': {'level': 3, 'description': 'سري'},
        'highly_confidential': {'level': 4, 'description': 'سري للغاية'},
        'restricted': {'level': 5, 'description': 'مقيد'}
    }
    
    def __init__(self):
        """تهيئة الخدمة"""
        self.cache_timeout = getattr(settings, 'FILE_CACHE_TIMEOUT', 1800)
        self.encryption_enabled = getattr(settings, 'ENCRYPT_SENSITIVE_FILES', True)
        self.virus_scan_enabled = getattr(settings, 'ENABLE_VIRUS_SCAN', False)
        self.max_files_per_employee = getattr(settings, 'MAX_FILES_PER_EMPLOYEE', 100)
    
    # =============================================================================
    # CORE FILE MANAGEMENT METHODS
    # =============================================================================
    
    def upload_employee_file(self, employee, file_data, uploaded_file, uploaded_by, 
                           auto_extract_metadata=True, encrypt_sensitive=True):
        """رفع ملف للموظف مع التحقق المتقدم والتشفير"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            
            with transaction.atomic():
                # Validate file
                validation_result = self._validate_file_enhanced(uploaded_file, file_data.get('file_type'))
                if not validation_result['is_valid']:
                    raise ValidationError(validation_result['errors'])
                
                # Check employee file limit
                current_files_count = EmployeeFileEnhanced.objects.filter(
                    employee=employee, is_deleted=False
                ).count()
                
                if current_files_count >= self.max_files_per_employee:
                    raise ValidationError(f"تم الوصول للحد الأقصى من الملفات ({self.max_files_per_employee})")
                
                # Virus scan if enabled
                if self.virus_scan_enabled:
                    scan_result = self._scan_file_for_viruses(uploaded_file)
                    if not scan_result['is_clean']:
                        raise ValidationError(f"الملف يحتوي على فيروس: {scan_result['threat']}")
                
                # Generate unique filename
                filename = self._generate_unique_filename(uploaded_file.name, employee.employee_id)
                
                # Extract metadata if requested
                metadata = {}
                if auto_extract_metadata:
                    metadata = self._extract_file_metadata(uploaded_file)
                
                # Encrypt file if sensitive
                file_content = uploaded_file.read()
                uploaded_file.seek(0)  # Reset file pointer
                
                if encrypt_sensitive and self._is_sensitive_file_type(file_data.get('file_type')):
                    file_content = self._encrypt_file_content(file_content)
                    metadata['is_encrypted'] = True
                
                # Save file
                file_path = self._save_file_securely(filename, file_content, employee.employee_id)
                
                # Generate file hash for integrity
                file_hash = hashlib.sha256(file_content).hexdigest()
                
                # Create file record
                employee_file = EmployeeFileEnhanced.objects.create(
                    employee=employee,
                    file_type=file_data.get('file_type', 'other'),
                    title=file_data.get('title'),
                    description=file_data.get('description', ''),
                    file_path=file_path,
                    original_filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    mime_type=mimetypes.guess_type(uploaded_file.name)[0],
                    file_hash=file_hash,
                    document_date=file_data.get('document_date'),
                    expiry_date=file_data.get('expiry_date'),
                    issue_date=file_data.get('issue_date'),
                    issuing_authority=file_data.get('issuing_authority'),
                    document_number=file_data.get('document_number'),
                    confidentiality_level=file_data.get('confidentiality_level', 'internal'),
                    requires_approval=file_data.get('requires_approval', False),
                    metadata=metadata,
                    uploaded_by=uploaded_by,
                    tags=file_data.get('tags', [])
                )
                
                # Generate thumbnail for images
                if self._is_image_file(uploaded_file.name):
                    self._generate_thumbnail(employee_file, file_content)
                
                # Clear cache
                self._clear_file_cache(employee.id)
                
                logger.info(f"Uploaded enhanced file {filename} for employee {employee.employee_id}")
                return employee_file
                
        except Exception as e:
            logger.error(f"Error uploading enhanced file for employee {employee.employee_id}: {e}")
            raise ValidationError(f"خطأ في رفع الملف: {e}")
    
    def check_document_expiry_enhanced(self, warning_days=None, include_predictions=True):
        """فحص متقدم للوثائق منتهية الصلاحية مع تنبؤات"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            
            if warning_days is None:
                warning_days = getattr(settings, 'HR_SETTINGS', {}).get('DOCUMENT_EXPIRY_WARNING_DAYS', 30)
            
            today = date.today()
            warning_date = today + timedelta(days=warning_days)
            
            # Get expiring files with detailed categorization
            expiring_files = EmployeeFileEnhanced.objects.filter(
                expiry_date__lte=warning_date,
                expiry_date__gte=today,
                is_deleted=False
            ).select_related('employee', 'uploaded_by').order_by('expiry_date')
            
            # Get expired files
            expired_files = EmployeeFileEnhanced.objects.filter(
                expiry_date__lt=today,
                is_deleted=False
            ).select_related('employee', 'uploaded_by').order_by('-expiry_date')
            
            # Categorize by urgency
            critical_files = expiring_files.filter(expiry_date__lte=today + timedelta(days=7))
            urgent_files = expiring_files.filter(
                expiry_date__gt=today + timedelta(days=7),
                expiry_date__lte=today + timedelta(days=15)
            )
            warning_files = expiring_files.filter(expiry_date__gt=today + timedelta(days=15))
            
            # Group by file type
            expiry_by_type = {}
            for file in expiring_files:
                file_type = file.get_file_type_display()
                if file_type not in expiry_by_type:
                    expiry_by_type[file_type] = []
                expiry_by_type[file_type].append(file)
            
            # Group by employee
            expiry_by_employee = {}
            for file in expiring_files:
                emp_id = file.employee.id
                if emp_id not in expiry_by_employee:
                    expiry_by_employee[emp_id] = {
                        'employee': file.employee,
                        'files': []
                    }
                expiry_by_employee[emp_id]['files'].append(file)
            
            result = {
                'summary': {
                    'total_expiring': expiring_files.count(),
                    'total_expired': expired_files.count(),
                    'critical_count': critical_files.count(),
                    'urgent_count': urgent_files.count(),
                    'warning_count': warning_files.count(),
                },
                'files': {
                    'expiring': expiring_files,
                    'expired': expired_files,
                    'critical': critical_files,
                    'urgent': urgent_files,
                    'warning': warning_files,
                },
                'groupings': {
                    'by_type': expiry_by_type,
                    'by_employee': expiry_by_employee,
                },
                'generated_at': timezone.now()
            }
            
            # Add predictions if requested
            if include_predictions:
                result['predictions'] = self._predict_future_expirations()
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking enhanced document expiry: {e}")
            raise ValidationError(f"خطأ في فحص انتهاء الوثائق: {e}")
    
    def organize_employee_files_enhanced(self, employee_id, organization_type='type'):
        """تنظيم متقدم لملفات الموظف"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            from ..models.employee.employee_models_enhanced import EmployeeEnhanced
            
            # Check cache first
            cache_key = f"employee_files_organized_{employee_id}_{organization_type}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            employee = EmployeeEnhanced.objects.get(id=employee_id)
            files = EmployeeFileEnhanced.objects.filter(
                employee=employee, is_deleted=False
            ).order_by('-uploaded_at')
            
            organized_files = {}
            file_statistics = {
                'total_files': files.count(),
                'total_size': sum(f.file_size for f in files),
                'by_type': {},
                'by_confidentiality': {},
                'expired_count': 0,
                'expiring_soon_count': 0,
                'encrypted_count': 0
            }
            
            for file in files:
                # Determine organization key
                if organization_type == 'type':
                    org_key = file.get_file_type_display()
                elif organization_type == 'date':
                    org_key = file.uploaded_at.strftime('%Y-%m')
                elif organization_type == 'confidentiality':
                    org_key = file.get_confidentiality_level_display()
                elif organization_type == 'status':
                    if file.is_expired:
                        org_key = 'منتهية الصلاحية'
                    elif file.is_expiring_soon:
                        org_key = 'تنتهي قريباً'
                    else:
                        org_key = 'سارية'
                else:
                    org_key = 'أخرى'
                
                if org_key not in organized_files:
                    organized_files[org_key] = []
                
                # Enhanced file info
                file_info = {
                    'file': file,
                    'is_expired': file.is_expired,
                    'is_expiring_soon': file.is_expiring_soon,
                    'days_until_expiry': file.days_until_expiry,
                    'is_encrypted': file.metadata.get('is_encrypted', False),
                    'has_thumbnail': hasattr(file, 'thumbnail_path') and file.thumbnail_path,
                    'download_count': file.download_count,
                    'last_accessed': file.last_accessed_at,
                    'file_age_days': (timezone.now().date() - file.uploaded_at.date()).days,
                    'integrity_status': self._check_file_integrity(file)
                }
                
                organized_files[org_key].append(file_info)
                
                # Update statistics
                file_type = file.get_file_type_display()
                if file_type not in file_statistics['by_type']:
                    file_statistics['by_type'][file_type] = 0
                file_statistics['by_type'][file_type] += 1
                
                conf_level = file.get_confidentiality_level_display()
                if conf_level not in file_statistics['by_confidentiality']:
                    file_statistics['by_confidentiality'][conf_level] = 0
                file_statistics['by_confidentiality'][conf_level] += 1
                
                if file.is_expired:
                    file_statistics['expired_count'] += 1
                elif file.is_expiring_soon:
                    file_statistics['expiring_soon_count'] += 1
                
                if file.metadata.get('is_encrypted'):
                    file_statistics['encrypted_count'] += 1
            
            result = {
                'employee': employee,
                'organized_files': organized_files,
                'statistics': file_statistics,
                'organization_type': organization_type,
                'generated_at': timezone.now()
            }
            
            # Cache for 30 minutes
            cache.set(cache_key, result, 1800)
            
            return result
            
        except EmployeeEnhanced.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"Error organizing enhanced files for employee {employee_id}: {e}")
            raise ValidationError(f"خطأ في تنظيم الملفات: {e}")
    
    def search_files_advanced(self, search_params, user=None):
        """البحث المتقدم في الملفات مع فلترة متطورة"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            
            # Build cache key
            cache_key = f"file_search_enhanced_{hashlib.md5(json.dumps(search_params, sort_keys=True).encode()).hexdigest()}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            files = EmployeeFileEnhanced.objects.select_related(
                'employee', 'uploaded_by'
            ).filter(is_deleted=False)
            
            # Apply security filters
            files = self._apply_file_security_filters(files, user)
            
            # Employee filter
            if search_params.get('employee_id'):
                files = files.filter(employee_id=search_params['employee_id'])
            
            # Department filter
            if search_params.get('department_ids'):
                files = files.filter(employee__department_id__in=search_params['department_ids'])
            
            # File type filter
            if search_params.get('file_types'):
                files = files.filter(file_type__in=search_params['file_types'])
            
            # Confidentiality level filter
            if search_params.get('confidentiality_levels'):
                files = files.filter(confidentiality_level__in=search_params['confidentiality_levels'])
            
            # Date range filters
            if search_params.get('upload_date_from'):
                files = files.filter(uploaded_at__gte=search_params['upload_date_from'])
            if search_params.get('upload_date_to'):
                files = files.filter(uploaded_at__lte=search_params['upload_date_to'])
            
            if search_params.get('document_date_from'):
                files = files.filter(document_date__gte=search_params['document_date_from'])
            if search_params.get('document_date_to'):
                files = files.filter(document_date__lte=search_params['document_date_to'])
            
            # Expiry status filter
            today = date.today()
            if search_params.get('expiry_status'):
                if search_params['expiry_status'] == 'expired':
                    files = files.filter(expiry_date__lt=today)
                elif search_params['expiry_status'] == 'expiring_soon':
                    warning_days = search_params.get('expiry_warning_days', 30)
                    warning_date = today + timedelta(days=warning_days)
                    files = files.filter(
                        expiry_date__lte=warning_date,
                        expiry_date__gte=today
                    )
                elif search_params['expiry_status'] == 'valid':
                    files = files.filter(
                        Q(expiry_date__isnull=True) | Q(expiry_date__gt=today)
                    )
            
            # File size filter
            if search_params.get('min_size'):
                files = files.filter(file_size__gte=search_params['min_size'])
            if search_params.get('max_size'):
                files = files.filter(file_size__lte=search_params['max_size'])
            
            # Text search in multiple fields
            if search_params.get('search_text'):
                search_text = search_params['search_text']
                files = files.filter(
                    Q(title__icontains=search_text) |
                    Q(description__icontains=search_text) |
                    Q(original_filename__icontains=search_text) |
                    Q(document_number__icontains=search_text) |
                    Q(issuing_authority__icontains=search_text) |
                    Q(employee__first_name__icontains=search_text) |
                    Q(employee__last_name__icontains=search_text) |
                    Q(employee__employee_id__icontains=search_text)
                )
            
            # Tags filter
            if search_params.get('tags'):
                for tag in search_params['tags']:
                    files = files.filter(tags__contains=[tag])
            
            # Approval status filter
            if search_params.get('approval_status'):
                if search_params['approval_status'] == 'pending':
                    files = files.filter(requires_approval=True, is_approved=False)
                elif search_params['approval_status'] == 'approved':
                    files = files.filter(is_approved=True)
                elif search_params['approval_status'] == 'rejected':
                    files = files.filter(requires_approval=True, is_approved=False, approval_notes__isnull=False)
            
            # Encryption filter
            if search_params.get('is_encrypted') is not None:
                files = files.filter(metadata__is_encrypted=search_params['is_encrypted'])
            
            # Ordering
            order_by = search_params.get('order_by', '-uploaded_at')
            if search_params.get('order_desc', True):
                if not order_by.startswith('-'):
                    order_by = f'-{order_by}'
            else:
                order_by = order_by.lstrip('-')
            
            files = files.order_by(order_by)
            
            # Pagination
            page = search_params.get('page', 1)
            page_size = min(search_params.get('page_size', 50), 200)
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = files.count()
            files_list = list(files[start:end])
            
            # Calculate statistics
            stats = self._calculate_search_statistics(files)
            
            result = {
                'files': files_list,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'has_next': end < total_count,
                'has_previous': page > 1,
                'statistics': stats,
                'search_params': search_params
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, result, 300)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced file search: {e}")
            raise ValidationError(f"خطأ في البحث المتقدم: {e}")
    
    # =============================================================================
    # FILE OPERATIONS
    # =============================================================================
    
    def download_file_secure(self, file_id, user, track_download=True):
        """تحميل آمن للملف مع تتبع التحميلات"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            
            file = EmployeeFileEnhanced.objects.get(id=file_id, is_deleted=False)
            
            # Check permissions
            if not self._check_file_access_permission(file, user):
                raise ValidationError("ليس لديك صلاحية للوصول لهذا الملف")
            
            # Check file integrity
            if not self._verify_file_integrity(file):
                raise ValidationError("الملف تالف أو تم تعديله")
            
            # Read file content
            if not default_storage.exists(file.file_path):
                raise ValidationError("الملف غير موجود على الخادم")
            
            file_content = default_storage.open(file.file_path, 'rb').read()
            
            # Decrypt if encrypted
            if file.metadata.get('is_encrypted'):
                file_content = self._decrypt_file_content(file_content)
            
            # Track download
            if track_download:
                file.download_count += 1
                file.last_accessed_at = timezone.now()
                file.last_accessed_by = user
                file.save(update_fields=['download_count', 'last_accessed_at', 'last_accessed_by'])
                
                # Log download
                logger.info(f"File {file.title} downloaded by {user.username}")
            
            return {
                'content': file_content,
                'filename': file.original_filename,
                'mime_type': file.mime_type,
                'size': file.file_size
            }
            
        except EmployeeFileEnhanced.DoesNotExist:
            raise ValidationError("الملف غير موجود")
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            raise ValidationError(f"خطأ في تحميل الملف: {e}")
    
    def delete_file_secure(self, file_id, user, reason=None, permanent=False):
        """حذف آمن للملف مع إمكانية الاستعادة"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            
            file = EmployeeFileEnhanced.objects.get(id=file_id)
            
            # Check permissions
            if not self._check_file_delete_permission(file, user):
                raise ValidationError("ليس لديك صلاحية لحذف هذا الملف")
            
            with transaction.atomic():
                if permanent:
                    # Permanent deletion
                    if file.file_path and default_storage.exists(file.file_path):
                        default_storage.delete(file.file_path)
                    
                    # Delete thumbnail if exists
                    if hasattr(file, 'thumbnail_path') and file.thumbnail_path:
                        if default_storage.exists(file.thumbnail_path):
                            default_storage.delete(file.thumbnail_path)
                    
                    file.delete()
                    logger.info(f"File {file.title} permanently deleted by {user.username}")
                else:
                    # Soft deletion
                    file.is_deleted = True
                    file.deleted_at = timezone.now()
                    file.deleted_by = user
                    file.deletion_reason = reason
                    file.save()
                    logger.info(f"File {file.title} soft deleted by {user.username}")
                
                # Clear cache
                self._clear_file_cache(file.employee.id)
            
            return True
            
        except EmployeeFileEnhanced.DoesNotExist:
            raise ValidationError("الملف غير موجود")
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            raise ValidationError(f"خطأ في حذف الملف: {e}")
    
    def restore_deleted_file(self, file_id, user):
        """استعادة ملف محذوف"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            
            file = EmployeeFileEnhanced.objects.get(id=file_id, is_deleted=True)
            
            # Check permissions
            if not self._check_file_restore_permission(file, user):
                raise ValidationError("ليس لديك صلاحية لاستعادة هذا الملف")
            
            # Verify file still exists
            if not default_storage.exists(file.file_path):
                raise ValidationError("الملف الأصلي غير موجود ولا يمكن استعادته")
            
            file.is_deleted = False
            file.deleted_at = None
            file.deleted_by = None
            file.deletion_reason = None
            file.restored_at = timezone.now()
            file.restored_by = user
            file.save()
            
            # Clear cache
            self._clear_file_cache(file.employee.id)
            
            logger.info(f"File {file.title} restored by {user.username}")
            return file
            
        except EmployeeFileEnhanced.DoesNotExist:
            raise ValidationError("الملف المحذوف غير موجود")
        except Exception as e:
            logger.error(f"Error restoring file {file_id}: {e}")
            raise ValidationError(f"خطأ في استعادة الملف: {e}")
    
    def bulk_file_operations(self, file_ids, operation, user, **kwargs):
        """عمليات مجمعة على الملفات"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            
            if len(file_ids) > 100:  # Limit bulk operations
                raise ValidationError("عدد الملفات يتجاوز الحد الأقصى (100)")
            
            files = EmployeeFileEnhanced.objects.filter(id__in=file_ids)
            
            if not files.exists():
                raise ValidationError("لم يتم العثور على ملفات للمعالجة")
            
            results = {
                'success_count': 0,
                'error_count': 0,
                'errors': []
            }
            
            with transaction.atomic():
                for file in files:
                    try:
                        if operation == 'delete':
                            self.delete_file_secure(
                                file.id, user, 
                                reason=kwargs.get('reason'),
                                permanent=kwargs.get('permanent', False)
                            )
                        elif operation == 'update_confidentiality':
                            if self._check_file_update_permission(file, user):
                                file.confidentiality_level = kwargs.get('confidentiality_level')
                                file.save()
                            else:
                                raise ValidationError("ليس لديك صلاحية لتحديث هذا الملف")
                        elif operation == 'add_tags':
                            if self._check_file_update_permission(file, user):
                                new_tags = kwargs.get('tags', [])
                                existing_tags = file.tags or []
                                file.tags = list(set(existing_tags + new_tags))
                                file.save()
                            else:
                                raise ValidationError("ليس لديك صلاحية لتحديث هذا الملف")
                        elif operation == 'approve':
                            if self._check_file_approval_permission(file, user):
                                file.is_approved = True
                                file.approved_by = user
                                file.approved_at = timezone.now()
                                file.approval_notes = kwargs.get('approval_notes')
                                file.save()
                            else:
                                raise ValidationError("ليس لديك صلاحية لاعتماد هذا الملف")
                        else:
                            raise ValidationError(f"العملية {operation} غير مدعومة")
                        
                        results['success_count'] += 1
                        
                    except Exception as e:
                        results['error_count'] += 1
                        results['errors'].append(f"خطأ في معالجة الملف {file.title}: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk file operations: {e}")
            raise ValidationError(f"خطأ في العمليات المجمعة: {e}")
    
    # =============================================================================
    # ANALYTICS AND REPORTING
    # =============================================================================
    
    def get_file_analytics(self, filters=None, user=None):
        """تحليلات شاملة للملفات"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            
            cache_key = f"file_analytics_{hashlib.md5(json.dumps(filters or {}, sort_keys=True).encode()).hexdigest()}"
            cached_analytics = cache.get(cache_key)
            
            if cached_analytics:
                return cached_analytics
            
            files = EmployeeFileEnhanced.objects.filter(is_deleted=False)
            files = self._apply_file_security_filters(files, user)
            
            if filters:
                files = files.filter(**filters)
            
            # Basic statistics
            total_files = files.count()
            total_size = files.aggregate(total_size=Sum('file_size'))['total_size'] or 0
            avg_size = files.aggregate(avg_size=Avg('file_size'))['avg_size'] or 0
            
            # By file type
            by_type = files.values('file_type').annotate(
                count=Count('id'),
                total_size=Sum('file_size'),
                avg_size=Avg('file_size')
            ).order_by('-count')
            
            # By confidentiality level
            by_confidentiality = files.values('confidentiality_level').annotate(
                count=Count('id'),
                total_size=Sum('file_size')
            ).order_by('-count')
            
            # By employee department
            by_department = files.values('employee__department__name').annotate(
                count=Count('id'),
                total_size=Sum('file_size'),
                unique_employees=Count('employee', distinct=True)
            ).order_by('-count')
            
            # Upload trends (last 12 months)
            from django.utils import timezone
            from dateutil.relativedelta import relativedelta
            
            upload_trends = []
            for i in range(12):
                month_start = timezone.now().replace(day=1) - relativedelta(months=i)
                month_end = month_start + relativedelta(months=1) - timedelta(days=1)
                
                month_files = files.filter(
                    uploaded_at__gte=month_start,
                    uploaded_at__lte=month_end
                )
                
                upload_trends.append({
                    'month': month_start.strftime('%Y-%m'),
                    'count': month_files.count(),
                    'size': month_files.aggregate(total=Sum('file_size'))['total'] or 0
                })
            
            upload_trends.reverse()
            
            # Expiry analysis
            today = date.today()
            expired_count = files.filter(expiry_date__lt=today).count()
            expiring_30_days = files.filter(
                expiry_date__gte=today,
                expiry_date__lte=today + timedelta(days=30)
            ).count()
            expiring_90_days = files.filter(
                expiry_date__gte=today,
                expiry_date__lte=today + timedelta(days=90)
            ).count()
            
            # Download statistics
            most_downloaded = files.filter(download_count__gt=0).order_by('-download_count')[:10]
            total_downloads = files.aggregate(total=Sum('download_count'))['total'] or 0
            
            # File age analysis
            file_age_ranges = [
                ('أقل من شهر', 0, 30),
                ('1-3 أشهر', 30, 90),
                ('3-6 أشهر', 90, 180),
                ('6-12 شهر', 180, 365),
                ('أكثر من سنة', 365, 9999)
            ]
            
            age_distribution = []
            for range_name, min_days, max_days in file_age_ranges:
                min_date = today - timedelta(days=max_days)
                max_date = today - timedelta(days=min_days)
                
                count = files.filter(
                    uploaded_at__date__gte=min_date,
                    uploaded_at__date__lte=max_date
                ).count()
                
                age_distribution.append({
                    'range': range_name,
                    'count': count,
                    'percentage': round((count / total_files * 100), 2) if total_files > 0 else 0
                })
            
            analytics = {
                'overview': {
                    'total_files': total_files,
                    'total_size': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'avg_size': avg_size,
                    'avg_size_mb': round(avg_size / (1024 * 1024), 2),
                    'total_downloads': total_downloads,
                },
                'distributions': {
                    'by_type': list(by_type),
                    'by_confidentiality': list(by_confidentiality),
                    'by_department': list(by_department),
                    'age_distribution': age_distribution,
                },
                'trends': {
                    'upload_trends': upload_trends,
                },
                'expiry_analysis': {
                    'expired_count': expired_count,
                    'expiring_30_days': expiring_30_days,
                    'expiring_90_days': expiring_90_days,
                },
                'popular_files': {
                    'most_downloaded': [
                        {
                            'file': f,
                            'downloads': f.download_count,
                            'employee': f.employee.full_name
                        } for f in most_downloaded
                    ]
                },
                'generated_at': timezone.now()
            }
            
            # Cache for 1 hour
            cache.set(cache_key, analytics, 3600)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating file analytics: {e}")
            raise ValidationError(f"خطأ في إنشاء التحليلات: {e}")
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _validate_file_enhanced(self, uploaded_file, file_type):
        """التحقق المتقدم من صحة الملف"""
        errors = []
        warnings = []
        
        try:
            # Get file type configuration
            type_config = self.ALLOWED_FILE_TYPES.get(file_type, self.ALLOWED_FILE_TYPES['other'])
            
            # Check file size
            if uploaded_file.size > type_config['max_size']:
                max_size_mb = type_config['max_size'] / (1024 * 1024)
                errors.append(f"حجم الملف كبير جداً. الحد الأقصى {max_size_mb:.1f} ميجابايت")
            
            # Check file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in type_config['extensions']:
                errors.append(f"نوع الملف غير مدعوم. الأنواع المدعومة: {', '.join(type_config['extensions'])}")
            
            # Check for dangerous files
            dangerous_extensions = ['exe', 'bat', 'cmd', 'scr', 'pif', 'com', 'vbs', 'js']
            if file_extension in dangerous_extensions:
                errors.append("نوع الملف غير آمن")
            
            # Check file content using python-magic
            if hasattr(magic, 'from_buffer'):
                file_content = uploaded_file.read(1024)  # Read first 1KB
                uploaded_file.seek(0)  # Reset file pointer
                
                detected_type = magic.from_buffer(file_content, mime=True)
                expected_types = self._get_expected_mime_types(file_extension)
                
                if detected_type not in expected_types:
                    warnings.append(f"نوع الملف المكتشف ({detected_type}) لا يطابق الامتداد")
            
            # Check for empty files
            if uploaded_file.size == 0:
                errors.append("الملف فارغ")
            
            # Check filename
            if len(uploaded_file.name) > 255:
                errors.append("اسم الملف طويل جداً")
            
            # Check for special characters in filename
            import re
            if not re.match(r'^[a-zA-Z0-9._\-\u0600-\u06FF\s]+$', uploaded_file.name):
                warnings.append("اسم الملف يحتوي على رموز خاصة")
            
            return {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f"خطأ في التحقق من الملف: {e}"],
                'warnings': []
            }
    
    def _get_expected_mime_types(self, extension):
        """الحصول على أنواع MIME المتوقعة للامتداد"""
        mime_map = {
            'pdf': ['application/pdf'],
            'doc': ['application/msword'],
            'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            'xls': ['application/vnd.ms-excel'],
            'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            'jpg': ['image/jpeg'],
            'jpeg': ['image/jpeg'],
            'png': ['image/png'],
            'gif': ['image/gif'],
            'txt': ['text/plain'],
            'zip': ['application/zip'],
            'rar': ['application/x-rar-compressed'],
        }
        return mime_map.get(extension, [])
    
    def _scan_file_for_viruses(self, uploaded_file):
        """فحص الملف للفيروسات (يتطلب ClamAV أو مشابه)"""
        # This would integrate with antivirus software
        # For now, return clean
        return {
            'is_clean': True,
            'threat': None,
            'scan_time': timezone.now()
        }
    
    def _is_sensitive_file_type(self, file_type):
        """تحديد ما إذا كان نوع الملف حساساً"""
        sensitive_types = ['identity', 'passport', 'visa', 'bank', 'medical', 'contract']
        return file_type in sensitive_types
    
    def _encrypt_file_content(self, content):
        """تشفير محتوى الملف"""
        # This would use proper encryption
        # For now, return as-is
        return content
    
    def _decrypt_file_content(self, content):
        """فك تشفير محتوى الملف"""
        # This would use proper decryption
        # For now, return as-is
        return content
    
    def _save_file_securely(self, filename, content, employee_id):
        """حفظ الملف بشكل آمن"""
        # Create employee-specific directory
        file_path = f'employee_files/{employee_id}/{filename}'
        
        # Save file
        from django.core.files.base import ContentFile
        return default_storage.save(file_path, ContentFile(content))
    
    def _generate_unique_filename(self, original_filename, employee_id):
        """إنشاء اسم ملف فريد"""
        import uuid
        from datetime import datetime
        
        # Get file extension
        file_extension = original_filename.split('.')[-1].lower()
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{employee_id}_{timestamp}_{unique_id}.{file_extension}"
    
    def _extract_file_metadata(self, uploaded_file):
        """استخراج البيانات الوصفية للملف"""
        metadata = {
            'original_size': uploaded_file.size,
            'upload_timestamp': timezone.now().isoformat(),
        }
        
        # Extract image metadata if it's an image
        if self._is_image_file(uploaded_file.name):
            try:
                image = Image.open(uploaded_file)
                metadata.update({
                    'image_width': image.width,
                    'image_height': image.height,
                    'image_format': image.format,
                    'image_mode': image.mode
                })
                
                # Extract EXIF data if available
                if hasattr(image, '_getexif') and image._getexif():
                    exif = image._getexif()
                    if exif:
                        metadata['exif_data'] = {k: str(v) for k, v in exif.items() if isinstance(v, (str, int, float))}
                
                uploaded_file.seek(0)  # Reset file pointer
            except Exception as e:
                logger.warning(f"Could not extract image metadata: {e}")
        
        return metadata
    
    def _is_image_file(self, filename):
        """تحديد ما إذا كان الملف صورة"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
        extension = filename.split('.')[-1].lower()
        return extension in image_extensions
    
    def _generate_thumbnail(self, file_obj, file_content):
        """إنشاء صورة مصغرة للملف"""
        try:
            if not self._is_image_file(file_obj.original_filename):
                return
            
            image = Image.open(BytesIO(file_content))
            
            # Create thumbnail
            thumbnail_size = (200, 200)
            image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumbnail_io = BytesIO()
            image.save(thumbnail_io, format='JPEG', quality=85)
            thumbnail_content = thumbnail_io.getvalue()
            
            # Generate thumbnail filename
            thumbnail_filename = f"thumb_{file_obj.id}.jpg"
            thumbnail_path = f'employee_files/thumbnails/{thumbnail_filename}'
            
            # Save thumbnail
            from django.core.files.base import ContentFile
            thumbnail_path = default_storage.save(thumbnail_path, ContentFile(thumbnail_content))
            
            # Update file object
            file_obj.thumbnail_path = thumbnail_path
            file_obj.save(update_fields=['thumbnail_path'])
            
        except Exception as e:
            logger.warning(f"Could not generate thumbnail for file {file_obj.id}: {e}")
    
    def _check_file_integrity(self, file_obj):
        """فحص سلامة الملف"""
        try:
            if not default_storage.exists(file_obj.file_path):
                return {'status': 'missing', 'message': 'الملف غير موجود'}
            
            # Check file hash if available
            if file_obj.file_hash:
                current_content = default_storage.open(file_obj.file_path, 'rb').read()
                current_hash = hashlib.sha256(current_content).hexdigest()
                
                if current_hash != file_obj.file_hash:
                    return {'status': 'corrupted', 'message': 'الملف تالف أو تم تعديله'}
            
            return {'status': 'ok', 'message': 'الملف سليم'}
            
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في فحص الملف: {e}'}
    
    def _verify_file_integrity(self, file_obj):
        """التحقق من سلامة الملف"""
        integrity_status = self._check_file_integrity(file_obj)
        return integrity_status['status'] == 'ok'
    
    def _predict_future_expirations(self):
        """تنبؤ بانتهاء الصلاحيات المستقبلية"""
        try:
            from ..models.employee.employee_file_models import EmployeeFileEnhanced
            
            today = date.today()
            predictions = {}
            
            # Predict for next 12 months
            for months_ahead in [1, 3, 6, 12]:
                future_date = today + timedelta(days=months_ahead * 30)
                
                expiring_count = EmployeeFileEnhanced.objects.filter(
                    expiry_date__gte=today,
                    expiry_date__lte=future_date,
                    is_deleted=False
                ).count()
                
                predictions[f'{months_ahead}_months'] = {
                    'count': expiring_count,
                    'date': future_date
                }
            
            return predictions
            
        except Exception as e:
            logger.warning(f"Could not generate expiration predictions: {e}")
            return {}
    
    def _calculate_search_statistics(self, files_queryset):
        """حساب إحصائيات البحث"""
        try:
            total_size = files_queryset.aggregate(total=Sum('file_size'))['total'] or 0
            avg_size = files_queryset.aggregate(avg=Avg('file_size'))['avg'] or 0
            
            by_type = files_queryset.values('file_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            by_confidentiality = files_queryset.values('confidentiality_level').annotate(
                count=Count('id')
            ).order_by('-count')
            
            return {
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'avg_size': avg_size,
                'avg_size_mb': round(avg_size / (1024 * 1024), 2),
                'by_type': list(by_type),
                'by_confidentiality': list(by_confidentiality)
            }
            
        except Exception as e:
            logger.warning(f"Could not calculate search statistics: {e}")
            return {}
    
    def _apply_file_security_filters(self, queryset, user):
        """تطبيق فلاتر الأمان على الملفات"""
        if not user:
            return queryset.none()
        
        # Super admin can see all files
        if user.is_superuser:
            return queryset
        
        # Apply confidentiality level restrictions
        if hasattr(user, 'hr_permissions'):
            # Check user's maximum confidentiality level access
            max_level = 1  # Default to public only
            
            if user.hr_permissions.filter(module='employee_files', permission_level='view_confidential').exists():
                max_level = 3
            elif user.hr_permissions.filter(module='employee_files', permission_level='view_internal').exists():
                max_level = 2
            
            # Filter based on confidentiality level
            allowed_levels = [level for level, config in self.CONFIDENTIALITY_LEVELS.items() 
                            if config['level'] <= max_level]
            
            queryset = queryset.filter(confidentiality_level__in=allowed_levels)
        
        return queryset
    
    def _check_file_access_permission(self, file, user):
        """التحقق من صلاحية الوصول للملف"""
        if not user:
            return False
        
        # Super admin can access all files
        if user.is_superuser:
            return True
        
        # File uploader can access
        if file.uploaded_by == user:
            return True
        
        # Employee can access their own files
        if hasattr(user, 'employee_profile') and file.employee == user.employee_profile:
            return True
        
        # Check confidentiality level permissions
        file_level = self.CONFIDENTIALITY_LEVELS[file.confidentiality_level]['level']
        
        if hasattr(user, 'hr_permissions'):
            if file_level <= 1:  # Public
                return True
            elif file_level <= 2 and user.hr_permissions.filter(module='employee_files', permission_level='view_internal').exists():
                return True
            elif file_level <= 3 and user.hr_permissions.filter(module='employee_files', permission_level='view_confidential').exists():
                return True
            elif file_level <= 4 and user.hr_permissions.filter(module='employee_files', permission_level='view_highly_confidential').exists():
                return True
            elif file_level <= 5 and user.hr_permissions.filter(module='employee_files', permission_level='view_restricted').exists():
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
        if hasattr(user, 'hr_permissions') and user.hr_permissions.filter(
            module='employee_files', permission_level='delete'
        ).exists():
            return True
        
        return False
    
    def _check_file_update_permission(self, file, user):
        """التحقق من صلاحية تحديث الملف"""
        if not user:
            return False
        
        # Super admin can update all files
        if user.is_superuser:
            return True
        
        # File uploader can update
        if file.uploaded_by == user:
            return True
        
        # HR admin can update
        if hasattr(user, 'hr_permissions') and user.hr_permissions.filter(
            module='employee_files', permission_level='change'
        ).exists():
            return True
        
        return False
    
    def _check_file_approval_permission(self, file, user):
        """التحقق من صلاحية اعتماد الملف"""
        if not user:
            return False
        
        # Super admin can approve all files
        if user.is_superuser:
            return True
        
        # HR manager can approve
        if hasattr(user, 'hr_permissions') and user.hr_permissions.filter(
            module='employee_files', permission_level='approve'
        ).exists():
            return True
        
        return False
    
    def _check_file_restore_permission(self, file, user):
        """التحقق من صلاحية استعادة الملف"""
        if not user:
            return False
        
        # Super admin can restore all files
        if user.is_superuser:
            return True
        
        # HR admin can restore
        if hasattr(user, 'hr_permissions') and user.hr_permissions.filter(
            module='employee_files', permission_level='restore'
        ).exists():
            return True
        
        return False
    
    def _clear_file_cache(self, employee_id=None):
        """مسح الكاش المتعلق بالملفات"""
        if employee_id:
            # Clear specific employee file cache
            cache.delete_many([
                f"employee_files_organized_{employee_id}_type",
                f"employee_files_organized_{employee_id}_date",
                f"employee_files_organized_{employee_id}_confidentiality",
                f"employee_files_organized_{employee_id}_status"
            ])
        else:
            # Clear general file caches
            cache.delete_pattern("file_*")
            cache.delete_pattern("employee_files_*")


# Create a singleton instance
file_service_enhanced = EmployeeFileServiceEnhanced()