from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from meetings.models import Meeting, MeetingTask, Attendee
from tasks.models import Task
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Test the integration between meetings and tasks applications'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting Integration Test'))
        self.stdout.write('='*50)
        
        try:
            self.test_existing_data()
            self.create_test_data()
            self.test_unified_view()
            self.stdout.write(self.style.SUCCESS('\n✅ Integration test completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Test failed with error: {e}'))
            import traceback
            traceback.print_exc()

    def test_existing_data(self):
        """Test existing data in the system"""
        self.stdout.write('\n📊 Checking existing data...')
        
        # Check users
        users = User.objects.all()
        self.stdout.write(f'Total users: {users.count()}')
        
        # Check meetings
        meetings = Meeting.objects.all()
        self.stdout.write(f'Total meetings: {meetings.count()}')
        
        # Check meeting tasks
        meeting_tasks = MeetingTask.objects.all()
        self.stdout.write(f'Total meeting tasks: {meeting_tasks.count()}')
        
        # Check regular tasks
        regular_tasks = Task.objects.all()
        self.stdout.write(f'Total regular tasks: {regular_tasks.count()}')
        
        # Show meeting tasks with assignments
        if meeting_tasks.exists():
            self.stdout.write('\nExisting meeting tasks:')
            for task in meeting_tasks:
                assigned_to = task.assigned_to.username if task.assigned_to else 'Unassigned'
                self.stdout.write(f'  - {task.description[:50]}... (Assigned to: {assigned_to})')

    def create_test_data(self):
        """Create test data if needed"""
        self.stdout.write('\n🔧 Creating test data...')
        
        # Get or create test users
        user1, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@test.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user1.set_password('admin123')
            user1.save()
            self.stdout.write(f'Created user: {user1.username}')
        
        user2, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'testuser@test.com'}
        )
        if created:
            user2.set_password('test123')
            user2.save()
            self.stdout.write(f'Created user: {user2.username}')
        
        # Create a test meeting if none exist
        if not Meeting.objects.filter(title__contains='اختبار التكامل').exists():
            meeting = Meeting.objects.create(
                title='اجتماع اختبار التكامل',
                date=timezone.now() + timedelta(days=1),
                topic='اختبار تكامل المهام مع الاجتماعات',
                status='pending',
                created_by=user1
            )
            
            # Add attendees
            Attendee.objects.create(meeting=meeting, user=user1)
            Attendee.objects.create(meeting=meeting, user=user2)
            
            # Create meeting tasks
            MeetingTask.objects.create(
                meeting=meeting,
                description='مهمة اختبار 1 - مراجعة التقارير',
                assigned_to=user2,
                status='in_progress',
                end_date=(timezone.now() + timedelta(days=7)).date()
            )
            
            MeetingTask.objects.create(
                meeting=meeting,
                description='مهمة اختبار 2 - إعداد العرض التقديمي',
                assigned_to=user2,
                status='pending',
                end_date=(timezone.now() + timedelta(days=5)).date()
            )
            
            self.stdout.write(f'✅ Created test meeting: {meeting.title}')
            self.stdout.write(f'✅ Created meeting tasks for testing')

    def test_unified_view(self):
        """Test the unified task view logic"""
        self.stdout.write('\n🔍 Testing unified task view...')
        
        # Test for each user
        for user in User.objects.all()[:3]:  # Test first 3 users
            self.stdout.write(f'\nTesting for user: {user.username}')
            
            # Get regular tasks
            regular_tasks = Task.objects.filter(assigned_to=user)
            
            # Get meeting tasks
            meeting_tasks = MeetingTask.objects.filter(assigned_to=user)
            
            self.stdout.write(f'  Regular tasks: {regular_tasks.count()}')
            self.stdout.write(f'  Meeting tasks: {meeting_tasks.count()}')
            
            # Show meeting tasks
            if meeting_tasks.exists():
                self.stdout.write('  Meeting tasks assigned:')
                for task in meeting_tasks:
                    self.stdout.write(f'    - {task.description[:40]}... (Status: {task.status})')
            
            # Test unified logic
            unified_count = regular_tasks.count() + meeting_tasks.count()
            self.stdout.write(f'  Total unified tasks: {unified_count}')
