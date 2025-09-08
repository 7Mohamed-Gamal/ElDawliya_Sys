#!/usr/bin/env python
"""
Test script for comprehensive employee edit functionality
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from employees.models import Employee
from employees.models_extended import (
    ExtendedEmployeeSocialInsurance,
    SalaryComponent,
    EmployeeSalaryComponent,
    SocialInsuranceJobTitle
)
from org.models import Branch, Department, Job
from decimal import Decimal

def test_comprehensive_edit_functionality():
    """Test the comprehensive edit page functionality"""
    print("🧪 Testing Comprehensive Employee Edit Functionality...")
    
    # Create test user
    try:
        User = get_user_model()
        import time
        unique_username = f'testuser_{int(time.time())}'
        user = User.objects.create_user(
            username=unique_username,
            password='testpass123',
            email='test@example.com'
        )
        print("✅ Test user created successfully")
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False
    
    # Create test organizational data
    try:
        branch = Branch.objects.create(
            branch_name='Test Branch'
        )

        department = Department.objects.create(
            dept_name='Test Department',
            branch=branch
        )

        job = Job.objects.create(
            job_title='Test Job'
        )
        print("✅ Test organizational data created successfully")
    except Exception as e:
        print(f"❌ Error creating organizational data: {e}")
        return False

    # Create test employee
    try:
        employee = Employee.objects.create(
            emp_code='TEST001',
            first_name='Test',
            last_name='Employee',
            gender='M',
            email='test.employee@company.com',
            mobile='1234567890',
            hire_date='2023-01-01',
            job=job,
            dept=department,
            branch=branch,
            emp_status='Active'
        )
        print("✅ Test employee created successfully")
    except Exception as e:
        print(f"❌ Error creating test employee: {e}")
        return False
    
    # Create test salary components
    try:
        allowance = SalaryComponent.objects.create(
            component_name='Housing Allowance',
            component_type='allowance',
            is_active=True
        )
        
        deduction = SalaryComponent.objects.create(
            component_name='Tax Deduction',
            component_type='deduction',
            is_active=True
        )
        print("✅ Test salary components created successfully")
    except Exception as e:
        print(f"❌ Error creating salary components: {e}")
        return False
    
    # Create test social insurance job title
    try:
        job_title = SocialInsuranceJobTitle.objects.create(
            job_code='TEST_JOB',
            job_title='Test Job Title'
        )
        print("✅ Test job title created successfully")
    except Exception as e:
        print(f"❌ Error creating job title: {e}")
        return False
    
    # Test client
    client = Client()
    
    # Login
    login_success = client.login(username=unique_username, password='testpass123')
    if not login_success:
        print("❌ Login failed")
        return False
    print("✅ Login successful")
    
    # Test comprehensive edit page access
    try:
        url = reverse('employees:comprehensive_edit', kwargs={'emp_id': employee.emp_id})
        response = client.get(url)
        
        if response.status_code == 200:
            print("✅ Comprehensive edit page loads successfully")
        else:
            print(f"❌ Comprehensive edit page failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing comprehensive edit page: {e}")
        return False
    
    # Test social insurance form submission
    try:
        social_insurance_data = {
            'active_tab': 'social_insurance',
            'insurance_status': 'active',
            'start_date': '2023-01-01',
            'subscription_confirmed': True,
            'job_title': job_title.job_title_id,
            'social_insurance_number': 'SI123456',
            'monthly_wage': '5000.00',
            'deduction_percentage': '9.0',
            'employee_deduction': '450.00',
            'company_contribution': '600.00',
            's1_field': False,
            'incoming_document_number': 'DOC123',
            'incoming_document_date': '2023-01-01',
            'notes': 'Test notes'
        }
        
        response = client.post(url, social_insurance_data)
        
        if response.status_code in [200, 302]:
            print("✅ Social insurance form submission successful")
        else:
            print(f"❌ Social insurance form submission failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error submitting social insurance form: {e}")
        return False
    
    # Test salary component addition via AJAX
    try:
        add_component_url = reverse('employees:add_salary_component')
        component_data = {
            'emp_id': employee.emp_id,
            'component_id': allowance.component_id,
            'amount': '1000.00',
            'calculation_type': 'fixed',
            'notes': 'Test allowance'
        }
        
        response = client.post(add_component_url, component_data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                print("✅ Salary component addition successful")
            else:
                print(f"❌ Salary component addition failed: {response_data.get('message')}")
                return False
        else:
            print(f"❌ Salary component addition request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error adding salary component: {e}")
        return False
    
    # Verify salary component was created
    try:
        salary_component = EmployeeSalaryComponent.objects.get(
            emp=employee,
            component=allowance
        )
        if salary_component.amount == Decimal('1000.00'):
            print("✅ Salary component created and saved correctly")
        else:
            print(f"❌ Salary component amount incorrect: {salary_component.amount}")
            return False
    except EmployeeSalaryComponent.DoesNotExist:
        print("❌ Salary component was not created")
        return False
    except Exception as e:
        print(f"❌ Error verifying salary component: {e}")
        return False
    
    # Test salary component removal
    try:
        remove_component_url = reverse('employees:remove_salary_component')
        remove_data = {
            'component_id': salary_component.emp_salary_component_id
        }
        
        response = client.post(remove_component_url, remove_data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                print("✅ Salary component removal successful")
            else:
                print(f"❌ Salary component removal failed: {response_data.get('message')}")
                return False
        else:
            print(f"❌ Salary component removal request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error removing salary component: {e}")
        return False
    
    # Verify salary component was removed
    try:
        EmployeeSalaryComponent.objects.get(emp_salary_component_id=salary_component.emp_salary_component_id)
        print("❌ Salary component was not removed")
        return False
    except EmployeeSalaryComponent.DoesNotExist:
        print("✅ Salary component removed successfully")
    except Exception as e:
        print(f"❌ Error verifying salary component removal: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED! Comprehensive edit functionality is working correctly.")
    return True

def cleanup_test_data():
    """Clean up test data"""
    try:
        # Remove test data
        User = get_user_model()
        User.objects.filter(username__startswith='testuser_').delete()
        Employee.objects.filter(emp_code='TEST001').delete()
        SalaryComponent.objects.filter(component_name__in=['Housing Allowance', 'Tax Deduction']).delete()
        SocialInsuranceJobTitle.objects.filter(job_code='TEST_JOB').delete()
        Job.objects.filter(job_title='Test Job').delete()
        Department.objects.filter(dept_name='Test Department').delete()
        Branch.objects.filter(branch_name='Test Branch').delete()
        print("✅ Test data cleaned up successfully")
    except Exception as e:
        print(f"⚠️ Warning: Error cleaning up test data: {e}")

if __name__ == '__main__':
    try:
        success = test_comprehensive_edit_functionality()
        if success:
            print("\n✅ All functionality tests passed!")
        else:
            print("\n❌ Some tests failed!")
    finally:
        cleanup_test_data()
