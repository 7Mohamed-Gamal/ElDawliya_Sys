# Migration Troubleshooting Guide

## EmployeeLeave Table Migration Issue

If you encounter an error related to the `sqlite_master` table when using SQL Server, follow these steps:

### For SQL Server Users:

1. Run the custom management command to fix the migration:

```
python manage.py fix_employeeleave_migration
```

2. Then run migrations again:

```
python manage.py migrate
```

### Complete Step-by-Step Fix for SQL Server

If you encounter migration issues with SQL Server, follow these steps in order:

1. Fix the EmployeeLeave table migration:

```
python manage.py fix_employeeleave_migration
```

2. Merge conflicting migrations if needed:

```
python manage.py makemigrations --merge
```

3. Fake apply problematic migrations one by one:

```
python manage.py migrate Hr 0023_fix_employeeleave_table_sqlite --fake
python manage.py migrate Hr 0025_merge_20250505_1945 --fake
python manage.py migrate Hr 0026_alter_employee_options_remove_employee_id_and_more --fake
```

4. If you encounter issues with inventory migrations:

```
python manage.py migrate inventory 0010_tblinvoiceitems_product_tblproducts_cat_and_more --fake
```

5. Complete the migration process:

```
python manage.py migrate
```

### Manual Fix (if the command doesn't work):

1. Delete the problematic migration records from the database:

```sql
DELETE FROM django_migrations
WHERE app = 'Hr' AND name IN (
    '0023_fix_employeeleave_table',
    '0010_create_leavetype_table',
    '0011_create_employeeleave_table'
);
```

2. Update the migration record to use the SQL Server compatible version:

```sql
UPDATE django_migrations
SET name = '0023_fix_employeeleave_table_mssql'
WHERE app = 'Hr' AND name = '0023_fix_employeeleave_table';
```

3. Run migrations again:

```
python manage.py migrate
```

## Common Migration Errors and Solutions

### Error: "Invalid object name 'sqlite_master'"

This error occurs when a migration is using SQLite-specific SQL with SQL Server. Solution:

1. Fake the migration:
```
python manage.py migrate Hr 0023_fix_employeeleave_table_sqlite --fake
```

2. Or replace the migration with a SQL Server compatible version.

### Error: "ALTER TABLE DROP COLUMN failed because 'name' is the only data column"

This error occurs when trying to remove the only column in a table. Solution:

1. Fake the migration:
```
python manage.py migrate Hr 0026_alter_employee_options_remove_employee_id_and_more --fake
```

### Error: "Column names in each table must be unique"

This error occurs when a migration tries to add a column that already exists. Solution:

1. Fake the migration:
```
python manage.py migrate inventory 0010_tblinvoiceitems_product_tblproducts_cat_and_more --fake
```

## General Migration Issues

If you encounter other migration issues, you can try:

1. Fixing the migration history:

```
python manage.py fix_migration_history
```

2. If specific tables already exist but Django is trying to create them again, you can use the `--fake` option:

```
python manage.py migrate Hr --fake
```

This tells Django to mark the migrations as applied without actually running them.

## Database Compatibility

This project supports both SQL Server and SQLite. Some migrations have database-specific versions:

- `0023_fix_employeeleave_table_mssql.py` - For SQL Server
- `0023_fix_employeeleave_table_sqlite.py` - For SQLite

Make sure you're using the correct version for your database.

## Creating Database-Agnostic Migrations

When creating custom migrations, use the utility functions in `Hr.utils.db_utils`:

```python
from django.db import migrations
from Hr.utils.db_utils import get_table_exists_sql, get_column_exists_sql

class Migration(migrations.Migration):
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
    ]
```

Alternatively, you can check the database type directly:

```python
from django.db import migrations, connection

class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL(
            # SQL Server version
            """IF OBJECT_ID('table_name', 'U') IS NOT NULL SELECT 1;"""
            if connection.vendor == 'microsoft' else
            # SQLite version
            """SELECT 1 FROM sqlite_master WHERE type='table' AND name='table_name';"""
        ),
    ]
```

See the example in `Hr/migrations/examples/db_agnostic_migration_example.py` for more details.
