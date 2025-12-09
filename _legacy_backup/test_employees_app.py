#!/usr/bin/env python
"""
Test script for employees app functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from companies.models import Company
from org.models import Branch, Department, Job
from banks.models import Bank
from apps.hr.employees.models import Employee, EmployeeBankAccount, EmployeeDocument

def test_employees_app():
    """Test employees app functionality"""
    print("Testing employees app...")
    
    try:
        # Test 1: Create test data
        print("1. Creating test data...")
        
        # Create a company
        company = Company.objects.create(
            name="Test Company",
            is_active=True
        )
        print(f"   Created company: {company}")
        
        # Create a branch
        branch = Branch.objects.create(
            branch_name="Main Branch",
            company=company,
            is_active=True
        )
        print(f"   Created branch: {branch}")
        
        # Create a department
        department = Department.objects.create(
            dept_name="IT Department",
            branch=branch,
            is_active=True
        )
        print(f"   Created department: {department}")
        
        # Create a job
        job = Job.objects.create(
            job_title="Software Developer",
            basic_salary=5000.00,
            is_active=True
        )
        print(f"   Created job: {job}")
        
        # Create a bank
        bank = Bank.objects.create(
            bank_name="Test Bank",
            swift_code="TESTBANK"
        )
        print(f"   Created bank: {bank}")
        
        # Test 2: Create an employee
        print("2. Creating employee...")
        employee = Employee.objects.create(
            emp_code="EMP001",
            first_name="Ahmed",
            last_name="Ali",
            gender="M",
            job=job,
            dept=department,
            branch=branch,
            emp_status="Active"
        )
        print(f"   Created employee: {employee}")
        print(f"   Employee full name: {employee.full_name}")
        
        # Test 3: Create employee bank account
        print("3. Creating employee bank account...")
        bank_account = EmployeeBankAccount.objects.create(
            emp=employee,
            bank=bank,
            account_no="123456789",
            iban="SA1234567890123456789",
            is_primary=True
        )
        print(f"   Created bank account: {bank_account}")
        
        # Test 4: Create employee document
        print("4. Creating employee document...")
        document = EmployeeDocument.objects.create(
            emp=employee,
            doc_type="ID",
            doc_name="National ID",
            is_active=True
        )
        print(f"   Created document: {document}")
        
        # Test 5: Test relationships
        print("5. Testing relationships...")
        print(f"   Employee department: {employee.dept}")
        print(f"   Employee branch: {employee.branch}")
        print(f"   Employee job: {employee.job}")
        print(f"   Employee bank accounts: {employee.bank_accounts.count()}")
        print(f"   Employee documents: {employee.documents.count()}")
        
        # Test 6: Test employee properties
        print("6. Testing employee properties...")
        print(f"   Is active: {employee.is_active}")
        print(f"   Age: {employee.age}")
        print(f"   Years of service: {employee.years_of_service}")
        
        # Test 7: Clean up
        print("7. Cleaning up test data...")
        employee.delete()
        bank.delete()
        job.delete()
        department.delete()
        branch.delete()
        company.delete()
        print("   Test data cleaned up")
        
        print("\n✅ All tests passed! Employees app is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_employees_app()
    sys.exit(0 if success else 1)