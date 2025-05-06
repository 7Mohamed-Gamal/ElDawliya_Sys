from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix EmployeeLeave table migration issue for SQL Server'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if we're using SQL Server
            is_mssql = connection.vendor == 'microsoft'
            
            if is_mssql:
                # Check if the table exists
                cursor.execute("""
                    IF OBJECT_ID('Hr_EmployeeLeave', 'U') IS NULL
                    BEGIN
                        -- Create the table if it doesn't exist
                        CREATE TABLE Hr_EmployeeLeave (
                            id INT IDENTITY(1,1) PRIMARY KEY,
                            start_date DATE NOT NULL,
                            end_date DATE NOT NULL,
                            days_count INT NOT NULL,
                            reason NVARCHAR(MAX) NOT NULL,
                            status NVARCHAR(20) NOT NULL DEFAULT 'pending',
                            approval_date DATETIME NULL,
                            rejection_reason NVARCHAR(MAX) NULL,
                            notes NVARCHAR(MAX) NULL,
                            created_at DATETIME NOT NULL DEFAULT GETDATE(),
                            updated_at DATETIME NOT NULL DEFAULT GETDATE(),
                            employee_id INT NOT NULL,
                            leave_type_id INT NOT NULL,
                            approved_by_id INT NULL
                        );
                    END
                """)
                
                # Fix the migration record
                cursor.execute("""
                    UPDATE django_migrations
                    SET name = '0023_fix_employeeleave_table_mssql'
                    WHERE app = 'Hr' AND name = '0023_fix_employeeleave_table';
                """)
                
                self.stdout.write(self.style.SUCCESS('Successfully fixed EmployeeLeave table for SQL Server'))
            else:
                self.stdout.write(self.style.WARNING('This command is only needed for SQL Server databases'))
