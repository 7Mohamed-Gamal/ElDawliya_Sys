"""
Django management command to migrate existing task and meeting data to the new unified project models.
"""
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.contrib.auth.models import User
from django.utils import timezone
from django.apps import apps

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command class"""
    help = 'Migrate existing task and meeting data to the new unified project models'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration in dry-run mode (no actual changes)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each batch',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        self.dry_run = False
        self.batch_size = 100
        self.verbose = False
        self.stats = {
            'projects_created': 0,
            'tasks_migrated': 0,
            'task_steps_migrated': 0,
            'meetings_migrated': 0,
            'meeting_attendees_migrated': 0,
            'meeting_tasks_migrated': 0,
            'errors': 0,
        }

    def handle(self, *args, **options):
        """handle function"""
        self.dry_run = options['dry_run']
        self.batch_size = options['batch_size']
        self.verbose = options['verbose']

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('Running in DRY-RUN mode - no changes will be made')
            )

        try:
            with transaction.atomic():
                self.migrate_data()

                if self.dry_run:
                    # Rollback transaction in dry-run mode
                    transaction.set_rollback(True)
                    self.stdout.write(
                        self.style.WARNING('DRY-RUN completed - rolling back changes')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('Migration completed successfully')
                    )

        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise CommandError(f"Migration failed: {str(e)}")

        self.print_statistics()

    def migrate_data(self):
        """Main migration logic"""
        self.stdout.write("Starting project models migration...")

        # Step 1: Create default project categories
        self.create_default_categories()

        # Step 2: Create default projects for orphaned tasks
        self.create_default_projects()

        # Step 3: Migrate existing tasks
        self.migrate_tasks()

        # Step 4: Migrate task steps
        self.migrate_task_steps()

        # Step 5: Migrate meetings
        self.migrate_meetings()

        # Step 6: Migrate meeting attendees
        self.migrate_meeting_attendees()

        # Step 7: Migrate meeting tasks
        self.migrate_meeting_tasks()

        self.stdout.write("Migration completed!")

    def create_default_categories(self):
        """Create default project categories"""
        self.stdout.write("Creating default project categories...")

        try:
            ProjectCategory = apps.get_model('core', 'ProjectCategory')

            default_categories = [
                {
                    'name': 'مشاريع عامة',
                    'description': 'مشاريع عامة غير مصنفة',
                    'color': '#3498db',
                    'icon': 'fas fa-project-diagram',
                },
                {
                    'name': 'مهام إدارية',
                    'description': 'المهام الإدارية والتنظيمية',
                    'color': '#e74c3c',
                    'icon': 'fas fa-tasks',
                },
                {
                    'name': 'اجتماعات',
                    'description': 'مشاريع مرتبطة بالاجتماعات',
                    'color': '#f39c12',
                    'icon': 'fas fa-users',
                },
            ]

            for category_data in default_categories:
                category, created = ProjectCategory.objects.get_or_create(
                    name=category_data['name'],
                    defaults=category_data
                )
                if created and self.verbose:
                    self.stdout.write(f"  Created category: {category.name}")

        except Exception as e:
            logger.error(f"Error creating default categories: {str(e)}")
            self.stats['errors'] += 1

    def create_default_projects(self):
        """Create default projects for tasks without projects"""
        self.stdout.write("Creating default projects...")

        try:
            Project = apps.get_model('core', 'Project')
            ProjectCategory = apps.get_model('core', 'ProjectCategory')

            # Get default categories
            general_category = ProjectCategory.objects.get(name='مشاريع عامة')
            admin_category = ProjectCategory.objects.get(name='مهام إدارية')
            meeting_category = ProjectCategory.objects.get(name='اجتماعات')

            default_projects = [
                {
                    'name': 'مهام عامة',
                    'code': 'GENERAL',
                    'description': 'مشروع افتراضي للمهام العامة غير المصنفة',
                    'category': general_category,
                    'status': 'active',
                    'priority': 'medium',
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date().replace(year=timezone.now().year + 1),
                },
                {
                    'name': 'مهام إدارية',
                    'code': 'ADMIN',
                    'description': 'مشروع افتراضي للمهام الإدارية',
                    'category': admin_category,
                    'status': 'active',
                    'priority': 'medium',
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date().replace(year=timezone.now().year + 1),
                },
                {
                    'name': 'اجتماعات ومهامها',
                    'code': 'MEETINGS',
                    'description': 'مشروع افتراضي للاجتماعات والمهام المرتبطة بها',
                    'category': meeting_category,
                    'status': 'active',
                    'priority': 'medium',
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date().replace(year=timezone.now().year + 1),
                },
            ]

            for project_data in default_projects:
                project, created = Project.objects.get_or_create(
                    code=project_data['code'],
                    defaults=project_data
                )
                if created:
                    self.stats['projects_created'] += 1
                    if self.verbose:
                        self.stdout.write(f"  Created project: {project.name}")

        except Exception as e:
            logger.error(f"Error creating default projects: {str(e)}")
            self.stats['errors'] += 1

    def migrate_tasks(self):
        """Migrate existing tasks to new Task model"""
        self.stdout.write("Migrating tasks...")

        try:
            # Get old Task model
            OldTask = apps.get_model('tasks', 'Task')
            NewTask = apps.get_model('core', 'Task')
            Project = apps.get_model('core', 'Project')

            # Get default project for orphaned tasks
            default_project = Project.objects.get(code='GENERAL')

            old_tasks = OldTask.objects.all().select_related()  # TODO: Add appropriate select_related fields
            total_tasks = old_tasks.count()

            self.stdout.write(f"Found {total_tasks} tasks to migrate")

            for i, old_task in enumerate(old_tasks.iterator(chunk_size=self.batch_size)):
                try:
                    # Map old task fields to new task fields
                    new_task_data = {
                        'title': old_task.title or old_task.description[:100],
                        'description': old_task.description,
                        'task_type': 'meeting' if old_task.meeting else 'regular',
                        'project': default_project,  # Assign to default project
                        'assigned_to': old_task.assigned_to,
                        'status': old_task.status,
                        'priority': old_task.priority,
                        'start_date': old_task.start_date,
                        'due_date': old_task.end_date,
                        'progress_percentage': old_task.progress,
                        'is_private': old_task.is_private,
                        'created_at': old_task.created_at,
                        'updated_at': old_task.updated_at,
                        'created_by': old_task.created_by,
                    }

                    # Handle completion date
                    if old_task.status == 'completed' and old_task.completion_date:
                        new_task_data['completed_date'] = old_task.completion_date

                    # Create new task
                    new_task = NewTask.objects.create(**new_task_data)

                    # Store mapping for later use
                    if not hasattr(self, 'task_mapping'):
                        self.task_mapping = {}
                    self.task_mapping[old_task.id] = new_task.id

                    self.stats['tasks_migrated'] += 1

                    if self.verbose and (i + 1) % 10 == 0:
                        self.stdout.write(f"  Migrated {i + 1}/{total_tasks} tasks")

                except Exception as e:
                    logger.error(f"Error migrating task {old_task.id}: {str(e)}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Error in task migration: {str(e)}")
            self.stats['errors'] += 1

    def migrate_task_steps(self):
        """Migrate existing task steps"""
        self.stdout.write("Migrating task steps...")

        try:
            OldTaskStep = apps.get_model('tasks', 'TaskStep')
            NewTaskStep = apps.get_model('core', 'TaskStep')
            NewTask = apps.get_model('core', 'Task')

            old_steps = OldTaskStep.objects.all().select_related()  # TODO: Add appropriate select_related fields
            total_steps = old_steps.count()

            self.stdout.write(f"Found {total_steps} task steps to migrate")

            for i, old_step in enumerate(old_steps.iterator(chunk_size=self.batch_size)):
                try:
                    # Find corresponding new task
                    if hasattr(self, 'task_mapping') and old_step.task_id in self.task_mapping:
                        new_task_id = self.task_mapping[old_step.task_id]
                        new_task = NewTask.objects.get(id=new_task_id)

                        new_step_data = {
                            'task': new_task,
                            'description': old_step.description,
                            'notes': old_step.notes or '',
                            'completed': old_step.completed,
                            'completion_date': old_step.completion_date,
                            'created_at': old_step.date,
                            'updated_at': old_step.updated_at,
                            'created_by': old_step.created_by,
                        }

                        NewTaskStep.objects.create(**new_step_data)
                        self.stats['task_steps_migrated'] += 1

                        if self.verbose and (i + 1) % 10 == 0:
                            self.stdout.write(f"  Migrated {i + 1}/{total_steps} task steps")

                except Exception as e:
                    logger.error(f"Error migrating task step {old_step.id}: {str(e)}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Error in task steps migration: {str(e)}")
            self.stats['errors'] += 1

    def migrate_meetings(self):
        """Migrate existing meetings"""
        self.stdout.write("Migrating meetings...")

        try:
            OldMeeting = apps.get_model('meetings', 'Meeting')
            NewMeeting = apps.get_model('core', 'Meeting')
            Project = apps.get_model('core', 'Project')

            # Get default project for meetings
            meeting_project = Project.objects.get(code='MEETINGS')

            old_meetings = OldMeeting.objects.all().select_related()  # TODO: Add appropriate select_related fields
            total_meetings = old_meetings.count()

            self.stdout.write(f"Found {total_meetings} meetings to migrate")

            for i, old_meeting in enumerate(old_meetings.iterator(chunk_size=self.batch_size)):
                try:
                    new_meeting_data = {
                        'title': old_meeting.title,
                        'description': old_meeting.topic,
                        'meeting_type': 'team',  # Default type
                        'project': meeting_project,
                        'start_datetime': old_meeting.date,
                        'end_datetime': old_meeting.date + timezone.timedelta(hours=1),  # Default 1 hour
                        'status': old_meeting.status,
                        'organizer': old_meeting.created_by,
                        'created_at': old_meeting.date,
                        'created_by': old_meeting.created_by,
                    }

                    new_meeting = NewMeeting.objects.create(**new_meeting_data)

                    # Store mapping for later use
                    if not hasattr(self, 'meeting_mapping'):
                        self.meeting_mapping = {}
                    self.meeting_mapping[old_meeting.id] = new_meeting.id

                    self.stats['meetings_migrated'] += 1

                    if self.verbose and (i + 1) % 10 == 0:
                        self.stdout.write(f"  Migrated {i + 1}/{total_meetings} meetings")

                except Exception as e:
                    logger.error(f"Error migrating meeting {old_meeting.id}: {str(e)}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Error in meetings migration: {str(e)}")
            self.stats['errors'] += 1

    def migrate_meeting_attendees(self):
        """Migrate meeting attendees"""
        self.stdout.write("Migrating meeting attendees...")

        try:
            OldAttendee = apps.get_model('meetings', 'Attendee')
            NewMeetingAttendee = apps.get_model('core', 'MeetingAttendee')
            NewMeeting = apps.get_model('core', 'Meeting')

            old_attendees = OldAttendee.objects.all().select_related()  # TODO: Add appropriate select_related fields
            total_attendees = old_attendees.count()

            self.stdout.write(f"Found {total_attendees} meeting attendees to migrate")

            for i, old_attendee in enumerate(old_attendees.iterator(chunk_size=self.batch_size)):
                try:
                    # Find corresponding new meeting
                    if hasattr(self, 'meeting_mapping') and old_attendee.meeting_id in self.meeting_mapping:
                        new_meeting_id = self.meeting_mapping[old_attendee.meeting_id]
                        new_meeting = NewMeeting.objects.get(id=new_meeting_id)

                        new_attendee_data = {
                            'meeting': new_meeting,
                            'user': old_attendee.user,
                            'role': 'participant',  # Default role
                            'attendance_status': 'invited',  # Default status
                        }

                        NewMeetingAttendee.objects.create(**new_attendee_data)
                        self.stats['meeting_attendees_migrated'] += 1

                        if self.verbose and (i + 1) % 10 == 0:
                            self.stdout.write(f"  Migrated {i + 1}/{total_attendees} attendees")

                except Exception as e:
                    logger.error(f"Error migrating attendee {old_attendee.id}: {str(e)}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Error in meeting attendees migration: {str(e)}")
            self.stats['errors'] += 1

    def migrate_meeting_tasks(self):
        """Migrate meeting tasks to regular tasks"""
        self.stdout.write("Migrating meeting tasks...")

        try:
            OldMeetingTask = apps.get_model('meetings', 'MeetingTask')
            NewTask = apps.get_model('core', 'Task')
            NewMeeting = apps.get_model('core', 'Meeting')
            Project = apps.get_model('core', 'Project')

            # Get meeting project
            meeting_project = Project.objects.get(code='MEETINGS')

            old_meeting_tasks = OldMeetingTask.objects.all().select_related()  # TODO: Add appropriate select_related fields
            total_meeting_tasks = old_meeting_tasks.count()

            self.stdout.write(f"Found {total_meeting_tasks} meeting tasks to migrate")

            for i, old_mtask in enumerate(old_meeting_tasks.iterator(chunk_size=self.batch_size)):
                try:
                    # Find corresponding new meeting
                    new_meeting = None
                    if hasattr(self, 'meeting_mapping') and old_mtask.meeting_id in self.meeting_mapping:
                        new_meeting_id = self.meeting_mapping[old_mtask.meeting_id]
                        new_meeting = NewMeeting.objects.get(id=new_meeting_id)

                    new_task_data = {
                        'title': old_mtask.description[:100],  # Use first 100 chars as title
                        'description': old_mtask.description,
                        'task_type': 'meeting',
                        'project': meeting_project,
                        'assigned_to': old_mtask.assigned_to,
                        'status': old_mtask.status,
                        'priority': 'medium',  # Default priority
                        'start_date': old_mtask.created_at,
                        'due_date': timezone.datetime.combine(
                            old_mtask.end_date,
                            timezone.datetime.min.time()
                        ) if old_mtask.end_date else old_mtask.created_at + timezone.timedelta(days=7),
                        'created_at': old_mtask.created_at,
                    }

                    new_task = NewTask.objects.create(**new_task_data)
                    self.stats['meeting_tasks_migrated'] += 1

                    if self.verbose and (i + 1) % 10 == 0:
                        self.stdout.write(f"  Migrated {i + 1}/{total_meeting_tasks} meeting tasks")

                except Exception as e:
                    logger.error(f"Error migrating meeting task {old_mtask.id}: {str(e)}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Error in meeting tasks migration: {str(e)}")
            self.stats['errors'] += 1

    def print_statistics(self):
        """Print migration statistics"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("MIGRATION STATISTICS")
        self.stdout.write("="*50)

        for key, value in self.stats.items():
            label = key.replace('_', ' ').title()
            if key == 'errors' and value > 0:
                self.stdout.write(
                    self.style.ERROR(f"{label}: {value}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"{label}: {value}")
                )

        self.stdout.write("="*50)

        if self.stats['errors'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Migration completed with {self.stats['errors']} errors. "
                    "Check logs for details."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Migration completed successfully with no errors!")
            )
