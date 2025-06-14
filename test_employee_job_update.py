#!/usr/bin/env python
"""
Test script to verify that employee job title updates work correctly.
This script tests the bug fix for employee job title/position updates.
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_Sys.settings')
django.setup()

from Hr.models.employee_model import Employee
from Hr.models.job_models import Job
from Hr.forms.employee_forms import EmployeeForm


def test_employee_job_update():
    """Test that employee job title updates work correctly"""
    print("🧪 Testing Employee Job Title Update Functionality")
    print("=" * 60)
    
    try:
        # Get an existing employee
        employee = Employee.objects.first()
        if not employee:
            print("❌ No employees found in database. Please add an employee first.")
            return False
            
        print(f"📋 Testing with employee: {employee.emp_full_name} (ID: {employee.emp_id})")
        print(f"   Current job: {employee.jop_name} (Code: {employee.jop_code})")
        
        # Get available jobs
        jobs = Job.objects.all()
        if jobs.count() < 2:
            print("❌ Need at least 2 jobs in database to test job updates.")
            return False
            
        # Find a different job to update to
        current_job_name = employee.jop_name
        new_job = None
        for job in jobs:
            if job.jop_name != current_job_name:
                new_job = job
                break
                
        if not new_job:
            print("❌ All jobs are the same. Cannot test job update.")
            return False
            
        print(f"🔄 Updating job to: {new_job.jop_name} (Code: {new_job.jop_code})")
        
        # Test form with job update
        form_data = {
            'emp_id': employee.emp_id,
            'emp_first_name': employee.emp_first_name,
            'emp_second_name': employee.emp_second_name,
            'emp_full_name': employee.emp_full_name,
            'jop_name': new_job.pk,  # Use the Job instance primary key
            'working_condition': employee.working_condition or 'سارى',
        }
        
        # Create form instance
        form = EmployeeForm(data=form_data, instance=employee)
        
        # Check if form is valid
        if not form.is_valid():
            print("❌ Form validation failed:")
            for field, errors in form.errors.items():
                print(f"   {field}: {errors}")
            return False
            
        print("✅ Form validation passed")
        
        # Save the form
        updated_employee = form.save()
        
        # Refresh from database
        updated_employee.refresh_from_db()
        
        # Verify the job was updated correctly
        if updated_employee.jop_name == new_job.jop_name and updated_employee.jop_code == new_job.jop_code:
            print(f"✅ Job update successful!")
            print(f"   New job name: {updated_employee.jop_name}")
            print(f"   New job code: {updated_employee.jop_code}")
            
            # Restore original job
            restore_form_data = form_data.copy()
            original_job = Job.objects.filter(jop_name=current_job_name).first()
            if original_job:
                restore_form_data['jop_name'] = original_job.pk
                restore_form = EmployeeForm(data=restore_form_data, instance=updated_employee)
                if restore_form.is_valid():
                    restore_form.save()
                    print(f"🔄 Restored original job: {current_job_name}")
                    
            return True
        else:
            print(f"❌ Job update failed!")
            print(f"   Expected: {new_job.jop_name} (Code: {new_job.jop_code})")
            print(f"   Got: {updated_employee.jop_name} (Code: {updated_employee.jop_code})")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_form_initialization():
    """Test that the form initializes correctly with existing employee data"""
    print("\n🧪 Testing Form Initialization")
    print("=" * 40)
    
    try:
        employee = Employee.objects.first()
        if not employee:
            print("❌ No employees found")
            return False
            
        form = EmployeeForm(instance=employee)
        
        # Check if job field is properly initialized
        job_field = form.fields['jop_name']
        initial_job = form.initial.get('jop_name') or job_field.initial
        
        print(f"📋 Employee: {employee.emp_full_name}")
        print(f"   Current job in DB: {employee.jop_name}")
        print(f"   Form initial job: {initial_job}")
        
        if employee.jop_name and initial_job:
            if hasattr(initial_job, 'jop_name'):
                if initial_job.jop_name == employee.jop_name:
                    print("✅ Form initialization correct")
                    return True
                else:
                    print(f"❌ Form initialization mismatch: {initial_job.jop_name} != {employee.jop_name}")
                    return False
            else:
                print("⚠️  Initial job is not a Job instance")
                return False
        else:
            print("✅ Form initialization correct (no job set)")
            return True
            
    except Exception as e:
        print(f"❌ Form initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Employee Job Update Tests")
    print("=" * 60)
    
    # Test 1: Form initialization
    init_success = test_form_initialization()
    
    # Test 2: Job update functionality
    update_success = test_employee_job_update()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Form Initialization: {'✅ PASS' if init_success else '❌ FAIL'}")
    print(f"   Job Update: {'✅ PASS' if update_success else '❌ FAIL'}")
    
    if init_success and update_success:
        print("\n🎉 All tests passed! Employee job title updates are working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the implementation.")
        sys.exit(1)
