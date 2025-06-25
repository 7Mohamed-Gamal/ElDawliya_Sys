#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.db import connection, transaction

def fix_migration_dependency():
    """
    Fix the migration dependency conflict between cars and Hr apps.
    
    The issue: cars.0004 is applied but depends on Hr.0002_initial which is not applied.
    Solution: Remove cars.0004 record, apply Hr migrations, then re-apply cars.0004.
    """
    
    print("=== Django Migration Dependency Fix ===")
    print("Fixing inconsistent migration history between cars and Hr apps...")
    
    with connection.cursor() as cursor:
        # Step 1: Check current state
        print("\n1. Checking current migration state...")
        
        cursor.execute("""
            SELECT app, name 
            FROM django_migrations 
            WHERE app IN ('Hr', 'cars') 
            ORDER BY app, name
        """)
        
        current_migrations = cursor.fetchall()
        print("Current applied migrations:")
        for app, name in current_migrations:
            print(f"  - {app}.{name}")
        
        # Step 2: Remove the problematic cars.0004 migration record
        print("\n2. Removing conflicting cars.0004 migration record...")
        
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'cars' AND name = '0004_delete_employee_alter_routepoint_employees'
        """)
        
        deleted_count = cursor.rowcount
        print(f"Removed {deleted_count} migration record(s)")
        
        # Step 3: Verify the removal
        print("\n3. Verifying migration records after removal...")
        
        cursor.execute("""
            SELECT app, name 
            FROM django_migrations 
            WHERE app IN ('Hr', 'cars') 
            ORDER BY app, name
        """)
        
        remaining_migrations = cursor.fetchall()
        print("Remaining applied migrations:")
        for app, name in remaining_migrations:
            print(f"  - {app}.{name}")
        
        print("\n✅ Migration dependency conflict resolved!")
        print("\nNext steps:")
        print("1. Run: python manage.py migrate Hr")
        print("2. Run: python manage.py migrate cars")
        print("3. Run: python manage.py showmigrations to verify")
        print("4. Run: python manage.py makemigrations to test")

if __name__ == "__main__":
    try:
        with transaction.atomic():
            fix_migration_dependency()
    except Exception as e:
        print(f"❌ Error fixing migration dependency: {e}")
        sys.exit(1)
