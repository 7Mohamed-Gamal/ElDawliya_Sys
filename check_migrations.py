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

def check_migration_records():
    with connection.cursor() as cursor:
        # Check what migrations are recorded in the database
        cursor.execute("""
            SELECT app, name 
            FROM django_migrations 
            WHERE app IN ('Hr', 'cars') 
            ORDER BY app, name
        """)
        
        print("=== Migration records in database ===")
        for row in cursor.fetchall():
            print(f"{row[0]}.{row[1]}")
        
        print("\n=== Cars migrations that depend on Hr ===")
        # Check cars migrations that depend on Hr
        cursor.execute("""
            SELECT app, name 
            FROM django_migrations 
            WHERE app = 'cars' AND name = '0004_delete_employee_alter_routepoint_employees'
        """)
        
        cars_0004_exists = cursor.fetchone()
        if cars_0004_exists:
            print("cars.0004_delete_employee_alter_routepoint_employees is recorded as applied")
        else:
            print("cars.0004_delete_employee_alter_routepoint_employees is NOT recorded as applied")
            
        cursor.execute("""
            SELECT app, name 
            FROM django_migrations 
            WHERE app = 'Hr' AND name = '0002_initial'
        """)
        
        hr_0002_exists = cursor.fetchone()
        if hr_0002_exists:
            print("Hr.0002_initial is recorded as applied")
        else:
            print("Hr.0002_initial is NOT recorded as applied")

        print("\n=== Checking if Hr tables exist ===")
        # Check if Hr_employee table exists (created by Hr.0002_initial)
        try:
            cursor.execute("SELECT COUNT(*) FROM Hr_employee")
            count = cursor.fetchone()[0]
            print(f"Hr_employee table exists with {count} records")
        except Exception as e:
            print(f"Hr_employee table does NOT exist: {e}")

if __name__ == "__main__":
    check_migration_records()
