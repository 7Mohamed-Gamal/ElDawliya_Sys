import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

# Import Django's database connection
from django.db import connections

def execute_sql_from_file(filename):
    """Execute SQL script from a file using Django's database connection."""
    # Read SQL file
    with open(filename, 'r') as f:
        sql = f.read()
    
    # Execute SQL using the primary database connection
    with connections['primary'].cursor() as cursor:
        try:
            cursor.execute(sql)
            print(f"SQL script {filename} executed successfully.")
        except Exception as e:
            print(f"Error executing SQL script: {str(e)}")

if __name__ == "__main__":
    # execute_sql_from_file('create_employeetask_table.sql')
    execute_sql_from_file('update_employeetask_table.sql')
