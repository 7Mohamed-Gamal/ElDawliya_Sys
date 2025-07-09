#!/usr/bin/env python
"""
Django Migration Conflict Resolver
A utility script to help resolve common Django migration conflicts
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
    django.setup()

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = %s
        """, [table_name])
        return cursor.fetchone()[0] > 0

def list_migration_status(app_name):
    """List migration status for an app"""
    print(f"\n=== Migration Status for {app_name} ===")
    execute_from_command_line(['manage.py', 'showmigrations', app_name])

def fake_migration(app_name, migration_name):
    """Fake a specific migration"""
    print(f"\n=== Faking migration {app_name}.{migration_name} ===")
    execute_from_command_line(['manage.py', 'migrate', app_name, migration_name, '--fake'])

def check_migration_conflicts():
    """Check for common migration conflicts"""
    setup_django()
    
    print("=== Django Migration Conflict Checker ===")
    
    # Common tables that might cause conflicts
    common_tables = [
        'Hr_AttendanceMachine',
        'Hr_AttendanceRecord', 
        'Hr_AttendanceSummary',
        'Hr_Car',
        'Hr_hremployeenote',
        'Hr_hremployeenotehistory'
    ]
    
    print("\n=== Checking for existing tables ===")
    existing_tables = []
    for table in common_tables:
        if check_table_exists(table):
            existing_tables.append(table)
            print(f"✓ Table exists: {table}")
        else:
            print(f"✗ Table missing: {table}")
    
    return existing_tables

def resolve_hr_migration_conflicts():
    """Resolve common Hr app migration conflicts"""
    setup_django()
    
    print("=== Hr App Migration Conflict Resolver ===")
    
    # Check current migration status
    list_migration_status('Hr')
    
    # Check for table conflicts
    existing_tables = check_migration_conflicts()
    
    if existing_tables:
        print(f"\n=== Found {len(existing_tables)} existing tables ===")
        print("This suggests that some migrations may need to be faked.")
        
        response = input("\nDo you want to fake the latest Hr migration? (y/n): ")
        if response.lower() == 'y':
            # Get the latest migration
            from django.db.migrations.recorder import MigrationRecorder
            recorder = MigrationRecorder(connection)
            applied_migrations = recorder.applied_migrations()
            
            # Find unapplied Hr migrations
            from django.db.migrations.loader import MigrationLoader
            loader = MigrationLoader(connection)
            hr_migrations = loader.graph.nodes
            hr_migrations = [m for m in hr_migrations if m[0] == 'Hr']
            
            unapplied = []
            for migration in hr_migrations:
                if migration not in applied_migrations:
                    unapplied.append(migration)
            
            if unapplied:
                latest_migration = max(unapplied, key=lambda x: x[1])
                print(f"Faking migration: {latest_migration[0]}.{latest_migration[1]}")
                fake_migration(latest_migration[0], latest_migration[1])
            else:
                print("No unapplied migrations found.")
    else:
        print("\nNo table conflicts detected. You can run migrations normally.")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'check':
            check_migration_conflicts()
        elif sys.argv[1] == 'resolve':
            resolve_hr_migration_conflicts()
        elif sys.argv[1] == 'status':
            setup_django()
            list_migration_status('Hr')
        else:
            print("Usage: python migration_conflict_resolver.py [check|resolve|status]")
    else:
        print("Django Migration Conflict Resolver")
        print("Usage:")
        print("  python migration_conflict_resolver.py check    - Check for table conflicts")
        print("  python migration_conflict_resolver.py resolve  - Resolve Hr migration conflicts")
        print("  python migration_conflict_resolver.py status   - Show Hr migration status")

if __name__ == '__main__':
    main()
