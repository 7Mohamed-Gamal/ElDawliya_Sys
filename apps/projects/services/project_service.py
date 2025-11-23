"""
خدمة إدارة المشاريع الشاملة
Comprehensive Project Management Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q, F
from decimal import Decimal
from datetime import date, timedelta
from core.services.base import BaseService
from core.models.projects import (
    Project, ProjectPhase, ProjectMilestone, ProjectTeamMember,
    ProjectBudget, ProjectRisk, ProjectStatus
)


class ProjectService(BaseService):
    """
    خدمة إدارة المشاريع الشاملة
    Comprehensive project management service
    """
    
    def create_project(self, data):
        """
        إنشاء مشروع جديد
        Create new project
        """
        self.check_permission('projects.add_project')
        
        required_fields = ['name_ar', 'name_en', 'start_date', 'end_date', 'project_manager_id']
        self.validate_required_fields(data, required_fields)
        
        try:
            from core.models.hr import Employee
            
            project_manager = Employee.objects.get(id=data['project_manager_id'])
            
            with transaction.atomic():
                # Generate project code
                project_code = self._generate_project_code()
                
                # Create project
                project_data = self.clean_data(data, [
                    'name_ar', 'name_en', 'description_ar', 'description_en',
                    'start_date', 'end_date', 'budget', 'priority', 'project_type',
                    'client_name', 'client_contact', 'objectives', 'deliverables'
                ])
                
                project = Project.objects.create(
                    project_code=project_code,
                    project_manager=project_manager,
                    status='planning',
                    **project_data,
                    created_by=self.user,
                    updated_by=self.user
                )
                
                # Add team members if provided
                if data.get('team_members'):
                    self._add_team_members(project, data['team_members'])
                
                # Add project phases if provided
                if data.get('phases'):
                    self._add_project_phases(project, data['phases'])
                
                # Create initial budget record
                if data.get('budget'):
                    ProjectBudget.objects.create(
                        project=project,
                        budget_type='initial',
                        allocated_amount=data['budget'],
                        description='الميزانية الأولية للمشروع',
                        created_by=self.user,
                        updated_by=self.user
                    )
                
                # Log the action
                self.log_action(
                    action='create',
                    resource='project',
                    content_object=project,
                    new_values=project_data,
                    message=f'تم إنشاء مشروع جديد: {project.name_ar}'
                )
                
                return self.format_response(
                    data={
                        'project_id': project.id,
                        'project_code': project_code,
                        'name': project.name_ar
                    },
                    message='تم إنشاء المشروع بنجاح'
                )
                
        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='مدير المشروع غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'create_project', 'project', data)
    
    def update_project(self, project_id, data):
        """
        تحديث بيانات المشروع
        Update project information
        """
        self.check_permission('projects.change_project')
        
        try:
            project = Project.objects.get(id=project_id)
            
            # Check object-level permission
            self.check_object_permission('projects.change_project', project)
            
            # Get old values for audit
            old_values, new_values = self.get_model_changes(project, data)
            
            # Update project data
            allowed_fields = [
                'name_ar', 'name_en', 'description_ar', 'description_en',
                'start_date', 'end_date', 'budget', 'priority', 'project_type',
                'client_name', 'client_contact', 'objectives', 'deliverables',
                'project_manager_id', 'status'
            ]
            
            for field, value in data.items():
                if field in allowed_fields and hasattr(project, field):
                    setattr(project, field, value)
            
            project.updated_by = self.user
            project.save()
            
            # Log the action
            self.log_action(
                action='update',
                resource='project',
                content_object=project,
                old_values=old_values,
                new_values=new_values,
                message=f'تم تحديث بيانات المشروع: {project.name_ar}'
            )
            
            # Invalidate cache
            self.invalidate_cache(f'project_{project_id}_*')
            
            return self.format_response(
                data={
                    'project_id': project.id,
                    'updated_fields': list(new_values.keys())
                },
                message='تم تحديث بيانات المشروع بنجاح'
            )
            
        except Project.DoesNotExist:
            return self.format_response(
                success=False,
                message='المشروع غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'update_project', f'project/{project_id}', data)
    
    def get_project(self, project_id, include_details=True):
        """
        الحصول على بيانات المشروع
        Get project details
        """
        self.check_permission('projects.view_project')
        
        try:
            cache_key = self.cache_key('project', project_id, 'details', include_details)
            
            def get_project_data():
                queryset = Project.objects.select_related('project_manager')
                
                if include_details:
                    queryset = queryset.prefetch_related(
                        'team_members__employee', 'phases', 'milestones', 
                        'tasks', 'budget_records'
                    )
                
                project = queryset.get(id=project_id)
                
                # Check object-level permission
                self.check_object_permission('projects.view_project', project)
                
                project_data = {
                    'id': project.id,
                    'project_code': project.project_code,
                    'name_ar': project.name_ar,
                    'name_en': project.name_en,
                    'description_ar': project.description_ar,
                    'start_date': project.start_date,
                    'end_date': project.end_date,
                    'budget': project.budget,
                    'priority': project.priority,
                    'project_type': project.project_type,
                    'status': project.status,
                    'client_name': project.client_name,
                    'client_contact': project.client_contact,
                    'objectives': project.objectives,
                    'deliverables': project.deliverables,
                    'project_manager': {
                        'id': project.project_manager.id,
                        'name': project.project_manager.get_full_name(),
                        'email': project.project_manager.email,
                    } if project.project_manager else None,
                    'created_at': project.created_at,
                    'progress_percentage': self._calculate_project_progress(project),
                }
                
                if include_details:
                    # Add team members
                    team_members = []
                    for member in project.team_members.all():
                        team_members.append({
                            'id': member.id,
                            'employee_name': member.employee.get_full_name(),
                            'role': member.role,
                            'responsibilities': member.responsibilities,
                            'allocation_percentage': member.allocation_percentage,
                            'joined_date': member.joined_date,
                        })
                    project_data['team_members'] = team_members
                    
                    # Add phases
                    phases = []
                    for phase in project.phases.all():
                        phases.append({
                            'id': phase.id,
                            'name': phase.name,
                            'description': phase.description,
                            'start_date': phase.start_date,
                            'end_date': phase.end_date,
                            'status': phase.status,
                            'progress_percentage': phase.progress_percentage,
                        })
                    project_data['phases'] = phases
                    
                    # Add budget summary
                    budget_records = project.budget_records.all()
                    total_allocated = sum(b.allocated_amount for b in budget_records)
                    total_spent = sum(b.spent_amount for b in budget_records)
                    
                    project_data['budget_summary'] = {
                        'total_allocated': total_allocated,
                        'total_spent': total_spent,
                        'remaining_budget': total_allocated - total_spent,
                        'budget_utilization': (total_spent / total_allocated * 100) if total_allocated > 0 else 0
                    }
                
                return project_data
            
            project_data = self.get_from_cache(cache_key)
            if not project_data:
                project_data = get_project_data()
                self.set_cache(cache_key, project_data, 300)  # 5 minutes
            
            return self.format_response(
                data=project_data,
                message='تم الحصول على بيانات المشروع بنجاح'
            )
            
        except Project.DoesNotExist:
            return self.format_response(
                success=False,
                message='المشروع غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_project', f'project/{project_id}')
    
    def get_projects_list(self, filters=None, page=1, page_size=20):
        """
        الحصول على قائمة المشاريع
        Get projects list with filters
        """
        self.check_permission('projects.view_project')
        
        try:
            queryset = Project.objects.select_related('project_manager')
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    queryset = queryset.filter(status=filters['status'])
                
                if filters.get('project_type'):
                    queryset = queryset.filter(project_type=filters['project_type'])
                
                if filters.get('priority'):
                    queryset = queryset.filter(priority=filters['priority'])
                
                if filters.get('project_manager_id'):
                    queryset = queryset.filter(project_manager_id=filters['project_manager_id'])
                
                if filters.get('start_date'):
                    queryset = queryset.filter(start_date__gte=filters['start_date'])
                
                if filters.get('end_date'):
                    queryset = queryset.filter(end_date__lte=filters['end_date'])
                
                if filters.get('search_term'):
                    term = filters['search_term']
                    queryset = queryset.filter(
                        Q(name_ar__icontains=term) |
                        Q(name_en__icontains=term) |
                        Q(project_code__icontains=term) |
                        Q(client_name__icontains=term)
                    )
            
            # Apply user-level filtering if not admin
            if not self.user.is_superuser and not self.user.has_perm('projects.view_all_projects'):
                # Show only projects where user is manager or team member
                user_employee = getattr(self.user, 'employee', None)
                if user_employee:
                    queryset = queryset.filter(
                        Q(project_manager=user_employee) |
                        Q(team_members__employee=user_employee)
                    ).distinct()
            
            queryset = queryset.order_by('-created_at')
            
            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)
            
            # Format project data
            projects = []
            for project in paginated_data['results']:
                projects.append({
                    'id': project.id,
                    'project_code': project.project_code,
                    'name_ar': project.name_ar,
                    'name_en': project.name_en,
                    'project_manager': project.project_manager.get_full_name() if project.project_manager else '',
                    'start_date': project.start_date,
                    'end_date': project.end_date,
                    'budget': project.budget,
                    'priority': project.priority,
                    'status': project.status,
                    'client_name': project.client_name,
                    'progress_percentage': self._calculate_project_progress(project),
                    'days_remaining': (project.end_date - timezone.now().date()).days if project.end_date else None,
                })
            
            paginated_data['results'] = projects
            
            return self.format_response(
                data=paginated_data,
                message='تم الحصول على قائمة المشاريع بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'get_projects_list', 'projects_list', filters)
    
    def add_team_member(self, project_id, member_data):
        """
        إضافة عضو فريق للمشروع
        Add team member to project
        """
        self.check_permission('projects.change_project')
        
        required_fields = ['employee_id', 'role']
        self.validate_required_fields(member_data, required_fields)
        
        try:
            project = Project.objects.get(id=project_id)
            
            from core.models.hr import Employee
            employee = Employee.objects.get(id=member_data['employee_id'])
            
            # Check if employee is already a team member
            if ProjectTeamMember.objects.filter(project=project, employee=employee).exists():
                return self.format_response(
                    success=False,
                    message='الموظف عضو في فريق المشروع بالفعل'
                )
            
            # Add team member
            team_member = ProjectTeamMember.objects.create(
                project=project,
                employee=employee,
                role=member_data['role'],
                responsibilities=member_data.get('responsibilities', ''),
                allocation_percentage=member_data.get('allocation_percentage', 100),
                joined_date=member_data.get('joined_date', timezone.now().date()),
                created_by=self.user,
                updated_by=self.user
            )
            
            # Log the action
            self.log_action(
                action='add_member',
                resource='project_team',
                content_object=project,
                details={
                    'employee_id': employee.id,
                    'employee_name': employee.get_full_name(),
                    'role': member_data['role']
                },
                message=f'تم إضافة عضو فريق للمشروع: {employee.get_full_name()}'
            )
            
            return self.format_response(
                data={'team_member_id': team_member.id},
                message='تم إضافة عضو الفريق بنجاح'
            )
            
        except Project.DoesNotExist:
            return self.format_response(
                success=False,
                message='المشروع غير موجود'
            )
        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'add_team_member', f'project_team/{project_id}', member_data)
    
    def create_milestone(self, project_id, milestone_data):
        """
        إنشاء معلم للمشروع
        Create project milestone
        """
        self.check_permission('projects.add_projectmilestone')
        
        required_fields = ['name', 'target_date']
        self.validate_required_fields(milestone_data, required_fields)
        
        try:
            project = Project.objects.get(id=project_id)
            
            milestone = ProjectMilestone.objects.create(
                project=project,
                name=milestone_data['name'],
                description=milestone_data.get('description', ''),
                target_date=milestone_data['target_date'],
                deliverables=milestone_data.get('deliverables', ''),
                success_criteria=milestone_data.get('success_criteria', ''),
                status='pending',
                created_by=self.user,
                updated_by=self.user
            )
            
            # Log the action
            self.log_action(
                action='create',
                resource='project_milestone',
                content_object=milestone,
                new_values=milestone_data,
                message=f'تم إنشاء معلم جديد للمشروع: {milestone.name}'
            )
            
            return self.format_response(
                data={'milestone_id': milestone.id},
                message='تم إنشاء المعلم بنجاح'
            )
            
        except Project.DoesNotExist:
            return self.format_response(
                success=False,
                message='المشروع غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'create_milestone', f'project_milestone/{project_id}', milestone_data)
    
    def update_project_status(self, project_id, new_status, notes=None):
        """
        تحديث حالة المشروع
        Update project status
        """
        self.check_permission('projects.change_project')
        
        try:
            project = Project.objects.get(id=project_id)
            
            old_status = project.status
            project.status = new_status
            project.updated_by = self.user
            
            # Set completion date if project is completed
            if new_status == 'completed' and not project.actual_end_date:
                project.actual_end_date = timezone.now().date()
            
            project.save()
            
            # Create status record
            ProjectStatus.objects.create(
                project=project,
                status=new_status,
                status_date=timezone.now().date(),
                notes=notes,
                changed_by=self.user,
                created_by=self.user,
                updated_by=self.user
            )
            
            # Log the action
            self.log_action(
                action='status_change',
                resource='project_status',
                content_object=project,
                old_values={'status': old_status},
                new_values={'status': new_status},
                details={'notes': notes},
                message=f'تم تغيير حالة المشروع من {old_status} إلى {new_status}'
            )
            
            return self.format_response(
                data={
                    'project_id': project.id,
                    'old_status': old_status,
                    'new_status': new_status
                },
                message='تم تحديث حالة المشروع بنجاح'
            )
            
        except Project.DoesNotExist:
            return self.format_response(
                success=False,
                message='المشروع غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'update_project_status', f'project_status/{project_id}')
    
    def get_project_dashboard(self, project_id):
        """
        الحصول على لوحة تحكم المشروع
        Get project dashboard data
        """
        self.check_permission('projects.view_project')
        
        try:
            project = Project.objects.select_related('project_manager').get(id=project_id)
            
            # Check object-level permission
            self.check_object_permission('projects.view_project', project)
            
            # Get project statistics
            from core.models.projects import Task
            
            tasks_stats = Task.objects.filter(project=project).aggregate(
                total_tasks=Count('id'),
                completed_tasks=Count('id', filter=Q(status='completed')),
                in_progress_tasks=Count('id', filter=Q(status='in_progress')),
                overdue_tasks=Count('id', filter=Q(
                    due_date__lt=timezone.now().date(),
                    status__in=['pending', 'in_progress']
                ))
            )
            
            # Calculate progress
            progress_percentage = self._calculate_project_progress(project)
            
            # Get recent activities (last 10)
            recent_activities = []
            # This would get recent tasks, milestones, etc.
            
            # Get upcoming milestones
            upcoming_milestones = project.milestones.filter(
                target_date__gte=timezone.now().date(),
                status__in=['pending', 'in_progress']
            ).order_by('target_date')[:5]
            
            milestones_data = []
            for milestone in upcoming_milestones:
                milestones_data.append({
                    'id': milestone.id,
                    'name': milestone.name,
                    'target_date': milestone.target_date,
                    'status': milestone.status,
                    'days_remaining': (milestone.target_date - timezone.now().date()).days
                })
            
            # Get budget utilization
            budget_records = project.budget_records.all()
            total_allocated = sum(b.allocated_amount for b in budget_records)
            total_spent = sum(b.spent_amount for b in budget_records)
            
            dashboard_data = {
                'project': {
                    'id': project.id,
                    'name': project.name_ar,
                    'status': project.status,
                    'progress_percentage': progress_percentage,
                    'start_date': project.start_date,
                    'end_date': project.end_date,
                    'days_remaining': (project.end_date - timezone.now().date()).days if project.end_date else None,
                },
                'tasks_summary': tasks_stats,
                'budget_summary': {
                    'total_allocated': total_allocated,
                    'total_spent': total_spent,
                    'remaining_budget': total_allocated - total_spent,
                    'utilization_percentage': (total_spent / total_allocated * 100) if total_allocated > 0 else 0
                },
                'upcoming_milestones': milestones_data,
                'recent_activities': recent_activities,
            }
            
            return self.format_response(
                data=dashboard_data,
                message='تم الحصول على لوحة تحكم المشروع بنجاح'
            )
            
        except Project.DoesNotExist:
            return self.format_response(
                success=False,
                message='المشروع غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_project_dashboard', f'project_dashboard/{project_id}')
    
    def _generate_project_code(self):
        """إنشاء كود المشروع"""
        from django.utils import timezone
        
        today = timezone.now().date()
        year = today.year
        
        # Get the last project number for this year
        last_project = Project.objects.filter(
            created_at__year=year
        ).order_by('-id').first()
        
        if last_project and last_project.project_code:
            # Extract sequence number from last project
            try:
                last_sequence = int(last_project.project_code.split('-')[-1])
                sequence = last_sequence + 1
            except (ValueError, IndexError):
                sequence = 1
        else:
            sequence = 1
        
        return f"PRJ-{year}-{sequence:04d}"
    
    def _add_team_members(self, project, team_members_data):
        """إضافة أعضاء الفريق"""
        from core.models.hr import Employee
        
        for member_data in team_members_data:
            try:
                employee = Employee.objects.get(id=member_data['employee_id'])
                
                ProjectTeamMember.objects.create(
                    project=project,
                    employee=employee,
                    role=member_data.get('role', 'team_member'),
                    responsibilities=member_data.get('responsibilities', ''),
                    allocation_percentage=member_data.get('allocation_percentage', 100),
                    joined_date=member_data.get('joined_date', timezone.now().date()),
                    created_by=self.user,
                    updated_by=self.user
                )
            except Employee.DoesNotExist:
                self.logger.warning(f"Employee {member_data['employee_id']} not found for project {project.id}")
    
    def _add_project_phases(self, project, phases_data):
        """إضافة مراحل المشروع"""
        for phase_data in phases_data:
            ProjectPhase.objects.create(
                project=project,
                name=phase_data['name'],
                description=phase_data.get('description', ''),
                start_date=phase_data.get('start_date'),
                end_date=phase_data.get('end_date'),
                status='planning',
                created_by=self.user,
                updated_by=self.user
            )
    
    def _calculate_project_progress(self, project):
        """حساب تقدم المشروع"""
        from core.models.projects import Task
        
        tasks = Task.objects.filter(project=project)
        total_tasks = tasks.count()
        
        if total_tasks == 0:
            return 0
        
        completed_tasks = tasks.filter(status='completed').count()
        return round((completed_tasks / total_tasks) * 100, 2)