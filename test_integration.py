#!/usr/bin/env python
"""
Test script to verify the integration between meetings and tasks applications.
This script creates test data and verifies that meeting tasks appear in the task list.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.contrib.auth import get_user_model
from meetings.models import Meeting, MeetingTask, Attendee
from tasks.models import Task
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

def create_test_data():
    """Create test meeting with assigned tasks"""
    print("Creating test data...")
    
    # Get or create test users
    try:
        user1 = User.objects.get(username='admin')
    except User.DoesNotExist:
        user1 = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
    
    try:
        user2 = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user2 = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='test123'
        )
    
    # Create a test meeting
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
    
    # Create meeting tasks assigned to users
    task1 = MeetingTask.objects.create(
        meeting=meeting,
        description='مهمة اختبار 1 - مراجعة التقارير',
        assigned_to=user2,
        status='in_progress',
        end_date=(timezone.now() + timedelta(days=7)).date()
    )
    
    task2 = MeetingTask.objects.create(
        meeting=meeting,
        description='مهمة اختبار 2 - إعداد العرض التقديمي',
        assigned_to=user2,
        status='pending',
        end_date=(timezone.now() + timedelta(days=5)).date()
    )
    
    task3 = MeetingTask.objects.create(
        meeting=meeting,
        description='مهمة اختبار 3 - متابعة مع الفريق',
        assigned_to=user1,
        status='pending',
        end_date=(timezone.now() + timedelta(days=3)).date()
    )
    
    print(f"✅ Created meeting: {meeting.title}")
    print(f"✅ Created {MeetingTask.objects.filter(meeting=meeting).count()} meeting tasks")
    
    return meeting, user1, user2

def test_task_list_integration():
    """Test that meeting tasks appear in the task list"""
    print("\nTesting task list integration...")
    
    meeting, user1, user2 = create_test_data()
    
    # Test for user2 (has 2 meeting tasks assigned)
    print(f"\nTesting for user: {user2.username}")
    
    # Get regular tasks for user2
    regular_tasks = Task.objects.filter(assigned_to=user2)
    print(f"Regular tasks for {user2.username}: {regular_tasks.count()}")
    
    # Get meeting tasks for user2
    meeting_tasks = MeetingTask.objects.filter(assigned_to=user2)
    print(f"Meeting tasks for {user2.username}: {meeting_tasks.count()}")
    
    for task in meeting_tasks:
        print(f"  - {task.description} (Status: {task.status})")
    
    # Test for user1 (has 1 meeting task assigned)
    print(f"\nTesting for user: {user1.username}")
    
    # Get regular tasks for user1
    regular_tasks = Task.objects.filter(assigned_to=user1)
    print(f"Regular tasks for {user1.username}: {regular_tasks.count()}")
    
    # Get meeting tasks for user1
    meeting_tasks = MeetingTask.objects.filter(assigned_to=user1)
    print(f"Meeting tasks for {user1.username}: {meeting_tasks.count()}")
    
    for task in meeting_tasks:
        print(f"  - {task.description} (Status: {task.status})")

def test_unified_task_view():
    """Test the unified task view logic"""
    print("\n" + "="*50)
    print("TESTING UNIFIED TASK VIEW LOGIC")
    print("="*50)
    
    # Get a user with meeting tasks
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        print("❌ Test user not found. Run create_test_data first.")
        return
    
    # Simulate the task_list view logic
    from datetime import datetime
    
    # Get regular tasks
    regular_tasks = Task.objects.filter(assigned_to=user)
    
    # Get meeting tasks assigned to the user
    meeting_tasks = MeetingTask.objects.filter(assigned_to=user)
    
    # Create unified task list with additional metadata
    unified_tasks = []
    
    # Add regular tasks
    for task in regular_tasks:
        unified_tasks.append({
            'id': task.id,
            'description': task.description,
            'status': task.status,
            'start_date': task.start_date,
            'end_date': task.end_date,
            'assigned_to': task.assigned_to,
            'created_by': task.created_by,
            'meeting': task.meeting,
            'task_type': 'regular',
            'get_status_display': task.get_status_display(),
        })
    
    # Add meeting tasks
    for mtask in meeting_tasks:
        # Convert end_date to datetime for consistency
        end_datetime = None
        if mtask.end_date:
            end_datetime = datetime.combine(mtask.end_date, datetime.min.time())
        
        unified_tasks.append({
            'id': f"meeting_{mtask.id}",
            'description': mtask.description,
            'status': mtask.status,
            'start_date': mtask.created_at,
            'end_date': end_datetime,
            'assigned_to': mtask.assigned_to,
            'created_by': None,
            'meeting': mtask.meeting,
            'task_type': 'meeting',
            'get_status_display': dict(MeetingTask.STATUS_CHOICES).get(mtask.status, mtask.status),
        })
    
    # Sort unified tasks by end_date (most recent first)
    unified_tasks.sort(key=lambda x: x['end_date'] or datetime.min, reverse=True)
    
    print(f"User: {user.username}")
    print(f"Total unified tasks: {len(unified_tasks)}")
    print(f"Regular tasks: {len([t for t in unified_tasks if t['task_type'] == 'regular'])}")
    print(f"Meeting tasks: {len([t for t in unified_tasks if t['task_type'] == 'meeting'])}")
    
    print("\nUnified Task List:")
    for i, task in enumerate(unified_tasks, 1):
        print(f"{i}. [{task['task_type'].upper()}] {task['description'][:50]}...")
        print(f"   Status: {task['get_status_display']}")
        print(f"   ID: {task['id']}")
        if task['meeting']:
            print(f"   Meeting: {task['meeting'].title}")
        print()

if __name__ == "__main__":
    print("🚀 Starting Integration Test")
    print("="*50)
    
    try:
        test_task_list_integration()
        test_unified_task_view()
        print("\n✅ Integration test completed successfully!")
        print("\nNext steps:")
        print("1. Login to the system")
        print("2. Navigate to /tasks/list/")
        print("3. Verify that meeting tasks appear with 'مهمة اجتماع' badge")
        print("4. Test status updates on meeting tasks")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
