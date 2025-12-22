"""
Script to fix migration issues in the administrator app.
This will fake the problematic migration 0003 and drop orphaned tables.
"""
import os
import sys
import sqlite3
from datetime import datetime

# Get the database path
DB_PATH = 'db.sqlite3'

def main():
    print("=" * 60)
    print("ElDawliya Migration Fix Script")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database {DB_PATH} not found!")
        return 1
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Step 1: Check current migration status
    print("\n[Step 1] Checking current migration status...")
    cursor.execute("SELECT app, name FROM django_migrations WHERE app='administrator' ORDER BY id")
    applied = cursor.fetchall()
    print(f"Applied administrator migrations: {[m[1] for m in applied]}")
    
    # Step 2: Fake migration 0003
    print("\n[Step 2] Faking migration 0003...")
    migration_name = '0003_remove_pagepermission_app_module_and_more'
    cursor.execute("SELECT COUNT(*) FROM django_migrations WHERE app='administrator' AND name=?", (migration_name,))
    exists = cursor.fetchone()[0]
    
    if exists:
        print(f"  Migration {migration_name} already marked as applied")
    else:
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
            ('administrator', migration_name, datetime.now().isoformat())
        )
        print(f"  Marked {migration_name} as applied")
    
    # Step 3: Drop orphaned tables that migration 0003 was supposed to delete
    print("\n[Step 3] Dropping orphaned administrator tables...")
    tables_to_drop = [
        'administrator_appmodule',
        'administrator_groupprofile', 
        'administrator_operationpermission',
        'administrator_pagepermission',
        'administrator_permission',
        'administrator_permission_groups',
        'administrator_permission_users',
        'administrator_permissionauditlog',
        'administrator_permissiongroup',
        'administrator_permissiongroup_permissions',
        'administrator_templatepermission',
        'administrator_templatepermission_groups',
        'administrator_templatepermission_users',
        'administrator_userdepartmentpermission',
        'administrator_usergroup',
        'administrator_usermodulepermission',
        'administrator_useroperationpermission',
        'administrator_userpagepermission',
    ]
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  Dropped table: {table}")
        except Exception as e:
            print(f"  Warning: Could not drop {table}: {e}")
    
    # Commit changes
    conn.commit()
    
    # Step 4: Verify
    print("\n[Step 4] Verifying migration status...")
    cursor.execute("SELECT app, name FROM django_migrations WHERE app='administrator' ORDER BY id")
    applied = cursor.fetchall()
    print(f"Applied administrator migrations: {[m[1] for m in applied]}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("Migration fix complete!")
    print("Run 'python manage.py migrate' to apply remaining migrations.")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

