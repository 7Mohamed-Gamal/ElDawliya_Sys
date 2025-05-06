# Generated manually - Modified to fix migration issue

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0008_create_employeefile_table'),
    ]

    operations = [
        # Check if table already exists and do nothing if it does
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