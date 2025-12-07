#!/usr/bin/env python
"""
Test script for all restored apps functionality
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
from employees.models import Employee, EmployeeBankAccount, EmployeeDocument
from attendance.models import AttendanceRule, EmployeeAttendanceProfile, AttendanceRecord

def test_restored_apps():
    """Test all restored apps functionality"""
    print("Testing all restored apps integration...")
    
    try:
        # Test 1: Create test data
        print("1. Creating test data...")
        
        # Create a company
        company = Company.objects.create(
            name="ElDawliya Test Company",
            is_active=True
        )
        print(f"   ✅ Created company: {company}")
        
        # Create a branch
        branch = Branch.objects.create(
            branch_name="Main Branch",
            company=company,
            is_active=True
        )
        print(f"   ✅ Created branch: {branch}")
        
        # Create a department
        department = Department.objects.create(
            dept_name="IT Department",
            branch=branch,
            is_active=True
        )
        print(f"   ✅ Created department: {department}")
        
        # Create a job
        job = Job.objects.create(
            job_title="Software Developer",
            basic_salary=5000.00,
            is_active=True
        )
        print(f"   ✅ Created job: {job}")
        
        # Create a bank
        bank = Bank.objects.create(
            bank_name="Test Bank",
            swift_code="TESTBANK"
        )
        print(f"   ✅ Created bank: {bank}")
        
        # Create an attendance rule
        attendance_rule = AttendanceRule.objects.create(
            name="Standard Work Rule",
            description="Standard 8-hour work day",
            late_grace_period=15,
            early_leave_grace_period=15
        )
        print(f"   ✅ Created attendance rule: {attendance_rule}")
        
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
        print(f"   ✅ Created employee: {employee}")
        
        # Test 3: Create employee bank account
        print("3. Creating employee bank account...")
        bank_account = EmployeeBankAccount.objects.create(
            emp=employee,
            bank=bank,
            account_no="123456789",
            iban="SA1234567890123456789",
            is_primary=True
        )
        print(f"   ✅ Created bank account: {bank_account}")
        
        # Test 4: Create employee attendance profile
        print("4. Creating employee attendance profile...")
        attendance_profile = EmployeeAttendanceProfile.objects.create(
            employee=employee,
            attendance_rule=attendance_rule,
            work_hours_per_day=8.0
        )
        print(f"   ✅ Created attendance profile: {attendance_profile}")
        
        # Test 5: Create attendance record
        print("5. Creating attendance record...")
        from datetime import date, datetime, time
        attendance_record = AttendanceRecord.objects.create(
            employee=employee,
            date=date.today(),
            check_in=datetime.combine(date.today(), time(9, 0)),
            check_out=datetime.combine(date.today(), time(17, 0)),
            record_type="present"
        )
        print(f"   ✅ Created attendance record: {attendance_record}")
        
        # Test 6: Test relationships and integration
        print("6. Testing relationships and integration...")
        print(f"   Employee company: {employee.branch.company.name}")
        print(f"   Employee department: {employee.dept.dept_name}")
        print(f"   Employee job: {employee.job.job_title}")
        print(f"   Employee bank: {employee.bank_accounts.first().bank.bank_name}")
        print(f"   Employee attendance rule: {employee.attendance_profile.attendance_rule.name}")
        print(f"   Employee attendance records: {employee.new_attendance_records.count()}")
        
        # Test 7: Test employee properties and methods
        print("7. Testing employee properties...")
        print(f"   Full name: {employee.full_name}")
        print(f"   Is active: {employee.is_active}")
        print(f"   Work hours: {attendance_record.work_hours}")
        
        # Test 8: Clean up
        print("8. Cleaning up test data...")
        attendance_record.delete()
        attendance_profile.delete()
        bank_account.delete()
        employee.delete()
        attendance_rule.delete()
        bank.delete()
        job.delete()
        department.delete()
        branch.delete()
        company.delete()
        print("   ✅ Test data cleaned up")
        
        print("\n🎉 All tests passed! All restored apps are working correctly together.")
        print("\n📋 Summary of restored apps:")
        print("   ✅ companies - Company management")
        print("   ✅ org - Organizational structure (branches, departments, jobs)")
        print("   ✅ banks - Bank management")
        print("   ✅ employees - Employee management")
        print("   ✅ attendance - Attendance and time tracking")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_restored_apps()
    sys.exit(0 if success else 1)