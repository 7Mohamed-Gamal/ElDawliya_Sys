"""
خدمة إدارة المهام وتتبع التقدم
Task Management and Progress Tracking Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Q
from core.services.base import BaseService
from core.models.projects import Task, TaskComment, TaskAttachment, TaskDependency


class TaskService(BaseService):
    """
    خدمة إدارة المهام وتتبع التقدم
    Task management and progress tracking service
    """
    
    def create_task(self, data):
        """إنشاء مهمة جديدة"""
        self.check_permission('projects.add_task')
        
        required_fields = ['title', 'project_id', 'assigned_to_id']
        self.validate_required_fields(data, required_fields)
        
        try:
            from core.models.projects import Project
            from core.models.hr import Employee
            
            project = Project.objects.get(id=data['project_id'])
            assigned_to = Employee.objects.get(id=data['assigned_to_id'])
            
            with transaction.atomic():
                task = Task.objects.create(
                    project=project,
                    title=data['title'],
                    description=data.get('description', ''),
                    assigned_to=assigned_to,
                    priority=data.get('priority', 'medium'),
                    status='pending',
                    due_date=data.get('due_date'),
                    estimated_hours=data.get('estimated_hours', 0),
                    created_by=self.user,
                    updated_by=self.user
                )
                
                # Add dependencies if provided
                if data.get('dependencies'):
                    self._add_task_dependencies(task, data['dependencies'])
                
                self.log_action(
                    action='create',
                    resource='task',
                    content_object=task,
                    message=f'تم إنشاء مهمة جديدة: {task.title}'
                )
                
                return self.format_response(
                    data={'task_id': task.id},
                    message='تم إنشاء المهمة بنجاح'
                )
                
        except (Project.DoesNotExist, Employee.DoesNotExist) as e:
            return self.format_response(
                success=False,
                message='المشروع أو الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'create_task', 'task', data)
    
    def update_task_status(self, task_id, new_status, progress_percentage=None, notes=None):
        """تحديث حالة المهمة"""
        self.check_permission('projects.change_task')
        
        try:
            task = Task.objects.get(id=task_id)
            
            old_status = task.status
            task.status = new_status
            
            if progress_percentage is not None:
                task.progress_percentage = progress_percentage
            
            if new_status == 'completed':
                task.completed_at = timezone.now()
                task.progress_percentage = 100
            
            task.updated_by = self.user
            task.save()
            
            # Add comment if notes provided
            if notes:
                TaskComment.objects.create(
                    task=task,
                    comment=notes,
                    comment_type='status_update',
                    created_by=self.user,
                    updated_by=self.user
                )
            
            self.log_action(
                action='status_update',
                resource='task',
                content_object=task,
                old_values={'status': old_status},
                new_values={'status': new_status},
                message=f'تم تحديث حالة المهمة: {task.title}'
            )
            
            return self.format_response(
                message='تم تحديث حالة المهمة بنجاح'
            )
            
        except Task.DoesNotExist:
            return self.format_response(
                success=False,
                message='المهمة غير موجودة'
            )
        except Exception as e:
            return self.handle_exception(e, 'update_task_status', f'task_status/{task_id}')
    
    def get_tasks(self, filters=None, page=1, page_size=20):
        """الحصول على قائمة المهام"""
        self.check_permission('projects.view_task')
        
        try:
            queryset = Task.objects.select_related('project', 'assigned_to')
            
            if filters:
                if filters.get('project_id'):
                    queryset = queryset.filter(project_id=filters['project_id'])
                if filters.get('assigned_to_id'):
                    queryset = queryset.filter(assigned_to_id=filters['assigned_to_id'])
                if filters.get('status'):
                    queryset = queryset.filter(status=filters['status'])
                if filters.get('priority'):
                    queryset = queryset.filter(priority=filters['priority'])
            
            queryset = queryset.order_by('-created_at')
            paginated_data = self.paginate_queryset(queryset, page, page_size)
            
            tasks = []
            for task in paginated_data['results']:
                tasks.append({
                    'id': task.id,
                    'title': task.title,
                    'project_name': task.project.name_ar,
                    'assigned_to': task.assigned_to.get_full_name() if task.assigned_to else '',
                    'status': task.status,
                    'priority': task.priority,
                    'due_date': task.due_date,
                    'progress_percentage': task.progress_percentage,
                })
            
            paginated_data['results'] = tasks
            
            return self.format_response(
                data=paginated_data,
                message='تم الحصول على قائمة المهام بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'get_tasks', 'tasks', filters)
    
    def _add_task_dependencies(self, task, dependencies):
        """إضافة تبعيات المهمة"""
        for dep_id in dependencies:
            try:
                dependent_task = Task.objects.get(id=dep_id)
                TaskDependency.objects.create(
                    task=task,
                    dependent_task=dependent_task,
                    dependency_type='finish_to_start',
                    created_by=self.user,
                    updated_by=self.user
                )
            except Task.DoesNotExist:
                self.logger.warning(f"Dependent task {dep_id} not found")