# Generated manually to fix EmployeeLeave table migration issue for SQLite

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0022_alter_employee_emp_image'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Check if the table exists and do nothing if it does
            SELECT 1 FROM sqlite_master WHERE type='table' AND name='Hr_EmployeeLeave';
            """,
            """
            -- No reverse SQL needed
            """
        ),
    ]
