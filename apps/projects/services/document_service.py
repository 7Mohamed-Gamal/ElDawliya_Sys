"""
خدمة إدارة الوثائق والملفات
Document Management Service
"""
from django.db import transaction
from django.utils import timezone
from core.services.base import BaseService
from core.models.projects import Document, DocumentVersion, DocumentAccess


class DocumentService(BaseService):
    """
    خدمة إدارة الوثائق والملفات
    Document and file management service
    """
    
    def upload_document(self, data):
        """رفع وثيقة جديدة"""
        self.check_permission('projects.add_document')
        
        required_fields = ['title', 'file_path', 'document_type']
        self.validate_required_fields(data, required_fields)
        
        try:
            with transaction.atomic():
                document = Document.objects.create(
                    title=data['title'],
                    description=data.get('description', ''),
                    document_type=data['document_type'],
                    file_path=data['file_path'],
                    file_size=data.get('file_size', 0),
                    mime_type=data.get('mime_type', ''),
                    project_id=data.get('project_id'),
                    version_number=1,
                    is_active=True,
                    uploaded_by=self.user,
                    created_by=self.user,
                    updated_by=self.user
                )
                
                # Create initial version
                DocumentVersion.objects.create(
                    document=document,
                    version_number=1,
                    file_path=data['file_path'],
                    file_size=data.get('file_size', 0),
                    change_notes=data.get('change_notes', 'الإصدار الأولي'),
                    uploaded_by=self.user,
                    created_by=self.user,
                    updated_by=self.user
                )
                
                self.log_action(
                    action='upload',
                    resource='document',
                    content_object=document,
                    message=f'تم رفع وثيقة جديدة: {document.title}'
                )
                
                return self.format_response(
                    data={'document_id': document.id},
                    message='تم رفع الوثيقة بنجاح'
                )
                
        except Exception as e:
            return self.handle_exception(e, 'upload_document', 'document', data)
    
    def create_new_version(self, document_id, version_data):
        """إنشاء إصدار جديد من الوثيقة"""
        self.check_permission('projects.change_document')
        
        try:
            document = Document.objects.get(id=document_id)
            
            # Get next version number
            next_version = document.version_number + 1
            
            with transaction.atomic():
                # Create new version
                DocumentVersion.objects.create(
                    document=document,
                    version_number=next_version,
                    file_path=version_data['file_path'],
                    file_size=version_data.get('file_size', 0),
                    change_notes=version_data.get('change_notes', ''),
                    uploaded_by=self.user,
                    created_by=self.user,
                    updated_by=self.user
                )
                
                # Update document
                document.version_number = next_version
                document.file_path = version_data['file_path']
                document.file_size = version_data.get('file_size', 0)
                document.updated_by = self.user
                document.save()
                
                self.log_action(
                    action='new_version',
                    resource='document_version',
                    content_object=document,
                    message=f'تم إنشاء إصدار جديد للوثيقة: {document.title} v{next_version}'
                )
                
                return self.format_response(
                    data={'version_number': next_version},
                    message='تم إنشاء إصدار جديد بنجاح'
                )
                
        except Document.DoesNotExist:
            return self.format_response(
                success=False,
                message='الوثيقة غير موجودة'
            )
        except Exception as e:
            return self.handle_exception(e, 'create_new_version', f'document_version/{document_id}')
    
    def grant_document_access(self, document_id, access_data):
        """منح صلاحية الوصول للوثيقة"""
        self.check_permission('projects.change_document')
        
        try:
            document = Document.objects.get(id=document_id)
            
            from core.models.hr import Employee
            employee = Employee.objects.get(id=access_data['employee_id'])
            
            # Check if access already exists
            existing_access = DocumentAccess.objects.filter(
                document=document,
                employee=employee
            ).first()
            
            if existing_access:
                existing_access.access_level = access_data['access_level']
                existing_access.updated_by = self.user
                existing_access.save()
            else:
                DocumentAccess.objects.create(
                    document=document,
                    employee=employee,
                    access_level=access_data['access_level'],
                    granted_by=self.user,
                    created_by=self.user,
                    updated_by=self.user
                )
            
            self.log_action(
                action='grant_access',
                resource='document_access',
                content_object=document,
                message=f'تم منح صلاحية الوصول للوثيقة: {employee.get_full_name()}'
            )
            
            return self.format_response(
                message='تم منح صلاحية الوصول بنجاح'
            )
            
        except (Document.DoesNotExist, Employee.DoesNotExist):
            return self.format_response(
                success=False,
                message='الوثيقة أو الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'grant_document_access', f'document_access/{document_id}')