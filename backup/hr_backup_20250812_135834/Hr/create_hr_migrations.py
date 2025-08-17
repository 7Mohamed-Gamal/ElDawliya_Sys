#!/usr/bin/env python
"""
Script to create and apply HR migrations systematically
This script ensures all HR models are properly migrated
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
    django.setup()

def create_migrations():
    """Create migrations for HR app"""
    print("Creating migrations for HR app...")
    
    try:
        # Create migrations for Hr app
        execute_from_command_line(['manage.py', 'makemigrations', 'Hr'])
        print("✓ HR migrations created successfully")
        
        # Show migration plan
        print("\nMigration plan:")
        execute_from_command_line(['manage.py', 'showmigrations', 'Hr'])
        
        return True
    except Exception as e:
        print(f"✗ Error creating migrations: {e}")
        return False

def apply_migrations():
    """Apply migrations to database"""
    print("\nApplying migrations...")
    
    try:
        # Apply migrations
        execute_from_command_line(['manage.py', 'migrate', 'Hr'])
        print("✓ HR migrations applied successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error applying migrations: {e}")
        return False

def check_migrations():
    """Check migration status"""
    print("\nChecking migration status...")
    
    try:
        execute_from_command_line(['manage.py', 'showmigrations', 'Hr'])
        return True
    except Exception as e:
        print(f"✗ Error checking migrations: {e}")
        return False

def main():
    """Main function"""
    print("HR Migration Management Script")
    print("=" * 40)
    
    # Setup Django
    setup_django()
    
    # Check current migration status
    print("Current migration status:")
    check_migrations()
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Create new migrations")
    print("2. Apply migrations")
    print("3. Create and apply migrations")
    print("4. Check migration status only")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        create_migrations()
    elif choice == '2':
        apply_migrations()
    elif choice == '3':
        if create_migrations():
            apply_migrations()
    elif choice == '4':
        check_migrations()
    elif choice == '5':
        print("Exiting...")
        return
    else:
        print("Invalid choice. Exiting...")
        return
    
    # Final status check
    print("\nFinal migration status:")
    check_migrations()

if __name__ == '__main__':
    main()