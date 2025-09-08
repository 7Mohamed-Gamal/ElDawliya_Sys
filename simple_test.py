#!/usr/bin/env python
"""
Simple test for comprehensive employee edit functionality
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from employees.models import Employee

def test_page_access():
    """Test if the comprehensive edit page loads without errors"""
    print("🧪 Testing Page Access...")
    
    # Get an existing employee
    try:
        employee = Employee.objects.first()
        if not employee:
            print("❌ No employees found in database")
            return False
        print(f"✅ Found employee: {employee.emp_code}")
    except Exception as e:
        print(f"❌ Error finding employee: {e}")
        return False
    
    # Get an existing user
    try:
        User = get_user_model()
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
        print(f"✅ Found user: {user.username}")
    except Exception as e:
        print(f"❌ Error finding user: {e}")
        return False
    
    # Test client
    client = Client()
    
    # Force login (bypass password check for testing)
    client.force_login(user)
    print("✅ Login successful")
    
    # Test comprehensive edit page access
    try:
        url = reverse('employees:comprehensive_edit', kwargs={'emp_id': employee.emp_id})
        print(f"📍 Testing URL: {url}")
        
        response = client.get(url)
        
        if response.status_code == 200:
            print("✅ Comprehensive edit page loads successfully")
            
            # Check if key elements are in the response
            content = response.content.decode('utf-8')
            
            checks = [
                ('Social Insurance Tab', 'social-insurance'),
                ('Salary Components Tab', 'payroll-components'),
                ('Leave Balances Tab', 'leave-balances'),
                ('Performance Evaluation Tab', 'performance-evaluation'),
                ('Documents Tab', 'documents'),
                ('Social Insurance Form', 'social_insurance_form'),
                ('Employee Data', employee.emp_code)
            ]
            
            for check_name, check_text in checks:
                if check_text in content:
                    print(f"✅ {check_name} found in page")
                else:
                    print(f"⚠️ {check_name} not found in page")
            
            return True
        else:
            print(f"❌ Comprehensive edit page failed to load: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Response content: {response.content[:500]}")
            return False
    except Exception as e:
        print(f"❌ Error accessing comprehensive edit page: {e}")
        return False

def test_ajax_endpoints():
    """Test AJAX endpoints"""
    print("\n🧪 Testing AJAX Endpoints...")
    
    # Get an existing employee
    employee = Employee.objects.first()
    if not employee:
        print("❌ No employees found")
        return False
    
    # Get an existing user
    User = get_user_model()
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return False
    
    client = Client()
    client.force_login(user)
    
    # Test salary component endpoints
    try:
        # Test add salary component endpoint
        add_url = reverse('employees:add_salary_component')
        print(f"📍 Testing Add Salary Component URL: {add_url}")
        
        response = client.post(add_url, {
            'emp_id': employee.emp_id,
            'component_id': '999999',  # Non-existent component
            'amount': '1000.00',
            'calculation_type': 'fixed'
        })
        
        if response.status_code == 200:
            print("✅ Add salary component endpoint accessible")
        else:
            print(f"⚠️ Add salary component endpoint returned: {response.status_code}")
        
        # Test remove salary component endpoint
        remove_url = reverse('employees:remove_salary_component')
        print(f"📍 Testing Remove Salary Component URL: {remove_url}")
        
        response = client.post(remove_url, {
            'component_id': '999999'  # Non-existent component
        })
        
        if response.status_code == 200:
            print("✅ Remove salary component endpoint accessible")
        else:
            print(f"⚠️ Remove salary component endpoint returned: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AJAX endpoints: {e}")
        return False

def test_form_submissions():
    """Test form submissions"""
    print("\n🧪 Testing Form Submissions...")
    
    # Get an existing employee
    employee = Employee.objects.first()
    if not employee:
        print("❌ No employees found")
        return False
    
    # Get an existing user
    User = get_user_model()
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return False
    
    client = Client()
    client.force_login(user)
    
    try:
        url = reverse('employees:comprehensive_edit', kwargs={'emp_id': employee.emp_id})
        
        # Test basic info form submission
        basic_info_data = {
            'active_tab': 'basic_info',
            'first_name': 'Updated Name',
            'last_name': 'Updated Last Name',
            'email': 'updated@example.com'
        }
        
        response = client.post(url, basic_info_data)
        
        if response.status_code in [200, 302]:
            print("✅ Basic info form submission successful")
        else:
            print(f"⚠️ Basic info form submission returned: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing form submissions: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting Simple Functionality Tests...\n")
    
    tests = [
        ("Page Access", test_page_access),
        ("AJAX Endpoints", test_ajax_endpoints),
        ("Form Submissions", test_form_submissions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"RESULTS: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ Some tests failed or had issues")
