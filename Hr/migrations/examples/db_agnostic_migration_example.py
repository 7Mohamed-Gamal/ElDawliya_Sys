# Example of a database-agnostic migration

from django.db import migrations
from Hr.utils.db_utils import get_table_exists_sql, get_column_exists_sql

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0028_merge_20250505_2023'),
    ]

    operations = [
        # Check if a table exists in a database-agnostic way
        migrations.RunSQL(
            get_table_exists_sql('Hr_EmployeeLeave'),
            reverse_sql="SELECT 1;"
        ),

        # Check if a column exists in a database-agnostic way
        migrations.RunSQL(
            get_column_exists_sql('Hr_EmployeeLeave', 'status'),
            reverse_sql="SELECT 1;"
        ),

        # Create a table only if it doesn't exist
        migrations.RunSQL(
            """
            -- This is a no-op SQL statement that will be executed safely
            -- In a real migration, you would use conditional logic based on the database type
            SELECT 1;
            """,
            reverse_sql="""
            SELECT 1;
            """
        ),
    ]
