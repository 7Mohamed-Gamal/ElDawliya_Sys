"""
Enhanced test suite for the improved tasks application
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import json

from tasks.models import Task, TaskStep
from tasks.forms import TaskForm, TaskStepForm, TaskFilterForm
from meetings.models import Meeting, MeetingTask, MeetingTaskStep, Attendee

User = get_user_model()


class EnhancedTaskModelTestCase(TestCase):
    """Test enhanced Task model functionality"""
    
    def setUp(self):
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
        
    def test_task_creation_with_validation(self):
        """Test task creation with enhanced validation"""
        task = Task.objects.create(
            title='Test Task',
            description='This is a test task with sufficient length',
            assigned_to=self.user1,
            created_by=self.user2,
            priority='high',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            status='pending'
        )
        
        self.assertEqual(task.priority, 'high')
        self.assertTrue(task.can_be_viewed_by(self.user1))
        self.assertTrue(task.can_be_viewed_by(self.user2))
        self.assertFalse(task.is_overdue)
        
    def test_task_validation_errors(self):
        """Test task validation catches errors"""
        with self.assertRaises(ValidationError):
            task = Task(
                title='Test Task',
                description='Short',  # Too short
                assigned_to=self.user1,
                start_date=timezone.now(),
                end_date=timezone.now() - timedelta(days=1),  # End before start
                status='pending'
            )
            task.full_clean()
    
    def test_task_queryset_methods(self):
        """Test custom queryset methods"""
        # Create test tasks
        Task.objects.create(
            title='Active Task',
            description='This is an active task for testing',
            assigned_to=self.user1,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            status='in_progress'
        )
        
        Task.objects.create(
            title='Overdue Task',
            description='This is an overdue task for testing',
            assigned_to=self.user1,
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=1),
            status='pending'
        )
        
        # Test queryset methods
        user_tasks = Task.objects.for_user(self.user1)
        self.assertEqual(user_tasks.count(), 2)
        
        overdue_tasks = Task.objects.overdue()
        self.assertEqual(overdue_tasks.count(), 1)
        
        active_tasks = Task.objects.active()
        self.assertEqual(active_tasks.count(), 2)
    
    def test_task_properties(self):
        """Test task computed properties"""
        # Create overdue task
        overdue_task = Task.objects.create(
            title='Overdue Task',
            description='This task is overdue for testing purposes',
            assigned_to=self.user1,
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=1),
            status='pending'
        )
        
        self.assertTrue(overdue_task.is_overdue)
        self.assertTrue(overdue_task.days_until_due < 0)
        self.assertEqual(overdue_task.progress_percentage, 10)
        
        # Test completed task
        completed_task = Task.objects.create(
            title='Completed Task',
            description='This task is completed for testing purposes',
            assigned_to=self.user1,
            start_date=timezone.now() - timedelta(days=5),
            end_date=timezone.now() + timedelta(days=2),
            status='completed'
        )
        
        self.assertEqual(completed_task.progress_percentage, 100)


class EnhancedTaskStepTestCase(TestCase):
    """Test enhanced TaskStep model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task for step testing',
            assigned_to=self.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            status='pending'
        )
    
    def test_task_step_creation(self):
        """Test enhanced task step creation"""
        step = TaskStep.objects.create(
            task=self.task,
            description='Test step with sufficient description length',
            notes='Some additional notes',
            completed=False,
            created_by=self.user
        )
        
        self.assertFalse(step.completed)
        self.assertIsNone(step.completion_date)
        self.assertTrue(step.is_recent)
    
    def test_task_step_completion(self):
        """Test task step completion logic"""
        step = TaskStep.objects.create(
            task=self.task,
            description='Test step for completion testing',
            created_by=self.user
        )
        
        # Mark as completed
        step.completed = True
        step.save()
        
        self.assertTrue(step.completed)
        self.assertIsNotNone(step.completion_date)


class EnhancedTaskFormTestCase(TestCase):
    """Test enhanced form functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def test_task_form_validation(self):
        """Test task form validation"""
        form_data = {
            'title': 'Test Task',
            'description': 'This is a test task with sufficient description length',
            'assigned_to': self.user.id,
            'priority': 'medium',
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=7),
            'status': 'pending'
        }
        
        form = TaskForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_task_form_date_validation(self):
        """Test task form date validation"""
        form_data = {
            'title': 'Test Task',
            'description': 'This is a test task with sufficient description length',
            'assigned_to': self.user.id,
            'priority': 'medium',
            'start_date': timezone.now(),
            'end_date': timezone.now() - timedelta(days=1),  # Invalid: end before start
            'status': 'pending'
        }
        
        form = TaskForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)
    
    def test_task_step_form_validation(self):
        """Test task step form validation"""
        form_data = {
            'description': 'Valid step description with sufficient length',
            'notes': 'Some notes',
            'completed': False
        }
        
        form = TaskStepForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test short description
        form_data['description'] = 'Short'
        form = TaskStepForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_filter_form(self):
        """Test task filter form"""
        form_data = {
            'search': 'test',
            'status': 'pending',
            'priority': 'high',
            'overdue_only': True
        }
        
        form = TaskFilterForm(data=form_data)
        self.assertTrue(form.is_valid())


class EnhancedTaskViewTestCase(TestCase):
    """Test enhanced view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task for view testing',
            assigned_to=self.user,
            created_by=self.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            status='pending'
        )
    
    def test_dashboard_view_performance(self):
        """Test dashboard view with optimized queries"""
        self.client.login(username='testuser', password='testpass123')
        
        with self.assertNumQueries(10):  # Should be optimized
            response = self.client.get(reverse('tasks:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'لوحة تحكم المهام')
    
    def test_task_list_with_filters(self):
        """Test task list view with filters"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test with filters
        response = self.client.get(reverse('tasks:list'), {
            'search': 'test',
            'status': 'pending',
            'priority': 'medium'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
    
    def test_task_creation_enhanced(self):
        """Test enhanced task creation"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('tasks:create'), {
            'title': 'New Test Task',
            'description': 'This is a new test task with sufficient description',
            'assigned_to': self.user.id,
            'priority': 'high',
            'start_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'end_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'status': 'pending'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Task.objects.filter(title='New Test Task').exists())
    
    def test_bulk_update_api(self):
        """Test bulk update functionality"""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.post(reverse('tasks:bulk_update'), {
            'action': 'update_status',
            'new_status': 'completed',
            'task_ids': str(self.task.id)
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify task was updated
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')
