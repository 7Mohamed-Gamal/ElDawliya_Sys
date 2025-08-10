# Generated migration for Employee Extended Models

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import uuid
from decimal import Decimal


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        # Ensure EmployeeEnhanced (hrms_employee_enhanced) exists before this migration
        ('Hr', '0030_create_enhanced_attendance_models'),
        ('Hr', '0028_create_enhanced_employee_models'),
        ('accounts', '0001_initial'),
    ]

    operations = [

        # Create EmployeeFileEnhanced


        # Create EmployeeFileAccessLog


        # Create EmployeeEmergencyContactEnhanced


        # Add indexes (SQL Server compatible syntax with proper table names and schema)
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_education_employee' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                CREATE INDEX [idx_employee_education_employee] ON [dbo].[Hr_employeeeducationenhanced]([employee_id]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_education_employee' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                DROP INDEX [idx_employee_education_employee] ON [dbo].[Hr_employeeeducationenhanced];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_education_degree' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                CREATE INDEX [idx_employee_education_degree] ON [dbo].[Hr_employeeeducationenhanced]([degree_type]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_education_degree' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                DROP INDEX [idx_employee_education_degree] ON [dbo].[Hr_employeeeducationenhanced];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_education_graduation' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                CREATE INDEX [idx_employee_education_graduation] ON [dbo].[Hr_employeeeducationenhanced]([graduation_year]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_education_graduation' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                DROP INDEX [idx_employee_education_graduation] ON [dbo].[Hr_employeeeducationenhanced];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_insurance_employee' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeinsuranceenhanced]'))
            BEGIN
                CREATE INDEX [idx_employee_insurance_employee] ON [dbo].[Hr_employeeinsuranceenhanced]([employee_id]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_insurance_employee' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeinsuranceenhanced]'))
            BEGIN
                DROP INDEX [idx_employee_insurance_employee] ON [dbo].[Hr_employeeinsuranceenhanced];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_insurance_type' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeinsuranceenhanced]'))
            BEGIN
                CREATE INDEX [idx_employee_insurance_type] ON [dbo].[Hr_employeeinsuranceenhanced]([insurance_type]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_insurance_type' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeeinsuranceenhanced]'))
            BEGIN
                DROP INDEX [idx_employee_insurance_type] ON [dbo].[Hr_employeeinsuranceenhanced];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_vehicle_employee' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeevehicleenhanced]'))
            BEGIN
                CREATE INDEX [idx_employee_vehicle_employee] ON [dbo].[Hr_employeevehicleenhanced]([employee_id]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_vehicle_employee' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeevehicleenhanced]'))
            BEGIN
                DROP INDEX [idx_employee_vehicle_employee] ON [dbo].[Hr_employeevehicleenhanced];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_vehicle_plate' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeevehicleenhanced]'))
            BEGIN
                CREATE INDEX [idx_employee_vehicle_plate] ON [dbo].[Hr_employeevehicleenhanced]([license_plate]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_vehicle_plate' AND object_id = OBJECT_ID(N'[dbo].[Hr_employeevehicleenhanced]'))
            BEGIN
                DROP INDEX [idx_employee_vehicle_plate] ON [dbo].[Hr_employeevehicleenhanced];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_file_employee' AND object_id = OBJECT_ID(N'[dbo].[hrms_employee_file_enhanced]'))
            BEGIN
                CREATE INDEX [idx_employee_file_employee] ON [dbo].[hrms_employee_file_enhanced]([employee_id]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_file_employee' AND object_id = OBJECT_ID(N'[dbo].[hrms_employee_file_enhanced]'))
            BEGIN
                DROP INDEX [idx_employee_file_employee] ON [dbo].[hrms_employee_file_enhanced];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_file_status' AND object_id = OBJECT_ID(N'[dbo].[hrms_employee_file_enhanced]'))
            BEGIN
                CREATE INDEX [idx_employee_file_status] ON [dbo].[hrms_employee_file_enhanced]([status]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_file_status' AND object_id = OBJECT_ID(N'[dbo].[hrms_employee_file_enhanced]'))
            BEGIN
                DROP INDEX [idx_employee_file_status] ON [dbo].[hrms_employee_file_enhanced];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_emergency_employee' AND object_id = OBJECT_ID(N'[dbo].[hrms_employee_emergency_contact]'))
            BEGIN
                CREATE INDEX [idx_employee_emergency_employee] ON [dbo].[hrms_employee_emergency_contact]([employee_id]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_emergency_employee' AND object_id = OBJECT_ID(N'[dbo].[hrms_employee_emergency_contact]'))
            BEGIN
                DROP INDEX [idx_employee_emergency_employee] ON [dbo].[hrms_employee_emergency_contact];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_emergency_priority' AND object_id = OBJECT_ID(N'[dbo].[hrms_employee_emergency_contact]'))
            BEGIN
                CREATE INDEX [idx_employee_emergency_priority] ON [dbo].[hrms_employee_emergency_contact]([priority]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_employee_emergency_priority' AND object_id = OBJECT_ID(N'[dbo].[hrms_employee_emergency_contact]'))
            BEGIN
                DROP INDEX [idx_employee_emergency_priority] ON [dbo].[hrms_employee_emergency_contact];
            END
            """
        ),

        # Add constraints (SQL Server compatible with IF EXISTS guards)
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = N'chk_start_before_graduation' AND parent_object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                ALTER TABLE [dbo].[Hr_employeeeducationenhanced] ADD CONSTRAINT [chk_start_before_graduation] CHECK ([start_year] <= [graduation_year]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = N'chk_start_before_graduation' AND parent_object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                ALTER TABLE [dbo].[Hr_employeeeducationenhanced] DROP CONSTRAINT [chk_start_before_graduation];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = N'chk_rank_within_class' AND parent_object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                ALTER TABLE [dbo].[Hr_employeeeducationenhanced] ADD CONSTRAINT [chk_rank_within_class] CHECK ([class_rank] <= [class_size]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = N'chk_rank_within_class' AND parent_object_id = OBJECT_ID(N'[dbo].[Hr_employeeeducationenhanced]'))
            BEGIN
                ALTER TABLE [dbo].[Hr_employeeeducationenhanced] DROP CONSTRAINT [chk_rank_within_class];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = N'chk_end_after_start_insurance' AND parent_object_id = OBJECT_ID(N'[dbo].[Hr_employeeinsuranceenhanced]'))
            BEGIN
                ALTER TABLE [dbo].[Hr_employeeinsuranceenhanced] ADD CONSTRAINT [chk_end_after_start_insurance] CHECK ([end_date] >= [start_date]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = N'chk_end_after_start_insurance' AND parent_object_id = OBJECT_ID(N'[dbo].[Hr_employeeinsuranceenhanced]'))
            BEGIN
                ALTER TABLE [dbo].[Hr_employeeinsuranceenhanced] DROP CONSTRAINT [chk_end_after_start_insurance];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = N'chk_return_after_assignment' AND parent_object_id = OBJECT_ID(N'[dbo].[Hr_employeevehicleenhanced]'))
            BEGIN
                ALTER TABLE [dbo].[Hr_employeevehicleenhanced] ADD CONSTRAINT [chk_return_after_assignment] CHECK ([return_date] >= [assigned_date]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = N'chk_return_after_assignment' AND parent_object_id = OBJECT_ID(N'[dbo].[Hr_employeevehicleenhanced]'))
            BEGIN
                ALTER TABLE [dbo].[Hr_employeevehicleenhanced] DROP CONSTRAINT [chk_return_after_assignment];
            END
            """
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = N'unique_employee_priority' AND parent_object_id = OBJECT_ID(N'[dbo].[hrms_employee_emergency_contact]'))
            BEGIN
                ALTER TABLE [dbo].[hrms_employee_emergency_contact] ADD CONSTRAINT [unique_employee_priority] UNIQUE ([employee_id], [priority]);
            END
            """,
            reverse_sql="""
            IF EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = N'unique_employee_priority' AND parent_object_id = OBJECT_ID(N'[dbo].[hrms_employee_emergency_contact]'))
            BEGIN
                ALTER TABLE [dbo].[hrms_employee_emergency_contact] DROP CONSTRAINT [unique_employee_priority];
            END
            """
        ),
    ]