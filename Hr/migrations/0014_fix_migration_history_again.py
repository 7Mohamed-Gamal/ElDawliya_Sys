# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0013_fix_migration_history'),
    ]

    operations = [
        # This migration is a placeholder to fix the migration history
        # It doesn't make any changes to the database
        migrations.RunSQL(
            """
            UPDATE django_migrations
            SET app = 'Hr', name = '0009_create_employee_table'
            WHERE app = 'Hr' AND name = '0009_alter_hrtask_table';
            """,
            """
            UPDATE django_migrations
            SET app = 'Hr', name = '0009_alter_hrtask_table'
            WHERE app = 'Hr' AND name = '0009_create_employee_table';
            """
        ),
    ]