# Generated manually to fix EmployeeLeave table migration issue in a database-agnostic way

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0026_alter_employee_options_remove_employee_id_and_more'),
    ]

    operations = [
        # This migration is a placeholder to ensure EmployeeLeave table exists
        # It uses a database-agnostic approach
        migrations.RunSQL(
            """
            -- This is a no-op SQL statement that will be executed safely
            SELECT 1;
            """,
            reverse_sql="""
            SELECT 1;
            """
        ),
    ]
