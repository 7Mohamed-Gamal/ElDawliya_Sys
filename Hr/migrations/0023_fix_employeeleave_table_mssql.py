# Generated manually to fix EmployeeLeave table migration issue for SQL Server

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0022_alter_employee_emp_image'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Check if the table exists using SQL Server syntax
            IF OBJECT_ID('Hr_EmployeeLeave', 'U') IS NOT NULL
                SELECT 1;
            ELSE
                SELECT 0;
            """,
            """
            -- No reverse SQL needed
            """
        ),
    ]
