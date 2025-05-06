# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0010_create_employee_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Add 'code' column to Hr_LeaveType if it doesn't exist
            ALTER TABLE Hr_LeaveType ADD COLUMN code TEXT DEFAULT NULL;
            
            -- Create a temporary table with the unique constraint
            CREATE TABLE IF NOT EXISTS Hr_LeaveType_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                affects_salary INTEGER NOT NULL DEFAULT 0,
                is_paid INTEGER NOT NULL DEFAULT 1,
                max_days_per_year INTEGER NOT NULL DEFAULT 0,
                description TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                code TEXT UNIQUE
            );
            
            -- Copy data from the original table to the temporary table
            INSERT OR IGNORE INTO Hr_LeaveType_temp 
            SELECT id, name, affects_salary, is_paid, max_days_per_year, description, is_active, created_at, updated_at, code 
            FROM Hr_LeaveType;
            
            -- Drop the original table
            DROP TABLE IF EXISTS Hr_LeaveType;
            
            -- Rename the temporary table to the original name
            ALTER TABLE Hr_LeaveType_temp RENAME TO Hr_LeaveType;
            """,
            """
            -- No reverse SQL needed
            """
        ),
    ]