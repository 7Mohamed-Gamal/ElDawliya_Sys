#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.db import connection

def check_all_hr_dependencies():
    """
    Check all migrations that depend on Hr app migrations and their current state.
    """
    
    print("=== Checking All Hr Migration Dependencies ===")
    
    with connection.cursor() as cursor:
        # Get all applied migrations
        cursor.execute("""
            SELECT app, name 
            FROM django_migrations 
            ORDER BY app, name
        """)
        
        applied_migrations = set()
        for app, name in cursor.fetchall():
            applied_migrations.add(f"{app}.{name}")
        
        print(f"Total applied migrations: {len(applied_migrations)}")
        
        # Check Hr migrations specifically
        hr_migrations = [m for m in applied_migrations if m.startswith('Hr.')]
        print(f"\nHr migrations applied: {len(hr_migrations)}")
        for migration in sorted(hr_migrations):
            print(f"  ✓ {migration}")
        
        # Check for problematic dependencies
        problematic_apps = []
        
        # Check attendance app
        if 'attendance.0001_initial' in applied_migrations:
            if 'Hr.0003_alter_employee_emp_image' not in applied_migrations:
                problematic_apps.append('attendance.0001_initial depends on Hr.0003_alter_employee_emp_image')
        
        # Check cars app
        cars_migrations = [m for m in applied_migrations if m.startswith('cars.')]
        print(f"\nCars migrations applied: {len(cars_migrations)}")
        for migration in sorted(cars_migrations):
            print(f"  ✓ {migration}")
        
        # Check other apps that might depend on Hr
        other_apps = ['employee_tasks', 'tasks', 'meetings', 'notifications']
        for app in other_apps:
            app_migrations = [m for m in applied_migrations if m.startswith(f'{app}.')]
            if app_migrations:
                print(f"\n{app} migrations applied: {len(app_migrations)}")
                for migration in sorted(app_migrations):
                    print(f"  ✓ {migration}")
        
        if problematic_apps:
            print(f"\n❌ Problematic dependencies found:")
            for problem in problematic_apps:
                print(f"  - {problem}")
        else:
            print(f"\n✅ No obvious dependency conflicts detected")
        
        print(f"\n=== Summary ===")
        print(f"Hr migrations need to be applied first before other dependent apps")
        print(f"Current Hr migration status: {len(hr_migrations)} applied")

if __name__ == "__main__":
    check_all_hr_dependencies()
