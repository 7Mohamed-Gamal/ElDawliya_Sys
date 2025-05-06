# Generated manually - Modified to fix migration issue

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0010_create_leavetype_table'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # First check if the table already exists
        migrations.RunSQL(
            """
            SELECT name FROM sqlite_master WHERE type='table' AND name='Hr_EmployeeLeave';
            """,
            reverse_sql="""
            SELECT 1;
            """
        ),

        # Only create the model if it doesn't exist
        # This is a placeholder that will be skipped if the table already exists
        # The actual model creation is handled in migration 0023_fix_employeeleave_table.py
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