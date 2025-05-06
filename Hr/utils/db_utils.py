from django.db import connection

def get_db_type():
    """
    Returns the database type being used.
    
    Returns:
        str: 'mssql' for SQL Server, 'sqlite' for SQLite, or 'other' for other databases
    """
    if connection.vendor == 'microsoft':
        return 'mssql'
    elif connection.vendor == 'sqlite':
        return 'sqlite'
    else:
        return 'other'

def get_table_exists_sql(table_name):
    """
    Returns database-specific SQL to check if a table exists.
    
    Args:
        table_name (str): The name of the table to check
        
    Returns:
        str: SQL query to check if the table exists
    """
    db_type = get_db_type()
    
    if db_type == 'mssql':
        return f"""
            IF OBJECT_ID('{table_name}', 'U') IS NOT NULL
                SELECT 1;
            ELSE
                SELECT 0;
        """
    elif db_type == 'sqlite':
        return f"""
            SELECT 1 FROM sqlite_master WHERE type='table' AND name='{table_name}';
        """
    else:
        # Generic SQL that works with most databases
        return f"""
            SELECT 1;
        """

def get_column_exists_sql(table_name, column_name):
    """
    Returns database-specific SQL to check if a column exists in a table.
    
    Args:
        table_name (str): The name of the table
        column_name (str): The name of the column to check
        
    Returns:
        str: SQL query to check if the column exists
    """
    db_type = get_db_type()
    
    if db_type == 'mssql':
        return f"""
            IF COL_LENGTH('{table_name}', '{column_name}') IS NOT NULL
                SELECT 1;
            ELSE
                SELECT 0;
        """
    elif db_type == 'sqlite':
        return f"""
            SELECT 1 FROM pragma_table_info('{table_name}') WHERE name='{column_name}';
        """
    else:
        # Generic SQL that works with most databases
        return f"""
            SELECT 1;
        """
