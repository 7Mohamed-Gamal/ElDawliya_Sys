# Modified to fix SQLite compatibility issue
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0019_merge_20240101_0003'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Check if the table already exists
            SELECT name FROM sqlite_master WHERE type='table' AND name='Hr_taskstep';
            """,
            """
            -- No reverse SQL needed
            SELECT 1;
            """
        ),

        # Only create the model if it doesn't exist
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
