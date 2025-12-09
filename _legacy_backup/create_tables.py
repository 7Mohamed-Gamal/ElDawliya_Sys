#!/usr/bin/env python
"""
Create tables for banks and employees apps
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.db import connection
from django.core.management.color import no_style
from django.db import models

def create_tables():
    """Create tables for banks and employees apps"""
    
    # Import models
    from banks.models import Bank
    from apps.hr.employees.models import Employee, EmployeeBankAccount, EmployeeDocument
    
    style = no_style()
    
    # Get SQL statements for creating tables
    with connection.schema_editor() as schema_editor:
        try:
            # Create Banks table
            print("Creating Banks table...")
            schema_editor.create_model(Bank)
            print("✅ Banks table created")
            
            # Create Employees table
            print("Creating Employees table...")
            schema_editor.create_model(Employee)
            print("✅ Employees table created")
            
            # Create EmployeeBankAccounts table
            print("Creating EmployeeBankAccounts table...")
            schema_editor.create_model(EmployeeBankAccount)
            print("✅ EmployeeBankAccounts table created")
            
            # Create EmployeeDocuments table
            print("Creating EmployeeDocuments table...")
            schema_editor.create_model(EmployeeDocument)
            print("✅ EmployeeDocuments table created")
            
            print("\n✅ All tables created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_tables()