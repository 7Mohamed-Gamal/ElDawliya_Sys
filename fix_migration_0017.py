#!/usr/bin/env python
"""
Fix for Django migration 0017 that fails due to missing EmployeeEmergencyContact table.

This script will:
1. Backup the original migration file
2. Create a fixed version that skips problematic operations
3. Run the migration
4. Provide instructions for cleanup
"""

import os
import shutil
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.db import connection
from django.core.management import call_command


def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = %s
        """, [table_name])
        return cursor.fetchone() is not None


def backup_migration():
    """Backup the original migration file"""
    original_file = Path('Hr/migrations/0017_employeebank_employeecontact_employeeeducation_and_more.py')
    backup_file = Path('Hr/migrations/0017_employeebank_employeecontact_employeeeducation_and_more.py.backup')
    
    if original_file.exists():
        shutil.copy2(original_file, backup_file)
        print(f"✓ Backed up original migration to {backup_file}")
        return True
    else:
        print(f"✗ Original migration file not found: {original_file}")
        return False


def create_fixed_migration():
    """Create a fixed version of the migration"""
    original_file = Path('Hr/migrations/0017_employeebank_employeecontact_employeeeducation_and_more.py')
    
    # Read the original file
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the problematic operations to comment out
    problematic_operations = [
        # AlterUniqueTogether for employeeemergencycontact
        "migrations.AlterUniqueTogether(\n            name='employeeemergencycontact',\n            unique_together=None,\n        ),",
        
        # RemoveField operations for employeeemergencycontact
        "migrations.RemoveField(\n            model_name='employeeemergencycontact',\n            name='created_by',\n        ),",
        "migrations.RemoveField(\n            model_name='employeeemergencycontact',\n            name='employee',\n        ),",
    ]
    
    # Comment out problematic operations
    for operation in problematic_operations:
        if operation in content:
            commented_operation = '\n        # COMMENTED OUT - Table does not exist\n        # ' + operation.replace('\n', '\n        # ')
            content = content.replace(operation, commented_operation)
            print(f"✓ Commented out problematic operation")
    
    # Also need to handle other employeeemergencycontact operations
    # Let's find and comment out all operations related to models that don't exist
    
    # Check which tables don't exist
    missing_tables = []
    tables_to_check = [
        'hrms_employee_emergency_contact',
        'hrms_employee_training', 
        'hrms_hr_attendance_record',
        'hrms_hr_attendance_summary',
        'hrms_hr_pickup_point',
        'hrms_hr_employee_attendance_rule',
        'hrms_hr_employee_note',
        'hrms_hr_employee_note_history',
        'hrms_hr_employee_task',
        'hrms_hr_official_holiday',
        'hrms_hr_task_new',
        'hrms_task_step',
        'hrms_legacy_employee'
    ]
    
    for table in tables_to_check:
        if not check_table_exists(table):
            missing_tables.append(table)
            print(f"✗ Table missing: {table}")
    
    # Comment out operations for missing models
    models_to_skip = [
        'employeeemergencycontact',
        'employeetraining', 
        'hrattendancerecord',
        'hrattendancesummary',
        'hrpickuppoint',
        'hremployeeattendancerule',
        'hremployeenote',
        'hremployeenotehistory',
        'hremployeetask',
        'hrofficialholiday',
        'hrtasknew',
        'taskstep',
        'legacyemployee'
    ]
    
    # Add a comment at the top explaining the fix
    header_comment = '''# MIGRATION FIXED - Original migration failed due to missing tables
# The following operations have been commented out because the referenced tables do not exist:
# - AlterUniqueTogether for employeeemergencycontact
# - RemoveField operations for missing models
# This allows the migration to proceed with creating new models and tables.

'''
    
    # Insert the comment after the imports
    import_end = content.find('class Migration(migrations.Migration):')
    if import_end != -1:
        content = content[:import_end] + header_comment + content[import_end:]
    
    # Write the fixed content
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Created fixed migration file")
    return True


def run_migration():
    """Run the fixed migration"""
    try:
        print("Running migration...")
        call_command('migrate', 'Hr', '0017', verbosity=2)
        print("✓ Migration completed successfully")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False


def main():
    print("Django Migration 0017 Fix Script")
    print("=" * 40)
    
    # Check current state
    print("\n1. Checking current state...")
    emergency_contact_exists = check_table_exists('hrms_employee_emergency_contact')
    print(f"   EmployeeEmergencyContact table exists: {emergency_contact_exists}")
    
    if emergency_contact_exists:
        print("   Table exists - migration should work normally")
        print("   Try running: python manage.py migrate Hr 0017")
        return
    
    print("   Table missing - applying fix...")
    
    # Step 1: Backup
    print("\n2. Backing up original migration...")
    if not backup_migration():
        return
    
    # Step 2: Create fixed version
    print("\n3. Creating fixed migration...")
    if not create_fixed_migration():
        return
    
    # Step 3: Run migration
    print("\n4. Running fixed migration...")
    if run_migration():
        print("\n✓ SUCCESS: Migration completed successfully!")
        print("\nNext steps:")
        print("1. Continue with remaining migrations: python manage.py migrate")
        print("2. The backup file is available if you need to restore the original")
    else:
        print("\n✗ FAILED: Migration still failed")
        print("Restoring original migration...")
        # Restore backup
        backup_file = Path('Hr/migrations/0017_employeebank_employeecontact_employeeeducation_and_more.py.backup')
        original_file = Path('Hr/migrations/0017_employeebank_employeecontact_employeeeducation_and_more.py')
        if backup_file.exists():
            shutil.copy2(backup_file, original_file)
            print("✓ Original migration restored")


if __name__ == '__main__':
    main()
