from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.urls import reverse
from typing import Optional, Dict, Any, Union, List
from meetings.models import Meeting
from accounts.models import Users_Login_New

class TaskQuerySet(models.QuerySet):
    """Custom QuerySet for Task model with optimized queries"""

    def with_related(self):
        """Optimize queries by selecting related objects"""
        return self.select_related('assigned_to', 'created_by', 'meeting').prefetch_related('steps')

    def for_user(self, user):
        """Get tasks accessible by a specific user"""
        if user.is_superuser:
            return self.all()
        return self.filter(
            models.Q(assigned_to=user) | models.Q(created_by=user)
        )

    def by_status(self, status: str):
        """Filter tasks by status"""
        return self.filter(status=status)

    def overdue(self):
        """Get overdue tasks"""
        return self.filter(
            end_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )

    def active(self):
        """Get active (non-completed/canceled) tasks"""
        return self.exclude(status__in=['completed', 'canceled'])

class TaskManager(models.Manager):
    """Custom manager for Task model"""

    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)

    def with_related(self):
        return self.get_queryset().with_related()

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def overdue(self):
        return self.get_queryset().overdue()

    def active(self):
        return self.get_queryset().active()

class Task(models.Model):
    """
    Enhanced Task model with improved performance and validation
    """
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'يجرى العمل عليها'),
        ('completed', 'مكتملة'),
        ('canceled', 'ملغاة'),
        ('deferred', 'مؤجلة'),
        ('failed', 'فشلت'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان المهمة",
        blank=True,
        null=True,
        help_text="عنوان مختصر للمهمة (اختياري)"
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
        verbose_name="الاجتماع المرتبط"
    )
    assigned_to = models.ForeignKey(
        Users_Login_New,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        verbose_name="المكلف بالمهمة"
    )
    created_by = models.ForeignKey(
        Users_Login_New,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        null=True,
        blank=True,
        verbose_name="منشئ المهمة"
    )
    description = models.TextField(
        verbose_name="وصف المهمة",
        help_text="وصف تفصيلي للمهمة والمطلوب إنجازه"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="الأولوية"
    )
    start_date = models.DateTimeField(verbose_name="تاريخ البدء")
    end_date = models.DateTimeField(verbose_name="تاريخ الانتهاء")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="الحالة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    # Custom manager
    objects = TaskManager()

    class Meta:
        verbose_name = "مهمة"
        verbose_name_plural = "المهام"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['created_by']),
            models.Index(fields=['end_date']),
            models.Index(fields=['priority']),
            models.Index(fields=['status', 'assigned_to']),
            models.Index(fields=['status', 'end_date']),
        ]
        permissions = [
            ("view_dashboard", "Can view tasks dashboard"),
            ("view_mytask", "Can view my tasks"),
            ("view_report", "Can view task reports"),
            ("export_report", "Can export task reports"),
            ("bulk_update", "Can perform bulk updates on tasks"),
        ]

    def __str__(self):
        title = self.title or self.description[:50]
        return f"{title} - {self.assigned_to.username}"

    def clean(self):
        """Validate model data"""
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'تاريخ الانتهاء لا يمكن أن يكون قبل تاريخ البدء'
            })

    def save(self, *args, **kwargs):
        """Override save to add validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get the URL for this task"""
        return reverse('tasks:detail', kwargs={'pk': self.pk})

    def get_display_title(self) -> str:
        """Get the display title for the task"""
        return self.title if self.title else self.description[:50] + "..."

    def get_status_display(self) -> str:
        """Get the display text for status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_priority_display(self) -> str:
        """Get the display text for priority"""
        return dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        return (
            self.end_date < timezone.now() and
            self.status in ['pending', 'in_progress']
        )

    @property
    def days_until_due(self) -> int:
        """Get number of days until task is due"""
        if self.end_date:
            delta = self.end_date.date() - timezone.now().date()
            return delta.days
        return 0

    @property
    def progress_percentage(self) -> int:
        """Calculate task progress based on status and steps"""
        if self.status == 'completed':
            return 100
        elif self.status == 'in_progress':
            steps = self.steps.all()
            if steps.exists():
                # For regular tasks, we estimate progress based on number of steps
                return min(50 + (steps.count() * 10), 90)
            return 50
        elif self.status in ['canceled', 'failed']:
            return 0
        return 10

    def can_be_edited_by(self, user) -> bool:
        """Check if user can edit this task"""
        return (
            user.is_superuser or
            user == self.assigned_to or
            user == self.created_by
        )

    def can_be_viewed_by(self, user) -> bool:
        """Check if user can view this task"""
        return (
            user.is_superuser or
            user == self.assigned_to or
            user == self.created_by
        )


class TaskStep(models.Model):
    """
    Enhanced TaskStep model for tracking task progress
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name="المهمة"
    )
    description = models.TextField(
        verbose_name="وصف الخطوة",
        help_text="وصف تفصيلي للخطوة المتخذة"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات",
        help_text="ملاحظات إضافية حول هذه الخطوة"
    )
    completed = models.BooleanField(
        default=False,
        verbose_name="مكتملة"
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الإنجاز"
    )
    created_by = models.ForeignKey(
        Users_Login_New,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks_steps',
        verbose_name="تم الإنشاء بواسطة"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاريخ التحديث"
    )

    class Meta:
        verbose_name = "خطوة مهمة"
        verbose_name_plural = "خطوات المهام"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['task']),
            models.Index(fields=['completed']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"خطوة: {self.description[:30]}... - {self.task.get_display_title()}"

    def save(self, *args, **kwargs):
        """Override save to handle completion date"""
        if self.completed and not self.completion_date:
            self.completion_date = timezone.now()
        elif not self.completed:
            self.completion_date = None
        super().save(*args, **kwargs)

    @property
    def is_recent(self) -> bool:
        """Check if step was created recently (within last 24 hours)"""
        return (timezone.now() - self.date).days < 1


class UnifiedTaskManager:
    """
    Manager class for handling both regular tasks and meeting tasks
    in a unified interface
    """

    @staticmethod
    def get_user_tasks(user, include_meeting_tasks=True):
        """Get all tasks for a user (regular + meeting tasks)"""
        from meetings.models import MeetingTask

        # Get regular tasks
        if user.is_superuser:
            regular_tasks = Task.objects.with_related()
        else:
            regular_tasks = Task.objects.for_user(user).with_related()

        tasks = []

        # Add regular tasks as UnifiedTask objects
        for task in regular_tasks:
            tasks.append(UnifiedTask(task, task_type='regular'))

        # Add meeting tasks if requested
        if include_meeting_tasks:
            if user.is_superuser:
                meeting_tasks = MeetingTask.objects.select_related(
                    'assigned_to', 'meeting'
                ).prefetch_related('steps')
            else:
                meeting_tasks = MeetingTask.objects.filter(
                    assigned_to=user
                ).select_related('assigned_to', 'meeting').prefetch_related('steps')

            for mtask in meeting_tasks:
                tasks.append(UnifiedTask(mtask, task_type='meeting'))

        return tasks

    @staticmethod
    def get_task_by_id(task_id: str, user=None):
        """Get a task by ID (supports both regular and meeting tasks)"""
        from meetings.models import MeetingTask

        if task_id.startswith('meeting_'):
            # Meeting task
            meeting_task_id = task_id.replace('meeting_', '')
            try:
                meeting_task = MeetingTask.objects.select_related(
                    'assigned_to', 'meeting'
                ).prefetch_related('steps').get(id=meeting_task_id)

                # Check permissions
                if user and not user.is_superuser and meeting_task.assigned_to != user:
                    return None

                return UnifiedTask(meeting_task, task_type='meeting')
            except MeetingTask.DoesNotExist:
                return None
        else:
            # Regular task
            try:
                task = Task.objects.with_related().get(id=task_id)

                # Check permissions
                if user and not task.can_be_viewed_by(user):
                    return None

                return UnifiedTask(task, task_type='regular')
            except Task.DoesNotExist:
                return None

    @staticmethod
    def get_statistics(user):
        """Get unified statistics for both task types"""
        from meetings.models import MeetingTask

        if user.is_superuser:
            regular_stats = Task.objects.aggregate(
                total=models.Count('id'),
                completed=models.Count(models.Case(
                    models.When(status='completed', then=1),
                    output_field=models.IntegerField()
                )),
                in_progress=models.Count(models.Case(
                    models.When(status='in_progress', then=1),
                    output_field=models.IntegerField()
                )),
                overdue=models.Count(models.Case(
                    models.When(
                        end_date__lt=timezone.now(),
                        status__in=['pending', 'in_progress'],
                        then=1
                    ),
                    output_field=models.IntegerField()
                ))
            )

            meeting_stats = MeetingTask.objects.aggregate(
                total=models.Count('id'),
                completed=models.Count(models.Case(
                    models.When(status='completed', then=1),
                    output_field=models.IntegerField()
                )),
                in_progress=models.Count(models.Case(
                    models.When(status='in_progress', then=1),
                    output_field=models.IntegerField()
                )),
                overdue=models.Count(models.Case(
                    models.When(
                        end_date__lt=timezone.now().date(),
                        status__in=['pending', 'in_progress'],
                        then=1
                    ),
                    output_field=models.IntegerField()
                ))
            )
        else:
            regular_stats = Task.objects.filter(
                models.Q(assigned_to=user) | models.Q(created_by=user)
            ).aggregate(
                total=models.Count('id'),
                completed=models.Count(models.Case(
                    models.When(status='completed', then=1),
                    output_field=models.IntegerField()
                )),
                in_progress=models.Count(models.Case(
                    models.When(status='in_progress', then=1),
                    output_field=models.IntegerField()
                )),
                overdue=models.Count(models.Case(
                    models.When(
                        end_date__lt=timezone.now(),
                        status__in=['pending', 'in_progress'],
                        then=1
                    ),
                    output_field=models.IntegerField()
                ))
            )

            meeting_stats = MeetingTask.objects.filter(assigned_to=user).aggregate(
                total=models.Count('id'),
                completed=models.Count(models.Case(
                    models.When(status='completed', then=1),
                    output_field=models.IntegerField()
                )),
                in_progress=models.Count(models.Case(
                    models.When(status='in_progress', then=1),
                    output_field=models.IntegerField()
                )),
                overdue=models.Count(models.Case(
                    models.When(
                        end_date__lt=timezone.now().date(),
                        status__in=['pending', 'in_progress'],
                        then=1
                    ),
                    output_field=models.IntegerField()
                ))
            )

        return {
            'total': regular_stats['total'] + meeting_stats['total'],
            'completed': regular_stats['completed'] + meeting_stats['completed'],
            'in_progress': regular_stats['in_progress'] + meeting_stats['in_progress'],
            'overdue': regular_stats['overdue'] + meeting_stats['overdue'],
            'regular_stats': regular_stats,
            'meeting_stats': meeting_stats,
        }


class UnifiedTask:
    """
    Wrapper class that provides a unified interface for both regular tasks
    and meeting tasks, allowing them to be treated uniformly in views and templates
    """

    def __init__(self, task_instance, task_type: str):
        """
        Initialize with either a Task or MeetingTask instance

        Args:
            task_instance: Either a Task or MeetingTask instance
            task_type: 'regular' or 'meeting'
        """
        self.task_instance = task_instance
        self.task_type = task_type
        self._cache = {}

    # Common properties that work for both task types
    @property
    def id(self):
        """Unified ID - prefixed for meeting tasks"""
        if self.task_type == 'meeting':
            return f"meeting_{self.task_instance.id}"
        return str(self.task_instance.id)

    @property
    def raw_id(self):
        """Raw database ID"""
        return self.task_instance.id

    @property
    def title(self):
        """Task title - regular tasks have titles, meeting tasks use description"""
        if self.task_type == 'regular':
            return self.task_instance.title
        return None  # Meeting tasks don't have titles

    @property
    def description(self):
        """Task description"""
        return self.task_instance.description

    @property
    def assigned_to(self):
        """Assigned user"""
        return self.task_instance.assigned_to

    @property
    def status(self):
        """Task status"""
        return self.task_instance.status

    @property
    def created_at(self):
        """Creation date"""
        return self.task_instance.created_at

    @property
    def updated_at(self):
        """Last update date - meeting tasks don't have this"""
        if self.task_type == 'regular':
            return self.task_instance.updated_at
        return self.task_instance.created_at  # Fallback to created_at

    @property
    def start_date(self):
        """Start date - meeting tasks use created_at"""
        if self.task_type == 'regular':
            return self.task_instance.start_date
        return self.task_instance.created_at

    @property
    def end_date(self):
        """End date"""
        if self.task_type == 'regular':
            return self.task_instance.end_date
        # Convert DateField to datetime for consistency
        if self.task_instance.end_date:
            from datetime import datetime, time
            return datetime.combine(self.task_instance.end_date, time.min)
        return None

    @property
    def priority(self):
        """Priority - only regular tasks have this"""
        if self.task_type == 'regular':
            return self.task_instance.priority
        return 'medium'  # Default for meeting tasks

    @property
    def created_by(self):
        """Creator - only regular tasks have this"""
        if self.task_type == 'regular':
            return self.task_instance.created_by
        return None

    @property
    def meeting(self):
        """Associated meeting"""
        if self.task_type == 'regular':
            return self.task_instance.meeting
        return self.task_instance.meeting

    @property
    def steps(self):
        """Task steps"""
        return self.task_instance.steps.all()

    @property
    def steps_count(self):
        """Number of steps"""
        if 'steps_count' not in self._cache:
            self._cache['steps_count'] = self.task_instance.steps.count()
        return self._cache['steps_count']

    # Display methods
    def get_display_title(self):
        """Get display title"""
        if self.task_type == 'regular':
            return self.task_instance.get_display_title()
        return self.description[:50] + "..." if len(self.description) > 50 else self.description

    def get_status_display(self):
        """Get status display text"""
        return self.task_instance.get_status_display()

    def get_priority_display(self):
        """Get priority display text"""
        if self.task_type == 'regular':
            return self.task_instance.get_priority_display()
        return 'متوسطة'  # Default for meeting tasks

    def get_task_type_display(self):
        """Get task type display text"""
        return 'مهمة عادية' if self.task_type == 'regular' else 'مهمة اجتماع'

    def get_task_type_badge_class(self):
        """Get CSS class for task type badge"""
        return 'badge-primary' if self.task_type == 'regular' else 'badge-info'

    # Computed properties
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.end_date:
            return False

        now = timezone.now()
        if self.task_type == 'regular':
            return self.end_date < now and self.status in ['pending', 'in_progress']
        else:
            # For meeting tasks, compare with date
            return self.end_date.date() < now.date() and self.status in ['pending', 'in_progress']

    @property
    def days_until_due(self):
        """Days until due date"""
        if not self.end_date:
            return 0

        if self.task_type == 'regular':
            delta = self.end_date.date() - timezone.now().date()
        else:
            delta = self.end_date.date() - timezone.now().date()

        return delta.days

    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.status == 'completed':
            return 100
        elif self.status == 'in_progress':
            # Base progress on steps completion
            total_steps = self.steps_count
            if total_steps > 0:
                completed_steps = sum(1 for step in self.steps if getattr(step, 'completed', False))
                return min(50 + int((completed_steps / total_steps) * 40), 90)
            return 50
        elif self.status in ['canceled', 'cancelled']:
            return 0
        return 10

    # Permission methods
    def can_be_edited_by(self, user):
        """Check if user can edit this task"""
        if user.is_superuser:
            return True

        if self.task_type == 'regular':
            return self.task_instance.can_be_edited_by(user)
        else:
            # Meeting tasks can be edited by assigned user
            return user == self.assigned_to

    def can_be_viewed_by(self, user):
        """Check if user can view this task"""
        if user.is_superuser:
            return True

        if self.task_type == 'regular':
            return self.task_instance.can_be_viewed_by(user)
        else:
            # Meeting tasks can be viewed by assigned user
            return user == self.assigned_to

    # URL methods
    def get_absolute_url(self):
        """Get URL for task detail"""
        return reverse('tasks:detail', kwargs={'pk': self.id})

    def get_edit_url(self):
        """Get URL for task editing"""
        if self.task_type == 'regular':
            return reverse('tasks:edit', kwargs={'pk': self.raw_id})
        else:
            # Meeting tasks are edited through the tasks interface
            return reverse('tasks:detail', kwargs={'pk': self.id})

    def get_delete_url(self):
        """Get URL for task deletion"""
        if self.task_type == 'regular':
            return reverse('tasks:delete', kwargs={'pk': self.raw_id})
        else:
            # Meeting tasks might not be deletable from tasks interface
            return None

    # Utility methods
    def update_status(self, new_status, user=None):
        """Update task status"""
        if self.can_be_edited_by(user):
            self.task_instance.status = new_status
            self.task_instance.save()
            return True
        return False

    def add_step(self, description, notes=None, user=None):
        """Add a step to the task"""
        if not self.can_be_edited_by(user):
            return None

        if self.task_type == 'regular':
            from tasks.models import TaskStep
            step = TaskStep.objects.create(
                task=self.task_instance,
                description=description,
                notes=notes or '',
                created_by=user
            )
        else:
            from meetings.models import MeetingTaskStep
            step = MeetingTaskStep.objects.create(
                meeting_task=self.task_instance,
                description=description,
                notes=notes or '',
                created_by=user
            )

        # Clear cache
        if 'steps_count' in self._cache:
            del self._cache['steps_count']

        return step

    def __str__(self):
        return f"[{self.get_task_type_display()}] {self.get_display_title()}"

    def __repr__(self):
        return f"UnifiedTask(id={self.id}, type={self.task_type}, status={self.status})"


