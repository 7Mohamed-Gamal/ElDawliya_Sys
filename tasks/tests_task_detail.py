"""
Test cases for the enhanced task detail functionality
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from tasks.models import Task, TaskStep
from meetings.models import Meeting, MeetingTask, MeetingTaskStep, Attendee

User = get_user_model()


class TaskDetailTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create test meeting
        self.meeting = Meeting.objects.create(
            title='Test Meeting',
            date=timezone.now() + timedelta(days=1),
            topic='Test meeting topic',
            created_by=self.user1
        )
        
        # Create meeting attendee
        Attendee.objects.create(meeting=self.meeting, user=self.user1)
        Attendee.objects.create(meeting=self.meeting, user=self.user2)
        
        # Create regular task
        self.regular_task = Task.objects.create(
            title='Test Regular Task',
            description='This is a test regular task',
            assigned_to=self.user1,
            created_by=self.user2,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            status='pending'
        )
        
        # Create meeting task
        self.meeting_task = MeetingTask.objects.create(
            meeting=self.meeting,
            description='This is a test meeting task',
            assigned_to=self.user1,
            status='pending'
        )
        
        # Create task steps
        self.task_step = TaskStep.objects.create(
            task=self.regular_task,
            description='First step of regular task'
        )
        
        self.meeting_task_step = MeetingTaskStep.objects.create(
            meeting_task=self.meeting_task,
            description='First step of meeting task',
            completed=False,
            created_by=self.user1
        )

    def test_regular_task_detail_view(self):
        """Test regular task detail view"""
        self.client.login(username='testuser1', password='testpass123')
        
        url = reverse('tasks:detail', kwargs={'pk': self.regular_task.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Regular Task')
        self.assertContains(response, 'This is a test regular task')
        self.assertContains(response, 'تفاصيل المهمة')
        self.assertFalse(response.context['is_meeting_task'])

    def test_meeting_task_detail_view(self):
        """Test meeting task detail view"""
        self.client.login(username='testuser1', password='testpass123')
        
        url = reverse('tasks:detail', kwargs={'pk': f'meeting_{self.meeting_task.pk}'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is a test meeting task')
        self.assertContains(response, 'مهمة اجتماع')
        self.assertTrue(response.context['is_meeting_task'])

    def test_task_detail_permissions(self):
        """Test task detail view permissions"""
        # Test unauthorized access
        self.client.login(username='testuser2', password='testpass123')
        
        url = reverse('tasks:detail', kwargs={'pk': self.regular_task.pk})
        response = self.client.get(url)
        
        # Should redirect to task list with error message
        self.assertEqual(response.status_code, 302)

    def test_task_step_creation(self):
        """Test task step creation"""
        self.client.login(username='testuser1', password='testpass123')
        
        url = reverse('tasks:detail', kwargs={'pk': self.regular_task.pk})
        response = self.client.post(url, {
            'description': 'New task step'
        })
        
        # Should redirect back to detail page
        self.assertEqual(response.status_code, 302)
        
        # Check if step was created
        self.assertTrue(
            TaskStep.objects.filter(
                task=self.regular_task,
                description='New task step'
            ).exists()
        )

    def test_meeting_task_step_creation(self):
        """Test meeting task step creation"""
        self.client.login(username='testuser1', password='testpass123')
        
        url = reverse('tasks:detail', kwargs={'pk': f'meeting_{self.meeting_task.pk}'})
        response = self.client.post(url, {
            'add_step': '1',
            'description': 'New meeting task step',
            'notes': 'Test notes',
            'completed': False
        })
        
        # Should redirect back to detail page
        self.assertEqual(response.status_code, 302)
        
        # Check if step was created
        self.assertTrue(
            MeetingTaskStep.objects.filter(
                meeting_task=self.meeting_task,
                description='New meeting task step'
            ).exists()
        )

    def test_task_status_update(self):
        """Test task status update via AJAX"""
        self.client.login(username='testuser1', password='testpass123')
        
        url = reverse('tasks:update_task_status', kwargs={'pk': self.regular_task.pk})
        response = self.client.post(
            url,
            data='{"status": "in_progress"}',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Refresh task from database
        self.regular_task.refresh_from_db()
        self.assertEqual(self.regular_task.status, 'in_progress')

    def test_meeting_task_status_update(self):
        """Test meeting task status update via AJAX"""
        self.client.login(username='testuser1', password='testpass123')
        
        url = reverse('tasks:update_task_status', kwargs={'pk': f'meeting_{self.meeting_task.pk}'})
        response = self.client.post(
            url,
            data='{"status": "completed"}',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Refresh task from database
        self.meeting_task.refresh_from_db()
        self.assertEqual(self.meeting_task.status, 'completed')

    def test_task_context_data(self):
        """Test that task detail view provides correct context data"""
        self.client.login(username='testuser1', password='testpass123')
        
        url = reverse('tasks:detail', kwargs={'pk': self.regular_task.pk})
        response = self.client.get(url)
        
        context = response.context
        self.assertIn('task', context)
        self.assertIn('steps', context)
        self.assertIn('step_form', context)
        self.assertIn('related_tasks', context)
        self.assertEqual(context['task'], self.regular_task)

    def test_meeting_task_context_data(self):
        """Test that meeting task detail view provides correct context data"""
        self.client.login(username='testuser1', password='testpass123')
        
        url = reverse('tasks:detail', kwargs={'pk': f'meeting_{self.meeting_task.pk}'})
        response = self.client.get(url)
        
        context = response.context
        self.assertIn('task', context)
        self.assertIn('steps', context)
        self.assertIn('step_form', context)
        self.assertIn('status_form', context)
        self.assertIn('meeting_tasks_stats', context)
        self.assertEqual(context['task'], self.meeting_task)
        self.assertTrue(context['is_meeting_task'])
