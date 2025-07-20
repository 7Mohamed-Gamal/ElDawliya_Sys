#!/usr/bin/env python
"""
Systematically fix migration 0017 by commenting out all operations 
that reference non-existent tables.
"""

import os
import django
import re
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.db import connection


def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = %s
        """, [table_name])
        return cursor.fetchone() is not None


def get_existing_tables():
    """Get all existing tables in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo'
            ORDER BY TABLE_NAME
        """)
        return [row[0] for row in cursor.fetchall()]


def get_model_table_name(model_name):
    """Get the expected table name for a Django model"""
    # Common patterns for table naming
    patterns = [
        f'hrms_{model_name.lower()}',
        f'Hr_{model_name}',
        f'Hr_{model_name.lower()}',
        f'{model_name}',
        f'{model_name.lower()}'
    ]
    return patterns


def fix_migration_file():
    """Fix the migration file by commenting out problematic operations"""
    migration_file = Path('Hr/migrations/0017_employeebank_employeecontact_employeeeducation_and_more.py')
    
    # Read the file
    with open(migration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get existing tables
    existing_tables = get_existing_tables()
    print(f"Found {len(existing_tables)} existing tables")
    
    # Models that are known to have issues
    problematic_models = [
        'employeeemergencycontact',
        'employeetraining',
        'hrattendancesummary',
        'hrpickuppoint',
        'hremployeeattendancerule',
        'hremployeenote',
        'hremployeenotehistory',
        'hremployeetask',
        'hrtasknew',
        'taskstep',
        'legacyemployee',
        'hrattendancerecord',
        'hrofficialholiday'
    ]
    
    # Check which models have missing tables
    missing_models = []
    for model in problematic_models:
        possible_tables = get_model_table_name(model)
        table_exists = any(table in existing_tables for table in possible_tables)
        if not table_exists:
            missing_models.append(model)
            print(f"✗ Model '{model}' - no matching table found")
        else:
            print(f"✓ Model '{model}' - table exists")
    
    # Comment out operations for missing models
    operations_to_comment = [
        'AlterUniqueTogether',
        'RemoveField',
        'DeleteModel'
    ]
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a problematic operation
        should_comment = False
        operation_type = None
        model_name = None
        
        for op_type in operations_to_comment:
            if f'migrations.{op_type}(' in line:
                operation_type = op_type
                # Look for the model name in the next few lines
                for j in range(i, min(i + 5, len(lines))):
                    if 'name=' in lines[j] or 'model_name=' in lines[j]:
                        # Extract model name
                        match = re.search(r"(?:name|model_name)='([^']+)'", lines[j])
                        if match:
                            model_name = match.group(1).lower()
                            if model_name in missing_models:
                                should_comment = True
                            break
                break
        
        if should_comment:
            # Find the end of this operation (look for the closing ),)
            operation_lines = [line]
            j = i + 1
            paren_count = line.count('(') - line.count(')')
            
            while j < len(lines) and paren_count > 0:
                operation_lines.append(lines[j])
                paren_count += lines[j].count('(') - lines[j].count(')')
                j += 1
            
            # Comment out all lines of this operation
            commented_lines = [f'        # COMMENTED OUT - Model "{model_name}" table does not exist']
            for op_line in operation_lines:
                commented_lines.append(f'        # {op_line.lstrip()}')
            
            new_lines.extend(commented_lines)
            i = j
            print(f"✓ Commented out {operation_type} for model '{model_name}'")
        else:
            new_lines.append(line)
            i += 1
    
    # Write the fixed content
    fixed_content = '\n'.join(new_lines)
    
    # Backup original
    backup_file = migration_file.with_suffix('.py.backup2')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backed up original to {backup_file}")
    
    # Write fixed version
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print(f"✓ Fixed migration file")
    
    return True


def main():
    print("Systematic Migration 0017 Fix")
    print("=" * 40)
    
    print("\n1. Analyzing existing tables...")
    existing_tables = get_existing_tables()
    print(f"Found tables: {', '.join(existing_tables[:10])}..." if len(existing_tables) > 10 else f"Found tables: {', '.join(existing_tables)}")
    
    print("\n2. Fixing migration file...")
    if fix_migration_file():
        print("\n✓ Migration file fixed successfully!")
        print("\nNext step: Run 'python manage.py migrate Hr 0017'")
    else:
        print("\n✗ Failed to fix migration file")


if __name__ == '__main__':
    main()
