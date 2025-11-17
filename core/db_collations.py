"""
Custom database collations for SQL Server.
This module registers custom collations for use with SQL Server.
"""
from django.db import connection
from django.db.backends.signals import connection_created
from django.dispatch import receiver


@receiver(connection_created)
def setup_collations(sender, connection, **kwargs):
    """
    Set up custom collations when a database connection is created.
    This is particularly useful for SQL Server to ensure proper Arabic text handling.
    """
    # Only apply to SQL Server connections
    if connection.vendor == 'microsoft':
        # SQL Server typically uses Arabic_CI_AS or Arabic_100_CI_AS for Arabic text
        # This is configured at the database level, so no additional setup is needed here
        pass


def get_arabic_collation():
    """
    Get the appropriate Arabic collation for the current database.
    
    Returns:
        str: The collation string to use for Arabic text fields.
    """
    if connection.vendor == 'microsoft':
        # Common Arabic collations in SQL Server:
        # - Arabic_CI_AS: Case-insensitive, accent-sensitive
        # - Arabic_100_CI_AS: SQL Server 2008+ version
        return 'Arabic_100_CI_AS'
    return None


def apply_collation_to_field(field_name, collation=None):
    """
    Apply a specific collation to a database field.
    
    Args:
        field_name (str): The name of the field to apply collation to.
        collation (str, optional): The collation to apply. Defaults to Arabic collation.
    
    Returns:
        str: SQL fragment to apply the collation.
    """
    if collation is None:
        collation = get_arabic_collation()
    
    if collation:
        return f"{field_name} COLLATE {collation}"
    return field_name

