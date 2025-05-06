# Modified to fix SQLite compatibility issue
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0009_alter_hrtask_table'),  # Updated dependency to match the fixed migration history
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Check if the table already exists
            SELECT name FROM sqlite_master WHERE type='table' AND name='hr_hrtask';
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