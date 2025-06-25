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

def comprehensive_migration_fix():
    """
    Comprehensive fix for migration dependency conflicts.
    
    Issues found:
    1. cars.0004 depends on Hr.0002_initial (not applied)
    2. attendance.0001_initial depends on Hr.0003_alter_employee_emp_image (not applied)
    3. No Hr migrations are applied at all
    
    Solution: Remove all dependent migrations, apply Hr migrations, then re-apply dependent migrations.
    """
    
    print("=== Comprehensive Django Migration Dependency Fix ===")
    print("Fixing all migration dependency conflicts...")
    
    with connection.cursor() as cursor:
        # Step 1: Check current state
        print("\n1. Checking current migration state...")
        
        cursor.execute("""
            SELECT app, name 
            FROM django_migrations 
            ORDER BY app, name
        """)
        
        all_migrations = cursor.fetchall()
        print(f"Total applied migrations: {len(all_migrations)}")
        
        # Find problematic migrations
        problematic_migrations = []
        
        # Check for attendance.0001_initial (depends on Hr.0003)
        cursor.execute("""
            SELECT 1 FROM django_migrations 
            WHERE app = 'attendance' AND name = '0001_initial'
        """)
        if cursor.fetchone():
            problematic_migrations.append(('attendance', '0001_initial'))
        
        # Check for cars.0004 (already removed, but let's be sure)
        cursor.execute("""
            SELECT 1 FROM django_migrations 
            WHERE app = 'cars' AND name = '0004_delete_employee_alter_routepoint_employees'
        """)
        if cursor.fetchone():
            problematic_migrations.append(('cars', '0004_delete_employee_alter_routepoint_employees'))
        
        print(f"Found {len(problematic_migrations)} problematic migrations:")
        for app, name in problematic_migrations:
            print(f"  - {app}.{name}")
        
        # Step 2: Remove problematic migration records
        if problematic_migrations:
            print("\n2. Removing problematic migration records...")
            
            for app, name in problematic_migrations:
                cursor.execute("""
                    DELETE FROM django_migrations 
                    WHERE app = %s AND name = %s
                """, [app, name])
                
                deleted_count = cursor.rowcount
                print(f"  Removed {app}.{name} ({deleted_count} record)")
        else:
            print("\n2. No problematic migration records to remove")
        
        # Step 3: Verify Hr migrations are not applied
        cursor.execute("""
            SELECT name FROM django_migrations 
            WHERE app = 'Hr'
            ORDER BY name
        """)
        
        hr_migrations = cursor.fetchall()
        if hr_migrations:
            print(f"\n3. Warning: Found {len(hr_migrations)} Hr migrations already applied:")
            for (name,) in hr_migrations:
                print(f"  - Hr.{name}")
        else:
            print("\n3. Confirmed: No Hr migrations are applied (as expected)")
        
        print("\n✅ Migration dependency conflicts resolved!")
        print("\nNext steps to complete the fix:")
        print("1. Run: python manage.py migrate Hr")
        print("2. Run: python manage.py migrate attendance")
        print("3. Run: python manage.py migrate cars")
        print("4. Run: python manage.py showmigrations to verify")
        print("5. Run: python manage.py makemigrations to test")

if __name__ == "__main__":
    try:
        with transaction.atomic():
            comprehensive_migration_fix()
    except Exception as e:
        print(f"❌ Error fixing migration dependencies: {e}")
        sys.exit(1)
