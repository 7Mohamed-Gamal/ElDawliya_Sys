# Generated manually to fix migration dependencies

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0023_fix_employeeleave_table_mssql'),
    ]

    operations = [
        # This migration is a placeholder to fix the migration history
        # It doesn't make any changes to the database
        migrations.RunSQL(
            """
            -- Update the dependencies in the django_migrations table
            UPDATE django_migrations
            SET applied = (SELECT applied FROM django_migrations WHERE app = 'Hr' AND name = '0010_create_employee_table')
            WHERE app = 'Hr' AND name = '0009_alter_hrtask_table';
            """,
            """
            -- No reverse SQL needed
            SELECT 1;
            """
        ),
    ]
