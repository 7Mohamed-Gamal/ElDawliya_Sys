"""
Script to check the current database schema and identify migration issues
This will help us understand what tables exist and resolve the migration conflicts
"""

import os
import sys
import django
from django.db import connection

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
            return True
        except Exception as e:
            return False, str(e)

def get_table_structure(table_name):
    """Get the structure of a table"""
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            return cursor.fetchall()
        except Exception as e:
            return None, str(e)

def check_migration_status():
    """Check the current migration status"""
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT app, name, applied 
                FROM django_migrations 
                WHERE app = 'Hr' 
                ORDER BY applied DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            return None, str(e)

def main():
    print("Database Schema Check for Hr Migration Issues")
    print("=" * 60)
    
    # Check migration status
    print("\n1. Current Migration Status:")
    print("-" * 30)
    migrations = check_migration_status()
    if migrations:
        for app, name, applied in migrations[-10:]:  # Show last 10
            print(f"  {app}.{name} - {applied}")
    else:
        print("  Could not retrieve migration status")
    
    # Check for problematic tables
    print("\n2. Table Existence Check:")
    print("-" * 30)
    
    tables_to_check = [
        'Tbl_Job',      # The table mentioned in the error
        'Tbl_Jop',      # The table both models claim to use
        'Tbl_Employee', # Referenced in the migration
        'django_migrations'
    ]
    
    for table in tables_to_check:
        exists = check_table_exists(table)
        if exists is True:
            print(f"  ✅ {table} - EXISTS")
        else:
            print(f"  ❌ {table} - NOT FOUND")
            if isinstance(exists, tuple):
                print(f"     Error: {exists[1]}")
    
    # Check Tbl_Jop structure if it exists
    print("\n3. Tbl_Jop Table Structure:")
    print("-" * 30)
    structure = get_table_structure('Tbl_Jop')
    if structure and not isinstance(structure, tuple):
        print("  Columns:")
        for column_name, data_type, is_nullable, default in structure:
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            print(f"    {column_name} - {data_type} {nullable}{default_str}")
    else:
        print("  Could not retrieve table structure")
        if isinstance(structure, tuple):
            print(f"  Error: {structure[1]}")
    
    # Check for model conflicts
    print("\n4. Model Conflict Analysis:")
    print("-" * 30)
    
    try:
        from Hr.models.legacy.legacy_models import Job as LegacyJob
        from Hr.models.job_models import HrJob
        
        print(f"  Legacy Job model:")
        print(f"    Table: {LegacyJob._meta.db_table}")
        print(f"    Managed: {LegacyJob._meta.managed}")
        
        print(f"  HrJob model:")
        print(f"    Table: {HrJob._meta.db_table}")
        print(f"    Managed: {HrJob._meta.managed}")
        
        if LegacyJob._meta.db_table == HrJob._meta.db_table:
            print("  ⚠️  CONFLICT: Both models use the same db_table!")
        
    except ImportError as e:
        print(f"  Could not import models: {e}")
    
    # Check current database connection
    print("\n5. Database Connection Info:")
    print("-" * 30)
    db_settings = connection.settings_dict
    print(f"  Engine: {db_settings.get('ENGINE', 'Unknown')}")
    print(f"  Host: {db_settings.get('HOST', 'Unknown')}")
    print(f"  Database: {db_settings.get('NAME', 'Unknown')}")
    
    # Recommendations
    print("\n6. Recommendations:")
    print("-" * 30)
    
    tbl_job_exists = check_table_exists('Tbl_Job')
    tbl_jop_exists = check_table_exists('Tbl_Jop')
    
    if tbl_jop_exists and not tbl_job_exists:
        print("  ✅ Tbl_Jop exists but Tbl_Job doesn't")
        print("     - The migration is looking for wrong table name")
        print("     - Need to fix the migration to use correct table")
    elif not tbl_jop_exists and not tbl_job_exists:
        print("  ❌ Neither Tbl_Jop nor Tbl_Job exists")
        print("     - Need to create the table first")
        print("     - Or mark models as unmanaged")
    elif tbl_job_exists and tbl_jop_exists:
        print("  ⚠️  Both tables exist - potential confusion")
        print("     - Need to clarify which table to use")
    
    print("\n  Model Conflict Resolution:")
    print("     - Remove duplicate HrJob model")
    print("     - Keep only the Legacy Job model")
    print("     - Update imports to use the correct model")
    
    print("\n  Migration Fix Options:")
    print("     1. Create a custom migration to handle the conflict")
    print("     2. Mark problematic models as unmanaged")
    print("     3. Fake the migration and fix manually")

if __name__ == "__main__":
    main()
