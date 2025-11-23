#!/usr/bin/env python
"""
Validation script for the new unified project models.
This script validates the model structure, relationships, and basic functionality.
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings.development')
django.setup()

from django.core.exceptions import ValidationError
from django.db import connection
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import uuid


def test_model_imports():
    """Test that all new models can be imported successfully"""
    print("Testing model imports...")
    
    try:
        from core.models.projects import (
            ProjectCategory,
            Project,
            ProjectPhase,
            ProjectMilestone,
            ProjectMember,
            Task,
            TaskStep,
            TimeEntry,
            Meeting,
            MeetingAttendee,
            Document,
        )
        print("✓ All project models imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_model_structure():
    """Test model field structure and meta options"""
    print("\nTesting model structure...")
    
    try:
        from core.models.projects import Project, Task, Meeting
        
        # Test Project model
        project_fields = [field.name for field in Project._meta.fields]
        required_project_fields = [
            'id', 'name', 'code', 'description', 'status', 'priority',
            'start_date', 'end_date', 'progress_percentage', 'created_at'
        ]
        
        for field in required_project_fields:
            if field not in project_fields:
                print(f"✗ Missing field '{field}' in Project model")
                return False
        
        # Test Task model
        task_fields = [field.name for field in Task._meta.fields]
        required_task_fields = [
            'id', 'title', 'description', 'task_type', 'status', 'priority',
            'start_date', 'due_date', 'progress_percentage', 'created_at'
        ]
        
        for field in required_task_fields:
            if field not in task_fields:
                print(f"✗ Missing field '{field}' in Task model")
                return False
        
        # Test Meeting model
        meeting_fields = [field.name for field in Meeting._meta.fields]
        required_meeting_fields = [
            'id', 'title', 'meeting_type', 'start_datetime', 'end_datetime',
            'status', 'organizer', 'created_at'
        ]
        
        for field in required_meeting_fields:
            if field not in meeting_fields:
                print(f"✗ Missing field '{field}' in Meeting model")
                return False
        
        print("✓ All required fields present in models")
        return True
        
    except Exception as e:
        print(f"✗ Model structure test failed: {e}")
        return False


def test_model_relationships():
    """Test model relationships and foreign keys"""
    print("\nTesting model relationships...")
    
    try:
        from core.models.projects import Project, Task, Meeting, ProjectPhase
        
        # Test Project relationships
        project_relations = [rel.name for rel in Project._meta.related_objects]
        expected_relations = ['phases', 'tasks', 'meetings', 'milestones', 'memberships']
        
        for relation in expected_relations:
            if relation not in project_relations:
                print(f"✗ Missing relation '{relation}' in Project model")
                return False
        
        # Test Task relationships
        task_relations = [rel.name for rel in Task._meta.related_objects]
        expected_task_relations = ['steps', 'time_entries', 'documents', 'subtasks']
        
        for relation in expected_task_relations:
            if relation not in task_relations:
                print(f"✗ Missing relation '{relation}' in Task model")
                return False
        
        print("✓ All required relationships present")
        return True
        
    except Exception as e:
        print(f"✗ Relationship test failed: {e}")
        return False


def test_model_validation():
    """Test model validation rules"""
    print("\nTesting model validation...")
    
    try:
        from core.models.projects import Project, Task, ProjectCategory
        
        # Create test category
        category = ProjectCategory(
            name="Test Category",
            description="Test category for validation",
            color="#3498db"
        )
        
        # Test Project validation
        project = Project(
            name="Test Project",
            code="TEST001",
            description="Test project for validation",
            category=category,
            status="planning",
            priority="medium",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            progress_percentage=0
        )
        
        # This should not raise validation error
        project.clean()
        
        # Test invalid date range
        invalid_project = Project(
            name="Invalid Project",
            code="INVALID001",
            description="Invalid project for validation",
            status="planning",
            priority="medium",
            start_date=date.today(),
            end_date=date.today() - timedelta(days=1),  # End before start
            progress_percentage=0
        )
        
        try:
            invalid_project.clean()
            print("✗ Validation should have failed for invalid date range")
            return False
        except ValidationError:
            pass  # Expected
        
        # Test Task validation
        task = Task(
            title="Test Task",
            description="Test task for validation",
            task_type="regular",
            status="pending",
            priority="medium",
            start_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=7),
            progress_percentage=0
        )
        
        # This should not raise validation error
        task.clean()
        
        print("✓ Model validation working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False


def test_model_methods():
    """Test model methods and properties"""
    print("\nTesting model methods...")
    
    try:
        from core.models.projects import Project, Task, Meeting
        from django.contrib.auth.models import User
        
        # Test Project methods
        project = Project(
            name="Test Project",
            code="TEST001",
            description="Test project",
            status="active",
            priority="high",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            progress_percentage=50
        )
        
        # Test properties
        assert hasattr(project, 'is_overdue'), "Project missing is_overdue property"
        assert hasattr(project, 'days_remaining'), "Project missing days_remaining property"
        assert hasattr(project, 'duration_days'), "Project missing duration_days property"
        
        # Test Task methods
        task = Task(
            title="Test Task",
            description="Test task",
            task_type="regular",
            status="in_progress",
            priority="high",
            start_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=7),
            progress_percentage=25
        )
        
        # Test properties
        assert hasattr(task, 'is_overdue'), "Task missing is_overdue property"
        assert hasattr(task, 'days_until_due'), "Task missing days_until_due property"
        assert hasattr(task, 'tag_list'), "Task missing tag_list property"
        
        # Test Meeting methods
        meeting = Meeting(
            title="Test Meeting",
            meeting_type="team",
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=1),
            status="scheduled"
        )
        
        # Test properties
        assert hasattr(meeting, 'duration_hours'), "Meeting missing duration_hours property"
        assert hasattr(meeting, 'is_upcoming'), "Meeting missing is_upcoming property"
        assert hasattr(meeting, 'is_past'), "Meeting missing is_past property"
        
        print("✓ All model methods and properties working")
        return True
        
    except Exception as e:
        print(f"✗ Model methods test failed: {e}")
        return False


def test_database_tables():
    """Test that database tables would be created correctly"""
    print("\nTesting database table structure...")
    
    try:
        from core.models.projects import (
            ProjectCategory, Project, ProjectPhase, ProjectMilestone,
            ProjectMember, Task, TaskStep, TimeEntry, Meeting,
            MeetingAttendee, Document
        )
        
        # Check table names
        expected_tables = {
            'project_categories': ProjectCategory,
            'projects': Project,
            'project_phases': ProjectPhase,
            'project_milestones': ProjectMilestone,
            'project_members': ProjectMember,
            'tasks': Task,
            'task_steps': TaskStep,
            'time_entries': TimeEntry,
            'meetings': Meeting,
            'meeting_attendees': MeetingAttendee,
            'documents': Document,
        }
        
        for table_name, model_class in expected_tables.items():
            if model_class._meta.db_table != table_name:
                print(f"✗ Table name mismatch for {model_class.__name__}: expected {table_name}, got {model_class._meta.db_table}")
                return False
        
        print("✓ All database table names correct")
        return True
        
    except Exception as e:
        print(f"✗ Database table test failed: {e}")
        return False


def test_model_permissions():
    """Test model permissions"""
    print("\nTesting model permissions...")
    
    try:
        from core.models.projects import Project, Task, Meeting
        
        # Test Project permissions
        project_permissions = [perm[0] for perm in Project._meta.permissions]
        expected_project_perms = [
            'view_project_dashboard',
            'manage_project_team',
            'view_project_reports',
            'export_project_data'
        ]
        
        for perm in expected_project_perms:
            if perm not in project_permissions:
                print(f"✗ Missing permission '{perm}' in Project model")
                return False
        
        # Test Task permissions
        task_permissions = [perm[0] for perm in Task._meta.permissions]
        expected_task_perms = [
            'view_task_dashboard',
            'view_all_tasks',
            'manage_task_assignments',
            'view_task_reports',
            'export_task_data'
        ]
        
        for perm in expected_task_perms:
            if perm not in task_permissions:
                print(f"✗ Missing permission '{perm}' in Task model")
                return False
        
        print("✓ All model permissions defined correctly")
        return True
        
    except Exception as e:
        print(f"✗ Model permissions test failed: {e}")
        return False


def test_model_choices():
    """Test model choice fields"""
    print("\nTesting model choices...")
    
    try:
        from core.models.projects import Project, Task, Meeting
        
        # Test Project choices
        project_status_choices = [choice[0] for choice in Project.STATUS_CHOICES]
        expected_project_statuses = ['planning', 'active', 'on_hold', 'completed', 'cancelled', 'archived']
        
        for status in expected_project_statuses:
            if status not in project_status_choices:
                print(f"✗ Missing status choice '{status}' in Project model")
                return False
        
        # Test Task choices
        task_status_choices = [choice[0] for choice in Task.STATUS_CHOICES]
        expected_task_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'deferred', 'blocked']
        
        for status in expected_task_statuses:
            if status not in task_status_choices:
                print(f"✗ Missing status choice '{status}' in Task model")
                return False
        
        # Test Meeting choices
        meeting_type_choices = [choice[0] for choice in Meeting.TYPE_CHOICES]
        expected_meeting_types = ['project', 'team', 'client', 'review', 'planning', 'standup', 'other']
        
        for meeting_type in expected_meeting_types:
            if meeting_type not in meeting_type_choices:
                print(f"✗ Missing type choice '{meeting_type}' in Meeting model")
                return False
        
        print("✓ All model choices defined correctly")
        return True
        
    except Exception as e:
        print(f"✗ Model choices test failed: {e}")
        return False


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("VALIDATING UNIFIED PROJECT MODELS")
    print("=" * 60)
    
    tests = [
        test_model_imports,
        test_model_structure,
        test_model_relationships,
        test_model_validation,
        test_model_methods,
        test_database_tables,
        test_model_permissions,
        test_model_choices,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {passed + failed}")
    
    if failed == 0:
        print("\n✓ All tests passed! The unified project models are ready.")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)