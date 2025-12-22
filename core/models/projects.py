"""
نماذج إدارة المشاريع والمهام الموحدة
Unified Project and Task Management Models
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .base import BaseModel, AuditableModel, SoftDeleteModel
from .permissions import Permission


class ProjectCategory(BaseModel):
    """
    تصنيفات المشاريع
    Project Categories
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('اسم التصنيف')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف التصنيف')
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name=_('اللون'),
        help_text=_('لون التصنيف بصيغة HEX')
    )
    icon = models.CharField(
        max_length=50,
        default='fas fa-project-diagram',
        verbose_name=_('الأيقونة')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_('التصنيف الأب')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('تصنيف المشروع')
        verbose_name_plural = _('تصنيفات المشاريع')
        ordering = ['name']
        db_table = 'project_categories'

    def __str__(self):
        """__str__ function"""
        return self.name

    @property
    def full_name(self):
        """Get full category name including parent"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Project(AuditableModel, SoftDeleteModel):
    """
    المشاريع الرئيسية
    Main Projects Model
    """
    STATUS_CHOICES = [
        ('planning', _('تخطيط')),
        ('active', _('نشط')),
        ('on_hold', _('معلق')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
        ('archived', _('مؤرشف')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('critical', _('حرجة')),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name=_('اسم المشروع')
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('رمز المشروع'),
        help_text=_('رمز فريد للمشروع')
    )
    description = models.TextField(
        verbose_name=_('وصف المشروع')
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name=_('التصنيف')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning',
        verbose_name=_('حالة المشروع')
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('الأولوية')
    )
    start_date = models.DateField(
        verbose_name=_('تاريخ البدء')
    )
    end_date = models.DateField(
        verbose_name=_('تاريخ الانتهاء المخطط')
    )
    actual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الانتهاء الفعلي')
    )
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('الميزانية')
    )
    actual_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name=_('التكلفة الفعلية')
    )
    progress_percentage = models.PositiveIntegerField(
        default=0,
        verbose_name=_('نسبة الإنجاز (%)'),
        help_text=_('من 0 إلى 100')
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_projects',
        verbose_name=_('مدير المشروع')
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        through_fields=('project', 'user'),
        related_name='projects',
        verbose_name=_('أعضاء الفريق')
    )
    parent_project = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subprojects',
        verbose_name=_('المشروع الأب')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('مشروع')
        verbose_name_plural = _('المشاريع')
        ordering = ['-created_at']
        db_table = 'projects'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['manager']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['category']),
        ]
        permissions = [
            ("view_project_dashboard", "Can view project dashboard"),
            ("manage_project_team", "Can manage project team"),
            ("view_project_reports", "Can view project reports"),
            ("export_project_data", "Can export project data"),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.code} - {self.name}"

    def clean(self):
        """Validate model data"""
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': _('تاريخ الانتهاء لا يمكن أن يكون قبل تاريخ البدء')
            })

        if self.progress_percentage < 0 or self.progress_percentage > 100:
            raise ValidationError({
                'progress_percentage': _('نسبة الإنجاز يجب أن تكون بين 0 و 100')
            })

    def get_absolute_url(self):
        """Get the URL for this project"""
        return reverse('projects:detail', kwargs={'pk': self.pk})

    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if self.status in ['completed', 'cancelled', 'archived']:
            return False
        return self.end_date < timezone.now().date()

    @property
    def days_remaining(self):
        """Get days remaining until end date"""
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return delta.days
        return 0

    @property
    def duration_days(self):
        """Get project duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    @property
    def budget_utilization(self):
        """Get budget utilization percentage"""
        if self.budget and self.budget > 0:
            return (self.actual_cost / self.budget) * 100
        return 0

    def calculate_progress(self):
        """Calculate project progress based on tasks and phases"""
        # Calculate based on tasks completion
        tasks = self.tasks.all()
        if tasks.exists():
            completed_tasks = tasks.filter(status='completed').count()
            total_tasks = tasks.count()
            task_progress = (completed_tasks / total_tasks) * 100

            # Calculate based on phases completion
            phases = self.phases.all()
            if phases.exists():
                phase_progress = sum(phase.progress_percentage for phase in phases) / phases.count()
                # Average of task and phase progress
                return (task_progress + phase_progress) / 2

            return task_progress

        # Fallback to manual progress
        return self.progress_percentage

    def update_progress(self):
        """Update project progress automatically"""
        self.progress_percentage = int(self.calculate_progress())
        self.save(update_fields=['progress_percentage'])


class ProjectPhase(AuditableModel):
    """
    مراحل المشروع
    Project Phases
    """
    STATUS_CHOICES = [
        ('not_started', _('لم تبدأ')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتملة')),
        ('on_hold', _('معلقة')),
        ('cancelled', _('ملغاة')),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='phases',
        verbose_name=_('المشروع')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('اسم المرحلة')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف المرحلة')
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name=_('الترتيب')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name=_('الحالة')
    )
    start_date = models.DateField(
        verbose_name=_('تاريخ البدء')
    )
    end_date = models.DateField(
        verbose_name=_('تاريخ الانتهاء المخطط')
    )
    actual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الانتهاء الفعلي')
    )
    progress_percentage = models.PositiveIntegerField(
        default=0,
        verbose_name=_('نسبة الإنجاز (%)'),
        help_text=_('من 0 إلى 100')
    )
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('ميزانية المرحلة')
    )
    actual_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name=_('التكلفة الفعلية')
    )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='responsible_phases',
        verbose_name=_('المسؤول عن المرحلة')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('مرحلة مشروع')
        verbose_name_plural = _('مراحل المشاريع')
        ordering = ['project', 'order']
        db_table = 'project_phases'
        unique_together = ['project', 'order']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.project.name} - {self.name}"

    def clean(self):
        """Validate model data"""
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': _('تاريخ الانتهاء لا يمكن أن يكون قبل تاريخ البدء')
            })

    @property
    def is_overdue(self):
        """Check if phase is overdue"""
        if self.status in ['completed', 'cancelled']:
            return False
        return self.end_date < timezone.now().date()


class ProjectMilestone(AuditableModel):
    """
    معالم المشروع
    Project Milestones
    """
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('achieved', _('تم تحقيقه')),
        ('missed', _('فائت')),
        ('cancelled', _('ملغي')),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name=_('المشروع')
    )
    phase = models.ForeignKey(
        ProjectPhase,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='milestones',
        verbose_name=_('المرحلة')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('اسم المعلم')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف المعلم')
    )
    target_date = models.DateField(
        verbose_name=_('التاريخ المستهدف')
    )
    actual_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('التاريخ الفعلي')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('الحالة')
    )
    importance = models.PositiveIntegerField(
        default=5,
        verbose_name=_('الأهمية'),
        help_text=_('من 1 إلى 10')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('معلم مشروع')
        verbose_name_plural = _('معالم المشاريع')
        ordering = ['project', 'target_date']
        db_table = 'project_milestones'
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['target_date']),
            models.Index(fields=['phase']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.project.name} - {self.name}"

    @property
    def is_overdue(self):
        """Check if milestone is overdue"""
        if self.status in ['achieved', 'cancelled']:
            return False
        return self.target_date < timezone.now().date()


class ProjectMember(BaseModel):
    """
    أعضاء فريق المشروع
    Project Team Members
    """
    ROLE_CHOICES = [
        ('manager', _('مدير المشروع')),
        ('lead', _('قائد الفريق')),
        ('developer', _('مطور')),
        ('analyst', _('محلل')),
        ('designer', _('مصمم')),
        ('tester', _('مختبر')),
        ('consultant', _('استشاري')),
        ('stakeholder', _('صاحب مصلحة')),
        ('observer', _('مراقب')),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('المشروع')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships',
        verbose_name=_('المستخدم')
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='developer',
        verbose_name=_('الدور')
    )
    joined_date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ الانضمام')
    )
    left_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ المغادرة')
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('المعدل بالساعة')
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='project_members',
        verbose_name=_('الصلاحيات')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('عضو فريق المشروع')
        verbose_name_plural = _('أعضاء فرق المشاريع')
        unique_together = ['project', 'user']
        db_table = 'project_members'
        indexes = [
            models.Index(fields=['project', 'role']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.user.get_full_name()} - {self.project.name}"

    @property
    def is_active(self):
        """Check if member is currently active in project"""
        return self.left_date is None or self.left_date > timezone.now().date()


class Task(AuditableModel, SoftDeleteModel):
    """
    المهام الموحدة (عادية ومرتبطة بالاجتماعات)
    Unified Tasks (Regular and Meeting-related)
    """
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتملة')),
        ('cancelled', _('ملغاة')),
        ('deferred', _('مؤجلة')),
        ('blocked', _('محجوبة')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('urgent', _('عاجلة')),
        ('critical', _('حرجة')),
    ]

    TYPE_CHOICES = [
        ('regular', _('مهمة عادية')),
        ('meeting', _('مهمة اجتماع')),
        ('milestone', _('مهمة معلم')),
        ('phase', _('مهمة مرحلة')),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان المهمة')
    )
    description = models.TextField(
        verbose_name=_('وصف المهمة')
    )
    task_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='regular',
        verbose_name=_('نوع المهمة')
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('المشروع')
    )
    phase = models.ForeignKey(
        ProjectPhase,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('المرحلة')
    )
    milestone = models.ForeignKey(
        ProjectMilestone,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('المعلم')
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name=_('المهمة الأب')
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tasks',
        verbose_name=_('مكلف إلى')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('الحالة')
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('الأولوية')
    )
    start_date = models.DateTimeField(
        verbose_name=_('تاريخ البدء')
    )
    due_date = models.DateTimeField(
        verbose_name=_('تاريخ الاستحقاق')
    )
    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الإنجاز')
    )
    estimated_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('الساعات المقدرة')
    )
    actual_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name=_('الساعات الفعلية')
    )
    progress_percentage = models.PositiveIntegerField(
        default=0,
        verbose_name=_('نسبة الإنجاز (%)'),
        help_text=_('من 0 إلى 100')
    )
    is_private = models.BooleanField(
        default=False,
        verbose_name=_('خاص'),
        help_text=_('إذا كان خاصًا، فلن يراه إلا المنشئ والمكلف')
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('العلامات'),
        help_text=_('علامات مفصولة بفواصل')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('مهمة')
        verbose_name_plural = _('المهام')
        ordering = ['-created_at']
        db_table = 'tasks'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['project']),
            models.Index(fields=['due_date']),
            models.Index(fields=['task_type']),
            models.Index(fields=['status', 'assigned_to']),
            models.Index(fields=['project', 'status']),
        ]
        permissions = [
            ("view_task_dashboard", "Can view task dashboard"),
            ("view_all_tasks", "Can view all tasks"),
            ("manage_task_assignments", "Can manage task assignments"),
            ("view_task_reports", "Can view task reports"),
            ("export_task_data", "Can export task data"),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.title} - {self.assigned_to.get_full_name() if self.assigned_to else 'غير مكلف'}"

    def clean(self):
        """Validate model data"""
        super().clean()
        if self.start_date and self.due_date and self.due_date < self.start_date:
            raise ValidationError({
                'due_date': _('تاريخ الاستحقاق لا يمكن أن يكون قبل تاريخ البدء')
            })

        if self.progress_percentage < 0 or self.progress_percentage > 100:
            raise ValidationError({
                'progress_percentage': _('نسبة الإنجاز يجب أن تكون بين 0 و 100')
            })

    def get_absolute_url(self):
        """Get the URL for this task"""
        return reverse('tasks:detail', kwargs={'pk': self.pk})

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status in ['completed', 'cancelled']:
            return False
        return self.due_date < timezone.now()

    @property
    def days_until_due(self):
        """Get days until due date"""
        if self.due_date:
            delta = self.due_date.date() - timezone.now().date()
            return delta.days
        return 0

    @property
    def duration_hours(self):
        """Get task duration in hours"""
        if self.start_date and self.due_date:
            delta = self.due_date - self.start_date
            return delta.total_seconds() / 3600
        return 0

    @property
    def tag_list(self):
        """Get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    def can_be_edited_by(self, user):
        """Check if user can edit this task"""
        return (
            user.is_superuser or
            user == self.assigned_to or
            user == self.created_by or
            (self.project and self.project.manager == user)
        )

    def can_be_viewed_by(self, user):
        """Check if user can view this task"""
        if self.is_private:
            return (
                user.is_superuser or
                user == self.assigned_to or
                user == self.created_by
            )

        return (
            user.is_superuser or
            user == self.assigned_to or
            user == self.created_by or
            (self.project and user in self.project.team_members.all())
        )


class TaskStep(BaseModel):
    """
    خطوات المهام
    Task Steps/Progress Tracking
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name=_('المهمة')
    )
    description = models.TextField(
        verbose_name=_('وصف الخطوة')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات')
    )
    completed = models.BooleanField(
        default=False,
        verbose_name=_('مكتملة')
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الإنجاز')
    )
    hours_spent = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name=_('الساعات المستغرقة')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('خطوة مهمة')
        verbose_name_plural = _('خطوات المهام')
        ordering = ['-created_at']
        db_table = 'task_steps'
        indexes = [
            models.Index(fields=['task']),
            models.Index(fields=['completed']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"خطوة: {self.description[:30]}... - {self.task.title}"

    def save(self, *args, **kwargs):
        """Override save to handle completion date"""
        if self.completed and not self.completion_date:
            self.completion_date = timezone.now()
        elif not self.completed:
            self.completion_date = None
        super().save(*args, **kwargs)


class TimeEntry(BaseModel):
    """
    إدخالات الوقت
    Time Tracking Entries
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='time_entries',
        verbose_name=_('المهمة')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_entries',
        verbose_name=_('المستخدم')
    )
    start_time = models.DateTimeField(
        verbose_name=_('وقت البدء')
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('وقت الانتهاء')
    )
    duration_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('المدة بالساعات')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف العمل المنجز')
    )
    is_billable = models.BooleanField(
        default=True,
        verbose_name=_('قابل للفوترة')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('إدخال وقت')
        verbose_name_plural = _('إدخالات الوقت')
        ordering = ['-start_time']
        db_table = 'time_entries'
        indexes = [
            models.Index(fields=['task', 'user']),
            models.Index(fields=['start_time']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.user.get_full_name()} - {self.task.title} - {self.duration_hours}h"

    def save(self, *args, **kwargs):
        """Calculate duration if end_time is provided"""
        if self.start_time and self.end_time and not self.duration_hours:
            delta = self.end_time - self.start_time
            self.duration_hours = delta.total_seconds() / 3600
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if time entry is currently active (no end time)"""
        return self.end_time is None


class Meeting(AuditableModel):
    """
    الاجتماعات المحسنة
    Enhanced Meetings Model
    """
    STATUS_CHOICES = [
        ('scheduled', _('مجدول')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
        ('postponed', _('مؤجل')),
    ]

    TYPE_CHOICES = [
        ('project', _('اجتماع مشروع')),
        ('team', _('اجتماع فريق')),
        ('client', _('اجتماع عميل')),
        ('review', _('اجتماع مراجعة')),
        ('planning', _('اجتماع تخطيط')),
        ('standup', _('اجتماع يومي')),
        ('other', _('أخرى')),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان الاجتماع')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف الاجتماع')
    )
    meeting_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='team',
        verbose_name=_('نوع الاجتماع')
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='meetings',
        verbose_name=_('المشروع المرتبط')
    )
    start_datetime = models.DateTimeField(
        verbose_name=_('تاريخ ووقت البدء')
    )
    end_datetime = models.DateTimeField(
        verbose_name=_('تاريخ ووقت الانتهاء')
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('المكان')
    )
    virtual_link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('رابط الاجتماع الافتراضي')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name=_('حالة الاجتماع')
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_meetings',
        verbose_name=_('منظم الاجتماع')
    )
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='MeetingAttendee',
        through_fields=('meeting', 'user'),
        related_name='meetings',
        verbose_name=_('الحضور')
    )
    agenda = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('جدول الأعمال')
    )
    minutes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('محضر الاجتماع')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('اجتماع')
        verbose_name_plural = _('الاجتماعات')
        ordering = ['-start_datetime']
        db_table = 'meetings'
        indexes = [
            models.Index(fields=['start_datetime']),
            models.Index(fields=['status']),
            models.Index(fields=['project']),
            models.Index(fields=['organizer']),
        ]
        permissions = [
            ("view_meeting_dashboard", "Can view meeting dashboard"),
            ("manage_meeting_attendees", "Can manage meeting attendees"),
            ("view_meeting_reports", "Can view meeting reports"),
            ("export_meeting_data", "Can export meeting data"),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.title} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """Validate model data"""
        super().clean()
        if self.start_datetime and self.end_datetime and self.end_datetime <= self.start_datetime:
            raise ValidationError({
                'end_datetime': _('وقت الانتهاء يجب أن يكون بعد وقت البدء')
            })

    def get_absolute_url(self):
        """Get the URL for this meeting"""
        return reverse('meetings:detail', kwargs={'pk': self.pk})

    @property
    def duration_hours(self):
        """Get meeting duration in hours"""
        if self.start_datetime and self.end_datetime:
            delta = self.end_datetime - self.start_datetime
            return delta.total_seconds() / 3600
        return 0

    @property
    def is_upcoming(self):
        """Check if meeting is upcoming"""
        return self.start_datetime > timezone.now() and self.status == 'scheduled'

    @property
    def is_past(self):
        """Check if meeting is in the past"""
        return self.end_datetime < timezone.now()


class MeetingAttendee(BaseModel):
    """
    حضور الاجتماعات
    Meeting Attendees
    """
    ATTENDANCE_STATUS_CHOICES = [
        ('invited', _('مدعو')),
        ('accepted', _('قبل')),
        ('declined', _('رفض')),
        ('tentative', _('مؤقت')),
        ('attended', _('حضر')),
        ('absent', _('غائب')),
    ]

    ROLE_CHOICES = [
        ('organizer', _('منظم')),
        ('presenter', _('مقدم')),
        ('participant', _('مشارك')),
        ('observer', _('مراقب')),
        ('required', _('مطلوب')),
        ('optional', _('اختياري')),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='attendee_records',
        verbose_name=_('الاجتماع')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meeting_attendances',
        verbose_name=_('المستخدم')
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='participant',
        verbose_name=_('الدور')
    )
    attendance_status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS_CHOICES,
        default='invited',
        verbose_name=_('حالة الحضور')
    )
    response_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الرد')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('حضور اجتماع')
        verbose_name_plural = _('حضور الاجتماعات')
        unique_together = ['meeting', 'user']
        db_table = 'meeting_attendees'
        indexes = [
            models.Index(fields=['meeting', 'attendance_status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.user.get_full_name()} - {self.meeting.title}"


class Document(AuditableModel, SoftDeleteModel):
    """
    إدارة الوثائق والملفات
    Document and File Management
    """
    DOCUMENT_TYPE_CHOICES = [
        ('project_doc', _('وثيقة مشروع')),
        ('meeting_doc', _('وثيقة اجتماع')),
        ('task_doc', _('وثيقة مهمة')),
        ('contract', _('عقد')),
        ('specification', _('مواصفات')),
        ('report', _('تقرير')),
        ('presentation', _('عرض تقديمي')),
        ('image', _('صورة')),
        ('other', _('أخرى')),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name=_('اسم الوثيقة')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف الوثيقة')
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='other',
        verbose_name=_('نوع الوثيقة')
    )
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        verbose_name=_('الملف')
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('حجم الملف (بايت)')
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('نوع MIME')
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('المشروع')
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('المهمة')
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('الاجتماع')
    )
    version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name=_('الإصدار')
    )
    is_confidential = models.BooleanField(
        default=False,
        verbose_name=_('سري')
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('العلامات'),
        help_text=_('علامات مفصولة بفواصل')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('وثيقة')
        verbose_name_plural = _('الوثائق')
        ordering = ['-created_at']
        db_table = 'documents'
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['project']),
            models.Index(fields=['task']),
            models.Index(fields=['meeting']),
        ]
        permissions = [
            ("view_confidential_documents", "Can view confidential documents"),
            ("manage_document_versions", "Can manage document versions"),
        ]

    def __str__(self):
        """__str__ function"""
        return self.name

    def save(self, *args, **kwargs):
        """Override save to set file size and mime type"""
        if self.file:
            self.file_size = self.file.size
            # You might want to use python-magic to detect mime type
            import mimetypes
            self.mime_type, _ = mimetypes.guess_type(self.file.name)
        super().save(*args, **kwargs)

    @property
    def file_extension(self):
        """Get file extension"""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return ''

    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

    @property
    def tag_list(self):
        """Get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    def can_be_viewed_by(self, user):
        """Check if user can view this document"""
        if self.is_confidential:
            return (
                user.is_superuser or
                user == self.created_by or
                (self.project and user in self.project.team_members.all())
            )
        return True
