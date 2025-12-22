"""
خدمة تتبع الوقت والإنتاجية
Time Tracking and Productivity Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Avg
from datetime import timedelta
from core.services.base import BaseService
from core.models.projects import TimeEntry, TimeSheet, ProjectTimeReport


class TimeTrackingService(BaseService):
    """
    خدمة تتبع الوقت والإنتاجية
    Time tracking and productivity service
    """

    def start_time_entry(self, data):
        """بدء تسجيل الوقت"""
        self.check_permission('projects.add_timeentry')

        required_fields = ['task_id']
        self.validate_required_fields(data, required_fields)

        try:
            from core.models.projects import Task

            task = Task.objects.get(id=data['task_id'])

            # Check if there's already an active time entry
            active_entry = TimeEntry.objects.filter(
                employee=self.user.employee,
                end_time__isnull=True
            ).first()

            if active_entry:
                return self.format_response(
                    success=False,
                    message='يوجد تسجيل وقت نشط بالفعل'
                )

            time_entry = TimeEntry.objects.create(
                task=task,
                employee=self.user.employee,
                start_time=timezone.now(),
                description=data.get('description', ''),
                created_by=self.user,
                updated_by=self.user
            )

            self.log_action(
                action='start_time',
                resource='time_entry',
                content_object=time_entry,
                message=f'تم بدء تسجيل الوقت للمهمة: {task.title}'
            )

            return self.format_response(
                data={'time_entry_id': time_entry.id},
                message='تم بدء تسجيل الوقت بنجاح'
            )

        except Task.DoesNotExist:
            return self.format_response(
                success=False,
                message='المهمة غير موجودة'
            )
        except Exception as e:
            return self.handle_exception(e, 'start_time_entry', 'time_entry', data)

    def stop_time_entry(self, time_entry_id, notes=None):
        """إيقاف تسجيل الوقت"""
        self.check_permission('projects.change_timeentry')

        try:
            time_entry = TimeEntry.objects.get(
                id=time_entry_id,
                employee=self.user.employee,
                end_time__isnull=True
            )

            time_entry.end_time = timezone.now()
            time_entry.duration = time_entry.end_time - time_entry.start_time
            time_entry.hours_worked = time_entry.duration.total_seconds() / 3600

            if notes:
                time_entry.notes = notes

            time_entry.updated_by = self.user
            time_entry.save()

            self.log_action(
                action='stop_time',
                resource='time_entry',
                content_object=time_entry,
                message=f'تم إيقاف تسجيل الوقت: {time_entry.hours_worked:.2f} ساعة'
            )

            return self.format_response(
                data={'hours_worked': time_entry.hours_worked},
                message='تم إيقاف تسجيل الوقت بنجاح'
            )

        except TimeEntry.DoesNotExist:
            return self.format_response(
                success=False,
                message='تسجيل الوقت غير موجود أو متوقف بالفعل'
            )
        except Exception as e:
            return self.handle_exception(e, 'stop_time_entry', f'time_entry/{time_entry_id}')

    def get_time_report(self, employee_id=None, project_id=None, start_date=None, end_date=None):
        """الحصول على تقرير الوقت"""
        self.check_permission('projects.view_timeentry')

        try:
            queryset = TimeEntry.objects.filter(end_time__isnull=False)

            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)
            elif not self.user.has_perm('projects.view_all_time_entries'):
                queryset = queryset.filter(employee=self.user.employee)

            if project_id:
                queryset = queryset.filter(task__project_id=project_id)

            if start_date:
                queryset = queryset.filter(start_time__date__gte=start_date)

            if end_date:
                queryset = queryset.filter(start_time__date__lte=end_date)

            # Calculate summary
            summary = queryset.aggregate(
                total_hours=Sum('hours_worked'),
                total_entries=Count('id'),
                avg_hours_per_entry=Avg('hours_worked')
            )

            # Get detailed entries
            entries = []
            for entry in queryset.select_related('task', 'employee').order_by('-start_time'):
                entries.append({
                    'id': entry.id,
                    'task_title': entry.task.title,
                    'project_name': entry.task.project.name_ar,
                    'employee_name': entry.employee.get_full_name(),
                    'start_time': entry.start_time,
                    'end_time': entry.end_time,
                    'hours_worked': entry.hours_worked,
                    'description': entry.description,
                })

            report_data = {
                'summary': summary,
                'entries': entries,
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                }
            }

            return self.format_response(
                data=report_data,
                message='تم إنشاء تقرير الوقت بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_time_report', 'time_report')
