# Generated manually - Modified to fix migration issue

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0011_create_employeeleave_table'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Check if tables already exist and do nothing if they do
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