#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.db import connection

def check_tables_to_delete():
    """Check if tables that migration wants to delete actually exist"""
    with connection.cursor() as cursor:
        # Check tables that migration wants to delete
        tables_to_check = [
            'hrms_salary_component',
            'Hr_SalaryComponent',
            'Hr_SalaryItem',
            'hrms_employee_salary_structure'
        ]

        for table_name in tables_to_check:
            cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = %s
            """, [table_name])
            table_exists = cursor.fetchone()
            print(f'Table {table_name} exists: {table_exists is not None}')

            if table_exists:
                # Check columns
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """, [table_name])
                columns = cursor.fetchall()
                print(f'  Columns in {table_name}:')
                for col in columns:
                    print(f'    - {col[0]} ({col[1]}, nullable: {col[2]}, default: {col[3]})')

                # Check constraints
                cursor.execute("""
                    SELECT
                        tc.CONSTRAINT_NAME,
                        tc.CONSTRAINT_TYPE,
                        STRING_AGG(ccu.COLUMN_NAME, ', ') as columns
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                    LEFT JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu
                        ON tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
                    WHERE tc.TABLE_NAME = %s
                    GROUP BY tc.CONSTRAINT_NAME, tc.CONSTRAINT_TYPE
                """, [table_name])
                constraints = cursor.fetchall()
                print(f'  Constraints in {table_name}:')
                for constraint in constraints:
                    print(f'    - {constraint[0]} ({constraint[1]}): {constraint[2]}')
                print()

        
        # Also check if the table was deleted/renamed
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME LIKE '%emergency%' OR TABLE_NAME LIKE '%contact%'
        """)
        similar_tables = cursor.fetchall()
        print(f'\nTables with "emergency" or "contact" in name:')
        for table in similar_tables:
            print(f'  - {table[0]}')

        # Check all Hr app tables
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME LIKE 'hrms_%' OR TABLE_NAME LIKE 'Hr_%'
            ORDER BY TABLE_NAME
        """)
        hr_tables = cursor.fetchall()
        print(f'\nAll HR-related tables:')
        for table in hr_tables:
            print(f'  - {table[0]}')

if __name__ == '__main__':
    check_tables_to_delete()
