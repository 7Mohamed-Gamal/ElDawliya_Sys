#!/usr/bin/env python
"""
Validation script for the task detail implementation
This script validates that all the implemented features are working correctly
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_Sys.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from tasks.models import Task, TaskStep
from meetings.models import Meeting, MeetingTask
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def validate_models():
    """Validate that models have the expected fields"""
    print("🔍 Validating Task model...")
    
    # Check Task model fields
    task_fields = [field.name for field in Task._meta.fields]
    expected_fields = ['id', 'title', 'meeting', 'assigned_to', 'created_by', 
                      'description', 'start_date', 'end_date', 'status', 
                      'created_at', 'updated_at']
    
    missing_fields = [field for field in expected_fields if field not in task_fields]
    if missing_fields:
        print(f"❌ Missing fields in Task model: {missing_fields}")
        return False
    else:
        print("✅ Task model has all expected fields")
    
    # Check Task model methods
    if hasattr(Task, 'get_display_title') and hasattr(Task, 'get_status_display'):
        print("✅ Task model has required methods")
    else:
        print("❌ Task model missing required methods")
        return False
    
    return True

def validate_views():
    """Validate that views are working correctly"""
    print("\n🔍 Validating views...")
    
    try:
        from tasks.views import task_detail, task_list, update_task_status
        print("✅ All required views are importable")
        return True
    except ImportError as e:
        print(f"❌ Error importing views: {e}")
        return False

def validate_templates():
    """Validate that templates exist and have required content"""
    print("\n🔍 Validating templates...")
    
    templates_to_check = [
        'tasks/templates/tasks/task_detail.html',
        'tasks/templates/tasks/task_list.html',
        'tasks/templates/tasks/task_form.html'
    ]
    
    for template_path in templates_to_check:
        if os.path.exists(template_path):
            print(f"✅ Template exists: {template_path}")
            
            # Check for key content in task_detail.html
            if 'task_detail.html' in template_path:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    required_content = [
                        'تفاصيل المهمة',
                        'is_meeting_task',
                        'meeting_tasks_stats',
                        'steps_stats'
                    ]
                    
                    for required in required_content:
                        if required in content:
                            print(f"  ✅ Contains: {required}")
                        else:
                            print(f"  ❌ Missing: {required}")
        else:
            print(f"❌ Template missing: {template_path}")
            return False
    
    return True

def validate_urls():
    """Validate that URL patterns are correctly configured"""
    print("\n🔍 Validating URL patterns...")
    
    try:
        # Test URL reverse
        task_detail_url = reverse('tasks:detail', kwargs={'pk': 1})
        task_list_url = reverse('tasks:list')
        update_status_url = reverse('tasks:update_task_status', kwargs={'pk': 1})
        
        print("✅ All URL patterns are correctly configured")
        print(f"  - Task detail URL: {task_detail_url}")
        print(f"  - Task list URL: {task_list_url}")
        print(f"  - Update status URL: {update_status_url}")
        return True
    except Exception as e:
        print(f"❌ URL configuration error: {e}")
        return False

def validate_forms():
    """Validate that forms have the expected fields"""
    print("\n🔍 Validating forms...")
    
    try:
        from tasks.forms import TaskForm, TaskStepForm
        
        # Check TaskForm fields
        task_form = TaskForm()
        expected_fields = ['title', 'description', 'assigned_to', 'start_date', 'end_date', 'status']
        form_fields = list(task_form.fields.keys())
        
        missing_fields = [field for field in expected_fields if field not in form_fields]
        if missing_fields:
            print(f"❌ TaskForm missing fields: {missing_fields}")
            return False
        else:
            print("✅ TaskForm has all expected fields")
        
        # Check TaskStepForm
        step_form = TaskStepForm()
        if 'description' in step_form.fields:
            print("✅ TaskStepForm has required fields")
        else:
            print("❌ TaskStepForm missing required fields")
            return False
        
        return True
    except ImportError as e:
        print(f"❌ Error importing forms: {e}")
        return False

def validate_migrations():
    """Check if migrations are applied"""
    print("\n🔍 Validating migrations...")
    
    try:
        # Try to create a task instance to test the new fields
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT title, created_at, updated_at FROM tasks_task LIMIT 1")
            print("✅ New Task model fields are available in database")
        
        return True
    except Exception as e:
        print(f"❌ Migration validation error: {e}")
        print("   Make sure to run: python manage.py migrate tasks")
        return False

def create_test_data():
    """Create some test data to validate functionality"""
    print("\n🔍 Creating test data...")
    
    try:
        # Create test user if not exists
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print("✅ Created test user")
        else:
            print("✅ Test user already exists")
        
        # Create test task
        task, created = Task.objects.get_or_create(
            title='Test Task Implementation',
            defaults={
                'description': 'This is a test task to validate the implementation',
                'assigned_to': user,
                'created_by': user,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=7),
                'status': 'pending'
            }
        )
        
        if created:
            print("✅ Created test task")
        else:
            print("✅ Test task already exists")
        
        # Create test step
        step, created = TaskStep.objects.get_or_create(
            task=task,
            defaults={
                'description': 'Test step for validation'
            }
        )
        
        if created:
            print("✅ Created test task step")
        else:
            print("✅ Test task step already exists")
        
        print(f"📋 Test task ID: {task.id}")
        print(f"📋 Test task URL: /tasks/{task.id}/")
        
        return True
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return False

def main():
    """Run all validation checks"""
    print("🚀 Starting Task Detail Implementation Validation")
    print("=" * 60)
    
    checks = [
        ("Model Validation", validate_models),
        ("View Validation", validate_views),
        ("Template Validation", validate_templates),
        ("URL Validation", validate_urls),
        ("Form Validation", validate_forms),
        ("Migration Validation", validate_migrations),
        ("Test Data Creation", create_test_data)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{check_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All validations passed! The task detail implementation is ready.")
        print("\n📝 Next steps:")
        print("1. Test the application manually by visiting /tasks/")
        print("2. Create some tasks and test the detail pages")
        print("3. Test both regular tasks and meeting tasks")
        print("4. Verify Arabic labels and UI consistency")
    else:
        print("⚠️  Some validations failed. Please review and fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
